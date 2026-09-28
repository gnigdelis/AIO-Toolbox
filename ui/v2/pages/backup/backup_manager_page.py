from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.backup.backup_service import (
    BackupResult,
    BackupService,
)
from core.database.database_context import database_context

from ui.v2.widgets.page_layout import (
    PAGE_LAYOUT_STYLE,
    setup_page_layout,
)


class BackupWorker(QThread):
    """Runs the database backup outside the Qt GUI thread."""

    finished_result = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        service: BackupService,
        udl_path: str,
    ) -> None:
        super().__init__()

        self.service = service
        self.udl_path = udl_path

    def run(self) -> None:
        try:
            result = self.service.backup_database(
                udl_path=self.udl_path,
            )

            self.finished_result.emit(
                result
            )

        except Exception as exc:
            self.failed.emit(
                str(exc)
            )


class BackupManagerPage(QWidget):
    """AIO Toolbox Backup Manager page."""

    def __init__(self) -> None:
        super().__init__()

        self.service = BackupService()
        self.worker: BackupWorker | None = None

        self._build_ui()
        self._connect_signals()
        self._update_database_info()

    def _build_ui(self) -> None:
        root, title, subtitle = setup_page_layout(
            self,
            "Backup Manager",
            "Create a full backup of the currently selected database.",
        )

        database_card = QFrame()
        database_card.setObjectName(
            "contentCard"
        )

        database_layout = QVBoxLayout(
            database_card
        )

        database_layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )

        database_layout.setSpacing(
            10
        )

        database_title = QLabel(
            "Selected Database"
        )
        database_title.setObjectName(
            "sectionTitle"
        )

        self.database_label = QLabel(
            "No database selected"
        )
        self.database_label.setObjectName(
            "fieldValue"
        )

        self.server_label = QLabel(
            "Server: —"
        )
        self.server_label.setObjectName(
            "fieldValue"
        )

        self.udl_label = QLabel(
            "UDL: —"
        )
        self.udl_label.setObjectName(
            "fieldValue"
        )

        self.udl_label.setWordWrap(
            True
        )

        database_layout.addWidget(
            database_title
        )

        database_layout.addWidget(
            self.database_label
        )

        database_layout.addWidget(
            self.server_label
        )

        database_layout.addWidget(
            self.udl_label
        )

        root.addWidget(
            database_card
        )

        destination_card = QFrame()
        destination_card.setObjectName(
            "contentCard"
        )

        destination_layout = QVBoxLayout(
            destination_card
        )

        destination_layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )

        destination_layout.setSpacing(
            10
        )

        destination_title = QLabel(
            "Backup Destination"
        )
        destination_title.setObjectName(
            "sectionTitle"
        )

        self.destination_label = QLabel(
            "SQL Server default backup folder"
        )
        self.destination_label.setObjectName(
            "fieldValue"
        )

        self.destination_label.setWordWrap(
            True
        )

        destination_info = QLabel(
            "The .bak backup is created directly in the "
            "SQL Server instance's default backup folder."
        )
        destination_info.setObjectName(
            "summaryText"
        )

        destination_info.setWordWrap(
            True
        )

        destination_layout.addWidget(
            destination_title
        )

        destination_layout.addWidget(
            self.destination_label
        )

        destination_layout.addWidget(
            destination_info
        )

        root.addWidget(
            destination_card
        )

        action_frame = QFrame()
        action_frame.setObjectName(
            "summaryFrame"
        )

        action_layout = QHBoxLayout(
            action_frame
        )

        action_layout.setContentsMargins(
            18,
            16,
            18,
            16,
        )

        action_layout.setSpacing(
            12
        )

        self.status_label = QLabel(
            "Ready"
        )
        self.status_label.setObjectName(
            "summaryText"
        )

        self.backup_button = QPushButton(
            "BACKUP NOW"
        )
        self.backup_button.setObjectName(
            "primaryButton"
        )

        self.backup_button.setMinimumHeight(
            42
        )

        self.backup_button.setMinimumWidth(
            150
        )

        action_layout.addWidget(
            self.status_label
        )

        action_layout.addStretch()

        action_layout.addWidget(
            self.backup_button
        )

        root.addWidget(
            action_frame
        )

        root.addStretch()

        self.setStyleSheet(
            PAGE_LAYOUT_STYLE
        )

    def _connect_signals(self) -> None:
        self.backup_button.clicked.connect(
            self._start_backup
        )

        database_context.database_changed.connect(
            self._on_database_changed
        )

    def _on_database_changed(
        self,
        database: object,
    ) -> None:
        self._update_database_info()

    def _update_database_info(self) -> None:
        database = database_context.active()

        if not database:
            self.database_label.setText(
                "No database selected"
            )

            self.server_label.setText(
                "Server: —"
            )

            self.udl_label.setText(
                "UDL: —"
            )

            self.destination_label.setText(
                "SQL Server default backup folder"
            )

            self.backup_button.setEnabled(
                False
            )

            self.status_label.setText(
                "Connect to a database first."
            )

            return

        database_name = (
            database.get("name")
            or database.get("database")
            or "Unknown database"
        )

        server_name = (
            database.get("server")
            or "Unknown server"
        )

        udl_path = (
            database.get("udl_path")
            or database.get("udl")
            or database.get("path")
            or ""
        )

        self.database_label.setText(
            f"Database: {database_name}"
        )

        self.server_label.setText(
            f"Server: {server_name}"
        )

        self.udl_label.setText(
            f"UDL: {udl_path or '—'}"
        )

        self.backup_button.setEnabled(
            bool(udl_path)
        )

        self.status_label.setText(
            "Ready"
        )

    def _start_backup(self) -> None:
        database = database_context.active()

        if not database:
            QMessageBox.warning(
                self,
                "Database Required",
                "Please connect to a database first.",
            )
            return

        udl_path = (
            database.get("udl_path")
            or database.get("udl")
            or database.get("path")
            or ""
        )

        if not udl_path:
            QMessageBox.warning(
                self,
                "UDL Required",
                "The selected database does not have a valid UDL path.",
            )
            return

        if self.worker is not None:
            return

        self.backup_button.setEnabled(
            False
        )

        self.backup_button.setText(
            "BACKING UP..."
        )

        self.status_label.setText(
            "Creating database backup..."
        )

        self.worker = BackupWorker(
            service=self.service,
            udl_path=str(udl_path),
        )

        self.worker.finished_result.connect(
            self._on_backup_finished
        )

        self.worker.failed.connect(
            self._on_backup_failed
        )

        self.worker.finished.connect(
            self._cleanup_worker
        )

        self.worker.start()

    def _on_backup_finished(
        self,
        result: object,
    ) -> None:
        if not isinstance(
            result,
            BackupResult,
        ):
            self._on_backup_failed(
                "The backup service returned an invalid result."
            )
            return

        self.destination_label.setText(
            result.backup_path
        )

        self.status_label.setText(
            "Backup completed successfully."
        )

        self.backup_button.setText(
            "BACKUP NOW"
        )

        QMessageBox.information(
            self,
            "Backup Completed",
            result.message,
        )

        self.backup_button.setEnabled(
            True
        )

    def _on_backup_failed(
        self,
        message: str,
    ) -> None:
        self.status_label.setText(
            "Backup failed."
        )

        self.backup_button.setText(
            "BACKUP NOW"
        )

        self.backup_button.setEnabled(
            True
        )

        QMessageBox.critical(
            self,
            "Backup Failed",
            (
                "The database backup could not be completed.\n\n"
                f"{message}"
            ),
        )

    def _cleanup_worker(self) -> None:
        worker = self.worker

        if worker is None:
            return

        worker.deleteLater()
        self.worker = None