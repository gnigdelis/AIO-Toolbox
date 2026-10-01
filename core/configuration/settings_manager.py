from __future__ import annotations

import json
from pathlib import Path


class SettingsManager:
    DEFAULTS = {
        "backup_destination": "",
        "schedule_enabled": False,
        "schedule_interval_hours": 24,
        "schedule_start_time": "02:00",
        "selected_udl": "",
        "selected_targets": {
            "configuration": True,
            "form_path": True,
            "programdata": True,
            "printers": True,
            "registry": True,
            "sql": True,
        },
    }

    def __init__(self, settings_path) -> None:
        self.settings_path = Path(settings_path)

    def _defaults(self) -> dict:
        data = dict(self.DEFAULTS)
        data["selected_targets"] = dict(self.DEFAULTS["selected_targets"])
        data["backup_destination"] = str(
            self.settings_path.parent.parent / "backup"
        )
        return data

    def load(self) -> dict:
        defaults = self._defaults()

        if not self.settings_path.exists():
            return defaults

        try:
            raw = json.loads(
                self.settings_path.read_text(encoding="utf-8")
            )
        except (OSError, ValueError, json.JSONDecodeError):
            return defaults

        if not isinstance(raw, dict):
            return defaults

        result = defaults.copy()
        result.update(raw)

        result["backup_destination"] = str(
            result.get("backup_destination") or defaults["backup_destination"]
        ).strip()

        try:
            result["schedule_interval_hours"] = max(
                1, min(int(result.get("schedule_interval_hours", 24)), 168)
            )
        except (TypeError, ValueError):
            result["schedule_interval_hours"] = 24

        result["schedule_enabled"] = bool(
            result.get("schedule_enabled", False)
        )

        start_time = str(
            result.get("schedule_start_time") or "02:00"
        ).strip()

        if (
            len(start_time) != 5
            or start_time[2] != ":"
            or not start_time[:2].isdigit()
            or not start_time[3:].isdigit()
            or int(start_time[:2]) > 23
            or int(start_time[3:]) > 59
        ):
            start_time = "02:00"

        result["schedule_start_time"] = start_time
        result["selected_udl"] = str(
            result.get("selected_udl") or ""
        ).strip()

        saved_targets = result.get("selected_targets")
        targets = dict(defaults["selected_targets"])

        if isinstance(saved_targets, dict):
            for key in targets:
                if key in saved_targets:
                    targets[key] = bool(saved_targets[key])

        result["selected_targets"] = targets
        return result

    def save(self, settings: dict) -> dict:
        current = self.load()
        current.update(dict(settings))

        current["backup_destination"] = str(
            current.get("backup_destination")
            or self._defaults()["backup_destination"]
        ).strip()

        try:
            current["schedule_interval_hours"] = max(
                1, min(int(current.get("schedule_interval_hours", 24)), 168)
            )
        except (TypeError, ValueError):
            current["schedule_interval_hours"] = 24

        current["schedule_enabled"] = bool(
            current.get("schedule_enabled", False)
        )

        current["schedule_start_time"] = str(
            current.get("schedule_start_time") or "02:00"
        )

        current["selected_udl"] = str(
            current.get("selected_udl") or ""
        ).strip()

        targets = dict(self._defaults()["selected_targets"])
        saved_targets = current.get("selected_targets")

        if isinstance(saved_targets, dict):
            for key in targets:
                if key in saved_targets:
                    targets[key] = bool(saved_targets[key])

        current["selected_targets"] = targets

        self.settings_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp = self.settings_path.with_suffix(
            self.settings_path.suffix + ".tmp"
        )

        temp.write_text(
            json.dumps(
                current,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        temp.replace(self.settings_path)
        return current
