from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"
backup_path = r"C:\AIO Toolbox Backup\PaulGlifada_test.bak"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

sql = f"""
BACKUP DATABASE [PaulGlifada]
TO DISK = N'{backup_path}'
WITH INIT, STATS = 10
"""

print("Executing:")
print(sql)

cur.execute(sql)

print("BACKUP COMMAND COMPLETED")

cur.execute("""
SELECT TOP 1
    bmf.physical_device_name,
    bs.backup_start_date,
    bs.backup_finish_date,
    bs.backup_size
FROM msdb.dbo.backupset bs
INNER JOIN msdb.dbo.backupmediafamily bmf
    ON bs.media_set_id = bmf.media_set_id
WHERE bs.database_name = 'PaulGlifada'
ORDER BY bs.backup_finish_date DESC
""")

row = cur.fetchone()

print()
print("LATEST BACKUP:")
print("FILE  :", row[0])
print("START :", row[1])
print("FINISH:", row[2])
print("SIZE  :", row[3])

cur.close()
cn.close()
