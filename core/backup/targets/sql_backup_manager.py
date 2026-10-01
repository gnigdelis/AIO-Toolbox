from pathlib import Path
from datetime import datetime
import shutil

import pyodbc

from core.common.result import Result
from core.database.database_context import database_context
from core.database.udl_reader import UDLReader


class SQLBackupManager:

    SYSTEM_DATABASES = [
        "master",
        "model",
        "msdb",
        "tempdb",
    ]

    # ---------------------------------------------------------
    # UDL
    # ---------------------------------------------------------

    def _get_active_udl(
        self,
    ):

        udl_path = (
            database_context.active_udl()
        )

        if not udl_path:

            raise RuntimeError(
                "No database selected. Please select a database before starting the backup."
            )

        return Path(
            udl_path
        )

    def _get_database_connection(
        self,
    ):

        udl_path = (
            self._get_active_udl()
        )

        reader = UDLReader(
            str(
                udl_path
            )
        )

        connection_string = (
            reader.get_connection_string()
        )

        return (
            reader,
            connection_string,
        )

    # ---------------------------------------------------------
    # Destination SQL Directory
    # ---------------------------------------------------------

    def _create_sql_directory(
        self,
        destination_path,
    ):

        sql_directory = (
            Path(destination_path)
            / "SQL"
        )

        sql_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return sql_directory

    # ---------------------------------------------------------
    # SQL Connection
    # ---------------------------------------------------------

    def _connect(
        self,
    ):

        reader, connection_string = (
            self._get_database_connection()
        )

        connection = pyodbc.connect(
            connection_string,
            autocommit=True,
            timeout=30,
        )

        return (
            reader,
            connection,
        )

    # ---------------------------------------------------------
    # Database List
    # ---------------------------------------------------------

    def _get_user_databases(
        self,
        connection,
    ):

        cursor = connection.cursor()

        try:

            cursor.execute(
                """
                SELECT name
                FROM sys.databases
                WHERE name NOT IN (?, ?, ?, ?)
                ORDER BY name
                """,
                self.SYSTEM_DATABASES[0],
                self.SYSTEM_DATABASES[1],
                self.SYSTEM_DATABASES[2],
                self.SYSTEM_DATABASES[3],
            )

            databases = []

            for row in cursor.fetchall():

                database_name = row[0]

                if database_name:

                    databases.append(
                        str(
                            database_name
                        )
                    )

            return databases

        finally:

            try:

                cursor.close()

            except Exception:

                pass

    # ---------------------------------------------------------
    # SQL Default Backup Directory
    # ---------------------------------------------------------

    def _get_sql_default_backup_directory(
        self,
        connection,
    ):

        #
        # First try the SQL Server instance property.
        #
        # This is the preferred method because the SQL Server
        # itself tells us where it expects backup files.
        #

        cursor = connection.cursor()

        try:

            cursor.execute(
                """
                SELECT CAST(
                    SERVERPROPERTY(
                        'InstanceDefaultBackupPath'
                    ) AS nvarchar(4000)
                )
                """
            )

            row = cursor.fetchone()

            if row and row[0]:

                value = str(
                    row[0]
                ).strip()

                if value:

                    return Path(
                        value
                    )

        except Exception:

            pass

        finally:

            try:

                cursor.close()

            except Exception:

                pass

        #
        # Fallback for older SQL Server versions.
        #
        # xp_instance_regread resolves the instance-specific
        # SQL Server registry path.
        #

        cursor = connection.cursor()

        try:

            backup_directory = None

            cursor.execute(
                """
                DECLARE @BackupDirectory NVARCHAR(4000);

                EXEC master.dbo.xp_instance_regread
                    N'HKEY_LOCAL_MACHINE',
                    N'Software\\Microsoft\\MSSQLServer\\MSSQLServer',
                    N'BackupDirectory',
                    @BackupDirectory OUTPUT;

                SELECT @BackupDirectory;
                """
            )

            while True:

                try:

                    row = cursor.fetchone()

                    if row is not None:

                        backup_directory = row[0]

                    break

                except pyodbc.Error:

                    if not cursor.nextset():

                        break

            if backup_directory:

                value = str(
                    backup_directory
                ).strip()

                if value:

                    return Path(
                        value
                    )

        except Exception:

            pass

        finally:

            try:

                cursor.close()

            except Exception:

                pass

        raise RuntimeError(
            "Could not determine the SQL Server default backup directory."
        )

    # ---------------------------------------------------------
    # SQL Identifier
    # ---------------------------------------------------------

    @staticmethod
    def _quote_identifier(
        value,
    ):

        return (
            "["
            + str(value).replace(
                "]",
                "]]",
            )
            + "]"
        )

    # ---------------------------------------------------------
    # Build Backup File Name
    # ---------------------------------------------------------

    @staticmethod
    def _build_backup_file_name(
        database_name,
    ):

        timestamp = datetime.now().strftime(
            "%d%m%Y_%H%M%S"
        )

        return (
            f"{database_name}_{timestamp}.bak"
        )

    # ---------------------------------------------------------
    # Backup Database
    # ---------------------------------------------------------

    def _backup_database(
        self,
        connection,
        database_name,
        sql_backup_directory,
        destination_sql_directory,
    ):

        backup_file_name = (
            self._build_backup_file_name(
                database_name
            )
        )

        #
        # SQL Server writes here.
        #

        temporary_backup_path = (
            Path(sql_backup_directory)
            / backup_file_name
        ).resolve()

        #
        # Final file that the Support Agent keeps.
        #

        destination_backup_path = (
            Path(destination_sql_directory)
            / backup_file_name
        ).resolve()

        database_identifier = (
            self._quote_identifier(
                database_name
            )
        )

        backup_path_sql = (
            str(
                temporary_backup_path
            )
            .replace(
                "'",
                "''",
            )
        )

        command = (
            f"BACKUP DATABASE "
            f"{database_identifier} "
            f"TO DISK = N'{backup_path_sql}' "
            f"WITH INIT"
        )

        cursor = connection.cursor()

        try:

            #
            # Remove a same-named old temporary file if it
            # somehow exists.
            #

            if temporary_backup_path.exists():

                try:

                    temporary_backup_path.unlink()

                except Exception:

                    pass

            #
            # Execute SQL backup.
            #

            cursor.execute(
                command
            )

            while cursor.nextset():

                pass

            #
            # Verify that SQL Server actually created
            # a non-empty backup file.
            #

            if not temporary_backup_path.exists():

                return {
                    "success": False,
                    "database_name": database_name,
                    "backup_file": str(
                        destination_backup_path
                    ),
                    "temporary_backup_file": str(
                        temporary_backup_path
                    ),
                    "stdout": "",
                    "stderr": (
                        "SQL Server reported completion, "
                        "but the backup file was not created."
                    ),
                }

            temporary_size = (
                temporary_backup_path.stat().st_size
            )

            if temporary_size <= 0:

                return {
                    "success": False,
                    "database_name": database_name,
                    "backup_file": str(
                        destination_backup_path
                    ),
                    "temporary_backup_file": str(
                        temporary_backup_path
                    ),
                    "stdout": "",
                    "stderr": (
                        "SQL Server created an empty "
                        "backup file."
                    ),
                }

            #
            # Make sure the destination directory exists.
            #

            Path(
                destination_sql_directory
            ).mkdir(
                parents=True,
                exist_ok=True,
            )

            #
            # Remove any old destination file.
            #

            if destination_backup_path.exists():

                try:

                    destination_backup_path.unlink()

                except Exception as error:

                    return {
                        "success": False,
                        "database_name": database_name,
                        "backup_file": str(
                            destination_backup_path
                        ),
                        "temporary_backup_file": str(
                            temporary_backup_path
                        ),
                        "stdout": "",
                        "stderr": (
                            "Could not replace the existing "
                            f"destination backup file: {error}"
                        ),
                    }

            #
            # Copy the SQL-created .bak from the SQL Server
            # backup directory to the Support Agent destination.
            #

            shutil.copy2(
                temporary_backup_path,
                destination_backup_path,
            )

            #
            # Verify final copy.
            #

            if not destination_backup_path.exists():

                return {
                    "success": False,
                    "database_name": database_name,
                    "backup_file": str(
                        destination_backup_path
                    ),
                    "temporary_backup_file": str(
                        temporary_backup_path
                    ),
                    "stdout": "",
                    "stderr": (
                        "The SQL backup was created, "
                        "but the final backup file could "
                        "not be created in the destination."
                    ),
                }

            destination_size = (
                destination_backup_path.stat().st_size
            )

            if destination_size <= 0:

                return {
                    "success": False,
                    "database_name": database_name,
                    "backup_file": str(
                        destination_backup_path
                    ),
                    "temporary_backup_file": str(
                        temporary_backup_path
                    ),
                    "stdout": "",
                    "stderr": (
                        "The final copied SQL backup "
                        "file is empty."
                    ),
                }

            #
            # Success.
            #

            return {
                "success": True,
                "database_name": database_name,
                "backup_file": str(
                    destination_backup_path
                ),
                "temporary_backup_file": str(
                    temporary_backup_path
                ),
                "stdout": (
                    "Backup completed successfully."
                ),
                "stderr": "",
            }

        except Exception as error:

            return {
                "success": False,
                "database_name": database_name,
                "backup_file": str(
                    destination_backup_path
                ),
                "temporary_backup_file": str(
                    temporary_backup_path
                ),
                "stdout": "",
                "stderr": str(
                    error
                ),
            }

        finally:

            try:

                cursor.close()

            except Exception:

                pass

            #
            # If the backup was successfully copied, remove
            # the temporary SQL Server copy.
            #
            # If copy failed, leave it in place so the failed
            # backup can be diagnosed/recovered.
            #

            try:

                if (
                    temporary_backup_path.exists()
                    and destination_backup_path.exists()
                    and destination_backup_path.stat().st_size > 0
                ):

                    temporary_backup_path.unlink()

            except Exception:

                pass

    # ---------------------------------------------------------
    # All Databases
    # ---------------------------------------------------------

    def _backup_all_databases(
        self,
        connection,
        user_databases,
        sql_backup_directory,
        destination_sql_directory,
    ):

        successful_backups = []
        failed_backups = []

        for database_name in user_databases:

            backup_result = (
                self._backup_database(
                    connection=connection,
                    database_name=database_name,
                    sql_backup_directory=sql_backup_directory,
                    destination_sql_directory=destination_sql_directory,
                )
            )

            if backup_result["success"]:

                successful_backups.append(
                    backup_result
                )

            else:

                failed_backups.append(
                    backup_result
                )

        return (
            successful_backups,
            failed_backups,
        )

    # ---------------------------------------------------------
    # Information File
    # ---------------------------------------------------------

    def _generate_sql_information_file(
        self,
        sql_directory,
        sql_backup_directory,
        udl_path,
        server_name,
        database_name,
        user_databases,
        successful_backups,
        failed_backups,
    ):

        information_file = (
            sql_directory
            / "SQL_Information.txt"
        )

        with open(
            information_file,
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                "SUNSOFT SQL BACKUP INFORMATION\n"
            )

            file.write(
                "=" * 50
                + "\n\n"
            )

            file.write(
                f"UDL : {udl_path}\n"
            )

            file.write(
                f"SQL Server : {server_name}\n"
            )

            file.write(
                f"Selected Database : {database_name}\n"
            )

            file.write(
                f"SQL Backup Directory : "
                f"{sql_backup_directory}\n\n"
            )

            file.write(
                "USER DATABASES\n"
            )

            file.write(
                "-" * 50
                + "\n"
            )

            if not user_databases:

                file.write(
                    "NONE\n"
                )

            else:

                for database in user_databases:

                    file.write(
                        f"{database}\n"
                    )

            file.write(
                "\nSUCCESSFUL BACKUPS\n"
            )

            file.write(
                "-" * 50
                + "\n"
            )

            if not successful_backups:

                file.write(
                    "NONE\n"
                )

            else:

                for backup in successful_backups:

                    file.write(
                        f"{Path(backup['backup_file']).name}\n"
                    )

            file.write(
                "\nFAILED BACKUPS\n"
            )

            file.write(
                "-" * 50
                + "\n"
            )

            if not failed_backups:

                file.write(
                    "NONE\n"
                )

            else:

                for backup in failed_backups:

                    file.write(
                        f"{backup['database_name']} : "
                        f"{backup['stderr']}\n"
                    )

        return str(
            information_file
        )

    # ---------------------------------------------------------
    # Main Backup
    # ---------------------------------------------------------

    def backup(
        self,
        destination_path,
    ):

        connection = None

        try:

            #
            # UDL
            #

            udl_path = (
                self._get_active_udl()
            )

            reader = UDLReader(
                str(
                    udl_path
                )
            )

            #
            # Server
            #

            server_name = (
                reader.get_server_name()
            )

            #
            # Selected database
            #

            selected_database = (
                reader.get_database_name()
            )

            if not selected_database:

                return Result.error(
                    "The selected UDL does not contain a database name."
                )

            #
            # Final destination SQL directory.
            #

            sql_directory = (
                self._create_sql_directory(
                    destination_path
                )
            )

            #
            # Connect to SQL Server.
            #

            connection = pyodbc.connect(
                reader.get_connection_string(),
                autocommit=True,
                timeout=30,
            )

            #
            # Find the SQL Server's own default backup path.
            #

            sql_backup_directory = (
                self._get_sql_default_backup_directory(
                    connection
                )
            )

            #
            # Verify that the SQL backup directory is visible
            # to the Agent process. We do NOT create it here.
            # SQL Server must own/use this location.
            #

            if not sql_backup_directory.exists():

                return Result.error(
                    (
                        "The SQL Server default backup "
                        "directory does not exist:\n"
                        f"{sql_backup_directory}"
                    )
                )

            #
            # Get all user databases.
            #

            user_databases = (
                self._get_user_databases(
                    connection
                )
            )

            #
            # Selected database is always included first.
            #

            databases_to_backup = [
                selected_database
            ]

            #
            # Include any additional user databases.
            #

            for database_name in user_databases:

                if (
                    database_name
                    not in databases_to_backup
                ):

                    databases_to_backup.append(
                        database_name
                    )

            #
            # Perform SQL backups.
            #

            successful_backups, failed_backups = (
                self._backup_all_databases(
                    connection=connection,
                    user_databases=databases_to_backup,
                    sql_backup_directory=sql_backup_directory,
                    destination_sql_directory=sql_directory,
                )
            )

            #
            # Generate information file.
            #

            sql_information_file = (
                self._generate_sql_information_file(
                    sql_directory=sql_directory,
                    sql_backup_directory=sql_backup_directory,
                    udl_path=str(
                        udl_path
                    ),
                    server_name=server_name,
                    database_name=selected_database,
                    user_databases=databases_to_backup,
                    successful_backups=successful_backups,
                    failed_backups=failed_backups,
                )
            )

            #
            # Files generated in the final SQL directory.
            #

            generated_files = [

                Path(
                    backup["backup_file"]
                ).name

                for backup
                in successful_backups
            ]

            generated_files.append(
                Path(
                    sql_information_file
                ).name
            )

            #
            # If none of the databases could be backed up,
            # report SQL as failed.
            #

            if not successful_backups:

                return Result.error(
                    "No SQL databases were backed up."
                )

            #
            # Return successful result even if some databases
            # failed, because successful backups exist.
            #

            return Result.success(
                data={
                    "status": "SUCCESS",
                    "udl_path": str(
                        udl_path
                    ),
                    "server_name": server_name,
                    "selected_database":
                        selected_database,
                    "sql_directory": str(
                        sql_directory
                    ),
                    "sql_backup_directory":
                        str(
                            sql_backup_directory
                        ),
                    "user_databases":
                        databases_to_backup,
                    "successful_backups":
                        successful_backups,
                    "failed_backups":
                        failed_backups,
                    "generated_files":
                        generated_files,
                }
            )

        except Exception as error:

            return Result.error(
                str(
                    error
                )
            )

        finally:

            if connection is not None:

                try:

                    connection.close()

                except Exception:

                    pass