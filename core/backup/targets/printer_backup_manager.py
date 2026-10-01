from pathlib import Path
import subprocess

from core.common.result import Result


class PrinterBackupManager:

    PRINTBRM_PATH = (
        r"C:\Windows\System32\spool\tools\PrintBrm.exe"
    )

    def _create_printers_directory(self, destination_path):

        printers_directory = (
            Path(destination_path)
            / "Printers"
        )

        printers_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return printers_directory

    def _export_printers(
        self,
        printers_directory,
    ):

        export_file = (
            printers_directory
            / "PrinterBackup.printerExport"
        ).resolve()

        command = [
            self.PRINTBRM_PATH,
            "-B",
            "-F",
            str(export_file),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        success = export_file.exists()

        return {
            "success": success,
            "export_file": str(export_file),
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def backup(self, destination_path):

        try:

            printers_directory = (
                self._create_printers_directory(
                    destination_path
                )
            )

            export_result = (
                self._export_printers(
                    printers_directory
                )
            )

            return Result.success(
                data={
                    "status": "SUCCESS",
                    "printers_directory":
                        str(printers_directory),
                    "export_result":
                        export_result,
                }
            )

        except Exception as error:

            return Result.error(
                str(error)
            )