from __future__ import annotations

from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHeaderView,
)

from core.pending_orders.pending_order_service import (
    PendingOrderService,
)

from ui.v2.widgets.page_layout import (
    PAGE_LAYOUT_STYLE,
    setup_page_layout,
)


class PendingOrderPage(QFrame):
    """
    AIO Toolbox page for finding and closing pending orders.
    """

    home_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName(
            "pendingOrderPage"
        )

        self.service = PendingOrderService()

        self._build_ui()
        self._connect_signals()
        self._update_buttons()

    # ==========================================================
    # UI
    # ==========================================================

    def _build_ui(self):
        layout, title, subtitle = setup_page_layout(
            self,
            "Delete Pending Order",
            "Find and close pending records of an order",
        )

        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        # ------------------------------------------------------
        # SEARCH CARD
        # ------------------------------------------------------

        search_card = QGroupBox("Search Pending Order")
        search_card.setObjectName("contentCard")

        search_layout = QVBoxLayout(search_card)
        search_layout.setContentsMargins(14, 18, 14, 14)
        search_layout.setSpacing(10)

        search_description = QLabel(
            "Enter the order number and date to find pending records."
        )
        search_description.setObjectName("cardDescription")
        search_description.setWordWrap(True)

        search_layout.addWidget(search_description)

        number_label = QLabel("Order Number")
        number_label.setObjectName("fieldLabel")

        self.note_no_edit = QLineEdit()
        self.note_no_edit.setObjectName("fieldEdit")
        self.note_no_edit.setPlaceholderText("Enter order number")
        self.note_no_edit.setMinimumHeight(36)

        search_layout.addWidget(number_label)
        search_layout.addWidget(self.note_no_edit)

        date_label = QLabel("Order Date")
        date_label.setObjectName("fieldLabel")

        self.date_edit = QDateEdit()
        self.date_edit.setObjectName("fieldEdit")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumHeight(36)

        search_layout.addWidget(date_label)
        search_layout.addWidget(self.date_edit)

        self.search_button = QPushButton("Search Order")
        self.search_button.setObjectName("primaryButton")
        self.search_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.search_button.setMinimumHeight(36)

        search_layout.addWidget(self.search_button)
        search_layout.addStretch()

        # ------------------------------------------------------
        # RESULT CARD
        # ------------------------------------------------------

        result_card = QGroupBox("Pending Order")
        result_card.setObjectName("contentCard")

        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(14, 18, 14, 14)
        result_layout.setSpacing(10)

        self.result_description = QLabel(
            "No pending order selected."
        )
        self.result_description.setObjectName("cardDescription")
        self.result_description.setWordWrap(True)

        result_layout.addWidget(self.result_description)

        self.result_status = QLabel(
            "Waiting for search..."
        )
        self.result_status.setObjectName("resultStatus")

        result_layout.addWidget(self.result_status)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.setObjectName("secondaryButton")
        self.select_all_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.select_all_button.setMinimumHeight(36)

        self.change_button = QPushButton(
            "Delete Pending Order"
        )
        self.change_button.setObjectName("dangerButton")
        self.change_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.change_button.setMinimumHeight(36)

        actions_layout.addWidget(self.select_all_button)
        actions_layout.addWidget(self.change_button)
        actions_layout.addStretch()

        result_layout.addLayout(actions_layout)

        self.table = QTableWidget()
        self.table.setObjectName("pendingOrderTable")
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            [
                "",
                "SalesTransOID",
                "Status",
                "Order Number",
                "Order Date",
            ]
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.ExtendedSelection
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Fixed,
        )
        header.resizeSection(0, 44)

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Interactive,
        )
        header.resizeSection(1, 125)

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Interactive,
        )
        header.resizeSection(2, 90)

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Interactive,
        )
        header.resizeSection(3, 130)

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.Stretch,
        )

        result_layout.addWidget(self.table, 1)

        content_layout.addWidget(search_card, 1)
        content_layout.addWidget(result_card, 2)

        layout.addLayout(content_layout, 1)

        # ------------------------------------------------------
        # STATUS
        # ------------------------------------------------------

        status_panel = QFrame()
        status_panel.setObjectName("pageStatus")

        status_layout = QHBoxLayout(status_panel)
        status_layout.setContentsMargins(14, 10, 14, 10)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("pageStatusLabel")

        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        self.result_count_label = QLabel("0 records")
        self.result_count_label.setObjectName("pageStatusCount")

        status_layout.addWidget(self.result_count_label)
        layout.addWidget(status_panel)

        self.setStyleSheet(
            PAGE_LAYOUT_STYLE
            + """
            QLabel#cardDescription {
                color: #66758A;
                font-size: 10px;
            }

            QLabel#resultStatus {
                color: #526176;
                font-size: 10px;
                font-weight: 600;
            }

            QLineEdit#fieldEdit,
            QDateEdit#fieldEdit {
                min-height: 36px;
                padding: 4px 9px;
                background: #F8FAFC;
                color: #26344D;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                font-size: 11px;
            }

            QLineEdit#fieldEdit:focus,
            QDateEdit#fieldEdit:focus {
                border: 1px solid #4C8BF5;
                background: #FFFFFF;
            }

            QPushButton#dangerButton {
                min-height: 36px;
                padding: 0 14px;
                background: #FFF1F2;
                color: #B42318;
                border: 1px solid #F3B4B0;
                border-radius: 6px;
                font-weight: 600;
            }

            QPushButton#dangerButton:hover {
                background: #FFE4E6;
            }

            QPushButton#dangerButton:disabled {
                color: #A8B2C0;
                background: #F1F4F8;
                border-color: #E1E6ED;
            }

            QFrame#pageStatus {
                background: #F5F8FC;
                border: 1px solid #DCE3EC;
                border-radius: 7px;
            }

            QLabel#pageStatusLabel {
                color: #526176;
                font-size: 10px;
                font-weight: 600;
            }

            QLabel#pageStatusCount {
                color: #718096;
                font-size: 10px;
            }

            QTableWidget#pendingOrderTable {
                background: #FFFFFF;
                alternate-background-color: #F8FAFC;
                color: #26344D;
                border: 1px solid #DCE3EC;
                gridline-color: #E7ECF2;
                selection-background-color: #E7F0FF;
                selection-color: #26344D;
            }

            QHeaderView::section {
                background: #F2F5F9;
                color: #526176;
                padding: 8px;
                border: none;
                border-right: 1px solid #DCE3EC;
                border-bottom: 1px solid #DCE3EC;
                font-weight: 600;
            }

            QCheckBox#orderCheckbox {
                color: #40506A;
            }
            """
        )

    # ==========================================================
    # SIGNALS
    # ==========================================================

    def _connect_signals(self):
        self.search_button.clicked.connect(
            self.search_orders
        )

        self.select_all_button.clicked.connect(
            self.select_all
        )

        self.change_button.clicked.connect(
            self.change_selected
        )

        self.table.itemSelectionChanged.connect(
            self._sync_selection_with_checkboxes
        )

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search_orders(self):
        note_no = (
            self.note_no_edit
            .text()
            .strip()
        )

        if not note_no:
            self._show_error(
                "Please enter the order number."
            )
            return

        try:
            int(note_no)
        except ValueError:
            self._show_error(
                "The order number must be numeric."
            )
            return

        init_date = (
            self.date_edit
            .date()
            .toString("yyyyMMdd")
        )

        self.search_button.setEnabled(
            False
        )

        self.status_label.setText(
            "Searching..."
        )

        self.result_status.setText(
            "Searching..."
        )

        try:
            rows = self.service.search(
                note_no,
                init_date,
            )

            self.populate_table(
                rows
            )

            count = len(rows)

            self.result_count_label.setText(
                f"{count} records"
            )

            if count:
                self.result_description.setText(
                    f"{count} pending record(s) found."
                )

                self.result_status.setText(
                    "Pending records found."
                )

                self.status_label.setText(
                    f"Found {count} pending record(s)."
                )

            else:
                self.result_description.setText(
                    "No pending order found."
                )

                self.result_status.setText(
                    "No pending records found."
                )

                self.status_label.setText(
                    "No pending records found."
                )

        except Exception as exc:
            self.table.setRowCount(
                0
            )

            self.result_count_label.setText(
                "0 records"
            )

            self.result_description.setText(
                "Search failed."
            )

            self.result_status.setText(
                "Search failed."
            )

            self.status_label.setText(
                "Search failed."
            )

            QMessageBox.critical(
                self,
                "Delete Pending Order",
                str(exc),
            )

        finally:
            self.search_button.setEnabled(
                True
            )

            self._update_buttons()

    # ==========================================================
    # POPULATE
    # ==========================================================

    def populate_table(
        self,
        rows,
    ):
        self.table.blockSignals(
            True
        )

        try:
            self.table.clearContents()

            self.table.setRowCount(
                0
            )

            for row_index, order in enumerate(
                rows
            ):
                self.table.insertRow(
                    row_index
                )

                checkbox = QCheckBox()

                checkbox.setObjectName(
                    "orderCheckbox"
                )

                checkbox.setCursor(
                    Qt.CursorShape.PointingHandCursor
                )

                checkbox.stateChanged.connect(
                    self._update_buttons
                )

                container = QFrame()

                checkbox_layout = QHBoxLayout(
                    container
                )

                checkbox_layout.setContentsMargins(
                    0,
                    0,
                    0,
                    0,
                )

                checkbox_layout.setAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                checkbox_layout.addWidget(
                    checkbox
                )

                self.table.setCellWidget(
                    row_index,
                    0,
                    container,
                )

                self._set_table_item(
                    row_index,
                    1,
                    order.get(
                        "oid",
                        "",
                    ),
                )

                self._set_table_item(
                    row_index,
                    2,
                    order.get(
                        "status",
                        "",
                    ),
                )

                self._set_table_item(
                    row_index,
                    3,
                    order.get(
                        "note_no",
                        "",
                    ),
                )

                self._set_table_item(
                    row_index,
                    4,
                    self._format_date(
                        order.get(
                            "init_date"
                        )
                    ),
                )

        finally:
            self.table.blockSignals(
                False
            )

        self._update_buttons()

    # ==========================================================
    # TABLE ITEM
    # ==========================================================

    def _set_table_item(
        self,
        row: int,
        column: int,
        value,
    ):
        item = QTableWidgetItem(
            str(value)
        )

        item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.table.setItem(
            row,
            column,
            item,
        )

    # ==========================================================
    # DATE
    # ==========================================================

    @staticmethod
    def _format_date(
        value,
    ) -> str:
        if value is None:
            return ""

        if hasattr(
            value,
            "strftime",
        ):
            return value.strftime(
                "%d/%m/%Y"
            )

        text = str(
            value
        )

        if len(text) >= 10:
            return (
                text[8:10]
                + "/"
                + text[5:7]
                + "/"
                + text[0:4]
            )

        return text

    # ==========================================================
    # CHECKED ROWS
    # ==========================================================

    def get_checked_rows(self):
        rows = []

        for row in range(
            self.table.rowCount()
        ):
            container = (
                self.table.cellWidget(
                    row,
                    0,
                )
            )

            if not container:
                continue

            checkbox = container.findChild(
                QCheckBox
            )

            if (
                checkbox
                and checkbox.isChecked()
            ):
                rows.append(
                    row
                )

        return rows

    # ==========================================================
    # TABLE SELECTION
    # ==========================================================

    def _sync_selection_with_checkboxes(self):
        selected_rows = {
            index.row()
            for index in (
                self.table
                .selectionModel()
                .selectedRows()
            )
        }

        self.table.blockSignals(
            True
        )

        try:
            for row in range(
                self.table.rowCount()
            ):
                container = (
                    self.table.cellWidget(
                        row,
                        0,
                    )
                )

                if not container:
                    continue

                checkbox = container.findChild(
                    QCheckBox
                )

                if checkbox:
                    checkbox.setChecked(
                        row in selected_rows
                    )

        finally:
            self.table.blockSignals(
                False
            )

        self._update_buttons()

    # ==========================================================
    # SELECT ALL
    # ==========================================================

    def select_all(self):
        has_rows = (
            self.table.rowCount()
            > 0
        )

        if not has_rows:
            return

        checked_rows = self.get_checked_rows()

        select = (
            len(checked_rows)
            != self.table.rowCount()
        )

        self.table.blockSignals(
            True
        )

        try:
            for row in range(
                self.table.rowCount()
            ):
                container = (
                    self.table.cellWidget(
                        row,
                        0,
                    )
                )

                if not container:
                    continue

                checkbox = container.findChild(
                    QCheckBox
                )

                if checkbox:
                    checkbox.setChecked(
                        select
                    )

        finally:
            self.table.blockSignals(
                False
            )

        self._update_buttons()

    # ==========================================================
    # BUTTON STATE
    # ==========================================================

    def _update_buttons(
        self,
        *_args,
    ):
        has_rows = (
            self.table.rowCount()
            > 0
        )

        checked_rows = self.get_checked_rows()

        self.select_all_button.setEnabled(
            has_rows
        )

        self.change_button.setEnabled(
            bool(checked_rows)
        )

        if (
            has_rows
            and len(checked_rows)
            == self.table.rowCount()
        ):
            self.select_all_button.setText(
                "Clear Selection"
            )
        else:
            self.select_all_button.setText(
                "Select All"
            )

    # ==========================================================
    # CHANGE STATUS
    # ==========================================================

    def change_selected(self):
        rows = self.get_checked_rows()

        if not rows:
            self._show_error(
                "No pending record has been selected."
            )
            return

        oids = []

        for row in rows:
            item = self.table.item(
                row,
                1,
            )

            if not item:
                continue

            try:
                oids.append(
                    int(
                        item.text()
                    )
                )
            except ValueError:
                continue

        if not oids:
            self._show_error(
                "No valid SalesTransOID was found."
            )
            return

        answer = QMessageBox.question(
            self,
            "Delete Pending Order",
            (
                "The selected pending order(s) "
                "will be closed.\n\n"
                f"Selected records: {len(oids)}\n\n"
                "Do you want to continue?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if (
            answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        self.change_button.setEnabled(
            False
        )

        self.search_button.setEnabled(
            False
        )

        self.status_label.setText(
            "Updating..."
        )

        try:
            result = (
                self.service.update_statuses(
                    oids
                )
            )

            updated = result.get(
                "updated",
                0,
            )

            self.status_label.setText(
                f"Completed. {updated} record(s) updated."
            )

            self.result_status.setText(
                "Update completed."
            )

            self.search_orders()

            if updated:
                QMessageBox.information(
                    self,
                    "Delete Pending Order",
                    (
                        f"{updated} pending record(s) "
                        "were successfully closed."
                    ),
                )

        except Exception as exc:
            self.status_label.setText(
                "Update failed."
            )

            QMessageBox.critical(
                self,
                "Delete Pending Order",
                str(exc),
            )

        finally:
            self.search_button.setEnabled(
                True
            )

            self._update_buttons()

    # ==========================================================
    # ERROR
    # ==========================================================

    def _show_error(
        self,
        message: str,
    ):
        QMessageBox.warning(
            self,
            "Delete Pending Order",
            message,
        )