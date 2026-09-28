from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class UtilityResult:
    success: bool
    title: str
    message: str


class UtilitiesService:
    """Windows utility launcher and maintenance helpers."""

    CREATE_NO_WINDOW = getattr(
        subprocess,
        "CREATE_NO_WINDOW",
        0,
    )

    def _launch(
        self,
        command: list[str],
        title: str,
    ) -> UtilityResult:
        try:
            subprocess.Popen(
                command,
                creationflags=self.CREATE_NO_WINDOW,
            )

            return UtilityResult(
                True,
                title,
                f"{title} started successfully.",
            )

        except FileNotFoundError as exc:
            return UtilityResult(
                False,
                title,
                f"Windows component was not found: {exc}",
            )

        except OSError as exc:
            return UtilityResult(
                False,
                title,
                str(exc),
            )

    def _open(
        self,
        target: str,
        title: str,
    ) -> UtilityResult:
        try:
            os.startfile(target)

            return UtilityResult(
                True,
                title,
                f"{title} opened successfully.",
            )

        except OSError as exc:
            return UtilityResult(
                False,
                title,
                str(exc),
            )

    # ------------------------------------------------------------------
    # Applications
    # ------------------------------------------------------------------

    def calculator(self) -> UtilityResult:
        return self._launch(
            ["calc.exe"],
            "Calculator",
        )

    def notepad(self) -> UtilityResult:
        return self._launch(
            ["notepad.exe"],
            "Notepad",
        )

    def file_explorer(self) -> UtilityResult:
        return self._launch(
            ["explorer.exe"],
            "File Explorer",
        )

    def command_prompt(self) -> UtilityResult:
        return self._launch(
            ["cmd.exe"],
            "Command Prompt",
        )

    def powershell(self) -> UtilityResult:
        return self._launch(
            ["powershell.exe"],
            "PowerShell",
        )

    def task_manager(self) -> UtilityResult:
        return self._launch(
            ["taskmgr.exe"],
            "Task Manager",
        )

    # ------------------------------------------------------------------
    # Windows administration
    # ------------------------------------------------------------------

    def computer_management(self) -> UtilityResult:
        return self._open(
            "compmgmt.msc",
            "Computer Management",
        )

    def services(self) -> UtilityResult:
        return self._open(
            "services.msc",
            "Services",
        )

    def registry_editor(self) -> UtilityResult:
        return self._launch(
            ["regedit.exe"],
            "Registry Editor",
        )

    # ------------------------------------------------------------------
    # Windows Settings
    # ------------------------------------------------------------------

    def windows_settings(
        self,
        section: str = "system",
    ) -> UtilityResult:

        allowed = {
            "system": "ms-settings:system",
            "display": "ms-settings:display",
            "network": "ms-settings:network",
            "apps": "ms-settings:appsfeatures",
            "windows_update": (
                "ms-settings:windowsupdate"
            ),
            "accounts": "ms-settings:accounts",
        }

        target = allowed.get(section)

        if target is None:
            raise ValueError(
                f"Unknown Windows Settings section: "
                f"{section}"
            )

        names = {
            "system": "Windows Settings - System",
            "display": "Windows Settings - Display",
            "network": "Windows Settings - Network",
            "apps": "Windows Settings - Apps",
            "windows_update": (
                "Windows Settings - Windows Update"
            ),
            "accounts": "Windows Settings - Accounts",
        }

        return self._open(
            target,
            names[section],
        )

    # ------------------------------------------------------------------
    # Power actions
    # ------------------------------------------------------------------

    def restart(self) -> UtilityResult:
        return self._launch(
            [
                "shutdown.exe",
                "/r",
                "/t",
                "0",
            ],
            "Restart Windows",
        )

    def shutdown(self) -> UtilityResult:
        return self._launch(
            [
                "shutdown.exe",
                "/s",
                "/t",
                "0",
            ],
            "Shutdown Windows",
        )

    # ------------------------------------------------------------------
    # Temporary files
    # ------------------------------------------------------------------

    def clear_temp_files(self) -> UtilityResult:

        temp_roots = {
            Path(
                tempfile.gettempdir()
            ),
        }

        windows_temp = (
            Path(
                os.environ.get(
                    "WINDIR",
                    r"C:\Windows",
                )
            )
            / "Temp"
        )

        temp_roots.add(
            windows_temp
        )

        deleted_files = 0
        deleted_dirs = 0
        failed_items = 0

        for root in temp_roots:

            if not root.exists():
                continue

            try:
                children = list(
                    root.iterdir()
                )

            except OSError:
                failed_items += 1
                continue

            for item in children:

                try:

                    if (
                        item.is_dir()
                        and not item.is_symlink()
                    ):
                        shutil.rmtree(item)
                        deleted_dirs += 1

                    else:
                        item.unlink()
                        deleted_files += 1

                except (
                    OSError,
                    PermissionError,
                ):
                    failed_items += 1

        message = (
            "Temporary file cleanup completed.\n\n"
            f"Files deleted: {deleted_files}\n"
            f"Folders deleted: {deleted_dirs}\n"
            f"Items skipped/in use: {failed_items}"
        )

        return UtilityResult(
            True,
            "Clear Temporary Files",
            message,
        )

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def execute(
        self,
        operation: str,
        **kwargs,
    ) -> UtilityResult:

        operations = {
            "calculator": self.calculator,
            "notepad": self.notepad,
            "file_explorer": self.file_explorer,
            "command_prompt": self.command_prompt,
            "powershell": self.powershell,
            "task_manager": self.task_manager,
            "computer_management": (
                self.computer_management
            ),
            "services": self.services,
            "registry_editor": (
                self.registry_editor
            ),
            "restart": self.restart,
            "shutdown": self.shutdown,
            "clear_temp_files": (
                self.clear_temp_files
            ),
        }

        if operation.startswith(
            "settings_"
        ):
            return self.windows_settings(
                operation.removeprefix(
                    "settings_"
                )
            )

        handler = operations.get(
            operation
        )

        if handler is None:
            raise ValueError(
                f"Unknown utility operation: "
                f"{operation}"
            )

        return handler(**kwargs)