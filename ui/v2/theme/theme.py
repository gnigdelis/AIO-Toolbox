import re
from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


THEME_LIGHT = "light"
THEME_DARK = "dark"

_SETTINGS_ORGANIZATION = "Sunsoft"
_SETTINGS_APPLICATION = "AIO Toolbox"
_SETTINGS_THEME_KEY = "theme"


LIGHT_STYLESHEET = """
QMainWindow { background-color: #F7F9FC; }
QWidget { font-family: "Segoe UI"; color: #17233C; }

#header { background-color: #FFFFFF; border-bottom: 1px solid #E2E7EF; }
#headerBranding { background: transparent; }
#headerLogo { background: transparent; }

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

#headerBrandingTitle {
    color: #14213D;
    font-size: 24px;
    font-weight: 700;
}

#headerBrandingSubtitle {
    color: #68758A;
    font-size: 11px;
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

#themeToggleButton {
    background: #F7F9FC;
    color: #40506A;
    border: 1px solid #D9E2EF;
    border-radius: 9px;
    padding: 0 12px;
    font-size: 13px;
    font-weight: 600;
}

#themeToggleButton:hover {
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

#impactStatusButton {
    border-radius: 7px;
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
    color: #20B15A;
    background: transparent;
    border-radius: 6px;
}

#statusText,
#dateTime {
    color: #526176;
    font-size: 13px;
}
"""


DARK_STYLESHEET = """
QMainWindow { background-color: #111827; }
QWidget {
    font-family: "Segoe UI";
    color: #E5E7EB;
}

#header {
    background-color: #18212F;
    border-bottom: 1px solid #2A3545;
}

#headerBranding,
#headerLogo {
    background: transparent;
}

#headerBrandingTitle {
    color: #F3F4F6;
    font-size: 24px;
    font-weight: 700;
}

#headerBrandingSubtitle {
    color: #94A3B8;
    font-size: 11px;
}

#headerButton {
    background: #202B3B;
}

#headerButton:hover {
    background: #29364A;
}

#themeToggleButton {
    background: #202B3B;
    color: #DCE6F2;
    border: 1px solid #35445A;
    border-radius: 9px;
    padding: 0 12px;
    font-size: 13px;
    font-weight: 600;
}

#themeToggleButton:hover {
    background: #29364A;
}

#versionLabel {
    color: #94A3B8;
    font-size: 12px;
}

#databaseHeaderButton {
    background: #202B3B;
    color: #55D68A;
    border: 1px solid #35654A;
}

#databaseHeaderButton:hover {
    background: #263B31;
}

#impactStatusButton {
    border-radius: 7px;
}

#sidebar {
    background-color: #18212F;
    border-right: 1px solid #2A3545;
}

#navigationItem {
    background: transparent;
    color: #D7E0EB;
}

#navigationItem:hover {
    background: #243146;
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

#contentArea {
    background-color: #111827;
}

#contentArea QScrollArea {
    background: transparent;
    border: none;
}

#contentArea QScrollArea > QWidget {
    background: transparent;
}

#welcomeBanner {
    background-color: #172C43;
    border: 1px solid #28496A;
    border-radius: 15px;
}

#welcomeEyebrow {
    color: #63A4FF;
}

#welcomeTitle {
    color: #DDEBFF;
}

#welcomeSubtitle {
    color: #B8D1F0;
}

#welcomeDescription {
    color: #8FA9C8;
}

#welcomeVisual {
    background-color: #1E3854;
    border: 1px solid #31577D;
}

#welcomeIconBox {
    background: rgba(255,255,255,0.08);
}

#welcomeIcon {
    background: #2F80ED;
}

#welcomeCheck {
    color: #82B5F0;
}

#welcomeTomorrow {
    color: #7895B7;
}

#infoPanel {
    background-color: #18212F;
    border: 1px solid #2A3545;
}

#panelTitle {
    color: #F1F5F9;
}

#panelLabel {
    color: #9AAAC0;
}

#panelValue {
    color: #D7E3F1;
}

#viewLogs {
    color: #63A4FF;
}

#activityIndicator {
    color: #38D98A;
}

#activityTime {
    color: #9DB5D0;
}

#activityDescription {
    color: #C3D0E0;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 4px 2px;
}

QScrollBar::handle:vertical {
    background: #3A485C;
    border-radius: 4px;
    min-height: 40px;
}

QScrollBar::handle:vertical:hover {
    background: #4A5B73;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

#statusBar {
    background: #18212F;
    border-top: 1px solid #2A3545;
}

#statusIndicator {
    color: #38D98A;
    background: transparent;
}

#statusText,
#dateTime {
    color: #9AAAC0;
    font-size: 13px;
}

QLineEdit,
QTextEdit,
QPlainTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox,
QDateEdit,
QDateTimeEdit {
    background: #1A2535;
    color: #E5E7EB;
    border: 1px solid #35445A;
    border-radius: 7px;
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QDateEdit:focus,
QDateTimeEdit:focus {
    border: 1px solid #4B91F1;
}

QPushButton {
    color: #E5E7EB;
}

QListWidget,
QTreeWidget,
QTableWidget {
    background: #18212F;
    color: #E5E7EB;
    border: 1px solid #2A3545;
    alternate-background-color: #1E2938;
}

QHeaderView::section {
    background: #202B3B;
    color: #DCE6F2;
    border: none;
    padding: 6px;
}

QToolTip {
    background: #202B3B;
    color: #F3F4F6;
    border: 1px solid #3A485C;
}
"""


def _build_palette(dark: bool) -> QPalette:
    palette = QPalette()

    if dark:
        window = "#111827"
        text = "#E5E7EB"
        base = "#18212F"
        alternate = "#1E2938"
        button = "#202B3B"
        button_text = "#E5E7EB"
        highlight = "#2F80ED"
        highlighted_text = "#FFFFFF"
        tooltip_base = "#202B3B"
        tooltip_text = "#F3F4F6"
    else:
        window = "#F7F9FC"
        text = "#17233C"
        base = "#FFFFFF"
        alternate = "#F7F9FC"
        button = "#FFFFFF"
        button_text = "#17233C"
        highlight = "#2F80ED"
        highlighted_text = "#FFFFFF"
        tooltip_base = "#FFFFFF"
        tooltip_text = "#17233C"

    palette.setColor(QPalette.ColorRole.Window, QColor(window))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(text))
    palette.setColor(QPalette.ColorRole.Base, QColor(base))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(alternate))
    palette.setColor(QPalette.ColorRole.Text, QColor(text))
    palette.setColor(QPalette.ColorRole.Button, QColor(button))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(button_text))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(highlight))
    palette.setColor(
        QPalette.ColorRole.HighlightedText,
        QColor(highlighted_text),
    )
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(tooltip_base))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(tooltip_text))

    return palette


def get_saved_theme() -> str:
    settings = QSettings(
        _SETTINGS_ORGANIZATION,
        _SETTINGS_APPLICATION,
    )

    value = settings.value(
        _SETTINGS_THEME_KEY,
        THEME_LIGHT,
    )

    if value not in {THEME_LIGHT, THEME_DARK}:
        return THEME_LIGHT

    return value


def save_theme(theme: str) -> None:
    if theme not in {THEME_LIGHT, THEME_DARK}:
        theme = THEME_LIGHT

    settings = QSettings(
        _SETTINGS_ORGANIZATION,
        _SETTINGS_APPLICATION,
    )

    settings.setValue(
        _SETTINGS_THEME_KEY,
        theme,
    )
    settings.sync()


def apply_theme(
    application: QApplication,
    theme: str | None = None,
) -> str:
    if theme is None:
        theme = get_saved_theme()

    if theme not in {THEME_LIGHT, THEME_DARK}:
        theme = THEME_LIGHT

    dark = theme == THEME_DARK

    application.setPalette(
        _build_palette(dark)
    )

    application.setStyleSheet(
        DARK_STYLESHEET
        if dark
        else LIGHT_STYLESHEET
    )

    return theme


def toggle_theme(
    application: QApplication,
) -> str:
    current = get_saved_theme()

    next_theme = (
        THEME_DARK
        if current == THEME_LIGHT
        else THEME_LIGHT
    )

    save_theme(next_theme)
    apply_theme(
        application,
        next_theme,
    )

    return next_theme

# ================================================================
# Inline widget theme bridge
# ================================================================
#
# Some pages contain their own widget-level stylesheets. Those
# stylesheets have higher priority than the QApplication stylesheet,
# so the central Dark theme cannot override their light backgrounds.
#
# We keep the original stylesheet and transform only the visual
# properties that need to change in Dark mode. Switching back to
# Light restores the original stylesheet exactly.
# ================================================================


# ================================================================
# Inline widget theme bridge
# ================================================================
#
# Several AIO Toolbox pages use widget-level stylesheets.
# Those stylesheets have higher priority than the QApplication
# stylesheet, so they must be synchronized explicitly when the
# user switches between Light and Dark mode.
#
# The original stylesheet of every widget is preserved in the
# _aio_original_stylesheet property and restored when Light mode
# is selected.
# ================================================================

def _darken_inline_stylesheet_for_theme(
    stylesheet: str,
) -> str:
    """
    Convert Light-mode inline styles to readable Dark-mode styles.

    This function only changes visual colors. It does not alter
    dimensions, spacing, fonts, layouts or widget behavior.
    """

    if not stylesheet:
        return stylesheet

    result = stylesheet

    # ------------------------------------------------------------
    # LIGHT SURFACES -> DARK SURFACES
    # ------------------------------------------------------------

    background_replacements = {
        "#FFFFFF": "#18212F",
        "#ffffff": "#18212F",

        "#F7F9FC": "#111827",
        "#f7f9fc": "#111827",

        "#F8FAFC": "#18212F",
        "#f8fafc": "#18212F",

        "#F9FAFB": "#18212F",
        "#f9fafb": "#18212F",

        "#F5F7FA": "#1A2535",
        "#f5f7fa": "#1A2535",

        "#F4F7FB": "#1A2535",
        "#f4f7fb": "#1A2535",

        "#F2F5F9": "#1A2535",
        "#f2f5f9": "#1A2535",

        "#EEF2F7": "#202B3B",
        "#eef2f7": "#202B3B",

        "#EAF1F8": "#2A394D",
        "#eaf1f8": "#2A394D",

        "#EDF2F7": "#202B3B",
        "#edf2f7": "#202B3B",

        "#F1F5F9": "#202B3B",
        "#f1f5f9": "#202B3B",
    }

    for old, new in background_replacements.items():
        result = result.replace(old, new)

    # Named white backgrounds.
    result = re.sub(
        r"(?i)(background(?:-color)?\s*:\s*)white(\s*[;])",
        r"\1#18212F\2",
        result,
    )

    # RGB white backgrounds.
    result = re.sub(
        r"rgba?\(\s*255\s*,\s*255\s*,\s*255(?:\s*,\s*1(?:\.0+)?)?\s*\)",
        "#18212F",
        result,
        flags=re.IGNORECASE,
    )

    # ------------------------------------------------------------
    # LIGHT BORDERS -> DARK BORDERS
    # ------------------------------------------------------------

    border_replacements = {
        "#D8E1EC": "#34445A",
        "#d8e1ec": "#34445A",

        "#D8E0EC": "#34445A",
        "#d8e0ec": "#34445A",

        "#D9E2EF": "#34445A",
        "#d9e2ef": "#34445A",

        "#DDE5EF": "#34445A",
        "#dde5ef": "#34445A",

        "#DDE4EE": "#34445A",
        "#dde4ee": "#34445A",

        "#E1E8F0": "#34445A",
        "#e1e8f0": "#34445A",

        "#E2E7EF": "#2A3545",
        "#e2e7ef": "#2A3545",

        "#E2E8F0": "#34445A",
        "#e2e8f0": "#34445A",

        "#CBD5E1": "#40506A",
        "#cbd5e1": "#40506A",

        "#CBD4E0": "#40506A",
        "#cbd4e0": "#40506A",
    }

    for old, new in border_replacements.items():
        result = result.replace(old, new)

    # ------------------------------------------------------------
    # DARK TEXT -> LIGHT TEXT
    # ------------------------------------------------------------
    #
    # IMPORTANT:
    # Do NOT globally replace white text. White text is correct
    # on blue/red/orange action buttons.
    # ------------------------------------------------------------

    text_replacements = {
        "#14213D": "#F1F5F9",
        "#14213d": "#F1F5F9",

        "#17233C": "#E5E7EB",
        "#17233c": "#E5E7EB",

        "#18304F": "#DCE6F2",
        "#18304f": "#DCE6F2",

        "#19375E": "#DCE6F2",
        "#19375e": "#DCE6F2",

        "#1F2937": "#E5E7EB",
        "#1f2937": "#E5E7EB",

        "#26344D": "#DCE6F2",
        "#26344d": "#DCE6F2",

        "#334155": "#DCE6F2",

        "#40506A": "#C8D5E5",
        "#40506a": "#C8D5E5",

        "#405875": "#C8D5E5",
        "#405875": "#C8D5E5",

        "#475569": "#C8D5E5",
        "#475569": "#C8D5E5",

        "#4B5563": "#C8D5E5",
        "#4b5563": "#C8D5E5",

        "#526176": "#B8C7DA",
        "#526176": "#B8C7DA",

        "#55759E": "#B8C7DA",
        "#55759e": "#B8C7DA",

        "#5B6B85": "#B8C7DA",
        "#5b6b85": "#B8C7DA",

        "#64748B": "#AEBED2",
        "#64748b": "#AEBED2",

        "#68758A": "#AEBED2",
        "#68758a": "#AEBED2",

        "#6A82A3": "#B8C7DA",
        "#6a82a3": "#B8C7DA",

        "#6B7280": "#AEBED2",
        "#6b7280": "#AEBED2",

        "#718096": "#AEBED2",
        "#718096": "#AEBED2",

        "#7B8CA7": "#AEBED2",
        "#7b8ca7": "#AEBED2",

        "#8AA7C8": "#AEBED2",
        "#8aa7c8": "#AEBED2",

        "#8FA9C8": "#B8C7DA",
        "#8fa9c8": "#B8C7DA",

        "#94A3B8": "#AEBED2",
        "#94a3b8": "#AEBED2",
    }

    for old, new in text_replacements.items():
        result = result.replace(old, new)

    # ------------------------------------------------------------
    # Generic dark-mode readability for common CSS text colors.
    # ------------------------------------------------------------

    result = re.sub(
        r"(?i)(color\s*:\s*)rgb\(\s*20\s*,\s*33\s*,\s*61\s*\)",
        r"\1#F1F5F9",
        result,
    )

    result = re.sub(
        r"(?i)(color\s*:\s*)rgb\(\s*23\s*,\s*35\s*,\s*60\s*\)",
        r"\1#E5E7EB",
        result,
    )

    result = re.sub(
        r"(?i)(color\s*:\s*)rgb\(\s*64\s*,\s*88\s*,\s*117\s*\)",
        r"\1#C8D5E5",
        result,
    )

    return result


def _apply_dark_input_style(
    widget,
) -> None:
    """
    Force editable/selectable input widgets to use a white
    surface with dark text in Dark mode.

    This intentionally applies only to input widgets so that
    action buttons keep their original colors.
    """

    class_name = widget.__class__.__name__

    input_classes = {
        "QLineEdit",
        "QDateEdit",
        "QDateTimeEdit",
        "QTimeEdit",
        "QComboBox",
        "QSpinBox",
        "QDoubleSpinBox",
    }

    if class_name not in input_classes:
        return

    current = widget.styleSheet()

    widget.setStyleSheet(
        current
        + """
        QLineEdit,
        QDateEdit,
        QDateTimeEdit,
        QTimeEdit,
        QComboBox,
        QSpinBox,
        QDoubleSpinBox {
            background-color: #FFFFFF;
            color: #17233C;
            selection-background-color: #2F80ED;
            selection-color: #FFFFFF;
            border: 1px solid #B8C7D9;
            border-radius: 7px;
        }

        QLineEdit:focus,
        QDateEdit:focus,
        QDateTimeEdit:focus,
        QTimeEdit:focus,
        QComboBox:focus,
        QSpinBox:focus,
        QDoubleSpinBox:focus {
            background-color: #FFFFFF;
            color: #17233C;
            border: 1px solid #2F80ED;
        }

        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            color: #17233C;
            selection-background-color: #2F80ED;
            selection-color: #FFFFFF;
            border: 1px solid #B8C7D9;
        }
        """
    )


def _apply_dark_text_edit_style(
    widget,
) -> None:
    """
    Keep log/editor areas dark, but make their text clearly readable.
    """

    class_name = widget.__class__.__name__

    if class_name not in {
        "QTextEdit",
        "QPlainTextEdit",
    }:
        return

    current = widget.styleSheet()

    widget.setStyleSheet(
        current
        + """
        QTextEdit,
        QPlainTextEdit {
            background-color: #111827;
            color: #E5E7EB;
            selection-background-color: #2F80ED;
            selection-color: #FFFFFF;
            border: 1px solid #34445A;
        }
        """
    )


def _apply_dark_table_style(
    widget,
) -> None:
    """
    Make tables readable in Dark mode.
    """

    class_name = widget.__class__.__name__

    if class_name not in {
        "QTableWidget",
        "QTableView",
        "QTreeWidget",
        "QListWidget",
    }:
        return

    current = widget.styleSheet()

    widget.setStyleSheet(
        current
        + """
        QTableWidget,
        QTableView,
        QTreeWidget,
        QListWidget {
            background-color: #18212F;
            color: #E5E7EB;
            border: 1px solid #34445A;
            gridline-color: #34445A;
            alternate-background-color: #1E2938;
        }

        QTableWidget::item,
        QTableView::item,
        QTreeWidget::item,
        QListWidget::item {
            color: #E5E7EB;
        }

        QHeaderView::section {
            background-color: #202B3B;
            color: #DCE6F2;
            border: 1px solid #34445A;
            padding: 6px;
        }
        """
    )


def _apply_dark_label_style(
    widget,
) -> None:
    """
    Improve readability of labels whose page-specific inline
    stylesheet still contains dark Light-mode text colors.
    """

    class_name = widget.__class__.__name__

    if class_name not in {
        "QLabel",
        "QGroupBox",
        "QCheckBox",
        "QRadioButton",
        "QToolButton",
    }:
        return

    current = widget.styleSheet()

    if not current:
        return

    # The converter already handles explicit color declarations.
    # This second pass only catches the common dark colors that
    # remained in older page stylesheets.
    converted = _darken_inline_stylesheet_for_theme(current)

    if converted != current:
        widget.setStyleSheet(converted)


def _sync_existing_widgets_for_theme(
    application,
    dark: bool,
) -> None:
    """
    Synchronize existing widgets with the selected theme.
    """

    if application is None:
        return

    for widget in application.allWidgets():
        try:
            original = widget.property(
                "_aio_original_stylesheet"
            )

            if original is None:
                original = widget.styleSheet()
                widget.setProperty(
                    "_aio_original_stylesheet",
                    original,
                )

            if dark:
                if original:
                    converted = (
                        _darken_inline_stylesheet_for_theme(
                            original
                        )
                    )

                    if converted != widget.styleSheet():
                        widget.setStyleSheet(converted)

                _apply_dark_input_style(widget)
                _apply_dark_text_edit_style(widget)
                _apply_dark_table_style(widget)
                _apply_dark_label_style(widget)

            else:
                if widget.styleSheet() != original:
                    widget.setStyleSheet(original)

        except RuntimeError:
            # Widget was deleted while traversing.
            continue
        except Exception:
            continue


def apply_theme(
    application,
    theme=None,
) -> str:
    """
    Apply Light or Dark theme.

    The application always starts in Light mode because
    main_window.py explicitly passes THEME_LIGHT at startup.
    """

    if application is None:
        return THEME_LIGHT

    if theme not in {
        THEME_LIGHT,
        THEME_DARK,
    }:
        theme = THEME_LIGHT

    dark = theme == THEME_DARK

    application.setPalette(
        _build_palette(dark)
    )

    application.setStyleSheet(
        DARK_STYLESHEET
        if dark
        else LIGHT_STYLESHEET
    )

    _sync_existing_widgets_for_theme(
        application,
        dark,
    )

    try:
        application.processEvents()
    except Exception:
        pass

    return theme
