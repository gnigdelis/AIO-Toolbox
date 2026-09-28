from __future__ import annotations

from PySide6.QtCore import (
    QObject,
    QThread,
    Qt,
    Signal,
)
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.diagnostics.diagnostics_service import (
    DiagnosticResult,
    DiagnosticsService,
)


class DiagnosticWorker(QObject):

    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        operation: str,
    ) -> None:
        super().__init__()

        self.operation = operation

    def run(self) -> None:

        try:

            result = (
                DiagnosticsService()
                .execute(
                    self.operation
                )
            )

            self.finished.emit(
                result
            )

        except Exception as exc:

            self.failed.emit(
                str(exc)
            )


class DiagnosticsPage(QWidget):
    """AIO Toolbox - Windows diagnostics."""

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:

        super().__init__(
            parent
        )

        self._thread: QThread | None = None
        self._worker: DiagnosticWorker | None = None

        self._buttons: list[QPushButton] = []

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:

        self.setObjectName(
            "diagnosticsPage"
        )

        self.setStyleSheet(
            """
            QWidget#diagnosticsPage {
                background: #f5f6f8;
            }

            QFrame#headerCard,
            QFrame#toolCard,
            QFrame#outputCard {
                background: #ffffff;
                border: 1px solid #e3e6eb;
                border-radius: 10px;
            }

            QLabel#pageTitle {
                color: #1f2937;
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#pageSubtitle {
                color: #6b7280;
                font-size: 13px;
            }

            QLabel#sectionTitle {
                color: #1f2937;
                font-size: 15px;
                font-weight: 700;
            }

            QLabel#toolTitle {
                color: #1f2937;
                font-size: 14px;
                font-weight: 700;
            }

            QLabel#toolDescription {
                color: #6b7280;
                font-size: 11px;
            }

            QPushButton#toolButton {
                background: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 7px 12px;
                font-size: 11px;
                font-weight: 700;
            }

            QPushButton#toolButton:hover {
                background: #1d4ed8;
            }

            QPushButton#toolButton:pressed {
                background: #1e40af;
            }

            QPushButton#toolButton:disabled {
                background: #b8c0cc;
                color: #eef0f3;
            }

            QPushButton#secondaryButton {
                background: #ffffff;
                color: #374151;
                border: 1px solid #d6dae1;
                border-radius: 6px;
                padding: 6px 11px;
                font-size: 11px;
                font-weight: 600;
            }

            QPushButton#secondaryButton:hover {
                background: #f3f4f6;
            }

            QTextEdit#outputText {
                background: #111827;
                color: #e5e7eb;
                border: none;
                border-radius: 7px;
                padding: 10px;
                font-family: Consolas;
                font-size: 11px;
            }
            """
        )

        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            22,
            20,
            22,
            18,
        )

        root.setSpacing(
            14
        )

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
            0,
            0,
            6,
            0,
        )

        content_layout.setSpacing(
            14
        )

        content_layout.addWidget(
            self._create_header_card()
        )

        content_layout.addWidget(
            self._create_tools_card()
        )

        content_layout.addWidget(
            self._create_output_card(),
            1,
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

    def _create_header_card(
        self,
    ) -> QFrame:

        card = QFrame()

        card.setObjectName(
            "headerCard"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            18,
            16,
            18,
            16,
        )

        layout.setSpacing(
            5
        )

        title = QLabel(
            "Diagnostics"
        )

        title.setObjectName(
            "pageTitle"
        )

        subtitle = QLabel(
            "Inspect Windows, hardware, "
            "storage and system health."
        )

        subtitle.setObjectName(
            "pageSubtitle"
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        return card

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def _create_tools_card(
        self,
    ) -> QFrame:

        wrapper = QFrame()

        wrapper.setStyleSheet(
            "QFrame { "
            "background: transparent; "
            "}"
        )

        layout = QVBoxLayout(
            wrapper
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            10
        )

        title = QLabel(
            "Diagnostic Tools"
        )

        title.setObjectName(
            "sectionTitle"
        )

        layout.addWidget(
            title
        )

        tools = [
            (
                "system_information",
                "System Information",
                "CPU, RAM, Windows, BIOS, "
                "uptime and computer details.",
            ),
            (
                "memory",
                "Memory",
                "RAM usage and available memory.",
            ),
            (
                "disks",
                "Disk Space",
                "Free and used space "
                "on local drives.",
            ),
            (
                "graphics",
                "Graphics",
                "GPU, driver and current "
                "display information.",
            ),
            (
                "network",
                "Network Status",
                "Active adapters, IP, "
                "gateway and DNS information.",
            ),
            (
                "processes",
                "Top Processes",
                "Processes using the most "
                "CPU and memory.",
            ),
            (
                "services",
                "Services Status",
                "Windows service health and "
                "automatic services not running.",
            ),
            (
                "windows_update",
                "Windows Update",
                "Windows Update service "
                "and client status.",
            ),
            (
                "event_log_errors",
                "System Errors",
                "Recent System error events "
                "from the last 7 days.",
            ),
        ]

        grid = QGridLayout()

        grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        grid.setHorizontalSpacing(
            12
        )

        grid.setVerticalSpacing(
            12
        )

        for index, (
            operation,
            title_text,
            description,
        ) in enumerate(tools):

            grid.addWidget(
                self._create_tool_card(
                    operation,
                    title_text,
                    description,
                ),
                index // 2,
                index % 2,
            )

        grid.setColumnStretch(
            0,
            1,
        )

        grid.setColumnStretch(
            1,
            1,
        )

        layout.addLayout(
            grid
        )

        return wrapper

    def _create_tool_card(
        self,
        operation: str,
        title_text: str,
        description: str,
    ) -> QFrame:

        card = QFrame()

        card.setObjectName(
            "toolCard"
        )

        card.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred,
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            14,
            13,
            14,
            13,
        )

        layout.setSpacing(
            7
        )

        title = QLabel(
            title_text
        )

        title.setObjectName(
            "toolTitle"
        )

        description_label = QLabel(
            description
        )

        description_label.setObjectName(
            "toolDescription"
        )

        description_label.setWordWrap(
            True
        )

        description_label.setMinimumHeight(
            30
        )

        button = QPushButton(
            f"RUN {title_text.upper()}"
        )

        button.setObjectName(
            "toolButton"
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        button.setMinimumHeight(
            32
        )

        button.clicked.connect(
            lambda checked=False,
            op=operation:
            self._run_operation(op)
        )

        self._buttons.append(
            button
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            description_label
        )

        layout.addStretch()

        layout.addWidget(
            button
        )

        return card

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def _create_output_card(
        self,
    ) -> QFrame:

        card = QFrame()

        card.setObjectName(
            "outputCard"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            14,
            13,
            14,
            13,
        )

        layout.setSpacing(
            9
        )

        header = QHBoxLayout()

        title = QLabel(
            "Diagnostic Output"
        )

        title.setObjectName(
            "sectionTitle"
        )

        self.output_status = QLabel(
            "Ready"
        )

        copy_button = QPushButton(
            "Copy"
        )

        copy_button.setObjectName(
            "secondaryButton"
        )

        copy_button.clicked.connect(
            self._copy_output
        )

        clear_button = QPushButton(
            "Clear"
        )

        clear_button.setObjectName(
            "secondaryButton"
        )

        clear_button.clicked.connect(
            self._clear_output
        )

        header.addWidget(
            title
        )

        header.addWidget(
            self.output_status
        )

        header.addStretch()

        header.addWidget(
            copy_button
        )

        header.addWidget(
            clear_button
        )

        layout.addLayout(
            header
        )

        self.output_text = QTextEdit()

        self.output_text.setObjectName(
            "outputText"
        )

        self.output_text.setReadOnly(
            True
        )

        self.output_text.setMinimumHeight(
            220
        )

        self.output_text.setFont(
            QFont(
                "Consolas",
                10,
            )
        )

        layout.addWidget(
            self.output_text,
            1,
        )

        return card

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------

    def _run_operation(
        self,
        operation: str,
    ) -> None:

        self._set_running(
            True
        )

        title = self._title(
            operation
        )

        self.output_text.clear()

        self.output_text.append(
            f">>> {title}"
        )

        self.output_text.append(
            ""
        )

        self.output_text.append(
            "Running..."
        )

        self.output_status.setText(
            "Running..."
        )

        thread = QThread(
            self
        )

        worker = DiagnosticWorker(
            operation
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
            self._operation_finished
        )

        worker.failed.connect(
            self._operation_failed
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

    @staticmethod
    def _title(
        operation: str,
    ) -> str:

        return {
            "system_information":
                "System Information",

            "memory":
                "Memory",

            "disks":
                "Disk Space",

            "graphics":
                "Graphics",

            "network":
                "Network Status",

            "processes":
                "Top Processes",

            "services":
                "Services Status",

            "windows_update":
                "Windows Update",

            "event_log_errors":
                "System Errors",
        }.get(
            operation,
            operation,
        )

    # ------------------------------------------------------------------
    # Result
    # ------------------------------------------------------------------

    def _operation_finished(
        self,
        result: object,
    ) -> None:

        if not isinstance(
            result,
            DiagnosticResult,
        ):

            self._operation_failed(
                "Invalid result from "
                "diagnostics service."
            )

            return

        self.output_text.clear()

        self.output_text.append(
            f">>> {result.title}"
        )

        self.output_text.append(
            ""
        )

        self.output_text.append(
            result.output
            or "No information returned."
        )

        if result.details:

            self.output_text.append(
                ""
            )

            self.output_text.append(
                f"Status: {result.details}"
            )

        self.output_status.setText(
            "Completed successfully"
            if result.success
            else
            "Completed with errors"
        )

        self._set_running(
            False
        )

    def _operation_failed(
        self,
        error: str,
    ) -> None:

        self.output_text.clear()

        self.output_text.append(
            ">>> Diagnostics"
        )

        self.output_text.append(
            ""
        )

        self.output_text.append(
            "Operation failed."
        )

        self.output_text.append(
            ""
        )

        self.output_text.append(
            error
        )

        self.output_status.setText(
            "Failed"
        )

        self._set_running(
            False
        )

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def _set_running(
        self,
        running: bool,
    ) -> None:

        for button in self._buttons:

            button.setEnabled(
                not running
            )

    def _thread_finished(
        self,
    ) -> None:

        self._thread = None
        self._worker = None

    # ------------------------------------------------------------------
    # Output actions
    # ------------------------------------------------------------------

    def _clear_output(
        self,
    ) -> None:

        self.output_text.clear()

        self.output_status.setText(
            "Ready"
        )

    def _copy_output(
        self,
    ) -> None:

        if not self.output_text.toPlainText().strip():
            return

        self.output_text.selectAll()

        self.output_text.copy()

        self.output_text.moveCursor(
            self.output_text
            .textCursor()
            .MoveOperation.End
        )

        self.output_status.setText(
            "Copied to clipboard"
        )

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def closeEvent(
        self,
        event,
    ) -> None:

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