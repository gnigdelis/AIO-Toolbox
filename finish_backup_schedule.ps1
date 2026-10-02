$ErrorActionPreference = 'Stop'
Set-Location 'C:\projects\AIO-Toolbox'

Write-Host 'Applying Backup + 7-Zip + Scheduler integration...' -ForegroundColor Cyan

$content = @'
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

'@
$path = Join-Path (Get-Location) 'core\configuration\settings_manager.py'
$dir = Split-Path $path -Parent
New-Item -ItemType Directory -Force -Path $dir | Out-Null
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host '  OK core\configuration\settings_manager.py' -ForegroundColor Green

$content = @'
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

'@
$path = Join-Path (Get-Location) 'core\configuration\windows_task_scheduler.py'
$dir = Split-Path $path -Parent
New-Item -ItemType Directory -Force -Path $dir | Out-Null
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host '  OK core\configuration\windows_task_scheduler.py' -ForegroundColor Green

$content = @'
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess


class CompressionManager:
    def __init__(self) -> None:
        self.seven_zip = self._find_7zip()

    @staticmethod
    def _find_7zip() -> str | None:
        candidates = [
            shutil.which("7z"),
            shutil.which("7z.exe"),
            shutil.which("7zz"),
            shutil.which("7zz.exe"),
            os.path.join(
                os.environ.get("ProgramFiles", ""),
                "7-Zip",
                "7z.exe",
            ),
            os.path.join(
                os.environ.get("ProgramFiles(x86)", ""),
                "7-Zip",
                "7z.exe",
            ),
        ]

        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                return str(Path(candidate))

        return None

    @staticmethod
    def _error(message: str) -> dict:
        return {
            "success": False,
            "status": "ERROR",
            "warnings": [],
            "errors": [message],
            "data": None,
        }

    def compress(self, source_path, archive_path) -> dict:
        source = Path(source_path)
        archive = Path(archive_path)

        if not source.is_dir():
            return self._error(
                f"Backup session folder not found: {source}"
            )

        if not self.seven_zip:
            return self._error(
                "7-Zip was not found. Install 7-Zip or add 7z.exe to PATH."
            )

        archive.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_archive = archive.with_name(
            archive.name + ".tmp.7z"
        )

        try:
            if temp_archive.exists():
                temp_archive.unlink()

            command = [
                self.seven_zip,
                "a",
                "-t7z",
                "-mx=5",
                str(temp_archive),
                str(source),
                "-r",
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )

            if result.returncode not in (0, 1):
                return self._error(
                    result.stderr
                    or result.stdout
                    or "7-Zip failed while creating the archive."
                )

            if (
                not temp_archive.exists()
                or temp_archive.stat().st_size == 0
            ):
                return self._error(
                    "7-Zip did not create a valid archive."
                )

            test = subprocess.run(
                [
                    self.seven_zip,
                    "t",
                    str(temp_archive),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )

            if test.returncode != 0:
                return self._error(
                    test.stderr
                    or test.stdout
                    or "7-Zip archive verification failed."
                )

            # Only after successful creation + verification do we replace
            # the previous archive.
            os.replace(
                temp_archive,
                archive,
            )

            return {
                "success": True,
                "status": "SUCCESS",
                "warnings": [],
                "errors": [],
                "data": {
                    "archive_path": str(archive),
                    "archive_size": archive.stat().st_size,
                },
            }

        except Exception as exc:
            return self._error(str(exc))

        finally:
            try:
                if temp_archive.exists():
                    temp_archive.unlink()
            except Exception:
                pass

    def finalize(self, source_path, archive_path) -> dict:
        source = Path(source_path)
        archive = Path(archive_path)

        try:
            if source.exists():
                shutil.rmtree(source)

            return {
                "success": True,
                "status": "SUCCESS",
                "warnings": [],
                "errors": [],
                "data": {
                    "archive_path": str(archive),
                },
            }

        except Exception as exc:
            return {
                "success": True,
                "status": "WARNING",
                "warnings": [
                    "Archive was created successfully, but temporary "
                    f"session cleanup failed: {exc}"
                ],
                "errors": [],
                "data": {
                    "archive_path": str(archive),
                },
            }

'@
$path = Join-Path (Get-Location) 'core\backup\compression_manager.py'
$dir = Split-Path $path -Parent
New-Item -ItemType Directory -Force -Path $dir | Out-Null
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host '  OK core\backup\compression_manager.py' -ForegroundColor Green

$content = @'
from __future__ import annotations

from pathlib import Path
from typing import Callable

from core.backup.backup_session_manager import BackupSessionManager
from core.backup.compression_manager import CompressionManager
from core.backup.targets.configuration_files_manager import ConfigurationFilesManager
from core.backup.targets.form_path_manager import FormPathManager
from core.backup.targets.programdata_sunsoft_manager import ProgramDataSunsoftManager
from core.backup.targets.registry_backup_manager import RegistryBackupManager
from core.backup.targets.printer_backup_manager import PrinterBackupManager
from core.backup.targets.sql_backup_manager import SQLBackupManager
from core.common.result import Result


class BackupEngine:
    TARGET_CONFIGURATION = "configuration"
    TARGET_FORM_PATH = "form_path"
    TARGET_PROGRAMDATA = "programdata"
    TARGET_PRINTERS = "printers"
    TARGET_REGISTRY = "registry"
    TARGET_SQL = "sql"

    def __init__(
        self,
        base_path,
        progress_callback: Callable[[int, str], None] | None = None,
    ) -> None:
        self.base_path = Path(base_path)
        self.progress_callback = progress_callback

        self.session_manager = BackupSessionManager()
        self.compression_manager = CompressionManager()

        self.configuration_manager = ConfigurationFilesManager()
        self.form_path_manager = FormPathManager()
        self.programdata_manager = ProgramDataSunsoftManager()
        self.registry_manager = RegistryBackupManager()
        self.printer_manager = PrinterBackupManager()

    def _progress(
        self,
        percentage: int,
        message: str,
    ) -> None:
        if not self.progress_callback:
            return

        try:
            self.progress_callback(
                int(percentage),
                str(message),
            )
        except Exception:
            pass

    @staticmethod
    def _normalise_targets(
        selected_targets,
    ) -> dict[str, bool]:
        defaults = {
            "configuration": True,
            "form_path": True,
            "programdata": True,
            "printers": True,
            "registry": True,
            "sql": True,
        }

        if isinstance(selected_targets, dict):
            defaults.update(
                {
                    key: bool(value)
                    for key, value in selected_targets.items()
                }
            )

        return defaults

    @staticmethod
    def _result_success(result) -> bool:
        return bool(
            isinstance(result, dict)
            and result.get("success")
        )

    @staticmethod
    def _result_errors(result) -> list[str]:
        if not isinstance(result, dict):
            return ["Invalid backup target result."]

        return [
            str(item)
            for item in (result.get("errors") or [])
        ]

    def _run_target(
        self,
        label,
        manager,
        session_path,
        percentage,
    ):
        self._progress(
            percentage,
            f"Backing up {label}...",
        )

        result = manager.backup(
            session_path
        )

        success = self._result_success(
            result
        )

        self._progress(
            percentage + 8,
            f"{label} completed."
            if success
            else f"{label} completed with warnings.",
        )

        return {
            "target": label,
            "success": success,
            "data": (
                result.get("data")
                if isinstance(result, dict)
                else None
            ),
            "warnings": (
                result.get("warnings", [])
                if isinstance(result, dict)
                else []
            ),
            "errors": self._result_errors(
                result
            ),
        }

    def run(
        self,
        selected_targets=None,
    ):
        targets = self._normalise_targets(
            selected_targets
        )

        if not any(targets.values()):
            return Result.error(
                "Please select at least one backup component."
            )

        try:
            self.base_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            self._progress(
                5,
                "Preparing backup...",
            )

            session = self.session_manager.create_session(
                self.base_path
            )

            if not session.get("success"):
                return session

            session_path = Path(
                session["data"]["session_path"]
            )

            results = []
            errors = []
            warnings = []

            jobs = [
                (
                    targets["configuration"],
                    "Configuration Files",
                    self.configuration_manager,
                    10,
                ),
                (
                    targets["form_path"],
                    r"C:\form_path",
                    self.form_path_manager,
                    25,
                ),
                (
                    targets["programdata"],
                    r"C:\ProgramData\Sunsoft",
                    self.programdata_manager,
                    40,
                ),
                (
                    targets["printers"],
                    "Windows Printers",
                    self.printer_manager,
                    55,
                ),
                (
                    targets["registry"],
                    "Registry",
                    self.registry_manager,
                    70,
                ),
            ]

            for enabled, label, manager, percentage in jobs:
                if not enabled:
                    continue

                item = self._run_target(
                    label,
                    manager,
                    session_path,
                    percentage,
                )

                results.append(item)
                warnings.extend(item["warnings"])
                errors.extend(item["errors"])

            if targets["sql"]:
                self._progress(
                    78,
                    "Backing up SQL databases...",
                )

                sql_result = SQLBackupManager().backup(
                    session_path
                )

                sql_item = {
                    "target": "SQL Databases",
                    "success": self._result_success(
                        sql_result
                    ),
                    "data": (
                        sql_result.get("data")
                        if isinstance(sql_result, dict)
                        else None
                    ),
                    "warnings": (
                        sql_result.get("warnings", [])
                        if isinstance(sql_result, dict)
                        else []
                    ),
                    "errors": self._result_errors(
                        sql_result
                    ),
                }

                results.append(
                    sql_item
                )
                warnings.extend(
                    sql_item["warnings"]
                )
                errors.extend(
                    sql_item["errors"]
                )

            failures = [
                item
                for item in results
                if not item["success"]
            ]

            if failures:
                self._progress(
                    100,
                    "Backup failed.",
                )

                return {
                    "success": False,
                    "status": "ERROR",
                    "warnings": warnings,
                    "errors": (
                        errors
                        or [
                            f"{item['target']} failed."
                            for item in failures
                        ]
                    ),
                    "data": {
                        "session_path": str(
                            session_path
                        ),
                        "results": results,
                        "selected_targets": targets,
                    },
                }

            archive_path = (
                self.base_path
                / f"{session_path.name}.7z"
            )

            self._progress(
                90,
                "Creating 7-Zip archive...",
            )

            compression = (
                self.compression_manager.compress(
                    source_path=session_path,
                    archive_path=archive_path,
                )
            )

            if not compression.get("success"):
                self._progress(
                    100,
                    "Compression failed.",
                )

                return {
                    "success": False,
                    "status": "ERROR",
                    "warnings": warnings,
                    "errors": (
                        self._result_errors(
                            compression
                        )
                        or [
                            "Unable to create the 7-Zip archive."
                        ]
                    ),
                    "data": {
                        "session_path": str(
                            session_path
                        ),
                        "archive_path": str(
                            archive_path
                        ),
                        "results": results,
                        "selected_targets": targets,
                    },
                }

            self._progress(
                97,
                "Cleaning temporary backup session...",
            )

            cleanup = (
                self.compression_manager.finalize(
                    source_path=session_path,
                    archive_path=archive_path,
                )
            )

            warnings.extend(
                cleanup.get("warnings") or []
            )

            self._progress(
                100,
                "Backup completed successfully.",
            )

            return {
                "success": True,
                "status": "SUCCESS",
                "warnings": warnings,
                "errors": [],
                "data": {
                    "session_path": str(
                        session_path
                    ),
                    "archive_path": str(
                        archive_path
                    ),
                    "selected_targets": targets,
                    "results": results,
                    "archive_size": (
                        archive_path.stat().st_size
                        if archive_path.exists()
                        else 0
                    ),
                },
            }

        except Exception as error:
            self._progress(
                100,
                "Backup failed.",
            )

            return Result.error(
                str(error)
            )

'@
$path = Join-Path (Get-Location) 'core\backup\backup_engine.py'
$dir = Split-Path $path -Parent
New-Item -ItemType Directory -Force -Path $dir | Out-Null
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host '  OK core\backup\backup_engine.py' -ForegroundColor Green

$content = @'
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

'@
$path = Join-Path (Get-Location) 'core\scheduled_backup.py'
$dir = Split-Path $path -Parent
New-Item -ItemType Directory -Force -Path $dir | Out-Null
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host '  OK core\scheduled_backup.py' -ForegroundColor Green

$content = @'
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

'@
$path = Join-Path (Get-Location) 'app.py'
$dir = Split-Path $path -Parent
New-Item -ItemType Directory -Force -Path $dir | Out-Null
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host '  OK app.py' -ForegroundColor Green

$content = @'
from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtCore import QThread, QTime, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from core.backup.backup_engine import BackupEngine
from core.configuration.settings_manager import SettingsManager
from core.configuration.windows_task_scheduler import WindowsTaskScheduler
from core.database.database_context import database_context

from ui.v2.widgets.page_layout import (
    PAGE_LAYOUT_STYLE,
    setup_page_layout,
)


def _app_base_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[3]


class BackupWorker(QThread):
    finished_result = Signal(object)
    failed = Signal(str)
    progress = Signal(int, str)

    def __init__(
        self,
        destination: str,
        selected_targets: dict[str, bool],
    ) -> None:
        super().__init__()

        self.destination = destination
        self.selected_targets = selected_targets

    def run(self) -> None:
        try:
            engine = BackupEngine(
                base_path=self.destination,
                progress_callback=(
                    lambda percentage, message:
                    self.progress.emit(
                        percentage,
                        message,
                    )
                ),
            )

            self.finished_result.emit(
                engine.run(
                    self.selected_targets
                )
            )

        except Exception as exc:
            self.failed.emit(
                str(exc)
            )


class BackupManagerPage(QWidget):

    def __init__(self) -> None:
        super().__init__()

        self.worker: BackupWorker | None = None

        self.settings_manager = SettingsManager(
            _app_base_path()
            / "config"
            / "settings.json"
        )

        self.settings = (
            self.settings_manager.load()
        )

        self.scheduler_manager = (
            WindowsTaskScheduler(
                _app_base_path()
            )
        )

        self._build_ui()
        self._connect_signals()
        self._load_settings()
        self._update_database_info()

    # ================================================================
    # UI
    # ================================================================

    def _build_ui(self) -> None:

        root, _, _ = setup_page_layout(
            self,
            "Backup Manager",
            "Create a complete backup of the selected system components.",
        )

        # ------------------------------------------------------------
        # Database
        # ------------------------------------------------------------

        database_card = QFrame()
        database_card.setObjectName(
            "contentCard"
        )

        database_layout = QVBoxLayout(
            database_card
        )

        database_layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )

        database_layout.setSpacing(
            8
        )

        database_title = QLabel(
            "Selected Database"
        )

        database_title.setObjectName(
            "sectionTitle"
        )

        self.database_label = QLabel(
            "No database selected"
        )

        self.server_label = QLabel(
            "Server: —"
        )

        self.udl_label = QLabel(
            "UDL: —"
        )

        self.udl_label.setWordWrap(
            True
        )

        for widget in (
            database_title,
            self.database_label,
            self.server_label,
            self.udl_label,
        ):
            database_layout.addWidget(
                widget
            )

        root.addWidget(
            database_card
        )

        # ------------------------------------------------------------
        # Components
        # ------------------------------------------------------------

        components_card = QFrame()
        components_card.setObjectName(
            "contentCard"
        )

        components_layout = QVBoxLayout(
            components_card
        )

        components_layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )

        components_layout.setSpacing(
            7
        )

        components_title = QLabel(
            "Backup Components"
        )

        components_title.setObjectName(
            "sectionTitle"
        )

        components_layout.addWidget(
            components_title
        )

        self.configuration_checkbox = QCheckBox(
            "Configuration Files"
        )

        self.form_path_checkbox = QCheckBox(
            r"C:\form_path"
        )

        self.programdata_checkbox = QCheckBox(
            r"C:\ProgramData\Sunsoft"
        )

        self.printers_checkbox = QCheckBox(
            "Windows Printers"
        )

        self.registry_checkbox = QCheckBox(
            "Registry"
        )

        self.sql_checkbox = QCheckBox(
            "SQL Databases"
        )

        self._backup_checkboxes = [
            self.configuration_checkbox,
            self.form_path_checkbox,
            self.programdata_checkbox,
            self.printers_checkbox,
            self.registry_checkbox,
            self.sql_checkbox,
        ]

        for checkbox in self._backup_checkboxes:
            components_layout.addWidget(
                checkbox
            )

        select_layout = QHBoxLayout()

        self.select_all_button = QPushButton(
            "SELECT ALL"
        )

        self.clear_all_button = QPushButton(
            "CLEAR ALL"
        )

        self.select_all_button.setObjectName(
            "secondaryButton"
        )

        self.clear_all_button.setObjectName(
            "secondaryButton"
        )

        select_layout.addWidget(
            self.select_all_button
        )

        select_layout.addWidget(
            self.clear_all_button
        )

        select_layout.addStretch()

        components_layout.addLayout(
            select_layout
        )

        root.addWidget(
            components_card
        )

        # ------------------------------------------------------------
        # Destination
        # ------------------------------------------------------------

        destination_card = QFrame()
        destination_card.setObjectName(
            "contentCard"
        )

        destination_layout = QVBoxLayout(
            destination_card
        )

        destination_layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )

        destination_layout.setSpacing(
            8
        )

        destination_title = QLabel(
            "Backup Destination"
        )

        destination_title.setObjectName(
            "sectionTitle"
        )

        self.destination_label = QLabel()

        self.destination_label.setWordWrap(
            True
        )

        self.browse_button = QPushButton(
            "BROWSE"
        )

        self.browse_button.setObjectName(
            "secondaryButton"
        )

        destination_layout.addWidget(
            destination_title
        )

        destination_layout.addWidget(
            self.destination_label
        )

        destination_layout.addWidget(
            self.browse_button,
            0,
        )

        root.addWidget(
            destination_card
        )

        # ------------------------------------------------------------
        # Schedule
        # ------------------------------------------------------------

        schedule_card = QFrame()
        schedule_card.setObjectName(
            "contentCard"
        )

        schedule_layout = QVBoxLayout(
            schedule_card
        )

        schedule_layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )

        schedule_layout.setSpacing(
            9
        )

        schedule_title = QLabel(
            "Scheduled Backup"
        )

        schedule_title.setObjectName(
            "sectionTitle"
        )

        schedule_layout.addWidget(
            schedule_title
        )

        self.schedule_enabled_checkbox = QCheckBox(
            "Enable automatic backup"
        )

        schedule_layout.addWidget(
            self.schedule_enabled_checkbox
        )

        schedule_row = QHBoxLayout()

        schedule_row.addWidget(
            QLabel("Run every:")
        )

        self.schedule_interval_spin = QSpinBox()

        self.schedule_interval_spin.setRange(
            1,
            168,
        )

        self.schedule_interval_spin.setSuffix(
            " hours"
        )

        schedule_row.addWidget(
            self.schedule_interval_spin
        )

        schedule_row.addSpacing(
            16
        )

        schedule_row.addWidget(
            QLabel("Start time:")
        )

        self.schedule_time_edit = QTimeEdit()

        self.schedule_time_edit.setDisplayFormat(
            "HH:mm"
        )

        schedule_row.addWidget(
            self.schedule_time_edit
        )

        schedule_row.addStretch()

        schedule_layout.addLayout(
            schedule_row
        )

        self.schedule_status_label = QLabel(
            "Scheduled backup is disabled."
        )

        self.schedule_status_label.setObjectName(
            "summaryText"
        )

        self.schedule_status_label.setWordWrap(
            True
        )

        schedule_layout.addWidget(
            self.schedule_status_label
        )

        self.save_schedule_button = QPushButton(
            "SAVE SCHEDULE"
        )

        self.save_schedule_button.setObjectName(
            "secondaryButton"
        )

        schedule_layout.addWidget(
            self.save_schedule_button,
            0,
        )

        root.addWidget(
            schedule_card
        )

        # ------------------------------------------------------------
        # Action
        # ------------------------------------------------------------

        action_frame = QFrame()

        action_frame.setObjectName(
            "summaryFrame"
        )

        action_layout = QHBoxLayout(
            action_frame
        )

        action_layout.setContentsMargins(
            18,
            14,
            18,
            14,
        )

        self.status_label = QLabel(
            "Ready"
        )

        self.progress_label = QLabel(
            ""
        )

        self.backup_button = QPushButton(
            "BACKUP NOW"
        )

        self.backup_button.setObjectName(
            "primaryButton"
        )

        self.backup_button.setMinimumHeight(
            42
        )

        self.backup_button.setMinimumWidth(
            150
        )

        action_layout.addWidget(
            self.status_label
        )

        action_layout.addWidget(
            self.progress_label
        )

        action_layout.addStretch()

        action_layout.addWidget(
            self.backup_button
        )

        root.addWidget(
            action_frame
        )

        root.addStretch()

        self.setStyleSheet(
            PAGE_LAYOUT_STYLE
        )

    # ================================================================
    # Signals
    # ================================================================

    def _connect_signals(self) -> None:

        self.backup_button.clicked.connect(
            self._start_backup
        )

        self.browse_button.clicked.connect(
            self._select_destination
        )

        self.select_all_button.clicked.connect(
            self._select_all
        )

        self.clear_all_button.clicked.connect(
            self._clear_all
        )

        self.save_schedule_button.clicked.connect(
            self._save_schedule
        )

        database_context.database_changed.connect(
            self._on_database_changed
        )

    # ================================================================
    # Settings
    # ================================================================

    def _load_settings(self) -> None:

        self.destination_label.setText(
            self.settings.get(
                "backup_destination",
                str(
                    Path.home()
                    / "AIO-Toolbox-Backups"
                ),
            )
        )

        targets = (
            self.settings.get(
                "selected_targets"
            )
            or {}
        )

        for key, checkbox in (
            self._target_checkbox_map().items()
        ):
            checkbox.setChecked(
                bool(
                    targets.get(
                        key,
                        True,
                    )
                )
            )

        self.schedule_enabled_checkbox.setChecked(
            bool(
                self.settings.get(
                    "schedule_enabled",
                    False,
                )
            )
        )

        self.schedule_interval_spin.setValue(
            int(
                self.settings.get(
                    "schedule_interval_hours",
                    24,
                )
            )
        )

        time_text = str(
            self.settings.get(
                "schedule_start_time",
                "02:00",
            )
        )

        parsed = QTime.fromString(
            time_text,
            "HH:mm",
        )

        self.schedule_time_edit.setTime(
            parsed
            if parsed.isValid()
            else QTime(2, 0)
        )

        self._refresh_schedule_status()

    def _target_checkbox_map(
        self,
    ) -> dict[str, QCheckBox]:

        return {
            "configuration":
                self.configuration_checkbox,

            "form_path":
                self.form_path_checkbox,

            "programdata":
                self.programdata_checkbox,

            "printers":
                self.printers_checkbox,

            "registry":
                self.registry_checkbox,

            "sql":
                self.sql_checkbox,
        }

    # ================================================================
    # Database
    # ================================================================

    def _on_database_changed(
        self,
        database: object,
    ) -> None:

        self._update_database_info()

    def _update_database_info(self) -> None:

        database = (
            database_context.active()
        )

        if not database:

            self.database_label.setText(
                "No database selected"
            )

            self.server_label.setText(
                "Server: —"
            )

            self.udl_label.setText(
                "UDL: —"
            )

            self.backup_button.setEnabled(
                False
            )

            return

        self.database_label.setText(
            "Database: "
            + str(
                database.get(
                    "name"
                )
                or "Unknown database"
            )
        )

        self.server_label.setText(
            "Server: "
            + str(
                database.get(
                    "server"
                )
                or "Unknown server"
            )
        )

        self.udl_label.setText(
            "UDL: "
            + str(
                database.get(
                    "path"
                )
                or "—"
            )
        )

        self.backup_button.setEnabled(
            True
        )

    # ================================================================
    # Components
    # ================================================================

    def _select_all(self) -> None:

        for checkbox in self._backup_checkboxes:
            checkbox.setChecked(
                True
            )

    def _clear_all(self) -> None:

        for checkbox in self._backup_checkboxes:
            checkbox.setChecked(
                False
            )

    def _get_selected_targets(
        self,
    ) -> dict[str, bool]:

        return {
            key:
                checkbox.isChecked()
            for key, checkbox
            in self._target_checkbox_map().items()
        }

    # ================================================================
    # Destination
    # ================================================================

    def _select_destination(self) -> None:

        current = (
            self.destination_label.text()
            .strip()
        )

        selected = (
            QFileDialog.getExistingDirectory(
                self,
                "Select Backup Destination",
                current
                if Path(current).exists()
                else str(Path.home()),
            )
        )

        if selected:
            self.destination_label.setText(
                selected
            )

    # ================================================================
    # Schedule
    # ================================================================

    def _save_schedule(self) -> None:

        selected_targets = (
            self._get_selected_targets()
        )

        if not any(
            selected_targets.values()
        ):
            QMessageBox.warning(
                self,
                "Backup Components",
                "Please select at least one backup component.",
            )
            return

        destination = Path(
            self.destination_label.text().strip()
        ).expanduser()

        if not str(
            destination
        ).strip():

            QMessageBox.warning(
                self,
                "Backup Destination",
                "Please select a backup destination.",
            )
            return

        try:
            destination.mkdir(
                parents=True,
                exist_ok=True,
            )

            active = (
                database_context.active()
            )

            selected_udl = (
                str(
                    active.get("path")
                )
                if active
                and active.get("path")
                else ""
            )

            if (
                selected_targets.get("sql")
                and not selected_udl
            ):
                QMessageBox.warning(
                    self,
                    "Database Required",
                    "SQL Databases is selected, but no database/UDL is selected.",
                )
                return

            time_text = (
                self.schedule_time_edit
                .time()
                .toString("HH:mm")
            )

            new_settings = {
                "backup_destination":
                    str(
                        destination.resolve()
                    ),

                "schedule_enabled":
                    self.schedule_enabled_checkbox.isChecked(),

                "schedule_interval_hours":
                    self.schedule_interval_spin.value(),

                "schedule_start_time":
                    time_text,

                "selected_udl":
                    selected_udl,

                "selected_targets":
                    selected_targets,
            }

            old_settings = dict(
                self.settings
            )

            saved = (
                self.settings_manager.save(
                    new_settings
                )
            )

            try:
                self.scheduler_manager.apply(
                    saved
                )

            except Exception:
                self.settings_manager.save(
                    old_settings
                )
                raise

            self.settings = saved

            self._refresh_schedule_status()

            QMessageBox.information(
                self,
                "Schedule Saved",
                (
                    "Scheduled backup settings were saved successfully."
                    if saved.get(
                        "schedule_enabled"
                    )
                    else
                    "Scheduled backup was disabled successfully."
                ),
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Schedule Error",
                (
                    "Unable to save the scheduled backup."
                    "\n\n"
                    f"{exc}"
                ),
            )

    def _refresh_schedule_status(
        self,
    ) -> None:

        if not self.settings.get(
            "schedule_enabled",
            False,
        ):

            self.schedule_status_label.setText(
                "Scheduled backup is disabled."
            )

            return

        interval = int(
            self.settings.get(
                "schedule_interval_hours",
                24,
            )
        )

        start_time = self.settings.get(
            "schedule_start_time",
            "02:00",
        )

        self.schedule_status_label.setText(
            "Scheduled backup is active"
            f" • Every {interval} hours"
            f" • Start: {start_time}"
        )

    # ================================================================
    # Manual Backup
    # ================================================================

    def _start_backup(self) -> None:

        database = (
            database_context.active()
        )

        if not database:

            QMessageBox.warning(
                self,
                "Database Required",
                "Please connect to a database first.",
            )

            return

        selected_targets = (
            self._get_selected_targets()
        )

        if not any(
            selected_targets.values()
        ):

            QMessageBox.warning(
                self,
                "Backup Components",
                "Please select at least one backup component.",
            )

            return

        destination = (
            self.destination_label
            .text()
            .strip()
        )

        if not destination:

            QMessageBox.warning(
                self,
                "Backup Destination",
                "Please select a backup destination.",
            )

            return

        if self.worker is not None:
            return

        self.backup_button.setEnabled(
            False
        )

        self.browse_button.setEnabled(
            False
        )

        self.select_all_button.setEnabled(
            False
        )

        self.clear_all_button.setEnabled(
            False
        )

        self.save_schedule_button.setEnabled(
            False
        )

        self.backup_button.setText(
            "BACKING UP..."
        )

        self.status_label.setText(
            "Preparing backup..."
        )

        self.progress_label.setText(
            "5%"
        )

        self.worker = BackupWorker(
            destination=destination,
            selected_targets=selected_targets,
        )

        self.worker.progress.connect(
            self._on_backup_progress
        )

        self.worker.finished_result.connect(
            self._on_backup_finished
        )

        self.worker.failed.connect(
            self._on_backup_failed
        )

        self.worker.finished.connect(
            self._cleanup_worker
        )

        self.worker.start()

    # ================================================================
    # Progress / Result
    # ================================================================

    def _on_backup_progress(
        self,
        percentage: int,
        message: str,
    ) -> None:

        self.progress_label.setText(
            f"{percentage}%"
        )

        self.status_label.setText(
            message
        )

    def _on_backup_finished(
        self,
        result: object,
    ) -> None:

        if (
            not isinstance(
                result,
                dict,
            )
            or not result.get(
                "success"
            )
        ):

            errors = (
                result.get(
                    "errors",
                    [],
                )
                if isinstance(
                    result,
                    dict,
                )
                else [
                    "Invalid backup result."
                ]
            )

            self._on_backup_failed(
                "\n".join(
                    str(error)
                    for error in errors
                )
            )

            return

        data = (
            result.get("data")
            or {}
        )

        archive = data.get(
            "archive_path"
        )

        self.status_label.setText(
            "Backup completed successfully."
        )

        self.progress_label.setText(
            "100%"
        )

        self.backup_button.setText(
            "BACKUP NOW"
        )

        self._set_controls_enabled(
            True
        )

        message = (
            "The backup completed successfully."
        )

        if archive:
            message += (
                "\n\nArchive:"
                f"\n{archive}"
            )

        QMessageBox.information(
            self,
            "Backup Completed",
            message,
        )

    def _on_backup_failed(
        self,
        message: str,
    ) -> None:

        self.status_label.setText(
            "Backup failed."
        )

        self.progress_label.setText(
            ""
        )

        self.backup_button.setText(
            "BACKUP NOW"
        )

        self._set_controls_enabled(
            True
        )

        QMessageBox.critical(
            self,
            "Backup Failed",
            (
                "The backup could not be completed."
                "\n\n"
                f"{message}"
            ),
        )

    def _set_controls_enabled(
        self,
        enabled: bool,
    ) -> None:

        self.backup_button.setEnabled(
            enabled
            and bool(
                database_context.active()
            )
        )

        self.browse_button.setEnabled(
            enabled
        )

        self.select_all_button.setEnabled(
            enabled
        )

        self.clear_all_button.setEnabled(
            enabled
        )

        self.save_schedule_button.setEnabled(
            enabled
        )

    def _cleanup_worker(self) -> None:

        if self.worker is None:
            return

        self.worker.deleteLater()
        self.worker = None

'@
$path = Join-Path (Get-Location) 'ui\v2\pages\backup\backup_manager_page.py'
$dir = Split-Path $path -Parent
New-Item -ItemType Directory -Force -Path $dir | Out-Null
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host '  OK ui\v2\pages\backup\backup_manager_page.py' -ForegroundColor Green

Write-Host ''
Write-Host 'Running syntax checks...' -ForegroundColor Cyan
python -m py_compile .\core\configuration\settings_manager.py .\core\configuration\windows_task_scheduler.py .\core\backup\compression_manager.py .\core\backup\backup_engine.py .\core\scheduled_backup.py .\ui\v2\pages\backup\backup_manager_page.py .\app.py
if ($LASTEXITCODE -ne 0) { throw 'Syntax check failed.' }
python -c "from core.backup.backup_engine import BackupEngine; from core.backup.compression_manager import CompressionManager; from core.configuration.settings_manager import SettingsManager; from core.configuration.windows_task_scheduler import WindowsTaskScheduler; from ui.v2.pages.backup.backup_manager_page import BackupManagerPage; print('IMPORTS OK')"
if ($LASTEXITCODE -ne 0) { throw 'Import check failed.' }
Write-Host ''
Write-Host 'DONE - next: run the app and configure Schedule.' -ForegroundColor Green