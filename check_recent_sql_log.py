from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

cur.execute("""
EXEC master.dbo.xp_readerrorlog
    0,
    1
""")

rows = cur.fetchall()

print("RECENT SQL SERVER ERROR LOG")
print("=" * 100)

for row in rows:
    text = str(row)
    if "Backup" in text or "backup" in text or "PaulGlifada" in text or "Error" in text:
        print(row)

cur.close()
cn.close()
