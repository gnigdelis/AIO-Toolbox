from __future__ import annotations

from dataclasses import dataclass

from core.database.database_connection import DatabaseConnection
from core.database.database_context import database_context


@dataclass
class SQLToolResult:
    success: bool
    message: str
    affected_rows: int = 0


class SQLToolsService:
    """
    SQL maintenance operations for the currently selected database.
    """

    DELETE_MYDATA_SQL = """
        DELETE FROM TblSnMyDATA_Response
        WHERE MyDATA_ResponseStatusCode <> 'Success'
    """

    REBUILD_DATABASE_SQL = """
        EXEC SPSnRebuildUpdate
    """

    SHRINK_DATABASE_SQL = """
        DBCC SHRINKDATABASE (0,10)
    """

    FAILED_MYDATA_PAYMENTS_SQL = """
        Declare @KeepFalseRecsWithMArK Bit

        Set @KeepFalseRecsWithMArK = 0

        Create Table #PosHdrWithMark (
            PosHdr Integer Primary Key
        )

        Insert Into #PosHdrWithMark
        Select Distinct
            MyDATA_ResponsePaymentsSalesTransPosHdr
        From
            TblSnMyDATA_ResponsePayments
        Where
            MyDATA_ResponsePaymentsSalesTransPosHdr Is Not Null
            And MyDATA_ResponsePaymentsPaymentMArK Is Not Null
            And MyDATA_ResponsePaymentsPaymentMArK <> ''

        If (@KeepFalseRecsWithMArK = 0)
        Begin

            Delete rps
            From
                TblSnMyDATA_ResponsePaymentsSignatures rps
            Inner Join
                TblSnMyDATA_ResponsePayments rp
                On rps.MyDATA_ResponsePaymentsOID =
                   rp.MyDATA_ResponsePaymentsOID
            Inner Join
                #PosHdrWithMark phm
                On phm.PosHdr =
                   rp.MyDATA_ResponsePaymentsSalesTransPosHdr
            Where
                rp.MyDATA_ResponsePaymentsPaymentMArK Is Null
                Or rp.MyDATA_ResponsePaymentsPaymentMArK = ''

            Delete rp
            From
                TblSnMyDATA_ResponsePayments rp
            Inner Join
                #PosHdrWithMark phm
                On phm.PosHdr =
                   rp.MyDATA_ResponsePaymentsSalesTransPosHdr
            Where
                rp.MyDATA_ResponsePaymentsPaymentMArK Is Null
                Or rp.MyDATA_ResponsePaymentsPaymentMArK = ''

        End

        Create Table #RecordsToKeep (
            PosHdr Integer,
            LastOID Integer Primary Key
        )

        Insert Into #RecordsToKeep
        Select
            MyDATA_ResponsePaymentsSalesTransPosHdr,
            LastOID = Max(MyDATA_ResponsePaymentsOID)
        From
            TblSnMyDATA_ResponsePayments
        Where
            MyDATA_ResponsePaymentsSalesTransPosHdr Not In (
                Select PosHdr
                From #PosHdrWithMark
            )
            And (
                MyDATA_ResponsePaymentsPaymentMArK Is Null
                Or MyDATA_ResponsePaymentsPaymentMArK = ''
            )
        Group By
            MyDATA_ResponsePaymentsSalesTransPosHdr

        Delete rps
        From
            TblSnMyDATA_ResponsePaymentsSignatures rps
        Inner Join
            TblSnMyDATA_ResponsePayments rp
            On rps.MyDATA_ResponsePaymentsOID =
               rp.MyDATA_ResponsePaymentsOID
        Where
            rp.MyDATA_ResponsePaymentsOID In (
                Select
                    rp.MyDATA_ResponsePaymentsOID
                From
                    TblSnMyDATA_ResponsePayments rp
                Where
                    (
                        rp.MyDATA_ResponsePaymentsPaymentMArK Is Null
                        Or rp.MyDATA_ResponsePaymentsPaymentMArK = ''
                    )
                    And rp.MyDATA_ResponsePaymentsSalesTransPosHdr Not In (
                        Select PosHdr
                        From #PosHdrWithMark
                    )
                    And rp.MyDATA_ResponsePaymentsOID Not In (
                        Select LastOID
                        From #RecordsToKeep
                    )
            )

        Delete
        From
            TblSnMyDATA_ResponsePayments
        Where
            MyDATA_ResponsePaymentsOID In (
                Select
                    rp.MyDATA_ResponsePaymentsOID
                From
                    TblSnMyDATA_ResponsePayments rp
                Where
                    (
                        rp.MyDATA_ResponsePaymentsPaymentMArK Is Null
                        Or rp.MyDATA_ResponsePaymentsPaymentMArK = ''
                    )
                    And rp.MyDATA_ResponsePaymentsSalesTransPosHdr Not In (
                        Select PosHdr
                        From #PosHdrWithMark
                    )
                    And rp.MyDATA_ResponsePaymentsOID Not In (
                        Select LastOID
                        From #RecordsToKeep
                    )
            )

        Drop Table #PosHdrWithMark
        Drop Table #RecordsToKeep
    """

    # ==============================================================
    # DATABASE CAPABILITY CHECK
    # ==============================================================

    def supports_failed_mydata_payments(self) -> bool:
        """
        Check whether the active database contains the tables
        required by Delete Failed MyDATA Payments.
        """

        connection = None
        cursor = None

        try:
            connection = self._connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT CASE
                    WHEN OBJECT_ID(
                        N'dbo.TblSnMyDATA_ResponsePayments',
                        N'U'
                    ) IS NOT NULL
                    AND OBJECT_ID(
                        N'dbo.TblSnMyDATA_ResponsePaymentsSignatures',
                        N'U'
                    ) IS NOT NULL
                    THEN 1
                    ELSE 0
                END
                """
            )

            row = cursor.fetchone()

            return bool(row and row[0])

        except Exception:
            return False

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

    # ==============================================================
    # DELETE FAILED MYDATA PAYMENTS
    # ==============================================================

    def delete_failed_mydata_payments(self) -> SQLToolResult:
        """
        Execute the real Delete Failed MyDATA Payments cleanup.

        The operation is available only on database versions
        that contain the required MyDATA payment tables.
        """

        if not self.supports_failed_mydata_payments():
            raise RuntimeError(
                "Η λειτουργία Delete Failed MyDATA Payments "
                "δεν υποστηρίζεται από αυτή την έκδοση "
                "της βάσης δεδομένων."
            )

        connection = None
        cursor = None

        try:
            connection = self._connect()
            cursor = connection.cursor()

            cursor.execute(
                self.FAILED_MYDATA_PAYMENTS_SQL
            )

            while cursor.nextset():
                pass

            connection.commit()

            return SQLToolResult(
                success=True,
                message=(
                    "Η διαγραφή των Failed MyDATA Payments "
                    "ολοκληρώθηκε επιτυχώς."
                ),
            )

        except Exception as exc:

            if connection is not None:
                try:
                    connection.rollback()
                except Exception:
                    pass

            raise RuntimeError(
                "Η διαγραφή των Failed MyDATA Payments απέτυχε.\n\n"
                f"{exc}"
            ) from exc

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

    # ==============================================================
    # DATABASE INFORMATION
    # ==============================================================

    def database_info(self) -> dict:
        """
        Return information about the currently selected database.
        """

        database = database_context.active()

        if not database:
            return {
                "selected": False,
                "connected": False,
                "database": None,
                "name": None,
                "database_name": None,
                "server": None,
                "server_name": None,
                "path": "",
                "udl": "",
                "udl_path": "",
            }

        name = (
            database.get("name")
            or database.get("database_name")
            or "Unknown"
        )

        server = (
            database.get("server")
            or database.get("server_name")
            or "Unknown"
        )

        path = (
            database.get("path")
            or database.get("udl")
            or database.get("udl_path")
            or ""
        )

        return {
            "selected": True,
            "connected": True,
            "database": name,
            "name": name,
            "database_name": name,
            "server": server,
            "server_name": server,
            "path": path,
            "udl": path,
            "udl_path": path,
        }

    # ==============================================================
    # CONNECTION
    # ==============================================================

    def _get_udl_path(self) -> str:
        """
        Return the UDL path of the currently selected database.
        """

        udl_path = database_context.active_udl()

        if not udl_path:
            raise RuntimeError(
                "Δεν έχει επιλεγεί ενεργή βάση δεδομένων."
            )

        return udl_path

    def _connect(self):
        """
        Create a connection to the currently selected database.
        """

        return DatabaseConnection(
            self._get_udl_path()
        ).connect()

    # ==============================================================
    # DELETE MYDATA RESPONSE
    # ==============================================================

    def delete_mydata_response(self) -> SQLToolResult:
        """
        Delete all MyDATA response records whose status
        is different from 'Success'.
        """

        connection = None
        cursor = None

        try:
            connection = self._connect()
            cursor = connection.cursor()

            cursor.execute(
                self.DELETE_MYDATA_SQL
            )

            affected_rows = cursor.rowcount

            connection.commit()

            return SQLToolResult(
                success=True,
                message=(
                    "Η διαγραφή των MyDATA responses "
                    "ολοκληρώθηκε επιτυχώς."
                ),
                affected_rows=(
                    affected_rows
                    if affected_rows is not None
                    and affected_rows >= 0
                    else 0
                ),
            )

        except Exception as exc:

            if connection is not None:
                try:
                    connection.rollback()
                except Exception:
                    pass

            raise RuntimeError(
                "Η διαγραφή των MyDATA responses απέτυχε.\n\n"
                f"{exc}"
            ) from exc

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

    # ==============================================================
    # REBUILD DATABASE
    # ==============================================================

    def rebuild_database(self) -> SQLToolResult:
        """
        Execute the real SPSnRebuildUpdate stored procedure.
        """

        connection = None
        cursor = None

        try:
            connection = self._connect()
            cursor = connection.cursor()

            cursor.execute(
                self.REBUILD_DATABASE_SQL
            )

            while cursor.nextset():
                pass

            connection.commit()

            return SQLToolResult(
                success=True,
                message=(
                    "Το Rebuild της βάσης "
                    "ολοκληρώθηκε επιτυχώς."
                ),
            )

        except Exception as exc:

            if connection is not None:
                try:
                    connection.rollback()
                except Exception:
                    pass

            raise RuntimeError(
                "Το Rebuild της βάσης απέτυχε.\n\n"
                f"{exc}"
            ) from exc

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

    # ==============================================================
    # SHRINK DATABASE
    # ==============================================================

    def shrink_database(self) -> SQLToolResult:
        """
        Execute the real SQL Server Shrink command.
        """

        connection = None
        cursor = None

        try:
            connection = DatabaseConnection(
                self._get_udl_path()
            ).connect(
                autocommit=True
            )

            cursor = connection.cursor()

            cursor.execute(
                self.SHRINK_DATABASE_SQL
            )

            while cursor.nextset():
                pass

            return SQLToolResult(
                success=True,
                message=(
                    "Το Shrink Database "
                    "ολοκληρώθηκε επιτυχώς."
                ),
            )

        except Exception as exc:

            raise RuntimeError(
                "Το Shrink Database απέτυχε.\n\n"
                f"{exc}"
            ) from exc

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