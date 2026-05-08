from pathlib import Path
import sqlite3
import json
from datetime import datetime

ROOT = Path(r"D:\Shinnan ERP")
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
out_path = REPORT_DIR / "資料庫盤點報告_v1.txt"
json_path = REPORT_DIR / "database_inventory_v1.json"

ignore_dirs = {
    ".venv",
    "__pycache__",
    ".git",
    "node_modules",
}

def is_ignored(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & ignore_dirs)

db_files = [
    p for p in ROOT.rglob("*.db")
    if not is_ignored(p)
]

inventory = {
    "generated_at": now,
    "root": str(ROOT),
    "db_files": [],
}

lines = []
lines.append("訊南 ERP 資料庫盤點報告 v1")
lines.append(f"產生時間：{now}")
lines.append(f"專案路徑：{ROOT}")
lines.append("")
lines.append("=" * 80)
lines.append("一、找到的資料庫檔案")
lines.append("=" * 80)

if not db_files:
    lines.append("未找到 .db 檔案。")
else:
    for db in db_files:
        lines.append(f"- {db}")

for db in db_files:
    rel = str(db.relative_to(ROOT))
    db_info = {
        "path": str(db),
        "relative_path": rel,
        "tables": [],
        "error": "",
    }

    lines.append("")
    lines.append("=" * 80)
    lines.append(f"二、資料庫：{rel}")
    lines.append("=" * 80)

    try:
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        tables = cur.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()

        if not tables:
            lines.append("沒有使用者資料表。")
            inventory["db_files"].append(db_info)
            conn.close()
            continue

        for t in tables:
            table = t["name"]

            try:
                count = cur.execute(f'SELECT COUNT(*) AS c FROM "{table}"').fetchone()["c"]
            except Exception as e:
                count = f"讀取失敗：{e}"

            cols = cur.execute(f'PRAGMA table_info("{table}")').fetchall()

            table_info = {
                "table": table,
                "count": count,
                "columns": [],
            }

            lines.append("")
            lines.append("-" * 80)
            lines.append(f"資料表：{table}")
            lines.append(f"筆數：{count}")
            lines.append("欄位：")

            for c in cols:
                col = {
                    "cid": c["cid"],
                    "name": c["name"],
                    "type": c["type"],
                    "notnull": c["notnull"],
                    "default": c["dflt_value"],
                    "pk": c["pk"],
                }
                table_info["columns"].append(col)

                lines.append(
                    f"  {c['cid']:>2}. {c['name']} | {c['type']} | "
                    f"NOT NULL={c['notnull']} | DEFAULT={c['dflt_value']} | PK={c['pk']}"
                )

            # 重要資料表抽樣
            if table in {
                "employee_profiles",
                "employee_accounts",
                "tickets",
                "customer_accounts",
                "buildings",
                "sales_business_records",
                "employee_leave_settings",
                "employee_rest_month_settings",
                "employee_proxy_settings",
            }:
                lines.append("前 5 筆抽樣：")
                try:
                    sample = cur.execute(f'SELECT * FROM "{table}" LIMIT 5').fetchall()
                    for row in sample:
                        safe = dict(row)
                        for key in list(safe.keys()):
                            if "hash" in key.lower() or "salt" in key.lower() or "password" in key.lower():
                                safe[key] = "***hidden***"
                        lines.append("  " + json.dumps(safe, ensure_ascii=False))
                except Exception as e:
                    lines.append(f"  抽樣失敗：{e}")

            # 常見重複檢查
            duplicate_checks = []
            col_names = {c["name"] for c in cols}

            if "staff_code" in col_names:
                duplicate_checks.append("staff_code")
            if "customer_no" in col_names:
                duplicate_checks.append("customer_no")
            if "building_no" in col_names:
                duplicate_checks.append("building_no")
            if "ticket_no" in col_names:
                duplicate_checks.append("ticket_no")

            for col in duplicate_checks:
                try:
                    dupes = cur.execute(f'''
                        SELECT "{col}" AS value, COUNT(*) AS c
                        FROM "{table}"
                        WHERE COALESCE("{col}", '') <> ''
                        GROUP BY "{col}"
                        HAVING COUNT(*) > 1
                        ORDER BY c DESC
                        LIMIT 10
                    ''').fetchall()

                    if dupes:
                        lines.append(f"疑似重複 {col}：")
                        for d in dupes:
                            lines.append(f"  {d['value']}：{d['c']} 筆")
                except Exception as e:
                    lines.append(f"  重複檢查 {col} 失敗：{e}")

            db_info["tables"].append(table_info)

        conn.close()

    except Exception as e:
        db_info["error"] = str(e)
        lines.append(f"讀取資料庫失敗：{e}")

    inventory["db_files"].append(db_info)

lines.append("")
lines.append("=" * 80)
lines.append("三、下一步建議")
lines.append("=" * 80)
lines.append("1. 先確認主資料庫是哪一個。")
lines.append("2. 確認 employee_profiles / employee_accounts 是否為員工主資料表。")
lines.append("3. 確認 buildings / customer_accounts / tickets / sales_business_records 的關聯欄位。")
lines.append("4. 第二步再做資料庫整理計畫，不直接改資料。")

out_path.write_text("\n".join(lines), encoding="utf-8")
json_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")

print("OK: database inventory generated")
print(out_path)
print(json_path)
