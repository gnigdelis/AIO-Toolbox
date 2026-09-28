from __future__ import annotations

import calendar
from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDateEdit,
    QFrame,
    QGroupBox,
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
from core.move_sales_to_hist.move_sales_to_hist_service import (
    MoveSalesToHistService,
)

from ui.v2.widgets.page_layout import (
    PAGE_LAYOUT_STYLE,
    setup_page_layout,
)


class MoveSalesToHistPage(QFrame):
    """
    Move active sales transactions to the sales history.

    The actual transfer is performed by:

        dbo.SnProPOS_SalesTrHist

    The page first reads the active sales range so the user can
    decide how far back the history transfer should go.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.service = MoveSalesToHistService()

        self.oldest_date: date | None = None
        self.latest_date: date | None = None
        self.active_count: int = 0

        self._build_ui()

        database_context.database_changed.connect(
            self._on_database_changed
        )

        self._on_database_changed(
            database_context.active()
        )

    # ==============================================================
    # UI
    # ==============================================================

    def _build_ui(self):
        root, title, subtitle = setup_page_layout(
            self,
            "Move Sales To Hist",
            "Μεταφορά πωλήσεων από την ενεργή βάση δεδομένων στους πίνακες ιστορικού.",
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(16)

        database_card = self._make_card("Active Database")
        database_layout = database_card.layout()

        database_row = QHBoxLayout()
        database_label = QLabel("Database")
        database_label.setObjectName("fieldLabel")
        self.database_value = QLabel("-")
        self.database_value.setObjectName("valueLabel")
        database_row.addWidget(database_label)
        database_row.addStretch()
        database_row.addWidget(self.database_value)
        database_layout.addLayout(database_row)

        server_row = QHBoxLayout()
        server_label = QLabel("Server")
        server_label.setObjectName("fieldLabel")
        self.server_value = QLabel("-")
        self.server_value.setObjectName("valueLabel")
        server_row.addWidget(server_label)
        server_row.addStretch()
        server_row.addWidget(self.server_value)
        database_layout.addLayout(server_row)
        layout.addWidget(database_card)

        sales_card = self._make_card("Active Sales")
        sales_layout = sales_card.layout()

        count_row = QHBoxLayout()
        count_label = QLabel("Active Sales Records")
        count_label.setObjectName("fieldLabel")
        self.count_value = QLabel("-")
        self.count_value.setObjectName("valueLabel")
        count_row.addWidget(count_label)
        count_row.addStretch()
        count_row.addWidget(self.count_value)
        sales_layout.addLayout(count_row)

        oldest_row = QHBoxLayout()
        oldest_label = QLabel("Oldest Active Sale")
        oldest_label.setObjectName("fieldLabel")
        self.oldest_value = QLabel("-")
        self.oldest_value.setObjectName("valueLabel")
        oldest_row.addWidget(oldest_label)
        oldest_row.addStretch()
        oldest_row.addWidget(self.oldest_value)
        sales_layout.addLayout(oldest_row)

        latest_row = QHBoxLayout()
        latest_label = QLabel("Latest Active Sale")
        latest_label.setObjectName("fieldLabel")
        self.latest_value = QLabel("-")
        self.latest_value.setObjectName("valueLabel")
        latest_row.addWidget(latest_label)
        latest_row.addStretch()
        latest_row.addWidget(self.latest_value)
        sales_layout.addLayout(latest_row)
        layout.addWidget(sales_card)

        range_card = self._make_card("Move Range")
        range_layout = range_card.layout()

        description = QLabel(
            "Επίλεξε μέχρι ποια ημερομηνία θέλεις να μεταφερθούν "
            "οι παλιές ενεργές πωλήσεις στο ιστορικό."
        )
        description.setObjectName("cardDescription")
        description.setWordWrap(True)
        range_layout.addWidget(description)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(8)

        self.one_month_button = QPushButton("1 Month")
        self.three_months_button = QPushButton("3 Months")
        self.custom_date_button = QPushButton("Custom Date")

        for button in (
            self.one_month_button,
            self.three_months_button,
            self.custom_date_button,
        ):
            button.setObjectName("secondaryButton")
            button.setMinimumHeight(36)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.one_month_button.clicked.connect(self._select_one_month)
        self.three_months_button.clicked.connect(self._select_three_months)
        self.custom_date_button.clicked.connect(self._select_custom_date)

        buttons_row.addWidget(self.one_month_button)
        buttons_row.addWidget(self.three_months_button)
        buttons_row.addWidget(self.custom_date_button)
        range_layout.addLayout(buttons_row)

        dates_row = QHBoxLayout()
        dates_row.setSpacing(12)

        from_container = QVBoxLayout()
        from_label = QLabel("From")
        from_label.setObjectName("fieldLabel")
        self.from_value = QLabel("-")
        self.from_value.setObjectName("valueLabel")
        from_container.addWidget(from_label)
        from_container.addWidget(self.from_value)
        dates_row.addLayout(from_container, 1)

        arrow = QLabel("→")
        arrow.setObjectName("dateArrow")
        arrow.setAlignment(Qt.AlignCenter)
        dates_row.addWidget(arrow)

        until_container = QVBoxLayout()
        until_label = QLabel("Move Until")
        until_label.setObjectName("fieldLabel")

        self.move_date = QDateEdit()
        self.move_date.setObjectName("dateEdit")
        self.move_date.setCalendarPopup(True)
        self.move_date.setDisplayFormat("dd/MM/yyyy")
        self.move_date.setMinimumDate(QDate(2000, 1, 1))
        self.move_date.setSpecialValueText("—")
        self.move_date.setMinimumHeight(36)
        self.move_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.move_date.dateChanged.connect(self._custom_date_changed)

        until_container.addWidget(until_label)
        until_container.addWidget(self.move_date)
        dates_row.addLayout(until_container, 1)

        range_layout.addLayout(dates_row)
        layout.addWidget(range_card)

        warning = QLabel(
            "Προσοχή: Η λειτουργία μεταφέρει τις επιλέξιμες "
            "πωλήσεις από τους ενεργούς πίνακες στους πίνακες "
            "ιστορικού. Η μεταφορά εκτελείται από stored procedure "
            "της SQL Server."
        )
        warning.setObjectName("warningLabel")
        warning.setWordWrap(True)
        layout.addWidget(warning)

        log_card = self._make_card("Operation Log")
        log_layout = log_card.layout()

        self.log_label = QLabel("Ready.")
        self.log_label.setObjectName("logLabel")
        self.log_label.setWordWrap(True)
        self.log_label.setMinimumHeight(70)
        self.log_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        log_layout.addWidget(self.log_label)
        layout.addWidget(log_card)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)

        self.move_button = QPushButton("MOVE SALES TO HIST")
        self.move_button.setObjectName("primaryButton")
        self.clear_button = QPushButton("Clear Log")
        self.clear_button.setObjectName("secondaryButton")

        self.move_button.setMinimumHeight(36)
        self.clear_button.setMinimumHeight(36)
        self.move_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.clear_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.move_button.clicked.connect(self._move_sales)
        self.clear_button.clicked.connect(self._clear_log)

        actions_row.addWidget(self.move_button)
        actions_row.addWidget(self.clear_button)
        layout.addLayout(actions_row)
        layout.addStretch()

        scroll_area.setWidget(content)
        root.addWidget(scroll_area, 1)

        self.setStyleSheet(
            PAGE_LAYOUT_STYLE
            + """
            QLabel#fieldLabel {
                color: #526176;
                font-size: 11px;
                font-weight: 600;
            }

            QLabel#valueLabel {
                color: #26344D;
                font-size: 11px;
                font-weight: 600;
            }

            QLabel#cardDescription {
                color: #66758A;
                font-size: 10px;
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

            QLabel#warningLabel {
                background: #FFF6D9;
                color: #7A5A00;
                border: 1px solid #E7C96A;
                border-radius: 8px;
                padding: 12px;
                font-size: 10px;
            }

            QLabel#logLabel {
                background: #111827;
                color: #E5E7EB;
                border: 1px solid #DCE3EC;
                border-radius: 7px;
                padding: 10px;
                font-family: Consolas;
                font-size: 10px;
            }
            """
        )

        self._set_controls_enabled(False)

    # ==============================================================
    # CARD
    # ==============================================================

    def _make_card(
        self,
        title: str,
    ) -> QGroupBox:
        card = QGroupBox(title)
        card.setObjectName("contentCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(10)

        return card

    # ==============================================================
    # DATABASE
    # ==============================================================

    def _on_database_changed(
        self,
        database,
    ):

        self.oldest_date = None
        self.latest_date = None
        self.active_count = 0

        self.from_value.setText(
            "-"
        )

        self.move_date.blockSignals(
            True
        )

        self.move_date.setDate(
            self.move_date.minimumDate()
        )

        self.move_date.blockSignals(
            False
        )

        if not database:

            self.database_value.setText(
                "-"
            )

            self.server_value.setText(
                "-"
            )

            self.count_value.setText(
                "-"
            )

            self.oldest_value.setText(
                "-"
            )

            self.latest_value.setText(
                "-"
            )

            self.log_label.setText(
                "Δεν έχει επιλεγεί βάση δεδομένων."
            )

            self._set_controls_enabled(
                False
            )

            return

        self.database_value.setText(
            database.get(
                "name",
                "-",
            )
        )

        self.server_value.setText(
            database.get(
                "server",
                "-",
            )
        )

        self.log_label.setText(
            "Ανάκτηση ενεργών πωλήσεων..."
        )

        self._load_active_sales()

    # ==============================================================
    # LOAD ACTIVE SALES
    # ==============================================================

    def _load_active_sales(self):

        try:

            summary = (
                self.service
                .get_active_sales_summary()
            )

            self.active_count = summary[
                "count"
            ]

            self.oldest_date = summary[
                "oldest_date"
            ]

            self.latest_date = summary[
                "latest_date"
            ]

            self.count_value.setText(
                f"{self.active_count:,}"
            )

            if self.oldest_date:

                self.oldest_value.setText(
                    self._format_date(
                        self.oldest_date
                    )
                )

            else:

                self.oldest_value.setText(
                    "None"
                )

            if self.latest_date:

                self.latest_value.setText(
                    self._format_date(
                        self.latest_date
                    )
                )

            else:

                self.latest_value.setText(
                    "None"
                )

            if not self.oldest_date:

                self.from_value.setText(
                    "-"
                )

                self.move_date.blockSignals(
                    True
                )

                self.move_date.setDate(
                    self.move_date.minimumDate()
                )

                self.move_date.blockSignals(
                    False
                )

                self.log_label.setText(
                    "Δεν βρέθηκαν ενεργές πωλήσεις "
                    "στο TblSnSalesTrans."
                )

                self._set_controls_enabled(
                    False
                )

                return

            self.from_value.setText(
                self._format_date(
                    self.oldest_date
                )
            )

            self._set_default_move_date()

            self.log_label.setText(
                "Έτοιμο. Επίλεξε 1 Month, 3 Months "
                "ή Custom Date."
            )

            self._set_controls_enabled(
                True
            )

        except Exception as exc:

            self.log_label.setText(
                "Σφάλμα κατά την ανάκτηση ενεργών "
                "πωλήσεων:\n"
                f"{exc}"
            )

            self._set_controls_enabled(
                False
            )

    # ==============================================================
    # DATE HELPERS
    # ==============================================================

    @staticmethod
    def _format_date(
        value: date,
    ) -> str:

        return value.strftime(
            "%d/%m/%Y"
        )

    @staticmethod
    def _add_months(
        source: date,
        months: int,
    ) -> date:

        month = (
            source.month
            - 1
            + months
        )

        year = (
            source.year
            + month // 12
        )

        month = (
            month % 12
            + 1
        )

        day = min(
            source.day,
            calendar.monthrange(
                year,
                month,
            )[1],
        )

        return date(
            year,
            month,
            day,
        )

    def _set_default_move_date(
        self,
    ):

        if not self.oldest_date:
            return

        proposed = self._add_months(
            self.oldest_date,
            1,
        )

        if (
            self.latest_date
            and proposed > self.latest_date
        ):
            proposed = self.latest_date

        self._set_move_date(
            proposed
        )

    def _set_move_date(
        self,
        value: date,
    ):

        if not self.oldest_date:
            return

        if value < self.oldest_date:
            value = self.oldest_date

        if (
            self.latest_date
            and value > self.latest_date
        ):
            value = self.latest_date

        self.move_date.blockSignals(
            True
        )

        self.move_date.setDate(
            QDate(
                value.year,
                value.month,
                value.day,
            )
        )

        self.move_date.blockSignals(
            False
        )

        self._update_range_display()

    # ==============================================================
    # QUICK SELECTION
    # ==============================================================

    def _select_one_month(self):

        if not self.oldest_date:
            return

        target = self._add_months(
            self.oldest_date,
            1,
        )

        self._set_move_date(
            target
        )

        self.log_label.setText(
            "Επιλέχθηκε μεταφορά 1 μήνα "
            "από την παλαιότερη ενεργή πώληση."
        )

    def _select_three_months(self):

        if not self.oldest_date:
            return

        target = self._add_months(
            self.oldest_date,
            3,
        )

        self._set_move_date(
            target
        )

        self.log_label.setText(
            "Επιλέχθηκε μεταφορά 3 μηνών "
            "από την παλαιότερη ενεργή πώληση."
        )

    def _select_custom_date(self):

        if not self.oldest_date:
            return

        self.move_date.setFocus()

        self.move_date.calendarWidget().show()

        self.log_label.setText(
            "Επίλεξε την ημερομηνία μέχρι την οποία "
            "θέλεις να μεταφερθούν οι πωλήσεις."
        )

    def _custom_date_changed(
        self,
        qdate: QDate,
    ):

        if not self.oldest_date:
            return

        selected = date(
            qdate.year(),
            qdate.month(),
            qdate.day(),
        )

        if selected < self.oldest_date:

            self._set_move_date(
                self.oldest_date
            )

            return

        if (
            self.latest_date
            and selected > self.latest_date
        ):

            self._set_move_date(
                self.latest_date
            )

            return

        self._update_range_display()

    # ==============================================================
    # RANGE DISPLAY
    # ==============================================================

    def _get_selected_date(
        self,
    ) -> date:

        qdate = self.move_date.date()

        return date(
            qdate.year(),
            qdate.month(),
            qdate.day(),
        )

    def _update_range_display(
        self,
    ):

        if not self.oldest_date:

            self.from_value.setText(
                "-"
            )

            return

        selected = self._get_selected_date()

        self.from_value.setText(
            self._format_date(
                self.oldest_date
            )
        )

        if selected < self.oldest_date:

            self.move_button.setEnabled(
                False
            )

            return

        if (
            self.latest_date
            and selected > self.latest_date
        ):

            self.move_button.setEnabled(
                False
            )

            return

        self.move_button.setEnabled(
            True
        )

    # ==============================================================
    # MOVE
    # ==============================================================

    def _move_sales(self):

        if not self.oldest_date:

            QMessageBox.warning(
                self,
                "Move Sales To Hist",
                "Δεν βρέθηκαν ενεργές πωλήσεις.",
            )

            return

        move_until = (
            self._get_selected_date()
        )

        if move_until < self.oldest_date:

            QMessageBox.warning(
                self,
                "Invalid Date",
                "Η ημερομηνία μεταφοράς δεν μπορεί "
                "να είναι πριν από την παλαιότερη "
                "ενεργή πώληση.",
            )

            return

        if (
            self.latest_date
            and move_until > self.latest_date
        ):

            QMessageBox.warning(
                self,
                "Invalid Date",
                "Η ημερομηνία μεταφοράς δεν μπορεί "
                "να είναι μετά την τελευταία "
                "ενεργή πώληση.",
            )

            return

        from_text = self._format_date(
            self.oldest_date
        )

        until_text = self._format_date(
            move_until
        )

        answer = QMessageBox.question(
            self,
            "Confirm Move Sales To Hist",
            (
                "Θέλεις να μεταφέρεις τις ενεργές "
                "πωλήσεις στο ιστορικό;\n\n"
                f"From: {from_text}\n"
                f"Until: {until_text}\n\n"
                "Η διαδικασία μεταφέρει τις επιλέξιμες "
                "εγγραφές από τους active tables "
                "στους history tables."
            ),
            QMessageBox.Yes
            | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        self._set_controls_enabled(
            False
        )

        self.log_label.setText(
            (
                "Εκτέλεση Move Sales To Hist...\n"
                f"From: {from_text}\n"
                f"Until: {until_text}"
            )
        )

        try:

            result = self.service.move_until(
                move_until,
                progress_callback=self._append_log,
            )

            self._append_log("")

            self._append_log(
                "Η μεταφορά ολοκληρώθηκε επιτυχώς."
            )

            if result.get("database"):

                self._append_log(
                    f"Database: {result['database']}"
                )

            if result.get("server"):

                self._append_log(
                    f"Server: {result['server']}"
                )

            QMessageBox.information(
                self,
                "Move Sales To Hist",
                "Η μεταφορά ολοκληρώθηκε επιτυχώς.",
            )

            self._load_active_sales()

        except Exception as exc:

            self._append_log("")

            self._append_log(
                f"ERROR: {exc}"
            )

            QMessageBox.critical(
                self,
                "Move Sales To Hist",
                (
                    "Η μεταφορά απέτυχε.\n\n"
                    f"{exc}"
                ),
            )

            self._set_controls_enabled(
                True
            )

    # ==============================================================
    # LOG
    # ==============================================================

    def _append_log(
        self,
        message: str,
    ):

        current = self.log_label.text()

        if not current:

            self.log_label.setText(
                message
            )

            return

        if not message:

            self.log_label.setText(
                current + "\n"
            )

            return

        self.log_label.setText(
            current
            + "\n"
            + message
        )

    def _clear_log(self):

        self.log_label.setText(
            "Ready."
        )

    # ==============================================================
    # ENABLE / DISABLE
    # ==============================================================

    def _set_controls_enabled(
        self,
        enabled: bool,
    ):

        self.one_month_button.setEnabled(
            enabled
        )

        self.three_months_button.setEnabled(
            enabled
        )

        self.custom_date_button.setEnabled(
            enabled
        )

        self.move_date.setEnabled(
            enabled
        )

        self.move_button.setEnabled(
            enabled
            and self.oldest_date is not None
        )

        self.clear_button.setEnabled(
            True
        )