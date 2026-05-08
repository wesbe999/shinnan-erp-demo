from __future__ import annotations

import json as _json
from pathlib import Path as _Path

from fastapi import APIRouter
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


@router.get("/api/app/dispatch/tickets", summary="手機派工 APP 讀取派工案件")
def api_app_dispatch_tickets(request: _Request):
    user = _employee_current_user_from_request(request)

    if not user:
        return _json_response({"ok": False, "error": "login required"}, status_code=401)

    staff_code = _safe_text(user.get("staff_code")).strip()
    staff_name = _safe_text(user.get("display_name")).strip()
    department = _safe_text(user.get("department")).strip()
    role = _safe_text(user.get("role")).strip()

    with engine.begin() as conn:
        ticket_cols = _table_columns(conn, "tickets")
        install_cols = _table_columns(conn, "ticket_install_details")
        return_cols = _table_columns(conn, "ticket_return_details")

        if not ticket_cols:
            return _json_response({
                "ok": False,
                "error": "tickets table not found",
                "items": [],
            }, status_code=500)

        join_install = "LEFT JOIN ticket_install_details i ON i.ticket_id = t.id" if install_cols else ""
        join_return = "LEFT JOIN ticket_return_details r ON r.ticket_id = t.id" if return_cols else ""

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
        },
        "items": items,
    })


@router.get("/api/app/dispatch/emergency-notices", summary="手機派工 APP 讀取緊急通知")
def api_app_dispatch_emergency_notices(request: _Request):
    user = _employee_current_user_from_request(request)

    if not user:
        return _json_response({"ok": False, "error": "login required"}, status_code=401)

    notice_file = _Path("data") / "emergency_notices.json"
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
  <link rel="stylesheet" href="/static/dispatch_app.css">
  <link rel="stylesheet" href="/static/app_header_unified.css?v=20260508_final">

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
      <button onclick="location.href='/app/employee/settings?return_to=/app/dispatch'">員工設定</button>
      <button onclick="loadEmergencyNotices(); loadTickets();">整理</button>
      <button class="primary" onclick="showCreatePage()">新增</button>
      <button class="danger" onclick="location.href='/employee/logout?next=/employee/login'">登出</button>
    </nav>
  </div>

  <script src="/static/dispatch_app.js"></script>
</body>
</html>
"""

    return (
        html
        .replace("__EMPLOYEE_DISPLAY_NAME__", employee_display_name)
        .replace("__EMPLOYEE_ROLE__", employee_role)
    )
# SHINNAN_DISPATCH_MOBILE_APP_END