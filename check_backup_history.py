from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

cur.execute("""
SELECT
    bs.database_name,
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

for row in cur.fetchall():
    print("DATABASE :", row[0])
    print("FILE     :", row[1])
    print("START    :", row[2])
    print("FINISH   :", row[3])
    print("SIZE     :", row[4])
    print("-" * 60)

cur.close()
cn.close()
