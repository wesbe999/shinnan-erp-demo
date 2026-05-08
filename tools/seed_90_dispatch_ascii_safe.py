from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import random
import shutil

from app.db import engine
from sqlalchemy import text

random.seed()

U = {
    "house_area": "\u900f\u5929",
    "install": "\u88dd\u6a5f",
    "repair": "\u7dad\u4fee",
    "return": "\u9000\u6a5f",
    "inspect": "\u5de1\u6aa2",
    "wait": "\u5f85\u6d3e\u5de5",
    "claimed": "\u5df2\u9818\u53d6",
    "done": "\u5df2\u5b8c\u5de5",
    "dispatch": "dispatch",
    "engineering": "engineering",
    "building": "building",
    "house": "house",
    "customer": "customer",
    "regional_unit": "\u5340\u57df\u5de5\u7a0b",
    "engineering_unit": "\u5de5\u7a0b\u90e8",
    "project_unit": "\u5c08\u6848\u90e8",
    "camera": "\u651d\u5f71\u6a5f\u67b6\u8a2d",
    "network_cable": "\u7db2\u8def\u62c9\u7dda",
    "network_improve": "\u7db2\u8def\u6539\u5584",
    "low_voltage": "\u5f31\u96fb\u65bd\u5de5",
    "construction": "\u5de5\u7a0b\u65bd\u5de5",
    "pending_sync": "\u672a\u540c\u6b65",
    "finance_pending": "pending",
    "test_done_note": "\u6e2c\u8a66\u5b8c\u5de5\u7d00\u9304",
}

def backup_db():
    db_path_raw = getattr(engine.url, "database", None)
    if not db_path_raw:
        print("DB_BACKUP = SKIPPED_UNKNOWN_DB")
        return

    db_path = Path(db_path_raw)
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path

    if not db_path.exists():
        print("DB_BACKUP = SKIPPED_NOT_FOUND", db_path)
        return

    backup = db_path.with_name(
        db_path.stem
        + "_before_ascii_safe_seed_90_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
        + db_path.suffix
    )
    shutil.copy2(db_path, backup)
    print("DB_BACKUP =", backup)

def cols(conn, table):
    return {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()}

def insert_row(conn, table, payload):
    table_cols = cols(conn, table)
    data = {k: v for k, v in payload.items() if k in table_cols}
    sql = "INSERT INTO " + table + " (" + ",".join(data.keys()) + ") VALUES (" + ",".join(":" + k for k in data.keys()) + ")"
    result = conn.execute(text(sql), data)
    return result.lastrowid

backup_db()

now = datetime.now()
today_code = now.strftime("%Y%m%d")

case_types = [U["install"], U["repair"], U["return"], U["inspect"]]
statuses = [U["wait"], U["wait"], U["claimed"], U["claimed"], U["done"]]

house_plan = [
    (U["install"], U["install"], U["dispatch"], U["regional_unit"]),
    (U["repair"], U["repair"], U["dispatch"], U["regional_unit"]),
    (U["return"], U["return"], U["dispatch"], U["regional_unit"]),
    (U["construction"], U["camera"], U["engineering"], U["engineering_unit"]),
    (U["construction"], U["network_cable"], U["engineering"], U["engineering_unit"]),
    (U["construction"], U["network_improve"], U["engineering"], U["engineering_unit"]),
    (U["construction"], U["low_voltage"], U["engineering"], U["engineering_unit"]),
    (U["install"], U["install"], U["dispatch"], U["regional_unit"]),
    (U["repair"], U["repair"], U["dispatch"], U["regional_unit"]),
    (U["return"], U["return"], U["dispatch"], U["regional_unit"]),
]

house_names = [
    "\u9673\u5fd7\u660e", "\u6797\u96c5\u5a77", "\u9ec3\u4fca\u5091", "\u738b\u6dd1\u82ac", "\u674e\u5b97\u7ff0",
    "\u5f35\u7f8e\u73b2", "\u5433\u51a0\u5b87", "\u8521\u4f73\u84c9", "\u90ed\u5bb6\u8c6a", "\u694a\u660e\u54f2",
]

house_addresses = [
    "\u53f0\u5357\u5e02\u6771\u5340\u900f\u5929\u6848\u5834",
    "\u53f0\u5357\u5e02\u5317\u5340\u900f\u5929\u6848\u5834",
    "\u53f0\u5357\u5e02\u6c38\u5eb7\u5340\u900f\u5929\u6848\u5834",
    "\u53f0\u5357\u5e02\u5b89\u5e73\u5340\u900f\u5929\u6848\u5834",
    "\u53f0\u5357\u5e02\u4ec1\u5fb7\u5340\u900f\u5929\u6848\u5834",
]

with engine.begin() as conn:
    for table in [
        "ticket_install_details",
        "ticket_return_details",
        "ticket_transfers",
        "engineering_projects",
        "system_notifications",
        "tickets",
    ]:
        conn.execute(text(f"DELETE FROM {table}"))
        print("CLEARED", table)

    areas = [
        row._mapping["area"]
        for row in conn.execute(text("""
            SELECT DISTINCT area
            FROM buildings
            WHERE COALESCE(area, '') <> ''
            ORDER BY area
        """)).fetchall()
    ]

    print("AREAS =", areas)

    customers_by_area = defaultdict(list)
    customer_rows = conn.execute(text("""
        SELECT
            c.id AS customer_id,
            c.customer_no,
            c.customer_name,
            c.customer_phone,
            c.building_no,
            c.room_no,
            c.service_address,
            c.monthly_fee,
            b.name AS building_name,
            b.area AS area,
            b.address AS building_address
        FROM customer_accounts c
        JOIN buildings b ON b.building_no = c.building_no
        WHERE COALESCE(b.area, '') <> ''
        ORDER BY b.area, c.id
    """)).fetchall()

    for row in customer_rows:
        customers_by_area[row._mapping["area"]].append(row)

    created = []
    seq = 1

    for area in areas:
        area_customers = customers_by_area.get(area, [])

        for i in range(10):
            is_house = area == U["house_area"]
            status = random.choice(statuses)

            if is_house:
                case_type, project_type, work_pool, responsible_unit = house_plan[i]
                customer_name = house_names[i % len(house_names)]
                phone = "0910" + str(random.randint(100000, 999999))
                service_address = house_addresses[i % len(house_addresses)]
                customer_no = "HOUSE-" + f"{i+1:03d}"
                building_no = "HOUSE"
                site_type = U["house"]
                source_type = U["house"]
                source_id = customer_no
                non_house_areas = [a for a in areas if a != U["house_area"]]
                responsible_area = random.choice(non_house_areas) if non_house_areas else area
                internal_note = "\u900f\u5929\u6848\u4ef6\uff1a\u5148\u6d3e\u6240\u5728\u7ba1\u8f44\u5340\uff0c\u5fc5\u8981\u6642\u518d\u8f49\u6d3e\u7dad\u4fee\uff0f\u5de5\u7a0b\uff0f\u5c08\u6848\u90e8\u3002"
                description = "\u900f\u5929\u6e2c\u8a66\u6d3e\u5de5\uff1a" + project_type + "\uff5c" + customer_name + "\uff5c" + service_address
                monthly_fee = 300
            else:
                case_type = case_types[i % len(case_types)]
                project_type = case_type
                work_pool = U["dispatch"]
                responsible_unit = U["regional_unit"]
                site_type = U["building"]
                source_type = U["customer"]
                responsible_area = area

                if area_customers:
                    c = area_customers[i % len(area_customers)]._mapping
                    customer_name = c["customer_name"] or (area + "\u6e2c\u8a66\u5ba2\u6236")
                    phone = c["customer_phone"] or "0910000000"
                    service_address = c["service_address"] or c["room_no"] or c["building_address"] or ""
                    customer_no = c["customer_no"] or ""
                    building_no = c["building_no"] or ""
                    source_id = customer_no
                    monthly_fee = c["monthly_fee"] or 300
                    building_name = c["building_name"] or ""
                else:
                    customer_name = area + "\u6e2c\u8a66\u5ba2\u6236" + f"{i+1:02d}"
                    phone = "0910" + str(random.randint(100000, 999999))
                    service_address = f"{random.randint(1,18)}F-{random.randint(1,5):02d}"
                    customer_no = area + "-C" + f"{i+1:03d}"
                    building_no = area + "-B" + f"{i+1:03d}"
                    source_id = customer_no
                    monthly_fee = 300
                    building_name = area + "\u6e2c\u8a66\u5927\u6a13"

                internal_note = "\u5f9e\u5ba2\u6236\u8cc7\u6599\u8207\u5927\u6a13\u5340\u57df\u7522\u751f\u6e2c\u8a66\u6d3e\u5de5\u3002"
                description = "\u5927\u6a13\u6e2c\u8a66\u6d3e\u5de5\uff1a" + area + "\uff5c" + case_type + "\uff5c" + customer_name + "\uff5c" + building_name

            engineer = ""
            engineer_staff_code = ""
            if status in (U["claimed"], U["done"]):
                engineer = "\u6e2c\u8a66\u5de5\u7a0b\u5e2b" + str(random.randint(1, 30))
                engineer_staff_code = "S" + f"{random.randint(1,99):04d}"

            completed_at = ""
            completion_note = ""
            result_status = "active"
            if status == U["done"]:
                completed_at = (now - timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d %H:%M:%S")
                completion_note = U["test_done_note"]
                result_status = "completed"

            ticket_payload = {
                "ticket_no": f"XN-{today_code}-T{seq:04d}",
                "case_type": case_type,
                "status": status,
                "customer_name": customer_name,
                "contact_name": customer_name,
                "contact_phone": phone,
                "service_address": service_address,
                "appointment_date": (now.date() + timedelta(days=random.randint(0,14))).isoformat(),
                "appointment_time": random.choice(["09:00", "10:30", "13:30", "15:00", "16:30"]),
                "assigned_engineer": engineer,
                "assigned_engineer_staff_code": engineer_staff_code,
                "description": description,
                "internal_note": internal_note,
                "completion_note": completion_note,
                "finance_sync_status": U["finance_pending"] if status == U["done"] else U["pending_sync"],
                "external_finance_id": "",
                "finance_note": "",
                "created_at": (now - timedelta(minutes=seq)).strftime("%Y-%m-%d %H:%M:%S"),
                "arrived_at": None,
                "completed_at": completed_at or None,
                "dispatch_area": area,
                "customer_signature_data": "",
                "customer_signature_signed_at": None,
                "extra_fees_data": "[]",
                "customer_no": customer_no,
                "building_no": building_no,
                "install_detail": "",
                "return_detail": "",

                "site_type": site_type,
                "source_type": source_type,
                "source_id": source_id,
                "work_pool": work_pool,
                "responsible_area": responsible_area,
                "responsible_unit": responsible_unit,
                "project_type": project_type,
                "transfer_status": "none",
                "transfer_to_unit": "",
                "transfer_reason": "",
                "transfer_note": "",
                "transferred_at": "",
                "transferred_by": "",
                "ticket_result_status": result_status,
                "reject_status": "none",
                "reject_reason": "",
                "reject_note": "",
                "rejected_at": "",
                "rejected_by": "",
                "returned_to_unit": "",
                "engineering_case_id": 0,
            }

            ticket_id = insert_row(conn, "tickets", ticket_payload)

            if case_type == U["install"]:
                insert_row(conn, "ticket_install_details", {
                    "ticket_id": ticket_id,
                    "deposit_amount": random.choice([0, 1000, 1500, 2000]),
                    "construction_fee": random.choice([0, 500, 1000, 1500]),
                    "monthly_fee": int(monthly_fee or 300),
                    "month_count": random.choice([1, 3, 6, 12]),
                    "other_fee": random.choice([0, 100, 200]),
                    "other_fee_note": "",
                    "material_name": "\u7db2\u8def\u7dda",
                    "material_quantity": random.randint(1, 5),
                    "usage_start_date": now.date().isoformat(),
                    "usage_end_date": (now.date() + timedelta(days=90)).isoformat(),
                    "usage_month_count": 3,
                    "rent_subtotal": int(monthly_fee or 300) * 3,
                    "total_amount": int(monthly_fee or 300) * 3 + 1000,
                })

            if case_type == U["return"]:
                insert_row(conn, "ticket_return_details", {
                    "ticket_id": ticket_id,
                    "payment_record": "\u5f85\u67e5\u5e33",
                    "deposit_amount": random.choice([0, 1000, 1500, 2000]),
                    "other_fee": random.choice([0, 100, 300]),
                    "other_fee_note": "",
                    "returned_device_status": "\u5f85\u56de\u6536",
                    "return_note": "\u6e2c\u8a66\u9000\u6a5f\u8cc7\u6599",
                    "settlement_note": "\u7cfb\u7d71\u6e2c\u8a66\u7d50\u7b97",
                })

            created.append((area, status, case_type, project_type, work_pool, site_type))
            seq += 1

    print("SEED_DONE")
    print("TOTAL_CREATED =", len(created))

    for title, idx in [
        ("AREA", 0),
        ("STATUS", 1),
        ("CASE_TYPE", 2),
        ("PROJECT_TYPE", 3),
        ("WORK_POOL", 4),
        ("SITE_TYPE", 5),
    ]:
        print("\n" + title + " COUNT")
        for k, v in Counter(x[idx] for x in created).items():
            print(k, "=", v)

    print("\nDETAIL COUNTS")
    for table in ["tickets", "ticket_install_details", "ticket_return_details"]:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(table, "=", count)

print("ascii_safe_seed_90_done")
