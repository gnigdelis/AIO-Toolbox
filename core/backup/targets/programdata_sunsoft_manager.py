from pathlib import Path
import shutil

from core.common.result import Result


class ProgramDataSunsoftManager:

    SOURCE_PATH = r"C:\ProgramData\Sunsoft"

    def backup(
        self,
        destination_path,
    ):

        try:

            source = Path(
                self.SOURCE_PATH
            )

            if not source.exists():

                return Result.success(

                    data={

                        "status": "NOT FOUND",

                        "target":
                        r"ProgramData\Sunsoft",

                    }

                )

            destination = (

                Path(destination_path)
                / "ProgramData"
                / "Sunsoft"

            )

            shutil.copytree(

                source,
                destination,
                dirs_exist_ok=True,

            )

            return Result.success(

                data={

                    "status": "SUCCESS",

                    "target":
                    r"ProgramData\Sunsoft",

                    "source_path":
                    str(source),

                    "destination_path":
                    str(destination),

                }

            )

        except Exception as error:

            return Result.error(
                str(error)
            )