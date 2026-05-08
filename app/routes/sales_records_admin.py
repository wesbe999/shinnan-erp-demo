import json as _sales_json

from fastapi import APIRouter
from fastapi.responses import Response as _SalesResponse
from sqlalchemy import text as _sales_sql_text

from app.db import engine as _sales_engine
from app.routes.buildings_admin import _buildings_db_init

router = APIRouter(tags=["sales-records-admin"])


# SHINNAN_SALES_DB_API_START
def _sales_business_records_init():
    with _sales_engine.begin() as conn:
        conn.execute(_sales_sql_text("""
            CREATE TABLE IF NOT EXISTS sales_business_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_no TEXT NOT NULL,
                business_type TEXT DEFAULT '',
                status TEXT DEFAULT '',
                contract_status TEXT DEFAULT '',
                contract_end_date TEXT DEFAULT '',
                feedback_type TEXT DEFAULT '',
                feedback_status TEXT DEFAULT '',
                event_type TEXT DEFAULT '',
                event_status TEXT DEFAULT '',
                event_schedule_date TEXT DEFAULT '',
                important_schedule INTEGER DEFAULT 0,
                next_visit TEXT DEFAULT '',
                owner TEXT DEFAULT '',
                business_note TEXT DEFAULT '',
                demo_type TEXT DEFAULT '',
                created_at TEXT DEFAULT '',
                updated_at TEXT DEFAULT ''
            )
        """))


@router.get("/api/admin/sales/business-records", summary="讀取業務工作資料")
def api_admin_sales_business_records():
    _sales_business_records_init()
    _buildings_db_init()

    with _sales_engine.begin() as conn:
        rows = conn.execute(_sales_sql_text("""
            SELECT
                s.id AS id,
                s.building_no AS building_no,
                b.name AS building_name,
                b.area AS area,
                b.address AS building_address,
                b.management_company AS management_company,
                b.management_phone AS management_phone,
                b.manager_name AS manager_name,
                b.manager_phone AS manager_phone,
                b.manager_age AS manager_age,
                b.manager_experience AS manager_experience,
                b.manager_interest AS manager_interest,
                b.visit_time AS visit_time,
                b.committee_time AS committee_time,
                b.resident_meeting_time AS resident_meeting_time,
                s.business_type AS business_type,
                s.status AS status,
                s.contract_status AS contract_status,
                s.contract_end_date AS contract_end_date,
                s.feedback_type AS feedback_type,
                s.feedback_status AS feedback_status,
                s.event_type AS event_type,
                s.event_status AS event_status,
                s.event_schedule_date AS event_schedule_date,
                s.important_schedule AS important_schedule,
                s.next_visit AS next_visit,
                s.owner AS owner,
                s.business_note AS business_note,
                s.demo_type AS demo_type,
                s.created_at AS created_at,
                s.updated_at AS updated_at
            FROM sales_business_records s
            LEFT JOIN buildings b ON b.building_no = s.building_no
            ORDER BY s.id DESC
        """)).mappings().fetchall()

    records = []

    for row in rows:
        item = dict(row)
        item["important_schedule"] = bool(item.get("important_schedule"))
        item["management_note"] = (
            "大樓地址：" + str(item.get("building_address") or "") + "\\n"
            "管理公司：" + str(item.get("management_company") or "") + "\\n"
            "管理室電話：" + str(item.get("management_phone") or "")
        )
        records.append(item)

    return _SalesResponse(
        content=_sales_json.dumps(records, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )
# SHINNAN_SALES_DB_API_END
