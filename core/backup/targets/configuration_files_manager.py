from pathlib import Path
import shutil

from core.common.result import Result


class ConfigurationFilesManager:

    CONFIGURATION_FILES = [
        r"C:\Program Files (x86)\Sunsoft Ltd\ExternalConnectionWebApi\External.Connection.Web.Api\appsettings.json",
        r"C:\Program Files (x86)\Sunsoft Ltd\ExternalTaxProvider\External.Tax.Provider\appsettings.production.json",
        r"C:\Program Files (x86)\Sunsoft Ltd\AmvrosiaWebService\Amvrosia.Web.Service\web.config",
        r"C:\Program Files (x86)\Sunsoft Ltd\WebPosReportClientApi\Web.Pos.Report.Client.Api\appsettings.json",
        r"C:\Program Files (x86)\Sunsoft Ltd\SnService\SnService.exe.config",
    ]

    def backup(self, destination_path):

        backed_up_files = []
        not_found_files = []
        copy_errors = []

        try:

            configuration_folder = (
                Path(destination_path)
                / "Configuration Files"
            )

            configuration_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            for file_path in self.CONFIGURATION_FILES:

                source = Path(file_path)

                if not source.exists():
                    not_found_files.append(file_path)
                    continue

                try:

                    service_folder = (
                        configuration_folder
                        / source.parent.name
                    )

                    service_folder.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    destination = (
                        service_folder
                        / source.name
                    )

                    shutil.copy2(
                        source,
                        destination,
                    )

                    backed_up_files.append(file_path)

                except Exception as error:

                    copy_errors.append(
                        f"{file_path} -> {error}"
                    )

            return Result.success(
                data={
                    "status": "SUCCESS",
                    "backed_up_files": backed_up_files,
                    "not_found_files": not_found_files,
                    "copy_errors": copy_errors,
                }
            )

        except Exception as error:

            return Result.error(str(error))