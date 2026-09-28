from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)

cur = cn.cursor()

cur.execute("""
SELECT
    SERVERPROPERTY('MachineName'),
    SERVERPROPERTY('ServerName'),
    SERVERPROPERTY('ProductVersion'),
    SERVERPROPERTY('InstanceDefaultBackupPath')
""")

print(cur.fetchone())

cur.close()
cn.close()
