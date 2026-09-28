from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.network.network_service import (
    NetworkResult,
    NetworkService,
)

from ui.v2.widgets.page_layout import (
    PAGE_LAYOUT_STYLE,
    setup_page_layout,
)


class NetworkToolWorker(QObject):
    line_received = Signal(str)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        operation: str,
        host: str = "",
        port: int | str = "",
    ) -> None:
        super().__init__()

        self.operation = operation
        self.host = host
        self.port = port

    def run(self) -> None:
        try:
            service = NetworkService()

            result = service.execute(
                self.operation,
                host=self.host,
                port=self.port,
                progress_callback=self._emit_progress,
            )

            self.finished.emit(result)

        except Exception as exc:
            self.failed.emit(str(exc))

    def _emit_progress(
        self,
        text: str,
    ) -> None:
        self.line_received.emit(text)


class NetworkToolsPage(QWidget):
    """AIO Toolbox - Network Tools."""

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._thread: QThread | None = None
        self._worker: NetworkToolWorker | None = None

        self._buttons: list[QPushButton] = []

        self._streaming_operation = False

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setObjectName("networkToolsPage")

        root, title, subtitle = setup_page_layout(
            self,
            "Network Tools",
            "Network diagnostics and connectivity tools for Windows.",
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

        # Operation Log is intentionally placed above the diagnostics area
        # so results are immediately visible without scrolling to the bottom.
        content_layout.addWidget(
            self._create_output_card(),
        )

        content_layout.addWidget(self._create_target_card())
        content_layout.addWidget(
            self._create_tools_card(),
            1,
        )

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        self.setStyleSheet(
            PAGE_LAYOUT_STYLE
            + """
            QWidget#networkToolsPage {
                background: transparent;
            }

            QFrame#targetCard,
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

            QLabel#fieldLabel {
                color: #526176;
                font-size: 11px;
                font-weight: 600;
            }

            QLineEdit#targetInput,
            QLineEdit#portInput {
                min-height: 36px;
                padding: 4px 9px;
                background: #F8FAFC;
                color: #26344D;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                font-size: 11px;
            }

            QLineEdit#targetInput:focus,
            QLineEdit#portInput:focus {
                border: 1px solid #4C8BF5;
                background: #FFFFFF;
            }

            QLabel#hintLabel {
                color: #718096;
                font-size: 10px;
            }

            QFrame#toolCard {
                background: #FFFFFF;
                border: 1px solid #DCE3EC;
                border-radius: 10px;
                min-height: 118px;
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

            QLabel#outputTitle {
                color: #526176;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#outputStatus {
                color: #718096;
                font-size: 10px;
            }

            QTextEdit#outputText {
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
    # Target
    # ------------------------------------------------------------------

    def _create_target_card(
        self,
    ) -> QFrame:

        card = QFrame()

        card.setObjectName(
            "targetCard"
        )

        layout = QVBoxLayout(card)

        layout.setContentsMargins(
            18,
            15,
            18,
            15,
        )

        layout.setSpacing(10)

        title = QLabel("Target")

        title.setObjectName(
            "sectionTitle"
        )

        layout.addWidget(title)

        fields = QHBoxLayout()

        fields.setSpacing(12)

        host_container = QWidget()

        host_layout = QVBoxLayout(
            host_container
        )

        host_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        host_layout.setSpacing(5)

        host_label = QLabel(
            "Hostname / IP Address"
        )

        host_label.setObjectName(
            "fieldLabel"
        )

        self.host_input = QLineEdit()

        self.host_input.setObjectName(
            "targetInput"
        )

        self.host_input.setPlaceholderText(
            "π.χ. 192.168.1.1 ή "
            "server01 ή google.com"
        )

        self.host_input.setMinimumHeight(
            36
        )

        host_layout.addWidget(
            host_label
        )

        host_layout.addWidget(
            self.host_input
        )

        port_container = QWidget()

        port_container.setMaximumWidth(
            170
        )

        port_layout = QVBoxLayout(
            port_container
        )

        port_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        port_layout.setSpacing(5)

        port_label = QLabel("Port")

        port_label.setObjectName(
            "fieldLabel"
        )

        self.port_input = QLineEdit()

        self.port_input.setObjectName(
            "portInput"
        )

        self.port_input.setPlaceholderText(
            "π.χ. 443"
        )

        self.port_input.setText(
            "443"
        )

        self.port_input.setMinimumHeight(
            36
        )

        port_layout.addWidget(
            port_label
        )

        port_layout.addWidget(
            self.port_input
        )

        fields.addWidget(
            host_container,
            1,
        )

        fields.addWidget(
            port_container
        )

        layout.addLayout(fields)

        hint = QLabel(
            "Το Host/IP χρησιμοποιείται από "
            "Ping, Traceroute, DNS Lookup "
            "και Port Test."
        )

        hint.setObjectName(
            "hintLabel"
        )

        layout.addWidget(hint)

        return card

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def _create_tools_card(
        self,
    ) -> QFrame:

        wrapper = QFrame()

        wrapper.setObjectName(
            "toolsWrapper"
        )

        wrapper.setStyleSheet(
            "QFrame#toolsWrapper "
            "{ background: transparent; }"
        )

        layout = QVBoxLayout(wrapper)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(10)

        title = QLabel(
            "Network Diagnostics"
        )

        title.setObjectName(
            "sectionTitle"
        )

        layout.addWidget(title)

        grid = QGridLayout()

        grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        grid.setHorizontalSpacing(12)

        grid.setVerticalSpacing(12)

        tools = [
            (
                "ping",
                "Ping",
                "Ελέγχει αν ένα host είναι "
                "reachable και εμφανίζει latency.",
            ),
            (
                "traceroute",
                "Traceroute",
                "Εμφανίζει τη διαδρομή των "
                "packets μέχρι τον προορισμό.",
            ),
            (
                "dns_lookup",
                "DNS Lookup",
                "Μετατρέπει hostname σε IP "
                "addresses και κάνει reverse lookup.",
            ),
            (
                "port_test",
                "Port Test",
                "Ελέγχει αν μια συγκεκριμένη "
                "TCP port είναι προσβάσιμη.",
            ),
            (
                "ip_configuration",
                "IP Configuration",
                "Εμφανίζει την πλήρη TCP/IP "
                "configuration του υπολογιστή.",
            ),
            (
                "network_adapters",
                "Network Adapters",
                "Εμφανίζει τους διαθέσιμους "
                "network adapters και την "
                "κατάστασή τους.",
            ),
            (
                "internet_connectivity",
                "Internet Connectivity",
                "Ελέγχει DNS και HTTPS "
                "connectivity προς το Internet.",
            ),
        ]

        for index, (
            operation,
            title_text,
            description,
        ) in enumerate(tools):

            tool_card = self._create_tool_card(
                operation,
                title_text,
                description,
            )

            grid.addWidget(
                tool_card,
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

        layout.addLayout(grid)

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

        layout = QVBoxLayout(card)

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
            self._button_text(
                operation
            )
        )

        button.setObjectName(
            "toolButton"
        )

        button.setProperty(
            "operation",
            operation,
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

        layout.addWidget(title)

        layout.addWidget(
            description_label
        )

        layout.addStretch()

        layout.addWidget(button)

        return card

    @staticmethod
    def _button_text(
        operation: str,
    ) -> str:

        return {
            "ping": "RUN PING",
            "traceroute": "RUN TRACEROUTE",
            "dns_lookup": "DNS LOOKUP",
            "port_test": "TEST PORT",
            "ip_configuration": "SHOW IP CONFIG",
            "network_adapters": "SHOW ADAPTERS",
            "internet_connectivity": "TEST INTERNET",
        }.get(
            operation,
            "RUN",
        )

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

        layout = QVBoxLayout(card)

        layout.setContentsMargins(
            14,
            13,
            14,
            13,
        )

        layout.setSpacing(9)

        header = QHBoxLayout()

        header.setSpacing(8)

        title = QLabel(
            "Operation Log"
        )

        title.setObjectName(
            "outputTitle"
        )

        self.output_status = QLabel(
            "Ready"
        )

        self.output_status.setObjectName(
            "outputStatus"
        )

        header.addWidget(title)

        header.addWidget(
            self.output_status
        )

        header.addStretch()

        copy_button = QPushButton(
            "Copy"
        )

        copy_button.setObjectName(
            "secondaryButton"
        )

        copy_button.setCursor(
            Qt.PointingHandCursor
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

        clear_button.setCursor(
            Qt.PointingHandCursor
        )

        clear_button.clicked.connect(
            self._clear_output
        )

        header.addWidget(
            copy_button
        )

        header.addWidget(
            clear_button
        )

        layout.addLayout(header)

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

        self.output_text.setPlaceholderText(
            "Τα αποτελέσματα των network "
            "tests θα εμφανιστούν εδώ..."
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

        host_required = {
            "ping",
            "traceroute",
            "dns_lookup",
            "port_test",
        }

        host = (
            self.host_input
            .text()
            .strip()
        )

        if (
            operation in host_required
            and not host
        ):

            QMessageBox.warning(
                self,
                "Network Tools",
                "Πρέπει να εισάγεις "
                "Hostname ή IP Address.",
            )

            self.host_input.setFocus()

            return

        port = (
            self.port_input
            .text()
            .strip()
        )

        if (
            operation == "port_test"
            and not port
        ):

            QMessageBox.warning(
                self,
                "Network Tools",
                "Πρέπει να εισάγεις "
                "TCP Port.",
            )

            self.port_input.setFocus()

            return

        self._streaming_operation = (
            operation
            in {
                "ping",
                "traceroute",
            }
        )

        self._set_running(
            True,
            operation,
        )

        self.output_text.clear()

        self.output_text.append(
            f">>> "
            f"{self._operation_title(operation)}"
        )

        self.output_text.append(
            ""
        )

        self.output_text.append(
            "Running..."
        )

        self.output_status.setText(
            f"Running "
            f"{self._operation_title(operation)}..."
        )

        thread = QThread(self)

        worker = NetworkToolWorker(
            operation=operation,
            host=host,
            port=port,
        )

        self._thread = thread

        self._worker = worker

        worker.moveToThread(
            thread
        )

        thread.started.connect(
            worker.run
        )

        worker.line_received.connect(
            self._operation_progress
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
    def _operation_title(
        operation: str,
    ) -> str:

        return {
            "ping": "Ping",
            "traceroute": "Traceroute",
            "dns_lookup": "DNS Lookup",
            "port_test": "Port Test",
            "ip_configuration": "IP Configuration",
            "network_adapters": "Network Adapters",
            "internet_connectivity": (
                "Internet Connectivity"
            ),
        }.get(
            operation,
            operation,
        )

    # ------------------------------------------------------------------
    # Live output
    # ------------------------------------------------------------------

    def _operation_progress(
        self,
        text: str,
    ) -> None:

        if (
            text.startswith(
                "Starting "
            )
            or text.startswith(
                "Completed "
            )
            or text
            == "Operation completed with errors."
        ):
            return

        if (
            text == "Running..."
            and self._streaming_operation
        ):
            return

        self.output_text.append(
            text
        )

        scrollbar = (
            self.output_text
            .verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )

    # ------------------------------------------------------------------
    # Finished
    # ------------------------------------------------------------------

    def _operation_finished(
        self,
        result: object,
    ) -> None:

        if not isinstance(
            result,
            NetworkResult,
        ):

            self._operation_failed(
                "Μη έγκυρο αποτέλεσμα "
                "από το network service."
            )

            return

        current = (
            self.output_text
            .toPlainText()
        )

        if not self._streaming_operation:

            self.output_text.clear()

            self.output_text.append(
                f">>> {result.title}"
            )

            self.output_text.append(
                ""
            )

            self.output_text.append(
                result.output
            )

        elif (
            result.output
            and result.output not in current
        ):

            self.output_text.append(
                ""
            )

            self.output_text.append(
                result.output
            )

        if result.details:

            self.output_text.append(
                ""
            )

            self.output_text.append(
                f"Status: "
                f"{result.details}"
            )

        if result.success:

            self.output_status.setText(
                "Completed successfully"
            )

        else:

            self.output_status.setText(
                "Completed with errors"
            )

        self._set_running(
            False
        )

    # ------------------------------------------------------------------
    # Failed
    # ------------------------------------------------------------------

    def _operation_failed(
        self,
        error: str,
    ) -> None:

        self.output_text.clear()

        self.output_text.append(
            ">>> Network Tools"
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
        operation: str = "",
    ) -> None:

        for button in self._buttons:

            button.setEnabled(
                not running
            )

        self.host_input.setEnabled(
            not running
        )

        self.port_input.setEnabled(
            not running
        )

        if running:

            self.output_status.setText(
                f"Running "
                f"{self._operation_title(operation)}..."
            )

    def _thread_finished(
        self,
    ) -> None:

        self._thread = None

        self._worker = None

        self._streaming_operation = False

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
            self.output_text.textCursor().MoveOperation.End
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