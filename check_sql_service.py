from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

cur.execute("""
SELECT
    servicename,
    service_account,
    status_desc,
    startup_type_desc
FROM sys.dm_server_services
WHERE servicename LIKE 'SQL Server (%'
""")

for row in cur.fetchall():
    print("SERVICE :", row[0])
    print("ACCOUNT :", row[1])
    print("STATUS  :", row[2])
    print("STARTUP :", row[3])
    print("-" * 60)

cur.close()
cn.close()
