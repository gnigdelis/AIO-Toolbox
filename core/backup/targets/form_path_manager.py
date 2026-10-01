from pathlib import Path
import shutil

from core.common.result import Result


class FormPathManager:

    SOURCE_PATH = r"C:\form_path"

    def backup(self, destination_path):

        try:

            source = Path(self.SOURCE_PATH)

            if not source.exists():

                return Result.success(
                    data={
                        "status": "NOT FOUND",
                        "target": r"C:\form_path",
                    }
                )

            destination = (
                Path(destination_path)
                / "form_path"
            )

            shutil.copytree(
                source,
                destination,
                dirs_exist_ok=True,
            )

            return Result.success(
                data={
                    "status": "SUCCESS",
                    "target": r"C:\form_path",
                    "source_path": str(source),
                    "destination_path": str(destination),
                }
            )

        except Exception as error:

            return Result.error(str(error))