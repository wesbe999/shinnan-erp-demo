from __future__ import annotations

import json as _json

from fastapi import APIRouter, Body
from fastapi import Request as _Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy import text as _sql_text

from app.db import engine
from app.routes.employee_auth import _employee_current_user_from_request


router = APIRouter(tags=["手機派工 APP"])


def _json_response(payload: dict, status_code: int = 200) -> Response:
    return Response(
        content=_json.dumps(payload, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
        status_code=status_code,
    )


def _safe_text(value) -> str:
    return "" if value is None else str(value)


def _safe_number(value):
    if value is None:
        return 0
    try:
        return float(value)
    except Exception:
        return 0


def _table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        _sql_text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table_name},
    ).fetchone()
    return row is not None


def _table_columns(conn, table_name: str) -> set[str]:
    if not _table_exists(conn, table_name):
        return set()

    rows = conn.execute(_sql_text(f"PRAGMA table_info({table_name})")).mappings().fetchall()
    return {str(row["name"]) for row in rows}


def _col(alias: str, columns: set[str], name: str, default_sql: str = "''") -> str:
    if name in columns:
        return f"{alias}.{name}"
    return default_sql


def _dispatch_building_col(join_enabled: bool, building_cols: set[str], name: str, default_sql: str = "''") -> str:
    if join_enabled and name in building_cols:
        return f"b.{name}"
    return default_sql


def _dispatch_plain_address(value) -> str:
    text = _safe_text(value).strip()

    for separator in ("|", "\uff5c"):
        if separator in text:
            text = text.split(separator)[-1].strip()

    return text


def _dispatch_navigation_address(raw: dict) -> tuple[str, str, str]:
    service_address = _safe_text(raw.get("service_address")).strip()
    building_address = (
        _dispatch_plain_address(raw.get("building_address"))
        or _dispatch_plain_address(raw.get("building_display_address"))
        or _dispatch_plain_address(raw.get("building_raw_address"))
    )
    building_type = _safe_text(raw.get("building_type")).strip()
    building_no = _safe_text(raw.get("building_no")).strip()

    is_house = (
        building_no.upper() == "HOUSE"
        or building_type in {"\u900f\u5929", "\u900f\u5929\u539d"}
        or ("\u900f\u5929" in service_address and not building_address)
    )

    if is_house:
        return service_address, building_address, building_type

    return building_address or service_address, building_address, building_type


# XN_DISPATCH_PROXY_CONTEXT_STABLE_V1
def _dispatch_proxy_context_from_request(request: _Request, user: dict) -> dict:
    login_staff_code = _safe_text(user.get("staff_code")).strip()
    login_staff_name = _safe_text(user.get("display_name")).strip()
    login_department = _safe_text(user.get("department")).strip()
    login_role = _safe_text(user.get("role")).strip()

    requested_owner = _safe_text(request.cookies.get("xunnan_permission_owner_code")).strip()
    requested_acting = _safe_text(request.cookies.get("xunnan_acting_staff_code")).strip()
    requested_code = requested_owner or requested_acting

    context = {
        "login_staff_code": login_staff_code,
        "login_display_name": login_staff_name,
        "login_department": login_department,
        "login_role": login_role,
        "staff_code": login_staff_code,
        "display_name": login_staff_name,
        "department": login_department,
        "role": login_role,
        "permission_owner_code": login_staff_code,
        "permission_owner_name": login_staff_name,
        "is_proxy_mode": False,
    }

    if not login_staff_code or not requested_code or requested_code == login_staff_code:
        return context

    with engine.begin() as conn:
        allowed = conn.execute(
            _sql_text("""
                SELECT 1
                FROM employee_proxy_settings
                WHERE staff_code = :owner_code
                  AND (
                    (proxy_one_staff_code = :login_staff_code AND COALESCE(proxy_one_status, '') = 'accepted')
                    OR
                    (proxy_two_staff_code = :login_staff_code AND COALESCE(proxy_two_status, '') = 'accepted')
                  )
                LIMIT 1
            """),
            {
                "owner_code": requested_code,
                "login_staff_code": login_staff_code,
            },
        ).fetchone()

        if not allowed:
            return context

        owner = conn.execute(
            _sql_text("""
                SELECT staff_code, display_name, department, role, position_title
                FROM employee_profiles
                WHERE staff_code = :staff_code
                LIMIT 1
            """),
            {"staff_code": requested_code},
        ).mappings().first()

    owner_code = requested_code
    owner_name = owner_code
    owner_department = ""
    owner_role = ""

    if owner:
        owner_code = _safe_text(owner.get("staff_code")).strip() or requested_code
        owner_name = _safe_text(owner.get("display_name")).strip() or owner_code
        owner_department = _safe_text(owner.get("department")).strip()
        owner_role = _safe_text(owner.get("role")).strip()

    context.update({
        "staff_code": owner_code,
        "display_name": owner_name,
        "department": owner_department,
        "role": owner_role,
        "permission_owner_code": owner_code,
        "permission_owner_name": owner_name,
        "is_proxy_mode": True,
    })

    return context
# XN_DISPATCH_PROXY_CONTEXT_STABLE_V1_END



# CL15L1_DISPATCH_TRANSFER_HELPERS_START
def _dispatch_now_text():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _ensure_dispatch_transfer_columns(conn):
    ticket_cols = _table_columns(conn, "tickets")
    wanted = {
        "transfer_origin_ticket_id": "INTEGER",
        "transfer_child_ticket_id": "INTEGER",
        "transfer_target_department": "TEXT",
        "transfer_source_department": "TEXT",
        "transfer_status": "TEXT",
        "transfer_note": "TEXT",
        "transfer_created_at": "TEXT",
        "transfer_updated_at": "TEXT",
    }

    for col, col_type in wanted.items():
        if col not in ticket_cols:
            conn.execute(_sql_text("ALTER TABLE tickets ADD COLUMN " + col + " " + col_type))


def _dispatch_status_completed_for_transfer():
    return "\u5df2\u5b8c\u5de5"


def _dispatch_status_unclaimed_for_transfer():
    return "\u672a\u9818\u53d6"


def _dispatch_status_transfering():
    return "\u8f49\u6d3e\u4e2d"


def _dispatch_get_departments(conn):
    departments = []

    if _table_exists(conn, "employee_profiles"):
        rows = conn.execute(_sql_text("""
            SELECT DISTINCT COALESCE(department, '') AS department
            FROM employee_profiles
            WHERE COALESCE(department, '') <> ''
            ORDER BY department
        """)).mappings().fetchall()
        departments = [str(r["department"] or "").strip() for r in rows if str(r["department"] or "").strip()]

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


# CL15L1_DISPATCH_TRANSFER_HELPERS_END


@router.get("/api/app/dispatch/tickets", summary="手機派工 APP 讀取派工案件")
def api_app_dispatch_tickets(request: _Request):
    user = _employee_current_user_from_request(request)

    if not user:
        return _json_response({"ok": False, "error": "login required"}, status_code=401)

    proxy_context = _dispatch_proxy_context_from_request(request, user)

    login_staff_code = proxy_context["login_staff_code"]
    staff_code = proxy_context["staff_code"]
    staff_name = proxy_context["display_name"]
    department = proxy_context["department"]
    role = proxy_context["role"]

    with engine.begin() as conn:
        ticket_cols = _table_columns(conn, "tickets")
        install_cols = _table_columns(conn, "ticket_install_details")
        return_cols = _table_columns(conn, "ticket_return_details")
        building_cols = _table_columns(conn, "buildings")

        if not ticket_cols:
            return _json_response({
                "ok": False,
                "error": "tickets table not found",
                "items": [],
            }, status_code=500)

        join_install = "LEFT JOIN ticket_install_details i ON i.ticket_id = t.id" if install_cols else ""
        join_return = "LEFT JOIN ticket_return_details r ON r.ticket_id = t.id" if return_cols else ""
        join_building = ""

        if (
            building_cols
            and "building_no" in ticket_cols
            and "building_no" in building_cols
        ):
            building_join_parts = ["COALESCE(b.building_no, '') = COALESCE(t.building_no, '')"]

            if "dispatch_area" in ticket_cols and "area" in building_cols:
                building_join_parts.append("COALESCE(b.area, '') = COALESCE(t.dispatch_area, '')")

            join_building = "LEFT JOIN buildings b ON " + " AND ".join(building_join_parts)

        has_building_join = bool(join_building)

        where_parts = []
        params = {}

        if role != "admin":
            personal_parts = []

            if "assigned_engineer" in ticket_cols and staff_name:
                personal_parts.append("COALESCE(t.assigned_engineer, '') = :staff_name")
                params["staff_name"] = staff_name

            if "assigned_engineer_staff_code" in ticket_cols and staff_code:
                personal_parts.append("COALESCE(t.assigned_engineer_staff_code, '') = :staff_code")
                params["staff_code"] = staff_code

            if "dispatch_area" in ticket_cols and department:
                personal_parts.append("COALESCE(t.dispatch_area, '') = :department")
                params["department"] = department

            if personal_parts:
                where_parts.append("(" + " OR ".join(personal_parts) + ")")

        where_sql = ""
        if where_parts:
            where_sql = "WHERE " + " AND ".join(where_parts)

        query = f"""
            SELECT
                {_col("t", ticket_cols, "id", "0")} AS id,
                {_col("t", ticket_cols, "ticket_no")} AS ticket_no,
                {_col("t", ticket_cols, "case_type")} AS case_type,
                {_col("t", ticket_cols, "status")} AS status,
                {_col("t", ticket_cols, "customer_name")} AS customer_name,
                {_col("t", ticket_cols, "contact_name")} AS contact_name,
                {_col("t", ticket_cols, "contact_phone")} AS contact_phone,
                {_col("t", ticket_cols, "service_address")} AS service_address,
                {_col("t", ticket_cols, "appointment_date")} AS appointment_date,
                {_col("t", ticket_cols, "appointment_time")} AS appointment_time,
                {_col("t", ticket_cols, "assigned_engineer")} AS assigned_engineer,
                {_col("t", ticket_cols, "assigned_engineer_staff_code")} AS assigned_engineer_staff_code,
                {_col("t", ticket_cols, "dispatch_area")} AS dispatch_area,
                {_col("t", ticket_cols, "description")} AS description,
                {_col("t", ticket_cols, "internal_note")} AS internal_note,
                {_col("t", ticket_cols, "completion_note")} AS completion_note,
                {_col("t", ticket_cols, "created_at")} AS created_at,
                {_col("t", ticket_cols, "arrived_at")} AS arrived_at,
                {_col("t", ticket_cols, "completed_at")} AS completed_at,
                {_col("t", ticket_cols, "customer_no")} AS customer_no,
                {_col("t", ticket_cols, "building_no")} AS building_no,
                {_dispatch_building_col(has_building_join, building_cols, "address")} AS building_address,
                {_dispatch_building_col(has_building_join, building_cols, "raw_address")} AS building_raw_address,
                {_dispatch_building_col(has_building_join, building_cols, "display_address")} AS building_display_address,
                {_dispatch_building_col(has_building_join, building_cols, "building_type")} AS building_type,
                {_col("t", ticket_cols, "transfer_origin_ticket_id", "0")} AS transfer_origin_ticket_id,
                {_col("t", ticket_cols, "transfer_child_ticket_id", "0")} AS transfer_child_ticket_id,
                {_col("t", ticket_cols, "transfer_target_department")} AS transfer_target_department,
                {_col("t", ticket_cols, "transfer_source_department")} AS transfer_source_department,
                {_col("t", ticket_cols, "transfer_status")} AS transfer_status,
                {_col("t", ticket_cols, "transfer_note")} AS transfer_note,

                {_col("i", install_cols, "id", "NULL")} AS install_detail_id,
                {_col("i", install_cols, "deposit_amount", "0")} AS i_deposit_amount,
                {_col("i", install_cols, "construction_fee", "0")} AS i_construction_fee,
                {_col("i", install_cols, "monthly_fee", "0")} AS i_monthly_fee,
                {_col("i", install_cols, "monthly_fee_1", "0")} AS i_monthly_fee_1,
                {_col("i", install_cols, "monthly_fee_2", "0")} AS i_monthly_fee_2,
                {_col("i", install_cols, "monthly_fee_3", "0")} AS i_monthly_fee_3,
                {_col("i", install_cols, "month_count", "1")} AS i_month_count,
                {_col("i", install_cols, "other_fee", "0")} AS i_other_fee,
                {_col("i", install_cols, "other_fee_1", "0")} AS i_other_fee_1,
                {_col("i", install_cols, "other_fee_2", "0")} AS i_other_fee_2,
                {_col("i", install_cols, "rent_subtotal", "0")} AS i_rent_subtotal,
                {_col("i", install_cols, "total_amount", "0")} AS i_total_amount,

                {_col("r", return_cols, "id", "NULL")} AS return_detail_id,
                {_col("r", return_cols, "payment_record")} AS r_payment_record,
                {_col("r", return_cols, "deposit_amount", "0")} AS r_deposit_amount,
                {_col("r", return_cols, "refund_amount", "0")} AS r_refund_amount,
                {_col("r", return_cols, "deduction_amount", "0")} AS r_deduction_amount,
                {_col("r", return_cols, "device_fee", "0")} AS r_device_fee,
                {_col("r", return_cols, "cleaning_fee", "0")} AS r_cleaning_fee,
                {_col("r", return_cols, "other_fee", "0")} AS r_other_fee,
                {_col("r", return_cols, "total_amount", "0")} AS r_total_amount,
                {_col("r", return_cols, "returned_device_status")} AS r_returned_device_status,
                {_col("r", return_cols, "return_note")} AS r_return_note,
                {_col("r", return_cols, "settlement_note")} AS r_settlement_note

            FROM tickets t
            {join_building}
            {join_install}
            {join_return}
            {where_sql}
            ORDER BY
                CASE COALESCE(t.status, '')
                    WHEN '未派工' THEN 1
                    WHEN '待派工' THEN 1
                    WHEN '已建立' THEN 2
                    WHEN '已指派' THEN 3
                    WHEN '已領取' THEN 4
                    WHEN '施工中' THEN 5
                    WHEN '已完工' THEN 9
                    WHEN '已完成' THEN 9
                    ELSE 6
                END,
                COALESCE(t.appointment_date, '') ASC,
                COALESCE(t.appointment_time, '') ASC,
                t.id DESC
        """

        rows = conn.execute(_sql_text(query), params).mappings().fetchall()

    items = []

    for row in rows:
        raw = dict(row)

        install_detail = None
        if raw.get("install_detail_id") is not None:
            monthly_fee = _safe_number(raw.get("i_monthly_fee"))
            monthly_fee_1 = _safe_number(raw.get("i_monthly_fee_1")) or monthly_fee

            install_detail = {
                "deposit_amount": _safe_number(raw.get("i_deposit_amount")),
                "construction_fee": _safe_number(raw.get("i_construction_fee")),
                "install_fee": _safe_number(raw.get("i_construction_fee")),
                "monthly_fee": monthly_fee,
                "monthly_fee_1": monthly_fee_1,
                "monthly_fee_2": _safe_number(raw.get("i_monthly_fee_2")),
                "monthly_fee_3": _safe_number(raw.get("i_monthly_fee_3")),
                "month_count": _safe_number(raw.get("i_month_count")) or 1,
                "rent_subtotal": _safe_number(raw.get("i_rent_subtotal")),
                "other_fee": _safe_number(raw.get("i_other_fee")),
                "other_fee_1": _safe_number(raw.get("i_other_fee_1")),
                "other_fee_2": _safe_number(raw.get("i_other_fee_2")),
                "total_amount": _safe_number(raw.get("i_total_amount")),
            }

        return_detail = None
        if raw.get("return_detail_id") is not None:
            return_detail = {
                "payment_record": _safe_text(raw.get("r_payment_record")),
                "deposit_amount": _safe_number(raw.get("r_deposit_amount")),
                "refund_amount": _safe_number(raw.get("r_refund_amount")),
                "deduction_amount": _safe_number(raw.get("r_deduction_amount")),
                "device_fee": _safe_number(raw.get("r_device_fee")),
                "cleaning_fee": _safe_number(raw.get("r_cleaning_fee")),
                "other_fee": _safe_number(raw.get("r_other_fee")),
                "total_amount": _safe_number(raw.get("r_total_amount")),
                "returned_device_status": _safe_text(raw.get("r_returned_device_status")),
                "return_note": _safe_text(raw.get("r_return_note")),
                "settlement_note": _safe_text(raw.get("r_settlement_note")),
            }

        navigation_address, building_address, building_type = _dispatch_navigation_address(raw)

        items.append({
            "id": raw.get("id"),
            "ticket_no": _safe_text(raw.get("ticket_no")),
            "case_type": _safe_text(raw.get("case_type")),
            "status": _safe_text(raw.get("status")),
            "customer_name": _safe_text(raw.get("customer_name")),
            "contact_name": _safe_text(raw.get("contact_name")),
            "contact_phone": _safe_text(raw.get("contact_phone")),
            "service_address": _safe_text(raw.get("service_address")),
            "appointment_date": _safe_text(raw.get("appointment_date")),
            "appointment_time": _safe_text(raw.get("appointment_time")),
            "assigned_engineer": _safe_text(raw.get("assigned_engineer")),
            "assigned_engineer_staff_code": _safe_text(raw.get("assigned_engineer_staff_code")),
            "dispatch_area": _safe_text(raw.get("dispatch_area")),
            "description": _safe_text(raw.get("description")),
            "internal_note": _safe_text(raw.get("internal_note")),
            "completion_note": _safe_text(raw.get("completion_note")),
            "created_at": _safe_text(raw.get("created_at")),
            "arrived_at": _safe_text(raw.get("arrived_at")),
            "completed_at": _safe_text(raw.get("completed_at")),
            "customer_no": _safe_text(raw.get("customer_no")),
            "building_no": _safe_text(raw.get("building_no")),
            "building_address": building_address,
            "building_type": building_type,
            "navigation_address": navigation_address,
            "transfer_origin_ticket_id": raw.get("transfer_origin_ticket_id") or 0,
            "transfer_child_ticket_id": raw.get("transfer_child_ticket_id") or 0,
            "transfer_target_department": _safe_text(raw.get("transfer_target_department")),
            "transfer_source_department": _safe_text(raw.get("transfer_source_department")),
            "transfer_status": _safe_text(raw.get("transfer_status")),
            "transfer_note": _safe_text(raw.get("transfer_note")),
            "install_detail": install_detail,
            "return_detail": return_detail,
        })

    return _json_response({
        "ok": True,
        "source": "tickets",
        "linked_with_admin_ticket_api": True,
        "user": {
            "staff_code": staff_code,
            "display_name": staff_name,
            "department": department,
            "role": role,
            "login_staff_code": login_staff_code,
            "permission_owner_code": proxy_context["permission_owner_code"],
            "permission_owner_name": proxy_context["permission_owner_name"],
            "is_proxy_mode": proxy_context["is_proxy_mode"],
        },
        "items": items,
    })



# CL15L1_DISPATCH_TRANSFER_APIS_START
@router.get("/api/app/dispatch/departments", summary="\u624b\u6a5f\u6d3e\u5de5 APP \u8f49\u6d3e\u90e8\u9580\u6e05\u55ae")
def api_app_dispatch_departments(request: _Request):
    user = _employee_current_user_from_request(request)

    if not user:
        return _json_response({"ok": False, "error": "login required"}, status_code=401)

    with engine.begin() as conn:
        departments = _dispatch_get_departments(conn)

    return _json_response({"ok": True, "items": departments})


@router.post("/api/app/dispatch/tickets/{ticket_id}/claim", summary="\u624b\u6a5f\u6d3e\u5de5 APP \u9818\u53d6\u6848\u4ef6")
def api_app_dispatch_claim_ticket(ticket_id: int, request: _Request, payload: dict = Body(default_factory=dict)):
    user = _employee_current_user_from_request(request)

    if not user:
        return _json_response({"ok": False, "error": "login required"}, status_code=401)

    proxy_context = _dispatch_proxy_context_from_request(request, user)
    staff_code = proxy_context["staff_code"]
    staff_name = str(payload.get("assigned_engineer") or proxy_context["display_name"] or "").strip()
    if not staff_name:
        staff_name = "\u7cfb\u7d71\u7ba1\u7406\u54e1"

    now_text = _dispatch_now_text()

    with engine.begin() as conn:
        _ensure_dispatch_transfer_columns(conn)
        ticket_cols = _table_columns(conn, "tickets")

        ticket = conn.execute(
            _sql_text("SELECT * FROM tickets WHERE id = :id LIMIT 1"),
            {"id": ticket_id},
        ).mappings().first()

        if not ticket:
            return _json_response({"ok": False, "error": "ticket not found"}, status_code=404)

        sets = []
        params = {
            "id": ticket_id,
            "status": "\u5df2\u9818\u53d6",
            "assigned_engineer": staff_name,
            "assigned_engineer_staff_code": staff_code,
            "arrived_at": now_text,
            "transfer_updated_at": now_text,
        }

        if "status" in ticket_cols:
            sets.append("status = :status")
        if "assigned_engineer" in ticket_cols:
            sets.append("assigned_engineer = :assigned_engineer")
        if "assigned_engineer_staff_code" in ticket_cols:
            sets.append("assigned_engineer_staff_code = :assigned_engineer_staff_code")
        if "arrived_at" in ticket_cols:
            sets.append("arrived_at = COALESCE(arrived_at, :arrived_at)")
        if "transfer_updated_at" in ticket_cols:
            sets.append("transfer_updated_at = :transfer_updated_at")

        if sets:
            conn.execute(_sql_text("UPDATE tickets SET " + ", ".join(sets) + " WHERE id = :id"), params)

        origin_id = int(ticket.get("transfer_origin_ticket_id") or 0)

        if origin_id > 0:
            origin_sets = []
            origin_params = {
                "origin_id": origin_id,
                "status": _dispatch_status_completed_for_transfer(),
                "completed_at": now_text,
                "finished_at": now_text,
                "transfer_status": "\u5df2\u9818\u53d6\uff0c\u539f\u6848\u5b8c\u5de5",
                "transfer_updated_at": now_text,
                "completion_note": "\u8f49\u6d3e\u6848\u4ef6\u5df2\u88ab\u9818\u53d6\uff0c\u539f\u6848\u81ea\u52d5\u5217\u70ba\u5b8c\u5de5\u3002",
            }

            if "status" in ticket_cols:
                origin_sets.append("status = :status")
            if "completed_at" in ticket_cols:
                origin_sets.append("completed_at = COALESCE(completed_at, :completed_at)")
            if "finished_at" in ticket_cols:
                origin_sets.append("finished_at = COALESCE(finished_at, :finished_at)")
            if "transfer_status" in ticket_cols:
                origin_sets.append("transfer_status = :transfer_status")
            if "transfer_updated_at" in ticket_cols:
                origin_sets.append("transfer_updated_at = :transfer_updated_at")
            if "completion_note" in ticket_cols:
                origin_sets.append("completion_note = CASE WHEN COALESCE(completion_note, '') = '' THEN :completion_note ELSE completion_note || char(10) || :completion_note END")

            if origin_sets:
                conn.execute(_sql_text("UPDATE tickets SET " + ", ".join(origin_sets) + " WHERE id = :origin_id"), origin_params)

    return _json_response({
        "ok": True,
        "id": ticket_id,
        "status": "\u5df2\u9818\u53d6",
        "assigned_engineer": staff_name,
        "transfer_origin_completed": bool(origin_id > 0),
    })


@router.post("/api/app/dispatch/tickets/{ticket_id}/transfer", summary="\u624b\u6a5f\u6d3e\u5de5 APP \u8f49\u6d3e\u6848\u4ef6")
def api_app_dispatch_transfer_ticket(ticket_id: int, request: _Request, payload: dict = Body(default_factory=dict)):
    user = _employee_current_user_from_request(request)

    if not user:
        return _json_response({"ok": False, "error": "login required"}, status_code=401)

    target_department = str(payload.get("target_department") or "").strip()
    transfer_note = str(payload.get("note") or "").strip()

    if not target_department:
        return _json_response({"ok": False, "error": "target department required"}, status_code=400)

    proxy_context = _dispatch_proxy_context_from_request(request, user)
    source_department = proxy_context["department"]
    now_text = _dispatch_now_text()

    with engine.begin() as conn:
        _ensure_dispatch_transfer_columns(conn)
        ticket_cols = _table_columns(conn, "tickets")

        departments = _dispatch_get_departments(conn)
        if target_department not in departments:
            return _json_response({"ok": False, "error": "target department not allowed"}, status_code=400)

        original = conn.execute(
            _sql_text("SELECT * FROM tickets WHERE id = :id LIMIT 1"),
            {"id": ticket_id},
        ).mappings().first()

        if not original:
            return _json_response({"ok": False, "error": "ticket not found"}, status_code=404)

        active_child = conn.execute(
            _sql_text("""
                SELECT id
                FROM tickets
                WHERE COALESCE(transfer_origin_ticket_id, 0) = :id
                  AND COALESCE(status, '') NOT IN ('\u9000\u56de', '\u5df2\u53d6\u6d88', '\u4f4f\u6236\u53d6\u6d88')
                ORDER BY id DESC
                LIMIT 1
            """),
            {"id": ticket_id},
        ).mappings().first()

        if active_child:
            return _json_response({"ok": False, "error": "ticket already transferred"}, status_code=409)

        clone = {}
        skip_cols = {"id"}

        for col in ticket_cols:
            if col in skip_cols:
                continue
            clone[col] = original.get(col)

        if "ticket_no" in ticket_cols:
            clone["ticket_no"] = str(original.get("ticket_no") or ("T" + str(ticket_id))) + "-TR" + str(ticket_id)

        if "dispatch_area" in ticket_cols:
            clone["dispatch_area"] = target_department
        if "status" in ticket_cols:
            clone["status"] = _dispatch_status_unclaimed_for_transfer()
        if "assigned_engineer" in ticket_cols:
            clone["assigned_engineer"] = ""
        if "assigned_engineer_staff_code" in ticket_cols:
            clone["assigned_engineer_staff_code"] = ""
        if "created_at" in ticket_cols:
            clone["created_at"] = now_text
        if "arrived_at" in ticket_cols:
            clone["arrived_at"] = None
        if "completed_at" in ticket_cols:
            clone["completed_at"] = None
        if "finished_at" in ticket_cols:
            clone["finished_at"] = None
        if "completion_note" in ticket_cols:
            clone["completion_note"] = ""
        if "transfer_origin_ticket_id" in ticket_cols:
            clone["transfer_origin_ticket_id"] = ticket_id
        if "transfer_child_ticket_id" in ticket_cols:
            clone["transfer_child_ticket_id"] = 0
        if "transfer_target_department" in ticket_cols:
            clone["transfer_target_department"] = target_department
        if "transfer_source_department" in ticket_cols:
            clone["transfer_source_department"] = str(original.get("dispatch_area") or source_department or "")
        if "transfer_status" in ticket_cols:
            clone["transfer_status"] = "\u5f85\u9818\u53d6"
        if "transfer_note" in ticket_cols:
            clone["transfer_note"] = transfer_note
        if "transfer_created_at" in ticket_cols:
            clone["transfer_created_at"] = now_text
        if "transfer_updated_at" in ticket_cols:
            clone["transfer_updated_at"] = now_text

        insert_cols = [c for c in clone.keys() if c in ticket_cols and c != "id"]
        insert_sql = "INSERT INTO tickets (" + ", ".join(insert_cols) + ") VALUES (" + ", ".join([":" + c for c in insert_cols]) + ")"
        result = conn.execute(_sql_text(insert_sql), {c: clone[c] for c in insert_cols})
        child_id = int(result.lastrowid)

        update_sets = []
        update_params = {
            "id": ticket_id,
            "status": _dispatch_status_transfering(),
            "child_id": child_id,
            "target_department": target_department,
            "source_department": str(original.get("dispatch_area") or source_department or ""),
            "transfer_status": "\u8f49\u6d3e\u4e2d",
            "transfer_note": transfer_note,
            "transfer_created_at": now_text,
            "transfer_updated_at": now_text,
        }

        if "status" in ticket_cols:
            update_sets.append("status = :status")
        if "transfer_child_ticket_id" in ticket_cols:
            update_sets.append("transfer_child_ticket_id = :child_id")
        if "transfer_target_department" in ticket_cols:
            update_sets.append("transfer_target_department = :target_department")
        if "transfer_source_department" in ticket_cols:
            update_sets.append("transfer_source_department = :source_department")
        if "transfer_status" in ticket_cols:
            update_sets.append("transfer_status = :transfer_status")
        if "transfer_note" in ticket_cols:
            update_sets.append("transfer_note = :transfer_note")
        if "transfer_created_at" in ticket_cols:
            update_sets.append("transfer_created_at = :transfer_created_at")
        if "transfer_updated_at" in ticket_cols:
            update_sets.append("transfer_updated_at = :transfer_updated_at")

        conn.execute(_sql_text("UPDATE tickets SET " + ", ".join(update_sets) + " WHERE id = :id"), update_params)

    return _json_response({
        "ok": True,
        "origin_ticket_id": ticket_id,
        "transfer_ticket_id": child_id,
        "target_department": target_department,
        "status": _dispatch_status_transfering(),
    })


@router.post("/api/app/dispatch/tickets/{ticket_id}/transfer-return", summary="\u624b\u6a5f\u6d3e\u5de5 APP \u9000\u56de\u8f49\u6d3e")
def api_app_dispatch_transfer_return(ticket_id: int, request: _Request, payload: dict = Body(default_factory=dict)):
    user = _employee_current_user_from_request(request)

    if not user:
        return _json_response({"ok": False, "error": "login required"}, status_code=401)

    reason = str(payload.get("reason") or "").strip()
    now_text = _dispatch_now_text()

    with engine.begin() as conn:
        _ensure_dispatch_transfer_columns(conn)
        ticket_cols = _table_columns(conn, "tickets")

        child = conn.execute(
            _sql_text("SELECT * FROM tickets WHERE id = :id LIMIT 1"),
            {"id": ticket_id},
        ).mappings().first()

        if not child:
            return _json_response({"ok": False, "error": "ticket not found"}, status_code=404)

        origin_id = int(child.get("transfer_origin_ticket_id") or 0)
        if origin_id <= 0:
            return _json_response({"ok": False, "error": "not a transferred ticket"}, status_code=400)

        child_sets = []
        child_params = {
            "id": ticket_id,
            "status": "\u9000\u56de",
            "transfer_status": "\u9000\u56de",
            "transfer_note": reason,
            "transfer_updated_at": now_text,
        }

        if "status" in ticket_cols:
            child_sets.append("status = :status")
        if "transfer_status" in ticket_cols:
            child_sets.append("transfer_status = :transfer_status")
        if "transfer_note" in ticket_cols:
            child_sets.append("transfer_note = CASE WHEN COALESCE(transfer_note, '') = '' THEN :transfer_note ELSE transfer_note || char(10) || :transfer_note END")
        if "transfer_updated_at" in ticket_cols:
            child_sets.append("transfer_updated_at = :transfer_updated_at")

        conn.execute(_sql_text("UPDATE tickets SET " + ", ".join(child_sets) + " WHERE id = :id"), child_params)

        origin_sets = []
        origin_params = {
            "origin_id": origin_id,
            "status": _dispatch_status_unclaimed_for_transfer(),
            "transfer_status": "\u8f49\u6d3e\u88ab\u9000\u56de",
            "transfer_updated_at": now_text,
            "assigned_engineer": "",
            "assigned_engineer_staff_code": "",
        }

        if "status" in ticket_cols:
            origin_sets.append("status = :status")
        if "assigned_engineer" in ticket_cols:
            origin_sets.append("assigned_engineer = :assigned_engineer")
        if "assigned_engineer_staff_code" in ticket_cols:
            origin_sets.append("assigned_engineer_staff_code = :assigned_engineer_staff_code")
        if "transfer_status" in ticket_cols:
            origin_sets.append("transfer_status = :transfer_status")
        if "transfer_updated_at" in ticket_cols:
            origin_sets.append("transfer_updated_at = :transfer_updated_at")

        conn.execute(_sql_text("UPDATE tickets SET " + ", ".join(origin_sets) + " WHERE id = :origin_id"), origin_params)

    return _json_response({
        "ok": True,
        "transfer_ticket_id": ticket_id,
        "origin_ticket_id": origin_id,
        "origin_status": _dispatch_status_unclaimed_for_transfer(),
    })


# CL15L1_DISPATCH_TRANSFER_APIS_END


@router.get("/api/app/dispatch/emergency-notices", summary="手機派工 APP 讀取緊急通知")
def api_app_dispatch_emergency_notices(request: _Request):
    user = _employee_current_user_from_request(request)

    if not user:
        return _json_response({"ok": False, "error": "login required"}, status_code=401)

    from app.config import data_file as _xunnan_data_file

    notice_file = _xunnan_data_file("emergency_notices.json")
    notices = []

    if notice_file.exists():
        try:
            data = _json.loads(notice_file.read_text(encoding="utf-8"))

            if isinstance(data, dict):
                raw = data.get("notices")
                if isinstance(raw, list):
                    notices = [str(x or "").strip() for x in raw if str(x or "").strip()]
                else:
                    old_message = data.get("message") or data.get("notice") or ""
                    if str(old_message or "").strip():
                        notices = [str(old_message).strip()]

            elif isinstance(data, list):
                notices = [str(x or "").strip() for x in data if str(x or "").strip()]

        except Exception:
            notices = []

    items = [
        {
            "id": index + 1,
            "title": "緊急通知",
            "message": message,
            "level": "warning",
            "enabled": 1,
        }
        for index, message in enumerate(notices)
    ]

    return _json_response({"ok": True, "items": items})


@router.get("/app/dispatch", response_class=HTMLResponse)
def dispatch_mobile_app_page(request: _Request):
    user = _employee_current_user_from_request(request)

    if not user:
        return RedirectResponse("/employee/login?next=/app/dispatch", status_code=303)

    employee_display_name = _safe_text(user.get("display_name")).strip() or _safe_text(user.get("staff_code")).strip() or "\u767b\u5165\u8005"
    employee_department = _safe_text(user.get("department")).strip()
    employee_role = _safe_text(user.get("role")).strip()

    html = """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

  <title>訊南派工系統｜訊南 ERP</title>

  <link rel="stylesheet" href="/static/app_common.css">
  <link rel="stylesheet" href="/static/dispatch_app.css?v=cl15l4_20260515_024129">

  <link rel="stylesheet" href="/static/app_header_unified.css?v=20260511_title_v1">

  <style id="cl15l4_dispatch_action_button_inline_final_v1">
    body .workflow-detail-actions {
      display: grid !important;
      gap: 12px !important;
    }

    body .workflow-detail-actions .action-row {
      display: grid !important;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
      gap: 12px !important;
      align-items: center !important;
    }

    body .workflow-detail-actions .action-row.single-full {
      grid-template-columns: 1fr !important;
    }

    body .workflow-detail-actions button.action-btn {
      width: 100% !important;
      min-height: 62px !important;
      border: 0 !important;
      border-radius: 22px !important;
      font-size: 20px !important;
      font-weight: 1000 !important;
      letter-spacing: 1px !important;
      opacity: 1 !important;
      filter: none !important;
      background-image: none !important;
      box-shadow: 0 10px 22px rgba(15, 23, 42, 0.12) !important;
      text-shadow: none !important;
    }

    body .workflow-detail-actions button.action-btn.dial-btn {
      background: #8b5e34 !important;
      color: #ffffff !important;
    }

    body .workflow-detail-actions button.action-btn.nav-btn {
      background: #e47a24 !important;
      color: #ffffff !important;
    }

    body .workflow-detail-actions button.action-btn.claim-btn,
    body .workflow-detail-actions button.action-btn.claim-btn:disabled {
      background: #0f3d2e !important;
      color: #ffffff !important;
      opacity: 1 !important;
      filter: none !important;
      cursor: pointer !important;
    }

    body .workflow-detail-actions button.action-btn.claim-btn:disabled {
      cursor: not-allowed !important;
    }

    body .workflow-detail-actions button.action-btn.transfer-btn {
      background: #f2c94c !important;
      color: #3b2f00 !important;
    }

    body .workflow-detail-actions button.action-btn.list-btn {
      background: #475569 !important;
      color: #ffffff !important;
    }

    body .workflow-detail-actions button.action-btn.action-next-blue,
    body .workflow-detail-actions button.action-btn.next-btn {
      background: #365ee8 !important;
      color: #ffffff !important;
      width: 100% !important;
      margin: 0 !important;
      justify-self: auto !important;
    }

    body .workflow-detail-actions button.action-btn.transfer-return-btn {
      background: #b83a2f !important;
      color: #ffffff !important;
    }

    body .workflow-detail-actions button.action-btn:active {
      transform: translateY(1px) scale(0.99) !important;
      filter: brightness(0.96) !important;
    }

    @media (max-width: 520px) {
      body .workflow-detail-actions {
        gap: 10px !important;
      }

      body .workflow-detail-actions .action-row {
        gap: 10px !important;
      }

      body .workflow-detail-actions button.action-btn {
        min-height: 56px !important;
        border-radius: 18px !important;
        font-size: 18px !important;
      }
    }
  </style>


  <style id="cl15l5_dispatch_button_color_tune_v1">
    body .workflow-detail-actions button.action-btn.claim-btn,
    body .workflow-detail-actions button.action-btn.claim-btn:disabled {
      background: #15803d !important;
      color: #ffffff !important;
      opacity: 1 !important;
      filter: none !important;
    }

    body .workflow-detail-actions button.action-btn.transfer-btn {
      background: #f2c94c !important;
      color: #ffffff !important;
      opacity: 1 !important;
      filter: none !important;
      text-shadow: 0 1px 2px rgba(0,0,0,0.28) !important;
    }
  </style>

</head>

<body>
  <div class="app-shell">
    <section class="hero app-standard-hero">
      <div class="hero-main">
        <span class="hero-logo">
          <img class="hero-logo-img" src="/static/shinnan_home_logo.png" alt="Logo">
        </span>
        <h1 class="hero-title">\u8a0a\u5357\u6d3e\u5de5\u7cfb\u7d71</h1>
      </div>
      <div class="hero-sub">__EMPLOYEE_DISPLAY_NAME__</div>
    </section>

    <div id="dispatch_proxy_user_banner" class="proxy-user-banner normal"></div>

    <div class="emergency-marquee">
      <div id="emergency_track" class="emergency-track">目前沒有緊急通知</div>
    </div>

    <main class="content">
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-label">今日</div>
          <div id="stat_today" class="stat-value">0</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">進行中</div>
          <div id="stat_active" class="stat-value">0</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">全部</div>
          <div id="stat_total" class="stat-value">0</div>
        </div>
      </div>

      <div class="filter-row">
        <button class="chip active" data-filter="全部">全部</button>
        <button class="chip" data-filter="今日">今日</button>
        <button class="chip" data-filter="未領用">未領用</button>
        <button class="chip" data-filter="已領用">已領用</button>
        <button class="chip" data-filter="已完成">已完成</button>
      </div>

      <input id="keyword" class="search" placeholder="搜尋客戶、電話、地址、案件類型">

      
      <select id="area_filter" class="area-select">
        <option value="&#x5168;&#x90E8;">&#x5168;&#x90E8;&#x5340;&#x57DF;</option>
      </select>
<div id="section_title" class="section-title">派工案件整理中...</div>
      <section id="list" class="list"></section>

      <!-- XN_APP_WORKFLOW_PAGES_HTML_V1 -->
      <section id="ticket_detail_page" class="work-page">
        <div id="ticket_detail_content"></div>
      </section>

      <section id="ticket_finish_page" class="work-page">
        <div id="ticket_finish_content"></div>
      </section>

      <!-- XN_APP_CREATE_PAGE_HTML_V1 -->
      <section id="ticket_create_page" class="work-page">
        <div id="ticket_create_content"></div>
      </section>
      <!-- XN_APP_CREATE_PAGE_HTML_V1_END -->
      <!-- XN_APP_WORKFLOW_PAGES_HTML_V1_END -->
    </main>

    <nav class="bottom-nav">
      <button onclick="location.href='/app'">APP首頁</button>
      <button onclick="loadEmergencyNotices(); loadTickets();">整理</button>
      <button class="primary" onclick="showCreatePage()">新增</button>
      <button class="danger" onclick="location.href='/employee/logout?next=/'">登出</button>
    </nav>
  </div>

  <script src="/static/dispatch_app.js?v=cl15l4_20260515_024129"></script>

  <script src="/static/app_header_actions.js?v=cl17p3"></script>
</body>
</html>
"""
    return (
        html
        .replace("__EMPLOYEE_DISPLAY_NAME__", employee_display_name)
        .replace("__EMPLOYEE_ROLE__", employee_role)
    )
# SHINNAN_DISPATCH_MOBILE_APP_END
