from __future__ import annotations

from PySide6.QtCore import QDate, QObject, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.database.database_context import database_context
from core.sql_tools.sql_tools_service import SQLToolsService, SQLToolResult

from ui.v2.widgets.page_layout import (
    PAGE_LAYOUT_STYLE,
    setup_page_layout,
)


class SQLToolWorker(QObject):
    finished = Signal(object, str)
    failed = Signal(str, str)

    def __init__(
        self,
        operation: str,
        operation_name: str,
        operation_arg: object | None = None,
    ) -> None:
        super().__init__()
        self.operation = operation
        self.operation_name = operation_name
        self.operation_arg = operation_arg

    def run(self) -> None:
        try:
            service = SQLToolsService()

            if self.operation == "delete_mydata":
                result = service.delete_mydata_response()

            elif self.operation == "delete_failed_mydata_payments":
                result = service.delete_failed_mydata_payments()

            elif self.operation == "delete_mydata_before":
                result = service.delete_mydata_responses_before(
                    str(self.operation_arg)
                )

            elif self.operation == "rebuild":
                result = service.rebuild_database()

            elif self.operation == "shrink":
                result = service.shrink_database()

            else:
                raise RuntimeError(
                    f"Unknown SQL Tools operation: {self.operation}"
                )

            self.finished.emit(result, self.operation_name)

        except Exception as ex:
            self.failed.emit(str(ex), self.operation_name)


class SQLToolsPage(QFrame):
    """
    SQL maintenance tools for the currently selected database.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.service = SQLToolsService()

        self._thread: QThread | None = None
        self._worker: SQLToolWorker | None = None
        self._failed_mydata_payments_supported = False

        database_context.database_changed.connect(
            self._on_database_changed
        )

        self.setObjectName("sqlToolsPage")

        self._build_ui()


    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root, title, subtitle = setup_page_layout(
            self,
            "SQL Tools",
            "Εργαλεία συντήρησης SQL για την ενεργή βάση δεδομένων.",
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 6, 0)
        content_layout.setSpacing(16)

        # --------------------------------------------------------------
        # Operation Log
        # --------------------------------------------------------------

        log_card = self._create_card()

        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(14, 18, 14, 14)
        log_layout.setSpacing(10)

        log_header = QHBoxLayout()
        log_header.setSpacing(8)

        log_title = QLabel("Operation Log")
        log_title.setObjectName("sectionTitle")

        log_status = QLabel("Ready")
        log_status.setObjectName("logStatus")

        log_header.addWidget(log_title)
        log_header.addWidget(log_status)
        log_header.addStretch()

        clear_log_button = QPushButton("Clear Log")
        clear_log_button.setObjectName("secondaryButton")
        clear_log_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        clear_log_button.setMinimumHeight(34)
        clear_log_button.clicked.connect(self._clear_log)

        log_header.addWidget(clear_log_button)
        log_layout.addLayout(log_header)

        self.log_label = QLabel(
            "Έτοιμο. Επίλεξε ένα SQL Tool."
        )
        self.log_label.setObjectName("operationLog")
        self.log_label.setWordWrap(True)
        self.log_label.setMinimumHeight(58)
        self.log_label.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        log_layout.addWidget(self.log_label)
        content_layout.addWidget(log_card)

        # --------------------------------------------------------------
        # Database Maintenance
        # --------------------------------------------------------------

        tools_title = QLabel("Database Maintenance")
        tools_title.setObjectName("sectionHeading")
        content_layout.addWidget(tools_title)

        self.delete_card = self._create_tool_card(
            title="Delete MyDATA Responses",
            description=(
                "Διαγράφει όλες τις εγγραφές από το "
                "TblSnMyDATA_Response που δεν έχουν status "
                "'Success'."
            ),
            button_text="DELETE RESPONSES",
            button_kind="danger",
        )

        self.delete_button = self.delete_card.findChild(
            QPushButton,
            "toolButton",
        )

        if self.delete_button:
            self.delete_button.clicked.connect(
                self._delete_mydata_responses
            )

        content_layout.addWidget(self.delete_card)

        self.failed_mydata_card = self._create_tool_card(
            title="Delete Failed MyDATA Payments",
            description=(
                "Διαγράφει αποτυχημένες εγγραφές MyDATA Payments "
                "σύμφωνα με τους κανόνες της συγκεκριμένης έκδοσης της βάσης."
            ),
            button_text="DELETE FAILED PAYMENTS",
            button_kind="danger",
        )

        self.failed_mydata_button = self.failed_mydata_card.findChild(
            QPushButton,
            "toolButton",
        )

        if self.failed_mydata_button:
            self.failed_mydata_button.clicked.connect(
                self._delete_failed_mydata_payments
            )

        content_layout.addWidget(self.failed_mydata_card)

        self.delete_before_date_card = self._create_card()

        delete_before_layout = QVBoxLayout(
            self.delete_before_date_card
        )
        delete_before_layout.setContentsMargins(
            14, 18, 14, 14
        )
        delete_before_layout.setSpacing(10)

        delete_before_top_layout = QHBoxLayout()
        delete_before_top_layout.setSpacing(12)

        delete_before_text_layout = QVBoxLayout()
        delete_before_text_layout.setSpacing(5)

        delete_before_title = QLabel(
            "Delete MyDATA Responses Before Date"
        )
        delete_before_title.setObjectName("toolTitle")

        delete_before_description = QLabel(
            "Delete all MyDATA response records from the "
            "selected date and before, including the selected date."
        )
        delete_before_description.setObjectName(
            "toolDescription"
        )
        delete_before_description.setWordWrap(True)

        delete_before_text_layout.addWidget(
            delete_before_title
        )
        delete_before_text_layout.addWidget(
            delete_before_description
        )

        delete_before_top_layout.addLayout(
            delete_before_text_layout,
            1,
        )

        delete_before_controls = QHBoxLayout()
        delete_before_controls.setSpacing(8)

        self.delete_before_date_edit = QDateEdit()
        self.delete_before_date_edit.setObjectName(
            "toolDateEdit"
        )
        self.delete_before_date_edit.setDisplayFormat(
            "dd/MM/yyyy"
        )
        self.delete_before_date_edit.setCalendarPopup(True)
        self.delete_before_date_edit.setDate(
            QDate.currentDate()
        )
        self.delete_before_date_edit.setMinimumWidth(125)
        self.delete_before_date_edit.setMinimumHeight(36)

        self.delete_before_date_button = QPushButton(
            "DELETE RESPONSES"
        )
        self.delete_before_date_button.setObjectName(
            "toolButton"
        )
        self.delete_before_date_button.setProperty(
            "buttonKind",
            "danger",
        )
        self.delete_before_date_button.setMinimumWidth(165)
        self.delete_before_date_button.setMinimumHeight(36)
        self.delete_before_date_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.delete_before_date_button.clicked.connect(
            self._delete_mydata_responses_before_date
        )

        delete_before_controls.addWidget(
            self.delete_before_date_edit
        )
        delete_before_controls.addWidget(
            self.delete_before_date_button
        )

        delete_before_top_layout.addLayout(
            delete_before_controls
        )

        delete_before_layout.addLayout(
            delete_before_top_layout
        )

        content_layout.addWidget(
            self.delete_before_date_card
        )

        self.rebuild_card = self._create_tool_card(
            title="Rebuild Database",
            description=(
                "Εκτελεί την πραγματική διαδικασία "
                "SPSnRebuildUpdate για rebuild και ενημέρωση "
                "των database indexes/statistics."
            ),
            button_text="REBUILD DATABASE",
            button_kind="primary",
        )

        self.rebuild_button = self.rebuild_card.findChild(
            QPushButton,
            "toolButton",
        )

        if self.rebuild_button:
            self.rebuild_button.clicked.connect(
                self._rebuild_database
            )

        content_layout.addWidget(self.rebuild_card)

        self.shrink_card = self._create_tool_card(
            title="Shrink Database",
            description=(
                "Εκτελεί τη διαδικασία Shrink της SQL Server "
                "για την ενεργή βάση δεδομένων."
            ),
            button_text="SHRINK DATABASE",
            button_kind="warning",
        )

        self.shrink_button = self.shrink_card.findChild(
            QPushButton,
            "toolButton",
        )

        if self.shrink_button:
            self.shrink_button.clicked.connect(
                self._shrink_database
            )

        content_layout.addWidget(self.shrink_card)

        content_layout.addStretch()

        self._refresh_database_capabilities()

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        self.setStyleSheet(
            PAGE_LAYOUT_STYLE
            + """
            QLabel#sectionHeading {
                color: #526176;
                font-size: 12px;
                font-weight: 600;
                margin-top: 2px;
            }

            QLabel#sectionTitle {
                color: #526176;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#logStatus {
                color: #718096;
                font-size: 10px;
            }

            QLabel#operationLog {
                background: #111827;
                border: 1px solid #DCE3EC;
                border-radius: 7px;
                color: #E5E7EB;
                font-family: Consolas;
                font-size: 10px;
                padding: 10px;
            }

            QLabel#toolTitle {
                color: #334155;
                font-size: 12px;
                font-weight: 700;
            }

            QLabel#toolDescription {
                color: #66758A;
                font-size: 10px;
            }

            QPushButton#toolButton {
                min-height: 36px;
                min-width: 165px;
                padding: 0 14px;
                border-radius: 6px;
                color: #FFFFFF;
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton#toolButton[buttonKind="primary"] {
                background: #2F6FED;
                border: 1px solid #2F6FED;
            }

            QPushButton#toolButton[buttonKind="primary"]:hover {
                background: #245DCA;
            }

            QPushButton#toolButton[buttonKind="danger"] {
                background: #B42318;
                border: 1px solid #B42318;
            }

            QPushButton#toolButton[buttonKind="danger"]:hover {
                background: #981B12;
            }

            QPushButton#toolButton[buttonKind="warning"] {
                background: #A65B00;
                border: 1px solid #A65B00;
            }

            QPushButton#toolButton[buttonKind="warning"]:hover {
                background: #8C4D00;
            }

            QPushButton#toolButton:disabled {
                color: #A8B2C0;
                background: #F1F4F8;
                border-color: #E1E6ED;
            }
            """
        )

    # ------------------------------------------------------------------
    # Card helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _create_card() -> QFrame:
        card = QFrame()
        card.setObjectName("contentCard")
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        return card

    def _create_tool_card(
        self,
        title: str,
        description: str,
        button_text: str,
        disabled: bool = False,
        button_kind: str = "primary",
    ) -> QFrame:
        card = self._create_card()

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(10)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setObjectName("toolTitle")

        description_label = QLabel(description)
        description_label.setObjectName("toolDescription")
        description_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(description_label)

        top_layout.addLayout(text_layout, 1)

        button = QPushButton(button_text)
        button.setObjectName("toolButton")
        button.setProperty("buttonKind", button_kind)
        button.setMinimumWidth(165)
        button.setMinimumHeight(36)
        button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        if disabled:
            button.setEnabled(False)

        top_layout.addWidget(
            button,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )

        layout.addLayout(top_layout)

        return card

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------

    def _delete_mydata_responses(self) -> None:
        if not database_context.is_selected():
            QMessageBox.warning(
                self,
                "Database Required",
                "Δεν έχει επιλεγεί βάση δεδομένων.",
            )
            return

        database = database_context.active() or {}

        database_name = database.get("name", "-")

        answer = QMessageBox.warning(
            self,
            "Delete MyDATA Responses",
            (
                "Πρόκειται να διαγραφούν όλες οι εγγραφές από "
                "TblSnMyDATA_Response που έχουν status διαφορετικό "
                "από 'Success'.\n\n"
                f"Database: {database_name}\n\n"
                "Η ενέργεια δεν μπορεί να αναιρεθεί.\n\n"
                "Θέλεις να συνεχίσεις;"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self._start_operation(
            "delete_mydata",
            "Delete MyDATA Responses",
        )

    def _delete_failed_mydata_payments(self) -> None:
        if not database_context.is_selected():
            QMessageBox.warning(
                self,
                "Database Required",
                "Δεν έχει επιλεγεί βάση δεδομένων.",
            )
            return

        if not self._failed_mydata_payments_supported:
            QMessageBox.information(
                self,
                "Delete Failed MyDATA Payments",
                (
                    "Η λειτουργία δεν υποστηρίζεται από αυτή την "
                    "έκδοση της βάσης δεδομένων."
                ),
            )
            return

        database = database_context.active() or {}
        database_name = database.get("name", "-")

        answer = QMessageBox.warning(
            self,
            "Delete Failed MyDATA Payments",
            (
                "Πρόκειται να διαγραφούν οι αποτυχημένες εγγραφές "
                "MyDATA Payments σύμφωνα με τους κανόνες καθαρισμού "
                "της εφαρμογής.\n\n"
                f"Database: {database_name}\n\n"
                "Η ενέργεια δεν μπορεί να αναιρεθεί.\n\n"
                "Θέλεις να συνεχίσεις;"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self._start_operation(
            "delete_failed_mydata_payments",
            "Delete Failed MyDATA Payments",
        )

    def _rebuild_database(self) -> None:
        if not database_context.is_selected():
            QMessageBox.warning(
                self,
                "Database Required",
                "Δεν έχει επιλεγεί βάση δεδομένων.",
            )
            return

        database = database_context.active() or {}

        database_name = database.get("name", "-")

        answer = QMessageBox.warning(
            self,
            "Rebuild Database",
            (
                "Πρόκειται να εκτελεστεί το πραγματικό "
                "SPSnRebuildUpdate.\n\n"
                f"Database: {database_name}\n\n"
                "Η διαδικασία μπορεί να διαρκέσει αρκετό χρόνο.\n\n"
                "Θέλεις να συνεχίσεις;"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self._start_operation(
            "rebuild",
            "Rebuild Database",
        )

    def _shrink_database(self) -> None:
        if not database_context.is_selected():
            QMessageBox.warning(
                self,
                "Database Required",
                "Δεν έχει επιλεγεί βάση δεδομένων.",
            )
            return

        database = database_context.active() or {}
        database_name = database.get("name", "-")

        answer = QMessageBox.warning(
            self,
            "Shrink Database",
            (
                "Πρόκειται να εκτελεστεί Shrink στην ενεργή βάση.\n\n"
                f"Database: {database_name}\n\n"
                "Η διαδικασία μπορεί να διαρκέσει αρκετό χρόνο.\n\n"
                "Θέλεις να συνεχίσεις;"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self._start_operation(
            "shrink",
            "Shrink Database",
        )

    # ------------------------------------------------------------------
    # Worker
    # ------------------------------------------------------------------

    def _delete_mydata_responses_before_date(self) -> None:
        if not database_context.is_selected():
            QMessageBox.warning(
                self,
                "Database Required",
                "No database is selected.",
            )
            return

        selected_date = self.delete_before_date_edit.date()

        display_date = selected_date.toString(
            "dd/MM/yyyy"
        )

        date_value = selected_date.toString(
            "yyyyMMdd"
        )

        database = database_context.active() or {}
        database_name = database.get("name", "-")

        answer = QMessageBox.warning(
            self,
            "Delete MyDATA Responses Before Date",
            (
                "All records from TblSnMyDATA_Response "
                "from the selected date and before will be deleted.\n\n"
                f"Date: {display_date}\n"
                f"Database: {database_name}\n\n"
                "The selected date is included.\n"
                "This action cannot be undone.\n\n"
                "Do you want to continue?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self._start_operation(
            "delete_mydata_before",
            "Delete MyDATA Responses Before Date",
            date_value,
        )

    def _start_operation(
        self,
        operation: str,
        operation_name: str,
        operation_arg: object | None = None,
    ) -> None:
        if self._thread is not None:
            return

        self._set_controls_enabled(False)

        self.log_label.setText(
            f"{operation_name} ξεκίνησε...\n"
            "Παρακαλώ περίμενε μέχρι να ολοκληρωθεί."
        )

        self._thread = QThread(self)
        self._worker = SQLToolWorker(
            operation,
            operation_name,
            operation_arg,
        )

        self._worker.moveToThread(self._thread)

        self._thread.started.connect(
            self._worker.run
        )

        self._worker.finished.connect(
            self._operation_finished
        )

        self._worker.failed.connect(
            self._operation_failed
        )

        self._worker.finished.connect(
            self._worker.deleteLater
        )

        self._worker.failed.connect(
            self._worker.deleteLater
        )

        self._worker.finished.connect(
            self._thread.quit
        )

        self._worker.failed.connect(
            self._thread.quit
        )

        self._thread.finished.connect(
            self._thread.deleteLater
        )

        self._thread.finished.connect(
            self._thread_finished
        )

        self._thread.start()

    def _operation_finished(
        self,
        result: SQLToolResult,
        operation_name: str,
    ) -> None:
        self._set_controls_enabled(True)

        if result.success:
            if operation_name in (
                "Delete MyDATA Responses",
                "Delete MyDATA Responses Before Date",
            ):
                if result.affected_rows >= 0:
                    message = (
                        f"{operation_name} ολοκληρώθηκε επιτυχώς.\n"
                        f"Διαγράφηκαν εγγραφές: "
                        f"{result.affected_rows}"
                    )
                else:
                    message = (
                        f"{operation_name} ολοκληρώθηκε επιτυχώς."
                    )
            else:
                message = (
                    f"{operation_name} ολοκληρώθηκε επιτυχώς."
                )

            self.log_label.setText(message)

            QMessageBox.information(
                self,
                operation_name,
                message,
            )

        else:
            self.log_label.setText(
                f"{operation_name} απέτυχε.\n"
                f"{result.message}"
            )

            QMessageBox.critical(
                self,
                operation_name,
                (
                    f"Η λειτουργία απέτυχε.\n\n"
                    f"{result.message}"
                ),
            )

    def _operation_failed(
        self,
        message: str,
        operation_name: str,
    ) -> None:
        self._set_controls_enabled(True)

        self.log_label.setText(
            f"{operation_name} απέτυχε.\n"
            f"{message}"
        )

        QMessageBox.critical(
            self,
            operation_name,
            (
                f"Η λειτουργία απέτυχε.\n\n"
                f"{message}"
            ),
        )

    def _thread_finished(self) -> None:
        self._worker = None
        self._thread = None

    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------

    def _set_controls_enabled(self, enabled: bool) -> None:
        database_selected = database_context.is_selected()

        if hasattr(self, "delete_button") and self.delete_button:
            self.delete_button.setEnabled(
                enabled and database_selected
            )

        if hasattr(self, "failed_mydata_button") and self.failed_mydata_button:
            self.failed_mydata_button.setEnabled(
                enabled
                and database_selected
                and self._failed_mydata_payments_supported
            )

        if hasattr(self, "delete_before_date_edit") and self.delete_before_date_edit:
            self.delete_before_date_edit.setEnabled(
                enabled and database_selected
            )

        if hasattr(self, "delete_before_date_button") and self.delete_before_date_button:
            self.delete_before_date_button.setEnabled(
                enabled and database_selected
            )

        if hasattr(self, "rebuild_button") and self.rebuild_button:
            self.rebuild_button.setEnabled(
                enabled and database_selected
            )

        if hasattr(self, "shrink_button") and self.shrink_button:
            self.shrink_button.setEnabled(
                enabled and database_selected
            )

    def _on_database_changed(self, _database: object) -> None:
        self._refresh_database_capabilities()

    def _refresh_database_capabilities(self) -> None:
        if not database_context.is_selected():
            self._failed_mydata_payments_supported = False
        else:
            try:
                self._failed_mydata_payments_supported = (
                    self.service.supports_failed_mydata_payments()
                )
            except Exception:
                self._failed_mydata_payments_supported = False

        if hasattr(self, "failed_mydata_button") and self.failed_mydata_button:
            self.failed_mydata_button.setEnabled(
                database_context.is_selected()
                and self._failed_mydata_payments_supported
            )

            if self._failed_mydata_payments_supported:
                self.failed_mydata_button.setText(
                    "DELETE FAILED PAYMENTS"
                )
            else:
                self.failed_mydata_button.setText(
                    "NOT AVAILABLE"
                )

        if hasattr(self, "delete_before_date_edit") and self.delete_before_date_edit:
            self.delete_before_date_edit.setEnabled(
                database_context.is_selected()
            )

        if hasattr(self, "delete_before_date_button") and self.delete_before_date_button:
            self.delete_before_date_button.setEnabled(
                database_context.is_selected()
            )

    def _clear_log(self) -> None:
        if database_context.is_selected():
            self.log_label.setText(
                "Έτοιμο. Επίλεξε ένα SQL Tool."
            )
        else:
            self.log_label.setText(
                "Δεν έχει επιλεγεί ενεργή βάση δεδομένων."
            )