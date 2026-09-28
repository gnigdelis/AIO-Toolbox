from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ToolCard(QFrame):
    """Reusable dashboard tool card."""

    def __init__(
        self,
        icon: str,
        title: str,
        description: str,
        object_name: str,
        navigation_key: str,
        on_click: Callable[[str], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.navigation_key = navigation_key
        self.on_click = on_click

        self.setObjectName(object_name)
        self.setMinimumHeight(125)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self._build_ui(
            icon,
            title,
            description,
        )

    def _build_ui(
        self,
        icon: str,
        title: str,
        description: str,
    ) -> None:
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        layout.setSpacing(8)

        # ------------------------------------------------------------
        # Top row
        # ------------------------------------------------------------

        top_row = QHBoxLayout()

        top_row.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        icon_label = QLabel(icon)

        icon_label.setObjectName(
            "toolCardIcon"
        )

        icon_label.setFixedSize(
            42,
            42,
        )

        icon_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        arrow = QPushButton("→")

        arrow.setObjectName(
            "toolCardArrow"
        )

        arrow.setFixedSize(
            30,
            30,
        )

        arrow.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        arrow.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        arrow.clicked.connect(
            self._handle_click
        )

        top_row.addWidget(
            icon_label
        )

        top_row.addStretch()

        top_row.addWidget(
            arrow
        )

        layout.addLayout(
            top_row
        )

        # ------------------------------------------------------------
        # Text
        # ------------------------------------------------------------

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "toolCardTitle"
        )

        description_label = QLabel(
            description
        )

        description_label.setObjectName(
            "toolCardDescription"
        )

        description_label.setWordWrap(
            True
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            description_label
        )

        layout.addStretch()

    def _handle_click(self) -> None:
        if self.on_click is not None:
            self.on_click(
                self.navigation_key
            )

    def mousePressEvent(
        self,
        event,
    ) -> None:
        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self._handle_click()

        super().mousePressEvent(
            event
        )


class QuickAccess(QWidget):
    """Quick-access tool cards displayed on the dashboard."""

    def __init__(
        self,
        on_navigate: Callable[[str], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.on_navigate = on_navigate

        self._build_ui()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        main_layout.setSpacing(
            10
        )

        # ------------------------------------------------------------
        # Section header
        # ------------------------------------------------------------

        header = QHBoxLayout()

        header.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        title = QLabel(
            "Quick Access"
        )

        title.setObjectName(
            "sectionTitle"
        )

        view_all = QPushButton(
            "View All Tools  →"
        )

        view_all.setObjectName(
            "viewAllButton"
        )

        view_all.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        view_all.clicked.connect(
            self._view_all_tools
        )

        header.addWidget(
            title
        )

        header.addStretch()

        header.addWidget(
            view_all
        )

        main_layout.addLayout(
            header
        )

        # ------------------------------------------------------------
        # Cards
        # ------------------------------------------------------------

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

        cards = [
            (
                "▣",
                "Network Tools",
                "Ping, Traceroute, etc.",
                "networkCard",
                "Network Tools",
            ),
            (
                "▱",
                "Remote Support",
                "Connect & Assist",
                "remoteCard",
                "Remote Support",
            ),
            (
                "▤",
                "Delete Pending Order",
                "Manage pending orders",
                "pendingOrderCard",
                "Delete Pending Order",
            ),
            (
                "◷",
                "Move Sales To Hist",
                "Move sales to history",
                "moveSalesHistCard",
                "Move Sales To Hist",
            ),
            (
                "▦",
                "Change Date",
                "Change restaurant date",
                "changeDateCard",
                "Change Date",
            ),
            (
                "⌘",
                "SQL Tools",
                "Database maintenance tools",
                "sqlToolsCard",
                "SQL Tools",
            ),
            (
                "◎",
                "myDATA Manager",
                "Manage myDATA operations",
                "myDataCard",
                "myDATA Manager",
            ),
            (
                "◈",
                "Diagnostics",
                "Logs & Troubleshooting",
                "diagnosticsCard",
                "Diagnostics",
            ),
        ]

        for index, card_data in enumerate(
            cards
        ):
            row = index // 4
            column = index % 4

            card = ToolCard(
                *card_data,
                on_click=self._navigate,
            )

            grid.addWidget(
                card,
                row,
                column,
            )

        for column in range(4):
            grid.setColumnStretch(
                column,
                1,
            )

        main_layout.addLayout(
            grid
        )

    # ------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------

    def _navigate(
        self,
        navigation_key: str,
    ) -> None:
        if self.on_navigate is not None:
            self.on_navigate(
                navigation_key
            )

    def _view_all_tools(self) -> None:
        if self.on_navigate is not None:
            self.on_navigate(
                "Network Tools"
            )