from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"
backup_path = r"C:\Program Files\Microsoft SQL Server\MSSQL17.MSSQLSERVER\MSSQL\Backup\AIO_TEST_PaulGlifada.bak"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

sql = f"""
BACKUP DATABASE [PaulGlifada]
TO DISK = N'{backup_path}'
WITH INIT, STATS = 10
"""

print("Executing backup...")
print(backup_path)
print()

try:
    cur.execute(sql)
    print("BACKUP COMMAND COMPLETED")
except Exception as exc:
    print("BACKUP ERROR:")
    print(type(exc).__name__)
    print(exc)
    raise
finally:
    cur.close()
    cn.close()
