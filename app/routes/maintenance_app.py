
from __future__ import annotations

import json
from datetime import datetime
from html import escape

from fastapi import APIRouter
from fastapi import Body
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from sqlalchemy import text as _sql_text

from app.db import engine
from app.routes.employee_auth import _employee_current_user_from_request


router = APIRouter(tags=["maintenance app"])


def _m_now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _m_json(data, status_code: int = 200):
    return JSONResponse(content=data, status_code=status_code)


def _m_text(value) -> str:
    return str(value or "").strip()


def _m_table_exists(conn, table_name: str) -> bool:
    return int(conn.execute(
        _sql_text("""
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
              AND name = :name
        """),
        {"name": table_name},
    ).scalar() or 0) > 0


def _m_columns(conn, table_name: str) -> set[str]:
    if not _m_table_exists(conn, table_name):
        return set()

    rows = conn.execute(_sql_text("PRAGMA table_info(" + table_name + ")")).mappings().fetchall()
    return {str(r["name"]) for r in rows}


def _m_ensure_columns(conn):
    cols = _m_columns(conn, "tickets")

    wanted = {
        "maintenance_status": "TEXT",
        "maintenance_note": "TEXT",
        "maintenance_result": "TEXT",
        "maintenance_updated_at": "TEXT",
    }

    for col, col_type in wanted.items():
        if col not in cols:
            conn.execute(_sql_text("ALTER TABLE tickets ADD COLUMN " + col + " " + col_type))


def _m_proxy_user(request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return None

    return {
        "staff_code": _m_text(user.get("staff_code") or user.get("username")),
        "display_name": _m_text(user.get("display_name") or user.get("staff_code") or user.get("username")),
        "department": _m_text(user.get("department")),
        "role": _m_text(user.get("role")),
    }


def _m_can_open(user: dict) -> bool:
    if not user:
        return False

    if user.get("staff_code") == "admin" or user.get("role") == "admin":
        return True

    department = _m_text(user.get("department"))
    if department == "\u7dad\u4fee\u90e8":
        return True

    try:
        with engine.begin() as conn:
            if not _m_table_exists(conn, "employee_profiles"):
                return False

            row = conn.execute(
                _sql_text("""
                    SELECT app_access
                    FROM employee_profiles
                    WHERE staff_code = :staff_code
                    LIMIT 1
                """),
                {"staff_code": user.get("staff_code") or ""},
            ).mappings().first()

            raw = _m_text(row.get("app_access")) if row else ""
            return "maintenance" in raw or "\u7dad\u4fee" in raw
    except Exception:
        return False




def _m_get_departments(conn):
    departments = []

    if _m_table_exists(conn, "employee_profiles"):
        rows = conn.execute(
            _sql_text("""
                SELECT DISTINCT COALESCE(department, '') AS department
                FROM employee_profiles
                WHERE COALESCE(department, '') <> ''
                ORDER BY department
            """)
        ).mappings().fetchall()

        departments = [
            _m_text(r.get("department"))
            for r in rows
            if _m_text(r.get("department"))
        ]

    fallback = [
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

    for item in fallback:
        if item not in departments:
            departments.append(item)

    return departments


def _m_row_to_item(row):
    ticket_id = int(row.get("id") or 0)
    status = _m_text(row.get("status"))
    transfer_source = _m_text(row.get("transfer_source_department"))

    tags = []
    if transfer_source:
        tags.append("\u4f86\u6e90\uff1a" + transfer_source)
    if _m_text(row.get("transfer_status")):
        tags.append(_m_text(row.get("transfer_status")))

    return {
        "id": ticket_id,
        "ticket_no": _m_text(row.get("ticket_no")) or ("T" + str(ticket_id)),
        "case_type": _m_text(row.get("case_type")),
        "status": status,
        "customer_name": _m_text(row.get("customer_name")),
        "contact_name": _m_text(row.get("contact_name")),
        "contact_phone": _m_text(row.get("contact_phone")),
        "service_address": _m_text(row.get("service_address")),
        "appointment_date": _m_text(row.get("appointment_date")),
        "appointment_time": _m_text(row.get("appointment_time")),
        "assigned_engineer": _m_text(row.get("assigned_engineer")),
        "description": _m_text(row.get("description")),
        "repair_reason": _m_text(row.get("repair_reason")),
        "completion_note": _m_text(row.get("completion_note")),
        "transfer_origin_ticket_id": int(row.get("transfer_origin_ticket_id") or 0),
        "transfer_source_department": transfer_source,
        "transfer_status": _m_text(row.get("transfer_status")),
        "transfer_note": _m_text(row.get("transfer_note")),
        "maintenance_status": _m_text(row.get("maintenance_status")),
        "maintenance_note": _m_text(row.get("maintenance_note")),
        "maintenance_result": _m_text(row.get("maintenance_result")),
        "tags": tags,
    }


@router.get("/api/app/maintenance/tickets")
def api_maintenance_tickets(request: Request):
    user = _m_proxy_user(request)
    if not user:
        return _m_json({"ok": False, "error": "login required"}, 401)

    if not _m_can_open(user):
        return _m_json({"ok": False, "error": "permission denied"}, 403)

    dept = "\u7dad\u4fee\u90e8"

    with engine.begin() as conn:
        _m_ensure_columns(conn)
        if not _m_table_exists(conn, "tickets"):
            return _m_json({"ok": True, "items": []})

        rows = conn.execute(
            _sql_text("""
                SELECT *
                FROM tickets
                WHERE (
                    COALESCE(dispatch_area, '') = :dept
                    OR COALESCE(transfer_target_department, '') = :dept
                    OR COALESCE(maintenance_status, '') <> ''
                    OR COALESCE(is_non_general_repair, 0) = 1
                )
                  AND COALESCE(status, '') NOT IN (
                    '\u5df2\u53d6\u6d88',
                    '\u4f4f\u6236\u53d6\u6d88',
                    '\u9000\u56de'
                  )
                ORDER BY
                    CASE
                      WHEN COALESCE(status, '') = '\u672a\u9818\u53d6' THEN 0
                      WHEN COALESCE(status, '') = '\u5df2\u9818\u53d6' THEN 1
                      WHEN COALESCE(status, '') = '\u8655\u7406\u4e2d' THEN 2
                      ELSE 3
                    END,
                    id DESC
                LIMIT 120
            """),
            {"dept": dept},
        ).mappings().fetchall()

    return _m_json({"ok": True, "items": [_m_row_to_item(r) for r in rows]})


@router.post("/api/app/maintenance/tickets/{ticket_id}/claim")
def api_maintenance_claim(ticket_id: int, request: Request):
    user = _m_proxy_user(request)
    if not user:
        return _m_json({"ok": False, "error": "login required"}, 401)

    if not _m_can_open(user):
        return _m_json({"ok": False, "error": "permission denied"}, 403)

    now_text = _m_now_text()

    with engine.begin() as conn:
        _m_ensure_columns(conn)
        cols = _m_columns(conn, "tickets")

        row = conn.execute(
            _sql_text("SELECT * FROM tickets WHERE id = :id LIMIT 1"),
            {"id": ticket_id},
        ).mappings().first()

        if not row:
            return _m_json({"ok": False, "error": "ticket not found"}, 404)

        sets = []
        params = {
            "id": ticket_id,
            "status": "\u5df2\u9818\u53d6",
            "assigned_engineer": user.get("display_name") or "",
            "assigned_engineer_staff_code": user.get("staff_code") or "",
            "maintenance_status": "\u7dad\u4fee\u90e8\u5df2\u9818\u53d6",
            "maintenance_updated_at": now_text,
            "arrived_at": now_text,
        }

        if "status" in cols:
            sets.append("status = :status")
        if "assigned_engineer" in cols:
            sets.append("assigned_engineer = :assigned_engineer")
        if "assigned_engineer_staff_code" in cols:
            sets.append("assigned_engineer_staff_code = :assigned_engineer_staff_code")
        if "maintenance_status" in cols:
            sets.append("maintenance_status = :maintenance_status")
        if "maintenance_updated_at" in cols:
            sets.append("maintenance_updated_at = :maintenance_updated_at")
        if "arrived_at" in cols:
            sets.append("arrived_at = COALESCE(arrived_at, :arrived_at)")

        conn.execute(_sql_text("UPDATE tickets SET " + ", ".join(sets) + " WHERE id = :id"), params)

    return _m_json({"ok": True})


@router.post("/api/app/maintenance/tickets/{ticket_id}/return")
def api_maintenance_return(ticket_id: int, request: Request, payload: dict = Body(default_factory=dict)):
    user = _m_proxy_user(request)
    if not user:
        return _m_json({"ok": False, "error": "login required"}, 401)

    if not _m_can_open(user):
        return _m_json({"ok": False, "error": "permission denied"}, 403)

    reason = _m_text(payload.get("reason"))
    now_text = _m_now_text()

    with engine.begin() as conn:
        _m_ensure_columns(conn)
        cols = _m_columns(conn, "tickets")

        row = conn.execute(
            _sql_text("SELECT * FROM tickets WHERE id = :id LIMIT 1"),
            {"id": ticket_id},
        ).mappings().first()

        if not row:
            return _m_json({"ok": False, "error": "ticket not found"}, 404)

        source_area = _m_text(row.get("transfer_source_department"))
        if not source_area:
            source_area = "\u539f\u5340"

        clone = {}
        for col in cols:
            if col == "id":
                continue
            clone[col] = row.get(col)

        if "ticket_no" in cols:
            clone["ticket_no"] = _m_text(row.get("ticket_no")) + "-RT" + str(ticket_id)
        if "dispatch_area" in cols:
            clone["dispatch_area"] = source_area
        if "status" in cols:
            clone["status"] = "\u672a\u9818\u53d6"
        if "assigned_engineer" in cols:
            clone["assigned_engineer"] = ""
        if "assigned_engineer_staff_code" in cols:
            clone["assigned_engineer_staff_code"] = ""
        if "created_at" in cols:
            clone["created_at"] = now_text
        if "arrived_at" in cols:
            clone["arrived_at"] = None
        if "completed_at" in cols:
            clone["completed_at"] = None
        if "finished_at" in cols:
            clone["finished_at"] = None
        if "finished_by_staff_code" in cols:
            clone["finished_by_staff_code"] = ""
        if "finished_by_name" in cols:
            clone["finished_by_name"] = ""
        if "transfer_origin_ticket_id" in cols:
            clone["transfer_origin_ticket_id"] = ticket_id
        if "transfer_child_ticket_id" in cols:
            clone["transfer_child_ticket_id"] = 0
        if "transfer_target_department" in cols:
            clone["transfer_target_department"] = source_area
        if "transfer_source_department" in cols:
            clone["transfer_source_department"] = "\u7dad\u4fee\u90e8"
        if "transfer_status" in cols:
            clone["transfer_status"] = "\u7dad\u4fee\u90e8\u9000\u56de"
        if "transfer_note" in cols:
            clone["transfer_note"] = reason
        if "transfer_created_at" in cols:
            clone["transfer_created_at"] = now_text
        if "transfer_updated_at" in cols:
            clone["transfer_updated_at"] = now_text
        if "maintenance_status" in cols:
            clone["maintenance_status"] = ""
        if "maintenance_note" in cols:
            clone["maintenance_note"] = reason
        if "maintenance_result" in cols:
            clone["maintenance_result"] = ""
        if "maintenance_updated_at" in cols:
            clone["maintenance_updated_at"] = now_text

        insert_cols = [c for c in clone.keys() if c in cols and c != "id"]
        insert_sql = "INSERT INTO tickets (" + ", ".join(insert_cols) + ") VALUES (" + ", ".join([":" + c for c in insert_cols]) + ")"
        result = conn.execute(_sql_text(insert_sql), {c: clone[c] for c in insert_cols})
        return_id = int(result.lastrowid)

        sets = []
        params = {
            "id": ticket_id,
            "status": "\u9000\u56de",
            "maintenance_status": "\u7dad\u4fee\u90e8\u9000\u56de",
            "maintenance_note": reason,
            "maintenance_updated_at": now_text,
            "transfer_child_ticket_id": return_id,
            "transfer_status": "\u5df2\u9000\u56de\u539f\u5340",
            "transfer_updated_at": now_text,
        }

        if "status" in cols:
            sets.append("status = :status")
        if "maintenance_status" in cols:
            sets.append("maintenance_status = :maintenance_status")
        if "maintenance_note" in cols:
            sets.append("maintenance_note = :maintenance_note")
        if "maintenance_updated_at" in cols:
            sets.append("maintenance_updated_at = :maintenance_updated_at")
        if "transfer_child_ticket_id" in cols:
            sets.append("transfer_child_ticket_id = :transfer_child_ticket_id")
        if "transfer_status" in cols:
            sets.append("transfer_status = :transfer_status")
        if "transfer_updated_at" in cols:
            sets.append("transfer_updated_at = :transfer_updated_at")

        conn.execute(_sql_text("UPDATE tickets SET " + ", ".join(sets) + " WHERE id = :id"), params)

    return _m_json({"ok": True, "return_ticket_id": return_id, "return_area": source_area})




@router.post("/api/app/maintenance/tickets/{ticket_id}/complete")
def api_maintenance_complete(ticket_id: int, request: Request, payload: dict = Body(default_factory=dict)):
    user = _m_proxy_user(request)
    if not user:
        return _m_json({"ok": False, "error": "login required"}, 401)

    if not _m_can_open(user):
        return _m_json({"ok": False, "error": "permission denied"}, 403)

    repair_reason = _m_text(payload.get("repair_reason"))
    result_note = _m_text(payload.get("result_note"))
    speedtest_photo_data = _m_text(payload.get("speedtest_photo_data"))

    if not repair_reason:
        return _m_json({"ok": False, "error": "\u8acb\u586b\u5beb\u7dad\u4fee\u539f\u56e0"}, 400)

    if not speedtest_photo_data:
        return _m_json({"ok": False, "error": "\u8acb\u4e0a\u50b3\u6e2c\u901f\u7167\u7247"}, 400)

    now_text = _m_now_text()

    with engine.begin() as conn:
        _m_ensure_columns(conn)
        cols = _m_columns(conn, "tickets")

        row = conn.execute(
            _sql_text("SELECT * FROM tickets WHERE id = :id LIMIT 1"),
            {"id": ticket_id},
        ).mappings().first()

        if not row:
            return _m_json({"ok": False, "error": "ticket not found"}, 404)

        origin_id = int(row.get("transfer_origin_ticket_id") or 0)

        sets = []
        params = {
            "id": ticket_id,
            "status": "\u5df2\u5b8c\u5de5",
            "repair_reason": repair_reason,
            "completion_note": result_note,
            "speedtest_photo_data": speedtest_photo_data,
            "finished_by_staff_code": user.get("staff_code") or "",
            "finished_by_name": user.get("display_name") or "",
            "completed_at": now_text,
            "finished_at": now_text,
            "maintenance_status": "\u7dad\u4fee\u90e8\u5df2\u5b8c\u5de5",
            "maintenance_result": result_note,
            "maintenance_updated_at": now_text,
        }

        for col in [
            "status",
            "repair_reason",
            "completion_note",
            "speedtest_photo_data",
            "finished_by_staff_code",
            "finished_by_name",
            "completed_at",
            "finished_at",
            "maintenance_status",
            "maintenance_result",
            "maintenance_updated_at",
        ]:
            if col in cols:
                sets.append(col + " = :" + col)

        conn.execute(_sql_text("UPDATE tickets SET " + ", ".join(sets) + " WHERE id = :id"), params)

        if origin_id > 0:
            origin_sets = []
            origin_params = {
                "origin_id": origin_id,
                "status": "\u5df2\u5b8c\u5de5",
                "transfer_status": "\u7dad\u4fee\u90e8\u5df2\u5b8c\u5de5",
                "transfer_updated_at": now_text,
                "completed_at": now_text,
                "finished_at": now_text,
            }

            for col in ["status", "transfer_status", "transfer_updated_at", "completed_at", "finished_at"]:
                if col in cols:
                    origin_sets.append(col + " = :" + col)

            if origin_sets:
                conn.execute(_sql_text("UPDATE tickets SET " + ", ".join(origin_sets) + " WHERE id = :origin_id"), origin_params)

    return _m_json({"ok": True})



# CL15M3_MAINTENANCE_TRANSFER_APIS_START
@router.get("/api/app/maintenance/departments")
def api_maintenance_departments(request: Request):
    user = _m_proxy_user(request)
    if not user:
        return _m_json({"ok": False, "error": "login required"}, 401)

    if not _m_can_open(user):
        return _m_json({"ok": False, "error": "permission denied"}, 403)

    with engine.begin() as conn:
        items = _m_get_departments(conn)

    items = [x for x in items if x and x != "\u7dad\u4fee\u90e8"]

    return _m_json({"ok": True, "items": items})


@router.post("/api/app/maintenance/tickets/{ticket_id}/transfer")
def api_maintenance_transfer(ticket_id: int, request: Request, payload: dict = Body(default_factory=dict)):
    user = _m_proxy_user(request)
    if not user:
        return _m_json({"ok": False, "error": "login required"}, 401)

    if not _m_can_open(user):
        return _m_json({"ok": False, "error": "permission denied"}, 403)

    target_department = _m_text(payload.get("target_department"))
    note = _m_text(payload.get("note"))

    if not target_department:
        return _m_json({"ok": False, "error": "target department required"}, 400)

    if target_department == "\u7dad\u4fee\u90e8":
        return _m_json({"ok": False, "error": "target department invalid"}, 400)

    now_text = _m_now_text()

    with engine.begin() as conn:
        _m_ensure_columns(conn)
        cols = _m_columns(conn, "tickets")

        allowed = _m_get_departments(conn)
        if target_department not in allowed:
            return _m_json({"ok": False, "error": "target department not allowed"}, 400)

        row = conn.execute(
            _sql_text("SELECT * FROM tickets WHERE id = :id LIMIT 1"),
            {"id": ticket_id},
        ).mappings().first()

        if not row:
            return _m_json({"ok": False, "error": "ticket not found"}, 404)

        source_department = _m_text(row.get("dispatch_area")) or "\u7dad\u4fee\u90e8"

        sets = []
        params = {
            "id": ticket_id,
            "target_department": target_department,
            "source_department": source_department,
            "status": "\u672a\u9818\u53d6",
            "empty": "",
            "transfer_status": "\u7dad\u4fee\u90e8\u8f49\u6d3e\u4e2d",
            "transfer_note": note,
            "now_text": now_text,
            "maintenance_status": "",
            "maintenance_note": note,
        }

        if "dispatch_area" in cols:
            sets.append("dispatch_area = :target_department")
        if "status" in cols:
            sets.append("status = :status")
        if "assigned_engineer" in cols:
            sets.append("assigned_engineer = :empty")
        if "assigned_engineer_staff_code" in cols:
            sets.append("assigned_engineer_staff_code = :empty")
        if "arrived_at" in cols:
            sets.append("arrived_at = NULL")
        if "completed_at" in cols:
            sets.append("completed_at = NULL")
        if "finished_at" in cols:
            sets.append("finished_at = NULL")
        if "finished_by_staff_code" in cols:
            sets.append("finished_by_staff_code = :empty")
        if "finished_by_name" in cols:
            sets.append("finished_by_name = :empty")
        if "transfer_target_department" in cols:
            sets.append("transfer_target_department = :target_department")
        if "transfer_source_department" in cols:
            sets.append("transfer_source_department = :source_department")
        if "transfer_status" in cols:
            sets.append("transfer_status = :transfer_status")
        if "transfer_note" in cols:
            sets.append("transfer_note = CASE WHEN COALESCE(transfer_note, '') = '' THEN :transfer_note ELSE transfer_note || char(10) || :transfer_note END")
        if "transfer_updated_at" in cols:
            sets.append("transfer_updated_at = :now_text")
        if "maintenance_status" in cols:
            sets.append("maintenance_status = :maintenance_status")
        if "maintenance_note" in cols:
            sets.append("maintenance_note = CASE WHEN COALESCE(maintenance_note, '') = '' THEN :maintenance_note ELSE maintenance_note || char(10) || :maintenance_note END")
        if "maintenance_updated_at" in cols:
            sets.append("maintenance_updated_at = :now_text")

        if not sets:
            return _m_json({"ok": False, "error": "no editable columns"}, 500)

        conn.execute(
            _sql_text("UPDATE tickets SET " + ", ".join(sets) + " WHERE id = :id"),
            params,
        )

    return _m_json({
        "ok": True,
        "id": ticket_id,
        "target_department": target_department,
        "status": "\u672a\u9818\u53d6",
    })


# CL15M3_MAINTENANCE_TRANSFER_APIS_END


@router.get("/app/maintenance", response_class=HTMLResponse)
def maintenance_app_page(request: Request):
    user = _m_proxy_user(request)

    if not user:
        return RedirectResponse("/employee/login?next=/app/maintenance", status_code=303)

    if not _m_can_open(user):
        return HTMLResponse(
            "<!doctype html><meta charset='utf-8'><body style='font-family:Arial;padding:24px'>permission denied</body>",
            status_code=403,
        )

    user_line = escape(user.get("display_name") or user.get("staff_code") or "")

    return """
<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>\u7dad\u4fee\u90e8\u7cfb\u7d71</title>
<link rel="stylesheet" href="/static/app_header_unified.css?v=20260515_m1">
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;background:#eef3f9;color:#102348;font-family:"Noto Sans TC","Microsoft JhengHei",Arial,sans-serif;padding-bottom:30px}
.app-shell{max-width:560px;margin:0 auto;min-height:100vh;background:#eef3f9}
.content{padding:14px 14px 28px}
.card{background:#fff;border:1px solid #d7e1ef;border-radius:20px;padding:14px;box-shadow:0 8px 22px rgba(15,23,42,.06);margin-bottom:12px}
.title{font-size:26px;font-weight:1000;margin:0 0 6px}
.sub{font-size:14px;color:#64748b;font-weight:900;line-height:1.45;margin-bottom:10px}
.toolbar{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}
.btn{height:44px;border:0;border-radius:14px;color:#fff;font-size:15px;font-weight:1000;background:#365ee8}
.btn.gray{background:#64748b}.btn.green{background:#15803d}.btn.red{background:#b83a2f}.btn.orange{background:#d97706}.btn.yellow{background:#f2c94c;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.28)}
.ticket{border:1px solid #dbe5f1;border-radius:18px;background:#fff;padding:13px;margin-bottom:10px}
.ticket-head{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}
.ticket-title{font-size:18px;font-weight:1000;line-height:1.25}
.badge{display:inline-flex;align-items:center;border-radius:999px;padding:4px 8px;background:#e2e8f0;color:#475569;font-size:12px;font-weight:1000;white-space:nowrap}
.meta{margin-top:8px;color:#475569;font-size:13px;font-weight:850;line-height:1.45;white-space:pre-wrap}
.actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
.actions.three{grid-template-columns:1fr 1fr 1fr}
.empty{padding:18px;text-align:center;color:#64748b;font-weight:900}
.mask{position:fixed;inset:0;background:rgba(15,23,42,.48);z-index:9999;display:none;align-items:center;justify-content:center;padding:18px}
.transfer-mask{position:fixed;inset:0;background:rgba(15,23,42,.48);z-index:9999;display:none;align-items:center;justify-content:center;padding:18px}
.modal{width:min(94vw,480px);background:#fff;border-radius:22px;padding:18px;box-shadow:0 22px 58px rgba(15,23,42,.24)}
.modal h2{margin:0 0 8px;font-size:23px}
label{display:block;margin:10px 0 5px;color:#475569;font-size:14px;font-weight:1000}
textarea,input{width:100%;border:1px solid #cbd5e1;border-radius:14px;background:#f8fafc;color:#102348;font-size:15px;font-weight:850;padding:10px}
textarea{min-height:80px;resize:vertical}
.modal-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px}
</style>
</head>
<body>
<div class="app-shell">
<section class="hero app-standard-hero">
  <div class="hero-main">
    <span class="hero-logo"><img class="hero-logo-img" src="/static/shinnan_home_logo.png" alt="Logo"></span>
    <h1 class="hero-title">\u7dad\u4fee\u90e8\u7cfb\u7d71</h1>
  </div>
  <div class="hero-sub">__USER_LINE__</div>
</section>

<main class="content">
  <div class="card">
    <h2 class="title">\u7dad\u4fee\u90e8\u6848\u4ef6</h2>
    <div class="sub">\u627f\u63a5\u5404\u5340\u5de5\u52d9\u7121\u6cd5\u5b8c\u4fee\u3001\u9700\u652f\u63f4\u6216\u516c\u8a2d\u76f8\u95dc\u6848\u4ef6\u3002</div>
    <div class="toolbar">
      <button class="btn gray" onclick="location.href='/app'">\u8fd4\u56de\u9996\u9801</button>
      <button class="btn green" onclick="loadTickets()">\u91cd\u65b0\u6574\u7406</button>
    </div>
  </div>
  <div id="ticket_list"></div>
</main>
</div>

<div id="complete_mask" class="mask">
  <div class="modal">
    <h2>\u5b8c\u5de5\u56de\u5831</h2>
    <input type="hidden" id="complete_ticket_id">
    <label>\u7dad\u4fee\u539f\u56e0</label>
    <textarea id="complete_reason" placeholder="\u8acb\u586b\u5beb\u7dad\u4fee\u539f\u56e0"></textarea>
    <label>\u8655\u7406\u7d50\u679c</label>
    <textarea id="complete_result" placeholder="\u8acb\u586b\u5beb\u8655\u7406\u65b9\u5f0f\u8207\u5b8c\u5de5\u8aaa\u660e"></textarea>
    <label>\u6e2c\u901f\u7167\u7247</label>
    <input id="complete_speedtest" type="file" accept="image/*">
    <div class="modal-actions">
      <button class="btn gray" onclick="closeCompleteModal()">\u53d6\u6d88</button>
      <button class="btn green" onclick="submitComplete()">\u9001\u51fa\u5b8c\u5de5</button>
    </div>
  </div>
</div>


<div id="transfer_mask" class="transfer-mask">
  <div class="modal">
    <h2>\u8f49\u6d3e\u6848\u4ef6</h2>
    <input type="hidden" id="transfer_ticket_id">

    <label>\u76ee\u6a19\u90e8\u9580</label>
    <select id="transfer_department" style="width:100%;border:1px solid #cbd5e1;border-radius:14px;background:#f8fafc;color:#102348;font-size:15px;font-weight:850;padding:10px"></select>

    <label>\u8f49\u6d3e\u5099\u8a3b</label>
    <textarea id="transfer_note" placeholder="\u53ef\u586b\u5beb\u8f49\u6d3e\u539f\u56e0\u6216\u88dc\u5145\u8aaa\u660e"></textarea>

    <div class="modal-actions">
      <button class="btn gray" onclick="closeTransferModal()">\u53d6\u6d88</button>
      <button class="btn yellow" onclick="submitTransfer()">\u78ba\u8a8d\u8f49\u6d3e</button>
    </div>
  </div>
</div>

<script>
const byId=(id)=>document.getElementById(id);
let tickets=[];

function esc(s){
  return String(s??"").replace(/[&<>"']/g,function(m){
    return {"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#039;"}[m];
  });
}

function statusBadge(item){
  const s=String(item.status||"");
  if(s.includes("\u672a\u9818")) return "\u5f85\u9818\u53d6";
  if(s.includes("\u9818")) return "\u8655\u7406\u4e2d";
  if(s.includes("\u5b8c")) return "\u5df2\u5b8c\u5de5";
  return s || "\u672a\u77e5";
}

async function loadTickets(){
  const box=byId("ticket_list");
  box.innerHTML="<div class='empty'>\u8cc7\u6599\u8f09\u5165\u4e2d...</div>";

  const res=await fetch("/api/app/maintenance/tickets?ts="+Date.now(),{cache:"no-store",credentials:"same-origin"});
  if(res.status===401){location.href="/employee/login?next=/app/maintenance";return}
  const data=await res.json().catch(()=>({}));

  if(!res.ok||!data.ok){
    box.innerHTML="<div class='card empty'>"+esc(data.error||"\u8f09\u5165\u5931\u6557")+"</div>";
    return;
  }

  tickets=data.items||[];
  renderTickets();
}

function renderTickets(){
  const box=byId("ticket_list");
  if(!tickets.length){
    box.innerHTML="<div class='card empty'>\u76ee\u524d\u6c92\u6709\u7dad\u4fee\u90e8\u6848\u4ef6\u3002</div>";
    return;
  }

  box.innerHTML=tickets.map(function(item){
    const title=esc(item.ticket_no)+"｜"+esc(item.case_type||"\u7dad\u4fee\u652f\u63f4");
    const meta=[
      item.customer_name ? "\u5ba2\u6236\uff1a"+item.customer_name : "",
      item.contact_name || item.contact_phone ? "\u806f\u7d61\uff1a"+[item.contact_name,item.contact_phone].filter(Boolean).join(" / ") : "",
      item.service_address ? "\u5730\u5740\uff1a"+item.service_address : "",
      item.transfer_source_department ? "\u4f86\u6e90\uff1a"+item.transfer_source_department : "",
      item.transfer_note ? "\u8f49\u6d3e\u5099\u8a3b\uff1a"+item.transfer_note : "",
      item.description ? "\u8aaa\u660e\uff1a"+item.description : ""
    ].filter(Boolean).join("\\n");

    return `
      <div class="ticket">
        <div class="ticket-head">
          <div class="ticket-title">${title}</div>
          <span class="badge">${esc(statusBadge(item))}</span>
        </div>
        <div class="meta">${esc(meta)}</div>
        <div class="actions">
          <button class="btn green" onclick="claimTicket(${item.id})">\u9818\u53d6</button>
          <button class="btn yellow" onclick="openTransferModal(${item.id})">\u8f49\u6d3e</button>
        </div>
        <div class="actions">
          <button class="btn orange" onclick="openCompleteModal(${item.id})">\u5b8c\u5de5</button>
          <button class="btn red" onclick="returnTicket(${item.id})">\u9000\u56de</button>
        </div>
      </div>
    `;
  }).join("");
}

async function claimTicket(id){
  if(!confirm("\u78ba\u8a8d\u9818\u53d6\u6b64\u7dad\u4fee\u6848\uff1f")) return;
  const res=await fetch("/api/app/maintenance/tickets/"+encodeURIComponent(id)+"/claim",{method:"POST",credentials:"same-origin"});
  const data=await res.json().catch(()=>({}));
  if(!res.ok||!data.ok){alert(data.error||"\u9818\u53d6\u5931\u6557");return}
  await loadTickets();
}

async function returnTicket(id){
  const reason=prompt("\u8acb\u8f38\u5165\u9000\u56de\u539f\u56e0","");
  if(reason===null)return;
  const res=await fetch("/api/app/maintenance/tickets/"+encodeURIComponent(id)+"/return",{
    method:"POST",
    credentials:"same-origin",
    headers:{"Content-Type":"application/json; charset=utf-8"},
    body:JSON.stringify({reason:reason})
  });
  const data=await res.json().catch(()=>({}));
  if(!res.ok||!data.ok){alert(data.error||"\u9000\u56de\u5931\u6557");return}
  alert("\u5df2\u9000\u56de\u539f\u5340\u3002");
  await loadTickets();
}

function openCompleteModal(id){
  byId("complete_ticket_id").value=String(id);
  byId("complete_reason").value="";
  byId("complete_result").value="";
  byId("complete_speedtest").value="";
  byId("complete_mask").style.display="flex";
}

function closeCompleteModal(){
  byId("complete_mask").style.display="none";
}

function fileToBase64(file){
  return new Promise(function(resolve){
    if(!file){resolve("");return}
    const reader=new FileReader();
    reader.onload=function(){resolve(String(reader.result||""))};
    reader.onerror=function(){resolve("")};
    reader.readAsDataURL(file);
  });
}

async function submitComplete(){
  const id=byId("complete_ticket_id").value;
  const file=byId("complete_speedtest").files[0];
  const speedtest=await fileToBase64(file);

  const payload={
    repair_reason:byId("complete_reason").value,
    result_note:byId("complete_result").value,
    speedtest_photo_data:speedtest
  };

  const res=await fetch("/api/app/maintenance/tickets/"+encodeURIComponent(id)+"/complete",{
    method:"POST",
    credentials:"same-origin",
    headers:{"Content-Type":"application/json; charset=utf-8"},
    body:JSON.stringify(payload)
  });
  const data=await res.json().catch(()=>({}));
  if(!res.ok||!data.ok){alert(data.error||"\u5b8c\u5de5\u5931\u6557");return}
  alert("\u5df2\u9001\u51fa\u5b8c\u5de5\u56de\u5831\u3002");
  closeCompleteModal();
  await loadTickets();
}


async function loadMaintenanceDepartments(){
  const res=await fetch("/api/app/maintenance/departments?ts="+Date.now(),{cache:"no-store",credentials:"same-origin"});
  const data=await res.json().catch(()=>({}));
  if(!res.ok||!data.ok){return []}
  return data.items||[];
}

async function openTransferModal(id){
  byId("transfer_ticket_id").value=String(id);
  byId("transfer_note").value="";
  const select=byId("transfer_department");
  select.innerHTML="<option value=''>\u8f09\u5165\u4e2d...</option>";

  const items=await loadMaintenanceDepartments();
  if(!items.length){
    select.innerHTML="<option value=''>\u6c92\u6709\u53ef\u8f49\u6d3e\u90e8\u9580</option>";
  }else{
    select.innerHTML=items.map(function(x){
      return "<option value='"+esc(x)+"'>"+esc(x)+"</option>";
    }).join("");
  }

  byId("transfer_mask").style.display="flex";
}

function closeTransferModal(){
  byId("transfer_mask").style.display="none";
}

async function submitTransfer(){
  const id=byId("transfer_ticket_id").value;
  const target=String(byId("transfer_department").value||"").trim();
  const note=String(byId("transfer_note").value||"").trim();

  if(!target){
    alert("\u8acb\u9078\u64c7\u76ee\u6a19\u90e8\u9580");
    return;
  }

  if(!confirm("\u78ba\u8a8d\u8f49\u6d3e\u7d66\u300c"+target+"\u300d\uff1f")){
    return;
  }

  const res=await fetch("/api/app/maintenance/tickets/"+encodeURIComponent(id)+"/transfer",{
    method:"POST",
    credentials:"same-origin",
    headers:{"Content-Type":"application/json; charset=utf-8"},
    body:JSON.stringify({target_department:target,note:note})
  });

  const data=await res.json().catch(()=>({}));

  if(!res.ok||!data.ok){
    alert(data.error||"\u8f49\u6d3e\u5931\u6557");
    return;
  }

  alert("\u5df2\u8f49\u6d3e\u7d66\u300c"+target+"\u300d");
  closeTransferModal();
  await loadTickets();
}

loadTickets();
</script>

  <script src="/static/app_header_actions.js?v=cl17p3"></script>
</body>
</html>
""".replace("__USER_LINE__", user_line)
