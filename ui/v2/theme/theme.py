from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


APP_STYLESHEET = """
QMainWindow { background-color: #F7F9FC; }
QWidget { font-family: "Segoe UI"; color: #17233C; }

#header { background-color: #FFFFFF; border-bottom: 1px solid #E2E7EF; }

#brandIcon {
    background-color: #2F80ED;
    border-radius: 16px;
}

#brandTitle {
    color: #14213D;
    font-size: 30px;
    font-weight: 700;
}

#brandTitleAccent {
    color: #2F80ED;
    font-size: 30px;
    font-weight: 700;
}

#brandSubtitle {
    color: #68758A;
    font-size: 13px;
}

#searchContainer {
    background-color: #F8FAFD;
    border: 1px solid #D9E2EF;
    border-radius: 12px;
}

#searchIcon {
    background: transparent;
}

#searchInput {
    background: transparent;
    border: none;
    color: #26344D;
    font-size: 15px;
    padding: 0 8px;
}

#searchShortcut {
    background: #FFFFFF;
    border: 1px solid #D7E0EC;
    border-radius: 8px;
    color: #6C7D96;
    font-size: 12px;
}

#headerButton {
    background: #F7F9FC;
    border: none;
    border-radius: 24px;
}

#headerButton:hover {
    background: #EEF4FB;
}

#versionLabel {
    color: #718096;
    font-size: 12px;
}

#databaseHeaderButton {
    background: #FFFFFF;
    color: #16803C;
    border: 1px solid #B9DEC8;
    border-radius: 12px;
    padding: 0 14px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
}

#databaseHeaderButton:hover {
    background: #F4FBF7;
}

#sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E7EF;
}

#navigationItem {
    background: transparent;
    border: none;
    border-radius: 10px;
    color: #18304F;
    font-size: 15px;
    font-weight: 500;
    text-align: left;
    padding: 0;
}

#navigationItem:hover {
    background: #F3F7FC;
}

#navigationItem[selected="true"] {
    background: #2F86E8;
    color: #FFFFFF;
}

#navigationItem[selected="true"]:hover {
    background: #2F86E8;
}

#navigationIcon {
    background: transparent;
}

#sunsoftBrand {
    color: #2F80ED;
    font-size: 25px;
    font-weight: 800;
}

#sunsoftSubtitle {
    color: #7B8CA7;
    font-size: 11px;
}

#contentArea {
    background-color: #F7F9FC;
}

#contentArea QScrollArea {
    background: transparent;
    border: none;
}

#contentArea QScrollArea > QWidget {
    background: transparent;
}

#welcomeBanner {
    background-color: #E8F4FF;
    border: 1px solid #CFE5FA;
    border-radius: 15px;
}

#welcomeEyebrow {
    color: #2F80ED;
    font-size: 13px;
    font-weight: 700;
}

#welcomeTitle {
    color: #123A72;
    font-size: 40px;
    font-weight: 700;
}

#welcomeSubtitle {
    color: #16447F;
    font-size: 20px;
}

#welcomeDescription {
    color: #5D7698;
    font-size: 14px;
}

#welcomeVisual {
    background-color: #D7EAFE;
    border: 1px solid #C5DCF5;
    border-radius: 18px;
}

#welcomeIconBox {
    background: rgba(255,255,255,0.18);
    border-radius: 16px;
}

#welcomeIcon {
    background: #2F80ED;
    border-radius: 22px;
}

#welcomeCheck {
    color: #3972B7;
    font-size: 13px;
    font-weight: 600;
}

#welcomeTomorrow {
    color: #8AA7C8;
    font-size: 12px;
    font-style: italic;
}

#infoPanel {
    background-color: #FFFFFF;
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

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 4px 2px;
}

QScrollBar::handle:vertical {
    background: #CBD4E0;
    border-radius: 4px;
    min-height: 40px;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

#statusBar {
    background: #FFFFFF;
    border-top: 1px solid #E2E7EF;
}

#statusIndicator {
    background: #20B15A;
    border-radius: 6px;
}

#statusText,
#dateTime {
    color: #526176;
    font-size: 13px;
}
"""


def apply_theme(application: QApplication) -> None:
    """
    Force AIO Toolbox to use a light Qt palette,
    regardless of the Windows system theme.
    """

    palette = QPalette()

    palette.setColor(
        QPalette.ColorRole.Window,
        QColor("#F7F9FC"),
    )

    palette.setColor(
        QPalette.ColorRole.WindowText,
        QColor("#17233C"),
    )

    palette.setColor(
        QPalette.ColorRole.Base,
        QColor("#FFFFFF"),
    )

    palette.setColor(
        QPalette.ColorRole.AlternateBase,
        QColor("#F7F9FC"),
    )

    palette.setColor(
        QPalette.ColorRole.Text,
        QColor("#17233C"),
    )

    palette.setColor(
        QPalette.ColorRole.Button,
        QColor("#FFFFFF"),
    )

    palette.setColor(
        QPalette.ColorRole.ButtonText,
        QColor("#17233C"),
    )

    palette.setColor(
        QPalette.ColorRole.Highlight,
        QColor("#2F80ED"),
    )

    palette.setColor(
        QPalette.ColorRole.HighlightedText,
        QColor("#FFFFFF"),
    )

    palette.setColor(
        QPalette.ColorRole.ToolTipBase,
        QColor("#FFFFFF"),
    )

    palette.setColor(
        QPalette.ColorRole.ToolTipText,
        QColor("#17233C"),
    )

    application.setPalette(
        palette
    )

    application.setStyleSheet(
        APP_STYLESHEET
    )