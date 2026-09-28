from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.utilities.utilities_service import (
    UtilityResult,
    UtilitiesService,
)

from ui.v2.widgets.page_layout import (
    PAGE_LAYOUT_STYLE,
    setup_page_layout,
)


class UtilityWorker(QObject):
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
            result = UtilitiesService().execute(
                self.operation
            )

            self.finished.emit(
                result
            )

        except Exception as exc:
            self.failed.emit(
                str(exc)
            )


class UtilitiesPage(QWidget):
    """AIO Toolbox - everyday Windows utilities."""

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._thread: QThread | None = None
        self._worker: UtilityWorker | None = None

        self._buttons: list[QPushButton] = []

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setObjectName("utilitiesPage")

        root, title, subtitle = setup_page_layout(
            self,
            "Utilities",
            "Everyday Windows utilities and shortcuts for support work.",
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 6, 0)
        content_layout.setSpacing(16)

        # Keep the Operation Log near the top so results are immediately
        # visible instead of being pushed to the bottom of the page.
        content_layout.addWidget(
            self._create_output_card()
        )

        content_layout.addWidget(
            self._create_tools_card(),
            1,
        )

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        self.setStyleSheet(
            PAGE_LAYOUT_STYLE
            + """
            QWidget#utilitiesPage {
                background: transparent;
            }

            QFrame#toolCard,
            QFrame#outputCard {
                background: #FFFFFF;
                border: 1px solid #DCE3EC;
                border-radius: 10px;
            }

            QLabel#sectionTitle {
                color: #526176;
                font-size: 12px;
                font-weight: 600;
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
                min-height: 32px;
                padding: 0 12px;
                background: #2F6FED;
                color: #FFFFFF;
                border: 1px solid #2F6FED;
                border-radius: 6px;
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton#toolButton:hover {
                background: #245DCA;
            }

            QPushButton#toolButton:pressed {
                background: #1F52B4;
            }

            QPushButton#toolButton:disabled {
                color: #A8B2C0;
                background: #F1F4F8;
                border-color: #E1E6ED;
            }

            QPushButton#toolButton[
                operation="danger"
            ] {
                background: #C92A2A;
                border-color: #C92A2A;
            }

            QPushButton#toolButton[
                operation="danger"
            ]:hover {
                background: #B42318;
            }

            QPushButton#toolButton[
                operation="warning"
            ] {
                background: #B66A00;
                border-color: #B66A00;
            }

            QPushButton#toolButton[
                operation="warning"
            ]:hover {
                background: #995800;
            }

            QPushButton#secondaryButton {
                min-height: 32px;
                padding: 0 12px;
                background: #FFFFFF;
                color: #40506A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton#secondaryButton:hover {
                background: #F5F8FC;
            }

            QTextEdit#outputText {
                min-height: 180px;
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

        layout = QVBoxLayout(card)

        layout.setContentsMargins(
            18,
            16,
            18,
            16,
        )

        layout.setSpacing(5)

        title = QLabel(
            "Utilities"
        )

        title.setObjectName(
            "pageTitle"
        )

        subtitle = QLabel(
            "Everyday Windows utilities "
            "and shortcuts for support work."
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

        layout.setSpacing(10)

        title = QLabel(
            "Windows Utilities"
        )

        title.setObjectName(
            "sectionTitle"
        )

        layout.addWidget(
            title
        )

        tools = [
            (
                "calculator",
                "Calculator",
                "Open the Windows Calculator.",
                "OPEN CALCULATOR",
                "normal",
            ),
            (
                "notepad",
                "Notepad",
                "Open Windows Notepad.",
                "OPEN NOTEPAD",
                "normal",
            ),
            (
                "file_explorer",
                "File Explorer",
                "Open Windows File Explorer.",
                "OPEN EXPLORER",
                "normal",
            ),
            (
                "command_prompt",
                "Command Prompt",
                "Open a standard Windows CMD window.",
                "OPEN CMD",
                "normal",
            ),
            (
                "powershell",
                "PowerShell",
                "Open Windows PowerShell.",
                "OPEN POWERSHELL",
                "normal",
            ),
            (
                "task_manager",
                "Task Manager",
                "Open Windows Task Manager.",
                "OPEN TASK MANAGER",
                "normal",
            ),
            (
                "computer_management",
                "Computer Management",
                "Open Computer Management console.",
                "OPEN MANAGEMENT",
                "normal",
            ),
            (
                "services",
                "Services",
                "Open the Windows Services console.",
                "OPEN SERVICES",
                "normal",
            ),
            (
                "registry_editor",
                "Registry Editor",
                "Open the Windows Registry Editor.",
                "OPEN REGISTRY",
                "normal",
            ),
            (
                "settings_system",
                "Windows Settings",
                "Open the main System settings page.",
                "OPEN SETTINGS",
                "normal",
            ),
            (
                "settings_network",
                "Network Settings",
                "Open Windows Network settings.",
                "OPEN NETWORK",
                "normal",
            ),
            (
                "settings_windows_update",
                "Windows Update",
                "Open Windows Update settings.",
                "OPEN UPDATE",
                "normal",
            ),
            (
                "clear_temp_files",
                "Clear Temporary Files",
                "Remove temporary files that are not in use.",
                "CLEAR TEMP FILES",
                "warning",
            ),
            (
                "restart",
                "Restart Windows",
                "Restart the computer after confirmation.",
                "RESTART WINDOWS",
                "danger",
            ),
            (
                "shutdown",
                "Shutdown Windows",
                "Shut down the computer after confirmation.",
                "SHUTDOWN WINDOWS",
                "danger",
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

        for index, item in enumerate(
            tools
        ):

            card = self._create_tool_card(
                *item
            )

            grid.addWidget(
                card,
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
        button_text: str,
        button_type: str,
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

        layout.setSpacing(7)

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
            button_text
        )

        button.setObjectName(
            "toolButton"
        )

        button.setProperty(
            "operation",
            button_type,
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

        layout.setSpacing(9)

        header = QHBoxLayout()

        title = QLabel(
            "Operation Log"
        )

        title.setObjectName(
            "sectionTitle"
        )

        self.output_status = QLabel(
            "Ready"
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

        copy_button = QPushButton(
            "Copy"
        )

        copy_button.setObjectName(
            "secondaryButton"
        )

        copy_button.clicked.connect(
            self._copy_output
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
            180
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

        if operation == "restart":

            answer = QMessageBox.question(
                self,
                "Restart Windows",
                "Are you sure you want to "
                "restart Windows now?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if (
                answer
                != QMessageBox.StandardButton.Yes
            ):
                return

        if operation == "shutdown":

            answer = QMessageBox.question(
                self,
                "Shutdown Windows",
                "Are you sure you want to "
                "shut down Windows now?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if (
                answer
                != QMessageBox.StandardButton.Yes
            ):
                return

        self._set_running(
            True
        )

        self.output_text.clear()

        self.output_text.append(
            f">>> {self._title(operation)}"
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

        worker = UtilityWorker(
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
            "calculator": "Calculator",
            "notepad": "Notepad",
            "file_explorer": "File Explorer",
            "command_prompt": "Command Prompt",
            "powershell": "PowerShell",
            "task_manager": "Task Manager",
            "computer_management":
                "Computer Management",
            "services": "Services",
            "registry_editor":
                "Registry Editor",
            "settings_system":
                "Windows Settings",
            "settings_network":
                "Network Settings",
            "settings_windows_update":
                "Windows Update",
            "clear_temp_files":
                "Clear Temporary Files",
            "restart":
                "Restart Windows",
            "shutdown":
                "Shutdown Windows",
        }.get(
            operation,
            operation,
        )

    def _operation_finished(
        self,
        result: object,
    ) -> None:

        if not isinstance(
            result,
            UtilityResult,
        ):

            self._operation_failed(
                "Invalid result from "
                "utilities service."
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
            result.message
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
            ">>> Utilities"
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
    # Output
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