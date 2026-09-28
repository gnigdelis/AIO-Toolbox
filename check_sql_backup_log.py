from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

cur.execute("""
EXEC master.dbo.xp_readerrorlog
    0,
    1,
    N'Backup'
""")

rows = cur.fetchall()

print("SQL SERVER BACKUP LOG")
print("=" * 80)

for row in rows:
    print(row)

cur.close()
cn.close()
