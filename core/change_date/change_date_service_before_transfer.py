from __future__ import annotations

from datetime import date, datetime

from core.database.database_connection import DatabaseConnection
from core.database.database_context import database_context


class ChangeDateService:
    """
    Service for the Change Date tool.

    This service currently provides the safe read-only part of the
    legacy Change Date functionality.

    The actual transfer operation is intentionally not implemented
    here yet because the legacy operation updates sales, payments,
    and movements as one database operation.
    """

    CURRENT_DATE_SQL = """
        SELECT TOP 1
            SalesStationRestDate
        FROM TblSnSalesStation
        WHERE SalesStationRestDate IS NOT NULL
        ORDER BY SalesStationOID
    """

    TRANSACTIONS_SQL = """
        SELECT
            SalesTransOID,
            SalesTransRealDate,
            SalesTransBeginTime,
            SalesTransNoteNo,
            SalesTransNoteCode,
            SalesTransFinPayVal
        FROM TblSnSalesTrans
        WHERE SalesTransRealDate >= ?
          AND SalesTransRealDate < ?
        ORDER BY
            SalesTransRealDate,
            SalesTransBeginTime,
            SalesTransOID
    """

    def _get_connection(self):
        udl_path = database_context.active_udl()

        if not udl_path:
            raise RuntimeError(
                "No database selected."
            )

        database = DatabaseConnection(udl_path)

        return database.connect()

    @staticmethod
    def _date_start(value: date) -> datetime:
        return datetime(
            value.year,
            value.month,
            value.day,
        )

    @staticmethod
    def _next_date(value: date) -> datetime:
        from datetime import timedelta

        next_day = value + timedelta(days=1)

        return datetime(
            next_day.year,
            next_day.month,
            next_day.day,
        )

    def get_current_restaurant_date(self) -> date:
        """
        Read the current restaurant date from TblSnSalesStation.
        """

        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                self.CURRENT_DATE_SQL
            )

            row = cursor.fetchone()

            cursor.close()

            if row is None:
                raise RuntimeError(
                    "Current restaurant date was not found."
                )

            value = row.SalesStationRestDate

            if isinstance(value, datetime):
                return value.date()

            if isinstance(value, date):
                return value

            raise RuntimeError(
                "Invalid restaurant date returned by the database."
            )

        finally:
            connection.close()

    def find_transactions(
        self,
        restaurant_date: date,
    ) -> list[dict]:
        """
        Find sales transactions belonging to the selected
        restaurant date.
        """

        if not isinstance(restaurant_date, date):
            raise ValueError(
                "Restaurant date must be a date."
            )

        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            start_date = self._date_start(
                restaurant_date
            )

            end_date = self._next_date(
                restaurant_date
            )

            cursor.execute(
                self.TRANSACTIONS_SQL,
                start_date,
                end_date,
            )

            rows = cursor.fetchall()

            result = []

            for row in rows:
                result.append(
                    {
                        "SalesTransOID": row.SalesTransOID,
                        "SalesTransRealDate": (
                            row.SalesTransRealDate
                        ),
                        "SalesTransBeginTime": (
                            row.SalesTransBeginTime
                        ),
                        "SalesTransNoteNo": (
                            row.SalesTransNoteNo
                        ),
                        "SalesTransNoteCode": (
                            row.SalesTransNoteCode
                        ),
                        "SalesTransFinPayVal": (
                            row.SalesTransFinPayVal
                        ),
                    }
                )

            cursor.close()

            return result

        finally:
            connection.close()

    def transfer_selected(
        self,
        sales_trans_oids: list[int],
        current_date: date,
        new_date: date,
    ) -> dict:
        """
        Placeholder for the legacy transfer operation.

        The real operation must update the complete transaction
        relationship, including sales, payments and movements.
        """

        raise NotImplementedError(
            "Change Date transfer is not enabled yet. "
            "The legacy sales/payment/movement transfer "
            "operation must be migrated first."
        )

    def transfer_all(
        self,
        current_date: date,
        new_date: date,
    ) -> dict:
        """
        Placeholder for the legacy Transfer All operation.
        """

        raise NotImplementedError(
            "Change Date transfer is not enabled yet. "
            "The legacy sales/payment/movement transfer "
            "operation must be migrated first."
        )