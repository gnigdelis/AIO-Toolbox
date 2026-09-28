from __future__ import annotations

import ctypes
import getpass
import os
import platform
import shutil
import socket
from collections.abc import Callable

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QPainter, QPixmap
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


class DashboardPage(QWidget):
    """Main AIO Toolbox dashboard."""

    def __init__(
        self,
        on_navigate: Callable[[str], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.on_navigate = on_navigate

        self.setObjectName(
            "dashboardPage"
        )

        self._build_ui()

    # ==================================================================
    # RESPONSIVE RESIZE
    # ==================================================================

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

        self._apply_responsive_layout()

    # ==================================================================
    # BUILD UI
    # ==================================================================

    def _build_ui(self) -> None:
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

        self._content_layout = layout

        layout.setContentsMargins(
            26,
            18,
            26,
            24,
        )

        layout.setSpacing(
            14
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
    # WELCOME BANNER
    # ==================================================================

    def _create_welcome_panel(self) -> QFrame:
        panel = QFrame()

        panel.setObjectName(
            "welcomeBanner"
        )

        panel.setMinimumHeight(
            218
        )

        panel.setMaximumHeight(
            218
        )

        panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QHBoxLayout(
            panel
        )

        layout.setContentsMargins(
            36,
            22,
            28,
            22,
        )

        layout.setSpacing(
            22
        )

        # --------------------------------------------------------------
        # Left text
        # --------------------------------------------------------------

        text = QVBoxLayout()

        text.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        text.setSpacing(
            2
        )

        eyebrow = QLabel(
            "WELCOME TO"
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
            "Support. Maintain. Diagnose. Solve."
        )

        description.setObjectName(
            "welcomeDescription"
        )

        description2 = QLabel(
            "Faster and easier."
        )

        description2.setObjectName(
            "welcomeDescription"
        )

        text.addWidget(
            eyebrow
        )

        text.addWidget(
            title
        )

        text.addSpacing(
            2
        )

        text.addWidget(
            subtitle
        )

        text.addSpacing(
            8
        )

        text.addWidget(
            description
        )

        text.addWidget(
            description2
        )

        text.addStretch(
            1
        )

        layout.addLayout(
            text,
            1
        )

        # --------------------------------------------------------------
        # Right visual area
        # --------------------------------------------------------------

        visual = QFrame()

        self._welcome_visual = visual

        visual.setObjectName(
            "welcomeVisualArea"
        )

        visual.setMinimumWidth(
            500
        )

        visual.setMaximumWidth(
            520
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
            20
        )

        # --------------------------------------------------------------
        # Toolbox illustration
        # --------------------------------------------------------------

        illustration_box = QFrame()

        self._welcome_illustration_box = (
            illustration_box
        )

        illustration_box.setObjectName(
            "welcomeIconBox"
        )

        illustration_box.setFixedSize(
            260,
            176
        )

        illustration_layout = QVBoxLayout(
            illustration_box
        )

        illustration_layout.setContentsMargins(
            18,
            10,
            18,
            10,
        )

        illustration_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        illustration = QLabel()

        illustration.setObjectName(
            "welcomeIllustration"
        )

        illustration.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        illustration.setPixmap(
            self._toolbox_pixmap(
                150,
                120,
            )
        )

        illustration_layout.addWidget(
            illustration
        )

        visual_layout.addWidget(
            illustration_box,
            0,
            Qt.AlignmentFlag.AlignCenter,
        )

        # --------------------------------------------------------------
        # Checklist
        # --------------------------------------------------------------

        checklist = QVBoxLayout()

        self._welcome_checklist_layout = (
            checklist
        )

        checklist.setContentsMargins(
            0,
            8,
            0,
            0,
        )

        checklist.setSpacing(
            8
        )

        for item in (
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
                "●"
            )

            check.setObjectName(
                "welcomeCheckDot"
            )

            check.setFixedWidth(
                16
            )

            label = QLabel(
                item
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
            "A more productive\ntomorrow."
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
            1
        )

        layout.addWidget(
            visual,
            0
        )

        return panel

    # ==================================================================
    # TOOLBOX ILLUSTRATION
    # ==================================================================

    @staticmethod
    def _toolbox_pixmap(
        width: int,
        height: int,
    ) -> QPixmap:
        svg = f'''
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="220"
            height="170"
            viewBox="0 0 220 170">

            <defs>

                <linearGradient
                    id="box"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1">

                    <stop
                        offset="0"
                        stop-color="#2F86EA"/>

                    <stop
                        offset="1"
                        stop-color="#1164C7"/>

                </linearGradient>

                <linearGradient
                    id="top"
                    x1="0"
                    y1="0"
                    x2="1"
                    y2="1">

                    <stop
                        offset="0"
                        stop-color="#58A4FF"/>

                    <stop
                        offset="1"
                        stop-color="#1973D8"/>

                </linearGradient>

            </defs>

            <ellipse
                cx="110"
                cy="148"
                rx="76"
                ry="9"
                fill="#B9D3EE"
                opacity=".55"/>

            <path
                d="M48 62h124v68c0 8-6 14-14 14H62c-8 0-14-6-14-14z"
                fill="url(#box)"/>

            <path
                d="M48 62l18-24h88l18 24z"
                fill="url(#top)"/>

            <path
                d="M78 39V28c0-11 7-17 17-17h30c10 0 17 6 17 17v11h-15V29c0-3-2-5-5-5H95c-3 0-5 2-5 5v10z"
                fill="#1468C9"/>

            <path
                d="M99 68h22v50H99z"
                fill="#F7FAFF"
                opacity=".95"/>

            <rect
                x="91"
                y="78"
                width="38"
                height="25"
                rx="5"
                fill="#E8F2FF"/>

            <rect
                x="101"
                y="84"
                width="18"
                height="13"
                rx="2"
                fill="#FFFFFF"/>

            <path
                d="M48 91h124"
                stroke="#0E5CB7"
                stroke-width="3"
                opacity=".65"/>

            <path
                d="M62 73h96"
                stroke="#6AB0FF"
                stroke-width="2"
                opacity=".7"/>

        </svg>
        '''

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

        # QSvgRenderer requires QPainter.
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

    # ==================================================================
    # SYSTEM OVERVIEW
    # ==================================================================

    def _create_system_overview(self) -> QFrame:
        panel = QFrame()

        panel.setObjectName(
            "infoPanel"
        )

        panel.setMinimumHeight(
            314
        )

        panel.setMaximumHeight(
            314
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

        # --------------------------------------------------------------
        # Header
        # --------------------------------------------------------------

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
            24
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

        # --------------------------------------------------------------
        # Live status
        # --------------------------------------------------------------

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

        self._live_status_dot = dot

        live.addWidget(
            dot
        )

        live_text = QLabel(
            "Live system information"
        )

        live_text.setObjectName(
            "liveStatus"
        )

        self._live_status = live_text

        live.addWidget(
            live_text
        )

        header.addLayout(
            live
        )

        layout.addLayout(
            header
        )

        # --------------------------------------------------------------
        # Separator
        # --------------------------------------------------------------

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

        # --------------------------------------------------------------
        # Information rows
        # --------------------------------------------------------------

        self._info_labels: list[QLabel] = []

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
    # INFORMATION ROW
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
            22
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

        self._info_labels.append(
            label
        )

        label.setObjectName(
            "panelLabel"
        )

        label.setFixedWidth(
            190
        )

        value = QLabel(
            value_text
        )

        value.setObjectName(
            "panelValue"
        )

        value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        value.setWordWrap(
            True
        )

        row_layout.addWidget(
            icon_label
        )

        row_layout.addWidget(
            label
        )

        row_layout.addWidget(
            value,
            1
        )

        return row

    # ==================================================================
    # RECENT ACTIVITY
    # ==================================================================

    def _create_recent_activity(self) -> QFrame:
        panel = QFrame()

        panel.setObjectName(
            "infoPanel"
        )

        panel.setMinimumHeight(
            218
        )

        panel.setMaximumHeight(
            218
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

        # --------------------------------------------------------------
        # Header
        # --------------------------------------------------------------

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
            24
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

        self._view_logs = logs

        logs.setObjectName(
            "viewLogs"
        )

        header.addWidget(
            logs
        )

        layout.addLayout(
            header
        )

        # --------------------------------------------------------------
        # Header separator
        # --------------------------------------------------------------

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

        # --------------------------------------------------------------
        # Activity entries
        # --------------------------------------------------------------

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

            if index < len(events) - 1:

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
            1
        )

        return row

    # ==================================================================
    # RESPONSIVE LAYOUT
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

            # ----------------------------------------------------------
            # Dashboard margins
            # ----------------------------------------------------------

            self._content_layout.setContentsMargins(
                14,
                12,
                14,
                18,
            )

            self._content_layout.setSpacing(
                10
            )

            # ----------------------------------------------------------
            # Welcome banner
            # ----------------------------------------------------------

            self._welcome_panel.setMinimumHeight(
                190
            )

            self._welcome_panel.setMaximumHeight(
                190
            )

            self._welcome_panel.layout().setContentsMargins(
                22,
                18,
                18,
                18,
            )

            self._welcome_panel.layout().setSpacing(
                12
            )

            # ----------------------------------------------------------
            # Compact right visual
            # ----------------------------------------------------------

            self._welcome_visual.setMinimumWidth(
                175
            )

            self._welcome_visual.setMaximumWidth(
                190
            )

            self._welcome_illustration_box.setFixedSize(
                150,
                142
            )

            # Remove unnecessary checklist width at 1024px.
            self._welcome_checklist_layout.setContentsMargins(
                0,
                0,
                0,
                0,
            )

            self._welcome_checklist_layout.setSpacing(
                0
            )

            for index in range(
                self._welcome_checklist_layout.count()
            ):

                item = (
                    self._welcome_checklist_layout.itemAt(
                        index
                    )
                )

                if item is None:
                    continue

                widget = item.widget()

                if widget is not None:
                    widget.setVisible(
                        False
                    )

                nested_layout = (
                    item.layout()
                )

                if nested_layout is not None:

                    for nested_index in range(
                        nested_layout.count()
                    ):

                        nested_item = (
                            nested_layout.itemAt(
                                nested_index
                            )
                        )

                        if nested_item is None:
                            continue

                        nested_widget = (
                            nested_item.widget()
                        )

                        if nested_widget is not None:
                            nested_widget.setVisible(
                                False
                            )

            # ----------------------------------------------------------
            # System overview
            # ----------------------------------------------------------

            self._system_panel.setMinimumHeight(
                300
            )

            self._system_panel.setMaximumHeight(
                300
            )

            # Hide right-side status so it cannot
            # overflow outside the panel.
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
                198
            )

            self._activity_panel.setMaximumHeight(
                198
            )

            self._view_logs.setVisible(
                False
            )

        else:

            # ==========================================================
            # NORMAL / LARGE SCREEN
            # ==========================================================

            self._content_layout.setContentsMargins(
                26,
                18,
                26,
                24,
            )

            self._content_layout.setSpacing(
                14
            )

            # ----------------------------------------------------------
            # Welcome banner
            # ----------------------------------------------------------

            self._welcome_panel.setMinimumHeight(
                218
            )

            self._welcome_panel.setMaximumHeight(
                218
            )

            self._welcome_panel.layout().setContentsMargins(
                36,
                22,
                28,
                22,
            )

            self._welcome_panel.layout().setSpacing(
                22
            )

            self._welcome_visual.setMinimumWidth(
                500
            )

            self._welcome_visual.setMaximumWidth(
                520
            )

            self._welcome_illustration_box.setFixedSize(
                260,
                176
            )

            # Restore checklist.
            for index in range(
                self._welcome_checklist_layout.count()
            ):

                item = (
                    self._welcome_checklist_layout.itemAt(
                        index
                    )
                )

                if item is None:
                    continue

                nested_layout = (
                    item.layout()
                )

                if nested_layout is not None:

                    for nested_index in range(
                        nested_layout.count()
                    ):

                        nested_item = (
                            nested_layout.itemAt(
                                nested_index
                            )
                        )

                        if nested_item is None:
                            continue

                        nested_widget = (
                            nested_item.widget()
                        )

                        if nested_widget is not None:
                            nested_widget.setVisible(
                                True
                            )

            self._welcome_checklist_layout.setContentsMargins(
                0,
                8,
                0,
                0,
            )

            self._welcome_checklist_layout.setSpacing(
                8
            )

            # ----------------------------------------------------------
            # System overview
            # ----------------------------------------------------------

            self._system_panel.setMinimumHeight(
                314
            )

            self._system_panel.setMaximumHeight(
                314
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
                218
            )

            self._activity_panel.setMaximumHeight(
                218
            )

            self._view_logs.setVisible(
                True
            )

    # ==================================================================
    # REAL SYSTEM INFORMATION
    # ==================================================================

    def _computer_name(
        self,
    ) -> str:

        try:
            return socket.gethostname()

        except OSError:
            return "Unknown"

    def _operating_system(
        self,
    ) -> str:

        try:

            system = platform.system()

            release = platform.release()

            if system == "Windows":

                name = self._windows_name()

                if name:

                    return (
                        f"{name} "
                        f"({release})"
                    )

                return (
                    f"Windows "
                    f"{release}"
                )

            return (
                f"{system} "
                f"{release}"
            )

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

                return str(
                    winreg.QueryValueEx(
                        key,
                        "ProductName",
                    )[0]
                )

        except Exception:
            return ""

    def _current_user(
        self,
    ) -> str:

        try:

            return getpass.getuser()

        except Exception:

            return os.environ.get(
                "USERNAME",
                "Unknown",
            )

    def _processor(
        self,
    ) -> str:

        try:

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
            return "Unknown"

    def _memory(
        self,
    ) -> str:

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
                        "sullAvailExtendedVirtual",
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

    def _system_drive(
        self,
    ) -> str:

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

    def _uptime(
        self,
    ) -> str:

        try:

            if (
                platform.system()
                != "Windows"
            ):
                return "Unavailable"

            milliseconds = (
                ctypes.windll.kernel32.GetTickCount64()
            )

            return self._format_uptime(
                milliseconds / 1000
            )

        except Exception:
            return "Unknown"

    @staticmethod
    def _format_uptime(
        total_seconds: float,
    ) -> str:

        seconds = int(
            total_seconds
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

    # ==================================================================
    # DASHBOARD STYLE
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
                background: #E8F4FF;
                border: 1px solid #CFE5FA;
                border-radius: 15px;
            }

            #welcomeEyebrow {
                color: #2F80ED;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 2px;
            }

            #welcomeTitle {
                color: #123A72;
                font-size: 40px;
                font-weight: 700;
            }

            #welcomeSubtitle {
                color: #16447F;
                font-size: 20px;
                font-weight: 500;
            }

            #welcomeDescription {
                color: #5D7698;
                font-size: 14px;
            }

            #welcomeVisualArea {
                background: transparent;
                border: none;
            }

            #welcomeIconBox {
                background: rgba(
                    255,
                    255,
                    255,
                    0.24
                );
                border: 1px solid rgba(
                    159,
                    197,
                    236,
                    0.48
                );
                border-radius: 16px;
            }

            #welcomeIllustration {
                background: transparent;
            }

            #welcomeCheckDot {
                color: #2F80ED;
                font-size: 14px;
            }

            #welcomeCheck {
                color: #3972B7;
                font-size: 14px;
                font-weight: 600;
            }

            #welcomeTomorrow {
                color: #8AA7C8;
                font-size: 12px;
                font-style: italic;
            }

            /* ========================================================
               INFORMATION PANELS
               ======================================================== */

            #infoPanel {
                background: #FFFFFF;
                border: 1px solid #DDE5EF;
                border-radius: 14px;
            }

            #panelTitle {
                color: #14213D;
                font-size: 18px;
                font-weight: 700;
            }

            #panelLabel {
                color: #6A82A3;
                font-size: 14px;
            }

            #panelValue {
                color: #19375E;
                font-size: 14px;
                font-weight: 500;
            }

            #liveDot,
            #liveStatus {
                color: #18B968;
            }

            #liveDot {
                font-size: 10px;
            }

            #liveStatus {
                font-size: 12px;
                font-weight: 600;
            }

            #panelSeparator,
            #activitySeparator {
                background: #E5EBF3;
                border: none;
            }

            /* ========================================================
               RECENT ACTIVITY
               ======================================================== */

            #viewLogs {
                color: #2F80ED;
                font-size: 14px;
                font-weight: 600;
            }

            #activityIndicator {
                color: #18B968;
                font-size: 10px;
            }

            #activityTime {
                color: #55759E;
                font-size: 13px;
                font-weight: 600;
            }

            #activityDescription {
                color: #405875;
                font-size: 14px;
            }
            """
        )