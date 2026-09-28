import pyodbc

from core.database.udl_reader import UDLReader


class DatabaseConnection:
    """Creates SQL Server connections from a UDL file."""

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

    def connect(self, autocommit: bool = False):
        return pyodbc.connect(
            self.connection_string,
            autocommit=autocommit,
        )

    def server_name(self) -> str:
        return self.reader.get_server_name()

    def database_name(self) -> str:
        return self.reader.get_database_name()