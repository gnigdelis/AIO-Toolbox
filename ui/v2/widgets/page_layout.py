from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


PAGE_LAYOUT_STYLE = """
QLabel#pageTitle {
    color: #1F2D3D;
    font-size: 25px;
    font-weight: 700;
}

QLabel#pageSubtitle {
    color: #66758A;
    font-size: 11px;
}

QGroupBox#contentCard {
    background: #FFFFFF;
    border: 1px solid #DCE3EC;
    border-radius: 10px;
    margin-top: 8px;
    padding-top: 10px;
    color: #334155;
    font-size: 12px;
    font-weight: 600;
}

QGroupBox#contentCard::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    color: #526176;
}

QPushButton {
    min-height: 36px;
    padding: 0 14px;
    border-radius: 6px;
    font-weight: 600;
}

QPushButton#primaryButton {
    background: #2F6FED;
    color: #FFFFFF;
    border: 1px solid #2F6FED;
}

QPushButton#primaryButton:hover {
    background: #245DCA;
}

QPushButton#secondaryButton {
    background: #FFFFFF;
    color: #40506A;
    border: 1px solid #C8D2E0;
}

QPushButton#secondaryButton:hover {
    background: #F5F8FC;
}

QPushButton#warningButton {
    background: #FFF4E5;
    color: #A65B00;
    border: 1px solid #F1C27D;
}

QPushButton#warningButton:hover {
    background: #FFEBD0;
}

QPushButton:disabled {
    color: #A8B2C0;
    background: #F1F4F8;
    border-color: #E1E6ED;
}
"""


def setup_page_layout(
    page: QWidget,
    title: str,
    subtitle: str,
) -> tuple[QVBoxLayout, QLabel, QLabel]:
    """
    Apply the common AIO Toolbox page layout.

    Returns:
        root layout, title label, subtitle label
    """
    root = QVBoxLayout(page)
    root.setContentsMargins(28, 24, 28, 28)
    root.setSpacing(16)

    title_label = QLabel(title)
    title_label.setObjectName("pageTitle")

    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("pageSubtitle")

    root.addWidget(title_label)
    root.addWidget(subtitle_label)

    return root, title_label, subtitle_label


def create_content_card(
    title: str,
) -> tuple[QGroupBox, QVBoxLayout]:
    """Create a standard AIO Toolbox content card."""
    card = QGroupBox(title)
    card.setObjectName("contentCard")

    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 18, 14, 14)
    layout.setSpacing(10)

    return card, layout


def create_button(
    text: str,
    object_name: str = "secondaryButton",
) -> QPushButton:
    """Create a standard AIO Toolbox button."""
    button = QPushButton(text)
    button.setObjectName(object_name)
    button.setMinimumHeight(36)
    return button


def create_button_row() -> tuple[QHBoxLayout, QVBoxLayout]:
    """
    Create standard horizontal button spacing.

    Returns:
        button row layout and an empty vertical layout placeholder.
    """
    row = QHBoxLayout()
    row.setSpacing(8)

    spacer = QVBoxLayout()

    return row, spacer