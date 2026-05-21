import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect(r"D:\Shinnan ERP\xunnan_dispatch.db")
cur = conn.cursor()

# 取所有大樓，依目前編號排序（B000 排最後）
cur.execute("""
    SELECT id, building_no, name, area 
    FROM buildings 
    ORDER BY 
        CASE WHEN building_no = 'B000' THEN 9999 ELSE CAST(SUBSTR(building_no,2) AS INTEGER) END
""")
rows = cur.fetchall()

print(f"總筆數: {len(rows)}")

# 重新編號 B001 ~ B440，B000 測試機保留
new_mapping = []
counter = 1
for row_id, old_no, name, area in rows:
    if old_no == 'B000':
        new_no = 'B000'  # 測試機保留 B000
    else:
        new_no = f'B{counter:03d}'
        counter += 1
    new_mapping.append((new_no, row_id, old_no, name))

# 顯示變更預覽
changes = [(old, new, name) for new, row_id, old, name in new_mapping if old != new]
print(f"需要變更: {len(changes)} 筆")
print("前10個變更:")
for old, new, name in changes[:10]:
    print(f"  {old} → {new} ({name})")

print("\n確認無誤，執行更新...")

# 先用臨時編號避免衝突
for new_no, row_id, old_no, name in new_mapping:
    tmp = f'T{row_id}'
    cur.execute("UPDATE buildings SET building_no=? WHERE id=?", (tmp, row_id))
conn.commit()

# 再改成正式編號
for new_no, row_id, old_no, name in new_mapping:
    cur.execute("UPDATE buildings SET building_no=? WHERE id=?", (new_no, row_id))
conn.commit()

# 確認
cur.execute("SELECT COUNT(*) FROM buildings")
print(f"更新完成，總筆數: {cur.fetchone()[0]}")

cur.execute("SELECT building_no, name FROM buildings ORDER BY CAST(SUBSTR(building_no,2) AS INTEGER) LIMIT 5")
print("前5筆:")
for r in cur.fetchall(): print(f"  {r}")

cur.execute("SELECT building_no, name FROM buildings ORDER BY CAST(SUBSTR(building_no,2) AS INTEGER) DESC LIMIT 5")
print("後5筆:")
for r in cur.fetchall(): print(f"  {r}")

conn.close()
print("完成!")
