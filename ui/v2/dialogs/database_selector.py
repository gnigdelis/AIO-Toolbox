from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from core.database.database_connection import (
    DatabaseConnection,
)
from core.database.udl_locator import UDLLocator


class DatabaseSelector(QDialog):
    """
    Dialog for selecting and testing a SQL Server UDL connection.
    """

    SETTINGS_ORGANIZATION = "Sunsoft"
    SETTINGS_APPLICATION = "AIO Toolbox"

    LAST_UDL_KEY = "database/last_udl"
    LAST_FOLDER_KEY = "database/last_folder"

    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.selected_udl: str | None = None
        self.database_name: str = ""
        self.server_name: str = ""

        self.setWindowTitle(
            "Database Connection"
        )

        self.setMinimumSize(
            760,
            500,
        )

        self._settings = QSettings(
            self.SETTINGS_ORGANIZATION,
            self.SETTINGS_APPLICATION,
        )

        self._build_ui()
        self._load_udls()

    # ============================================================
    # UI
    # ============================================================

    def _build_ui(self) -> None:
        self.setObjectName(
            "databaseSelector"
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )

        layout.setSpacing(14)

        title = QLabel(
            "Database Connection"
        )
        title.setObjectName(
            "dialogTitle"
        )

        subtitle = QLabel(
            "Select the UDL file used by this installation "
            "to connect to the SQL Server database."
        )

        subtitle.setObjectName(
            "dialogSubtitle"
        )

        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        content = QHBoxLayout()
        content.setSpacing(16)

        # --------------------------------------------------------
        # Available UDL
        # --------------------------------------------------------

        left_card = QFrame()
        left_card.setObjectName(
            "dialogCard"
        )

        left_layout = QVBoxLayout(
            left_card
        )

        left_layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        left_layout.setSpacing(10)

        left_title = QLabel(
            "Available UDL files"
        )
        left_title.setObjectName(
            "cardTitle"
        )

        self.udl_list = QListWidget()
        self.udl_list.setObjectName(
            "udlList"
        )

        self.udl_list.itemSelectionChanged.connect(
            self._selection_changed
        )

        self.udl_list.itemDoubleClicked.connect(
            self._connect_selected
        )

        left_layout.addWidget(
            left_title
        )

        left_layout.addWidget(
            self.udl_list,
            1,
        )

        browse_button = QPushButton(
            "Browse for UDL..."
        )

        browse_button.setObjectName(
            "secondaryButton"
        )

        browse_button.clicked.connect(
            self._browse_udl
        )

        left_layout.addWidget(
            browse_button
        )

        content.addWidget(
            left_card,
            1,
        )

        # --------------------------------------------------------
        # Connection details
        # --------------------------------------------------------

        right_card = QFrame()
        right_card.setObjectName(
            "dialogCard"
        )

        right_layout = QVBoxLayout(
            right_card
        )

        right_layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        right_layout.setSpacing(10)

        details_title = QLabel(
            "Connection Details"
        )
        details_title.setObjectName(
            "cardTitle"
        )

        right_layout.addWidget(
            details_title
        )

        self.udl_value = self._create_detail_label(
            "UDL file:"
        )

        self.server_value = self._create_detail_label(
            "Server:"
        )

        self.database_value = self._create_detail_label(
            "Database:"
        )

        self.status_value = self._create_detail_label(
            "Status:"
        )

        right_layout.addWidget(
            self.udl_value
        )

        right_layout.addWidget(
            self.server_value
        )

        right_layout.addWidget(
            self.database_value
        )

        right_layout.addWidget(
            self.status_value
        )

        right_layout.addSpacing(8)

        self.test_button = QPushButton(
            "Test Connection"
        )

        self.test_button.setObjectName(
            "primaryButton"
        )

        self.test_button.setEnabled(False)

        self.test_button.clicked.connect(
            self._test_connection
        )

        right_layout.addWidget(
            self.test_button
        )

        right_layout.addStretch()

        content.addWidget(
            right_card,
            1,
        )

        layout.addLayout(
            content,
            1,
        )

        # --------------------------------------------------------
        # Bottom buttons
        # --------------------------------------------------------

        bottom = QHBoxLayout()

        bottom.addStretch()

        cancel_button = QPushButton(
            "Cancel"
        )

        cancel_button.setObjectName(
            "secondaryButton"
        )

        cancel_button.clicked.connect(
            self.reject
        )

        self.connect_button = QPushButton(
            "Connect"
        )

        self.connect_button.setObjectName(
            "primaryButton"
        )

        self.connect_button.setEnabled(False)

        self.connect_button.clicked.connect(
            self._connect_selected
        )

        bottom.addWidget(
            cancel_button
        )

        bottom.addWidget(
            self.connect_button
        )

        layout.addLayout(
            bottom
        )

        self.setStyleSheet(
            """
            QDialog {
                background: #F5F7FB;
            }

            QLabel#dialogTitle {
                color: #17233B;
                font-size: 20px;
                font-weight: 700;
            }

            QLabel#dialogSubtitle {
                color: #66758B;
                font-size: 13px;
            }

            QFrame#dialogCard {
                background: #FFFFFF;
                border: 1px solid #DDE4EF;
                border-radius: 10px;
            }

            QLabel#cardTitle {
                color: #26344D;
                font-size: 14px;
                font-weight: 600;
            }

            QListWidget#udlList {
                background: #FBFCFE;
                border: 1px solid #DDE4EF;
                border-radius: 7px;
                padding: 4px;
                color: #26344D;
            }

            QListWidget#udlList::item {
                padding: 10px;
                border-radius: 5px;
            }

            QListWidget#udlList::item:selected {
                background: #2F80ED;
                color: white;
            }

            QLabel#detailLabel {
                color: #26344D;
                font-size: 12px;
                padding: 6px;
                background: #F7F9FC;
                border-radius: 5px;
            }

            QPushButton#primaryButton {
                min-height: 38px;
                padding: 0 18px;
                background: #2F80ED;
                color: white;
                border: none;
                border-radius: 7px;
                font-weight: 600;
            }

            QPushButton#primaryButton:hover {
                background: #2474DB;
            }

            QPushButton#primaryButton:disabled {
                background: #B8C4D5;
            }

            QPushButton#secondaryButton {
                min-height: 38px;
                padding: 0 18px;
                background: #FFFFFF;
                color: #26344D;
                border: 1px solid #D5DDE9;
                border-radius: 7px;
            }

            QPushButton#secondaryButton:hover {
                background: #F3F6FA;
            }
            """
        )

    def _set_status(
        self,
        text: str,
        state: str = "default",
    ) -> None:
        self.status_value.setText(text)

        state_styles = {
            "success": (
                "color: #16803A;"
                " background: #ECF9F0;"
                " border: 1px solid #A9DFB9;"
                " font-weight: 700;"
            ),
            "error": (
                "color: #C62828;"
                " background: #FFF1F1;"
                " border: 1px solid #F0B8B8;"
                " font-weight: 700;"
            ),
            "testing": (
                "color: #1D66B3;"
                " background: #EEF6FF;"
                " border: 1px solid #B9D8F8;"
                " font-weight: 600;"
            ),
            "default": (
                "color: #26344D;"
                " background: #F7F9FC;"
                " border: 1px solid transparent;"
            ),
        }

        self.status_value.setStyleSheet(
            "QLabel#detailLabel { "
            + state_styles.get(state, state_styles["default"])
            + " padding: 6px;"
            " border-radius: 5px;"
            "}"
        )

    def _create_detail_label(
        self,
        title: str,
    ) -> QLabel:
        label = QLabel(
            f"{title} -"
        )

        label.setObjectName(
            "detailLabel"
        )

        label.setWordWrap(True)

        return label

    # ============================================================
    # UDL LIST
    # ============================================================

    def _load_udls(self) -> None:
        self.udl_list.clear()

        udls = UDLLocator.find_all()

        last_udl = str(
            self._settings.value(
                self.LAST_UDL_KEY,
                "",
            )
            or ""
        )

        last_udl_path = (
            Path(last_udl).resolve()
            if last_udl
            else None
        )

        selected_row = -1

        for index, udl in enumerate(udls):
            item = QListWidgetItem(
                udl.name
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                str(udl),
            )

            item.setToolTip(
                str(udl)
            )

            self.udl_list.addItem(
                item
            )

            try:
                if (
                    last_udl_path
                    and udl.resolve()
                    == last_udl_path
                ):
                    selected_row = index
            except (
                OSError,
                RuntimeError,
            ):
                pass

        if selected_row >= 0:
            self.udl_list.setCurrentRow(
                selected_row
            )

        elif self.udl_list.count() == 1:
            self.udl_list.setCurrentRow(0)

        else:
            initial_udl = (
                UDLLocator.find_initial()
            )

            if initial_udl:
                for index in range(
                    self.udl_list.count()
                ):
                    item = (
                        self.udl_list.item(
                            index
                        )
                    )

                    path = item.data(
                        Qt.ItemDataRole.UserRole
                    )

                    if (
                        str(path).lower()
                        == str(initial_udl).lower()
                    ):
                        self.udl_list.setCurrentRow(
                            index
                        )
                        break

        if self.udl_list.count() == 0:
            self._set_status(
                "Status: No UDL files found",
                "error",
            )

    # ============================================================
    # SELECTION
    # ============================================================

    def _selection_changed(self) -> None:
        item = self.udl_list.currentItem()

        if item is None:
            self._clear_details()
            return

        udl_path = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not udl_path:
            self._clear_details()
            return

        self._show_udl_details(
            str(udl_path)
        )

    def _show_udl_details(
        self,
        udl_path: str,
    ) -> None:
        self.test_button.setEnabled(True)
        self.connect_button.setEnabled(True)

        self.udl_value.setText(
            f"UDL file: {udl_path}"
        )

        try:
            connection = DatabaseConnection(
                udl_path
            )

            self.server_value.setText(
                "Server: "
                + (
                    connection.server_name()
                    or "-"
                )
            )

            self.database_value.setText(
                "Database: "
                + (
                    connection.database_name()
                    or "-"
                )
            )

            self._set_status(
                "Status: Not tested",
                "default",
            )

        except Exception as exc:
            self.server_value.setText(
                "Server: -"
            )

            self.database_value.setText(
                "Database: -"
            )

            self._set_status(
                f"Status: Invalid UDL - {exc}",
                "error",
            )

    def _clear_details(self) -> None:
        self.udl_value.setText(
            "UDL file: -"
        )

        self.server_value.setText(
            "Server: -"
        )

        self.database_value.setText(
            "Database: -"
        )

        self._set_status(
            "Status: Not selected",
            "default",
        )

        self.test_button.setEnabled(False)
        self.connect_button.setEnabled(False)

    # ============================================================
    # BROWSE
    # ============================================================

    def _browse_udl(self) -> None:
        last_folder = str(
            self._settings.value(
                self.LAST_FOLDER_KEY,
                "",
            )
            or ""
        )

        if not last_folder:
            last_folder = str(
                Path.home()
            )

        if not Path(last_folder).exists():
            last_folder = str(
                Path.home()
            )

        file_path, _ = (
            QFileDialog.getOpenFileName(
                self,
                "Select UDL File",
                last_folder,
                "UDL files (*.udl);;All files (*.*)",
            )
        )

        if not file_path:
            return

        selected_path = Path(
            file_path
        ).resolve()

        self._save_last_folder(
            selected_path.parent
        )

        self._add_or_select_udl(
            selected_path
        )

    def _add_or_select_udl(
        self,
        udl_path: Path,
    ) -> None:
        target = str(
            udl_path.resolve()
        ).lower()

        for index in range(
            self.udl_list.count()
        ):
            item = self.udl_list.item(
                index
            )

            path = item.data(
                Qt.ItemDataRole.UserRole
            )

            if (
                str(path).lower()
                == target
            ):
                self.udl_list.setCurrentRow(
                    index
                )
                return

        item = QListWidgetItem(
            udl_path.name
        )

        item.setData(
            Qt.ItemDataRole.UserRole,
            str(udl_path),
        )

        item.setToolTip(
            str(udl_path)
        )

        self.udl_list.addItem(
            item
        )

        self.udl_list.setCurrentItem(
            item
        )

    # ============================================================
    # TEST CONNECTION
    # ============================================================

    def _test_connection(self) -> None:
        udl_path = self._selected_udl()

        if not udl_path:
            return

        self._set_status(
            "Status: Testing connection...",
            "testing",
        )

        try:
            connection = DatabaseConnection(
                udl_path
            )

            sql_connection = (
                connection.connect()
            )

            try:
                sql_connection.close()
            except Exception:
                pass

            self.server_name = (
                connection.server_name()
            )

            self.database_name = (
                connection.database_name()
            )

            self._set_status(
                "Status: Connection successful",
                "success",
            )

        except Exception as exc:
            self._set_status(
                "Status: Connection failed",
                "error",
            )

            QMessageBox.critical(
                self,
                "Connection Failed",
                "The database connection could not "
                "be established.\n\n"
                f"UDL:\n{udl_path}\n\n"
                f"Error:\n{exc}",
            )

    # ============================================================
    # CONNECT
    # ============================================================

    def _connect_selected(
        self,
        checked: bool = False,
    ) -> None:
        del checked

        udl_path = self._selected_udl()

        if not udl_path:
            return

        self._set_status(
            "Status: Connecting...",
            "testing",
        )

        try:
            connection = DatabaseConnection(
                udl_path
            )

            sql_connection = (
                connection.connect()
            )

            try:
                sql_connection.close()
            except Exception:
                pass

            self.selected_udl = (
                udl_path
            )

            self.database_name = (
                connection.database_name()
            )

            self.server_name = (
                connection.server_name()
            )

            self._save_last_selection(
                udl_path
            )

            self._set_status(
                "Status: Connected",
                "success",
            )

            self.accept()

        except Exception as exc:
            self._set_status(
                "Status: Connection failed",
                "error",
            )

            QMessageBox.critical(
                self,
                "Connection Failed",
                "The database connection could not "
                "be established.\n\n"
                f"UDL:\n{udl_path}\n\n"
                f"Error:\n{exc}",
            )

    # ============================================================
    # SETTINGS
    # ============================================================

    def _save_last_folder(
        self,
        folder: Path,
    ) -> None:
        self._settings.setValue(
            self.LAST_FOLDER_KEY,
            str(folder.resolve()),
        )

        self._settings.sync()

    def _save_last_selection(
        self,
        udl_path: str,
    ) -> None:
        path = Path(
            udl_path
        ).resolve()

        self._settings.setValue(
            self.LAST_UDL_KEY,
            str(path),
        )

        self._settings.setValue(
            self.LAST_FOLDER_KEY,
            str(path.parent),
        )

        self._settings.sync()

    def _selected_udl(self) -> str | None:
        item = self.udl_list.currentItem()

        if item is None:
            return None

        path = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not path:
            return None

        return str(path)