from pathlib import Path
import sqlite3
import json
from datetime import datetime

ROOT = Path(r"D:\Shinnan ERP")
DB = ROOT / "xunnan_dispatch.db"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

report_path = REPORT_DIR / "派工案件人工處理佇列同步_v5.txt"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

lines = []
lines.append("訊南 ERP 派工案件人工處理佇列同步 v5")
lines.append(f"產生時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
lines.append(f"主資料庫：{DB}")
lines.append("")

tickets = cur.execute("""
    SELECT
        id,
        ticket_no,
        customer_name,
        contact_name,
        contact_phone,
        service_address,
        customer_no,
        building_no
    FROM tickets
    WHERE COALESCE(customer_no, '') = ''
       OR COALESCE(building_no, '') = ''
    ORDER BY id
""").fetchall()

summary = {
    "待建立客戶": 0,
    "待人工確認": 0,
    "已略過": 0,
}

lines.append("=" * 80)
lines.append(f"待處理派工案件：{len(tickets)} 筆")
lines.append("=" * 80)

for t in tickets:
    ticket_id = t["id"]
    ticket_no = t["ticket_no"]
    phone = (t["contact_phone"] or "").strip()
    cname = (t["customer_name"] or "").strip()
    contact = (t["contact_name"] or "").strip()

    candidates = []

    if phone:
        rows = cur.execute("""
            SELECT
                c.customer_no,
                c.building_no,
                c.customer_name,
                c.customer_phone,
                c.service_address
            FROM customer_accounts c
            WHERE c.customer_phone = :phone
            ORDER BY c.customer_no
            LIMIT 20
        """, {"phone": phone}).fetchall()
        candidates = [dict(r) for r in rows]

    if not candidates and (cname or contact):
        rows = cur.execute("""
            SELECT
                c.customer_no,
                c.building_no,
                c.customer_name,
                c.customer_phone,
                c.service_address
            FROM customer_accounts c
            WHERE c.customer_name = :cname
               OR c.customer_name = :contact
            ORDER BY c.customer_no
            LIMIT 20
        """, {"cname": cname, "contact": contact}).fetchall()
        candidates = [dict(r) for r in rows]

    if len(candidates) == 1 and not phone:
        # 只有姓名命中，不能自動綁，只做人工候選
        c = candidates[0]
        match_type = "possible_name_only"
        match_score = 40
        review_status = "待人工確認"
        review_note = (
            "僅姓名命中，電話或地址未一致，不可自動綁定。"
            f"候選客戶：{c.get('customer_no', '')} / {c.get('customer_name', '')}"
        )
        candidate_customer_no = c.get("customer_no", "") or ""
        candidate_building_no = c.get("building_no", "") or ""
        summary["待人工確認"] += 1

    elif len(candidates) == 1:
        # 電話唯一才可能安全，但本批資料實際上沒有此情況；保守仍列人工確認
        c = candidates[0]
        match_type = "possible_phone_unique"
        match_score = 80
        review_status = "待人工確認"
        review_note = (
            "電話唯一命中，但本階段仍保守列入人工確認。"
            f"候選客戶：{c.get('customer_no', '')} / {c.get('customer_name', '')}"
        )
        candidate_customer_no = c.get("customer_no", "") or ""
        candidate_building_no = c.get("building_no", "") or ""
        summary["待人工確認"] += 1

    else:
        match_type = "no_match"
        match_score = 0
        review_status = "待建立客戶"
        review_note = "主客戶資料無安全候選，需人工建立新客戶或手動選擇既有客戶。"
        candidate_customer_no = ""
        candidate_building_no = ""
        summary["待建立客戶"] += 1

    exists = cur.execute("""
        SELECT id
        FROM ticket_customer_candidates
        WHERE ticket_id = :ticket_id
        LIMIT 1
    """, {"ticket_id": ticket_id}).fetchone()

    if exists:
        cur.execute("""
            UPDATE ticket_customer_candidates
            SET ticket_no = :ticket_no,
                customer_name = :customer_name,
                contact_phone = :contact_phone,
                service_address = :service_address,
                candidate_customer_no = :candidate_customer_no,
                candidate_building_no = :candidate_building_no,
                match_type = :match_type,
                match_score = :match_score,
                review_status = :review_status,
                review_note = :review_note,
                updated_at = CURRENT_TIMESTAMP
            WHERE ticket_id = :ticket_id
        """, {
            "ticket_id": ticket_id,
            "ticket_no": ticket_no,
            "customer_name": t["customer_name"] or "",
            "contact_phone": t["contact_phone"] or "",
            "service_address": t["service_address"] or "",
            "candidate_customer_no": candidate_customer_no,
            "candidate_building_no": candidate_building_no,
            "match_type": match_type,
            "match_score": match_score,
            "review_status": review_status,
            "review_note": review_note,
        })
    else:
        cur.execute("""
            INSERT INTO ticket_customer_candidates (
                ticket_id,
                ticket_no,
                customer_name,
                contact_phone,
                service_address,
                candidate_customer_no,
                candidate_building_no,
                match_type,
                match_score,
                review_status,
                review_note,
                created_at,
                updated_at
            )
            VALUES (
                :ticket_id,
                :ticket_no,
                :customer_name,
                :contact_phone,
                :service_address,
                :candidate_customer_no,
                :candidate_building_no,
                :match_type,
                :match_score,
                :review_status,
                :review_note,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
        """, {
            "ticket_id": ticket_id,
            "ticket_no": ticket_no,
            "customer_name": t["customer_name"] or "",
            "contact_phone": t["contact_phone"] or "",
            "service_address": t["service_address"] or "",
            "candidate_customer_no": candidate_customer_no,
            "candidate_building_no": candidate_building_no,
            "match_type": match_type,
            "match_score": match_score,
            "review_status": review_status,
            "review_note": review_note,
        })

    lines.append(
        f"{ticket_no}｜{t['customer_name']}｜{t['contact_phone']}｜"
        f"{match_type}｜{review_status}"
    )

conn.commit()

lines.append("")
lines.append("=" * 80)
lines.append("同步結果")
lines.append("=" * 80)
for k, v in summary.items():
    lines.append(f"{k}: {v} 筆")

rows = cur.execute("""
    SELECT review_status, match_type, COUNT(*) AS count
    FROM ticket_customer_candidates
    GROUP BY review_status, match_type
    ORDER BY review_status, match_type
""").fetchall()

lines.append("")
lines.append("=" * 80)
lines.append("目前 ticket_customer_candidates 分布")
lines.append("=" * 80)
for r in rows:
    lines.append(f"{r['review_status']} / {r['match_type']}: {r['count']} 筆")

report_path.write_text("\n".join(lines), encoding="utf-8")
conn.close()

print("OK: ticket customer candidate queue synced")
print(report_path)
