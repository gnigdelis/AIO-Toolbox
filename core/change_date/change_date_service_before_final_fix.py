from __future__ import annotations

from datetime import date, datetime, timedelta

from core.database.database_connection import DatabaseConnection
from core.database.database_context import database_context


class ChangeDateService:
    """
    Service for the Change Date tool.
    """

    CURRENT_DATE_SQL = """
        SELECT TOP 1
            SalesStationOID,
            SalesStationRestDate
        FROM TblSnSalesStation
        WHERE SalesStationRestDate IS NOT NULL
        ORDER BY SalesStationOID
    """

    TRANSACTIONS_SQL = """
        SELECT
            p.SalesTransPosHdr AS SalesTransPosHdr,
            MIN(s.SalesTransOID) AS SalesTransOID,
            MIN(s.SalesTransInitDate) AS SalesTransInitDate,
            MIN(s.SalesTransRealDate) AS SalesTransRealDate,
            MIN(s.SalesTransBeginTime) AS SalesTransBeginTime,
            MIN(s.SalesTransNoteNo) AS SalesTransNoteNo,
            MIN(s.SalesTransNoteCode) AS SalesTransNoteCode,
            SUM(ISNULL(s.SalesTransCashGrs, 0))
                AS SalesTransCashGrs,
            SUM(ISNULL(s.SalesTransCredGrs, 0))
                AS SalesTransCredGrs,
            SUM(ISNULL(s.SalesTransFoffGrs, 0))
                AS SalesTransFoffGrs,
            COUNT(*) AS TransactionRowCount
        FROM TblSnSalesTrans s
        INNER JOIN TblSnSalesTransPos p
            ON p.SalesTransOID = s.SalesTransOID
        WHERE s.SalesTransInitDate >= ?
          AND s.SalesTransInitDate < ?
        GROUP BY
            p.SalesTransPosHdr
        ORDER BY
            MIN(s.SalesTransBeginTime),
            p.SalesTransPosHdr
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
        next_day = value + timedelta(days=1)

        return datetime(
            next_day.year,
            next_day.month,
            next_day.day,
        )

    def get_current_restaurant_date(self) -> date:
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
                        "SalesTransPosHdr":
                            row.SalesTransPosHdr,

                        "SalesTransOID":
                            row.SalesTransOID,

                        "SalesTransInitDate":
                            row.SalesTransInitDate,

                        "SalesTransRealDate":
                            row.SalesTransRealDate,

                        "SalesTransBeginTime":
                            row.SalesTransBeginTime,

                        "SalesTransNoteNo":
                            row.SalesTransNoteNo,

                        "SalesTransNoteCode":
                            row.SalesTransNoteCode,

                        "SalesTransCashGrs":
                            row.SalesTransCashGrs,

                        "SalesTransCredGrs":
                            row.SalesTransCredGrs,

                        "SalesTransFoffGrs":
                            row.SalesTransFoffGrs,

                        "TransactionRowCount":
                            row.TransactionRowCount,
                    }
                )

            cursor.close()

            return result

        finally:
            connection.close()

    def transfer_selected(
        self,
        transaction_ids: list[int],
        new_date: date,
    ) -> dict:

        if not transaction_ids:
            return {
                "success": False,
                "affected_rows": 0,
                "message": "No transactions selected.",
            }

        if new_date is None:
            return {
                "success": False,
                "affected_rows": 0,
                "message": (
                    "New restaurant date is required."
                ),
            }

        try:
            pos_headers = [
                int(value)
                for value in transaction_ids
                if value is not None
            ]

        except (TypeError, ValueError) as error:
            return {
                "success": False,
                "affected_rows": 0,
                "message": (
                    "Invalid transaction selection."
                    f"\n\n{error}"
                ),
            }

        pos_headers = list(
            dict.fromkeys(pos_headers)
        )

        if not pos_headers:
            return {
                "success": False,
                "affected_rows": 0,
                "message": "No valid transactions selected.",
            }

        database = self._get_connection()

        try:
            cursor = database.cursor()

            placeholders = ",".join(
                "?" for _ in pos_headers
            )

            verify_sql = f"""
                SELECT
                    p.SalesTransPosHdr,
                    MIN(s.SalesTransInitDate)
                        AS SalesTransInitDate,
                    MIN(s.SalesTransRealDate)
                        AS SalesTransRealDate,
                    MIN(s.SalesTransNoteNo)
                        AS SalesTransNoteNo,
                    MIN(s.SalesTransNoteCode)
                        AS SalesTransNoteCode
                FROM TblSnSalesTransPos p
                INNER JOIN TblSnSalesTrans s
                    ON s.SalesTransOID = p.SalesTransOID
                WHERE p.SalesTransPosHdr IN (
                    {placeholders}
                )
                GROUP BY
                    p.SalesTransPosHdr
            """

            cursor.execute(
                verify_sql,
                *pos_headers,
            )

            selected_rows = cursor.fetchall()

            found_headers = {
                int(row.SalesTransPosHdr)
                for row in selected_rows
            }

            missing_headers = [
                header
                for header in pos_headers
                if header not in found_headers
            ]

            if missing_headers:
                raise RuntimeError(
                    "One or more selected transactions "
                    "could not be found in the database.\n\n"
                    "Missing SalesTransPosHdr: "
                    + ", ".join(
                        str(value)
                        for value in missing_headers
                    )
                )

            source_dates = {
                row.SalesTransInitDate.date()
                if hasattr(
                    row.SalesTransInitDate,
                    "date",
                )
                else row.SalesTransInitDate
                for row in selected_rows
                if row.SalesTransInitDate is not None
            }

            if not source_dates:
                raise RuntimeError(
                    "The selected transactions do not "
                    "have a valid restaurant date."
                )

            if len(source_dates) != 1:
                raise RuntimeError(
                    "The selected transactions belong "
                    "to different restaurant dates."
                )

            source_date = next(
                iter(source_dates)
            )

            if source_date == new_date:
                raise RuntimeError(
                    "Source and destination restaurant "
                    "dates are the same."
                )

            update_sales_sql = f"""
                UPDATE s
                SET
                    s.SalesTransInitDate = ?
                FROM TblSnSalesTrans s
                INNER JOIN TblSnSalesTransPos p
                    ON p.SalesTransOID = s.SalesTransOID
                WHERE p.SalesTransPosHdr IN (
                    {placeholders}
                )
                  AND s.SalesTransInitDate = ?
            """

            cursor.execute(
                update_sales_sql,
                new_date,
                *pos_headers,
                source_date,
            )

            sales_affected = cursor.rowcount

            update_payments_sql = f"""
                UPDATE TblSnSalesPayWay
                SET
                    SalesPWInitDate = ?
                WHERE SalesPWPosHdr IN (
                    {placeholders}
                )
                  AND SalesPWInitDate = ?
            """

            cursor.execute(
                update_payments_sql,
                new_date,
                *pos_headers,
                source_date,
            )

            payments_affected = cursor.rowcount

            database.commit()

            return {
                "success": True,
                "affected_rows": (
                    sales_affected
                    + payments_affected
                ),
                "sales_rows": sales_affected,
                "payment_rows": payments_affected,
                "message": (
                    f"{len(pos_headers)} selected "
                    "transaction(s) transferred "
                    f"from "
                    f"{source_date.strftime('%d/%m/%Y')} "
                    "to "
                    f"{new_date.strftime('%d/%m/%Y')}."
                ),
            }

        except Exception as error:

            try:
                database.rollback()
            except Exception:
                pass

            return {
                "success": False,
                "affected_rows": 0,
                "message": (
                    "Transaction transfer failed. "
                    "All changes were rolled back."
                    f"\n\n{error}"
                ),
            }

        finally:
            cursor.close()
            database.close()

    def change_restaurant_date(
        self,
        new_date: date,
    ) -> dict:
        if new_date is None:
            return {
                "success": False,
                "message": "New restaurant date is required.",
            }

        database = self._get_connection()

        try:
            cursor = database.cursor()

            cursor.execute(
                self.CURRENT_DATE_SQL
            )

            row = cursor.fetchone()

            if row is None:
                raise RuntimeError(
                    "Current restaurant date was not found."
                )

            station_oid = row.SalesStationOID
            current_value = row.SalesStationRestDate

            if station_oid is None:
                raise RuntimeError(
                    "Restaurant station record was not found."
                )

            if isinstance(current_value, datetime):
                current_date = current_value.date()
            elif isinstance(current_value, date):
                current_date = current_value
            else:
                raise RuntimeError(
                    "Invalid restaurant date returned by the database."
                )

            if current_date == new_date:
                return {
                    "success": False,
                    "message": (
                        "Current and new restaurant dates are the same."
                    ),
                }

            update_sql = """
                UPDATE TblSnSalesStation
                SET SalesStationRestDate = ?
                WHERE SalesStationOID = ?
            """

            cursor.execute(
                update_sql,
                new_date,
                station_oid,
            )

            affected_rows = cursor.rowcount

            if affected_rows <= 0:
                raise RuntimeError(
                    "The restaurant date could not be updated."
                )

            database.commit()

            return {
                "success": True,
                "affected_rows": affected_rows,
                "message": (
                    "Restaurant date changed successfully "
                    f"from {current_date.strftime('%d/%m/%Y')} "
                    "to "
                    f"{new_date.strftime('%d/%m/%Y')}."
                ),
            }

        except Exception as error:
            try:
                database.rollback()
            except Exception:
                pass

            return {
                "success": False,
                "affected_rows": 0,
                "message": (
                    "Restaurant date change failed. "
                    "All changes were rolled back."
                    f"\n\n{error}"
                ),
            }

        finally:
            try:
                cursor.close()
            except Exception:
                pass

            database.close()

    def transfer_all(
        self,
        old_date: date,
        new_date: date,
    ) -> dict:
        if old_date is None:
            return {
                "success": False,
                "affected_rows": 0,
                "message": "Old restaurant date is required.",
            }

        if new_date is None:
            return {
                "success": False,
                "affected_rows": 0,
                "message": "New restaurant date is required.",
            }

        if old_date == new_date:
            return {
                "success": False,
                "affected_rows": 0,
                "message": (
                    "Source and destination restaurant "
                    "dates are the same."
                ),
            }

        database = self._get_connection()

        try:
            cursor = database.cursor()

            # --------------------------------------------------
            # STEP 1: UPDATE PAYMENTS
            # --------------------------------------------------
            update_payments_sql = """
                UPDATE TblSnSalesPayWay
                SET
                    SalesPWInitDate = ?
                WHERE SalesPWPosHdr IN (
                    SELECT
                        SalesTransPosHdr
                    FROM TblSnSalesPayWay w WITH (NOLOCK)
                    INNER JOIN TblSnSalesTransPos p WITH (NOLOCK)
                        ON w.SalesPWPosHdr = p.SalesTransPosHdr
                    INNER JOIN TblSnSalesTrans s WITH (NOLOCK)
                        ON p.SalesTransOID = s.SalesTransOID
                    WHERE s.SalesTransInitDate = ?
                )
                  AND SalesPWInitDate = ?
            """

            cursor.execute(
                update_payments_sql,
                new_date,
                old_date,
                old_date,
            )
            payments_affected = cursor.rowcount

            # --------------------------------------------------
            # STEP 2: UPDATE SALES
            # --------------------------------------------------
            update_sales_sql = """
                UPDATE TblSnSalesTrans
                SET
                    SalesTransInitDate = ?
                WHERE SalesTransInitDate = ?
            """

            cursor.execute(
                update_sales_sql,
                new_date,
                old_date,
            )
            sales_affected = cursor.rowcount

            # --------------------------------------------------
            # STEP 3: UPDATE MOVEMENTS / TRANSFERS
            # --------------------------------------------------
            update_movements_sql = """
                UPDATE TblSnSalesTransfers
                SET
                    SalesTransfersInitDate = ?
                WHERE SalesTransfersInitDate = ?
            """

            cursor.execute(
                update_movements_sql,
                new_date,
                old_date,
            )
            movements_affected = cursor.rowcount

            # --------------------------------------------------
            # COMMIT EVERYTHING TOGETHER
            # --------------------------------------------------
            database.commit()

            print(
                "[ChangeDate] Transfer All committed.",
                flush=True,
            )
            print(
                "[ChangeDate] Source date:",
                old_date,
                flush=True,
            )
            print(
                "[ChangeDate] Destination date:",
                new_date,
                flush=True,
            )
            print(
                "[ChangeDate] Payment rows updated:",
                payments_affected,
                flush=True,
            )
            print(
                "[ChangeDate] Sales rows updated:",
                sales_affected,
                flush=True,
            )
            print(
                "[ChangeDate] Movement rows updated:",
                movements_affected,
                flush=True,
            )

            return {
                "success": True,
                "affected_rows": (
                    payments_affected
                    + sales_affected
                    + movements_affected
                ),
                "payment_rows": payments_affected,
                "sales_rows": sales_affected,
                "movement_rows": movements_affected,
                "message": (
                    "All records were transferred "
                    f"from {old_date.strftime('%d/%m/%Y')} "
                    "to "
                    f"{new_date.strftime('%d/%m/%Y')}."
                ),
            }

        except Exception as error:
            try:
                database.rollback()
            except Exception:
                pass

            print(
                "[ChangeDate] Transfer All ROLLBACK.",
                flush=True,
            )
            print(
                "[ChangeDate] Error:",
                error,
                flush=True,
            )

            return {
                "success": False,
                "affected_rows": 0,
                "message": (
                    "Transfer All failed. "
                    "All changes were rolled back."
                    f"\n\n{error}"
                ),
            }

        finally:
            try:
                cursor.close()
            except Exception:
                pass

            database.close()