from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

cur.execute("""
SELECT
    SUSER_SNAME() AS LoginName,
    USER_NAME() AS DatabaseUser,
    DB_NAME() AS DatabaseName,
    @@SERVERNAME AS ServerName,
    IS_SRVROLEMEMBER('sysadmin') AS IsSysAdmin,
    HAS_PERMS_BY_NAME(DB_NAME(), 'DATABASE', 'BACKUP DATABASE') AS CanBackup
""")

row = cur.fetchone()

print("LoginName    :", row[0])
print("DatabaseUser :", row[1])
print("DatabaseName :", row[2])
print("ServerName   :", row[3])
print("IsSysAdmin   :", row[4])
print("CanBackup    :", row[5])

cur.close()
cn.close()
