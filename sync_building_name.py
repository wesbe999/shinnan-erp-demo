import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect(r"D:\Shinnan ERP\xunnan_dispatch.db")
cur = conn.cursor()

cur.execute("SELECT building_no, name FROM buildings WHERE name LIKE '%永龍%' OR building_no='B012'")
print("buildings 永龍/B012:")
for r in cur.fetchall(): print(" ", r)

# 同步 building_name
print("\n同步 building_name...")
cur.execute("""
    UPDATE customer_accounts SET
        building_name = (
            SELECT name FROM buildings
            WHERE buildings.building_no = customer_accounts.building_no
        )
    WHERE building_no IS NOT NULL AND building_no != ''
""")
conn.commit()
print(f"更新: {cur.rowcount} 筆")

# 確認
cur.execute("SELECT COUNT(*) FROM customer_accounts WHERE building_name IS NOT NULL AND building_name != ''")
print(f"有 building_name: {cur.fetchone()[0]}")

conn.close()
