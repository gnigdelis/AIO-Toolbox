import sys

from ui.v2.main_window import MainWindow, create_application


def main() -> int:
    """Application entry point."""

    application = create_application()

    window = MainWindow()
    window.show()

    return application.exec()


if __name__ == "__main__":
    sys.exit(main())