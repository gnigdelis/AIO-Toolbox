from pathlib import Path
import subprocess

from core.common.result import Result


class RegistryBackupManager:

    REGISTRY_TARGETS = [

        (
            r"HKLM\SOFTWARE\WOW6432Node\Sunsoft\System\Printers",
            "Sunsoft_System_Printers.reg",
        ),

        (
            r"HKCU\Software\VB and VBA Program Settings",
            "VB_and_VBA_Program_Settings.reg",
        ),

    ]

    def backup(self, destination_path):

        exported_files = []
        not_found_keys = []

        try:

            registry_folder = (
                Path(destination_path)
                / "Registry"
            )

            registry_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            for registry_key, filename in self.REGISTRY_TARGETS:

                output_file = (
                    registry_folder
                    / filename
                )

                result = subprocess.run(
                    [
                        "reg",
                        "export",
                        registry_key,
                        str(output_file),
                        "/y",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:

                    exported_files.append(
                        str(output_file)
                    )

                else:

                    not_found_keys.append(
                        registry_key
                    )

            return Result.success(
                data={
                    "status": "SUCCESS",
                    "exported_files": exported_files,
                    "not_found_keys": not_found_keys,
                }
            )

        except Exception as error:

            return Result.error(
                str(error)
            )