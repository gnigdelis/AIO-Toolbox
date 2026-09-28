from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDateEdit,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.change_date.change_date_service import ChangeDateService
from core.database.database_context import database_context


class ChangeDatePage(QWidget):
    """AIO Toolbox Change Date page."""

    def __init__(self) -> None:
        super().__init__()

        self.service = ChangeDateService()
        self._loading_dates = False
        self._loaded = False

        self._build_ui()
        self._connect_signals()
        self._clear_transactions()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(16)

        title = QLabel("Change Date")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Transfer selected transactions to the correct restaurant date."
        )
        subtitle.setObjectName("pageSubtitle")

        root.addWidget(title)
        root.addWidget(subtitle)

        date_card = QGroupBox("Restaurant Date")
        date_card.setObjectName("contentCard")
        date_layout = QHBoxLayout(date_card)
        date_layout.setContentsMargins(18, 18, 18, 18)
        date_layout.setSpacing(12)

        current_label = QLabel("Restaurant Date")
        current_label.setObjectName("fieldLabel")

        self.current_date = QDateEdit()
        self.current_date.setObjectName("dateEdit")
        self.current_date.setCalendarPopup(True)
        self.current_date.setDisplayFormat("dd/MM/yyyy")
        self.current_date.setMinimumWidth(125)

        arrow = QLabel("→")
        arrow.setObjectName("dateArrow")

        new_label = QLabel("New Restaurant Date")
        new_label.setObjectName("fieldLabel")

        self.new_date = QDateEdit()
        self.new_date.setObjectName("dateEdit")
        self.new_date.setCalendarPopup(True)
        self.new_date.setDisplayFormat("dd/MM/yyyy")
        self.new_date.setMinimumWidth(125)

        self.search_button = QPushButton("Search Transactions")
        self.search_button.setObjectName("primaryButton")
        self.search_button.setMinimumHeight(38)

        date_layout.addWidget(current_label)
        date_layout.addWidget(self.current_date)
        date_layout.addWidget(arrow)
        date_layout.addWidget(new_label)
        date_layout.addWidget(self.new_date)
        date_layout.addStretch()
        date_layout.addWidget(self.search_button)

        root.addWidget(date_card)

        summary_frame = QFrame()
        summary_frame.setObjectName("summaryFrame")
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(14, 10, 14, 10)

        self.transfer_summary = QLabel(
            "Select transactions and transfer them to the new date."
        )
        self.transfer_summary.setObjectName("summaryText")
        summary_layout.addWidget(self.transfer_summary)

        root.addWidget(summary_frame)

        transactions_card = QGroupBox("Transactions Found")
        transactions_card.setObjectName("contentCard")
        transactions_layout = QVBoxLayout(transactions_card)
        transactions_layout.setContentsMargins(14, 18, 14, 14)
        transactions_layout.setSpacing(10)

        self.transactions_table = QTableWidget()
        self.transactions_table.setObjectName("dataTable")
        self.transactions_table.setColumnCount(7)
        self.transactions_table.setHorizontalHeaderLabels(
            [
                "",
                "Real Date",
                "Time",
                "Note No",
                "Note Code",
                "Amount",
                "SalesTransOID",
            ]
        )
        self.transactions_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.transactions_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.transactions_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.transactions_table.verticalHeader().setVisible(False)
        self.transactions_table.setAlternatingRowColors(True)

        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        self.transactions_table.setColumnWidth(0, 42)

        transactions_layout.addWidget(self.transactions_table, 1)

        selection_row = QHBoxLayout()

        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.setObjectName("selectAllCheck")
        selection_row.addWidget(self.select_all_checkbox)
        selection_row.addStretch()

        transactions_layout.addLayout(selection_row)

        footer = QHBoxLayout()
        footer.setSpacing(8)

        self.selected_label = QLabel("Selected: 0 transactions")
        self.selected_label.setObjectName("mutedLabel")

        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("secondaryButton")

        self.transfer_all_button = QPushButton("Transfer All")
        self.transfer_all_button.setObjectName("warningButton")

        self.transfer_button = QPushButton("Transfer Selected")
        self.transfer_button.setObjectName("primaryButton")

        footer.addWidget(self.selected_label)
        footer.addStretch()
        footer.addWidget(self.clear_button)
        footer.addWidget(self.transfer_all_button)
        footer.addWidget(self.transfer_button)

        transactions_layout.addLayout(footer)
        root.addWidget(transactions_card, 1)

        self.setStyleSheet(
            """
            QLabel#pageTitle {
                color: #1F2D3D;
                font-size: 25px;
                font-weight: 700;
            }

            QLabel#pageSubtitle {
                color: #66758A;
                font-size: 11px;
            }

            QGroupBox#contentCard {
                background: #FFFFFF;
                border: 1px solid #DCE3EC;
                border-radius: 10px;
                margin-top: 8px;
                padding-top: 10px;
                color: #334155;
                font-size: 12px;
                font-weight: 600;
            }

            QGroupBox#contentCard::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                color: #526176;
            }

            QLabel#fieldLabel {
                color: #526176;
                font-size: 11px;
                font-weight: 600;
            }

            QLabel#dateArrow {
                color: #7C8BA1;
                font-size: 18px;
                font-weight: 600;
                padding: 0 4px;
            }

            QDateEdit#dateEdit {
                min-height: 36px;
                padding: 4px 9px;
                background: #F8FAFC;
                color: #26344D;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
            }

            QDateEdit#dateEdit:focus {
                border: 1px solid #4C8BF5;
                background: #FFFFFF;
            }

            QPushButton {
                min-height: 36px;
                padding: 0 14px;
                border-radius: 6px;
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

            QPushButton#secondaryButton {
                background: #FFFFFF;
                color: #40506A;
                border: 1px solid #C8D2E0;
            }

            QPushButton#secondaryButton:hover {
                background: #F5F8FC;
            }

            QPushButton#warningButton {
                background: #FFF4E5;
                color: #A65B00;
                border: 1px solid #F1C27D;
            }

            QPushButton#warningButton:hover {
                background: #FFEBD0;
            }

            QPushButton:disabled {
                color: #A8B2C0;
                background: #F1F4F8;
                border-color: #E1E6ED;
            }

            QFrame#summaryFrame {
                background: #F5F8FC;
                border: 1px solid #DCE3EC;
                border-radius: 7px;
            }

            QLabel#summaryText {
                color: #526176;
                font-size: 10px;
                font-weight: 600;
            }

            QLabel#mutedLabel {
                color: #718096;
                font-size: 10px;
            }

            QCheckBox#selectAllCheck {
                color: #40506A;
                font-size: 10px;
                font-weight: 600;
            }

            QTableWidget#dataTable {
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
            """
        )

    def _connect_signals(self) -> None:
        self.search_button.clicked.connect(self.find_transactions)
        self.clear_button.clicked.connect(self._clear_transactions)
        self.transfer_all_button.clicked.connect(self.transfer_all)
        self.transfer_button.clicked.connect(self.transfer_selected)
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        database_context.database_changed.connect(self._on_database_changed)
        self.transactions_table.itemChanged.connect(
            self.update_selection_count
        )

    def showEvent(self, event) -> None:
        super().showEvent(event)

        if not self._loaded:
            self._loaded = True
            self.load_current_restaurant_date()

    def _on_database_changed(self, database: dict | None) -> None:
        if database:
            self._loaded = True
            self.load_current_restaurant_date()
            return

        self._loaded = False
        self._clear_dates_and_transactions()

    def load_current_restaurant_date(self) -> None:
        if not self._database_is_selected():
            self._clear_dates_and_transactions()
            return

        try:
            current_date = self.service.get_current_restaurant_date()

            self._loading_dates = True
            qdate = self.current_date.date().fromString(
                current_date.strftime("%Y-%m-%d"),
                "yyyy-MM-dd",
            )
            self.current_date.setDate(qdate)
            self.new_date.setDate(qdate.addDays(1))
            self._loading_dates = False

            self._clear_transactions()

        except Exception as error:
            self._loading_dates = False
            self._clear_dates_and_transactions()
            QMessageBox.critical(
                self,
                "Change Date",
                "Unable to read the current restaurant date.\n\n"
                f"{error}",
            )

    def _database_is_selected(self) -> bool:
        from core.database.database_context import database_context

        return database_context.is_selected()

    def _clear_dates_and_transactions(self) -> None:
        self._loading_dates = True
        self.current_date.clear()
        self.new_date.clear()
        self._loading_dates = False
        self._clear_transactions()

    def find_transactions(self) -> None:
        if not self._database_is_selected():
            QMessageBox.warning(
                self,
                "Change Date",
                "Please connect to a database from the DB button "
                "in the header first.",
            )
            return

        current_date = self.current_date.date().toPython()
        new_date = self.new_date.date().toPython()

        if current_date == new_date:
            QMessageBox.warning(
                self,
                "Change Date",
                "Restaurant Date and New Restaurant Date "
                "must be different.",
            )
            self._clear_transactions()
            return

        try:
            transactions = self.service.find_transactions(current_date)
            self._populate_transactions(transactions)

        except Exception as error:
            self._clear_transactions()
            QMessageBox.critical(
                self,
                "Change Date",
                "Unable to find transactions.\n\n"
                f"{error}",
            )

    def _populate_transactions(self, transactions: list[dict]) -> None:
        self.transactions_table.blockSignals(True)

        try:
            self.transactions_table.setRowCount(0)

            for transaction in transactions:
                row = self.transactions_table.rowCount()
                self.transactions_table.insertRow(row)

                checkbox = QTableWidgetItem()
                checkbox.setFlags(
                    Qt.ItemFlag.ItemIsUserCheckable
                    | Qt.ItemFlag.ItemIsEnabled
                )
                checkbox.setCheckState(Qt.CheckState.Unchecked)

                # Selected transactions are identified by the POS header,
                # because that is the complete transaction document key.
                checkbox.setData(
                    Qt.ItemDataRole.UserRole,
                    transaction.get("SalesTransPosHdr"),
                )
                self.transactions_table.setItem(row, 0, checkbox)

                real_date = transaction.get("SalesTransRealDate")
                begin_time = transaction.get("SalesTransBeginTime")

                real_date_text = (
                    real_date.strftime("%d/%m/%Y")
                    if real_date is not None
                    else ""
                )
                time_text = (
                    begin_time.strftime("%H:%M:%S")
                    if begin_time is not None
                    else ""
                )

                self.transactions_table.setItem(
                    row, 1, QTableWidgetItem(real_date_text)
                )
                self.transactions_table.setItem(
                    row, 2, QTableWidgetItem(time_text)
                )
                self.transactions_table.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        str(transaction.get("SalesTransNoteNo") or "")
                    ),
                )
                self.transactions_table.setItem(
                    row,
                    4,
                    QTableWidgetItem(
                        str(transaction.get("SalesTransNoteCode") or "")
                    ),
                )

                amount = (
                    (transaction.get("SalesTransCashGrs") or 0)
                    + (transaction.get("SalesTransCredGrs") or 0)
                    + (transaction.get("SalesTransFoffGrs") or 0)
                )

                amount_item = QTableWidgetItem(f"{amount:.2f}")
                amount_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight
                    | Qt.AlignmentFlag.AlignVCenter
                )
                self.transactions_table.setItem(row, 5, amount_item)

                oid_item = QTableWidgetItem(
                    str(transaction.get("SalesTransOID") or "")
                )
                oid_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight
                    | Qt.AlignmentFlag.AlignVCenter
                )
                self.transactions_table.setItem(row, 6, oid_item)

        finally:
            self.transactions_table.blockSignals(False)

        self.selected_label.setText(
            f"Found: {len(transactions)} transactions"
        )
        self.update_selection_count(None)

    def _clear_transactions(self) -> None:
        self.transactions_table.blockSignals(True)

        try:
            self.transactions_table.setRowCount(0)
        finally:
            self.transactions_table.blockSignals(False)

        self.selected_label.setText("Selected: 0 transactions")
        self.transfer_button.setEnabled(False)
        self.transfer_all_button.setEnabled(False)

        self.select_all_checkbox.blockSignals(True)
        self.select_all_checkbox.setCheckState(
            Qt.CheckState.Unchecked
        )
        self.select_all_checkbox.blockSignals(False)

        self._update_transfer_summary(0)

    def toggle_select_all(self, state: int) -> None:
        if not self.transactions_table.rowCount():
            self.select_all_checkbox.blockSignals(True)
            self.select_all_checkbox.setCheckState(
                Qt.CheckState.Unchecked
            )
            self.select_all_checkbox.blockSignals(False)
            return

        checked = state == Qt.CheckState.Checked.value

        self.transactions_table.blockSignals(True)

        try:
            for row in range(self.transactions_table.rowCount()):
                item = self.transactions_table.item(row, 0)
                if item is not None:
                    item.setCheckState(
                        Qt.CheckState.Checked
                        if checked
                        else Qt.CheckState.Unchecked
                    )
        finally:
            self.transactions_table.blockSignals(False)

        self.update_selection_count(None)

    def update_selection_count(self, item) -> None:
        if item is not None and item.column() != 0:
            return

        total = self.transactions_table.rowCount()
        selected = 0

        for row in range(total):
            checkbox = self.transactions_table.item(row, 0)

            if (
                checkbox is not None
                and checkbox.checkState() == Qt.CheckState.Checked
            ):
                selected += 1

        self.selected_label.setText(
            f"Selected: {selected} transactions"
        )
        self.transfer_button.setEnabled(selected > 0)
        self.transfer_all_button.setEnabled(total > 0)

        self.select_all_checkbox.blockSignals(True)

        try:
            if total == 0 or selected == 0:
                state = Qt.CheckState.Unchecked
            elif selected == total:
                state = Qt.CheckState.Checked
            else:
                state = Qt.CheckState.PartiallyChecked

            self.select_all_checkbox.setCheckState(state)
        finally:
            self.select_all_checkbox.blockSignals(False)

        self._update_transfer_summary(selected)

    def _update_transfer_summary(self, selected_count: int) -> None:
        if self.current_date.date().isValid():
            current_text = self.current_date.date().toString("dd/MM/yyyy")
        else:
            current_text = "-"

        if self.new_date.date().isValid():
            new_text = self.new_date.date().toString("dd/MM/yyyy")
        else:
            new_text = "-"

        if selected_count > 0:
            text = (
                f"Selected: {selected_count} transaction(s)  "
                f"from {current_text} → {new_text}"
            )
        else:
            text = (
                f"Select transactions from {current_text} → {new_text}"
            )

        self.transfer_summary.setText(text)
        self.transfer_button.setText(
            f"Transfer Selected to {new_text}"
        )
        self.transfer_all_button.setText(
            f"Transfer All to {new_text}"
        )

    def _selected_transaction_ids(self) -> list[int]:
        values = []

        for row in range(self.transactions_table.rowCount()):
            checkbox = self.transactions_table.item(row, 0)

            if (
                checkbox is not None
                and checkbox.checkState() == Qt.CheckState.Checked
            ):
                value = checkbox.data(Qt.ItemDataRole.UserRole)

                if value is not None:
                    values.append(int(value))

        return values

    def transfer_all(self) -> None:
        total = self.transactions_table.rowCount()

        if total <= 0:
            return

        current_date = self.current_date.date().toPython()
        new_date = self.new_date.date().toPython()

        if current_date == new_date:
            QMessageBox.warning(
                self,
                "Change Date",
                "Restaurant Date and New Restaurant Date "
                "must be different.",
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Transfer",
            (
                f"Transfer all records from "
                f"{current_date:%d/%m/%Y} to "
                f"{new_date:%d/%m/%Y}?\n\n"
                "This will transfer SALES, PAYMENTS and MOVEMENTS "
                "for the selected restaurant date."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            result = self.service.transfer_all(
                current_date,
                new_date,
            )

            if result.get("success"):
                QMessageBox.information(
                    self,
                    "Change Date",
                    (
                        result.get(
                            "message",
                            "Transfer completed successfully.",
                        )
                        + "\n\n"
                        + "Sales rows updated: "
                        + str(result.get("sales_rows", 0))
                        + "\n"
                        + "Payment rows updated: "
                        + str(result.get("payment_rows", 0))
                        + "\n"
                        + "Movement rows updated: "
                        + str(result.get("movement_rows", 0))
                    ),
                )
                self.find_transactions()
            else:
                QMessageBox.critical(
                    self,
                    "Change Date",
                    result.get(
                        "message",
                        "Transfer All failed.",
                    ),
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Change Date",
                f"Transfer All failed.\n\n{error}",
            )

    def transfer_selected(self) -> None:
        transaction_ids = self._selected_transaction_ids()

        if not transaction_ids:
            QMessageBox.information(
                self,
                "Change Date",
                "No transactions have been selected.",
            )
            return

        current_date = self.current_date.date().toPython()
        new_date = self.new_date.date().toPython()

        if current_date == new_date:
            QMessageBox.warning(
                self,
                "Change Date",
                "Restaurant Date and New Restaurant Date "
                "must be different.",
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Transfer",
            (
                f"Transfer {len(transaction_ids)} selected "
                f"transaction(s) from "
                f"{current_date:%d/%m/%Y} to "
                f"{new_date:%d/%m/%Y}?\n\n"
                "The selected SALES and PAYMENTS will be updated."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            result = self.service.transfer_selected(
                transaction_ids,
                new_date,
            )

            if result.get("success"):
                QMessageBox.information(
                    self,
                    "Change Date",
                    (
                        result.get(
                            "message",
                            "Transfer completed successfully.",
                        )
                        + "\n\n"
                        + "Sales rows updated: "
                        + str(result.get("sales_rows", 0))
                        + "\n"
                        + "Payment rows updated: "
                        + str(result.get("payment_rows", 0))
                    ),
                )
                self.find_transactions()
            else:
                QMessageBox.critical(
                    self,
                    "Change Date",
                    result.get(
                        "message",
                        "Transfer Selected failed.",
                    ),
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Change Date",
                f"Transfer Selected failed.\n\n{error}",
            )