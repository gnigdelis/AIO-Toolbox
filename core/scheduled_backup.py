from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

from core.backup.backup_engine import BackupEngine
from core.configuration.settings_manager import SettingsManager
from core.database.database_context import database_context


def app_base_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[1]


def run_scheduled_backup() -> int:
    base = app_base_path()

    settings_manager = SettingsManager(
        base / "config" / "settings.json"
    )
    settings = settings_manager.load()

    log_path = (
        base
        / "logs"
        / "scheduled_backup.log"
    )

    log_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    def log(message: str) -> None:
        with log_path.open(
            "a",
            encoding="utf-8",
        ) as handle:
            handle.write(
                f"[{datetime.now():%Y-%m-%d %H:%M:%S}] "
                f"{message}\n"
            )

    if not settings.get(
        "schedule_enabled",
        False,
    ):
        log(
            "Scheduled backup skipped: schedule is disabled."
        )
        return 0

    selected_targets = (
        settings.get("selected_targets")
        or {}
    )

    destination = Path(
        settings.get(
            "backup_destination",
            str(base / "backup"),
        )
    ).expanduser()

    if selected_targets.get(
        "sql",
        True,
    ):
        selected_udl = settings.get(
            "selected_udl",
            "",
        )

        if not selected_udl:
            log(
                "Scheduled backup failed: "
                "no selected UDL for SQL backup."
            )
            return 1

        try:
            database_context.select(
                selected_udl
            )
        except Exception as exc:
            log(
                "Scheduled backup failed: "
                f"unable to select UDL: {exc}"
            )
            return 1

    log(
        "Scheduled backup started. "
        f"Destination: {destination}"
    )

    log(
        "Selected targets: "
        f"{selected_targets}"
    )

    def progress(
        percentage: int,
        message: str,
    ) -> None:
        log(
            f"{percentage}% - {message}"
        )

    try:
        engine = BackupEngine(
            base_path=destination,
            progress_callback=progress,
        )

        result = engine.run(
            selected_targets
        )

        if result.get("success"):
            log(
                "Scheduled backup completed successfully."
            )

            data = (
                result.get("data")
                or {}
            )

            log(
                "Archive: "
                f"{data.get('archive_path', '-')}"
            )

            return 0

        log(
            "Scheduled backup failed: "
            + "; ".join(
                result.get("errors")
                or ["Unknown error."]
            )
        )

        return 1

    except Exception as exc:
        log(
            f"Scheduled backup crashed: {exc}"
        )
        return 1
