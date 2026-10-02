from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.logging.app_logger import log_path


class LogsPage(QWidget):
    """
    Central application log viewer.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName(
            "logsPage"
        )

        self._build_ui()
        self._load_logs()

        self._timer = QTimer(self)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(
            self._load_logs
        )
        self._timer.start()

    # ================================================================
    # UI
    # ================================================================

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        root.setContentsMargins(
            28,
            24,
            28,
            28,
        )

        root.setSpacing(
            16
        )

        # ------------------------------------------------------------
        # Header
        # ------------------------------------------------------------

        header = QHBoxLayout()

        header.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        title_layout = QVBoxLayout()

        title_layout.setSpacing(
            4
        )

        title = QLabel(
            "Logs"
        )

        title.setObjectName(
            "logsTitle"
        )

        subtitle = QLabel(
            "Application activity and operation history"
        )

        subtitle.setObjectName(
            "logsSubtitle"
        )

        title_layout.addWidget(
            title
        )

        title_layout.addWidget(
            subtitle
        )

        header.addLayout(
            title_layout
        )

        header.addStretch(
            1
        )

        self.refresh_button = QPushButton(
            "REFRESH"
        )

        self.refresh_button.setObjectName(
            "logsRefreshButton"
        )

        self.refresh_button.clicked.connect(
            self._load_logs
        )

        self.clear_button = QPushButton(
            "CLEAR LOGS"
        )

        self.clear_button.setObjectName(
            "logsClearButton"
        )

        self.clear_button.clicked.connect(
            self._clear_logs
        )

        header.addWidget(
            self.refresh_button
        )

        header.addWidget(
            self.clear_button
        )

        root.addLayout(
            header
        )

        # ------------------------------------------------------------
        # Status
        # ------------------------------------------------------------

        status_frame = QFrame()

        status_frame.setObjectName(
            "logsStatusFrame"
        )

        status_layout = QHBoxLayout(
            status_frame
        )

        status_layout.setContentsMargins(
            14,
            10,
            14,
            10,
        )

        self.status_label = QLabel(
            "Ready"
        )

        self.status_label.setObjectName(
            "logsStatus"
        )

        status_layout.addWidget(
            self.status_label
        )

        status_layout.addStretch(
            1
        )

        root.addWidget(
            status_frame
        )

        # ------------------------------------------------------------
        # Log viewer
        # ------------------------------------------------------------

        self.log_viewer = QPlainTextEdit()

        self.log_viewer.setObjectName(
            "logsViewer"
        )

        self.log_viewer.setReadOnly(
            True
        )

        self.log_viewer.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.NoWrap
        )

        root.addWidget(
            self.log_viewer,
            1,
        )

        self._apply_style()

    # ================================================================
    # LOG FILE
    # ================================================================

    def _load_logs(self) -> None:
        path = Path(
            log_path()
        )

        if not path.exists():
            self.log_viewer.clear()

            self.status_label.setText(
                "No log entries yet."
            )

            return

        try:
            content = path.read_text(
                encoding="utf-8"
            )

            self.log_viewer.setPlainText(
                content
            )

            cursor = (
                self.log_viewer.textCursor()
            )

            cursor.movePosition(
                cursor.MoveOperation.End
            )

            self.log_viewer.setTextCursor(
                cursor
            )

            line_count = (
                len(
                    content.splitlines()
                )
                if content
                else 0
            )

            self.status_label.setText(
                f"{line_count} log entries  •  "
                f"{path}"
            )

        except Exception as exc:
            self.status_label.setText(
                f"Unable to read log file: {exc}"
            )

    # ================================================================
    # CLEAR
    # ================================================================

    def _clear_logs(self) -> None:
        path = Path(
            log_path()
        )

        try:
            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            path.write_text(
                "",
                encoding="utf-8",
            )

            self.log_viewer.clear()

            self.status_label.setText(
                "Logs cleared."
            )

        except Exception as exc:
            self.status_label.setText(
                f"Unable to clear logs: {exc}"
            )

    # ================================================================
    # STYLE
    # ================================================================

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            #logsPage {
                background: #F7F9FC;
            }

            #logsTitle {
                color: #103C78;
                font-size: 30px;
                font-weight: 700;
            }

            #logsSubtitle {
                color: #6B83A3;
                font-size: 14px;
                font-weight: 500;
            }

            #logsStatusFrame {
                background: #FFFFFF;
                border: 1px solid #DCE6F1;
                border-radius: 8px;
            }

            #logsStatus {
                color: #607A9D;
                font-size: 12px;
                font-weight: 500;
            }

            #logsViewer {
                background: #101820;
                color: #D9E7F5;
                border: 1px solid #D6E1ED;
                border-radius: 10px;
                padding: 12px;
                font-family: Consolas;
                font-size: 12px;
            }

            #logsRefreshButton,
            #logsClearButton {
                min-height: 38px;
                padding-left: 18px;
                padding-right: 18px;
                border-radius: 7px;
                font-size: 12px;
                font-weight: 700;
            }

            #logsRefreshButton {
                background: #1877E8;
                color: white;
                border: none;
            }

            #logsRefreshButton:hover {
                background: #1468CC;
            }

            #logsClearButton {
                background: #FFFFFF;
                color: #D64545;
                border: 1px solid #E2CACA;
            }

            #logsClearButton:hover {
                background: #FFF5F5;
            }
            """
        )
