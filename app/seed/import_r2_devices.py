"""
匯入 r2_devices CSV 到 ERP 資料庫
建立 r2_devices 資料表並匯入 NMS 裝置資料
"""
import sqlite3
import csv
import sys
from pathlib import Path

DB_PATH  = Path(__file__).parent.parent.parent / "xunnan_dispatch.db"
CSV_PATH = Path(__file__).parent.parent.parent / "r2_devices.csv"

# 如果 CSV 路徑不存在，嘗試找傳入的參數
if len(sys.argv) > 1:
    CSV_PATH = Path(sys.argv[1])

print(f"DB:  {DB_PATH}")
print(f"CSV: {CSV_PATH}")

conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

# ── 建立資料表 ──────────────────────────────
cur.executescript("""
CREATE TABLE IF NOT EXISTS r2_devices (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id        TEXT    NOT NULL UNIQUE,   -- NMS form_id / DID
    building_name    TEXT    DEFAULT '',
    community        TEXT    DEFAULT '',
    device_no        TEXT    DEFAULT '',        -- shinnan-xxx
    model            TEXT    DEFAULT '',
    serial           TEXT    DEFAULT '',
    routeros_version TEXT    DEFAULT '',
    management_ip    TEXT    DEFAULT '',
    management_port  TEXT    DEFAULT '9000',
    management_url   TEXT    DEFAULT '',
    circuit_no       TEXT    DEFAULT '',
    bandwidth        TEXT    DEFAULT '',
    uptime           TEXT    DEFAULT '',
    checked_at       TEXT    DEFAULT '',
    class_name       TEXT    DEFAULT 'SF_1',    -- SF_0/SF_1/SF_2/SF_4
    form_id          TEXT    DEFAULT '',
    created_at       TEXT    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TEXT    DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_r2_device_no  ON r2_devices(device_no);
CREATE INDEX IF NOT EXISTS idx_r2_class_name ON r2_devices(class_name);
CREATE INDEX IF NOT EXISTS idx_r2_community  ON r2_devices(community);
""")
conn.commit()
print("資料表建立完成")

# ── 匯入 CSV ────────────────────────────────
with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

inserted = 0
updated  = 0

for row in rows:
    did = row.get("device_id", "").strip()
    if not did:
        continue

    data = (
        row.get("building_name",    "").strip(),
        row.get("community",        "").strip(),
        row.get("device_no",        "").strip(),
        row.get("model",            "").strip(),
        row.get("serial",           "").strip(),
        row.get("routeros_version", "").strip(),
        row.get("management_ip",    "").strip(),
        row.get("management_port",  "9000").strip(),
        row.get("management_url",   "").strip(),
        row.get("circuit_no",       "").strip(),
        row.get("bandwidth",        "").strip(),
        row.get("uptime",           "").strip(),
        row.get("checked_at",       "").strip(),
        row.get("class_name",       "SF_1").strip(),
        row.get("form_id",          "").strip(),
        did,
    )

    cur.execute("""
        INSERT INTO r2_devices
            (building_name, community, device_no, model, serial,
             routeros_version, management_ip, management_port, management_url,
             circuit_no, bandwidth, uptime, checked_at, class_name, form_id,
             device_id, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, CURRENT_TIMESTAMP)
        ON CONFLICT(device_id) DO UPDATE SET
            building_name    = excluded.building_name,
            community        = excluded.community,
            device_no        = excluded.device_no,
            model            = excluded.model,
            serial           = excluded.serial,
            routeros_version = excluded.routeros_version,
            management_ip    = excluded.management_ip,
            management_port  = excluded.management_port,
            management_url   = excluded.management_url,
            circuit_no       = excluded.circuit_no,
            bandwidth        = excluded.bandwidth,
            uptime           = excluded.uptime,
            checked_at       = excluded.checked_at,
            class_name       = excluded.class_name,
            form_id          = excluded.form_id,
            updated_at       = CURRENT_TIMESTAMP
    """, data)

    if cur.rowcount == 1:
        inserted += 1
    else:
        updated += 1

conn.commit()
conn.close()

print(f"完成！新增 {inserted} 筆，更新 {updated} 筆，共 {len(rows)} 筆")
