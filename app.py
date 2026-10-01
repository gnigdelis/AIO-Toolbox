from __future__ import annotations

import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from core.scheduled_backup import run_scheduled_backup
from ui.v2.main_window import MainWindow


APP_ICON_PATH = "assets/branding/window/app.ico"


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(
        base_path,
        relative_path,
    )


def main() -> int:
    if "--scheduled-backup" in sys.argv:
        return run_scheduled_backup()

    application = QApplication(sys.argv)

    application.setApplicationName(
        "AIO Toolbox"
    )
    application.setApplicationDisplayName(
        "AIO Toolbox"
    )
    application.setOrganizationName(
        "Sunsoft"
    )

    app_icon = QIcon(
        resource_path(APP_ICON_PATH)
    )

    if not app_icon.isNull():
        application.setWindowIcon(
            app_icon
        )

    window = MainWindow()

    if not app_icon.isNull():
        window.setWindowIcon(
            app_icon
        )

    window.show()

    return application.exec()


if __name__ == "__main__":
    sys.exit(main())
