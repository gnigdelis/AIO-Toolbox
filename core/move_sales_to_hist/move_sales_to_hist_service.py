from __future__ import annotations

from datetime import date, datetime
from typing import Callable

from core.database.database_connection import DatabaseConnection
from core.database.database_context import database_context


class MoveSalesToHistService:
    """
    Service for the legacy Move Sales To Hist operation.

    The actual move is performed by:

        dbo.SnProPOS_SalesTrHist

    The stored procedure receives a cutoff date and moves
    eligible sales whose SalesTransInitDate is <= that date.
    """

    PROCEDURE_NAME = "dbo.SnProPOS_SalesTrHist"

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # DATABASE
    # ------------------------------------------------------------------

    def _get_connection(self):
        if not database_context.is_selected():
            raise RuntimeError(
                "Δεν έχει επιλεγεί βάση δεδομένων."
            )

        database = database_context.active()

        if not database:
            raise RuntimeError(
                "Δεν υπάρχει ενεργή βάση δεδομένων."
            )

        udl_path = database.get("path")

        if not udl_path:
            raise RuntimeError(
                "Δεν βρέθηκε το UDL της ενεργής βάσης δεδομένων."
            )

        connection_manager = DatabaseConnection(udl_path)

        # The stored procedure manages its own transaction.
        # Autocommit prevents pyodbc from wrapping the procedure
        # inside an additional outer transaction.
        return connection_manager.connect(
            autocommit=True
        )

    # ------------------------------------------------------------------
    # ACTIVE SALES SUMMARY
    # ------------------------------------------------------------------

    def get_active_sales_summary(self) -> dict:
        """
        Returns information about the currently active sales table.

        This operation is read-only.

        Returns:
            {
                "count": int,
                "oldest_date": date | None,
                "latest_date": date | None,
            }
        """

        connection = None
        cursor = None

        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    MIN(SalesTransInitDate) AS OldestDate,
                    MAX(SalesTransInitDate) AS LatestDate,
                    COUNT(*) AS TotalRecords
                FROM TblSnSalesTrans
                WHERE SalesTransInitDate IS NOT NULL
                """
            )

            row = cursor.fetchone()

            if row is None:
                return {
                    "count": 0,
                    "oldest_date": None,
                    "latest_date": None,
                }

            oldest_value = row[0]
            latest_value = row[1]
            total_records = row[2] or 0

            return {
                "count": int(total_records),
                "oldest_date": self._to_date(oldest_value),
                "latest_date": self._to_date(latest_value),
            }

        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass

            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass

    def get_oldest_active_sale_date(self) -> date | None:
        """
        Read-only helper returning the oldest active SalesTrans date.
        """

        summary = self.get_active_sales_summary()

        return summary.get("oldest_date")

    # ------------------------------------------------------------------
    # DATE CONVERSION
    # ------------------------------------------------------------------

    @staticmethod
    def _to_date(value) -> date | None:
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        text = str(value).strip()

        if not text:
            return None

        formats = (
            "%Y%m%d",
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y",
        )

        for fmt in formats:
            try:
                return datetime.strptime(
                    text,
                    fmt,
                ).date()
            except ValueError:
                continue

        raise ValueError(
            f"Μη αναγνωρίσιμη ημερομηνία βάσης δεδομένων: {value}"
        )

    # ------------------------------------------------------------------
    # COUNT HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _count_active_until(
        cursor,
        cutoff: str,
    ) -> int:
        """
        Count active sales up to and including the cutoff date.
        """

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM TblSnSalesTrans
            WHERE SalesTransInitDate <= ?
            """,
            cutoff,
        )

        row = cursor.fetchone()

        if row is None:
            return 0

        return int(row[0] or 0)

    @staticmethod
    def _count_history_until(
        cursor,
        cutoff: str,
    ) -> int:
        """
        Count history sales up to and including the cutoff date.
        """

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM TblSnSalesTransHist
            WHERE SalesTransInitDate <= ?
            """,
            cutoff,
        )

        row = cursor.fetchone()

        if row is None:
            return 0

        return int(row[0] or 0)

    # ------------------------------------------------------------------
    # SQL MESSAGES
    # ------------------------------------------------------------------

    @staticmethod
    def _collect_sql_messages(
        cursor,
        connection,
    ) -> list[str]:
        """
        Collect messages exposed by pyodbc.
        """

        messages: list[str] = []

        for source in (cursor, connection):
            try:
                source_messages = getattr(
                    source,
                    "messages",
                    [],
                ) or []
            except Exception:
                source_messages = []

            for sql_message in source_messages:
                if isinstance(sql_message, tuple):
                    text = " ".join(
                        str(part)
                        for part in sql_message
                        if part is not None
                    )
                else:
                    text = str(sql_message)

                text = text.strip()

                if text:
                    messages.append(text)

        return messages

    # ------------------------------------------------------------------
    # MOVE
    # ------------------------------------------------------------------

    def move_until(
        self,
        move_until_date: date,
        progress_callback: Callable[[str], None] | None = None,
    ) -> dict:
        """
        Move eligible sales to history up to and including
        move_until_date.

        The SQL stored procedure performs the actual transaction.

        The operation is considered successful only when:

        1. The stored procedure returns 0.
        2. The active records up to the cutoff have actually
           disappeared.
        3. The history table increased by the same number of records.
        """

        if not isinstance(move_until_date, date):
            raise TypeError(
                "Η ημερομηνία πρέπει να είναι τύπου date."
            )

        if not database_context.is_selected():
            raise RuntimeError(
                "Δεν έχει επιλεγεί βάση δεδομένων."
            )

        database = database_context.active()

        if not database:
            raise RuntimeError(
                "Δεν υπάρχει ενεργή βάση δεδομένων."
            )

        cutoff = move_until_date.strftime("%Y%m%d")

        messages: list[str] = []

        def emit(message: str) -> None:
            messages.append(message)

            if progress_callback is not None:
                progress_callback(message)

        connection = None
        cursor = None

        try:
            emit(
                f"Έναρξη Move Sales To Hist έως "
                f"{move_until_date.strftime('%d/%m/%Y')}..."
            )

            connection = self._get_connection()
            cursor = connection.cursor()

            # ----------------------------------------------------------
            # BEFORE COUNTS
            # ----------------------------------------------------------

            active_before = self._count_active_until(
                cursor,
                cutoff,
            )

            history_before = self._count_history_until(
                cursor,
                cutoff,
            )

            emit(
                f"Active εγγραφές πριν τη μεταφορά: "
                f"{active_before:,}"
            )

            # Nothing to move.
            if active_before == 0:
                emit(
                    "Δεν υπάρχουν ενεργές εγγραφές έως "
                    "την επιλεγμένη ημερομηνία."
                )

                return {
                    "success": True,
                    "date": move_until_date,
                    "cutoff": cutoff,
                    "messages": messages,
                    "database": database.get("name"),
                    "server": database.get("server"),
                    "active_before": 0,
                    "active_after": 0,
                    "history_before": history_before,
                    "history_after": history_before,
                    "moved_count": 0,
                    "procedure_result": 0,
                }

            # ----------------------------------------------------------
            # EXECUTE STORED PROCEDURE
            # ----------------------------------------------------------

            sql = f"""
SET NOCOUNT ON;

DECLARE @ProcedureResult INT;

EXEC @ProcedureResult = {self.PROCEDURE_NAME}
    @SStOIDs = NULL,
    @STTransf = NULL,
    @STInitDate = ?;

SELECT @ProcedureResult AS ProcedureReturnValue;
"""

            cursor.execute(
                sql,
                cutoff,
            )

            # The final SELECT returns the stored procedure return code.
            result_row = cursor.fetchone()

            procedure_result = None

            if result_row is not None:
                procedure_result = result_row[0]

            # Consume any remaining result sets.
            while True:
                try:
                    has_next = cursor.nextset()
                except Exception:
                    break

                if not has_next:
                    break

                try:
                    cursor.fetchall()
                except Exception:
                    pass

            # Collect any SQL Server informational messages.
            for sql_message in self._collect_sql_messages(
                cursor,
                connection,
            ):
                emit(sql_message)

            # ----------------------------------------------------------
            # PROCEDURE RESULT
            # ----------------------------------------------------------

            if procedure_result is None:
                raise RuntimeError(
                    "Δεν ήταν δυνατή η λήψη του return value "
                    "της stored procedure."
                )

            try:
                procedure_result = int(procedure_result)
            except (TypeError, ValueError):
                raise RuntimeError(
                    "Μη έγκυρο return value από τη stored procedure: "
                    f"{procedure_result}"
                )

            emit(
                f"Stored procedure return value: "
                f"{procedure_result}"
            )

            if procedure_result != 0:
                raise RuntimeError(
                    "Η stored procedure SnProPOS_SalesTrHist "
                    f"επέστρεψε κωδικό {procedure_result}."
                )

            # ----------------------------------------------------------
            # AFTER COUNTS
            # ----------------------------------------------------------

            active_after = self._count_active_until(
                cursor,
                cutoff,
            )

            history_after = self._count_history_until(
                cursor,
                cutoff,
            )

            moved_count = active_before - active_after
            history_delta = history_after - history_before

            # ----------------------------------------------------------
            # FINAL VERIFICATION
            # ----------------------------------------------------------

            if active_after != 0:
                raise RuntimeError(
                    "Η stored procedure επέστρεψε 0, "
                    f"αλλά παραμένουν {active_after:,} "
                    "ενεργές εγγραφές έως την επιλεγμένη "
                    "ημερομηνία. Η μεταφορά δεν επιβεβαιώθηκε."
                )

            if moved_count <= 0:
                raise RuntimeError(
                    "Η stored procedure επέστρεψε 0, "
                    "αλλά δεν μεταφέρθηκε καμία εγγραφή."
                )

            if history_delta != moved_count:
                raise RuntimeError(
                    "Η μεταφορά δεν επιβεβαιώθηκε σωστά. "
                    f"Active πριν: {active_before:,}, "
                    f"Active μετά: {active_after:,}, "
                    f"History πριν: {history_before:,}, "
                    f"History μετά: {history_after:,}, "
                    f"History αύξηση: {history_delta:,}."
                )

            emit(
                f"Μεταφέρθηκαν {moved_count:,} εγγραφές "
                "στο history."
            )

            emit(
                "Το Move Sales To Hist ολοκληρώθηκε επιτυχώς."
            )

            return {
                "success": True,
                "date": move_until_date,
                "cutoff": cutoff,
                "messages": messages,
                "database": database.get("name"),
                "server": database.get("server"),
                "active_before": active_before,
                "active_after": active_after,
                "history_before": history_before,
                "history_after": history_after,
                "moved_count": moved_count,
                "procedure_result": procedure_result,
            }

        except Exception:
            raise

        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass

            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass