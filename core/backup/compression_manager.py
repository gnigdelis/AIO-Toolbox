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
