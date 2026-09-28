from core.database.database_connection import DatabaseConnection

udl = r"C:\ProgramData\Sunsoft\BackOffice\PaulGlifada.udl"

c = DatabaseConnection(udl)
cn = c.connect(autocommit=True)
cur = cn.cursor()

for keyword in (
    "PaulGlifada",
    "Operating system error",
    "Error: 18210",
    "Error: 3201",
    "Error: 3013",
):
    print()
    print("=" * 80)
    print("SEARCH:", keyword)
    print("=" * 80)

    cur.execute(
        """
        EXEC master.dbo.xp_readerrorlog
            0,
            1,
            ?
        """,
        keyword,
    )

    for row in cur.fetchall():
        print(row)

cur.close()
cn.close()
