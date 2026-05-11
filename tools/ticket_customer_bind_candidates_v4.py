from pathlib import Path
import sqlite3
import json
from datetime import datetime
from tools.db_path import current_sqlite_path

ROOT = Path(__file__).resolve().parents[1]
DB = current_sqlite_path()
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

report_path = REPORT_DIR / "派工案件客戶綁定候選_v4.txt"
json_path = REPORT_DIR / "ticket_customer_bind_candidates_v4.json"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

lines = []
items = []

lines.append("訊南 ERP 派工案件客戶綁定候選 v4")
lines.append(f"產生時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
lines.append(f"主資料庫：{DB}")
lines.append("")
lines.append("說明：本報告只做候選比對，不修改資料。")
lines.append("安全等級：")
lines.append("  safe_phone_unique：電話唯一命中，可考慮自動綁定")
lines.append("  possible_name_phone：姓名與電話同時命中，但需人工確認")
lines.append("  possible_name_only：只有姓名命中，需人工確認")
lines.append("  no_match：無候選")
lines.append("")

tickets = cur.execute("""
    SELECT
        id,
        ticket_no,
        case_type,
        status,
        customer_name,
        contact_name,
        contact_phone,
        service_address,
        customer_no,
        building_no,
        assigned_engineer,
        assigned_engineer_staff_code
    FROM tickets
    WHERE COALESCE(customer_no, '') = ''
       OR COALESCE(building_no, '') = ''
    ORDER BY id
""").fetchall()

lines.append("=" * 80)
lines.append(f"待綁定派工案件：{len(tickets)} 筆")
lines.append("=" * 80)

for t in tickets:
    ticket = dict(t)

    phone = (ticket.get("contact_phone") or "").strip()
    cname = (ticket.get("customer_name") or "").strip()
    contact = (ticket.get("contact_name") or "").strip()

    candidates = []
    match_type = "no_match"

    if phone:
        phone_rows = cur.execute("""
            SELECT
                c.customer_no,
                c.customer_name,
                c.customer_phone,
                c.building_no,
                c.service_address,
                c.account_status,
                b.name AS building_name,
                b.area AS building_area
            FROM customer_accounts c
            LEFT JOIN buildings b ON b.building_no = c.building_no
            WHERE c.customer_phone = :phone
            ORDER BY c.customer_no
            LIMIT 20
        """, {"phone": phone}).fetchall()

        for r in phone_rows:
            candidates.append(dict(r))

        if len(phone_rows) == 1:
            match_type = "safe_phone_unique"
        elif len(phone_rows) > 1:
            match_type = "possible_phone_multi"

    if not candidates and (cname or contact):
        name_rows = cur.execute("""
            SELECT
                c.customer_no,
                c.customer_name,
                c.customer_phone,
                c.building_no,
                c.service_address,
                c.account_status,
                b.name AS building_name,
                b.area AS building_area
            FROM customer_accounts c
            LEFT JOIN buildings b ON b.building_no = c.building_no
            WHERE c.customer_name = :cname
               OR c.customer_name = :contact
            ORDER BY c.customer_no
            LIMIT 20
        """, {"cname": cname, "contact": contact}).fetchall()

        for r in name_rows:
            candidates.append(dict(r))

        if name_rows:
            match_type = "possible_name_only"

    item = {
        "ticket": ticket,
        "match_type": match_type,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    items.append(item)

    lines.append("")
    lines.append("-" * 80)
    lines.append(f"案件：{ticket['ticket_no']}｜{ticket['case_type']}｜{ticket['status']}")
    lines.append(f"客戶：{ticket['customer_name']}｜電話：{ticket['contact_phone']}｜地址：{ticket['service_address']}")
    lines.append(f"目前 customer_no：{ticket['customer_no']}｜building_no：{ticket['building_no']}")
    lines.append(f"比對結果：{match_type}｜候選數：{len(candidates)}")

    if candidates:
        for c in candidates[:5]:
            lines.append(
                "  候選："
                f"{c.get('customer_no')}｜"
                f"{c.get('customer_name')}｜"
                f"{c.get('customer_phone')}｜"
                f"{c.get('building_no')}｜"
                f"{c.get('building_name')}｜"
                f"{c.get('service_address')}｜"
                f"{c.get('account_status')}"
            )
    else:
        lines.append("  無候選")

summary = {}
for item in items:
    summary[item["match_type"]] = summary.get(item["match_type"], 0) + 1

lines.append("")
lines.append("=" * 80)
lines.append("統計")
lines.append("=" * 80)
for k, v in sorted(summary.items()):
    lines.append(f"{k}: {v} 筆")

safe_count = summary.get("safe_phone_unique", 0)
lines.append("")
lines.append("=" * 80)
lines.append("下一步建議")
lines.append("=" * 80)
lines.append(f"1. safe_phone_unique 共 {safe_count} 筆，可在確認後進行自動綁定。")
lines.append("2. possible_* 類型需做人工確認頁。")
lines.append("3. no_match 類型可提供建立新客戶並綁定。")
lines.append("4. 目前不建議直接用姓名自動綁定，避免同名誤綁。")

report_path.write_text("\n".join(lines), encoding="utf-8")
json_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

conn.close()

print("OK: v4 candidate report generated")
print(report_path)
print(json_path)
