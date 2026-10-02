from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtCore import QThread, QTime, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from core.backup.backup_engine import BackupEngine
from core.configuration.settings_manager import SettingsManager
from core.configuration.windows_task_scheduler import WindowsTaskScheduler
from core.database.database_context import database_context

from ui.v2.widgets.page_layout import (
    PAGE_LAYOUT_STYLE,
    setup_page_layout,
)


def _app_base_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[3]


class BackupWorker(QThread):
    finished_result = Signal(object)
    failed = Signal(str)
    progress = Signal(int, str)

    def __init__(
        self,
        destination: str,
        selected_targets: dict[str, bool],
    ) -> None:
        super().__init__()

        self.destination = destination
        self.selected_targets = selected_targets

    def run(self) -> None:
        try:
            engine = BackupEngine(
                base_path=self.destination,
                progress_callback=(
                    lambda percentage, message:
                    self.progress.emit(
                        percentage,
                        message,
                    )
                ),
            )

            self.finished_result.emit(
                engine.run(
                    self.selected_targets
                )
            )

        except Exception as exc:
            self.failed.emit(
                str(exc)
            )


class BackupManagerPage(QWidget):

    def __init__(self) -> None:
        super().__init__()

        self.worker: BackupWorker | None = None

        self.settings_manager = SettingsManager(
            _app_base_path()
            / "config"
            / "settings.json"
        )

        self.settings = (
            self.settings_manager.load()
        )

        self.scheduler_manager = (
            WindowsTaskScheduler(
                _app_base_path()
            )
        )

        self._build_ui()
        self._connect_signals()
        self._load_settings()
        self._update_database_info()

    # ================================================================
    # UI
    # ================================================================

    def _build_ui(self) -> None:

        root, _, _ = setup_page_layout(
            self,
            "Backup Manager",
            "Create a complete backup of the selected system components.",
        )

        # ------------------------------------------------------------
        # Database
        # ------------------------------------------------------------

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
            8
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

        self.server_label = QLabel(
            "Server: β€”"
        )

        self.udl_label = QLabel(
            "UDL: β€”"
        )

        self.udl_label.setWordWrap(
            True
        )

        for widget in (
            database_title,
            self.database_label,
            self.server_label,
            self.udl_label,
        ):
            database_layout.addWidget(
                widget
            )

        root.addWidget(
            database_card
        )

        # ------------------------------------------------------------
        # Components
        # ------------------------------------------------------------

        components_card = QFrame()
        components_card.setObjectName(
            "contentCard"
        )

        components_layout = QVBoxLayout(
            components_card
        )

        components_layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )

        components_layout.setSpacing(
            7
        )

        components_title = QLabel(
            "Backup Components"
        )

        components_title.setObjectName(
            "sectionTitle"
        )

        components_layout.addWidget(
            components_title
        )

        self.configuration_checkbox = QCheckBox(
            "Configuration Files"
        )

        self.form_path_checkbox = QCheckBox(
            r"C:\form_path"
        )

        self.programdata_checkbox = QCheckBox(
            r"C:\ProgramData\Sunsoft"
        )

        self.printers_checkbox = QCheckBox(
            "Windows Printers"
        )

        self.registry_checkbox = QCheckBox(
            "Registry"
        )

        self.sql_checkbox = QCheckBox(
            "SQL Databases"
        )

        self._backup_checkboxes = [
            self.configuration_checkbox,
            self.form_path_checkbox,
            self.programdata_checkbox,
            self.printers_checkbox,
            self.registry_checkbox,
            self.sql_checkbox,
        ]

        for checkbox in self._backup_checkboxes:
            components_layout.addWidget(
                checkbox
            )

        select_layout = QHBoxLayout()

        self.select_all_button = QPushButton(
            "SELECT ALL"
        )

        self.clear_all_button = QPushButton(
            "CLEAR ALL"
        )

        self.select_all_button.setObjectName(
            "secondaryButton"
        )

        self.clear_all_button.setObjectName(
            "secondaryButton"
        )

        select_layout.addWidget(
            self.select_all_button
        )

        select_layout.addWidget(
            self.clear_all_button
        )

        select_layout.addStretch()

        components_layout.addLayout(
            select_layout
        )

        root.addWidget(
            components_card
        )

        # ------------------------------------------------------------
        # Destination
        # ------------------------------------------------------------

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
            8
        )

        destination_title = QLabel(
            "Backup Destination"
        )

        destination_title.setObjectName(
            "sectionTitle"
        )

        self.destination_label = QLabel()

        self.destination_label.setWordWrap(
            True
        )

        self.browse_button = QPushButton(
            "BROWSE"
        )

        self.browse_button.setObjectName(
            "secondaryButton"
        )
        self.browse_button.setStyleSheet(
            """
            QPushButton {
                background: #2F6FED;
                color: #FFFFFF;
                border: 1px solid #2F6FED;
            }

            QPushButton:hover {
                background: #245DCA;
            }

            QPushButton:disabled {
                background: #F1F4F8;
                color: #A8B2C0;
                border-color: #E1E6ED;
            }
            """
        )

        destination_layout.addWidget(
            destination_title
        )

        destination_layout.addWidget(
            self.destination_label
        )

        destination_layout.addWidget(
            self.browse_button,
            0,
        )

        root.addWidget(
            destination_card
        )

        # ------------------------------------------------------------
        # Schedule
        # ------------------------------------------------------------

        schedule_card = QFrame()
        schedule_card.setObjectName(
            "contentCard"
        )

        schedule_layout = QVBoxLayout(
            schedule_card
        )

        schedule_layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )

        schedule_layout.setSpacing(
            9
        )

        schedule_title = QLabel(
            "Scheduled Backup"
        )

        schedule_title.setObjectName(
            "sectionTitle"
        )

        schedule_layout.addWidget(
            schedule_title
        )

        self.schedule_enabled_checkbox = QCheckBox(
            "Enable automatic backup"
        )

        schedule_layout.addWidget(
            self.schedule_enabled_checkbox
        )

        schedule_row = QHBoxLayout()

        schedule_row.addWidget(
            QLabel("Run every:")
        )

        self.schedule_interval_spin = QSpinBox()

        self.schedule_interval_spin.setRange(
            1,
            168,
        )

        self.schedule_interval_spin.setSuffix(
            " hours"
        )

        schedule_row.addWidget(
            self.schedule_interval_spin
        )

        schedule_row.addSpacing(
            16
        )

        schedule_row.addWidget(
            QLabel("Start time:")
        )

        self.schedule_time_edit = QTimeEdit()

        self.schedule_time_edit.setDisplayFormat(
            "HH:mm"
        )

        schedule_row.addWidget(
            self.schedule_time_edit
        )

        schedule_row.addStretch()

        schedule_layout.addLayout(
            schedule_row
        )

        self.schedule_status_label = QLabel(
            "Scheduled backup is disabled."
        )

        self.schedule_status_label.setObjectName(
            "summaryText"
        )

        self.schedule_status_label.setWordWrap(
            True
        )

        schedule_layout.addWidget(
            self.schedule_status_label
        )

        self.save_schedule_button = QPushButton(
            "SAVE SCHEDULE"
        )

        self.save_schedule_button.setObjectName(
            "secondaryButton"
        )
        self.save_schedule_button.setStyleSheet(
            """
            QPushButton {
                background: #2F6FED;
                color: #FFFFFF;
                border: 1px solid #2F6FED;
            }

            QPushButton:hover {
                background: #245DCA;
            }

            QPushButton:disabled {
                background: #F1F4F8;
                color: #A8B2C0;
                border-color: #E1E6ED;
            }
            """
        )

        schedule_layout.addWidget(
            self.save_schedule_button,
            0,
        )

        root.addWidget(
            schedule_card
        )

        # ------------------------------------------------------------
        # Action
        # ------------------------------------------------------------

        action_frame = QFrame()

        action_frame.setObjectName(
            "summaryFrame"
        )

        action_layout = QHBoxLayout(
            action_frame
        )

        action_layout.setContentsMargins(
            18,
            14,
            18,
            14,
        )

        self.status_label = QLabel(
            "Ready"
        )

        self.progress_label = QLabel(
            ""
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

        action_layout.addWidget(
            self.progress_label
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

    # ================================================================
    # Signals
    # ================================================================

    def _connect_signals(self) -> None:

        self.backup_button.clicked.connect(
            self._start_backup
        )

        self.browse_button.clicked.connect(
            self._select_destination
        )

        self.select_all_button.clicked.connect(
            self._select_all
        )

        self.clear_all_button.clicked.connect(
            self._clear_all
        )

        self.save_schedule_button.clicked.connect(
            self._save_schedule
        )

        database_context.database_changed.connect(
            self._on_database_changed
        )

    # ================================================================
    # Settings
    # ================================================================

    def _load_settings(self) -> None:

        self.destination_label.setText(
            self.settings.get(
                "backup_destination",
                str(
                    Path.home()
                    / "AIO-Toolbox-Backups"
                ),
            )
        )

        targets = (
            self.settings.get(
                "selected_targets"
            )
            or {}
        )

        for key, checkbox in (
            self._target_checkbox_map().items()
        ):
            checkbox.setChecked(
                bool(
                    targets.get(
                        key,
                        True,
                    )
                )
            )

        self.schedule_enabled_checkbox.setChecked(
            bool(
                self.settings.get(
                    "schedule_enabled",
                    False,
                )
            )
        )

        self.schedule_interval_spin.setValue(
            int(
                self.settings.get(
                    "schedule_interval_hours",
                    24,
                )
            )
        )

        time_text = str(
            self.settings.get(
                "schedule_start_time",
                "02:00",
            )
        )

        parsed = QTime.fromString(
            time_text,
            "HH:mm",
        )

        self.schedule_time_edit.setTime(
            parsed
            if parsed.isValid()
            else QTime(2, 0)
        )

        self._refresh_schedule_status()

    def _target_checkbox_map(
        self,
    ) -> dict[str, QCheckBox]:

        return {
            "configuration":
                self.configuration_checkbox,

            "form_path":
                self.form_path_checkbox,

            "programdata":
                self.programdata_checkbox,

            "printers":
                self.printers_checkbox,

            "registry":
                self.registry_checkbox,

            "sql":
                self.sql_checkbox,
        }

    # ================================================================
    # Database
    # ================================================================

    def _on_database_changed(
        self,
        database: object,
    ) -> None:

        self._update_database_info()

    def _update_database_info(self) -> None:

        database = (
            database_context.active()
        )

        if not database:

            self.database_label.setText(
                "No database selected"
            )

            self.server_label.setText(
                "Server: β€”"
            )

            self.udl_label.setText(
                "UDL: β€”"
            )

            self.backup_button.setEnabled(
                False
            )

            return

        self.database_label.setText(
            "Database: "
            + str(
                database.get(
                    "name"
                )
                or "Unknown database"
            )
        )

        self.server_label.setText(
            "Server: "
            + str(
                database.get(
                    "server"
                )
                or "Unknown server"
            )
        )

        self.udl_label.setText(
            "UDL: "
            + str(
                database.get(
                    "path"
                )
                or "β€”"
            )
        )

        self.backup_button.setEnabled(
            True
        )

    # ================================================================
    # Components
    # ================================================================

    def _select_all(self) -> None:

        for checkbox in self._backup_checkboxes:
            checkbox.setChecked(
                True
            )

    def _clear_all(self) -> None:

        for checkbox in self._backup_checkboxes:
            checkbox.setChecked(
                False
            )

    def _get_selected_targets(
        self,
    ) -> dict[str, bool]:

        return {
            key:
                checkbox.isChecked()
            for key, checkbox
            in self._target_checkbox_map().items()
        }

    # ================================================================
    # Destination
    # ================================================================

    def _select_destination(self) -> None:

        current = (
            self.destination_label.text()
            .strip()
        )

        selected = (
            QFileDialog.getExistingDirectory(
                self,
                "Select Backup Destination",
                current
                if Path(current).exists()
                else str(Path.home()),
            )
        )

        if selected:
            self.destination_label.setText(
                selected
            )

    # ================================================================
    # Schedule
    # ================================================================

    def _save_schedule(self) -> None:

        selected_targets = (
            self._get_selected_targets()
        )

        if not any(
            selected_targets.values()
        ):
            QMessageBox.warning(
                self,
                "Backup Components",
                "Please select at least one backup component.",
            )
            return

        destination = Path(
            self.destination_label.text().strip()
        ).expanduser()

        if not str(
            destination
        ).strip():

            QMessageBox.warning(
                self,
                "Backup Destination",
                "Please select a backup destination.",
            )
            return

        try:
            destination.mkdir(
                parents=True,
                exist_ok=True,
            )

            active = (
                database_context.active()
            )

            selected_udl = (
                str(
                    active.get("path")
                )
                if active
                and active.get("path")
                else ""
            )

            if (
                selected_targets.get("sql")
                and not selected_udl
            ):
                QMessageBox.warning(
                    self,
                    "Database Required",
                    "SQL Databases is selected, but no database/UDL is selected.",
                )
                return

            time_text = (
                self.schedule_time_edit
                .time()
                .toString("HH:mm")
            )

            new_settings = {
                "backup_destination":
                    str(
                        destination.resolve()
                    ),

                "schedule_enabled":
                    self.schedule_enabled_checkbox.isChecked(),

                "schedule_interval_hours":
                    self.schedule_interval_spin.value(),

                "schedule_start_time":
                    time_text,

                "selected_udl":
                    selected_udl,

                "selected_targets":
                    selected_targets,
            }

            old_settings = dict(
                self.settings
            )

            saved = (
                self.settings_manager.save(
                    new_settings
                )
            )

            try:
                self.scheduler_manager.apply(
                    saved
                )

            except Exception:
                self.settings_manager.save(
                    old_settings
                )
                raise

            self.settings = saved

            self._refresh_schedule_status()

            QMessageBox.information(
                self,
                "Schedule Saved",
                (
                    "Scheduled backup settings were saved successfully."
                    if saved.get(
                        "schedule_enabled"
                    )
                    else
                    "Scheduled backup was disabled successfully."
                ),
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Schedule Error",
                (
                    "Unable to save the scheduled backup."
                    "\n\n"
                    f"{exc}"
                ),
            )

    def _refresh_schedule_status(
        self,
    ) -> None:

        if not self.settings.get(
            "schedule_enabled",
            False,
        ):

            self.schedule_status_label.setText(
                "Scheduled backup is disabled."
            )

            return

        interval = int(
            self.settings.get(
                "schedule_interval_hours",
                24,
            )
        )

        start_time = self.settings.get(
            "schedule_start_time",
            "02:00",
        )

        self.schedule_status_label.setText(
            "Scheduled backup is active"
            f" β€Ά Every {interval} hours"
            f" β€Ά Start: {start_time}"
        )

    # ================================================================
    # Manual Backup
    # ================================================================

    def _start_backup(self) -> None:

        database = (
            database_context.active()
        )

        if not database:

            QMessageBox.warning(
                self,
                "Database Required",
                "Please connect to a database first.",
            )

            return

        selected_targets = (
            self._get_selected_targets()
        )

        if not any(
            selected_targets.values()
        ):

            QMessageBox.warning(
                self,
                "Backup Components",
                "Please select at least one backup component.",
            )

            return

        destination = (
            self.destination_label
            .text()
            .strip()
        )

        if not destination:

            QMessageBox.warning(
                self,
                "Backup Destination",
                "Please select a backup destination.",
            )

            return

        if self.worker is not None:
            return

        self.backup_button.setEnabled(
            False
        )

        self.browse_button.setEnabled(
            False
        )

        self.select_all_button.setEnabled(
            False
        )

        self.clear_all_button.setEnabled(
            False
        )

        self.save_schedule_button.setEnabled(
            False
        )

        self.backup_button.setText(
            "BACKING UP..."
        )

        self.status_label.setText(
            "Preparing backup..."
        )

        self.progress_label.setText(
            "5%"
        )

        self.worker = BackupWorker(
            destination=destination,
            selected_targets=selected_targets,
        )

        self.worker.progress.connect(
            self._on_backup_progress
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

    # ================================================================
    # Progress / Result
    # ================================================================

    def _on_backup_progress(
        self,
        percentage: int,
        message: str,
    ) -> None:

        self.progress_label.setText(
            f"{percentage}%"
        )

        self.status_label.setText(
            message
        )

    def _on_backup_finished(
        self,
        result: object,
    ) -> None:

        if (
            not isinstance(
                result,
                dict,
            )
            or not result.get(
                "success"
            )
        ):

            errors = (
                result.get(
                    "errors",
                    [],
                )
                if isinstance(
                    result,
                    dict,
                )
                else [
                    "Invalid backup result."
                ]
            )

            self._on_backup_failed(
                "\n".join(
                    str(error)
                    for error in errors
                )
            )

            return

        data = (
            result.get("data")
            or {}
        )

        archive = data.get(
            "archive_path"
        )

        self.status_label.setText(
            "Backup completed successfully."
        )

        self.progress_label.setText(
            "100%"
        )

        self.backup_button.setText(
            "BACKUP NOW"
        )

        self._set_controls_enabled(
            True
        )

        message = (
            "The backup completed successfully."
        )

        if archive:
            message += (
                "\n\nArchive:"
                f"\n{archive}"
            )

        QMessageBox.information(
            self,
            "Backup Completed",
            message,
        )

    def _on_backup_failed(
        self,
        message: str,
    ) -> None:

        self.status_label.setText(
            "Backup failed."
        )

        self.progress_label.setText(
            ""
        )

        self.backup_button.setText(
            "BACKUP NOW"
        )

        self._set_controls_enabled(
            True
        )

        QMessageBox.critical(
            self,
            "Backup Failed",
            (
                "The backup could not be completed."
                "\n\n"
                f"{message}"
            ),
        )

    def _set_controls_enabled(
        self,
        enabled: bool,
    ) -> None:

        self.backup_button.setEnabled(
            enabled
            and bool(
                database_context.active()
            )
        )

        self.browse_button.setEnabled(
            enabled
        )

        self.select_all_button.setEnabled(
            enabled
        )

        self.clear_all_button.setEnabled(
            enabled
        )

        self.save_schedule_button.setEnabled(
            enabled
        )

    def _cleanup_worker(self) -> None:

        if self.worker is None:
            return

        self.worker.deleteLater()
        self.worker = None
