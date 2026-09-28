from __future__ import annotations

import ctypes
import getpass
import os
import platform
import shutil
import socket
from collections.abc import Callable

from PySide6.QtCore import QByteArray, QPointF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.v2.theme.svg_icons import pixmap


class WelcomePanel(QFrame):
    """Locked AIO Toolbox welcome banner."""

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName(
            "welcomeBanner"
        )

        self.setMinimumHeight(
            218
        )

        self.setMaximumHeight(
            218
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
            38,
            20,
            26,
            18,
        )

        layout.setSpacing(
            22
        )

        # ==============================================================
        # LEFT TEXT
        # ==============================================================

        text_layout = QVBoxLayout()

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        text_layout.setSpacing(
            1
        )

        welcome = QLabel(
            "W E L C O M E  T O"
        )

        welcome.setObjectName(
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
            welcome
        )

        text_layout.addWidget(
            title
        )

        text_layout.addWidget(
            subtitle
        )

        text_layout.addSpacing(
            6
        )

        text_layout.addWidget(
            description
        )

        text_layout.addStretch(
            1
        )

        layout.addLayout(
            text_layout,
            1,
        )

        # ==============================================================
        # RIGHT VISUAL
        # ==============================================================

        visual = QFrame()

        visual.setObjectName(
            "welcomeVisual"
        )

        visual.setMinimumWidth(
            390
        )

        visual.setMaximumWidth(
            405
        )

        visual.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        visual_layout = QHBoxLayout(
            visual
        )

        visual_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        visual_layout.setSpacing(
            18
        )

        # ==============================================================
        # TOOLBOX BOX
        # ==============================================================

        toolbox_box = QFrame()

        toolbox_box.setObjectName(
            "welcomeIconBox"
        )

        toolbox_box.setFixedSize(
            265,
            178,
        )

        toolbox_layout = QVBoxLayout(
            toolbox_box
        )

        toolbox_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        toolbox_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        toolbox = QLabel()

        toolbox.setObjectName(
            "welcomeToolbox"
        )

        toolbox.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        toolbox.setPixmap(
            self._toolbox_pixmap(
                190,
                150,
            )
        )

        toolbox_layout.addWidget(
            toolbox
        )

        visual_layout.addWidget(
            toolbox_box,
            0,
            Qt.AlignmentFlag.AlignCenter,
        )

        # ==============================================================
        # CHECKLIST
        # ==============================================================

        checklist = QVBoxLayout()

        checklist.setContentsMargins(
            0,
            8,
            0,
            0,
        )

        checklist.setSpacing(
            8
        )

        for text in (
            "Support",
            "Maintain",
            "Diagnose",
            "Solve",
        ):
            row = QHBoxLayout()

            row.setContentsMargins(
                0,
                0,
                0,
                0,
            )

            row.setSpacing(
                8
            )

            check = QLabel(
                "✓"
            )

            check.setObjectName(
                "welcomeCheckCircle"
            )

            check.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            check.setFixedSize(
                20,
                20,
            )

            label = QLabel(
                text
            )

            label.setObjectName(
                "welcomeCheck"
            )

            row.addWidget(
                check
            )

            row.addWidget(
                label
            )

            row.addStretch(
                1
            )

            checklist.addLayout(
                row
            )

        tomorrow = QLabel(
            "A more productive\n"
            "tomorrow."
        )

        tomorrow.setObjectName(
            "welcomeTomorrow"
        )

        checklist.addSpacing(
            3
        )

        checklist.addWidget(
            tomorrow
        )

        checklist.addStretch(
            1
        )

        visual_layout.addLayout(
            checklist,
            1,
        )

        layout.addWidget(
            visual,
            0,
        )

    @staticmethod
    def _toolbox_pixmap(
        width: int,
        height: int,
    ) -> QPixmap:
        """
        Render the toolbox illustration into a QPixmap.

        QSvgRenderer requires QPainter when rendering to a pixmap.
        """

        svg = """
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="240"
            height="190"
            viewBox="0 0 240 190">

            <defs>

                <linearGradient
                    id="body"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1">

                    <stop
                        offset="0"
                        stop-color="#2F8CF2"/>

                    <stop
                        offset="1"
                        stop-color="#0965CC"/>

                </linearGradient>

                <linearGradient
                    id="lid"
                    x1="0"
                    y1="0"
                    x2="1"
                    y2="1">

                    <stop
                        offset="0"
                        stop-color="#63AEFF"/>

                    <stop
                        offset="1"
                        stop-color="#1475D9"/>

                </linearGradient>

                <linearGradient
                    id="handle"
                    x1="0"
                    y1="0"
                    x2="1"
                    y2="1">

                    <stop
                        offset="0"
                        stop-color="#3D98F5"/>

                    <stop
                        offset="1"
                        stop-color="#0E68CC"/>

                </linearGradient>

                <filter
                    id="shadow"
                    x="-30%"
                    y="-30%"
                    width="160%"
                    height="180%">

                    <feGaussianBlur
                        stdDeviation="5"/>

                </filter>

            </defs>

            <!-- shadow -->

            <ellipse
                cx="120"
                cy="167"
                rx="70"
                ry="10"
                fill="#7FAEDC"
                opacity=".32"
                filter="url(#shadow)"/>

            <!-- handle -->

            <path
                d="
                    M88 55
                    V39
                    C88 27 96 19 108 19
                    H132
                    C144 19 152 27 152 39
                    V55
                    H137
                    V41
                    C137 37 135 35 131 35
                    H109
                    C105 35 103 37 103 41
                    V55
                    Z
                "
                fill="url(#handle)"/>

            <!-- main body -->

            <path
                d="
                    M48 70
                    H192
                    V139
                    C192 150 185 157 174 157
                    H66
                    C55 157 48 150 48 139
                    Z
                "
                fill="url(#body)"/>

            <!-- lid -->

            <path
                d="
                    M42 70
                    L58 48
                    H182
                    L198 70
                    Z
                "
                fill="url(#lid)"/>

            <!-- lid highlight -->

            <path
                d="
                    M59 53
                    H181
                    L188 64
                    H51
                    Z
                "
                fill="#70B7FF"
                opacity=".32"/>

            <!-- front separation -->

            <path
                d="
                    M48 91
                    H192
                "
                stroke="#075DBB"
                stroke-width="4"
                opacity=".72"/>

            <!-- toolbox front highlight -->

            <path
                d="
                    M57 100
                    H183
                "
                stroke="#53A3F5"
                stroke-width="2"
                opacity=".5"/>

            <!-- center lock -->

            <rect
                x="101"
                y="86"
                width="38"
                height="43"
                rx="7"
                fill="#F8FBFF"/>

            <rect
                x="107"
                y="92"
                width="26"
                height="31"
                rx="4"
                fill="#E7F2FF"/>

            <rect
                x="111"
                y="100"
                width="18"
                height="16"
                rx="3"
                fill="#FFFFFF"/>

            <!-- lock vertical -->

            <path
                d="
                    M120 96
                    V119
                "
                stroke="#D2E4F8"
                stroke-width="3"/>

            <!-- side highlights -->

            <path
                d="
                    M58 77
                    V135
                "
                stroke="#69B1FA"
                stroke-width="2"
                opacity=".28"/>

            <path
                d="
                    M182 77
                    V135
                "
                stroke="#075DBB"
                stroke-width="2"
                opacity=".25"/>

        </svg>
        """

        renderer = QSvgRenderer(
            QByteArray(
                svg.encode(
                    "utf-8"
                )
            )
        )

        result = QPixmap(
            width,
            height,
        )

        result.fill(
            Qt.GlobalColor.transparent
        )

        painter = QPainter(
            result
        )

        try:
            renderer.render(
                painter
            )
        finally:
            painter.end()

        return result

    # ==============================================================
    # WAVE BACKGROUND
    # ==============================================================

    def paintEvent(
        self,
        event,
    ) -> None:
        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        rect = self.rect()

        # ----------------------------------------------------------
        # Main background
        # ----------------------------------------------------------

        painter.setPen(
            QPen(
                QColor("#CFE4FA"),
                1,
            )
        )

        painter.setBrush(
            QBrush(
                QColor("#E8F5FF")
            )
        )

        painter.drawRoundedRect(
            rect.adjusted(
                0,
                0,
                -1,
                -1,
            ),
            15,
            15,
        )

        # ----------------------------------------------------------
        # Large soft wave
        # ----------------------------------------------------------

        wave = QPainterPath()

        wave.moveTo(
            QPointF(
                0,
                self.height() * 0.66,
            )
        )

        wave.cubicTo(
            QPointF(
                self.width() * 0.20,
                self.height() * 0.58,
            ),
            QPointF(
                self.width() * 0.32,
                self.height() * 0.27,
            ),
            QPointF(
                self.width() * 0.52,
                self.height() * 0.25,
            ),
        )

        wave.cubicTo(
            QPointF(
                self.width() * 0.69,
                self.height() * 0.22,
            ),
            QPointF(
                self.width() * 0.84,
                self.height() * 0.56,
            ),
            QPointF(
                self.width(),
                self.height() * 0.36,
            ),
        )

        wave.lineTo(
            QPointF(
                self.width(),
                self.height(),
            )
        )

        wave.lineTo(
            QPointF(
                0,
                self.height(),
            )
        )

        wave.closeSubpath()

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QBrush(
                QColor(
                    205,
                    229,
                    250,
                    95,
                )
            )
        )

        painter.drawPath(
            wave
        )

        # ----------------------------------------------------------
        # Second softer wave
        # ----------------------------------------------------------

        wave2 = QPainterPath()

        wave2.moveTo(
            QPointF(
                0,
                self.height() * 0.88,
            )
        )

        wave2.cubicTo(
            QPointF(
                self.width() * 0.24,
                self.height() * 0.76,
            ),
            QPointF(
                self.width() * 0.38,
                self.height() * 0.42,
            ),
            QPointF(
                self.width() * 0.60,
                self.height() * 0.44,
            )
        )

        wave2.cubicTo(
            QPointF(
                self.width() * 0.78,
                self.height() * 0.44,
            ),
            QPointF(
                self.width() * 0.90,
                self.height() * 0.68,
            ),
            QPointF(
                self.width(),
                self.height() * 0.56,
            )
        )

        wave2.lineTo(
            QPointF(
                self.width(),
                self.height(),
            )
        )

        wave2.lineTo(
            QPointF(
                0,
                self.height(),
            )
        )

        wave2.closeSubpath()

        painter.setBrush(
            QBrush(
                QColor(
                    191,
                    220,
                    247,
                    65,
                )
            )
        )

        painter.drawPath(
            wave2
        )

        painter.end()

        super().paintEvent(
            event
        )


class DashboardPage(QWidget):
    """Main AIO Toolbox dashboard."""

    def __init__(
        self,
        on_navigate: Callable[
            [str],
            None,
        ]
        | None = None,
        parent: QWidget | None = None,
    ) -> None:

        super().__init__(
            parent
        )

        self.on_navigate = (
            on_navigate
        )

        self.setObjectName(
            "dashboardPage"
        )

        self._build_ui()

    # ==================================================================
    # RESIZE
    # ==================================================================

    def resizeEvent(
        self,
        event,
    ) -> None:

        super().resizeEvent(
            event
        )

        self._apply_responsive_layout()

    # ==================================================================
    # BUILD UI
    # ==================================================================

    def _build_ui(
        self,
    ) -> None:

        outer = QVBoxLayout(
            self
        )

        outer.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        outer.setSpacing(
            0
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        content = QWidget()

        content.setObjectName(
            "dashboardContent"
        )

        layout = QVBoxLayout(
            content
        )

        self._content_layout = (
            layout
        )

        layout.setContentsMargins(
            28,
            24,
            28,
            28,
        )

        layout.setSpacing(
            16
        )

        self._welcome_panel = (
            self._create_welcome_panel()
        )

        self._system_panel = (
            self._create_system_overview()
        )

        self._activity_panel = (
            self._create_recent_activity()
        )

        layout.addWidget(
            self._welcome_panel
        )

        layout.addWidget(
            self._system_panel
        )

        layout.addWidget(
            self._activity_panel
        )

        layout.addStretch(
            1
        )

        scroll.setWidget(
            content
        )

        outer.addWidget(
            scroll
        )

        self._apply_dashboard_style()

    # ==================================================================
    # WELCOME
    # ==================================================================

    def _create_welcome_panel(
        self,
    ) -> WelcomePanel:

        panel = WelcomePanel()

        self._welcome_panel_widget = (
            panel
        )

        return panel

    # ==================================================================
    # SYSTEM OVERVIEW
    # ==================================================================

    def _create_system_overview(
        self,
    ) -> QFrame:

        panel = QFrame()

        panel.setObjectName(
            "infoPanel"
        )

        panel.setMinimumHeight(
            306
        )

        panel.setMaximumHeight(
            306
        )

        panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(
            panel
        )

        layout.setContentsMargins(
            24,
            16,
            24,
            18,
        )

        layout.setSpacing(
            7
        )

        header = QHBoxLayout()

        header.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        header.setSpacing(
            9
        )

        icon_label = QLabel()

        icon_label.setPixmap(
            pixmap(
                "monitor",
                "#2F80ED",
                21,
            )
        )

        icon_label.setFixedSize(
            24,
            24,
        )

        title = QLabel(
            "System Overview"
        )

        title.setObjectName(
            "panelTitle"
        )

        header.addWidget(
            icon_label
        )

        header.addWidget(
            title
        )

        header.addStretch(
            1
        )

        live = QHBoxLayout()

        live.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        live.setSpacing(
            7
        )

        dot = QLabel(
            "●"
        )

        dot.setObjectName(
            "liveDot"
        )

        live.addWidget(
            dot
        )

        live_text = QLabel(
            "Live system information"
        )

        live_text.setObjectName(
            "liveStatus"
        )

        self._live_status = (
            live_text
        )

        self._live_status_dot = (
            dot
        )

        live.addWidget(
            live_text
        )

        header.addLayout(
            live
        )

        layout.addLayout(
            header
        )

        separator = QFrame()

        separator.setFrameShape(
            QFrame.Shape.HLine
        )

        separator.setObjectName(
            "panelSeparator"
        )

        separator.setFixedHeight(
            1
        )

        layout.addWidget(
            separator
        )

        self._info_labels = []

        rows = [
            (
                "monitor",
                "Computer Name",
                self._computer_name(),
            ),
            (
                "windows",
                "Operating System",
                self._operating_system(),
            ),
            (
                "user",
                "User",
                self._current_user(),
            ),
            (
                "cpu",
                "CPU",
                self._processor(),
            ),
            (
                "memory",
                "Memory",
                self._memory(),
            ),
            (
                "drive",
                "System Drive",
                self._system_drive(),
            ),
            (
                "clock",
                "Uptime",
                self._uptime(),
            ),
        ]

        for (
            icon_name,
            label,
            value,
        ) in rows:

            layout.addWidget(
                self._info_row(
                    icon_name,
                    label,
                    value,
                )
            )

        layout.addStretch(
            1
        )

        return panel

    # ==================================================================
    # INFO ROW
    # ==================================================================

    def _info_row(
        self,
        icon_name: str,
        label_text: str,
        value_text: str,
    ) -> QWidget:

        row = QWidget()

        row.setMinimumHeight(
            30
        )

        row_layout = QHBoxLayout(
            row
        )

        row_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        row_layout.setSpacing(
            9
        )

        icon_label = QLabel()

        icon_label.setFixedSize(
            22,
            22,
        )

        icon_label.setPixmap(
            pixmap(
                icon_name,
                "#2F80ED",
                18,
            )
        )

        icon_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        label = QLabel(
            label_text
        )

        label.setObjectName(
            "panelLabel"
        )

        label.setFixedWidth(
            190
        )

        self._info_labels.append(
            label
        )

        value = QLabel(
            value_text
        )

        value.setObjectName(
            "panelValue"
        )

        value.setWordWrap(
            True
        )

        value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        row_layout.addWidget(
            icon_label
        )

        row_layout.addWidget(
            label
        )

        row_layout.addWidget(
            value,
            1,
        )

        return row

    # ==================================================================
    # RECENT ACTIVITY
    # ==================================================================

    def _create_recent_activity(
        self,
    ) -> QFrame:

        panel = QFrame()

        panel.setObjectName(
            "infoPanel"
        )

        panel.setMinimumHeight(
            210
        )

        panel.setMaximumHeight(
            210
        )

        panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(
            panel
        )

        layout.setContentsMargins(
            24,
            16,
            24,
            16,
        )

        layout.setSpacing(
            5
        )

        header = QHBoxLayout()

        header.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        header.setSpacing(
            9
        )

        icon_label = QLabel()

        icon_label.setPixmap(
            pixmap(
                "activity",
                "#2F80ED",
                22,
            )
        )

        icon_label.setFixedSize(
            24,
            24,
        )

        title = QLabel(
            "Recent Activity"
        )

        title.setObjectName(
            "panelTitle"
        )

        header.addWidget(
            icon_label
        )

        header.addWidget(
            title
        )

        header.addStretch(
            1
        )

        logs = QLabel(
            "View Logs  →"
        )

        logs.setObjectName(
            "viewLogs"
        )

        self._view_logs = logs

        header.addWidget(
            logs
        )

        layout.addLayout(
            header
        )

        separator = QFrame()

        separator.setFrameShape(
            QFrame.Shape.HLine
        )

        separator.setObjectName(
            "panelSeparator"
        )

        separator.setFixedHeight(
            1
        )

        layout.addWidget(
            separator
        )

        events = (
            (
                "NOW",
                "Dashboard loaded successfully",
            ),
            (
                "LIVE",
                "System information read from Windows",
            ),
            (
                "LIVE",
                "System drive information retrieved",
            ),
            (
                "LIVE",
                "Windows uptime retrieved",
            ),
        )

        for index, (
            time_text,
            message,
        ) in enumerate(
            events
        ):

            layout.addWidget(
                self._activity_row(
                    time_text,
                    message,
                )
            )

            if index < (
                len(events) - 1
            ):

                line = QFrame()

                line.setFrameShape(
                    QFrame.Shape.HLine
                )

                line.setObjectName(
                    "activitySeparator"
                )

                line.setFixedHeight(
                    1
                )

                layout.addWidget(
                    line
                )

        layout.addStretch(
            1
        )

        return panel

    # ==================================================================
    # ACTIVITY ROW
    # ==================================================================

    def _activity_row(
        self,
        time_text: str,
        message: str,
    ) -> QWidget:

        row = QWidget()

        row.setMinimumHeight(
            31
        )

        row_layout = QHBoxLayout(
            row
        )

        row_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        row_layout.setSpacing(
            10
        )

        dot = QLabel(
            "●"
        )

        dot.setObjectName(
            "activityIndicator"
        )

        dot.setFixedWidth(
            18
        )

        time_label = QLabel(
            time_text
        )

        time_label.setObjectName(
            "activityTime"
        )

        time_label.setFixedWidth(
            78
        )

        message_label = QLabel(
            message
        )

        message_label.setObjectName(
            "activityDescription"
        )

        row_layout.addWidget(
            dot
        )

        row_layout.addWidget(
            time_label
        )

        row_layout.addWidget(
            message_label,
            1,
        )

        return row

    # ==================================================================
    # RESPONSIVE
    # ==================================================================

    def _apply_responsive_layout(
        self,
    ) -> None:

        if not hasattr(
            self,
            "_content_layout",
        ):
            return

        compact = (
            self.width()
            <= 1099
        )

        if compact:

            self._content_layout.setContentsMargins(
                18,
                16,
                18,
                20,
            )

            self._content_layout.setSpacing(
                14
            )

            # ----------------------------------------------------------
            # Welcome
            # ----------------------------------------------------------

            self._welcome_panel_widget.setMinimumHeight(
                190
            )

            self._welcome_panel_widget.setMaximumHeight(
                190
            )

            welcome_layout = (
                self._welcome_panel_widget.layout()
            )

            if welcome_layout is not None:

                welcome_layout.setContentsMargins(
                    22,
                    16,
                    16,
                    16,
                )

                welcome_layout.setSpacing(
                    12
                )

            # Find the visual area.
            visual = (
                self._welcome_panel_widget.findChild(
                    QFrame,
                    "welcomeVisual",
                )
            )

            if visual is not None:

                visual.setMinimumWidth(
                    250
                )

                visual.setMaximumWidth(
                    265
                )

                visual_layout = (
                    visual.layout()
                )

                if visual_layout is not None:
                    visual_layout.setSpacing(
                        10
                    )

            icon_box = (
                self._welcome_panel_widget.findChild(
                    QFrame,
                    "welcomeIconBox",
                )
            )

            if icon_box is not None:

                icon_box.setFixedSize(
                    160,
                    150,
                )

            toolbox = (
                self._welcome_panel_widget.findChild(
                    QLabel,
                    "welcomeToolbox",
                )
            )

            if toolbox is not None:

                toolbox.setPixmap(
                    WelcomePanel._toolbox_pixmap(
                        135,
                        110,
                    )
                )

            # ----------------------------------------------------------
            # System overview
            # ----------------------------------------------------------

            self._system_panel.setMinimumHeight(
                292
            )

            self._system_panel.setMaximumHeight(
                292
            )

            self._live_status.setVisible(
                False
            )

            self._live_status_dot.setVisible(
                False
            )

            for label in self._info_labels:

                label.setFixedWidth(
                    125
                )

            # ----------------------------------------------------------
            # Recent activity
            # ----------------------------------------------------------

            self._activity_panel.setMinimumHeight(
                190
            )

            self._activity_panel.setMaximumHeight(
                190
            )

            self._view_logs.setVisible(
                False
            )

        else:

            self._content_layout.setContentsMargins(
                28,
                24,
                28,
                28,
            )

            self._content_layout.setSpacing(
                16
            )

            # ----------------------------------------------------------
            # Welcome
            # ----------------------------------------------------------

            self._welcome_panel_widget.setMinimumHeight(
                218
            )

            self._welcome_panel_widget.setMaximumHeight(
                218
            )

            welcome_layout = (
                self._welcome_panel_widget.layout()
            )

            if welcome_layout is not None:

                welcome_layout.setContentsMargins(
                    38,
                    20,
                    26,
                    18,
                )

                welcome_layout.setSpacing(
                    22
                )

            visual = (
                self._welcome_panel_widget.findChild(
                    QFrame,
                    "welcomeVisual",
                )
            )

            if visual is not None:

                visual.setMinimumWidth(
                    390
                )

                visual.setMaximumWidth(
                    405
                )

                visual_layout = (
                    visual.layout()
                )

                if visual_layout is not None:
                    visual_layout.setSpacing(
                        18
                    )

            icon_box = (
                self._welcome_panel_widget.findChild(
                    QFrame,
                    "welcomeIconBox",
                )
            )

            if icon_box is not None:

                icon_box.setFixedSize(
                    265,
                    178,
                )

            toolbox = (
                self._welcome_panel_widget.findChild(
                    QLabel,
                    "welcomeToolbox",
                )
            )

            if toolbox is not None:

                toolbox.setPixmap(
                    WelcomePanel._toolbox_pixmap(
                        190,
                        150,
                    )
                )

            # ----------------------------------------------------------
            # System overview
            # ----------------------------------------------------------

            self._system_panel.setMinimumHeight(
                306
            )

            self._system_panel.setMaximumHeight(
                306
            )

            self._live_status.setVisible(
                True
            )

            self._live_status_dot.setVisible(
                True
            )

            for label in self._info_labels:

                label.setFixedWidth(
                    190
                )

            # ----------------------------------------------------------
            # Recent activity
            # ----------------------------------------------------------

            self._activity_panel.setMinimumHeight(
                210
            )

            self._activity_panel.setMaximumHeight(
                210
            )

            self._view_logs.setVisible(
                True
            )

    # ==================================================================
    # SYSTEM INFORMATION
    # ==================================================================

    @staticmethod
    def _computer_name() -> str:

        try:
            return socket.gethostname()

        except Exception:
            return "Unknown"

    @staticmethod
    def _windows_name() -> str:

        try:

            import winreg

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
            ) as key:

                product_name = str(
                    winreg.QueryValueEx(
                        key,
                        "ProductName",
                    )[0]
                )

                try:
                    build_number = int(
                        winreg.QueryValueEx(
                            key,
                            "CurrentBuildNumber",
                        )[0]
                    )
                except (TypeError, ValueError, OSError):
                    build_number = 0

                # Windows 11 may report "Windows 10"
                # in ProductName for compatibility.
                if (
                    build_number >= 22000
                    and product_name.startswith("Windows 10")
                ):
                    product_name = product_name.replace(
                        "Windows 10",
                        "Windows 11",
                        1,
                    )

                return product_name

        except Exception:
            return ""

    @classmethod
    def _operating_system(
        cls,
    ) -> str:

        try:

            if (
                platform.system()
                == "Windows"
            ):

                name = cls._windows_name()

                release = (
                    platform.release()
                )

                if name:

                    return name

                return (
                    f"Windows "
                    f"{release}"
                )

            return (
                f"{platform.system()} "
                f"{platform.release()}"
            )

        except Exception:
            return "Unknown"

    @staticmethod
    def _current_user() -> str:

        try:
            return getpass.getuser()

        except Exception:

            return os.environ.get(
                "USERNAME",
                "Unknown",
            )

    @staticmethod
    def _processor() -> str:

        try:

            # platform.processor() on modern Windows installations
            # can return only a generic Intel identifier.
            # Use Windows' ProcessorNameString for the actual
            # commercial CPU name when available.
            if platform.system() == "Windows":

                import winreg

                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
                ) as key:

                    processor_name = str(
                        winreg.QueryValueEx(
                            key,
                            "ProcessorNameString",
                        )[0]
                    ).strip()

                    if processor_name:
                        return processor_name

            value = (
                platform.processor()
            )

            if value:
                return value

            return (
                platform.machine()
                or
                f"{os.cpu_count() or 1} logical processors"
            )

        except Exception:

            try:

                value = (
                    platform.processor()
                )

                if value:
                    return value

            except Exception:
                pass

            return (
                platform.machine()
                or
                f"{os.cpu_count() or 1} logical processors"
            )

    @staticmethod
    def _memory() -> str:

        try:

            class MEMORYSTATUSEX(
                ctypes.Structure
            ):

                _fields_ = [
                    (
                        "dwLength",
                        ctypes.c_ulong,
                    ),
                    (
                        "dwMemoryLoad",
                        ctypes.c_ulong,
                    ),
                    (
                        "ullTotalPhys",
                        ctypes.c_ulonglong,
                    ),
                    (
                        "ullAvailPhys",
                        ctypes.c_ulonglong,
                    ),
                    (
                        "ullTotalPageFile",
                        ctypes.c_ulonglong,
                    ),
                    (
                        "ullAvailPageFile",
                        ctypes.c_ulonglong,
                    ),
                    (
                        "ullTotalVirtual",
                        ctypes.c_ulonglong,
                    ),
                    (
                        "ullAvailVirtual",
                        ctypes.c_ulonglong,
                    ),
                    (
                        "ullAvailExtendedVirtual",
                        ctypes.c_ulonglong,
                    ),
                ]

            status = (
                MEMORYSTATUSEX()
            )

            status.dwLength = (
                ctypes.sizeof(
                    MEMORYSTATUSEX
                )
            )

            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(
                ctypes.byref(
                    status
                )
            ):
                return "Unknown"

            total_gb = (
                status.ullTotalPhys
                / (
                    1024 ** 3
                )
            )

            return (
                f"{total_gb:.1f} GB total "
                f"({status.dwMemoryLoad}% used)"
            )

        except Exception:
            return "Unknown"

    @staticmethod
    def _system_drive() -> str:

        try:

            drive = (
                os.environ.get(
                    "SystemDrive",
                    "C:",
                )
                + "\\"
            )

            total, used, free = (
                shutil.disk_usage(
                    drive
                )
            )

            total_gb = (
                total
                / (
                    1024 ** 3
                )
            )

            free_gb = (
                free
                / (
                    1024 ** 3
                )
            )

            used_percent = (
                used
                / total
                * 100
                if total
                else 0
            )

            return (
                f"{drive}  •  "
                f"{free_gb:.1f} GB free of "
                f"{total_gb:.1f} GB "
                f"({used_percent:.0f}% used)"
            )

        except Exception:
            return "Unknown"

    @staticmethod
    def _uptime() -> str:

        try:

            if (
                platform.system()
                != "Windows"
            ):
                return "Unavailable"

            milliseconds = (
                ctypes.windll.kernel32.GetTickCount64()
            )

            seconds = int(
                milliseconds
                / 1000
            )

            days, remainder = divmod(
                seconds,
                86400,
            )

            hours, remainder = divmod(
                remainder,
                3600,
            )

            minutes, _ = divmod(
                remainder,
                60,
            )

            if days:

                return (
                    f"{days} day"
                    f"{'s' if days != 1 else ''}, "
                    f"{hours} hour"
                    f"{'s' if hours != 1 else ''}, "
                    f"{minutes} min"
                )

            if hours:

                return (
                    f"{hours} hour"
                    f"{'s' if hours != 1 else ''}, "
                    f"{minutes} min"
                )

            return (
                f"{minutes} min"
            )

        except Exception:
            return "Unknown"

    # ==================================================================
    # STYLE
    # ==================================================================

    def _apply_dashboard_style(
        self,
    ) -> None:

        self.setStyleSheet(
            """
            #dashboardPage,
            #dashboardContent {
                background: #F7F9FC;
            }

            /* ========================================================
               WELCOME BANNER
               ======================================================== */

            #welcomeBanner {
                border: 1px solid #DCE6F1;
                border-radius: 10px;
            }

            #welcomeEyebrow {
                color: #1877E8;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 3px;
            }

            #welcomeTitle {
                color: #103C78;
                font-size: 40px;
                font-weight: 700;
            }

            #welcomeSubtitle {
                color: #123E7A;
                font-size: 20px;
                font-weight: 500;
            }

            #welcomeDescription {
                color: #6080A8;
                font-size: 14px;
                font-weight: 500;
            }

            #welcomeVisual {
                background: transparent;
                border: none;
            }

            #welcomeIconBox {
                background: rgba(
                    226,
                    241,
                    255,
                    0.68
                );

                border: 1px solid #C7E0F8;
                border-radius: 10px;
            }

            #welcomeToolbox {
                background: transparent;
                border: none;
            }

            #welcomeCheckCircle {
                background: #2585EC;
                color: white;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 700;
            }

            #welcomeCheck {
                color: #5276A4;
                font-size: 14px;
                font-weight: 500;
            }

            #welcomeTomorrow {
                color: #75A1CE;
                font-size: 12px;
                font-style: italic;
            }

            /* ========================================================
               SYSTEM OVERVIEW
               ======================================================== */

            #infoPanel {
                background: #FFFFFF;
                border: 1px solid #DCE6F1;
                border-radius: 10px;
            }

            #panelTitle {
                color: #123D73;
                font-size: 18px;
                font-weight: 700;
            }

            #panelLabel {
                color: #6884A8;
                font-size: 14px;
            }

            #panelValue {
                color: #163F78;
                font-size: 14px;
                font-weight: 500;
            }

            #panelSeparator,
            #activitySeparator {
                background: #E1EAF3;
                border: none;
            }

            #liveDot {
                color: #17B968;
                font-size: 10px;
            }

            #liveStatus {
                color: #17A963;
                font-size: 12px;
                font-weight: 600;
            }

            /* ========================================================
               RECENT ACTIVITY
               ======================================================== */

            #viewLogs {
                color: #1877E8;
                font-size: 14px;
                font-weight: 600;
            }

            #activityIndicator {
                color: #18B968;
                font-size: 10px;
            }

            #activityTime {
                color: #52749D;
                font-size: 13px;
                font-weight: 600;
            }

            #activityDescription {
                color: #405B7B;
                font-size: 14px;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 4px 2px 4px 2px;
            }

            QScrollBar::handle:vertical {
                background: #C7D4E2;
                border-radius: 4px;
                min-height: 40px;
            }

            QScrollBar::handle:vertical:hover {
                background: #AEBECD;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )