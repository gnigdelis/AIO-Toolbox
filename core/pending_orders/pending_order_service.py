from __future__ import annotations

from core.database.database_connection import DatabaseConnection
from core.database.database_context import database_context


class PendingOrderService:
    """
    Service for finding and closing pending sales transactions.

    The legacy Support Toolbox calls this operation
    "Delete Pending Order", but the actual database operation
    changes SalesTransStatus to 1.
    """

    SEARCH_SQL = """
        SELECT
            SalesTransOID,
            SalesTransStatus,
            SalesTransNoteNo,
            SalesTransInitDate
        FROM TblSnSalesTrans
        WHERE SalesTransNoteNo = ?
          AND SalesTransInitDate = ?
          AND SalesTransStatus IN (0, 2)
        ORDER BY SalesTransOID
    """

    UPDATE_SQL = """
        UPDATE TblSnSalesTrans
        SET SalesTransStatus = 1
        WHERE SalesTransOID = ?
          AND SalesTransStatus IN (0, 2)
    """

    def _get_connection(self):
        udl_path = database_context.active_udl()

        if not udl_path:
            raise RuntimeError(
                "No database selected."
            )

        database = DatabaseConnection(
            udl_path
        )

        return database.connect()

    def search(
        self,
        note_no: str | int,
        init_date: str,
    ) -> list[dict]:
        """
        Find pending transactions for an invoice number and date.
        """

        try:
            invoice_number = int(note_no)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Invoice number must be a number."
            ) from exc

        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                self.SEARCH_SQL,
                invoice_number,
                init_date,
            )

            rows = cursor.fetchall()

            result = []

            for row in rows:
                result.append(
                    {
                        "oid": row.SalesTransOID,
                        "status": row.SalesTransStatus,
                        "note_no": row.SalesTransNoteNo,
                        "init_date": row.SalesTransInitDate,
                    }
                )

            cursor.close()

            return result

        finally:
            connection.close()

    def update_statuses(
        self,
        oids: list[int],
    ) -> dict:
        """
        Change selected pending transactions to status 1.
        """

        if not oids:
            return {
                "updated": 0,
            }

        connection = self._get_connection()

        updated = 0

        try:
            cursor = connection.cursor()

            for oid in oids:
                cursor.execute(
                    self.UPDATE_SQL,
                    oid,
                )

                updated += cursor.rowcount

            connection.commit()

            cursor.close()

            return {
                "updated": updated,
            }

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()