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
