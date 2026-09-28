from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

cur.execute("""
SELECT
    name,
    type_desc,
    physical_name
FROM sys.master_files
WHERE database_id = DB_ID('PaulGlifada')
ORDER BY file_id
""")

print("DATABASE FILES")
print("=" * 80)

for row in cur.fetchall():
    print("Name         :", row[0])
    print("Type         :", row[1])
    print("Physical path:", row[2])
    print("-" * 80)

cur.close()
cn.close()
