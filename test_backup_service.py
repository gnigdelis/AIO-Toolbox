from core.backup.backup_service import BackupService

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

print("Starting BackupService test...")
print()

try:
    result = BackupService().backup_database(
        udl_path=udl
    )

    print("SUCCESS")
    print("Database:", result.database_name)
    print("Path    :", result.backup_path)
    print("Message :", result.message)

except Exception as exc:
    print("BACKUP FAILED")
    print(type(exc).__name__)
    print(exc)
