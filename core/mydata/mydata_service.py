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

    SEARCH_SQL = """
    WITH HistoricalInvoices AS
    (
        SELECT
            p.SalesTransPosHdr AS InvoiceId,
            MAX(s.SalesTransNoteCode) AS NoteCode,
            MAX(s.SalesTransNoteNo) AS NoteNo,
            MAX(s.SalesTransRealDate) AS RealDate,
            MAX(s.SalesTransBeginTime) AS BeginTime,
            MAX(s.SalesTransOtherNoteNo) AS OtherNoteNo,
            MAX(s.SalesTransOID) AS SalesTransOID
        FROM TblSnSalesTransPos p
        INNER JOIN TblSnSalesTrans s
            ON s.SalesTransOID = p.SalesTransOID
        WHERE
            CONVERT(date, s.SalesTransRealDate)
                BETWEEN CONVERT(date, ?, 112)
                AND CONVERT(date, ?, 112)
            AND EXISTS
            (
                SELECT 1
                FROM TblSnMyDATA_Response r0
                WHERE
                    r0.MyDATA_ResponseSalesTransPosHdr =
                        p.SalesTransPosHdr
            )
        GROUP BY
            p.SalesTransPosHdr
    ),

    HistoricalWithResponse AS
    (
        SELECT
            h.InvoiceId,
            h.NoteCode,
            h.NoteNo,
            h.RealDate,
            h.BeginTime,
            h.OtherNoteNo,
            h.SalesTransOID,

            CASE
                WHEN EXISTS
                (
                    SELECT 1
                    FROM TblSnMyDATA_Response rs
                    WHERE
                        rs.MyDATA_ResponseSalesTransPosHdr = h.InvoiceId
                        AND rs.MyDATA_ResponseStatusCode = 'Success'
                )
                    THEN 'SENT'
                ELSE 'PENDING'
            END AS MyDataState,

            SuccessResponse.MyDATA_ResponseInvoiceMARK AS MARK,
            SuccessResponse.MyDATA_ResponseProviderQRCodeLink AS ImpactLink,
            SuccessResponse.MyDATA_ResponseTransactorTRN AS CustAFM

        FROM HistoricalInvoices h

        OUTER APPLY
        (
            SELECT TOP 1
                r.MyDATA_ResponseInvoiceMARK,
                r.MyDATA_ResponseProviderQRCodeLink,
                r.MyDATA_ResponseTransactorTRN
            FROM TblSnMyDATA_Response r
            WHERE
                r.MyDATA_ResponseSalesTransPosHdr = h.InvoiceId
                AND r.MyDATA_ResponseStatusCode = 'Success'
            ORDER BY r.MyDATA_ResponseOID DESC
        ) AS SuccessResponse
    ),

    CurrentInvoices AS
    (
        SELECT DISTINCT
            CAST(invoiceType AS NVARCHAR(64)) AS InvoiceType,
            CAST(DocumentType AS NVARCHAR(256)) AS DocumentName,
            CONVERT(varchar(10), issueDate, 23) AS IssueDate,
            aa,
            InvoiceId,
            CustAFM
        FROM VSnMyDATAInvoicesAMV
        WHERE
            CONVERT(date, issueDate)
                BETWEEN CONVERT(date, ?, 112)
                AND CONVERT(date, ?, 112)
    ),

    CurrentWithResponse AS
    (
        SELECT
            c.InvoiceType,
            c.DocumentName,
            c.IssueDate,
            c.aa,
            c.InvoiceId,
            c.CustAFM,

            CASE
                WHEN EXISTS
                (
                    SELECT 1
                    FROM TblSnMyDATA_Response rs
                    WHERE
                        rs.MyDATA_ResponseSalesTransPosHdr = c.InvoiceId
                        AND rs.MyDATA_ResponseStatusCode = 'Success'
                )
                    THEN 'SENT'
                ELSE 'PENDING'
            END AS MyDataState,

            ISNULL(
                SuccessResponse.MyDATA_ResponseInvoiceMARK,
                ''
            ) AS MARK,

            ISNULL(
                SuccessResponse.MyDATA_ResponseProviderQRCodeLink,
                ''
            ) AS ImpactLink

        FROM CurrentInvoices c

        OUTER APPLY
        (
            SELECT TOP 1
                r.MyDATA_ResponseInvoiceMARK,
                r.MyDATA_ResponseProviderQRCodeLink
            FROM TblSnMyDATA_Response r
            WHERE
                r.MyDATA_ResponseSalesTransPosHdr = c.InvoiceId
                AND r.MyDATA_ResponseStatusCode = 'Success'
            ORDER BY r.MyDATA_ResponseOID DESC
        ) AS SuccessResponse
    )

    SELECT
        CAST(
            CASE
                WHEN h.NoteCode IS NULL THEN ''
                ELSE CAST(h.NoteCode AS NVARCHAR(64))
            END
            AS NVARCHAR(64)
        ) AS InvoiceType,

        CAST(
            CASE
                WHEN h.NoteCode IS NULL THEN 'MyDATA'
                ELSE 'Document ' + CAST(h.NoteCode AS NVARCHAR(64))
            END
            AS NVARCHAR(256)
        ) AS DocumentName,

        CONVERT(varchar(10), h.RealDate, 23) AS IssueDate,
        CAST(h.NoteNo AS NVARCHAR(64)) AS AA,
        h.InvoiceId,
        ISNULL(h.CustAFM, '') AS CustAFM,
        h.MyDataState,
        ISNULL(h.MARK, '') AS MARK,
        ISNULL(h.ImpactLink, '') AS ImpactLink

    FROM HistoricalWithResponse h

    UNION

    SELECT
        c.InvoiceType,
        c.DocumentName,
        c.IssueDate,
        c.aa,
        c.InvoiceId,
        c.CustAFM,
        c.MyDataState,
        c.MARK,
        c.ImpactLink

    FROM CurrentWithResponse c

    WHERE NOT EXISTS
    (
        SELECT 1
        FROM HistoricalWithResponse h
        WHERE h.InvoiceId = c.InvoiceId
    )

    ORDER BY
        IssueDate,
        AA
    """

    def _get_connection(self):
        udl_path = database_context.active_udl()

        if not udl_path:
            raise RuntimeError(
                "Δεν έχει επιλεγεί βάση δεδομένων."
            )

        database = DatabaseConnection(
            udl_path
        )

        return database.connect()

    def search(
        self,
        start_date: str,
        end_date: str,
    ) -> list[MyDataInvoice]:

        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                self.SEARCH_SQL,
                start_date,
                end_date,
                start_date,
                end_date,
            )

            rows = cursor.fetchall()

            invoices: list[MyDataInvoice] = []

            for row in rows:
                mydata_state = str(
                    row[6] or "PENDING"
                ).upper()

                if mydata_state not in (
                    "SENT",
                    "PENDING",
                ):
                    mydata_state = "PENDING"

                invoices.append(
                    MyDataInvoice(
                        invoice_type=str(
                            row[0] or ""
                        ),
                        document_name=str(
                            row[1] or ""
                        ),
                        issue_date=str(
                            row[2] or ""
                        ),
                        aa=str(
                            row[3] or ""
                        ),
                        invoice_id=int(
                            row[4]
                        ),
                        cust_afm=str(
                            row[5] or ""
                        ),
                        sent=(
                            mydata_state == "SENT"
                        ),
                        mark=str(
                            row[7] or ""
                        ),
                        impact_link=str(
                            row[8] or ""
                        ),
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
                    ISNULL(
                        MyDATA_ResponseInvoiceMARK,
                        ''
                    ),
                    ISNULL(
                        MyDATA_ResponseProviderQRCodeLink,
                        ''
                    )
                FROM TblSnMyDATA_Response
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

            return (
                str(row[0] or ""),
                str(row[1] or ""),
            )

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

        if message.startswith(
            "https://einvoice.impact.gr/"
        ):
            impact_link = message

        mark = ""

        if response.status_code == 200:
            try:
                db_mark, db_link = (
                    self._get_response_metadata(
                        invoice_id
                    )
                )

                mark = db_mark
                impact_link = (
                    db_link or impact_link
                )

            except Exception:
                pass

        return {
            "success": (
                response.status_code == 200
            ),
            "status_code": response.status_code,
            "message": message,
            "mark": mark,
            "impact_link": impact_link,
            "url": response.url,
        }

    def send_invoices(
        self,
        invoices,
    ) -> list[dict]:

        results = []

        for invoice in invoices:
            try:
                result = self.send_invoice(
                    invoice.invoice_id
                )

                invoice.send_status = (
                    result["status_code"]
                )

                invoice.send_message = (
                    result.get(
                        "message",
                        "",
                    )
                    or ""
                )

                invoice.impact_link = (
                    result.get(
                        "impact_link",
                        "",
                    )
                    or ""
                )

                invoice.mark = (
                    result.get(
                        "mark",
                        "",
                    )
                    or getattr(
                        invoice,
                        "mark",
                        "",
                    )
                    or ""
                )

                invoice.sent = bool(
                    result.get(
                        "success",
                        False,
                    )
                )

                invoice.mydata_state = (
                    "SENT"
                    if invoice.sent
                    else "PENDING"
                )

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