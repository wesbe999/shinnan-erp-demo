from __future__ import annotations

import json as _sales_json
import json as _managers_json
from datetime import datetime as _emp_datetime
from urllib.parse import parse_qs as _emp_parse_qs

from fastapi import APIRouter
from fastapi import Request as _EmpRequest
from fastapi import Body
from fastapi.responses import HTMLResponse
from fastapi.responses import Response as _ManagersResponse
from fastapi.responses import Response as _SalesResponse
from fastapi.responses import RedirectResponse as _EmpRedirectResponse
from sqlalchemy import text as _sales_sql_text
from sqlalchemy import text as _buildings_sql_text

from app.db import engine as _sales_engine
from app.db import engine as _buildings_engine
from app.routes.employee_auth import _employee_current_user_from_request


router = APIRouter(tags=["手機業務 APP"])


def _buildings_db_init():
    with _buildings_engine.begin() as conn:
        conn.execute(_buildings_sql_text("""
            CREATE TABLE IF NOT EXISTS buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_no TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                area TEXT DEFAULT '',
                address TEXT DEFAULT '',
                raw_address TEXT DEFAULT '',
                display_address TEXT DEFAULT '',
                management_company TEXT DEFAULT '',
                management_phone TEXT DEFAULT '',
                manager_name TEXT DEFAULT '',
                manager_phone TEXT DEFAULT '',
                manager_age TEXT DEFAULT '',
                manager_experience TEXT DEFAULT '',
                manager_interest TEXT DEFAULT '',
                visit_time TEXT DEFAULT '',
                committee_time TEXT DEFAULT '',
                resident_meeting_time TEXT DEFAULT '',
                active_users INTEGER DEFAULT 0,
                total_households INTEGER DEFAULT 0,
                ip TEXT DEFAULT '',
                host TEXT DEFAULT '',
                note TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))


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
            "大樓地址：" + str(item.get("building_address") or "") + "\n"
            "管理公司：" + str(item.get("management_company") or "") + "\n"
            "管理室電話：" + str(item.get("management_phone") or "")
        )
        records.append(item)

    return _SalesResponse(
        content=_sales_json.dumps(records, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


def _sales_completed_statuses() -> set[str]:
    return {
        "\u5df2\u5b8c\u6210",
        "\u5df2\u7d50\u6848",
        "\u5df2\u95dc\u9589",
    }


def _sales_is_admin_scope(user: dict | None) -> bool:
    if not user:
        return False

    role = str(user.get("role") or "").strip().lower()
    display_name = str(user.get("display_name") or "").strip()
    staff_code = str(user.get("staff_code") or user.get("username") or "").strip().lower()
    department = str(user.get("department") or "").strip()

    admin_roles = {"admin", "boss", "manager", "management", "system_admin"}
    admin_names = {
        "\u7cfb\u7d71\u7ba1\u7406\u54e1",
        "\u8001\u95c6",
        "\u7ba1\u7406\u5c64",
        "admin",
    }
    admin_departments = {
        "\u7ba1\u7406\u5c64",
        "\u4eba\u4e8b\u90e8",
        "\u8001\u95c6 / \u6700\u9ad8\u7ba1\u7406",
        "\u6700\u9ad8\u7ba1\u7406",
    }

    return (
        role in admin_roles
        or staff_code == "admin"
        or display_name in admin_names
        or department in admin_departments
    )


def _sales_business_records_for_app(user: dict) -> list[dict]:
    _sales_business_records_init()
    _buildings_db_init()

    completed = tuple(_sales_completed_statuses())
    params = {
        "done_1": completed[0],
        "done_2": completed[1],
        "done_3": completed[2],
    }

    where = """
            WHERE COALESCE(s.status, '') NOT IN (:done_1, :done_2, :done_3)
        """

    if not _sales_is_admin_scope(user):
        where += " AND COALESCE(s.owner, '') = :owner"
        params["owner"] = str(user.get("display_name") or "").strip()

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
        """ + where + """
            ORDER BY
                COALESCE(s.important_schedule, 0) DESC,
                COALESCE(NULLIF(s.next_visit, ''), NULLIF(s.event_schedule_date, ''), '9999-12-31') ASC,
                s.id DESC
        """), params).mappings().fetchall()

    records = []
    for row in rows:
        item = dict(row)
        item["important_schedule"] = bool(item.get("important_schedule"))
        item["management_note"] = (
            "\u5927\u6a13\u5730\u5740\uff1a" + str(item.get("building_address") or "") + "\n"
            "\u7ba1\u7406\u516c\u53f8\uff1a" + str(item.get("management_company") or "") + "\n"
            "\u7ba1\u59d4\u96fb\u8a71\uff1a" + str(item.get("management_phone") or "")
        )
        records.append(item)

    return records



# CL15N1_SALES_DISPATCH_REQUEST_API_START
def _sales_safe_text(value) -> str:
    return str(value or "").strip()


def _sales_now_text() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _sales_table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        _sales_sql_text("""
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
              AND name = :name
        """),
        {"name": table_name},
    ).scalar()
    return int(row or 0) > 0


def _sales_table_columns(conn, table_name: str) -> set:
    if not _sales_table_exists(conn, table_name):
        return set()
    rows = conn.execute(_sales_sql_text("PRAGMA table_info(" + table_name + ")")).mappings().fetchall()
    return {str(r["name"]) for r in rows}


def _sales_ensure_tickets_table(conn):
    conn.execute(_sales_sql_text("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_no TEXT DEFAULT '',
            dispatch_area TEXT DEFAULT '',
            case_type TEXT DEFAULT '',
            status TEXT DEFAULT '',
            customer_name TEXT DEFAULT '',
            contact_name TEXT DEFAULT '',
            contact_phone TEXT DEFAULT '',
            service_address TEXT DEFAULT '',
            appointment_date TEXT DEFAULT '',
            appointment_time TEXT DEFAULT '',
            assigned_engineer TEXT DEFAULT '',
            assigned_engineer_staff_code TEXT DEFAULT '',
            customer_no TEXT DEFAULT '',
            building_no TEXT DEFAULT '',
            description TEXT DEFAULT '',
            internal_note TEXT DEFAULT '',
            completion_note TEXT DEFAULT '',
            created_at TEXT DEFAULT ''
        )
    """))

    cols = _sales_table_columns(conn, "tickets")
    wanted = {
        "ticket_no": "TEXT DEFAULT ''",
        "dispatch_area": "TEXT DEFAULT ''",
        "case_type": "TEXT DEFAULT ''",
        "status": "TEXT DEFAULT ''",
        "customer_name": "TEXT DEFAULT ''",
        "contact_name": "TEXT DEFAULT ''",
        "contact_phone": "TEXT DEFAULT ''",
        "service_address": "TEXT DEFAULT ''",
        "appointment_date": "TEXT DEFAULT ''",
        "appointment_time": "TEXT DEFAULT ''",
        "assigned_engineer": "TEXT DEFAULT ''",
        "assigned_engineer_staff_code": "TEXT DEFAULT ''",
        "customer_no": "TEXT DEFAULT ''",
        "building_no": "TEXT DEFAULT ''",
        "description": "TEXT DEFAULT ''",
        "internal_note": "TEXT DEFAULT ''",
        "completion_note": "TEXT DEFAULT ''",
        "created_at": "TEXT DEFAULT ''",
        "source_channel": "TEXT DEFAULT ''",
        "is_public_facility": "INTEGER DEFAULT 0",
        "is_non_general_repair": "INTEGER DEFAULT 0",
        "boss_review_required": "INTEGER DEFAULT 0",
        "transfer_origin_ticket_id": "INTEGER DEFAULT 0",
        "transfer_child_ticket_id": "INTEGER DEFAULT 0",
        "transfer_target_department": "TEXT DEFAULT ''",
        "transfer_source_department": "TEXT DEFAULT ''",
        "transfer_status": "TEXT DEFAULT ''",
        "transfer_note": "TEXT DEFAULT ''",
        "transfer_created_at": "TEXT DEFAULT ''",
        "transfer_updated_at": "TEXT DEFAULT ''",
    }

    for col, col_type in wanted.items():
        if col not in cols:
            conn.execute(_sales_sql_text("ALTER TABLE tickets ADD COLUMN " + col + " " + col_type))


def _sales_dispatch_departments():
    return [
        "\u5de5\u52d9\u90e8",
        "\u7dad\u4fee\u90e8",
        "\u5de5\u7a0b\u90e8",
        "\u5ba2\u670d\u90e8",
        "\u5e33\u52d9\u90e8",
        "\u696d\u52d9\u90e8",
        "\u63a1\u8cfc\u90e8",
        "\u7522\u54c1\u63a8\u5ee3\u90e8",
        "\u5c08\u6848\u90e8",
    ]


@router.get("/api/app/sales/dispatch/departments")
def api_app_sales_dispatch_departments(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    return _ManagersResponse(
        content=_managers_json.dumps({"ok": True, "items": _sales_dispatch_departments()}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )



# CL15N2_SALES_DISPATCH_BUILDING_PICKER_API_START
@router.get("/api/app/sales/dispatch/buildings")
def api_app_sales_dispatch_buildings(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _buildings_db_init()

    with _sales_engine.begin() as conn:
        rows = conn.execute(_sales_sql_text("""
            SELECT
                building_no,
                name,
                area,
                address,
                raw_address,
                display_address,
                management_company,
                management_phone,
                manager_name,
                manager_phone
            FROM buildings
            ORDER BY area, name, building_no
        """)).mappings().fetchall()

    items = []

    for row in rows:
        address = (
            _sales_safe_text(row.get("display_address"))
            or _sales_safe_text(row.get("address"))
            or _sales_safe_text(row.get("raw_address"))
        )

        phone = (
            _sales_safe_text(row.get("manager_phone"))
            or _sales_safe_text(row.get("management_phone"))
        )

        items.append({
            "building_no": _sales_safe_text(row.get("building_no")),
            "name": _sales_safe_text(row.get("name")),
            "area": _sales_safe_text(row.get("area")),
            "address": address,
            "management_company": _sales_safe_text(row.get("management_company")),
            "manager_name": _sales_safe_text(row.get("manager_name")),
            "phone": phone,
        })

    return _ManagersResponse(
        content=_managers_json.dumps({"ok": True, "items": items}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


# CL15N2_SALES_DISPATCH_BUILDING_PICKER_API_END


@router.post("/api/app/sales/dispatch/create")
def api_app_sales_dispatch_create(request: _EmpRequest, payload: dict = Body(default_factory=dict)):
    user = _employee_current_user_from_request(request)

    if not user:
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    target_department = _sales_safe_text(payload.get("target_department"))
    request_unit = _sales_safe_text(payload.get("request_unit"))
    request_type = _sales_safe_text(payload.get("request_type")) or "\u516c\u8a2d"
    building_no = _sales_safe_text(payload.get("building_no"))
    building_name = _sales_safe_text(payload.get("building_name"))
    service_address = _sales_safe_text(payload.get("service_address"))
    contact_name = _sales_safe_text(payload.get("contact_name"))
    contact_phone = _sales_safe_text(payload.get("contact_phone"))
    description = _sales_safe_text(payload.get("description"))

    if not target_department:
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "\u8acb\u9078\u64c7\u6d3e\u5de5\u55ae\u4f4d"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    if target_department not in _sales_dispatch_departments():
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "\u6d3e\u5de5\u55ae\u4f4d\u4e0d\u6b63\u78ba"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    if not request_unit:
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "\u8acb\u586b\u5beb\u8981\u6c42\u55ae\u4f4d"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    if not building_name:
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "\u8acb\u586b\u5beb\u5927\u6a13\u540d\u7a31"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    if not description:
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "\u8acb\u586b\u5beb\u9700\u6c42\u5167\u5bb9"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    owner = _sales_safe_text(user.get("display_name") or user.get("staff_code"))
    now_text = _sales_now_text()

    _buildings_db_init()

    with _sales_engine.begin() as conn:
        _sales_ensure_tickets_table(conn)
        ticket_cols = _sales_table_columns(conn, "tickets")

        building = None
        if building_no:
            building = conn.execute(
                _sales_sql_text("""
                    SELECT *
                    FROM buildings
                    WHERE building_no = :building_no
                    LIMIT 1
                """),
                {"building_no": building_no},
            ).mappings().first()

        if not building and building_name:
            building = conn.execute(
                _sales_sql_text("""
                    SELECT *
                    FROM buildings
                    WHERE name = :name
                    LIMIT 1
                """),
                {"name": building_name},
            ).mappings().first()

        if building:
            building_no = _sales_safe_text(building.get("building_no")) or building_no
            building_name = _sales_safe_text(building.get("name")) or building_name
            service_address = (
                _sales_safe_text(building.get("display_address"))
                or _sales_safe_text(building.get("address"))
                or _sales_safe_text(building.get("raw_address"))
                or service_address
            )
            if not contact_name:
                contact_name = _sales_safe_text(building.get("manager_name"))
            if not contact_phone:
                contact_phone = _sales_safe_text(building.get("manager_phone")) or _sales_safe_text(building.get("management_phone"))

        if not building_name:
            building_name = service_address or "\u696d\u52d9\u6d3e\u5de5"

        max_id = conn.execute(_sales_sql_text("SELECT COALESCE(MAX(id), 0) FROM tickets")).scalar() or 0
        ticket_no = "SREQ" + now_text[:10].replace("-", "") + str(int(max_id) + 1).zfill(4)

        case_type = request_type
        if request_type in ["\u516c\u8a2d", "\u516c\u8a2d\u9700\u6c42"]:
            case_type = "\u516c\u8a2d"
        elif request_type in ["\u56de\u994b", "\u5ba2\u6236\u56de\u994b"]:
            case_type = "\u56de\u994b"
        elif request_type in ["\u793e\u5340\u9700\u6c42"]:
            case_type = "\u793e\u5340\u9700\u6c42"

        full_description = (
            "\u696d\u52d9\u6d3e\u5de5\u9700\u6c42\n"
            "\u8981\u6c42\u55ae\u4f4d\uff1a" + request_unit + "\n"
            "\u6d3e\u5de5\u55ae\u4f4d\uff1a" + target_department + "\n"
            "\u9700\u6c42\u985e\u578b\uff1a" + request_type + "\n"
            "\u767c\u8d77\u696d\u52d9\uff1a" + owner + "\n"
            "\u5927\u6a13\uff1a" + building_name + "\n"
            "\u5167\u5bb9\uff1a" + description
        )

        data = {
            "ticket_no": ticket_no,
            "dispatch_area": target_department,
            "case_type": case_type,
            "status": "\u672a\u9818\u53d6",
            "customer_name": building_name,
            "contact_name": contact_name,
            "contact_phone": contact_phone,
            "service_address": service_address,
            "appointment_date": "",
            "appointment_time": "",
            "assigned_engineer": "",
            "assigned_engineer_staff_code": "",
            "customer_no": "",
            "building_no": building_no,
            "description": full_description,
            "internal_note": "\u696d\u52d9APP\u5efa\u7acb\uff1b\u8981\u6c42\u55ae\u4f4d\uff1a" + request_unit,
            "completion_note": "",
            "created_at": now_text,
            "source_channel": "\u696d\u52d9APP",
            "is_public_facility": 1 if "\u516c\u8a2d" in request_type else 0,
            "is_non_general_repair": 1 if target_department in ["\u7dad\u4fee\u90e8", "\u5de5\u7a0b\u90e8"] else 0,
            "boss_review_required": 1 if target_department in ["\u7dad\u4fee\u90e8", "\u5de5\u7a0b\u90e8"] else 0,
            "transfer_origin_ticket_id": 0,
            "transfer_child_ticket_id": 0,
            "transfer_target_department": target_department,
            "transfer_source_department": "\u696d\u52d9\u90e8",
            "transfer_status": "\u696d\u52d9\u65b0\u589e\u6d3e\u5de5",
            "transfer_note": description,
            "transfer_created_at": now_text,
            "transfer_updated_at": now_text,
        }

        insert_cols = [c for c in data.keys() if c in ticket_cols]
        insert_sql = "INSERT INTO tickets (" + ", ".join(insert_cols) + ") VALUES (" + ", ".join([":" + c for c in insert_cols]) + ")"
        result = conn.execute(_sales_sql_text(insert_sql), {c: data[c] for c in insert_cols})
        ticket_id = int(result.lastrowid)

    return _ManagersResponse(
        content=_managers_json.dumps({
            "ok": True,
            "ticket_id": ticket_id,
            "ticket_no": ticket_no,
            "target_department": target_department,
        }, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


# CL15N1_SALES_DISPATCH_REQUEST_API_END


# SHINNAN_SALES_MOBILE_APP_START
@router.get("/app/sales", response_class=HTMLResponse)
def sales_mobile_app_page(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmpRedirectResponse("/employee/login?next=/app/sales", status_code=303)

    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

  <title>訊南業務系統｜訊南 ERP</title>

  <style>
    :root {
      --bg: #eef3f9;
      --card: #ffffff;
      --line: #d7e1ef;
      --text: #102348;
      --muted: #64748b;
      --blue: #365ee8;
      --green: #16a34a;
      --orange: #f97316;
      --purple: #7c3aed;
      --red: #dc2626;
    }

    * {
      box-sizing: border-box;
      -webkit-tap-highlight-color: transparent;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .app {
      min-height: 100vh;
      padding-bottom: 88px;
    }

    .top {
      position: sticky;
      top: 0;
      z-index: 20;
      padding: 14px 14px 10px;
      background: linear-gradient(135deg, #0f766e, #2563eb, #7c3aed);
      color: #fff;
      box-shadow: 0 10px 28px rgba(15, 23, 42, 0.22);
      border-bottom-left-radius: 22px;
      border-bottom-right-radius: 22px;
    }

    .top-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
    }

    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 1000;
      letter-spacing: 0.02em;
    }

    .top-sub {
      margin-top: 4px;
      font-size: 13px;
      font-weight: 800;
      opacity: 0.9;
    }

    .home-btn {
      border: 0;
      border-radius: 12px;
      height: 34px;
      padding: 0 12px;
      background: rgba(255,255,255,0.18);
      color: #fff;
      font-size: 13px;
      font-weight: 1000;
    }

    .summary {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      padding: 12px 12px 4px;
    }

    .summary-card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 10px 8px;
      box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
    }

    .summary-label {
      color: var(--muted);
      font-size: 11px;
      font-weight: 1000;
    }

    .summary-num {
      margin-top: 2px;
      color: var(--text);
      font-size: 24px;
      line-height: 1;
      font-weight: 1000;
    }

    .filters {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding: 8px 12px;
      scrollbar-width: none;
    }

    .filters::-webkit-scrollbar {
      display: none;
    }

    .filter-btn {
      flex: 0 0 auto;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--text);
      height: 34px;
      padding: 0 13px;
      font-size: 13px;
      font-weight: 1000;
    }

    .filter-btn.active {
      background: var(--blue);
      color: #fff;
      border-color: var(--blue);
    }

    .search-box {
      padding: 4px 12px 8px;
    }

    .search-box input {
      width: 100%;
      height: 38px;
      border: 1px solid var(--line);
      border-radius: 13px;
      padding: 0 12px;
      font-size: 14px;
      font-weight: 800;
      outline: none;
    }

    .section-title {
      padding: 6px 14px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 1000;
    }

    .list {
      padding: 0 12px 14px;
      display: grid;
      gap: 10px;
    }

    .case-card {
      border: 1px solid var(--line);
      background: var(--card);
      border-radius: 18px;
      padding: 12px;
      box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
    }

    .case-card.important {
      border-color: #f59e0b;
      background: #fffaf0;
    }

    .case-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 8px;
    }

    .building {
      font-size: 18px;
      font-weight: 1000;
      color: var(--text);
      line-height: 1.25;
    }

    .meta {
      margin-top: 2px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
      line-height: 1.35;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 9px;
      border-radius: 999px;
      background: #eaf2ff;
      color: #1d4ed8;
      font-size: 12px;
      font-weight: 1000;
      white-space: nowrap;
    }

    .pill.green {
      background: #dcfce7;
      color: #166534;
    }

    .pill.orange {
      background: #ffedd5;
      color: #9a3412;
    }

    .pill.purple {
      background: #ede9fe;
      color: #6d28d9;
    }

    .pill.red {
      background: #fee2e2;
      color: #b91c1c;
    }

    .info-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-top: 10px;
    }

    .info {
      background: #f8fafc;
      border-radius: 12px;
      padding: 8px;
    }

    .info-label {
      color: var(--muted);
      font-size: 11px;
      font-weight: 1000;
    }

    .info-value {
      margin-top: 2px;
      color: var(--text);
      font-size: 13px;
      font-weight: 1000;
      line-height: 1.35;
    }

    .note {
      margin-top: 9px;
      padding: 9px;
      border-radius: 12px;
      background: #f8fafc;
      color: #334155;
      font-size: 13px;
      font-weight: 850;
      line-height: 1.45;
      white-space: pre-wrap;
    }

    .empty {
      margin: 12px;
      padding: 18px;
      text-align: center;
      color: var(--muted);
      background: #fff;
      border: 1px dashed var(--line);
      border-radius: 16px;
      font-size: 14px;
      font-weight: 1000;
    }

    .bottom-nav {
      position: fixed;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 30;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      padding: 10px 12px 14px;
      background: rgba(238, 243, 249, 0.94);
      backdrop-filter: blur(10px);
      border-top: 1px solid var(--line);
    }

    .bottom-nav button {
      height: 42px;
      border: 0;
      border-radius: 14px;
      background: #fff;
      color: var(--text);
      font-size: 13px;
      font-weight: 1000;
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    }

    .bottom-nav button.primary {
      background: var(--green);
      color: #fff;
    }

    .modal-mask {
      position: fixed;
      inset: 0;
      z-index: 60;
      display: none;
      align-items: flex-end;
      background: rgba(15, 23, 42, 0.45);
    }

    .modal-mask.show {
      display: flex;
    }

    .modal {
      width: 100%;
      max-height: 86vh;
      overflow-y: auto;
      background: #fff;
      border-top-left-radius: 24px;
      border-top-right-radius: 24px;
      padding: 16px;
      box-shadow: 0 -16px 44px rgba(15, 23, 42, 0.24);
    }

    .modal-title {
      font-size: 22px;
      font-weight: 1000;
      color: var(--text);
      margin-bottom: 6px;
    }

    .modal-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-top: 14px;
    }

    .modal-actions button {
      height: 42px;
      border: 0;
      border-radius: 14px;
      font-size: 14px;
      font-weight: 1000;
    }

    .modal-actions .close {
      background: #64748b;
      color: #fff;
    }

    .modal-actions .call {
      background: var(--green);
      color: #fff;
    }

    @media (min-width: 760px) {
      .app {
        max-width: 520px;
        margin: 0 auto;
        border-left: 1px solid var(--line);
        border-right: 1px solid var(--line);
        background: var(--bg);
      }

      .bottom-nav {
        max-width: 520px;
        margin: 0 auto;
      }
    }
  </style>

<style id="sales_mobile_logout_button_v1">
  .logout-btn {
    background: rgba(220, 38, 38, 0.82) !important;
    color: #fff !important;
  }
</style>




<style id="sales_bottom_nav_employee_settings_v2">
  .bottom-nav {
    position: fixed !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    z-index: 40 !important;
    display: grid !important;
    grid-template-columns: repeat(4, 1fr) !important;
    gap: 8px !important;
    padding: 10px 10px calc(10px + env(safe-area-inset-bottom)) !important;
    background: rgba(238, 243, 249, .94) !important;
    backdrop-filter: blur(12px) !important;
    border-top: 1px solid #d7e1ef !important;
    max-width: 520px !important;
    margin: 0 auto !important;
  }

  .bottom-nav button {
    height: 54px !important;
    border: 0 !important;
    border-radius: 18px !important;
    background: #fff !important;
    color: #102348 !important;
    font-size: 15px !important;
    font-weight: 1000 !important;
    box-shadow: 0 8px 20px rgba(15,23,42,.08) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
    padding: 0 4px !important;
  }

  .bottom-nav button.danger {
    background: #dc2626 !important;
    color: #fff !important;
  }
</style>




  <link rel="stylesheet" href="/static/app_header_unified.css?v=20260511_title_v1">

<style id="cl15n1_sales_dispatch_card_modal_style_v1">
  .sales-action-card {
    margin: 12px 14px 0;
    padding: 14px;
    border-radius: 22px;
    background: linear-gradient(135deg, #0f3d2e, #166534);
    color: #ffffff;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.16);
  }

  .sales-action-card-title {
    font-size: 22px;
    font-weight: 1000;
    letter-spacing: 1px;
  }

  .sales-action-card-sub {
    margin-top: 4px;
    font-size: 13px;
    line-height: 1.5;
    font-weight: 850;
    opacity: 0.92;
  }

  .sales-action-card button {
    margin-top: 12px;
    width: 100%;
    height: 48px;
    border: 0;
    border-radius: 16px;
    background: #f2c94c;
    color: #ffffff;
    font-size: 17px;
    font-weight: 1000;
    text-shadow: 0 1px 2px rgba(0,0,0,.28);
  }

  .bottom-nav {
    grid-template-columns: repeat(4, 1fr) !important;
  }

  .bottom-nav button.dispatch-entry {
    background: #15803d !important;
    color: #ffffff !important;
  }

  .sales-dispatch-mask {
    position: fixed;
    inset: 0;
    z-index: 10000;
    display: none;
    align-items: flex-end;
    background: rgba(15, 23, 42, 0.45);
  }

  .sales-dispatch-mask.show {
    display: flex !important;
  }

  .sales-dispatch-modal {
    width: 100%;
    max-height: 88vh;
    overflow-y: auto;
    background: #ffffff;
    border-top-left-radius: 24px;
    border-top-right-radius: 24px;
    padding: 16px;
    box-shadow: 0 -16px 44px rgba(15, 23, 42, 0.24);
  }

  .sales-dispatch-title {
    font-size: 23px;
    font-weight: 1000;
    margin-bottom: 4px;
    color: #102348;
  }

  .sales-dispatch-sub {
    color: #64748b;
    font-size: 13px;
    font-weight: 900;
    line-height: 1.45;
    margin-bottom: 12px;
  }

  .sales-dispatch-modal label {
    display: block;
    margin: 10px 0 5px;
    color: #475569;
    font-size: 14px;
    font-weight: 1000;
  }

  .sales-dispatch-modal input,
  .sales-dispatch-modal select,
  .sales-dispatch-modal textarea {
    width: 100%;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
    background: #f8fafc;
    color: #102348;
    font-size: 15px;
    font-weight: 850;
    padding: 10px 12px;
    outline: none;
  }

  .sales-dispatch-modal input,
  .sales-dispatch-modal select {
    min-height: 46px;
  }

  .sales-dispatch-modal textarea {
    min-height: 92px;
    resize: vertical;
  }

  .sales-dispatch-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }

  .sales-dispatch-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 14px;
  }

  .sales-dispatch-actions button {
    height: 46px;
    border: 0;
    border-radius: 16px;
    font-size: 16px;
    font-weight: 1000;
  }

  .sales-dispatch-cancel {
    background: #64748b;
    color: #ffffff;
  }

  .sales-dispatch-submit {
    background: #15803d;
    color: #ffffff;
  }

  @media (min-width: 760px) {
    .sales-dispatch-mask {
      align-items: center;
      justify-content: center;
      padding: 18px;
    }

    .sales-dispatch-modal {
      max-width: 520px;
      border-radius: 24px;
    }
  }
</style>


<style id="cl15n2_sales_dispatch_building_picker_style_v1">

  .sales-dispatch-manual-hint {
    margin-top: 5px;
    color: #64748b;
    font-size: 12px;
    font-weight: 850;
    line-height: 1.4;
  }
</style>


<style id="cl15n4_sales_building_area_card_style_v1">
  .sales-building-mask {
    position: fixed;
    inset: 0;
    z-index: 20000;
    display: none;
    align-items: flex-end;
    background: rgba(15, 23, 42, 0.45);
  }

  .sales-building-mask.show {
    display: flex;
  }

  .sales-building-sheet {
    width: 100%;
    max-height: 88vh;
    overflow-y: auto;
    background: #eef3f9;
    border-top-left-radius: 24px;
    border-top-right-radius: 24px;
    padding: 14px;
    box-shadow: 0 -16px 44px rgba(15, 23, 42, 0.24);
  }

  .sales-building-head {
    background: #ffffff;
    border: 1px solid #d7e1ef;
    border-radius: 20px;
    padding: 14px;
    margin-bottom: 10px;
  }

  .sales-building-title {
    font-size: 23px;
    font-weight: 1000;
    color: #102348;
  }

  .sales-building-sub {
    margin-top: 4px;
    color: #64748b;
    font-size: 13px;
    font-weight: 900;
    line-height: 1.45;
  }

  .sales-building-filters {
    display: grid;
    grid-template-columns: 0.9fr 1.1fr;
    gap: 8px;
    margin-top: 10px;
  }

  .sales-building-filters select,
  .sales-building-filters input {
    min-height: 44px;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
    background: #f8fafc;
    color: #102348;
    font-size: 14px;
    font-weight: 850;
    padding: 8px 10px;
  }

  .sales-building-card {
    background: #ffffff;
    border: 1px solid #d7e1ef;
    border-radius: 18px;
    padding: 12px;
    margin-bottom: 10px;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
  }

  .sales-building-card-title {
    font-size: 18px;
    font-weight: 1000;
    color: #102348;
  }

  .sales-building-card-meta {
    margin-top: 6px;
    white-space: pre-wrap;
    color: #475569;
    font-size: 13px;
    font-weight: 850;
    line-height: 1.45;
  }

  .sales-building-card-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 10px;
  }

  .sales-building-card-actions button,
  .sales-building-close {
    min-height: 42px;
    border: 0;
    border-radius: 14px;
    color: #ffffff;
    font-size: 14px;
    font-weight: 1000;
  }

  .sales-building-use {
    background: #15803d;
  }

  .sales-building-close {
    background: #64748b;
    width: 100%;
    margin-top: 8px;
  }

  .sales-building-empty {
    padding: 18px;
    text-align: center;
    color: #64748b;
    font-weight: 900;
  }

  @media (min-width: 760px) {
    .sales-building-mask {
      align-items: center;
      justify-content: center;
      padding: 18px;
    }

    .sales-building-sheet {
      max-width: 560px;
      border-radius: 24px;
    }
  }
</style>


<style id="cl15n6_sales_dispatch_area_building_same_row_style_v1">
  .sales-dispatch-building-row {
    grid-template-columns: 0.82fr 1.18fr !important;
    align-items: end !important;
  }

  .sales-dispatch-building-row label {
    min-height: 20px;
  }

  @media (max-width: 420px) {
    .sales-dispatch-building-row {
      grid-template-columns: 1fr !important;
    }
  }
</style>


<style id="cl15n7b_sales_app_new_button_style_v1">
  .bottom-nav {
    grid-template-columns: repeat(5, 1fr) !important;
  }

  .bottom-nav button.new-entry {
    background: #365ee8 !important;
    color: #ffffff !important;
  }

  @media (max-width: 520px) {
    .bottom-nav {
      grid-template-columns: repeat(5, 1fr) !important;
      gap: 8px !important;
    }

    .bottom-nav button {
      min-width: 0 !important;
      padding-left: 6px !important;
      padding-right: 6px !important;
      font-size: 16px !important;
    }
  }
</style>


<style id="cl15n7c_sales_bottom_nav_force_style_v1">
  .bottom-nav {
    grid-template-columns: repeat(5, 1fr) !important;
  }

  .bottom-nav button.new-entry {
    background: #365ee8 !important;
    color: #ffffff !important;
  }

  .bottom-nav button.dispatch-entry {
    background: #15803d !important;
    color: #ffffff !important;
  }

  @media (max-width: 520px) {
    .bottom-nav {
      grid-template-columns: repeat(5, 1fr) !important;
      gap: 8px !important;
    }

    .bottom-nav button {
      min-width: 0 !important;
      padding-left: 6px !important;
      padding-right: 6px !important;
      font-size: 16px !important;
    }
  }
</style>


<style id="cl15n7d_sales_new_button_route_style_v1">
  .bottom-nav {
    grid-template-columns: repeat(5, 1fr) !important;
  }

  .bottom-nav button.new-entry {
    background: #365ee8 !important;
    color: #ffffff !important;
  }

  @media (max-width: 520px) {
    .bottom-nav {
      grid-template-columns: repeat(5, 1fr) !important;
      gap: 8px !important;
    }

    .bottom-nav button {
      min-width: 0 !important;
      padding-left: 6px !important;
      padding-right: 6px !important;
      font-size: 16px !important;
    }
  }
</style>


<style id="cl15n8_sales_complete_button_style_v1">
  .modal-actions button.complete {
    background: #15803d !important;
    color: #ffffff !important;
  }

  .modal-actions.three-actions {
    grid-template-columns: 1fr 1fr 1fr !important;
  }

  @media (max-width: 520px) {
    .modal-actions.three-actions {
      grid-template-columns: 1fr !important;
    }
  }
</style>

</head>

<body>
  <div class="app">
    <section class="hero app-standard-hero">
      <div class="hero-main">
        <span class="hero-logo">
          <img class="hero-logo-img" src="/static/shinnan_home_logo.png" alt="Logo">
        </span>
        <h1 class="hero-title">\u8a0a\u5357\u696d\u52d9\u7cfb\u7d71</h1>
      </div>
      <div id="sales_employee_name" class="hero-sub">\u767b\u5165\u8005</div>
    </section>

    <section class="summary">
      <div class="summary-card" onclick="setFilter('今日')">
        <div class="summary-label">今日</div>
        <div id="sum_today" class="summary-num">0</div>
      </div>

      <div class="summary-card" onclick="setFilter('重要')">
        <div class="summary-label">重要</div>
        <div id="sum_important" class="summary-num">0</div>
      </div>

      <div class="summary-card" onclick="setFilter('事件')">
        <div class="summary-label">事件</div>
        <div id="sum_event" class="summary-num">0</div>
      </div>
    </section>

    <nav class="filters">
      <button class="filter-btn active" data-filter="全部" onclick="setFilter('全部')">全部</button>
      <button class="filter-btn" data-filter="今日" onclick="setFilter('今日')">今日</button>
      <button class="filter-btn" data-filter="重要" onclick="setFilter('重要')">重要</button>
      <button class="filter-btn" data-filter="待拜訪" onclick="setFilter('待拜訪')">待拜訪</button>
      <button class="filter-btn" data-filter="合約" onclick="setFilter('合約')">合約</button>
      <button class="filter-btn" data-filter="事件" onclick="setFilter('事件')">事件</button>
    </nav>

    <div class="search-box">
      <input id="keyword" placeholder="搜尋大樓、總幹事、電話、負責業務" oninput="renderList()">
    </div>

    <div id="section_title" class="section-title">全部業務工作</div>
    <main id="list" class="list"></main>

    <div class="sales-action-card">
      <div class="sales-action-card-title">\u696d\u52d9\u6d3e\u5de5</div>
      <div class="sales-action-card-sub">\u91dd\u5c0d\u5927\u6a13\u516c\u8a2d\u3001\u793e\u5340\u56de\u994b\u3001\u7ba1\u59d4\u6703\u9700\u6c42\uff0c\u5efa\u7acb\u8de8\u90e8\u9580\u6d3e\u5de5\u55ae\u3002</div>
      <button type="button" data-sales-dispatch-open="1" onclick="openSalesDispatchModal()">\u5efa\u7acb\u6d3e\u5de5</button>
    </div>

    <div class="bottom-nav">
      <button type="button" onclick="location.href='/app'">APP\u9996\u9801</button>
      <button type="button" onclick="openSalesBuildingCards()">\u5927\u6a13\u540d\u9304</button>
      <button type="button" class="dispatch-entry" data-sales-dispatch-open="1" onclick="openSalesDispatchModal()">\u6d3e\u5de5</button>
      <button type="button" class="new-entry" onclick="cl15n7dOpenSalesNewCard()">\u65b0\u589e</button>
      <button type="button" class="danger" onclick="location.href='/employee/logout?next=/'">\u767b\u51fa</button>
    </div>
  </div>

  
  <div id="sales_dispatch_mask" class="sales-dispatch-mask" onclick="closeSalesDispatchModal(event)">
    <div class="sales-dispatch-modal" onclick="event.stopPropagation()">
      <div class="sales-dispatch-title">\u696d\u52d9\u6d3e\u5de5</div>
      <div class="sales-dispatch-sub">\u5efa\u7acb\u516c\u8a2d\u3001\u56de\u994b\u6216\u793e\u5340\u9700\u6c42\u7684\u8de8\u90e8\u9580\u6d3e\u5de5\u55ae\u3002</div>

      <div class="sales-dispatch-grid">
        <div>
          <label>\u6d3e\u5de5\u55ae\u4f4d</label>
          <select id="sales_dispatch_target_department"></select>
        </div>
        <div>
          <label>\u9700\u6c42\u985e\u578b</label>
          <select id="sales_dispatch_request_type">
            <option value="\u516c\u8a2d">\u516c\u8a2d</option>
            <option value="\u56de\u994b">\u56de\u994b</option>
            <option value="\u793e\u5340\u9700\u6c42">\u793e\u5340\u9700\u6c42</option>
            <option value="\u5176\u4ed6">\u5176\u4ed6</option>
          </select>
        </div>
      </div>

      <label>\u8981\u6c42\u55ae\u4f4d</label>
      <input id="sales_dispatch_request_unit" list="sales_dispatch_request_unit_list" placeholder="\u53ef\u5f9e\u4e0b\u62c9\u9078\u64c7\uff0c\u6216\u76f4\u63a5\u624b\u52d5\u8f38\u5165">
      <datalist id="sales_dispatch_request_unit_list">
        <option value="\u7ba1\u59d4\u6703"></option>
        <option value="\u7ba1\u7406\u5ba4"></option>
        <option value="\u696d\u52d9\u90e8"></option>
        <option value="\u8001\u95c6\u6307\u793a"></option>
        <option value="\u793e\u5340\u4e3b\u59d4"></option>
        <option value="\u7e3d\u5e79\u4e8b"></option>
        <option value="\u5ba2\u6236\u56de\u994b"></option>
      </datalist>

      <input type="hidden" id="sales_dispatch_building_no">

      <div class="sales-dispatch-grid sales-dispatch-building-row">
        <div>
          <label>\u5340\u57df</label>
          <select id="sales_dispatch_building_area" onchange="populateSalesDispatchBuildingNameList()">
            <option value="">\u5168\u90e8\u5340\u57df</option>
          </select>
        </div>
        <div>
          <label>\u5927\u6a13\u540d\u7a31</label>
          <input id="sales_dispatch_building_name" list="sales_dispatch_building_name_list" placeholder="\u53ef\u5f9e\u540d\u518a\u9078\u64c7\uff0c\u6216\u624b\u52d5\u8f38\u5165" oninput="applySalesDispatchBuildingByName()">
          <datalist id="sales_dispatch_building_name_list"></datalist>
        </div>
      </div>
      <div class="sales-dispatch-manual-hint">\u9078\u5340\u57df\u53ef\u7e2e\u5c0f\u540d\u518a\u5019\u9078\uff1b\u82e5\u662f\u65b0\u5927\u6a13\uff0c\u53ef\u76f4\u63a5\u624b\u52d5\u8f38\u5165\u4e0b\u65b9\u8cc7\u6599\u3002</div>

      <label>\u5730\u5740</label>
      <input id="sales_dispatch_service_address" placeholder="\u540d\u518a\u5167\u5927\u6a13\u6703\u81ea\u52d5\u5e36\u5165\uff1b\u65b0\u5927\u6a13\u8acb\u624b\u52d5\u586b\u5beb">

      <div class="sales-dispatch-grid">
        <div>
          <label>\u806f\u7d61\u4eba</label>
          <input id="sales_dispatch_contact_name" placeholder="\u540d\u518a\u6703\u81ea\u52d5\u5e36\u5165\uff1b\u4e5f\u53ef\u624b\u52d5\u8f38\u5165">
        </div>
        <div>
          <label>\u96fb\u8a71</label>
          <input id="sales_dispatch_contact_phone" placeholder="\u540d\u518a\u6703\u81ea\u52d5\u5e36\u5165\uff1b\u4e5f\u53ef\u624b\u52d5\u8f38\u5165">
        </div>
      </div>

      <label>\u9700\u6c42\u5167\u5bb9</label>
      <textarea id="sales_dispatch_description" placeholder="\u8acb\u8aaa\u660e\u516c\u8a2d\u9700\u6c42\u3001\u793e\u5340\u56de\u994b\u6216\u9700\u5354\u52a9\u4e8b\u9805"></textarea>

      <div class="sales-dispatch-actions">
        <button class="sales-dispatch-cancel" type="button" onclick="hideSalesDispatchModal()">\u53d6\u6d88</button>
        <button class="sales-dispatch-submit" type="button" onclick="submitSalesDispatchRequest()">\u9001\u51fa\u6d3e\u5de5</button>
      </div>
    </div>
  </div>


  <div id="sales_building_mask" class="sales-building-mask" onclick="closeSalesBuildingCards(event)">
    <div class="sales-building-sheet" onclick="event.stopPropagation()">
      <div class="sales-building-head">
        <div class="sales-building-title">\u5927\u6a13\u540d\u9304</div>
        <div class="sales-building-sub">\u624b\u6a5f APP \u5361\u7247\u7248\uff0c\u53ef\u4f9d\u5340\u57df\u8207\u95dc\u9375\u5b57\u67e5\u8a62\u3002</div>
        <div class="sales-building-filters">
          <select id="sales_building_area_filter" onchange="renderSalesBuildingCards()">
            <option value="">\u5168\u90e8\u5340\u57df</option>
          </select>
          <input id="sales_building_keyword" placeholder="\u641c\u5c0b\u5927\u6a13\u540d\u7a31\uff0f\u5730\u5740" oninput="renderSalesBuildingCards()">
        </div>
        <button class="sales-building-close" type="button" onclick="hideSalesBuildingCards()">\u95dc\u9589</button>
      </div>
      <div id="sales_building_card_list"></div>
    </div>
  </div>

<div id="detail_mask" class="modal-mask" onclick="closeDetail(event)">
    <div class="modal" onclick="event.stopPropagation()">
      <div id="detail_title" class="modal-title"></div>
      <div id="detail_body"></div>

            <div class="modal-actions three-actions">
        <button class="close" onclick="hideDetail()">\u95dc\u9589</button>
        <button class="complete" onclick="completeSalesBusinessRecord()">\u5df2\u5b8c\u6210</button>
        <button id="call_button" class="call">\u64a5\u6253\u7e3d\u5e79\u4e8b</button>
      </div>
    </div>
  </div>

  <script>
    let records = [];
    let currentSalesDetailId = null;
    let currentFilter = "全部";

    function todayText() {
      const d = new Date();
      return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    }

    function esc(v) {
      return String(v ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function isEventActive(item) {
      const eventType = String((item && item.event_type) || "").trim();
      const eventStatus = String((item && item.event_status) || "").trim();
      return eventType && eventType !== "無" && !["", "無", "已完成", "完成"].includes(eventStatus);
    }

    function isToday(item) {
      const t = todayText();
      return item.next_visit === t || item.event_schedule_date === t;
    }

    function isContract(item) {
      const status = String((item && item.contract_status) || "").trim();
      return ["即將到期", "洽談中", "續約中", "待客戶回覆"].includes(status);
    }

    function buildActionText(item) {
      const parts = [];

      if (item.event_type && item.event_type !== "無") parts.push(item.event_type);
      if (item.event_status && item.event_status !== "無") parts.push(item.event_status);
      if (item.business_type) parts.push(item.business_type);
      if (isContract(item)) parts.push("合約追蹤");
      if (item.feedback_type && item.feedback_type !== "無") parts.push(item.feedback_type);

      return parts.join("｜") || "拜訪管理室";
    }

    function statusPill(item) {
      if (item.important_schedule) return '<span class="pill orange">重要</span>';
      if (isToday(item)) return '<span class="pill green">今日</span>';
      if (isContract(item)) return '<span class="pill purple">合約</span>';
      if (isEventActive(item)) return '<span class="pill red">事件</span>';
      return '<span class="pill">追蹤</span>';
    }

    function setFilter(filter) {
      currentFilter = filter;

      document.querySelectorAll(".filter-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.filter === filter);
      });

      renderList();
    }

    function filterRecords() {
      const keyword = document.getElementById("keyword").value.trim().toLowerCase();

      return records.filter(item => {
        if (currentFilter === "今日" && !isToday(item)) return false;
        if (currentFilter === "重要" && !item.important_schedule) return false;
        if (currentFilter === "待拜訪" && !item.next_visit) return false;
        if (currentFilter === "合約" && !isContract(item)) return false;
        if (currentFilter === "事件" && !isEventActive(item)) return false;

        if (keyword) {
          const hay = [
            item.building_name,
            item.area,
            item.manager_name,
            item.manager_phone,
            item.owner,
            item.business_type,
            item.status,
            item.event_type,
            item.event_status,
            item.contract_status
          ].join(" ").toLowerCase();

          if (!hay.includes(keyword)) return false;
        }

        return true;
      });
    }

    function renderSummary() {
      document.getElementById("sum_today").textContent = records.filter(isToday).length;
      document.getElementById("sum_important").textContent = records.filter(x => x.important_schedule).length;
      document.getElementById("sum_event").textContent = records.filter(isEventActive).length;
    }

    function renderList() {
      renderSummary();

      const rows = filterRecords();
      const box = document.getElementById("list");
      const title = document.getElementById("section_title");

      title.textContent = currentFilter + "業務工作｜" + rows.length + " 筆";

      if (!rows.length) {
        box.innerHTML = '<div class="empty">目前沒有符合條件的業務工作。</div>';
        return;
      }

      box.innerHTML = rows.map((item, index) => {
        const realIndex = records.indexOf(item);

        return `
          <article class="case-card ${item.important_schedule ? "important" : ""}" onclick="showDetail(${realIndex})">
            <div class="case-head">
              <div>
                <div class="building">${esc(item.building_name || "-")}</div>
                <div class="meta">${esc(item.area || "-")}｜負責：${esc(item.owner || "-")}</div>
              </div>
              ${statusPill(item)}
            </div>

            <div class="info-grid">
              <div class="info">
                <div class="info-label">總幹事</div>
                <div class="info-value">${esc(item.manager_name || "-")}<br>${esc(item.manager_phone || "-")}</div>
              </div>

              <div class="info">
                <div class="info-label">下次拜訪</div>
                <div class="info-value">${esc(item.next_visit || "-")}</div>
              </div>

              <div class="info">
                <div class="info-label">狀態</div>
                <div class="info-value">${esc(item.status || "-")}｜${esc(item.contract_status || "-")}</div>
              </div>

              <div class="info">
                <div class="info-label">業務行為</div>
                <div class="info-value">${esc(buildActionText(item))}</div>
              </div>
            </div>

            <div class="note">${esc(item.business_note || "無備註")}</div>
          </article>
        `;
      }).join("");
    }

    function showDetail(index) {
      const item = records[index];
      if (!item) return;
      currentSalesDetailId = item.id;

      document.getElementById("detail_title").textContent = item.building_name || "業務資料";

      document.getElementById("detail_body").innerHTML = `
        <div class="info-grid">
          <div class="info">
            <div class="info-label">大樓</div>
            <div class="info-value">${esc(item.building_name || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">區域</div>
            <div class="info-value">${esc(item.area || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">管理公司</div>
            <div class="info-value">${esc(item.management_company || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">管理室電話</div>
            <div class="info-value">${esc(item.management_phone || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">總幹事</div>
            <div class="info-value">${esc(item.manager_name || "-")}<br>${esc(item.manager_phone || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">負責業務</div>
            <div class="info-value">${esc(item.owner || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">業務類型</div>
            <div class="info-value">${esc(item.business_type || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">目前狀態</div>
            <div class="info-value">${esc(item.status || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">合約</div>
            <div class="info-value">${esc(item.contract_status || "-")}<br>${esc(item.contract_end_date || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">事件</div>
            <div class="info-value">${esc(item.event_type || "-")}<br>${esc(item.event_status || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">委員會</div>
            <div class="info-value">${esc(item.committee_time || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">住戶大會</div>
            <div class="info-value">${esc(item.resident_meeting_time || "-")}</div>
          </div>
        </div>

        <div class="note">${esc(item.business_note || "無備註")}</div>
      `;

      const callBtn = document.getElementById("call_button");
      const phone = item.manager_phone || item.management_phone || "";

      callBtn.onclick = function () {
        if (!phone) {
          alert("沒有可撥打電話");
          return;
        }

        location.href = "tel:" + phone;
      };

      document.getElementById("detail_mask").classList.add("show");
    }


    async function completeSalesBusinessRecord() {
      if (!currentSalesDetailId) {
        alert("\u627e\u4e0d\u5230\u76ee\u524d\u696d\u52d9\u6848\u4ef6");
        return;
      }

      if (!confirm("\u78ba\u8a8d\u5c07\u6b64\u696d\u52d9\u6848\u4ef6\u6a19\u8a18\u70ba\u5df2\u5b8c\u6210\uff1f\\n\u5b8c\u6210\u5f8c\u5c07\u5f9e APP \u5217\u8868\u79fb\u9664\u3002")) {
        return;
      }

      const res = await fetch("/api/app/sales/business-records/" + encodeURIComponent(currentSalesDetailId) + "/complete", {
        method: "POST",
        credentials: "same-origin"
      });

      const data = await res.json().catch(function () { return {}; });

      if (!res.ok || !data.ok) {
        alert(data.error || "\u66f4\u65b0\u5931\u6557");
        return;
      }

      alert("\u5df2\u6a19\u8a18\u70ba\u5df2\u5b8c\u6210\u3002");
      hideDetail();
      await reloadData();
    }

    function hideDetail() {
      document.getElementById("detail_mask").classList.remove("show");
      currentSalesDetailId = null;
    }

    function closeDetail(event) {
      if (event.target.id === "detail_mask") hideDetail();
    }

    async function reloadData() {
      const box = document.getElementById("list");
      box.innerHTML = '<div class="empty">\u8cc7\u6599\u8f09\u5165\u4e2d...</div>';

      try {
        const res = await fetch("/api/app/sales/business-records?ts=" + Date.now(), {
          cache: "no-store",
          credentials: "same-origin"
        });

        const data = await res.json().catch(function () {
          return null;
        });

        if (!res.ok) {
          const msg = data && data.error ? data.error : ("\u696d\u52d9 API \u8b80\u53d6\u5931\u6557\uff1a" + res.status);
          records = [];
          renderList();
          box.innerHTML = '<div class="empty">' + esc(msg) + '</div>';
          return;
        }

        if (data && data.ok === false) {
          records = [];
          renderList();
          box.innerHTML = '<div class="empty">' + esc(data.error || "\u696d\u52d9 API \u56de\u50b3\u932f\u8aa4") + '</div>';
          return;
        } else if (Array.isArray(data)) {
          records = data;
        } else if (data && Array.isArray(data.items)) {
          records = data.items;
        } else if (data && Array.isArray(data.records)) {
          records = data.records;
        } else {
          records = [];
          renderList();
          box.innerHTML = '<div class="empty">\u696d\u52d9 API \u56de\u50b3\u683c\u5f0f\u4e0d\u7b26\u5408\u9810\u671f\u3002</div>';
          return;
        }

        records.sort((a, b) => {
          const ai = a.important_schedule ? 0 : 1;
          const bi = b.important_schedule ? 0 : 1;
          if (ai !== bi) return ai - bi;

          const ad = a.next_visit || a.event_schedule_date || "9999-12-31";
          const bd = b.next_visit || b.event_schedule_date || "9999-12-31";

          return String(ad).localeCompare(String(bd));
        });

        renderList();
      } catch (err) {
        records = [];
        renderList();
        box.innerHTML = '<div class="empty">\u696d\u52d9 APP \u8b80\u53d6\u932f\u8aa4\uff1a' + esc(err && err.message ? err.message : String(err)) + '</div>';
      }
    }



    let salesDispatchBuildings = [];

    function uniqueSalesAreas(items) {
      const seen = {};
      const out = [];

      (items || []).forEach(function (b) {
        const area = String(b.area || "").trim();
        if (!area || seen[area]) return;
        seen[area] = true;
        out.push(area);
      });

      return out.sort();
    }

    async function loadSalesDispatchBuildings() {
      try {
        const res = await fetch("/api/app/sales/dispatch/buildings?ts=" + Date.now(), {
          cache: "no-store",
          credentials: "same-origin"
        });

        const data = await res.json();

        if (!res.ok || !data.ok) {
          salesDispatchBuildings = [];
          return;
        }

        salesDispatchBuildings = data.items || [];
        populateSalesDispatchBuildingAreas();
        populateSalesDispatchBuildingNameList();
      } catch (err) {
        salesDispatchBuildings = [];
      }
    }

    function populateSalesDispatchBuildingAreas() {
      const areaSelect = document.getElementById("sales_dispatch_building_area");
      if (!areaSelect) return;

      const areas = uniqueSalesAreas(salesDispatchBuildings);
      const current = areaSelect.value;

      areaSelect.innerHTML = '<option value="">\u5168\u90e8\u5340\u57df</option>' + areas.map(function (area) {
        return '<option value="' + esc(area) + '">' + esc(area) + '</option>';
      }).join("");

      if (current && areas.includes(current)) {
        areaSelect.value = current;
      }
    }

    function filteredSalesDispatchBuildingsForArea() {
      const areaSelect = document.getElementById("sales_dispatch_building_area");
      const area = areaSelect ? String(areaSelect.value || "").trim() : "";

      return (salesDispatchBuildings || []).filter(function (b) {
        if (!area) return true;
        return String(b.area || "").trim() === area;
      });
    }

    function populateSalesDispatchBuildingNameList() {
      const list = document.getElementById("sales_dispatch_building_name_list");
      if (!list) return;

      const items = filteredSalesDispatchBuildingsForArea();

      list.innerHTML = items.map(function (b) {
        return '<option value="' + esc(b.name || "") + '"></option>';
      }).join("");

      applySalesDispatchBuildingByName();
    }

    function findSalesDispatchBuildingByNo(buildingNo) {
      const value = String(buildingNo || "").trim();

      if (!value) return null;

      return salesDispatchBuildings.find(function (b) {
        return String(b.building_no || "").trim() === value;
      }) || null;
    }

    function findSalesDispatchBuildingByName(name) {
      const value = String(name || "").trim();
      const areaSelect = document.getElementById("sales_dispatch_building_area");
      const area = areaSelect ? String(areaSelect.value || "").trim() : "";

      if (!value) return null;

      return (salesDispatchBuildings || []).find(function (b) {
        const nameOk = String(b.name || "").trim() === value;
        const areaOk = !area || String(b.area || "").trim() === area;
        return nameOk && areaOk;
      }) || (salesDispatchBuildings || []).find(function (b) {
        return String(b.name || "").trim() === value;
      }) || null;
    }

    function applySalesDispatchBuildingByName() {
      const noEl = document.getElementById("sales_dispatch_building_no");
      const nameEl = document.getElementById("sales_dispatch_building_name");
      const addressEl = document.getElementById("sales_dispatch_service_address");
      const contactEl = document.getElementById("sales_dispatch_contact_name");
      const phoneEl = document.getElementById("sales_dispatch_contact_phone");

      if (!noEl || !nameEl) return;

      const b = findSalesDispatchBuildingByName(nameEl.value);

      if (!b) {
        noEl.value = "";
        return;
      }

      noEl.value = b.building_no || "";

      if (addressEl && !String(addressEl.value || "").trim()) addressEl.value = b.address || "";
      if (contactEl && !String(contactEl.value || "").trim()) contactEl.value = b.manager_name || "";
      if (phoneEl && !String(phoneEl.value || "").trim()) phoneEl.value = b.phone || "";

      if (addressEl && b.address) addressEl.value = b.address || "";
      if (contactEl && b.manager_name) contactEl.value = b.manager_name || "";
      if (phoneEl && b.phone) phoneEl.value = b.phone || "";
    }

    function getFilteredSalesBuildingCards() {
      const area = String((document.getElementById("sales_building_area_filter") || {}).value || "").trim();
      const keyword = String((document.getElementById("sales_building_keyword") || {}).value || "").trim().toLowerCase();

      return (salesDispatchBuildings || []).filter(function (b) {
        const areaOk = !area || String(b.area || "") === area;
        const hay = [b.name, b.address, b.area, b.management_company, b.manager_name, b.phone].join(" ").toLowerCase();
        const keyOk = !keyword || hay.includes(keyword);
        return areaOk && keyOk;
      });
    }

    function populateSalesBuildingCardAreas() {
      const select = document.getElementById("sales_building_area_filter");
      if (!select) return;

      const areas = uniqueSalesAreas(salesDispatchBuildings);
      const current = select.value;

      select.innerHTML = '<option value="">\u5168\u90e8\u5340\u57df</option>' + areas.map(function (area) {
        return '<option value="' + esc(area) + '">' + esc(area) + '</option>';
      }).join("");

      if (current && areas.includes(current)) select.value = current;
    }

    function renderSalesBuildingCards() {
      const list = document.getElementById("sales_building_card_list");
      if (!list) return;

      const items = getFilteredSalesBuildingCards();

      if (!items.length) {
        list.innerHTML = '<div class="sales-building-empty">\u627e\u4e0d\u5230\u7b26\u5408\u689d\u4ef6\u7684\u5927\u6a13\u3002</div>';
        return;
      }

      list.innerHTML = items.slice(0, 120).map(function (b) {
        const meta = [
          b.area ? "\u5340\u57df\uff1a" + b.area : "",
          b.address ? "\u5730\u5740\uff1a" + b.address : "",
          b.manager_name ? "\u806f\u7d61\u4eba\uff1a" + b.manager_name : "",
          b.phone ? "\u96fb\u8a71\uff1a" + b.phone : ""
        ].filter(Boolean).join("\\n");

        return '<div class="sales-building-card">' +
          '<div class="sales-building-card-title">' + esc(b.name || "") + '</div>' +
          '<div class="sales-building-card-meta">' + esc(meta) + '</div>' +
          '<div class="sales-building-card-actions">' +
            '<button class="sales-building-use" type="button" data-building-no="' + esc(b.building_no || "") + '" onclick="useBuildingCardForDispatch(this.dataset.buildingNo)">\u5e36\u5165\u6d3e\u5de5</button>' +
            '<button class="sales-building-close" type="button" onclick="hideSalesBuildingCards()">\u95dc\u9589</button>' +
          '</div>' +
        '</div>';
      }).join("");
    }

    async function openSalesBuildingCards() {
      const mask = document.getElementById("sales_building_mask");
      if (!mask) return;

      mask.classList.add("show");

      if (!salesDispatchBuildings.length) {
        await loadSalesDispatchBuildings();
      }

      populateSalesBuildingCardAreas();
      renderSalesBuildingCards();
    }

    function hideSalesBuildingCards() {
      const mask = document.getElementById("sales_building_mask");
      if (mask) mask.classList.remove("show");
    }

    function closeSalesBuildingCards(event) {
      if (event && event.target && event.target.id === "sales_building_mask") {
        hideSalesBuildingCards();
      }
    }

    function useBuildingCardForDispatch(buildingNo) {
      const b = findSalesDispatchBuildingByNo(buildingNo);
      if (!b) return;

      hideSalesBuildingCards();
      openSalesDispatchModal();

      setTimeout(function () {
        const areaSelect = document.getElementById("sales_dispatch_building_area");
        const nameEl = document.getElementById("sales_dispatch_building_name");
        const noEl = document.getElementById("sales_dispatch_building_no");
        const addressEl = document.getElementById("sales_dispatch_service_address");
        const contactEl = document.getElementById("sales_dispatch_contact_name");
        const phoneEl = document.getElementById("sales_dispatch_contact_phone");

        if (areaSelect) {
          areaSelect.value = b.area || "";
          populateSalesDispatchBuildingNameList();
        }

        if (noEl) noEl.value = b.building_no || "";
        if (nameEl) nameEl.value = b.name || "";
        if (addressEl) addressEl.value = b.address || "";
        if (contactEl) contactEl.value = b.manager_name || "";
        if (phoneEl) phoneEl.value = b.phone || "";
      }, 120);
    }

    async function loadSalesDispatchDepartments() {
      const select = document.getElementById("sales_dispatch_target_department");
      if (!select) return;

      select.innerHTML = '<option value="">\u8f09\u5165\u4e2d...</option>';

      try {
        const res = await fetch("/api/app/sales/dispatch/departments?ts=" + Date.now(), {
          cache: "no-store",
          credentials: "same-origin"
        });

        const data = await res.json();

        if (!res.ok || !data.ok) {
          select.innerHTML = '<option value="">\u8b80\u53d6\u5931\u6557</option>';
          return;
        }

        select.innerHTML = '<option value="">\u8acb\u9078\u64c7\u6d3e\u5de5\u55ae\u4f4d</option>' + (data.items || []).map(function (name) {
          return '<option value="' + esc(name) + '">' + esc(name) + '</option>';
        }).join("");
      } catch (err) {
        select.innerHTML = '<option value="">\u8b80\u53d6\u5931\u6557</option>';
      }
    }

    function openSalesDispatchModal() {
      const mask = document.getElementById("sales_dispatch_mask");
      if (!mask) return;

      const selected = records.find(function (item) {
        return item && item.__selected_for_dispatch;
      });

      mask.classList.add("show");
      loadSalesDispatchDepartments();
      loadSalesDispatchBuildings();
    }

    function hideSalesDispatchModal() {
      const mask = document.getElementById("sales_dispatch_mask");
      if (mask) mask.classList.remove("show");
    }

    function closeSalesDispatchModal(event) {
      if (event && event.target && event.target.id === "sales_dispatch_mask") {
        hideSalesDispatchModal();
      }
    }

    function getValue(id) {
      const el = document.getElementById(id);
      return el ? String(el.value || "").trim() : "";
    }

    async function submitSalesDispatchRequest() {
      const payload = {
        target_department: getValue("sales_dispatch_target_department"),
        request_unit: getValue("sales_dispatch_request_unit"),
        request_type: getValue("sales_dispatch_request_type"),
        building_no: getValue("sales_dispatch_building_no"),
        building_name: getValue("sales_dispatch_building_name"),
        service_address: getValue("sales_dispatch_service_address"),
        contact_name: getValue("sales_dispatch_contact_name"),
        contact_phone: getValue("sales_dispatch_contact_phone"),
        description: getValue("sales_dispatch_description")
      };

      const res = await fetch("/api/app/sales/dispatch/create", {
        method: "POST",
        credentials: "same-origin",
        headers: {"Content-Type": "application/json; charset=utf-8"},
        body: JSON.stringify(payload)
      });

      const data = await res.json().catch(function () { return {}; });

      if (!res.ok || !data.ok) {
        alert(data.error || "\u6d3e\u5de5\u5efa\u7acb\u5931\u6557");
        return;
      }

      alert("\u6d3e\u5de5\u5df2\u5efa\u7acb\uff1a" + data.ticket_no);
      hideSalesDispatchModal();
      reloadData();
    }


    function cl15n7dOpenSalesNewCard() {
      if (typeof window.openSalesNewModal === "function") {
        window.openSalesNewModal();
      }
    }

    window.reloadData = reloadData;
    window.renderList = renderList;
    window.showDetail = showDetail;
    window.hideDetail = hideDetail;
    window.closeDetail = closeDetail;
    window.completeSalesBusinessRecord = completeSalesBusinessRecord;
    window.openSalesBuildingCards = openSalesBuildingCards;
    window.hideSalesBuildingCards = hideSalesBuildingCards;
    window.closeSalesBuildingCards = closeSalesBuildingCards;
    window.useBuildingCardForDispatch = useBuildingCardForDispatch;
    window.openSalesDispatchModal = openSalesDispatchModal;
    window.hideSalesDispatchModal = hideSalesDispatchModal;
    window.closeSalesDispatchModal = closeSalesDispatchModal;
    window.applySalesDispatchBuildingByName = applySalesDispatchBuildingByName;
    window.populateSalesDispatchBuildingNameList = populateSalesDispatchBuildingNameList;
    window.submitSalesDispatchRequest = submitSalesDispatchRequest;
    window.cl15n7dOpenSalesNewCard = cl15n7dOpenSalesNewCard;
    // openSalesNewModal 等函式由下方 sales_new_modal_js_v1 IIFE export 到 window

    document.addEventListener("click", function (event) {
      const opener = event.target && event.target.closest ? event.target.closest("[data-sales-dispatch-open]") : null;
      if (!opener) return;
      event.preventDefault();
      openSalesDispatchModal();
    });

    reloadData();
  </script>

<script id="sales_header_exact_user_v2">
(function () {
  async function setSalesEmployeeNameFromSession() {
    var box = document.getElementById("sales_employee_name");
    if (!box) return;

    box.textContent = "登入者讀取中...";

    try {
      var res = await fetch("/api/app/employee/profile?ts=" + Date.now(), {
        cache: "no-store",
        credentials: "same-origin"
      });

      if (!res.ok) {
        box.textContent = "登入者";
        return;
      }

      var data = await res.json();
      var profile = data.profile || data.user || data || {};

      var name =
        profile.display_name ||
        profile.name ||
        profile.staff_name ||
        profile.staff_code ||
        "";

      box.textContent = name || "\\u767b\\u5165\\u8005";

    } catch (err) {
      box.textContent = "登入者";
    }
  }

  window.setSalesEmployeeNameFromSession = setSalesEmployeeNameFromSession;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setSalesEmployeeNameFromSession);
  } else {
    setSalesEmployeeNameFromSession();
  }

  window.addEventListener("load", setSalesEmployeeNameFromSession);
  setTimeout(setSalesEmployeeNameFromSession, 300);
  setTimeout(setSalesEmployeeNameFromSession, 1200);
})();
</script>


<script>
(function(){
  function fixSalesUserLabel(){
    var el = document.getElementById("sales_employee_name");
    if (!el) return;
    var t = (el.textContent || "").trim();
    if (t.indexOf("\uff5c") >= 0) t = t.split("\uff5c")[0].trim();
    if (t.indexOf("|") >= 0) t = t.split("|")[0].trim();
    el.textContent = t;
  }
  fixSalesUserLabel();
  setTimeout(fixSalesUserLabel, 100);
  setTimeout(fixSalesUserLabel, 500);
})();
</script>


<!-- 新增業務案件 Sheet（與派工 modal 共用同一套樣式） -->
<style id="sales_new_modal_style_v1">
  .sales-new-mask {
    position: fixed;
    inset: 0;
    z-index: 10000;
    display: none;
    align-items: flex-end;
    background: rgba(15, 23, 42, 0.45);
  }
  .sales-new-mask.show { display: flex !important; }
  .sales-new-modal {
    width: 100%;
    max-height: 88vh;
    overflow-y: auto;
    background: #ffffff;
    border-top-left-radius: 24px;
    border-top-right-radius: 24px;
    padding: 16px;
    box-shadow: 0 -16px 44px rgba(15, 23, 42, 0.24);
  }
  .sales-new-modal::-webkit-scrollbar { width: 8px; }
  .sales-new-modal::-webkit-scrollbar-thumb { background: #8b949e; border-radius: 999px; }
  .sales-new-modal::-webkit-scrollbar-track { background: transparent; }
  .sales-new-title {
    font-size: 23px;
    font-weight: 1000;
    margin-bottom: 4px;
    color: #102348;
  }
  .sales-new-sub {
    color: #64748b;
    font-size: 13px;
    font-weight: 900;
    line-height: 1.45;
    margin-bottom: 12px;
  }
  .sales-new-section {
    margin: 16px 0 8px;
    color: #334155;
    font-size: 15px;
    font-weight: 1000;
    padding-bottom: 4px;
    border-bottom: 1px solid #e2e8f0;
  }
  .sales-new-modal label {
    display: block;
    margin: 10px 0 5px;
    color: #475569;
    font-size: 14px;
    font-weight: 1000;
  }
  .sales-new-modal input,
  .sales-new-modal select,
  .sales-new-modal textarea {
    width: 100%;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
    background: #f8fafc;
    color: #102348;
    font-family: inherit;
    font-size: 15px;
    font-weight: 850;
    padding: 10px 12px;
    outline: none;
  }
  .sales-new-modal input,
  .sales-new-modal select { min-height: 46px; padding: 0 12px; }
  .sales-new-modal textarea { min-height: 92px; resize: vertical; }
  .sales-new-modal input:focus,
  .sales-new-modal select:focus,
  .sales-new-modal textarea:focus {
    border-color: #365ee8;
    box-shadow: 0 0 0 3px rgba(54, 94, 232, .12);
  }
  .sales-new-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .sales-new-building-row {
    display: grid;
    grid-template-columns: .85fr 1.15fr 88px;
    gap: 10px;
    align-items: end;
  }
  .sales-new-choose-btn {
    min-height: 46px;
    border: 0;
    border-radius: 14px;
    background: #365ee8;
    color: #ffffff;
    font-size: 14px;
    font-weight: 1000;
    cursor: pointer;
  }
  .sales-new-hint {
    margin-top: 5px;
    color: #64748b;
    font-size: 12px;
    font-weight: 850;
    line-height: 1.4;
  }
  .sales-new-check-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 6px;
    color: #102348;
    font-size: 14px;
    font-weight: 1000;
  }
  .sales-new-check-row input[type=checkbox] {
    width: 20px;
    height: 20px;
    min-height: unset;
    padding: 0;
  }
  .sales-new-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 14px;
    padding-bottom: 8px;
  }
  .sales-new-actions button {
    height: 46px;
    border: 0;
    border-radius: 16px;
    font-size: 16px;
    font-weight: 1000;
  }
  .sales-new-cancel { background: #64748b; color: #ffffff; }
  .sales-new-save { background: #15803d; color: #ffffff; }
  .sales-new-msg {
    margin: 8px 0;
    padding: 10px 12px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 1000;
    display: none;
  }
  .sales-new-msg.ok { display: block; background: #dcfce7; color: #166534; }
  .sales-new-msg.err { display: block; background: #fee2e2; color: #991b1b; }
  @media (min-width: 760px) {
    .sales-new-mask {
      align-items: center;
      justify-content: center;
      padding: 18px;
    }
    .sales-new-modal {
      max-width: 560px;
      border-radius: 24px;
    }
  }
  @media (max-width: 520px) {
    .sales-new-grid { grid-template-columns: 1fr; }
    .sales-new-building-row { grid-template-columns: 1fr 1fr; }
    .sales-new-building-row .sales-new-choose-btn { grid-column: 1 / -1; }
  }
</style>

<div id="sales_new_mask" class="sales-new-mask" onclick="closeSalesNewModal(event)">
  <div class="sales-new-modal" onclick="event.stopPropagation()">
    <div class="sales-new-title">&#x65B0;&#x589E;&#x696D;&#x52D9;&#x6848;&#x4EF6;</div>
    <div class="sales-new-sub">&#x6848;&#x4EF6;&#x6703;&#x81EA;&#x52D5;&#x6B78;&#x5C6C;&#x76EE;&#x524D;&#x767B;&#x5165;&#x8CEC;&#x865F;&#x3002;</div>
    <div id="sales_new_msg" class="sales-new-msg"></div>

    <div class="sales-new-section">&#x5927;&#x6A13;&#x8CC7;&#x6599;</div>
    <div class="sales-new-building-row">
      <div>
        <label>&#x5340;&#x57DF;</label>
        <input id="sn_building_area" list="sn_area_options" placeholder="&#x53EF;&#x624B;&#x52D5;&#x8F38;&#x5165;">
        <datalist id="sn_area_options"></datalist>
      </div>
      <div>
        <label>&#x5927;&#x6A13;&#x540D;&#x7A31;</label>
        <input id="sn_building_name" list="sn_building_name_options" placeholder="&#x53EF;&#x624B;&#x52D5;&#x8F38;&#x5165;" required>
        <datalist id="sn_building_name_options"></datalist>
        <input id="sn_building_no" type="hidden">
      </div>
      <button type="button" class="sales-new-choose-btn" onclick="openSalesNewBuildingSheet()">&#x9078;&#x64C7;</button>
    </div>
    <div class="sales-new-hint">&#x9078;&#x540D;&#x518A;&#x5927;&#x6A13;&#x6703;&#x81EA;&#x52D5;&#x5E36;&#x5165;&#x5730;&#x5740;&#x8207;&#x806F;&#x7D61;&#x4EBA;&#xFF0C;&#x4E5F;&#x53EF;&#x5168;&#x90E8;&#x624B;&#x52D5;&#x8F38;&#x5165;&#x3002;</div>

    <div class="sales-new-grid" style="margin-top:10px">
      <div style="grid-column:1/-1">
        <label>&#x5730;&#x5740;</label>
        <input id="sn_building_address" placeholder="&#x53EF;&#x624B;&#x52D5;&#x8F38;&#x5165;">
      </div>
      <div>
        <label>&#x806F;&#x7D61;&#x4EBA;</label>
        <input id="sn_contact_name" placeholder="&#x53EF;&#x624B;&#x52D5;&#x8F38;&#x5165;">
      </div>
      <div>
        <label>&#x96FB;&#x8A71;</label>
        <input id="sn_contact_phone" inputmode="tel" placeholder="&#x53EF;&#x624B;&#x52D5;&#x8F38;&#x5165;">
      </div>
    </div>

    <div class="sales-new-section">&#x696D;&#x52D9;&#x8CC7;&#x6599;</div>
    <div class="sales-new-grid">
      <div>
        <label>&#x696D;&#x52D9;&#x985E;&#x578B;</label>
        <select id="sn_business_type">
          <option value="&#x65B0;&#x5927;&#x6A13;&#x958B;&#x767C;">&#x65B0;&#x5927;&#x6A13;&#x958B;&#x767C;</option>
          <option value="&#x820A;&#x5927;&#x6A13;&#x62DC;&#x8A2A;" selected>&#x820A;&#x5927;&#x6A13;&#x62DC;&#x8A2A;</option>
          <option value="&#x5408;&#x7D04;&#x7E8C;&#x7D04;">&#x5408;&#x7D04;&#x7E8C;&#x7D04;</option>
          <option value="&#x7BA1;&#x7406;&#x5BA4;&#x62DC;&#x8A2A;">&#x7BA1;&#x7406;&#x5BA4;&#x62DC;&#x8A2A;</option>
          <option value="&#x696D;&#x52D9;&#x4E8B;&#x4EF6;">&#x696D;&#x52D9;&#x4E8B;&#x4EF6;</option>
          <option value="&#x56DE;&#x994B;&#x8655;&#x7406;">&#x56DE;&#x994B;&#x8655;&#x7406;</option>
        </select>
      </div>
      <div>
        <label>&#x76EE;&#x524D;&#x72C0;&#x614B;</label>
        <select id="sn_status">
          <option value="&#x5F85;&#x62DC;&#x8A2F;" selected>&#x5F85;&#x62DC;&#x8A2F;</option>
          <option value="&#x5DF2;&#x63A5;&#x89F8;">&#x5DF2;&#x63A5;&#x89F8;</option>
          <option value="&#x5DF2;&#x62DC;&#x8A2F;">&#x5DF2;&#x62DC;&#x8A2F;</option>
          <option value="&#x7B49;&#x7BA1;&#x59D4;&#x6703;">&#x7B49;&#x7BA1;&#x59D4;&#x6703;</option>
          <option value="&#x8AC7;&#x7D04;&#x4E2D;">&#x8AC7;&#x7D04;&#x4E2D;</option>
          <option value="&#x5F85;&#x56DE;&#x8986;">&#x5F85;&#x56DE;&#x8986;</option>
          <option value="&#x8FFD;&#x8E64;&#x4E2D;">&#x8FFD;&#x8E64;&#x4E2D;</option>
        </select>
      </div>
      <div>
        <label>&#x5408;&#x7D04;&#x72C0;&#x614B;</label>
        <select id="sn_contract_status">
          <option value="&#x6D3D;&#x8AC7;&#x4E2D;" selected>&#x6D3D;&#x8AC7;&#x4E2D;</option>
          <option value="&#x5373;&#x5C07;&#x5230;&#x671F;">&#x5373;&#x5C07;&#x5230;&#x671F;</option>
          <option value="&#x5DF2;&#x7C3D;">&#x5DF2;&#x7C3D;</option>
          <option value="&#x7121;">&#x7121;</option>
        </select>
      </div>
      <div>
        <label>&#x56DE;&#x994B;&#x985E;&#x578B;</label>
        <select id="sn_feedback_type">
          <option value="&#x7121;" selected>&#x7121;</option>
          <option value="&#x50F9;&#x683C;&#x56DE;&#x994B;">&#x50F9;&#x683C;&#x56DE;&#x994B;</option>
          <option value="&#x670D;&#x52D9;&#x56DE;&#x994B;">&#x670D;&#x52D9;&#x56DE;&#x994B;</option>
          <option value="&#x516C;&#x8A2D;&#x9700;&#x6C42;">&#x516C;&#x8A2D;&#x9700;&#x6C42;</option>
        </select>
      </div>
      <div>
        <label>&#x4E8B;&#x4EF6;&#x985E;&#x578B;</label>
        <select id="sn_event_type">
          <option value="&#x7121;" selected>&#x7121;</option>
          <option value="&#x7BA1;&#x7406;&#x5BA4;&#x8981;&#x6C42;">&#x7BA1;&#x7406;&#x5BA4;&#x8981;&#x6C42;</option>
          <option value="&#x7BA1;&#x59D4;&#x6703;&#x8981;&#x6C42;">&#x7BA1;&#x59D4;&#x6703;&#x8981;&#x6C42;</option>
          <option value="&#x4F4F;&#x6236;&#x53CD;&#x61C9;">&#x4F4F;&#x6236;&#x53CD;&#x61C9;</option>
          <option value="&#x5408;&#x7D04;&#x554F;&#x984C;">&#x5408;&#x7D04;&#x554F;&#x984C;</option>
        </select>
      </div>
      <div>
        <label>&#x4E8B;&#x4EF6;&#x72C0;&#x614B;</label>
        <select id="sn_event_status">
          <option value="&#x7121;" selected>&#x7121;</option>
          <option value="&#x5F85;&#x8655;&#x7406;">&#x5F85;&#x8655;&#x7406;</option>
          <option value="&#x8655;&#x7406;&#x4E2D;">&#x8655;&#x7406;&#x4E2D;</option>
          <option value="&#x5DF2;&#x56DE;&#x8986;">&#x5DF2;&#x56DE;&#x8986;</option>
        </select>
      </div>
    </div>

    <div class="sales-new-section">&#x8FFD;&#x8E64;&#x8207;&#x5099;&#x8A3B;</div>
    <div class="sales-new-grid">
      <div>
        <label>&#x4E0B;&#x6B21;&#x62DC;&#x8A2A;&#x65E5;&#x671F;</label>
        <input id="sn_next_visit" type="date">
      </div>
      <div>
        <label>&#x4E8B;&#x4EF6;&#x65E5;&#x671F;</label>
        <input id="sn_event_schedule_date" type="date">
      </div>
      <div style="grid-column:1/-1">
        <div class="sales-new-check-row">
          <input id="sn_important_schedule" type="checkbox" value="1">
          <span>&#x91CD;&#x8981;&#x884C;&#x7A0B;&#xFF0C;&#x986F;&#x793A;&#x5728;&#x6700;&#x4E0A;&#x65B9;</span>
        </div>
      </div>
      <div style="grid-column:1/-1">
        <label>&#x5099;&#x8A3B;</label>
        <textarea id="sn_business_note" placeholder="&#x4F8B;&#xFF1A;&#x7BA1;&#x7406;&#x5BA4;&#x8981;&#x6C42;&#x91CD;&#x8AC7;&#x5408;&#x7D04;&#xFF0C;&#x9700;&#x5E36;&#x5408;&#x7D04;&#x8CC7;&#x6599;&#x8207;&#x56DE;&#x994B;&#x65B9;&#x6848;&#x3002;"></textarea>
      </div>
    </div>

    <div class="sales-new-actions">
      <button type="button" class="sales-new-cancel" onclick="hideSalesNewModal()">&#x53D6;&#x6D88;</button>
      <button type="button" class="sales-new-save" onclick="submitSalesNewCase()">&#x5132;&#x5B58;&#x65B0;&#x589E;</button>
    </div>
  </div>
</div>

<!-- 新增案件用：選擇大樓 sheet（複用派工的樣式） -->
<div id="sn_building_mask" class="sales-building-mask" onclick="if(event.target.id==='sn_building_mask') hideSalesNewBuildingSheet()">
  <div class="sales-building-sheet" onclick="event.stopPropagation()">
    <div class="sales-building-head">
      <div class="sales-building-title">&#x9078;&#x64C7;&#x5927;&#x6A13;</div>
      <div class="sales-building-sub">&#x53EF;&#x4F9D;&#x5340;&#x57DF;&#x8207;&#x95DC;&#x9375;&#x5B57;&#x67E5;&#x8A62;&#x3002;</div>
      <div class="sales-building-filters">
        <select id="sn_area_filter" onchange="renderSnBuildingCards()">
          <option value="">&#x5168;&#x90E8;&#x5340;&#x57DF;</option>
        </select>
        <input id="sn_keyword" placeholder="&#x641C;&#x5C0B;&#x5927;&#x6A13;&#x540D;&#x7A31;&#xFF0F;&#x5730;&#x5740;" oninput="renderSnBuildingCards()">
      </div>
      <button class="sales-building-close" type="button" onclick="hideSalesNewBuildingSheet()">&#x95DC;&#x9589;</button>
    </div>
    <div id="sn_building_card_list"></div>
  </div>
</div>

<script id="sales_new_modal_js_v1">
(function () {
  let snBuildings = [];

  function snEsc(v) {
    return String(v ?? "")
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function snGetVal(id) {
    const el = document.getElementById(id);
    return el ? String(el.value || "").trim() : "";
  }

  function snSetVal(id, v) {
    const el = document.getElementById(id);
    if (el) el.value = v;
  }

  function showSnMsg(type, text) {
    const box = document.getElementById("sales_new_msg");
    if (!box) return;
    box.className = "sales-new-msg " + type;
    box.textContent = text;
    setTimeout(function () { box.className = "sales-new-msg"; }, 3500);
  }

  function resetSnForm() {
    ["sn_building_no","sn_building_area","sn_building_name","sn_building_address",
     "sn_contact_name","sn_contact_phone","sn_next_visit","sn_event_schedule_date","sn_business_note"]
      .forEach(function (id) { snSetVal(id, ""); });
    ["sn_business_type","sn_status","sn_contract_status","sn_feedback_type","sn_event_type","sn_event_status"]
      .forEach(function (id) {
        const el = document.getElementById(id);
        if (el && el.options.length) el.selectedIndex = 0;
      });
    const chk = document.getElementById("sn_important_schedule");
    if (chk) chk.checked = false;
    const msg = document.getElementById("sales_new_msg");
    if (msg) msg.className = "sales-new-msg";
  }

  function openSalesNewModal() {
    const mask = document.getElementById("sales_new_mask");
    if (!mask) return;
    resetSnForm();
    mask.classList.add("show");
    if (!snBuildings.length) loadSnBuildings();
    else { populateSnAreaOptions(); populateSnBuildingNameOptions(); }
  }

  function hideSalesNewModal() {
    const mask = document.getElementById("sales_new_mask");
    if (mask) mask.classList.remove("show");
  }

  function closeSalesNewModal(event) {
    if (event && event.target && event.target.id === "sales_new_mask") hideSalesNewModal();
  }

  async function loadSnBuildings() {
    try {
      const res = await fetch("/api/app/sales/dispatch/buildings?ts=" + Date.now(), {
        cache: "no-store", credentials: "same-origin"
      });
      const data = await res.json().catch(function () { return {}; });
      snBuildings = Array.isArray(data.items) ? data.items : [];
      populateSnAreaOptions();
      populateSnBuildingNameOptions();
    } catch (e) { snBuildings = []; }
  }

  function populateSnAreaOptions() {
    const dl = document.getElementById("sn_area_options");
    const filter = document.getElementById("sn_area_filter");
    if (!dl) return;
    const areas = [...new Set(snBuildings.map(function (b) { return (b.area || "").trim(); }).filter(Boolean))].sort();
    dl.innerHTML = areas.map(function (a) { return '<option value="' + snEsc(a) + '">'; }).join("");
    if (filter) {
      const cur = filter.value;
      filter.innerHTML = '<option value="">&#x5168;&#x90E8;&#x5340;&#x57DF;</option>' +
        areas.map(function (a) { return '<option value="' + snEsc(a) + '">' + snEsc(a) + '</option>'; }).join("");
      if (cur) filter.value = cur;
    }
  }

  function populateSnBuildingNameOptions() {
    const dl = document.getElementById("sn_building_name_options");
    if (!dl) return;
    dl.innerHTML = snBuildings.map(function (b) {
      return '<option value="' + snEsc(b.name || "") + '">';
    }).join("");
  }

  function findSnBuilding(no) {
    return snBuildings.find(function (b) { return b.building_no === no; }) || null;
  }

  function findSnBuildingByName(name) {
    const n = (name || "").trim();
    return snBuildings.find(function (b) { return (b.name || "").trim() === n; }) || null;
  }

  function useSnBuilding(no) {
    const b = findSnBuilding(no);
    if (!b) return;
    snSetVal("sn_building_no", b.building_no || "");
    snSetVal("sn_building_area", b.area || "");
    snSetVal("sn_building_name", b.name || "");
    snSetVal("sn_building_address", b.address || "");
    snSetVal("sn_contact_name", b.manager_name || "");
    snSetVal("sn_contact_phone", b.phone || "");
    hideSalesNewBuildingSheet();
  }

  function renderSnBuildingCards() {
    const list = document.getElementById("sn_building_card_list");
    if (!list) return;
    const area = snGetVal("sn_area_filter");
    const key = snGetVal("sn_keyword").toLowerCase();
    const items = snBuildings.filter(function (b) {
      const areaOk = !area || (b.area || "") === area;
      const hay = [b.name, b.address, b.area, b.manager_name, b.phone].join(" ").toLowerCase();
      return areaOk && (!key || hay.includes(key));
    });
    if (!items.length) {
      list.innerHTML = '<div class="sales-building-empty">&#x627E;&#x4E0D;&#x5230;&#x7B26;&#x5408;&#x689D;&#x4EF6;&#x7684;&#x5927;&#x6A13;&#x3002;</div>';
      return;
    }
    list.innerHTML = items.slice(0, 120).map(function (b) {
      const meta = [
        b.area ? "&#x5340;&#x57DF;&#xFF1A;" + snEsc(b.area) : "",
        b.address ? "&#x5730;&#x5740;&#xFF1A;" + snEsc(b.address) : "",
        b.manager_name ? "&#x806F;&#x7D61;&#x4EBA;&#xFF1A;" + snEsc(b.manager_name) : "",
        b.phone ? "&#x96FB;&#x8A71;&#xFF1A;" + snEsc(b.phone) : ""
      ].filter(Boolean).join("<br>");
      return '<div class="sales-building-card">' +
        '<div class="sales-building-card-title">' + snEsc(b.name || "") + '</div>' +
        '<div class="sales-building-card-meta">' + meta + '</div>' +
        '<div class="sales-building-card-actions">' +
          '<button class="sales-building-use" type="button" data-sn-no="' + snEsc(b.building_no || "") + '" onclick="window.snUseBuildingNo(this.getAttribute(&quot;data-sn-no&quot;))">' +
            '&#x5E36;&#x5165;</button>' +
          '<button class="sales-building-close" type="button" onclick="hideSalesNewBuildingSheet()">&#x95DC;&#x9589;</button>' +
        '</div>' +
      '</div>';
    }).join("");
  }

  function openSalesNewBuildingSheet() {
    const mask = document.getElementById("sn_building_mask");
    if (!mask) return;
    mask.classList.add("show");
    if (!snBuildings.length) {
      loadSnBuildings().then(renderSnBuildingCards);
    } else {
      populateSnAreaOptions();
      renderSnBuildingCards();
    }
  }

  function hideSalesNewBuildingSheet() {
    const mask = document.getElementById("sn_building_mask");
    if (mask) mask.classList.remove("show");
  }

  document.addEventListener("click", function (event) {
    // 保留相容舊 data-sn-no 屬性（若有）
    const btn = event.target && event.target.closest ? event.target.closest("[data-sn-no]") : null;
    if (btn && btn.dataset.snNo) useSnBuilding(btn.dataset.snNo);
  });

  const snNameInput = document.getElementById("sn_building_name");
  if (snNameInput) {
    snNameInput.addEventListener("change", function () {
      const b = findSnBuildingByName(this.value);
      if (b) useSnBuilding(b.building_no || "");
    });
  }

  async function submitSalesNewCase() {
    const buildingName = snGetVal("sn_building_name");
    if (!buildingName) {
      showSnMsg("err", "&#x8ACB;&#x8F38;&#x5165;&#x6216;&#x9078;&#x64C7;&#x5927;&#x6A13;&#x540D;&#x7A31;");
      return;
    }

    const params = new URLSearchParams({
      building_no: snGetVal("sn_building_no"),
      building_name: buildingName,
      building_area: snGetVal("sn_building_area"),
      building_address: snGetVal("sn_building_address"),
      contact_name: snGetVal("sn_contact_name"),
      contact_phone: snGetVal("sn_contact_phone"),
      business_type: snGetVal("sn_business_type"),
      status: snGetVal("sn_status"),
      contract_status: snGetVal("sn_contract_status"),
      feedback_type: snGetVal("sn_feedback_type"),
      event_type: snGetVal("sn_event_type"),
      event_status: snGetVal("sn_event_status"),
      next_visit: snGetVal("sn_next_visit"),
      event_schedule_date: snGetVal("sn_event_schedule_date"),
      important_schedule: document.getElementById("sn_important_schedule") && document.getElementById("sn_important_schedule").checked ? "1" : "0",
      business_note: snGetVal("sn_business_note")
    });

    const saveBtn = document.querySelector(".sales-new-save");
    if (saveBtn) { saveBtn.disabled = true; saveBtn.textContent = "&#x5132;&#x5B58;&#x4E2D;..."; }

    try {
      const res = await fetch("/api/app/sales/business-records/create", {
        method: "POST",
        credentials: "same-origin",
        body: params
      });
      const data = await res.json().catch(function () { return {}; });
      if (!res.ok || !data.ok) {
        showSnMsg("err", data.error || "&#x5EFA;&#x7ACB;&#x5931;&#x6557;");
        return;
      }
      showSnMsg("ok", "&#x6848;&#x4EF6;&#x5DF2;&#x65B0;&#x589E;");
      setTimeout(function () {
        hideSalesNewModal();
        if (typeof reloadData === "function") reloadData();
      }, 700);
    } catch (e) {
      showSnMsg("err", "&#x7DB2;&#x8DEF;&#x932F;&#x8AA4;&#xFF0C;&#x8ACB;&#x91CD;&#x8A66;");
    } finally {
      if (saveBtn) { saveBtn.disabled = false; saveBtn.textContent = "&#x5132;&#x5B58;&#x65B0;&#x589E;"; }
    }
  }

  window.openSalesNewModal = openSalesNewModal;
  window.hideSalesNewModal = hideSalesNewModal;
  window.closeSalesNewModal = closeSalesNewModal;
  window.submitSalesNewCase = submitSalesNewCase;
  window.openSalesNewBuildingSheet = openSalesNewBuildingSheet;
  window.hideSalesNewBuildingSheet = hideSalesNewBuildingSheet;
  window.renderSnBuildingCards = renderSnBuildingCards;
  window.snUseBuildingNo = useSnBuilding;

  // 偵測 #open-new hash（從 /app/sales/new 跳轉過來），自動開啟新增 sheet
  if (location.hash === "#open-new") {
    history.replaceState(null, "", "/app/sales");
    openSalesNewModal();
  }
})();
</script>

</body>
</html>
"""
# SHINNAN_SALES_MOBILE_APP_END



# SHINNAN_EMPLOYEE_CURRENT_USER_HELPER_START

@router.get("/api/app/sales/business-records", summary="手機 APP 讀取個人業務工作資料")
def api_app_sales_business_records(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    rows = _sales_business_records_for_app(user)

    return _ManagersResponse(
        content=_managers_json.dumps({
            "ok": True,
            "items": rows,
            "count": len(rows),
            "scope": "all" if _sales_is_admin_scope(user) else "self",
        }, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )



# CL15N8_SALES_COMPLETE_CASE_API_START
def _sales_complete_now_text() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _sales_complete_columns(conn, table_name: str) -> set:
    rows = conn.execute(_sales_sql_text("PRAGMA table_info(" + table_name + ")")).mappings().fetchall()
    return {str(r["name"]) for r in rows}


@router.post("/api/app/sales/business-records/{record_id}/complete")
def api_app_sales_business_record_complete(record_id: int, request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _sales_business_records_init()

    now_text = _sales_complete_now_text()
    staff_name = str(user.get("display_name") or user.get("staff_code") or "").strip()
    role = str(user.get("role") or "").strip()

    with _sales_engine.begin() as conn:
        cols = _sales_complete_columns(conn, "sales_business_records")

        if "completed_at" not in cols:
            conn.execute(_sales_sql_text("ALTER TABLE sales_business_records ADD COLUMN completed_at TEXT DEFAULT ''"))
        if "completed_by" not in cols:
            conn.execute(_sales_sql_text("ALTER TABLE sales_business_records ADD COLUMN completed_by TEXT DEFAULT ''"))

        cols = _sales_complete_columns(conn, "sales_business_records")

        row = conn.execute(
            _sales_sql_text("""
                SELECT id, owner, status
                FROM sales_business_records
                WHERE id = :id
                LIMIT 1
            """),
            {"id": record_id},
        ).mappings().first()

        if not row:
            return _ManagersResponse(
                content=_managers_json.dumps({"ok": False, "error": "record not found"}, ensure_ascii=False),
                media_type="application/json; charset=utf-8",
                status_code=404,
            )

        display_name = str(user.get("display_name") or "").strip()
        is_admin_scope = _sales_is_admin_scope(user)

        if not is_admin_scope:
            owner_name = display_name
            if str(row.get("owner") or "").strip() != owner_name:
                return _ManagersResponse(
                    content=_managers_json.dumps({"ok": False, "error": "permission denied"}, ensure_ascii=False),
                    media_type="application/json; charset=utf-8",
                    status_code=403,
                )

        sets = []
        params = {
            "id": record_id,
            "status": "\u5df2\u5b8c\u6210",
            "completed_at": now_text,
            "completed_by": staff_name,
        }

        if "status" in cols:
            sets.append("status = :status")
        if "completed_at" in cols:
            sets.append("completed_at = :completed_at")
        if "completed_by" in cols:
            sets.append("completed_by = :completed_by")

        if not sets:
            return _ManagersResponse(
                content=_managers_json.dumps({"ok": False, "error": "no editable columns"}, ensure_ascii=False),
                media_type="application/json; charset=utf-8",
                status_code=500,
            )

        conn.execute(
            _sales_sql_text("UPDATE sales_business_records SET " + ", ".join(sets) + " WHERE id = :id"),
            params,
        )

    return _ManagersResponse(
        content=_managers_json.dumps({
            "ok": True,
            "id": record_id,
            "status": "\u5df2\u5b8c\u6210",
        }, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


# CL15N8_SALES_COMPLETE_CASE_API_END


# SHINNAN_SALES_MOBILE_NEW_CASE_START
# /app/sales/new 整合為主頁 bottom sheet，此路由載入後自動跳轉並開啟 sheet
@router.get("/app/sales/new", response_class=HTMLResponse)
def sales_mobile_new_case_page(request: _EmpRequest):
    user = _employee_current_user_from_request(request)
    if not user:
        return _EmpRedirectResponse("/employee/login?next=/app/sales", status_code=303)
    # 回傳一個極輕量頁面，立即 redirect 到主頁並帶 hash，主頁偵測後自動開啟 sheet
    return HTMLResponse("""<!doctype html><html><head><meta charset="utf-8">
<script>location.replace("/app/sales#open-new");</script>
</head><body></body></html>""")
# SHINNAN_SALES_MOBILE_NEW_CASE_END


# SHINNAN_EMPLOYEE_LOGIN_ROUTES_END
