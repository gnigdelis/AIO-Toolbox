from __future__ import annotations

from pathlib import Path
import subprocess
import sys


class WindowsTaskScheduler:
    TASK_NAME = "AIO Toolbox - Automatic Backup"

    def __init__(self, app_base_path) -> None:
        self.app_base_path = Path(app_base_path).resolve()

    def _action(self) -> str:
        if getattr(sys, "frozen", False):
            executable = Path(sys.executable).resolve()
            return f'"{executable}" --scheduled-backup'

        executable = Path(sys.executable).resolve()
        script = self.app_base_path / "app.py"
        return f'"{executable}" "{script}" --scheduled-backup'

    def install(self, interval_hours: int, start_time: str) -> dict:
        interval_hours = int(interval_hours)

        if not 1 <= interval_hours <= 168:
            raise ValueError(
                "Schedule interval must be between 1 and 168 hours."
            )

        start_time = str(start_time).strip()

        if (
            len(start_time) != 5
            or start_time[2] != ":"
            or not start_time[:2].isdigit()
            or not start_time[3:].isdigit()
        ):
            raise ValueError(
                "Schedule start time must use HH:mm format."
            )

        command = [
            "schtasks",
            "/Create",
            "/TN",
            self.TASK_NAME,
            "/SC",
            "HOURLY",
            "/MO",
            str(interval_hours),
            "/ST",
            start_time,
            "/TR",
            self._action(),
            "/RL",
            "HIGHEST",
            "/F",
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr
                or result.stdout
                or "Unable to create the Windows scheduled task."
            )

        return {
            "success": True,
            "task_name": self.TASK_NAME,
            "interval_hours": interval_hours,
            "start_time": start_time,
        }

    def remove(self) -> dict:
        result = subprocess.run(
            [
                "schtasks",
                "/Delete",
                "/TN",
                self.TASK_NAME,
                "/F",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        if result.returncode != 0:
            combined = (result.stderr or "") + (result.stdout or "")
            lowered = combined.lower()

            if (
                "cannot find" in lowered
                or "does not exist" in lowered
            ):
                return {
                    "success": True,
                    "removed": False,
                }

            raise RuntimeError(
                result.stderr
                or result.stdout
                or "Unable to remove the Windows scheduled task."
            )

        return {
            "success": True,
            "removed": True,
        }

    def apply(self, settings: dict) -> dict:
        if not bool(
            settings.get("schedule_enabled", False)
        ):
            return self.remove()

        return self.install(
            settings.get("schedule_interval_hours", 24),
            settings.get("schedule_start_time", "02:00"),
        )
