from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

cur.execute("""
SELECT
    SERVERPROPERTY('ProductVersion') AS ProductVersion,
    SERVERPROPERTY('Edition') AS Edition,
    SERVERPROPERTY('InstanceName') AS InstanceName,
    SERVERPROPERTY('InstanceDefaultBackupPath') AS DefaultBackupPath
""")

row = cur.fetchone()

print("ProductVersion :", row[0])
print("Edition        :", row[1])
print("InstanceName   :", row[2])
print("DefaultPath    :", row[3])

cur.close()
cn.close()
