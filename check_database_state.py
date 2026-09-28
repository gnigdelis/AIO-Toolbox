from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

cur.execute("""
SELECT
    name,
    state_desc,
    user_access_desc,
    recovery_model_desc,
    is_read_only,
    is_in_standby,
    source_database_id
FROM sys.databases
WHERE name = 'PaulGlifada'
""")

row = cur.fetchone()

print("DATABASE STATUS")
print("=" * 60)
print("Name              :", row[0])
print("State             :", row[1])
print("User access       :", row[2])
print("Recovery model    :", row[3])
print("Read only         :", row[4])
print("In standby        :", row[5])
print("Source database ID:", row[6])

cur.close()
cn.close()
