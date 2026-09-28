from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

cur.execute("""
DECLARE @path nvarchar(4000);

SELECT @path =
    CAST(SERVERPROPERTY('InstanceDefaultBackupPath') AS nvarchar(4000))
    + N'\AIO_DIRECT_TEST.bak';

PRINT N'BACKUP PATH: ' + @path;

BACKUP DATABASE [PaulGlifada]
TO DISK = @path
WITH INIT, STATS = 10;
""")

print("SQL command returned.")

while cur.nextset():
    pass

cur.close()
cn.close()
