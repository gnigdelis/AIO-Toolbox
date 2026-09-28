from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.database.database_context import database_context
from core.reports.reports_service import (
    HealthCheckItem,
    HealthCheckResult,
    ReportsService,
)


class ReportWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        database: dict | None,
    ) -> None:
        super().__init__()
        self.database = database

    def run(self) -> None:
        try:
            result = ReportsService().run_health_check(
                self.database
            )

            self.finished.emit(
                result
            )

        except Exception as exc:
            self.failed.emit(
                str(exc)
            )


class ReportsPage(QWidget):
    """AIO Toolbox Support Health Check."""

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._thread: QThread | None = None
        self._worker: ReportWorker | None = None

        self._build_ui()

        database_context.database_changed.connect(
            self._database_changed
        )

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setObjectName(
            "reportsPage"
        )

        self.setStyleSheet(
            """
            QWidget#reportsPage {
                background: #F5F6F8;
            }

            QFrame#headerCard,
            QFrame#healthCard,
            QFrame#issuesCard,
            QFrame#reportCard {
                background: #FFFFFF;
                border: 1px solid #E3E6EB;
                border-radius: 10px;
            }

            QLabel#pageTitle {
                color: #1F2937;
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#pageSubtitle {
                color: #6B7280;
                font-size: 13px;
            }

            QLabel#databaseStatus {
                color: #6B7280;
                font-size: 11px;
            }

            QLabel#sectionTitle {
                color: #1F2937;
                font-size: 15px;
                font-weight: 700;
            }

            QLabel#overallStatus {
                color: #1B7F3A;
                font-size: 20px;
                font-weight: 800;
            }

            QLabel#summary {
                color: #4B5563;
                font-size: 12px;
            }

            QFrame#healthItem {
                background: #F8FAFC;
                border: 1px solid #E5E7EB;
                border-radius: 7px;
            }

            QLabel#healthTitle {
                color: #374151;
                font-size: 11px;
                font-weight: 700;
            }

            QLabel#healthValue {
                color: #6B7280;
                font-size: 10px;
            }

            QLabel#healthStatus {
                font-size: 9px;
                font-weight: 800;
            }

            QLabel#issueText {
                color: #4B5563;
                font-size: 11px;
            }

            QTextEdit#output {
                background: #111827;
                color: #E5E7EB;
                border: none;
                border-radius: 7px;
                padding: 12px;
                font-family: Consolas;
                font-size: 10px;
            }

            QPushButton#primaryButton {
                background: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 9px 16px;
                font-size: 11px;
                font-weight: 700;
            }

            QPushButton#primaryButton:hover {
                background: #1D4ED8;
            }

            QPushButton#primaryButton:pressed {
                background: #1E40AF;
            }

            QPushButton#primaryButton:disabled {
                background: #B8C0CC;
                color: #EEF0F3;
            }

            QPushButton#secondaryButton {
                background: #FFFFFF;
                color: #374151;
                border: 1px solid #D6DAE1;
                border-radius: 6px;
                padding: 7px 12px;
                font-size: 11px;
                font-weight: 600;
            }

            QPushButton#secondaryButton:hover {
                background: #F3F4F6;
            }

            QPushButton#exportButton {
                background: #0F766E;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 7px 12px;
                font-size: 11px;
                font-weight: 700;
            }

            QPushButton#exportButton:hover {
                background: #115E59;
            }
            """
        )

        root = QVBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        root.setSpacing(0)

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.NoFrame
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        content = QWidget()

        content_layout = QVBoxLayout(
            content
        )

        content_layout.setContentsMargins(
            22,
            20,
            22,
            18,
        )

        content_layout.setSpacing(
            14
        )

        content_layout.addWidget(
            self._create_header()
        )

        content_layout.addWidget(
            self._create_health_card()
        )

        content_layout.addWidget(
            self._create_issues_card()
        )

        content_layout.addWidget(
            self._create_report_card()
        )

        scroll.setWidget(
            content
        )

        root.addWidget(
            scroll
        )

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _create_header(self) -> QFrame:
        card = QFrame()

        card.setObjectName(
            "headerCard"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            18,
            14,
            18,
            14,
        )

        layout.setSpacing(
            4
        )

        title = QLabel(
            "Reports"
        )

        title.setObjectName(
            "pageTitle"
        )

        subtitle = QLabel(
            "Run a complete health check of this computer."
        )

        subtitle.setObjectName(
            "pageSubtitle"
        )

        self.database_status = QLabel()

        self.database_status.setObjectName(
            "databaseStatus"
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        layout.addWidget(
            self.database_status
        )

        self._update_database_status()

        return card

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def _create_health_card(self) -> QFrame:
        card = QFrame()

        card.setObjectName(
            "healthCard"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            18,
            14,
            18,
            14,
        )

        layout.setSpacing(
            9
        )

        header = QHBoxLayout()

        header.setSpacing(
            12
        )

        title = QLabel(
            "Overall Status"
        )

        title.setObjectName(
            "sectionTitle"
        )

        self.overall_status = QLabel(
            "READY"
        )

        self.overall_status.setObjectName(
            "overallStatus"
        )

        self.summary_label = QLabel(
            "Run a full health check to analyze this computer."
        )

        self.summary_label.setObjectName(
            "summary"
        )

        self.generate_button = QPushButton(
            "RUN FULL HEALTH CHECK"
        )

        self.generate_button.setObjectName(
            "primaryButton"
        )

        self.generate_button.setCursor(
            Qt.PointingHandCursor
        )

        self.generate_button.setMinimumHeight(
            36
        )

        self.generate_button.clicked.connect(
            self._run_health_check
        )

        header.addWidget(
            title
        )

        header.addWidget(
            self.overall_status
        )

        header.addStretch()

        header.addWidget(
            self.generate_button
        )

        layout.addLayout(
            header
        )

        layout.addWidget(
            self.summary_label
        )

        self.health_grid = QGridLayout()

        self.health_grid.setContentsMargins(
            0,
            3,
            0,
            2,
        )

        self.health_grid.setHorizontalSpacing(
            8
        )

        self.health_grid.setVerticalSpacing(
            8
        )

        for column in range(3):
            self.health_grid.setColumnStretch(
                column,
                1,
            )

        layout.addLayout(
            self.health_grid
        )

        return card

    # ------------------------------------------------------------------
    # Issues
    # ------------------------------------------------------------------

    def _create_issues_card(self) -> QFrame:
        card = QFrame()

        card.setObjectName(
            "issuesCard"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            18,
            12,
            18,
            12,
        )

        layout.setSpacing(
            6
        )

        title = QLabel(
            "Issues Found"
        )

        title.setObjectName(
            "sectionTitle"
        )

        self.issues_label = QLabel(
            "No health check has been run yet."
        )

        self.issues_label.setObjectName(
            "issueText"
        )

        self.issues_label.setWordWrap(
            True
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            self.issues_label
        )

        return card

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------

    def _create_report_card(self) -> QFrame:
        card = QFrame()

        card.setObjectName(
            "reportCard"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            14,
            12,
            14,
            12,
        )

        layout.setSpacing(
            8
        )

        header = QHBoxLayout()

        title = QLabel(
            "Support Report"
        )

        title.setObjectName(
            "sectionTitle"
        )

        self.report_status = QLabel(
            "Ready"
        )

        copy_button = QPushButton(
            "Copy"
        )

        copy_button.setObjectName(
            "secondaryButton"
        )

        copy_button.clicked.connect(
            self._copy_report
        )

        export_txt = QPushButton(
            "Export TXT"
        )

        export_txt.setObjectName(
            "exportButton"
        )

        export_txt.clicked.connect(
            self._export_txt
        )

        export_pdf = QPushButton(
            "Export PDF"
        )

        export_pdf.setObjectName(
            "exportButton"
        )

        export_pdf.clicked.connect(
            self._export_pdf
        )

        clear_button = QPushButton(
            "Clear"
        )

        clear_button.setObjectName(
            "secondaryButton"
        )

        clear_button.clicked.connect(
            self._clear_report
        )

        header.addWidget(
            title
        )

        header.addWidget(
            self.report_status
        )

        header.addStretch()

        header.addWidget(
            copy_button
        )

        header.addWidget(
            export_txt
        )

        header.addWidget(
            export_pdf
        )

        header.addWidget(
            clear_button
        )

        layout.addLayout(
            header
        )

        self.report_output = QTextEdit()

        self.report_output.setObjectName(
            "output"
        )

        self.report_output.setReadOnly(
            True
        )

        self.report_output.setFont(
            QFont(
                "Consolas",
                10,
            )
        )

        self.report_output.setMinimumHeight(
            300
        )

        layout.addWidget(
            self.report_output
        )

        return card

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def _run_health_check(self) -> None:
        if (
            self._thread is not None
            and self._thread.isRunning()
        ):
            return

        database = (
            database_context.active()
        )

        self.generate_button.setEnabled(
            False
        )

        self.overall_status.setText(
            "SCANNING..."
        )

        self.overall_status.setStyleSheet(
            "color: #2563EB;"
        )

        self.summary_label.setText(
            "Collecting system information and checking Windows health..."
        )

        self.issues_label.setText(
            "Running health check..."
        )

        self.report_output.clear()

        self.report_output.setPlainText(
            ">>> AIO TOOLBOX SUPPORT HEALTH CHECK\n\n"
            "Running full health check..."
        )

        self.report_status.setText(
            "Scanning..."
        )

        self._clear_health_items()

        thread = QThread(
            self
        )

        worker = ReportWorker(
            database
        )

        self._thread = thread
        self._worker = worker

        worker.moveToThread(
            thread
        )

        thread.started.connect(
            worker.run
        )

        worker.finished.connect(
            self._health_check_finished
        )

        worker.failed.connect(
            self._health_check_failed
        )

        worker.finished.connect(
            thread.quit
        )

        worker.failed.connect(
            thread.quit
        )

        worker.finished.connect(
            worker.deleteLater
        )

        worker.failed.connect(
            worker.deleteLater
        )

        thread.finished.connect(
            thread.deleteLater
        )

        thread.finished.connect(
            self._thread_finished
        )

        thread.start()

    def _health_check_finished(
        self,
        result: object,
    ) -> None:
        if not isinstance(
            result,
            HealthCheckResult,
        ):
            self._health_check_failed(
                "Invalid result from health check service."
            )
            return

        self._display_result(
            result
        )

        self.generate_button.setEnabled(
            True
        )

    def _health_check_failed(
        self,
        error: str,
    ) -> None:
        self.overall_status.setText(
            "FAILED"
        )

        self.overall_status.setStyleSheet(
            "color: #D32F2F;"
        )

        self.summary_label.setText(
            "The health check could not be completed."
        )

        self.issues_label.setText(
            error
        )

        self.report_output.setPlainText(
            ">>> AIO TOOLBOX SUPPORT HEALTH CHECK\n\n"
            "Health check failed.\n\n"
            f"{error}"
        )

        self.report_status.setText(
            "Failed"
        )

        self.generate_button.setEnabled(
            True
        )

    # ------------------------------------------------------------------
    # Result display
    # ------------------------------------------------------------------

    def _display_result(
        self,
        result: HealthCheckResult,
    ) -> None:
        status = result.overall_status

        self.overall_status.setText(
            status
        )

        if status == "HEALTHY":
            self.overall_status.setStyleSheet(
                "color: #1B7F3A;"
            )

        elif status == "WARNING":
            self.overall_status.setStyleSheet(
                "color: #C47A00;"
            )

        elif status == "CRITICAL":
            self.overall_status.setStyleSheet(
                "color: #D32F2F;"
            )

        else:
            self.overall_status.setStyleSheet(
                "color: #526176;"
            )

        self.summary_label.setText(
            result.summary
        )

        self._display_health_items(
            result.items
        )

        if result.issues:
            self.issues_label.setText(
                "\n".join(
                    f"• {issue}"
                    for issue in result.issues
                )
            )

        else:
            self.issues_label.setText(
                "No issues detected."
            )

        self.report_output.setPlainText(
            result.report_text
        )

        self.report_status.setText(
            "Completed"
        )

    # ------------------------------------------------------------------
    # Health item cards
    # ------------------------------------------------------------------

    def _clear_health_items(self) -> None:
        while self.health_grid.count():
            item = (
                self.health_grid.takeAt(0)
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def _display_health_items(
        self,
        items: list[HealthCheckItem],
    ) -> None:
        self._clear_health_items()

        for index, item in enumerate(
            items
        ):
            row = index // 3
            column = index % 3

            frame = (
                self._create_health_item(
                    item
                )
            )

            self.health_grid.addWidget(
                frame,
                row,
                column,
            )

    def _create_health_item(
        self,
        item: HealthCheckItem,
    ) -> QFrame:
        frame = QFrame()

        frame.setObjectName(
            "healthItem"
        )

        frame.setMinimumHeight(
            68
        )

        layout = QHBoxLayout(
            frame
        )

        layout.setContentsMargins(
            10,
            8,
            10,
            8,
        )

        layout.setSpacing(
            8
        )

        text_layout = QVBoxLayout()

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        text_layout.setSpacing(
            3
        )

        title = QLabel(
            item.title
        )

        title.setObjectName(
            "healthTitle"
        )

        value = QLabel(
            item.value
        )

        value.setObjectName(
            "healthValue"
        )

        value.setWordWrap(
            True
        )

        value.setMaximumHeight(
            32
        )

        text_layout.addWidget(
            title
        )

        text_layout.addWidget(
            value
        )

        status = QLabel(
            item.status
        )

        status.setObjectName(
            "healthStatus"
        )

        status.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        status.setMinimumWidth(
            62
        )

        if item.status == "OK":
            status.setStyleSheet(
                "color: #1B7F3A;"
            )

        elif item.status == "WARNING":
            status.setStyleSheet(
                "color: #C47A00;"
            )

        elif item.status == "CRITICAL":
            status.setStyleSheet(
                "color: #D32F2F;"
            )

        else:
            status.setStyleSheet(
                "color: #526176;"
            )

        layout.addLayout(
            text_layout,
            1,
        )

        layout.addWidget(
            status
        )

        return frame

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    def _database_changed(
        self,
        database: dict | None,
    ) -> None:
        self._update_database_status()

    def _update_database_status(self) -> None:
        database = (
            database_context.active()
        )

        if database:
            self.database_status.setText(
                "Active database: "
                f"{database.get('name') or 'Connected'}"
            )

        else:
            self.database_status.setText(
                "Active database: Not connected"
            )

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def _copy_report(self) -> None:
        text = (
            self.report_output
            .toPlainText()
            .strip()
        )

        if not text:
            return

        self.report_output.selectAll()
        self.report_output.copy()

        cursor = (
            self.report_output
            .textCursor()
        )

        cursor.movePosition(
            cursor.MoveOperation.End
        )

        self.report_output.setTextCursor(
            cursor
        )

        self.report_status.setText(
            "Copied"
        )

    def _export_txt(self) -> None:
        text = (
            self.report_output
            .toPlainText()
            .strip()
        )

        if not text:
            QMessageBox.information(
                self,
                "No Report",
                "Run the health check first.",
            )
            return

        path, _ = (
            QFileDialog.getSaveFileName(
                self,
                "Export Support Report",
                "AIO_Support_Health_Check.txt",
                "Text Files (*.txt)",
            )
        )

        if not path:
            return

        try:
            with open(
                path,
                "w",
                encoding="utf-8",
            ) as file:
                file.write(
                    text
                )

            self.report_status.setText(
                "TXT exported"
            )

            QMessageBox.information(
                self,
                "Report Exported",
                "The support report was exported successfully.",
            )

        except OSError as exc:
            QMessageBox.critical(
                self,
                "Export Error",
                str(exc),
            )

    def _export_pdf(self) -> None:
        text = (
            self.report_output
            .toPlainText()
            .strip()
        )

        if not text:
            QMessageBox.information(
                self,
                "No Report",
                "Run the health check first.",
            )
            return

        path, _ = (
            QFileDialog.getSaveFileName(
                self,
                "Export Support Report",
                "AIO_Support_Health_Check.pdf",
                "PDF Files (*.pdf)",
            )
        )

        if not path:
            return

        try:
            printer = QPrinter(
                QPrinter.PrinterMode.HighResolution
            )

            printer.setOutputFormat(
                QPrinter.OutputFormat.PdfFormat
            )

            printer.setOutputFileName(
                path
            )

            from PySide6.QtGui import QTextDocument

            document = QTextDocument()

            html = (
                "<html>"
                "<head>"
                "<meta charset='utf-8'>"
                "<style>"
                "body {"
                "font-family: Consolas, monospace;"
                "font-size: 9pt;"
                "white-space: pre-wrap;"
                "}"
                "</style>"
                "</head>"
                "<body>"
                + self._escape_html(
                    text
                )
                + "</body>"
                "</html>"
            )

            document.setHtml(
                html
            )

            document.print_(
                printer
            )

            self.report_status.setText(
                "PDF exported"
            )

            QMessageBox.information(
                self,
                "Report Exported",
                "The support report was exported successfully.",
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "PDF Export Error",
                str(exc),
            )

    @staticmethod
    def _escape_html(
        text: str,
    ) -> str:
        return (
            text
            .replace(
                "&",
                "&amp;",
            )
            .replace(
                "<",
                "&lt;",
            )
            .replace(
                ">",
                "&gt;",
            )
            .replace(
                "\n",
                "<br>",
            )
        )

    # ------------------------------------------------------------------
    # Clear / Thread
    # ------------------------------------------------------------------

    def _clear_report(self) -> None:
        self.report_output.clear()

        self._clear_health_items()

        self.overall_status.setText(
            "READY"
        )

        self.overall_status.setStyleSheet(
            "color: #1B7F3A;"
        )

        self.summary_label.setText(
            "Run a full health check to analyze this computer."
        )

        self.issues_label.setText(
            "No health check has been run yet."
        )

        self.report_status.setText(
            "Ready"
        )

    def _thread_finished(self) -> None:
        self._thread = None
        self._worker = None

    def closeEvent(self, event) -> None:
        if (
            self._thread is not None
            and self._thread.isRunning()
        ):
            self._thread.quit()
            self._thread.wait(
                2000
            )

        super().closeEvent(
            event
        )