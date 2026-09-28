from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pyodbc

from core.database.database_connection import DatabaseConnection
from core.database.udl_reader import UDLReader


@dataclass
class BackupResult:
    success: bool
    database_name: str
    backup_path: str
    message: str


class BackupService:
    """Creates SQL Server database backups."""

    def backup_database(
        self,
        udl_path: str,
        destination_folder: str | None = None,
    ) -> BackupResult:

        reader = UDLReader(
            udl_path
        )

        database_name = (
            reader.get_database_name().strip()
        )

        server_name = (
            reader.get_server_name().strip()
        )

        if not database_name:
            raise RuntimeError(
                "The selected UDL does not contain a database name."
            )

        if not server_name:
            raise RuntimeError(
                "The selected UDL does not contain a SQL Server name."
            )

        connection = DatabaseConnection(
            udl_path
        )

        cn = None

        try:
            cn = connection.connect(
                autocommit=True
            )

            cursor = cn.cursor()

            cursor.execute(
                """
                SELECT SERVERPROPERTY(
                    'InstanceDefaultBackupPath'
                )
                """
            )

            row = cursor.fetchone()

            if not row or not row[0]:
                raise RuntimeError(
                    "SQL Server did not return its default backup folder."
                )

            backup_folder = Path(
                str(row[0]).strip()
            )

            if not backup_folder.exists():
                raise RuntimeError(
                    "The SQL Server backup folder does not exist.\n\n"
                    f"Folder:\n{backup_folder}"
                )

            if not backup_folder.is_dir():
                raise RuntimeError(
                    "The SQL Server backup path is not a folder.\n\n"
                    f"Path:\n{backup_folder}"
                )

            backup_path = (
                backup_folder
                / f"{database_name}.bak"
            )

            sql_database = database_name.replace(
                "]",
                "]]",
            )

            sql_database_literal = (
                database_name.replace(
                    "'",
                    "''",
                )
            )

            sql = f"""
DECLARE @backup_folder nvarchar(4000);
DECLARE @backup_path nvarchar(4000);

SELECT @backup_folder =
    CAST(
        SERVERPROPERTY('InstanceDefaultBackupPath')
        AS nvarchar(4000)
    );

SET @backup_path =
    @backup_folder
    + NCHAR(92)
    + N'{sql_database_literal}'
    + N'.bak';

BACKUP DATABASE [{sql_database}]
TO DISK = @backup_path
WITH INIT, STATS = 10;
"""

            try:
                cursor.execute(
                    sql
                )

                while cursor.nextset():
                    pass

            except pyodbc.Error as exc:
                raise RuntimeError(
                    "SQL Server could not create the backup.\n\n"
                    f"Server: {server_name}\n"
                    f"Database: {database_name}\n"
                    f"Backup file:\n{backup_path}\n\n"
                    f"SQL error:\n{exc}"
                ) from exc

            finally:
                cursor.close()

            if not backup_path.exists():
                raise RuntimeError(
                    "SQL Server completed the backup command, "
                    "but the backup file was not created.\n\n"
                    f"Expected file:\n{backup_path}"
                )

            backup_size = (
                backup_path.stat().st_size
            )

            if backup_size <= 0:
                raise RuntimeError(
                    "The backup file was created, "
                    "but its size is zero.\n\n"
                    f"Backup file:\n{backup_path}"
                )

            return BackupResult(
                success=True,
                database_name=database_name,
                backup_path=str(
                    backup_path
                ),
                message=(
                    "Database backup completed successfully.\n\n"
                    f"Server: {server_name}\n"
                    f"Database: {database_name}\n"
                    f"Backup file:\n{backup_path}\n\n"
                    f"Backup size: {backup_size:,} bytes"
                ),
            )

        finally:
            if cn is not None:
                cn.close()