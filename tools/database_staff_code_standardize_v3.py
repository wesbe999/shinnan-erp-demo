from pathlib import Path
import sqlite3
from datetime import datetime

ROOT = Path(r"D:\Shinnan ERP")
DB = ROOT / "xunnan_dispatch.db"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

report_path = REPORT_DIR / "資料庫員工編號標準化_v3.txt"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

lines = []
lines.append("訊南 ERP 資料庫員工編號標準化 v3")
lines.append(f"產生時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
lines.append(f"主資料庫：{DB}")
lines.append("")

def table_columns(table):
    return {row["name"] for row in cur.execute(f'PRAGMA table_info("{table}")').fetchall()}

def add_column_if_missing(table, column, coltype):
    cols = table_columns(table)
    if column in cols:
        lines.append(f"SKIP: {table}.{column} 已存在")
        return False

    cur.execute(f'ALTER TABLE "{table}" ADD COLUMN "{column}" {coltype}')
    lines.append(f"ADD: {table}.{column} {coltype}")
    return True

lines.append("=" * 80)
lines.append("一、補欄位")
lines.append("=" * 80)

add_column_if_missing("sales_business_records", "owner_staff_code", "TEXT DEFAULT ''")
add_column_if_missing("tickets", "assigned_engineer_staff_code", "TEXT DEFAULT ''")

lines.append("")
lines.append("=" * 80)
lines.append("二、回填員工編號")
lines.append("=" * 80)

cur.execute("""
    UPDATE sales_business_records
    SET owner_staff_code = COALESCE((
        SELECT p.staff_code
        FROM employee_profiles p
        WHERE p.display_name = sales_business_records.owner
        LIMIT 1
    ), '')
    WHERE COALESCE(owner, '') <> ''
""")

lines.append(f"UPDATE: sales_business_records.owner_staff_code 回填完成，影響筆數：{cur.rowcount}")

cur.execute("""
    UPDATE tickets
    SET assigned_engineer_staff_code = COALESCE((
        SELECT p.staff_code
        FROM employee_profiles p
        WHERE p.display_name = tickets.assigned_engineer
        LIMIT 1
    ), '')
    WHERE COALESCE(assigned_engineer, '') <> ''
""")

lines.append(f"UPDATE: tickets.assigned_engineer_staff_code 回填完成，影響筆數：{cur.rowcount}")

conn.commit()

lines.append("")
lines.append("=" * 80)
lines.append("三、驗證結果")
lines.append("=" * 80)

rows = cur.execute("""
    SELECT owner, owner_staff_code, COUNT(*) AS count
    FROM sales_business_records
    GROUP BY owner, owner_staff_code
    ORDER BY owner
""").fetchall()

lines.append("業務 owner 對應：")
for row in rows:
    lines.append(f"  {row['owner']} -> {row['owner_staff_code']}：{row['count']} 筆")

rows = cur.execute("""
    SELECT assigned_engineer, assigned_engineer_staff_code, COUNT(*) AS count
    FROM tickets
    WHERE COALESCE(assigned_engineer, '') <> ''
    GROUP BY assigned_engineer, assigned_engineer_staff_code
    ORDER BY assigned_engineer
""").fetchall()

lines.append("")
lines.append("派工工程師 assigned_engineer 對應：")
for row in rows:
    lines.append(f"  {row['assigned_engineer']} -> {row['assigned_engineer_staff_code']}：{row['count']} 筆")

sales_missing = cur.execute("""
    SELECT COUNT(*) AS count
    FROM sales_business_records
    WHERE COALESCE(owner, '') <> ''
      AND COALESCE(owner_staff_code, '') = ''
""").fetchone()["count"]

dispatch_missing = cur.execute("""
    SELECT COUNT(*) AS count
    FROM tickets
    WHERE COALESCE(assigned_engineer, '') <> ''
      AND COALESCE(assigned_engineer_staff_code, '') = ''
""").fetchone()["count"]

lines.append("")
lines.append(f"業務 owner 有姓名但無 staff_code：{sales_missing} 筆")
lines.append(f"派工 assigned_engineer 有姓名但無 staff_code：{dispatch_missing} 筆")

lines.append("")
lines.append("=" * 80)
lines.append("四、保留事項")
lines.append("=" * 80)
lines.append("1. admin 是系統帳號，保留在 employee_accounts，不加入 employee_profiles。")
lines.append("2. HOUSE 是透天戶特殊代號，不新增到 buildings。")
lines.append("3. tickets.customer_no / tickets.building_no 仍有大量空白，下一階段再做案件與客戶半自動綁定。")
lines.append("4. company_holidays 目前 0 筆，下一階段再匯入國定假日資料。")

report_path.write_text("\n".join(lines), encoding="utf-8")

conn.close()

print("OK: staff code standardization complete")
print(report_path)
