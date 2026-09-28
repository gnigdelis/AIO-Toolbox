from pathlib import Path


class UDLReader:
    """Reads a Microsoft UDL file and converts it to an ODBC connection string."""

    def __init__(self, udl_path: str):
        self.udl_path = Path(udl_path)

    def _read_lines(self) -> list[str]:
        if not self.udl_path.exists():
            raise FileNotFoundError(
                f"UDL file not found: {self.udl_path}"
            )

        for encoding in (
            "utf-16",
            "utf-8",
            "latin-1",
        ):
            try:
                return self.udl_path.read_text(
                    encoding=encoding
                ).splitlines()
            except UnicodeError:
                continue

        raise RuntimeError(
            "Unable to read UDL file."
        )

    def read(self) -> str:
        for line in self._read_lines():
            line = line.strip()

            if not line:
                continue

            if line.startswith(";"):
                continue

            if line.lower() == "[oledb]":
                continue

            if line.startswith("Provider="):
                return line

        raise RuntimeError(
            "Invalid UDL file."
        )

    def get_connection_string(self) -> str:
        connection = self.read()

        # Remove OLEDB Provider.
        connection = connection.replace(
            "Provider=SQLOLEDB.1;",
            "",
        )

        # OLEDB -> ODBC.
        connection = connection.replace(
            "Data Source=",
            "SERVER=",
        )

        connection = connection.replace(
            "Initial Catalog=",
            "DATABASE=",
        )

        connection = connection.replace(
            "User ID=",
            "UID=",
        )

        connection = connection.replace(
            "Password=",
            "PWD=",
        )

        # Build ODBC connection string.
        conn = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            + connection
        )

        return conn

    def get_database_name(self) -> str:
        connection = self.read()

        for item in connection.split(";"):
            if item.startswith("Initial Catalog="):
                return item.replace(
                    "Initial Catalog=",
                    "",
                )

        return ""

    def get_server_name(self) -> str:
        connection = self.read()

        for item in connection.split(";"):
            if item.startswith("Data Source="):
                return item.replace(
                    "Data Source=",
                    "",
                )

        return ""