from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

print("CHECK FOLDER:")
cur.execute("""
EXEC master.dbo.xp_fileexist
    'C:\AIO Toolbox Backup'
""")

for row in cur.fetchall():
    print(row)

print()
print("CHECK ROOT C:")
cur.execute("""
EXEC master.dbo.xp_fileexist
    'C:\'
""")

for row in cur.fetchall():
    print(row)

cur.close()
cn.close()
