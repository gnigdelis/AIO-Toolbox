from __future__ import annotations

import ctypes
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ui.v2.main_window import MainWindow, create_application


APP_ICON_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "branding"
    / "window"
    / "app.ico"
)


def _set_windows_app_user_model_id() -> None:
    """
    Give Windows a unique AppUserModelID so the application
    is correctly identified and grouped in the taskbar.
    """
    if sys.platform != "win32":
        return

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "Sunsoft.AIO-Toolbox"
        )
    except Exception:
        pass


def _hide_console_when_frozen() -> None:
    """
    Hide the console window when running the frozen executable.
    """
    if not getattr(sys, "frozen", False):
        return

    try:
        console_window = ctypes.windll.kernel32.GetConsoleWindow()

        if console_window:
            ctypes.windll.user32.ShowWindow(
                console_window,
                0,
            )
    except Exception:
        pass


def main() -> int:
    _set_windows_app_user_model_id()
    _hide_console_when_frozen()

    application = create_application()

    # Load the real AIO Toolbox application icon.
    app_icon = QIcon(str(APP_ICON_PATH))

    # Set the icon globally for Qt.
    application.setWindowIcon(app_icon)

    window = MainWindow()

    # Explicitly set it on the main window as well.
    # This guarantees the icon appears in the title bar
    # even if another window/component changes the default icon.
    window.setWindowIcon(app_icon)

    window.show()

    return application.exec()


if __name__ == "__main__":
    sys.exit(main())