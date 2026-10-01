from __future__ import annotations

from dataclasses import dataclass

import requests

from core.database.database_connection import DatabaseConnection
from core.database.database_context import database_context


@dataclass
class MyDataInvoice:
    invoice_type: str
    document_name: str
    issue_date: str
    aa: str
    invoice_id: int
    cust_afm: str

    sent: bool = False
    send_status: int | None = None
    send_message: str = ""
    mark: str = ""
    impact_link: str = ""
    mydata_state: str = "PENDING"


class MyDataService:
    """Business logic for searching and sending myDATA documents."""

    API_BASE_URL = (
        "http://localhost/External.Tax.Provider"
    )

    SEND_USER_ID = 3

    # The old implementation queried VSnMyDATAInvoicesAMV directly.
    # That view performs full-table response aggregation and is very slow.
    # The optimized search builds the small candidate set first, then resolves
    # response metadata only for those candidates.
    #
    # IMPORTANT: all temporary tables are created and consumed inside ONE SQL
    # batch. This avoids temp-table scope issues with the ODBC driver.
    SEARCH_SQL = """
    SET NOCOUNT ON;

    SELECT DISTINCT
        stp.SalesTransPosHdr AS InvoiceId,
        st.SalesTransOrderIssuedTime AS IssueDate,
        st.SalesTransNoteNo AS AA,
        nts.MyDATA_NoteTypeSubCategCode AS InvoiceType,
        nt.NoteTypeDescr AS DocumentName,
        CASE
            WHEN cus.CustExternal = 1
                THEN NULLIF(ISNULL(cus.CustVATNumber, ''), '')
            ELSE NULLIF(ISNULL(cus.CustAFM, ''), '')
        END AS CustAFM
    INTO #MyDataCandidates
    FROM VSnVSalesTrans st WITH (NOLOCK)
    INNER JOIN VSnVSalesTransPos stp WITH (NOLOCK)
        ON st.SalesTransOID = stp.SalesTransOID
    INNER JOIN VSnVSalesPayWay spw WITH (NOLOCK)
        ON stp.SalesTransPosHdr = spw.SalesPWPosHdr
    INNER JOIN TblSnPayWay pw WITH (NOLOCK)
        ON spw.PayWayOID = pw.PayWayOID
    INNER JOIN VSnVatPercentFull vp WITH (NOLOCK)
        ON st.VatPercentOID = vp.VatPercentOID
    INNER JOIN TblSnShopItem si WITH (NOLOCK)
        ON st.ShopItemOID = si.ShopItemOID
    INNER JOIN TblSnItem i WITH (NOLOCK)
        ON si.ItemOID = i.ItemOID
    INNER JOIN TblSnFinYear fy WITH (NOLOCK)
        ON st.FinYearOID = fy.FinYearOID
    INNER JOIN TblSnCustomer cus WITH (NOLOCK)
        ON st.CustomerOID = cus.CustomerOID
    INNER JOIN TblSnSalesStation ss WITH (NOLOCK)
        ON st.SalesStationOID = ss.SalesStationOID
    INNER JOIN TblSnShop shop WITH (NOLOCK)
        ON ss.ShopOID = shop.ShopOID
    INNER JOIN TblSnNoteType nt WITH (NOLOCK)
        ON st.SalesTransNoteCode = nt.NoteTypeOID
    LEFT JOIN TblSnMyDATA_NoteTypeSubCateg nts WITH (NOLOCK)
        ON nt.MyDATA_NoteTypeSubCategOID = nts.MyDATA_NoteTypeSubCategOID
    INNER JOIN TblSnDataBase db WITH (NOLOCK)
        ON st.DataBaseOID = db.DataBaseOID
    WHERE
        st.SalesTransOrderIssuedTime >= CONVERT(datetime, ?, 112)
        AND st.SalesTransOrderIssuedTime < DATEADD(
            day, 1, CONVERT(datetime, ?, 112)
        )
        AND ISNULL(nt.NoteTypeMyDATAIncluded, 0) = 1
        AND nt.MyDATA_NoteTypeSubCategOID IS NOT NULL
        AND cus.CustMyDATAIncluded = 1
        AND st.SalesTransInitDate >= shop.ShopAMVProviderStartDate
        AND (
            (
                i.ItemNonPrintable = 0
                AND nt.NoteTypeGroupPos > 2
            )
            OR (
                i.ItemNonPrintable = 0
                AND nt.NoteTypeGroupPos <= 2
                AND nt.NoteTypeIssue = 1
            )
            OR (
                nt.NoteTypeGroupPos <= 2
                AND nt.NoteTypeIssue = 0
            )
        )
        AND stp.SalesTransPosItemFlag NOT IN (10)
        AND (
            st.SalesTransCashGrs > 0
            OR nts.MyDATA_NoteTypeSubCategCode = '9.3'
            OR stp.SalesTransPosItemFlag = 14
        )
        AND db.DataBaseLocal = 1
        AND shop.ShopAMVProviderEnabled = 1;

    CREATE UNIQUE CLUSTERED INDEX IX_MyDataCandidates
        ON #MyDataCandidates (InvoiceId);

    SELECT
        c.InvoiceId,
        MAX(r.MyDATA_ResponseOID) AS LastResponseOID
    INTO #MyDataLatestResponse
    FROM #MyDataCandidates c
    INNER JOIN TblSnMyDATA_Response r WITH (NOLOCK)
        ON r.MyDATA_ResponseSalesTransPosHdr = c.InvoiceId
    GROUP BY c.InvoiceId;

    CREATE UNIQUE CLUSTERED INDEX IX_MyDataLatestResponse
        ON #MyDataLatestResponse (InvoiceId);

    SELECT
        c.InvoiceId,
        MAX(r.MyDATA_ResponseOID) AS LastSuccessOID
    INTO #MyDataLatestSuccess
    FROM #MyDataCandidates c
    INNER JOIN TblSnMyDATA_Response r WITH (NOLOCK)
        ON r.MyDATA_ResponseSalesTransPosHdr = c.InvoiceId
    WHERE r.MyDATA_ResponseStatusCode = 'Success'
    GROUP BY c.InvoiceId;

    CREATE UNIQUE CLUSTERED INDEX IX_MyDataLatestSuccess
        ON #MyDataLatestSuccess (InvoiceId);

    SELECT
        p.SalesTransPosHdr AS InvoiceId,
        MAX(s.SalesTransNoteCode) AS NoteCode,
        MAX(s.SalesTransNoteNo) AS NoteNo,
        MAX(s.SalesTransRealDate) AS RealDate,
        MAX(s.SalesTransBeginTime) AS BeginTime,
        MAX(s.SalesTransOtherNoteNo) AS OtherNoteNo,
        MAX(s.SalesTransOID) AS SalesTransOID
    INTO #MyDataHistorical
    FROM TblSnSalesTransPos p WITH (NOLOCK)
    INNER JOIN TblSnSalesTrans s WITH (NOLOCK)
        ON s.SalesTransOID = p.SalesTransOID
    WHERE
        CONVERT(date, s.SalesTransRealDate)
            BETWEEN CONVERT(date, ?, 112)
            AND CONVERT(date, ?, 112)
        AND EXISTS
        (
            SELECT 1
            FROM TblSnMyDATA_Response r0 WITH (NOLOCK)
            WHERE r0.MyDATA_ResponseSalesTransPosHdr = p.SalesTransPosHdr
        )
    GROUP BY p.SalesTransPosHdr;

    CREATE UNIQUE CLUSTERED INDEX IX_MyDataHistorical
        ON #MyDataHistorical (InvoiceId);

    SELECT
        CAST(
            CASE
                WHEN h.NoteCode IS NULL THEN ''
                ELSE CAST(h.NoteCode AS NVARCHAR(64))
            END AS NVARCHAR(64)
        ) AS InvoiceType,
        CAST(
            CASE
                WHEN h.NoteCode IS NULL THEN 'MyDATA'
                ELSE 'Document ' + CAST(h.NoteCode AS NVARCHAR(64))
            END AS NVARCHAR(256)
        ) AS DocumentName,
        CONVERT(varchar(10), h.RealDate, 23) AS IssueDate,
        CAST(h.NoteNo AS NVARCHAR(64)) AS AA,
        h.InvoiceId,
        ISNULL(sr.MyDATA_ResponseTransactorTRN, '') AS CustAFM,
        CASE
            WHEN sr.MyDATA_ResponseOID IS NOT NULL
                THEN 'SENT'
            ELSE 'PENDING'
        END AS MyDataState,
        ISNULL(sr.MyDATA_ResponseInvoiceMARK, '') AS MARK,
        ISNULL(sr.MyDATA_ResponseProviderQRCodeLink, '') AS ImpactLink
    FROM #MyDataHistorical h
    OUTER APPLY
    (
        SELECT TOP 1
            r.MyDATA_ResponseOID,
            r.MyDATA_ResponseInvoiceMARK,
            r.MyDATA_ResponseProviderQRCodeLink,
            r.MyDATA_ResponseTransactorTRN
        FROM TblSnMyDATA_Response r WITH (NOLOCK)
        WHERE
            r.MyDATA_ResponseSalesTransPosHdr = h.InvoiceId
            AND r.MyDATA_ResponseStatusCode = 'Success'
        ORDER BY r.MyDATA_ResponseOID DESC
    ) sr

    UNION ALL

    SELECT
        CAST(c.InvoiceType AS NVARCHAR(64)) AS InvoiceType,
        CAST(c.DocumentName AS NVARCHAR(256)) AS DocumentName,
        CONVERT(varchar(10), c.IssueDate, 23) AS IssueDate,
        CAST(c.AA AS NVARCHAR(64)) AS AA,
        c.InvoiceId,
        ISNULL(c.CustAFM, '') AS CustAFM,
        CASE
            WHEN sr.MyDATA_ResponseOID IS NOT NULL
                THEN 'SENT'
            ELSE 'PENDING'
        END AS MyDataState,
        ISNULL(sr.MyDATA_ResponseInvoiceMARK, '') AS MARK,
        ISNULL(sr.MyDATA_ResponseProviderQRCodeLink, '') AS ImpactLink
    FROM #MyDataCandidates c
    LEFT JOIN #MyDataLatestResponse lr
        ON lr.InvoiceId = c.InvoiceId
    LEFT JOIN TblSnMyDATA_Response latest WITH (NOLOCK)
        ON latest.MyDATA_ResponseOID = lr.LastResponseOID
    LEFT JOIN #MyDataLatestSuccess ls
        ON ls.InvoiceId = c.InvoiceId
    LEFT JOIN TblSnMyDATA_Response sr WITH (NOLOCK)
        ON sr.MyDATA_ResponseOID = ls.LastSuccessOID
    WHERE
        NOT EXISTS
        (
            SELECT 1
            FROM #MyDataHistorical h
            WHERE h.InvoiceId = c.InvoiceId
        )
        -- Do not filter on MyDATA_ResponseUpdated here.
        -- A response with Updated=1 can be a successfully sent document
        -- and must remain visible in the SENT tab. The state is determined
        -- by the existence of the latest successful response above.

    ORDER BY IssueDate, AA;
    """

    def _get_connection(self):
        udl_path = database_context.active_udl()

        if not udl_path:
            raise RuntimeError(
                "Δεν έχει επιλεγεί βάση δεδομένων."
            )

        database = DatabaseConnection(udl_path)
        return database.connect()

    def search(
        self,
        start_date: str,
        end_date: str,
    ) -> list[MyDataInvoice]:
        """Search myDATA documents using the optimized single SQL batch."""

        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            # One execute is intentional: SQL Server local temp tables must
            # remain in the same ODBC session/batch used to consume them.
            cursor.execute(
                self.SEARCH_SQL,
                start_date,
                end_date,
                start_date,
                end_date,
            )

            # The batch contains SELECT INTO / CREATE INDEX statements
            # before the final SELECT. ODBC exposes those as intermediate
            # result sets with no columns, so advance to the first real
            # result set before calling fetchall().
            while cursor.description is None:
                if not cursor.nextset():
                    raise RuntimeError(
                        "Η αναζήτηση δεν επέστρεψε αποτέλεσμα."
                    )

            rows = cursor.fetchall()

            invoices: list[MyDataInvoice] = []

            for row in rows:
                mydata_state = str(
                    row[6] or "PENDING"
                ).upper()

                if mydata_state not in ("SENT", "PENDING"):
                    mydata_state = "PENDING"

                invoices.append(
                    MyDataInvoice(
                        invoice_type=str(row[0] or ""),
                        document_name=str(row[1] or ""),
                        issue_date=str(row[2] or ""),
                        aa=str(row[3] or ""),
                        invoice_id=int(row[4]),
                        cust_afm=str(row[5] or ""),
                        sent=(mydata_state == "SENT"),
                        mark=str(row[7] or ""),
                        impact_link=str(row[8] or ""),
                        mydata_state=mydata_state,
                    )
                )

            cursor.close()
            return invoices

        finally:
            connection.close()

    def _get_response_metadata(
        self,
        invoice_id: int,
    ) -> tuple[str, str]:
        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT TOP 1
                    ISNULL(MyDATA_ResponseInvoiceMARK, ''),
                    ISNULL(MyDATA_ResponseProviderQRCodeLink, '')
                FROM TblSnMyDATA_Response WITH (NOLOCK)
                WHERE
                    MyDATA_ResponseSalesTransPosHdr = ?
                    AND MyDATA_ResponseStatusCode = 'Success'
                ORDER BY MyDATA_ResponseOID DESC
                """,
                invoice_id,
            )

            row = cursor.fetchone()
            cursor.close()

            if not row:
                return "", ""

            return str(row[0] or ""), str(row[1] or "")

        finally:
            connection.close()

    def send_invoice(
        self,
        invoice_id: int,
    ) -> dict:
        url = (
            f"{self.API_BASE_URL}"
            "/api/TaxProvider/SendInvoice/1/0/1/1/0"
        )

        params = {
            "id": invoice_id,
            "userId": self.SEND_USER_ID,
        }

        response = requests.post(
            url,
            params=params,
            timeout=120,
        )

        message = response.text.strip()
        impact_link = ""

        if message.startswith("https://einvoice.impact.gr/"):
            impact_link = message

        mark = ""

        if response.status_code == 200:
            try:
                db_mark, db_link = self._get_response_metadata(invoice_id)
                mark = db_mark
                impact_link = db_link or impact_link
            except Exception:
                pass

        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "message": message,
            "mark": mark,
            "impact_link": impact_link,
            "url": response.url,
        }

    def send_invoices(self, invoices) -> list[dict]:
        results = []

        for invoice in invoices:
            try:
                result = self.send_invoice(invoice.invoice_id)

                invoice.send_status = result["status_code"]
                invoice.send_message = result.get("message", "") or ""
                invoice.impact_link = result.get("impact_link", "") or ""
                invoice.mark = (
                    result.get("mark", "")
                    or getattr(invoice, "mark", "")
                    or ""
                )
                invoice.sent = bool(result.get("success", False))
                invoice.mydata_state = "SENT" if invoice.sent else "PENDING"

                results.append(
                    {
                        "invoice": invoice,
                        "result": result,
                    }
                )

            except Exception as exc:
                invoice.sent = False
                invoice.mydata_state = "PENDING"
                invoice.send_status = None
                invoice.send_message = str(exc)

                results.append(
                    {
                        "invoice": invoice,
                        "result": {
                            "success": False,
                            "status_code": None,
                            "message": str(exc),
                            "mark": "",
                            "impact_link": "",
                        },
                    }
                )

        return results

    def database_selected(self) -> bool:
        return database_context.is_selected()
