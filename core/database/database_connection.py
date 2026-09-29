from __future__ import annotations

from typing import Any

import pyodbc

from core.database.udl_reader import UDLReader


class DatabaseConnection:
    """Creates SQL Server connections from a UDL file or remote profile."""

    def __init__(self, udl_path: str):
        self.reader = UDLReader(udl_path)

        print(
            "UDL:",
            udl_path,
            flush=True,
        )
        print(
            "Database:",
            self.reader.get_database_name(),
            flush=True,
        )
        print(
            "Server:",
            self.reader.get_server_name(),
            flush=True,
        )

        self.connection_string = (
            self.reader.get_connection_string()
        )

    @classmethod
    def from_remote(
        cls,
        server: str,
        database: str,
        username: str,
        password: str,
        driver: str = "ODBC Driver 17 for SQL Server",
        encrypt: bool = False,
        trust_server_certificate: bool = True,
    ) -> "DatabaseConnection":
        """
        Creates a SQL Server connection directly from remote settings.

        This does not require a UDL file.

        The profile is kept only in memory by this object.
        """

        instance = cls.__new__(cls)

        instance.reader = None

        instance._remote_server = server
        instance._remote_database = database
        instance._remote_username = username

        encrypt_value = "Yes" if encrypt else "No"
        trust_value = (
            "Yes"
            if trust_server_certificate
            else "No"
        )

        instance.connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"Encrypt={encrypt_value};"
            f"TrustServerCertificate={trust_value};"
        )

        return instance

    def connect(self, autocommit: bool = False):
        return pyodbc.connect(
            self.connection_string,
            autocommit=autocommit,
        )

    def server_name(self) -> str:
        if self.reader is not None:
            return self.reader.get_server_name()

        return getattr(
            self,
            "_remote_server",
            "",
        )

    def database_name(self) -> str:
        if self.reader is not None:
            return self.reader.get_database_name()

        return getattr(
            self,
            "_remote_database",
            "",
        )

    def connection_type(self) -> str:
        if self.reader is not None:
            return "udl"

        return "remote"

    def info(self) -> dict[str, Any]:
        return {
            "type": self.connection_type(),
            "server": self.server_name(),
            "database": self.database_name(),
            "username": getattr(
                self,
                "_remote_username",
                "",
            ),
        }
