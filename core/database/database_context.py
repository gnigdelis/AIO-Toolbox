from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal

from core.database.udl_reader import UDLReader


class DatabaseContext(QObject):
    """Keeps track of the database currently selected by the user."""

    database_changed = Signal(object)

    def __init__(self):
        super().__init__()

        self._active_udl: dict | None = None
        self._active_remote: dict | None = None

    def select(self, udl_path: str | Path) -> dict:
        path = Path(udl_path).expanduser().resolve()

        reader = UDLReader(str(path))

        database = {
            "type": "udl",
            "path": str(path),
            "name": reader.get_database_name(),
            "server": reader.get_server_name(),
        }

        self._active_udl = database
        self._active_remote = None

        self.database_changed.emit(database)

        return database

    def select_remote(
        self,
        server: str,
        database: str,
        username: str,
        password: str,
        driver: str = "ODBC Driver 17 for SQL Server",
        encrypt: bool = False,
        trust_server_certificate: bool = True,
        store_name: str = "",
    ) -> dict:
        """
        Selects a remote SQL Server connection.

        Credentials are kept only in memory for now.
        They are not written to disk by this method.
        """

        remote = {
            "type": "remote",
            "store_name": store_name,
            "server": server,
            "name": database,
            "database": database,
            "username": username,
            "password": password,
            "driver": driver,
            "encrypt": encrypt,
            "trust_server_certificate": (
                trust_server_certificate
            ),
        }

        self._active_remote = remote
        self._active_udl = None

        self.database_changed.emit(remote)

        return {
            "type": remote["type"],
            "store_name": remote["store_name"],
            "server": remote["server"],
            "name": remote["name"],
            "database": remote["database"],
            "username": remote["username"],
        }

    def clear(self) -> None:
        self._active_udl = None
        self._active_remote = None

        self.database_changed.emit(None)

    def active(self) -> dict | None:
        if self._active_remote is not None:
            return {
                "type": self._active_remote["type"],
                "store_name": self._active_remote["store_name"],
                "server": self._active_remote["server"],
                "name": self._active_remote["name"],
                "database": self._active_remote["database"],
                "username": self._active_remote["username"],
            }

        return self._active_udl

    def active_udl(self) -> str | None:
        if not self._active_udl:
            return None

        return self._active_udl["path"]

    def active_remote(self) -> dict | None:
        if self._active_remote is None:
            return None

        return dict(self._active_remote)

    def is_selected(self) -> bool:
        return (
            self._active_udl is not None
            or self._active_remote is not None
        )

    def is_remote(self) -> bool:
        return self._active_remote is not None

    def is_udl(self) -> bool:
        return self._active_udl is not None


database_context = DatabaseContext()
