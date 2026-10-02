from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys


def app_base_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]


def log_path() -> Path:
    path = (
        app_base_path()
        / "logs"
        / "app.log"
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


def write_log(
    message: str,
    level: str = "INFO",
) -> None:
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    line = (
        f"[{timestamp}] "
        f"[{level.upper()}] "
        f"{message}\n"
    )

    try:
        with log_path().open(
            "a",
            encoding="utf-8",
        ) as handle:
            handle.write(line)

    except Exception:
        pass


def info(message: str) -> None:
    write_log(
        message,
        "INFO",
    )


def warning(message: str) -> None:
    write_log(
        message,
        "WARNING",
    )


def error(message: str) -> None:
    write_log(
        message,
        "ERROR",
    )


def success(message: str) -> None:
    write_log(
        message,
        "SUCCESS",
    )
