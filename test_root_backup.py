from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"
backup_path = r"C:\PaulGlifada_AIO_TEST.bak"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

sql = f"""
BACKUP DATABASE [PaulGlifada]
TO DISK = N'{backup_path}'
WITH INIT, STATS = 10
"""

print("Starting SQL Server backup...")
cur.execute(sql)
print("SQL Server backup command completed.")

cur.close()
cn.close()
