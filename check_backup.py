from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

backup_path = (
    r"C:\Program Files\Microsoft SQL Server"
    r"\MSSQL17.MSSQLSERVER\MSSQL\Backup"
    r"\PaulGlifada_test.bak"
)

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)

cur = cn.cursor()

sql = f"""
BACKUP DATABASE [PaulGlifada]
TO DISK = N'{backup_path}'
WITH INIT, STATS = 10
"""

print("Executing backup...")
print(sql)

cur.execute(sql)

print("BACKUP COMMAND COMPLETED")

cur.close()
cn.close()
