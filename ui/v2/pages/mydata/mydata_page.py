from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, QThread, Signal, QDate
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.database.database_context import database_context
from core.mydata.mydata_service import MyDataInvoice, MyDataService

from ui.v2.widgets.page_layout import (
    PAGE_LAYOUT_STYLE,
    setup_page_layout,
)


class MyDataSendWorker(QThread):
    progress = Signal(int, int, object, object)
    finished_result = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        service: MyDataService,
        invoices: list[MyDataInvoice],
    ) -> None:
        super().__init__()

        self.service = service
        self.invoices = invoices

    def run(self) -> None:
        results: list[dict[str, Any]] = []

        try:
            total = len(self.invoices)

            for index, invoice in enumerate(self.invoices, start=1):
                try:
                    result = self.service.send_invoice(
                        invoice.invoice_id
                    )

                    if isinstance(result, dict):
                        success = bool(
                            result.get("success", False)
                        )

                        invoice.sent = success

                        if success:
                            invoice.mydata_state = "SENT"
                            invoice.send_status = result.get("status_code")
                            invoice.send_message = (
                                result.get("message")
                                or "Document sent successfully."
                            )
                            invoice.mark = (
                                result.get("mark")
                                or invoice.mark
                            )
                            invoice.impact_link = (
                                result.get("impact_link")
                                or invoice.impact_link
                            )
                        else:
                            invoice.mydata_state = "PENDING"
                            invoice.send_status = (
                                result.get("status_code")
                                or result.get("status")
                                or "FAILED"
                            )
                            invoice.send_message = (
                                result.get("message")
                                or "Document could not be sent."
                            )

                    results.append(
                        {
                            "invoice": invoice,
                            "result": result,
                            "success": bool(
                                isinstance(result, dict)
                                and result.get("success", False)
                            ),
                        }
                    )

                except Exception as exc:
                    invoice.sent = False
                    invoice.mydata_state = "PENDING"
                    invoice.send_status = "FAILED"
                    invoice.send_message = str(exc)

                    results.append(
                        {
                            "invoice": invoice,
                            "result": {
                                "success": False,
                                "status": "ERROR",
                                "message": str(exc),
                            },
                            "success": False,
                        }
                    )

                self.progress.emit(
                    index,
                    total,
                    invoice,
                    results[-1],
                )

            self.finished_result.emit(results)

        except Exception as exc:
            self.failed.emit(str(exc))


class MyDataSearchWorker(QThread):
    """Run the myDATA document search outside the Qt GUI thread."""

    finished_result = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        service: MyDataService,
        start_date: str,
        end_date: str,
    ) -> None:
        super().__init__()

        self.service = service
        self.start_date = start_date
        self.end_date = end_date

    def run(self) -> None:
        try:
            invoices = self.service.search(
                self.start_date,
                self.end_date,
            )
            self.finished_result.emit(invoices)
        except Exception as exc:
            self.failed.emit(str(exc))


class MyDataPage(QWidget):
    """
    AIO Toolbox myDATA Manager.

    Provides:
    - UDL/database selection
    - document search by date
    - Pending/Sent tabs
    - Select All
    - Send Selected
    - Send All
    - send progress
    - failure reporting
    - MARK
    - Impact Link
    """

    def __init__(self) -> None:
        super().__init__()

        self.service = MyDataService()

        self.invoices: list[MyDataInvoice] = []
        self.pending_invoices: list[MyDataInvoice] = []
        self.sent_invoices: list[MyDataInvoice] = []

        self.current_tab = "pending"
        self.worker: MyDataSendWorker | None = None
        self.search_worker: MyDataSearchWorker | None = None

        self._build_ui()
        self._connect_signals()
        self._update_connection_status()

    # ============================================================
    # UI
    # ============================================================

    def _build_ui(self) -> None:
        root, title, subtitle = setup_page_layout(
            self,
            "myDATA Manager",
            "Check, validate and send documents to myDATA",
        )

        # Keep the connection indicator close to the page header.
        self.connection_label = QLabel()
        self.connection_label.setObjectName(
            "myDataConnectionStatus"
        )
        root.addWidget(self.connection_label)

        root.addWidget(self._create_database_card())
        root.addWidget(self._create_search_card())
        root.addWidget(self._create_action_bar())
        root.addWidget(self._create_progress_card())
        root.addWidget(self._create_failure_card())
        root.addWidget(self._create_status_tabs())
        root.addWidget(self._create_table(), 1)

        self.setStyleSheet(
            PAGE_LAYOUT_STYLE
            + """
            QLabel#myDataConnectionStatus {
                color: #718096;
                font-size: 10px;
                font-weight: 600;
            }

            QLabel#myDataConnectionStatus[connected="true"] {
                color: #16803C;
            }

            QFrame#myDataCard {
                background: #FFFFFF;
                border: 1px solid #DCE3EC;
                border-radius: 10px;
            }

            QLabel#cardTitle {
                color: #526176;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#databaseLabel {
                color: #26344D;
                font-size: 11px;
                font-weight: 600;
            }

            QLabel#fieldLabel {
                color: #526176;
                font-size: 10px;
                font-weight: 600;
            }

            QDateEdit {
                min-height: 36px;
                padding: 4px 9px;
                background: #F8FAFC;
                color: #26344D;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                font-size: 11px;
            }

            QDateEdit:focus {
                border: 1px solid #4C8BF5;
                background: #FFFFFF;
            }

            QPushButton#primaryButton,
            QPushButton#secondaryButton,
            QPushButton#dangerButton {
                min-height: 36px;
                padding: 0 14px;
                border-radius: 6px;
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton#primaryButton {
                background: #2F6FED;
                color: #FFFFFF;
                border: 1px solid #2F6FED;
            }

            QPushButton#primaryButton:hover {
                background: #245DCA;
            }

            QPushButton#primaryButton:disabled {
                color: #A8B2C0;
                background: #F1F4F8;
                border-color: #E1E6ED;
            }

            QPushButton#secondaryButton {
                background: #FFFFFF;
                color: #34435B;
                border: 1px solid #CBD5E1;
            }

            QPushButton#secondaryButton:hover {
                background: #F4F7FB;
            }

            QPushButton#secondaryButton:disabled {
                color: #A8B2C0;
                background: #F1F4F8;
                border-color: #E1E6ED;
            }

            QPushButton#dangerButton {
                background: #FFF1F2;
                color: #B42318;
                border: 1px solid #F3B4B0;
            }

            QPushButton#dangerButton:hover {
                background: #FFE4E6;
            }

            QFrame#myDataProgressCard {
                background: #F3F7FF;
                border: 1px solid #D8E3FF;
                border-radius: 10px;
            }

            QLabel#myDataProgressDetail {
                color: #526176;
                font-size: 11px;
                font-weight: 600;
            }

            QLabel#myDataProgressCurrent {
                color: #315EF5;
                font-size: 10px;
            }

            QFrame#myDataFailureCard {
                background: #FFF8F3;
                border: 1px solid #F2D0B5;
                border-radius: 10px;
            }

            QProgressBar {
                min-height: 12px;
                border: 1px solid #D6DEEA;
                border-radius: 6px;
                background: #FFFFFF;
                text-align: center;
                color: #26344D;
            }

            QProgressBar::chunk {
                border-radius: 5px;
                background: #315EF5;
            }

            QPushButton#myDataTab {
                min-width: 125px;
                min-height: 36px;
                padding: 0 15px;
                border: 1px solid #DCE3EC;
                border-bottom: 2px solid transparent;
                border-radius: 6px 6px 0 0;
                background: #F7F9FC;
                color: #667085;
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton#myDataTab:checked {
                background: #FFFFFF;
                color: #2F6FED;
                border-bottom: 2px solid #2F6FED;
            }

            QFrame#myDataTableContainer {
                background: #FFFFFF;
                border: 1px solid #DCE3EC;
                border-radius: 10px;
            }

            QTableWidget {
                background: #FFFFFF;
                alternate-background-color: #F8FAFC;
                border: none;
                gridline-color: #E7ECF2;
                color: #344054;
                selection-background-color: #E7F0FF;
                selection-color: #26344D;
            }

            QHeaderView::section {
                min-height: 38px;
                padding: 0 8px;
                border: none;
                border-bottom: 1px solid #DCE3EC;
                background: #F2F5F9;
                color: #526176;
                font-size: 10px;
                font-weight: 600;
            }

            QTableWidget::item {
                padding: 5px;
            }

            QTableWidget::item:selected {
                background: #E7F0FF;
                color: #26344D;
            }
            """
        )

    def _create_header(self) -> QWidget:
        container = QWidget()

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title = QLabel("myDATA Manager")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Check, validate and send documents to myDATA"
        )
        subtitle.setObjectName("pageSubtitle")

        self.connection_label = QLabel()
        self.connection_label.setObjectName(
            "myDataConnectionStatus"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(5)
        layout.addWidget(self.connection_label)

        return container

    def _create_database_card(self) -> QWidget:
        card = QFrame()
        card.setObjectName("myDataCard")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        title = QLabel("Database")
        title.setObjectName("cardTitle")

        self.database_label = QLabel("No database selected")
        self.database_label.setObjectName("databaseLabel")
        self.database_label.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(self.database_label, 1)

        return card

    def _create_search_card(self) -> QWidget:
        card = QFrame()
        card.setObjectName("myDataCard")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        title = QLabel("Search Documents")
        title.setObjectName("cardTitle")

        from_label = QLabel("From")
        from_label.setObjectName("fieldLabel")

        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDisplayFormat(
            "dd/MM/yyyy"
        )
        self.from_date.setDate(
            QDate.currentDate().addMonths(-1)
        )
        self.from_date.setFixedWidth(120)

        to_label = QLabel("To")
        to_label.setObjectName("fieldLabel")

        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDisplayFormat(
            "dd/MM/yyyy"
        )
        self.to_date.setDate(
            QDate.currentDate()
        )
        self.to_date.setFixedWidth(120)

        self.search_button = QPushButton(
            "Search Documents"
        )
        self.search_button.setObjectName(
            "primaryButton"
        )
        self.search_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        layout.addWidget(title)
        layout.addSpacing(12)
        layout.addWidget(from_label)
        layout.addWidget(self.from_date)
        layout.addWidget(to_label)
        layout.addWidget(self.to_date)
        layout.addStretch()
        layout.addWidget(self.search_button)

        return card

    def _create_action_bar(self) -> QWidget:
        container = QWidget()

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.select_all_button = QPushButton(
            "Select All"
        )
        self.send_selected_button = QPushButton(
            "Send Selected"
        )
        self.send_all_button = QPushButton(
            "Send All"
        )
        self.delete_mark_button = QPushButton(
            "Delete M.A.R.K."
        )

        for button in (
            self.select_all_button,
            self.send_selected_button,
            self.send_all_button,
            self.delete_mark_button,
        ):
            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

        self.select_all_button.setObjectName(
            "secondaryButton"
        )
        self.send_selected_button.setObjectName(
            "primaryButton"
        )
        self.send_all_button.setObjectName(
            "primaryButton"
        )
        self.delete_mark_button.setObjectName(
            "dangerButton"
        )

        layout.addWidget(
            self.select_all_button
        )
        layout.addWidget(
            self.send_selected_button
        )
        layout.addWidget(
            self.send_all_button
        )
        layout.addWidget(
            self.delete_mark_button
        )
        layout.addStretch()

        return container

    def _create_progress_card(self) -> QWidget:
        self.progress_card = QFrame()
        self.progress_card.setObjectName(
            "myDataProgressCard"
        )
        self.progress_card.setVisible(False)

        layout = QVBoxLayout(
            self.progress_card
        )
        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )
        layout.setSpacing(8)

        self.progress_title = QLabel(
            "Sending documents..."
        )
        self.progress_title.setObjectName(
            "cardTitle"
        )

        self.progress_detail = QLabel(
            "0 / 0 documents"
        )
        self.progress_detail.setObjectName(
            "myDataProgressDetail"
        )

        self.progress_current = QLabel(
            "Preparing..."
        )
        self.progress_current.setObjectName(
            "myDataProgressCurrent"
        )

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        layout.addWidget(
            self.progress_title
        )
        layout.addWidget(
            self.progress_detail
        )
        layout.addWidget(
            self.progress_current
        )
        layout.addWidget(
            self.progress_bar
        )

        return self.progress_card

    def _create_failure_card(self) -> QWidget:
        self.failure_card = QFrame()
        self.failure_card.setObjectName(
            "myDataFailureCard"
        )
        self.failure_card.setVisible(False)

        layout = QVBoxLayout(
            self.failure_card
        )
        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )
        layout.setSpacing(6)

        title = QLabel(
            "Failed Documents"
        )
        title.setObjectName("cardTitle")

        self.failure_detail = QLabel()
        self.failure_detail.setWordWrap(True)

        self.view_errors_button = QPushButton(
            "View Errors"
        )
        self.view_errors_button.setObjectName(
            "secondaryButton"
        )
        self.view_errors_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.view_errors_button.clicked.connect(
            self._show_failure_dialog
        )

        layout.addWidget(title)
        layout.addWidget(
            self.failure_detail
        )
        layout.addWidget(
            self.view_errors_button,
            0,
            Qt.AlignmentFlag.AlignLeft,
        )

        return self.failure_card

    def _create_status_tabs(self) -> QWidget:
        container = QWidget()

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.pending_tab = QPushButton(
            "Pending (0)"
        )
        self.sent_tab = QPushButton(
            "Sent (0)"
        )

        self.pending_tab.setCheckable(True)
        self.sent_tab.setCheckable(True)

        self.pending_tab.setChecked(True)

        self.pending_tab.setObjectName(
            "myDataTab"
        )
        self.sent_tab.setObjectName(
            "myDataTab"
        )

        self.pending_tab.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.sent_tab.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        layout.addWidget(
            self.pending_tab
        )
        layout.addWidget(
            self.sent_tab
        )
        layout.addStretch()

        return container

    def _create_table(self) -> QWidget:
        container = QFrame()
        container.setObjectName(
            "myDataTableContainer"
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            [
                "",
                "Type",
                "Document",
                "Date",
                "A/A",
                "VAT No.",
                "ID",
                "Status",
                "MARK",
                "Impact Link",
            ]
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setAlternatingRowColors(False)
        self.table.setSortingEnabled(False)
        self.table.setWordWrap(False)

        header = self.table.horizontalHeader()

        header.setStretchLastSection(True)

        widths = [
            42,
            75,
            270,
            105,
            75,
            120,
            105,
            95,
            150,
            115,
        ]

        for index, width in enumerate(widths):
            self.table.setColumnWidth(
                index,
                width,
            )

        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        return container

    # ============================================================
    # SIGNALS
    # ============================================================

    def _connect_signals(self) -> None:
        self.search_button.clicked.connect(
            self._search_documents
        )

        self.select_all_button.clicked.connect(
            self._toggle_select_all
        )

        self.send_selected_button.clicked.connect(
            self._send_selected
        )

        self.send_all_button.clicked.connect(
            self._send_all
        )

        self.delete_mark_button.clicked.connect(
            self._delete_mark
        )

        self.pending_tab.clicked.connect(
            lambda: self._change_tab("pending")
        )

        self.sent_tab.clicked.connect(
            lambda: self._change_tab("sent")
        )

        self.table.cellDoubleClicked.connect(
            self._table_double_clicked
        )

        database_context.database_changed.connect(
            self._on_database_changed
        )

    # ============================================================
    # DATABASE
    # ============================================================

    def _on_database_changed(
        self,
        database: object,
    ) -> None:
        self._update_connection_status()

    def _update_connection_status(self) -> None:
        database = database_context.active()

        if database:
            name = database.get("name") or "Unknown database"
            server = database.get("server") or "Unknown server"

            self.database_label.setText(
                f"{name}  |  {server}"
            )

            self.connection_label.setText(
                "● Connected"
            )

            self.connection_label.setProperty(
                "connected",
                True,
            )
        else:
            self.database_label.setText(
                "No database selected"
            )

            self.connection_label.setText(
                "● Not Connected"
            )

            self.connection_label.setProperty(
                "connected",
                False,
            )

        self.connection_label.style().unpolish(
            self.connection_label
        )
        self.connection_label.style().polish(
            self.connection_label
        )
        self.connection_label.update()

    # ============================================================
    # SEARCH
    # ============================================================

    def _search_documents(self) -> None:
        if not database_context.is_selected():
            QMessageBox.warning(
                self,
                "Database Required",
                "Please connect to a database from the Database button in the header first.",
            )
            return

        if self.search_worker is not None:
            return

        start = self.from_date.date()
        end = self.to_date.date()

        if start > end:
            QMessageBox.warning(
                self,
                "Invalid Date Range",
                "The From date cannot be later than the To date.",
            )
            return

        start_date = start.toString("yyyyMMdd")
        end_date = end.toString("yyyyMMdd")

        # The SQL search can take time on some customer installations.
        # Run it in a worker thread so the Qt GUI remains responsive.
        self._set_controls_enabled(False)
        self.search_button.setText("Searching...")

        self.search_worker = MyDataSearchWorker(
            self.service,
            start_date,
            end_date,
        )

        self.search_worker.finished_result.connect(
            self._on_search_finished
        )
        self.search_worker.failed.connect(
            self._on_search_failed
        )
        self.search_worker.finished.connect(
            self._cleanup_search_worker
        )

        self.search_worker.start()

    def _on_search_finished(self, invoices: object) -> None:
        if not isinstance(invoices, list):
            invoices = []

        self.invoices = invoices

        self.pending_invoices = [
            invoice
            for invoice in invoices
            if isinstance(invoice, MyDataInvoice)
            and str(invoice.mydata_state).upper() == "PENDING"
        ]

        self.sent_invoices = [
            invoice
            for invoice in invoices
            if isinstance(invoice, MyDataInvoice)
            and str(invoice.mydata_state).upper() == "SENT"
        ]

        self.current_tab = "pending"

        self._update_tab_counts()
        self._update_tab_state()
        self._populate_table()
        self.failure_card.setVisible(False)
        self._failed_invoices = []

        self.search_button.setText("Search Documents")
        self._set_controls_enabled(True)

    def _on_search_failed(self, message: str) -> None:
        self.search_button.setText("Search Documents")
        self._set_controls_enabled(True)

        QMessageBox.critical(
            self,
            "Search Error",
            f"Unable to search documents.\n\n{message}",
        )

    def _cleanup_search_worker(self) -> None:
        worker = self.search_worker

        if worker is None:
            return

        self.search_worker = None
        worker.deleteLater()

    # ============================================================
    # TABS / TABLE
    # ============================================================

    def _change_tab(self, tab: str) -> None:
        self.current_tab = tab

        self._update_tab_state()
        self._populate_table()

    def _update_tab_counts(self) -> None:
        self.pending_tab.setText(
            f"Pending ({len(self.pending_invoices)})"
        )

        self.sent_tab.setText(
            f"Sent ({len(self.sent_invoices)})"
        )

    def _update_tab_state(self) -> None:
        pending = (
            self.current_tab == "pending"
        )

        self.pending_tab.setChecked(
            pending
        )
        self.sent_tab.setChecked(
            not pending
        )

        self.select_all_button.setEnabled(
            pending
        )

        self.send_selected_button.setEnabled(
            pending
            and bool(self.pending_invoices)
        )

        self.send_all_button.setEnabled(
            pending
            and bool(self.pending_invoices)
        )

    def _current_invoices(
        self,
    ) -> list[MyDataInvoice]:
        if self.current_tab == "sent":
            return self.sent_invoices

        return self.pending_invoices

    def _populate_table(self) -> None:
        """Populate the table efficiently, including large Sent result sets.

        Sent documents can easily contain many thousands of rows. Creating a
        QWidget/QCheckBox for every row makes Qt spend a very long time laying
        out child widgets and can make the application appear frozen.

        Only Pending rows need checkboxes because the send actions operate on
        Pending documents. Sent rows therefore use plain table items only.
        The row count is allocated once instead of repeatedly calling
        insertRow(), which also reduces the cost substantially.
        """
        invoices = self._current_invoices()
        is_pending_tab = self.current_tab == "pending"

        self.table.setUpdatesEnabled(False)
        self.table.blockSignals(True)

        try:
            self.table.clearContents()
            self.table.setRowCount(len(invoices))

            for row, invoice in enumerate(invoices):
                # Checkboxes are only needed for Pending documents. Sent can
                # contain many thousands of rows, so avoid one QWidget per row.
                if is_pending_tab:
                    checkbox = QCheckBox()
                    checkbox.setProperty(
                        "invoice_id",
                        invoice.invoice_id,
                    )

                    checkbox_widget = QWidget()
                    checkbox_layout = QHBoxLayout(
                        checkbox_widget
                    )
                    checkbox_layout.setContentsMargins(0, 0, 0, 0)
                    checkbox_layout.setAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )
                    checkbox_layout.addWidget(checkbox)

                    self.table.setCellWidget(
                        row,
                        0,
                        checkbox_widget,
                    )

                self._set_item(row, 1, invoice.invoice_type)
                self._set_item(row, 2, invoice.document_name)
                self._set_item(row, 3, invoice.issue_date)
                self._set_item(row, 4, invoice.aa)
                self._set_item(row, 5, invoice.cust_afm)
                self._set_item(row, 6, invoice.invoice_id)

                status = (
                    "SENT"
                    if str(invoice.mydata_state).upper() == "SENT"
                    else "PENDING"
                )
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                self.table.setItem(row, 7, status_item)

                mark_item = QTableWidgetItem(
                    str(invoice.mark) if invoice.mark else "-"
                )
                mark_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                self.table.setItem(row, 8, mark_item)

                impact_item = QTableWidgetItem()
                if invoice.impact_link:
                    impact_item.setText("Open")
                    impact_item.setData(
                        Qt.ItemDataRole.UserRole,
                        invoice.impact_link,
                    )
                else:
                    impact_item.setText("-")

                impact_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                self.table.setItem(row, 9, impact_item)
        finally:
            self.table.blockSignals(False)
            self.table.setUpdatesEnabled(True)
            self.table.viewport().update()

    def _set_item(
        self,
        row: int,
        column: int,
        value: object,
    ) -> None:
        item = QTableWidgetItem(
            "" if value is None else str(value)
        )

        self.table.setItem(
            row,
            column,
            item,
        )

    # ============================================================
    # SELECTION
    # ============================================================

    def _checkboxes(self) -> list[QCheckBox]:
        result: list[QCheckBox] = []

        for row in range(
            self.table.rowCount()
        ):
            widget = self.table.cellWidget(
                row,
                0,
            )

            if widget is None:
                continue

            checkbox = widget.findChild(
                QCheckBox
            )

            if checkbox is not None:
                result.append(checkbox)

        return result

    def _toggle_select_all(self) -> None:
        checkboxes = self._checkboxes()

        if not checkboxes:
            return

        select_all = any(
            not checkbox.isChecked()
            for checkbox in checkboxes
        )

        for checkbox in checkboxes:
            checkbox.setChecked(
                select_all
            )

        self.select_all_button.setText(
            "Deselect All"
            if select_all
            else "Select All"
        )

    def _selected_invoices(
        self,
    ) -> list[MyDataInvoice]:
        invoices = self._current_invoices()

        selected: list[MyDataInvoice] = []

        for row in range(
            self.table.rowCount()
        ):
            widget = self.table.cellWidget(
                row,
                0,
            )

            if widget is None:
                continue

            checkbox = widget.findChild(
                QCheckBox
            )

            if (
                checkbox is not None
                and checkbox.isChecked()
                and row < len(invoices)
            ):
                selected.append(
                    invoices[row]
                )

        return selected

    # ============================================================
    # SEND
    # ============================================================

    def _send_selected(self) -> None:
        invoices = self._selected_invoices()

        if not invoices:
            QMessageBox.information(
                self,
                "No Documents Selected",
                "Please select at least one pending document.",
            )
            return

        self._send_invoices(invoices)

    def _send_all(self) -> None:
        if not self.pending_invoices:
            return

        answer = QMessageBox.question(
            self,
            "Send All Documents",
            (
                f"Send all "
                f"{len(self.pending_invoices)} "
                f"pending documents?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self._send_invoices(
            list(self.pending_invoices)
        )

    def _send_invoices(
        self,
        invoices: list[MyDataInvoice],
    ) -> None:
        if self.worker is not None:
            return

        if not invoices:
            return

        self.progress_card.setVisible(True)
        self.failure_card.setVisible(False)
        self._failed_invoices = []

        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)

        self.progress_detail.setText(
            f"0 / {len(invoices)} documents"
        )

        self.progress_current.setText(
            f"Preparing to send {len(invoices)} document(s)..."
        )

        self._set_controls_enabled(False)

        self.worker = MyDataSendWorker(
            self.service,
            invoices,
        )

        self.worker.progress.connect(
            self._on_send_progress
        )

        self.worker.finished_result.connect(
            self._on_send_finished
        )

        self.worker.failed.connect(
            self._on_send_failed
        )

        self.worker.finished.connect(
            self._cleanup_worker
        )

        self.worker.start()

    def _on_send_progress(
        self,
        current: int,
        total: int,
        invoice: MyDataInvoice,
        result: object,
    ) -> None:
        percentage = int(
            (current / total) * 100
        ) if total else 0

        self.progress_bar.setValue(
            percentage
        )

        self.progress_detail.setText(
            f"{current} / {total} documents"
        )

        self.progress_current.setText(
            f"Sending now: {invoice.document_name}"
        )

        self.progress_title.setText(
            "Sending documents..."
        )

        self._update_invoice_row(
            invoice
        )

    def _on_send_finished(
        self,
        results: object,
    ) -> None:
        if not isinstance(results, list):
            results = []

        successful: list[MyDataInvoice] = []
        failed: list[MyDataInvoice] = []

        for entry in results:
            if not isinstance(entry, dict):
                continue

            invoice = entry.get("invoice")

            if not isinstance(
                invoice,
                MyDataInvoice,
            ):
                continue

            if entry.get("success"):
                successful.append(invoice)
            else:
                failed.append(invoice)

        self._rebuild_invoice_lists(
            successful
        )

        self.progress_bar.setValue(100)

        self.progress_title.setText(
            "Send completed"
        )

        self.progress_detail.setText(
            (
                f"{len(results)} / {len(results)} documents"
                f"   |   Successful: {len(successful)}"
                f"   |   Failed: {len(failed)}"
            )
        )

        self.progress_current.setText(
            "All documents have been processed."
        )

        self._update_tab_counts()
        self._update_tab_state()
        self._populate_table()

        if failed:
            self._show_failures(failed)

        else:
            self.failure_card.setVisible(False)

            QMessageBox.information(
                self,
                "Send Completed",
                (
                    f"{len(successful)} "
                    "document(s) sent successfully."
                ),
            )

        self._set_controls_enabled(True)

    def _on_send_failed(
        self,
        message: str,
    ) -> None:
        self.progress_card.setVisible(False)

        QMessageBox.critical(
            self,
            "Send Error",
            message,
        )

        self._set_controls_enabled(True)

    def _rebuild_invoice_lists(
        self,
        successful: list[MyDataInvoice],
    ) -> None:
        successful_ids = {
            invoice.invoice_id
            for invoice in successful
        }

        self.pending_invoices = [
            invoice
            for invoice in self.pending_invoices
            if invoice.invoice_id
            not in successful_ids
        ]

        existing_sent_ids = {
            invoice.invoice_id
            for invoice in self.sent_invoices
        }

        for invoice in successful:
            if (
                invoice.invoice_id
                not in existing_sent_ids
            ):
                self.sent_invoices.append(
                    invoice
                )

        self.invoices = (
            list(self.pending_invoices)
            + list(self.sent_invoices)
        )

    def _update_invoice_row(
        self,
        invoice: MyDataInvoice,
    ) -> None:
        invoices = self._current_invoices()

        try:
            row = next(
                index
                for index, item in enumerate(
                    invoices
                )
                if item.invoice_id
                == invoice.invoice_id
            )
        except StopIteration:
            return

        status = (
            "SENT"
            if str(
                invoice.mydata_state
            ).upper()
            == "SENT"
            else "PENDING"
        )

        self._set_item(
            row,
            7,
            status,
        )

        self._set_item(
            row,
            8,
            invoice.mark or "-",
        )

        impact = QTableWidgetItem()

        if invoice.impact_link:
            impact.setText("Open")
            impact.setData(
                Qt.ItemDataRole.UserRole,
                invoice.impact_link,
            )
        else:
            impact.setText("-")

        impact.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.table.setItem(
            row,
            9,
            impact,
        )

    # ============================================================
    # FAILURES
    # ============================================================

    def _show_failures(
        self,
        invoices: list[MyDataInvoice],
    ) -> None:
        self._failed_invoices = list(invoices)

        count = len(invoices)
        self.failure_detail.setText(
            f"{count} document(s) failed to send. "
            "Click View Errors to inspect each failure."
        )

        self.view_errors_button.setEnabled(
            bool(invoices)
        )
        self.failure_card.setVisible(True)

    def _show_failure_dialog(self) -> None:
        invoices = getattr(
            self,
            "_failed_invoices",
            [],
        )

        if not invoices:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Failed Documents")
        dialog.setMinimumSize(760, 460)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        summary = QLabel(
            f"{len(invoices)} document(s) failed to send. "
            "Select a document to view its error."
        )
        summary.setObjectName("cardTitle")
        layout.addWidget(summary)

        content = QHBoxLayout()
        content.setSpacing(12)

        document_list = QListWidget()
        document_list.setMinimumWidth(300)

        details = QPlainTextEdit()
        details.setReadOnly(True)
        details.setPlaceholderText(
            "Select a failed document to view the error."
        )

        for invoice in invoices:
            aa = str(invoice.aa or "-")
            name = str(invoice.document_name or "Document")
            item = QListWidgetItem(
                f"A/A {aa}  |  {name}"
            )
            item.setData(
                Qt.ItemDataRole.UserRole,
                invoice,
            )
            document_list.addItem(item)

        def show_item_error(item: QListWidgetItem) -> None:
            invoice = item.data(
                Qt.ItemDataRole.UserRole
            )

            status = (
                invoice.send_status
                if invoice.send_status not in (None, "")
                else "-"
            )
            message = (
                invoice.send_message
                or "Unknown error."
            )

            details.setPlainText(
                f"Document: {invoice.document_name or '-'}\n"
                f"A/A: {invoice.aa or '-'}\n"
                f"Invoice ID: {invoice.invoice_id}\n"
                f"HTTP Status: {status}\n\n"
                f"Error:\n{message}"
            )

        document_list.currentItemChanged.connect(
            lambda current, previous: (
                show_item_error(current)
                if current is not None
                else None
            )
        )

        content.addWidget(document_list, 1)
        content.addWidget(details, 2)
        layout.addLayout(content, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        buttons.rejected.connect(dialog.reject)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        if document_list.count():
            document_list.setCurrentRow(0)

        dialog.exec()

    # ============================================================
    # ACTIONS
    # ============================================================

    def _delete_mark(self) -> None:
        QMessageBox.information(
            self,
            "Delete M.A.R.K.",
            (
                "Delete M.A.R.K. is not implemented "
                "by the existing MyDATA service yet."
            ),
        )

    def _table_double_clicked(
        self,
        row: int,
        column: int,
    ) -> None:
        if column != 9:
            return

        item = self.table.item(
            row,
            column,
        )

        if item is None:
            return

        url = item.data(
            Qt.ItemDataRole.UserRole
        )

        if url:
            QDesktopServices.openUrl(
                str(url)
            )

    # ============================================================
    # STATE
    # ============================================================

    def _set_controls_enabled(
        self,
        enabled: bool,
    ) -> None:
        self.search_button.setEnabled(
            enabled
        )
        self.from_date.setEnabled(
            enabled
        )
        self.to_date.setEnabled(
            enabled
        )
        self.pending_tab.setEnabled(
            enabled
        )
        self.sent_tab.setEnabled(
            enabled
        )

        if enabled:
            self._update_tab_state()

        else:
            self.select_all_button.setEnabled(
                False
            )
            self.send_selected_button.setEnabled(
                False
            )
            self.send_all_button.setEnabled(
                False
            )
            self.delete_mark_button.setEnabled(
                False
            )

    def _cleanup_worker(self) -> None:
        worker = self.worker

        if worker is None:
            return

        self.worker = None

        worker.deleteLater()

    def _repolish(
        self,
        widget: QWidget,
    ) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    # ============================================================
    # STYLE
    # ============================================================