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

    def select(self, udl_path: str | Path) -> dict:
        path = Path(udl_path).expanduser().resolve()

        reader = UDLReader(str(path))

        database = {
            "path": str(path),
            "name": reader.get_database_name(),
            "server": reader.get_server_name(),
        }

        self._active_udl = database

        self.database_changed.emit(database)

        return database

    def clear(self) -> None:
        self._active_udl = None
        self.database_changed.emit(None)

    def active(self) -> dict | None:
        return self._active_udl

    def active_udl(self) -> str | None:
        if not self._active_udl:
            return None

        return self._active_udl["path"]

    def is_selected(self) -> bool:
        return self._active_udl is not None


database_context = DatabaseContext()