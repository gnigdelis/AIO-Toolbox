from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.v2.theme.svg_icons import pixmap


class WelcomeBanner(QFrame):
    """Locked AIO Toolbox welcome banner."""

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName(
            "welcomeBanner"
        )

        self.setFixedHeight(
            220
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            36,
            24,
            28,
            24,
        )

        layout.setSpacing(
            24
        )

        # ============================================================
        # LEFT SIDE
        # ============================================================

        text_layout = QVBoxLayout()

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        text_layout.setSpacing(
            4
        )

        eyebrow = QLabel(
            "W E L C O M E  T O"
        )

        eyebrow.setObjectName(
            "welcomeEyebrow"
        )

        title = QLabel(
            "AIO Toolbox"
        )

        title.setObjectName(
            "welcomeTitle"
        )

        subtitle = QLabel(
            "All the tools you need. In one place."
        )

        subtitle.setObjectName(
            "welcomeSubtitle"
        )

        description = QLabel(
            "Support. Maintain. Diagnose. Solve.\n"
            "Faster and easier."
        )

        description.setObjectName(
            "welcomeDescription"
        )

        text_layout.addWidget(
            eyebrow
        )

        text_layout.addWidget(
            title
        )

        text_layout.addWidget(
            subtitle
        )

        text_layout.addSpacing(
            8
        )

        text_layout.addWidget(
            description
        )

        text_layout.addStretch()

        layout.addLayout(
            text_layout,
            1,
        )

        # ============================================================
        # RIGHT SIDE
        # ============================================================

        visual = QFrame()

        visual.setObjectName(
            "welcomeVisual"
        )

        visual.setFixedSize(
            260,
            178,
        )

        visual_layout = QHBoxLayout(
            visual
        )

        visual_layout.setContentsMargins(
            18,
            12,
            12,
            12,
        )

        visual_layout.setSpacing(
            20
        )

        # ============================================================
        # TOOLBOX
        # ============================================================

        icon_box = QFrame()

        icon_box.setObjectName(
            "welcomeIconBox"
        )

        icon_box.setFixedSize(
            160,
            150,
        )

        icon_layout = QVBoxLayout(
            icon_box
        )

        icon_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        icon_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        icon_label = QLabel()

        icon_label.setObjectName(
            "welcomeIcon"
        )

        icon_label.setFixedSize(
            118,
            118,
        )

        icon_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        icon_label.setPixmap(
            pixmap(
                "toolbox",
                "#FFFFFF",
                72,
            )
        )

        icon_layout.addWidget(
            icon_label
        )

        visual_layout.addWidget(
            icon_box
        )

        # ============================================================
        # CHECKLIST
        # ============================================================

        checklist = QVBoxLayout()

        checklist.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        checklist.setSpacing(
            7
        )

        for text in (
            "Support",
            "Maintain",
            "Diagnose",
            "Solve",
        ):
            item = QLabel(
                f"●  {text}"
            )

            item.setObjectName(
                "welcomeCheck"
            )

            checklist.addWidget(
                item
            )

        tomorrow = QLabel(
            "A more productive\n"
            "tomorrow."
        )

        tomorrow.setObjectName(
            "welcomeTomorrow"
        )

        checklist.addSpacing(
            5
        )

        checklist.addWidget(
            tomorrow
        )

        checklist.addStretch()

        visual_layout.addLayout(
            checklist
        )

        layout.addWidget(
            visual
        )