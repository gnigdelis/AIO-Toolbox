from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SystemOverview(QFrame):
    """System overview panel."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setObjectName("infoPanel")

        self._build_ui()

    def _build_ui(self) -> None:

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        title = QLabel("▣   System Overview")
        title.setObjectName("panelTitle")

        layout.addWidget(title)

        rows = [
            ("Computer Name", "DESKTOP-01"),
            ("Operating System", "Windows 11 Pro 64-bit"),
            ("User", "Current User"),
            ("Uptime", "2 days, 4 hours"),
        ]

        for label, value in rows:

            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)

            label_widget = QLabel(label)
            label_widget.setObjectName("panelLabel")

            value_widget = QLabel(value)
            value_widget.setObjectName("panelValue")

            row.addWidget(label_widget)
            row.addWidget(value_widget)
            row.addStretch()

            layout.addLayout(row)


class RecentActivity(QFrame):
    """Recent activity panel."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setObjectName("infoPanel")

        self._build_ui()

    def _build_ui(self) -> None:

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        header = QHBoxLayout()

        title = QLabel("◷   Recent Activity")
        title.setObjectName("panelTitle")

        view_logs = QLabel("View Logs  →")
        view_logs.setObjectName("viewLogs")

        header.addWidget(title)
        header.addStretch()
        header.addWidget(view_logs)

        layout.addLayout(header)

        activities = [
            ("10:24", "System information retrieved"),
            ("10:18", "Network test completed"),
            ("10:05", "Backup task finished"),
            ("09:47", "Remote session closed"),
            ("09:32", "Application started"),
        ]

        for time, description in activities:

            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(10)

            indicator = QLabel("●")
            indicator.setObjectName("activityIndicator")

            time_label = QLabel(time)
            time_label.setObjectName("activityTime")
            time_label.setFixedWidth(42)

            description_label = QLabel(description)
            description_label.setObjectName(
                "activityDescription"
            )

            row.addWidget(indicator)
            row.addWidget(time_label)
            row.addWidget(description_label)
            row.addStretch()

            layout.addLayout(row)


class DashboardInfoPanels(QWidget):
    """Container for the dashboard information panels."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        system = SystemOverview()
        activity = RecentActivity()

        layout.addWidget(system, 1)
        layout.addWidget(activity, 1)