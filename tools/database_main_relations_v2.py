from pathlib import Path
import sqlite3
import json
from datetime import datetime
from tools.db_path import current_sqlite_path

ROOT = Path(__file__).resolve().parents[1]
DB = current_sqlite_path()
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

out_path = REPORT_DIR / "資料庫主關聯盤點_v2.txt"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
lines = []

def q(sql, params=None):
    return cur.execute(sql, params or {}).fetchall()

def one(sql, params=None):
    row = cur.execute(sql, params or {}).fetchone()
    if not row:
        return None
    return dict(row)

def section(title):
    lines.append("")
    lines.append("=" * 80)
    lines.append(title)
    lines.append("=" * 80)

lines.append("訊南 ERP 資料庫主關聯盤點 v2")
lines.append(f"產生時間：{now}")
lines.append(f"主資料庫：{DB}")

section("一、主表筆數")
for table in [
    "buildings",
    "customer_accounts",
    "customer_service_items",
    "employee_accounts",
    "employee_profiles",
    "employee_sessions",
    "sales_business_records",
    "tickets",
    "ticket_customer_candidates",
    "employee_leave_settings",
    "employee_rest_month_settings",
    "employee_proxy_settings",
    "company_holidays",
]:
    try:
        r = one(f'SELECT COUNT(*) AS c FROM "{table}"')
        lines.append(f"{table}: {r['c']} 筆")
    except Exception as e:
        lines.append(f"{table}: 讀取失敗 {e}")

section("二、員工帳號與員工資料一致性")
rows = q("""
    SELECT a.staff_code, a.display_name, a.department, a.role
    FROM employee_accounts a
    LEFT JOIN employee_profiles p ON p.staff_code = a.staff_code
    WHERE p.staff_code IS NULL
    ORDER BY a.staff_code
""")
lines.append("employee_accounts 有、employee_profiles 沒有：")
if rows:
    for r in rows:
        lines.append("  " + json.dumps(dict(r), ensure_ascii=False))
else:
    lines.append("  無")

rows = q("""
    SELECT p.staff_code, p.display_name, p.department, p.role
    FROM employee_profiles p
    LEFT JOIN employee_accounts a ON a.staff_code = p.staff_code
    WHERE a.staff_code IS NULL
    ORDER BY p.staff_code
""")
lines.append("")
lines.append("employee_profiles 有、employee_accounts 沒有：")
if rows:
    for r in rows:
        lines.append("  " + json.dumps(dict(r), ensure_ascii=False))
else:
    lines.append("  無")

section("三、客戶與大樓關聯")
r = one("""
    SELECT COUNT(*) AS c
    FROM customer_accounts c
    LEFT JOIN buildings b ON b.building_no = c.building_no
    WHERE b.building_no IS NULL
""")
lines.append(f"customer_accounts.building_no 找不到 buildings 的筆數：{r['c']}")

rows = q("""
    SELECT c.building_no, COUNT(*) AS c
    FROM customer_accounts c
    LEFT JOIN buildings b ON b.building_no = c.building_no
    WHERE b.building_no IS NULL
    GROUP BY c.building_no
    ORDER BY c DESC
    LIMIT 20
""")
if rows:
    lines.append("找不到的大樓代號前 20：")
    for r in rows:
        lines.append(f"  {r['building_no']}: {r['c']} 筆")

section("四、服務項目與客戶關聯")
r = one("""
    SELECT COUNT(*) AS c
    FROM customer_service_items s
    LEFT JOIN customer_accounts c ON c.customer_no = s.customer_no
    WHERE c.customer_no IS NULL
""")
lines.append(f"customer_service_items.customer_no 找不到 customer_accounts 的筆數：{r['c']}")

section("五、業務案件與大樓關聯")
r = one("""
    SELECT COUNT(*) AS c
    FROM sales_business_records s
    LEFT JOIN buildings b ON b.building_no = s.building_no
    WHERE b.building_no IS NULL
""")
lines.append(f"sales_business_records.building_no 找不到 buildings 的筆數：{r['c']}")

lines.append("")
lines.append("sales_business_records.owner 分布：")
rows = q("""
    SELECT owner, COUNT(*) AS c
    FROM sales_business_records
    GROUP BY owner
    ORDER BY c DESC, owner
""")
for r in rows:
    lines.append(f"  {r['owner']}: {r['c']} 筆")

lines.append("")
lines.append("sales owner 是否可對應員工姓名：")
rows = q("""
    SELECT s.owner, COUNT(*) AS c,
           p.staff_code,
           p.display_name,
           p.department,
           p.role
    FROM sales_business_records s
    LEFT JOIN employee_profiles p ON p.display_name = s.owner
    GROUP BY s.owner, p.staff_code
    ORDER BY s.owner
""")
for r in rows:
    lines.append("  " + json.dumps(dict(r), ensure_ascii=False))

section("六、派工案件與客戶、大樓關聯")
r = one("""
    SELECT COUNT(*) AS c
    FROM tickets t
    WHERE COALESCE(t.customer_no, '') = ''
""")
lines.append(f"tickets.customer_no 空白筆數：{r['c']}")

r = one("""
    SELECT COUNT(*) AS c
    FROM tickets t
    WHERE COALESCE(t.building_no, '') = ''
""")
lines.append(f"tickets.building_no 空白筆數：{r['c']}")

r = one("""
    SELECT COUNT(*) AS c
    FROM tickets t
    LEFT JOIN customer_accounts c ON c.customer_no = t.customer_no
    WHERE COALESCE(t.customer_no, '') <> ''
      AND c.customer_no IS NULL
""")
lines.append(f"tickets.customer_no 有值但找不到 customer_accounts 的筆數：{r['c']}")

r = one("""
    SELECT COUNT(*) AS c
    FROM tickets t
    LEFT JOIN buildings b ON b.building_no = t.building_no
    WHERE COALESCE(t.building_no, '') <> ''
      AND b.building_no IS NULL
""")
lines.append(f"tickets.building_no 有值但找不到 buildings 的筆數：{r['c']}")

lines.append("")
lines.append("tickets.assigned_engineer 分布：")
rows = q("""
    SELECT assigned_engineer, COUNT(*) AS c
    FROM tickets
    GROUP BY assigned_engineer
    ORDER BY c DESC, assigned_engineer
""")
for r in rows:
    lines.append(f"  {r['assigned_engineer']}: {r['c']} 筆")

lines.append("")
lines.append("assigned_engineer 是否可對應員工姓名：")
rows = q("""
    SELECT t.assigned_engineer, COUNT(*) AS c,
           p.staff_code,
           p.display_name,
           p.department,
           p.role
    FROM tickets t
    LEFT JOIN employee_profiles p ON p.display_name = t.assigned_engineer
    WHERE COALESCE(t.assigned_engineer, '') <> ''
    GROUP BY t.assigned_engineer, p.staff_code
    ORDER BY t.assigned_engineer
""")
for r in rows:
    lines.append("  " + json.dumps(dict(r), ensure_ascii=False))

section("七、目前建議整理方向")
lines.append(f"1. 主資料庫由 XUNNAN_DB_PATH/DATABASE_URL 決定，目前為：{DB}")
lines.append("2. 先不要刪除其他 .db，全部視為備份。")
lines.append("3. 員工主資料建議以 employee_profiles 為人事主檔，employee_accounts 為登入帳號。")
lines.append("4. 業務 owner 目前用姓名，建議下一階段新增 owner_staff_code。")
lines.append("5. 派工 assigned_engineer 目前用姓名，建議下一階段新增 assigned_engineer_staff_code。")
lines.append("6. tickets 已有 customer_no / building_no，但目前仍有空白，需要逐步人工/半自動綁定。")
lines.append("7. company_holidays 目前 0 筆，休假日曆若要同步國定假日，下一階段要先匯入假日表。")

out_path.write_text("\n".join(lines), encoding="utf-8")
conn.close()

print("OK: main relation report generated")
print(out_path)
