from __future__ import annotations

import json as _billing_json
import hashlib as _billing_hashlib
from datetime import datetime as _billing_datetime
from datetime import timedelta as _billing_timedelta
from html import escape as _billing_escape
from pathlib import Path as _BillingPath

from fastapi import APIRouter
from fastapi import Request as _EmpRequest
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse as _EmpRedirectResponse
from fastapi.responses import Response as _BillingResponse
from sqlalchemy import text as _billing_sql_text

from app.db import engine as _billing_engine
from app.routes.employee_auth import _employee_current_user_from_request


router = APIRouter(tags=["手機帳務 APP"])




def _billing_table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        _billing_sql_text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table_name},
    ).fetchone()
    return row is not None


def _billing_table_columns(conn, table_name: str) -> set[str]:
    if not _billing_table_exists(conn, table_name):
        return set()

    return {
        row[1]
        for row in conn.execute(_billing_sql_text(f"PRAGMA table_info({table_name})")).fetchall()
    }


def _billing_pick_column(columns: set[str], candidates: list[str]) -> str | None:
    for name in candidates:
        if name in columns:
            return name
    return None


def _billing_staff_pool_for_assignment(current_user: dict) -> list[dict]:
    fallback = {
        "staff_code": str(current_user.get("staff_code", "") or "admin"),
        "display_name": str(current_user.get("display_name", "") or "系統管理員"),
        "department": str(current_user.get("department", "") or ""),
        "role": str(current_user.get("role", "") or ""),
        "position_title": str(current_user.get("position_title", "") or ""),
    }

    with _billing_engine.begin() as conn:
        profile_exists = _billing_table_exists(conn, "employee_profiles")
        account_exists = _billing_table_exists(conn, "employee_accounts")

        if not profile_exists and not account_exists:
            return [fallback]

        profile_cols = _billing_table_columns(conn, "employee_profiles") if profile_exists else set()
        account_cols = _billing_table_columns(conn, "employee_accounts") if account_exists else set()

        p_staff = _billing_pick_column(profile_cols, ["staff_code", "employee_code", "username", "account", "login_id"])
        p_name = _billing_pick_column(profile_cols, ["display_name", "employee_name", "name", "full_name"])
        p_dept = _billing_pick_column(profile_cols, ["department", "department_name", "dept"])
        p_role = _billing_pick_column(profile_cols, ["role", "permission_role", "account_role"])
        p_pos = _billing_pick_column(profile_cols, ["position_title", "position", "job_title", "title"])
        p_status = _billing_pick_column(profile_cols, ["employment_status", "status"])

        a_staff = _billing_pick_column(account_cols, ["staff_code", "employee_code", "username", "account", "login_id"])
        a_name = _billing_pick_column(account_cols, ["display_name", "employee_name", "name", "full_name"])
        a_role = _billing_pick_column(account_cols, ["role", "permission_role", "account_role"])
        a_enabled = _billing_pick_column(account_cols, ["enabled", "active", "is_active"])

        rows = []

        if profile_exists and p_staff:
            join_sql = ""
            select_parts = [
                f"p.{p_staff} AS staff_code",
                f"p.{p_name} AS display_name" if p_name else "'' AS display_name",
                f"p.{p_dept} AS department" if p_dept else "'' AS department",
                f"p.{p_role} AS role" if p_role else "'' AS role",
                f"p.{p_pos} AS position_title" if p_pos else "'' AS position_title",
                f"p.{p_status} AS employment_status" if p_status else "'在職' AS employment_status",
            ]

            if account_exists and a_staff:
                join_sql = f" LEFT JOIN employee_accounts a ON a.{a_staff} = p.{p_staff} "
                if not p_role and a_role:
                    select_parts[3] = f"a.{a_role} AS role"
                if not p_name and a_name:
                    select_parts[1] = f"a.{a_name} AS display_name"
                if a_enabled:
                    select_parts.append(f"a.{a_enabled} AS account_enabled")
                else:
                    select_parts.append("1 AS account_enabled")
            else:
                select_parts.append("1 AS account_enabled")

            sql = f"""
                SELECT
                    {", ".join(select_parts)}
                FROM employee_profiles p
                {join_sql}
            """

            rows = [dict(row) for row in conn.execute(_billing_sql_text(sql)).mappings().fetchall()]

        elif account_exists and a_staff:
            select_parts = [
                f"a.{a_staff} AS staff_code",
                f"a.{a_name} AS display_name" if a_name else f"a.{a_staff} AS display_name",
                "'' AS department",
                f"a.{a_role} AS role" if a_role else "'' AS role",
                "'' AS position_title",
                "'在職' AS employment_status",
                f"a.{a_enabled} AS account_enabled" if a_enabled else "1 AS account_enabled",
            ]

            sql = f"""
                SELECT
                    {", ".join(select_parts)}
                FROM employee_accounts a
            """

            rows = [dict(row) for row in conn.execute(_billing_sql_text(sql)).mappings().fetchall()]

    clean = []

    for row in rows:
        staff_code = str(row.get("staff_code", "") or "").strip()
        display_name = str(row.get("display_name", "") or "").strip()
        department = str(row.get("department", "") or "").strip()
        role = str(row.get("role", "") or "").strip()
        position_title = str(row.get("position_title", "") or "").strip()
        employment_status = str(row.get("employment_status", "") or "").strip()
        account_enabled = str(row.get("account_enabled", "1") if row.get("account_enabled", "1") is not None else "1").strip()

        if not staff_code and not display_name:
            continue

        if not display_name:
            display_name = staff_code

        if employment_status and employment_status not in ("在職", "啟用", "正常", "active", "Active", "ACTIVE"):
            continue

        if account_enabled in ("0", "False", "false", "停用", "disabled", "Disabled"):
            continue

        clean.append({
            "staff_code": staff_code,
            "display_name": display_name,
            "department": department,
            "role": role,
            "position_title": position_title,
        })

    if not clean:
        return [fallback]

    billing_keywords = ("帳務", "會計", "billing", "accounting", "accountant")

    billing_people = []
    for item in clean:
        haystack = " ".join([
            str(item.get("department", "") or ""),
            str(item.get("role", "") or ""),
            str(item.get("position_title", "") or ""),
            str(item.get("display_name", "") or ""),
        ]).lower()

        if any(keyword.lower() in haystack for keyword in billing_keywords):
            billing_people.append(item)

    if billing_people:
        return sorted(billing_people, key=lambda x: (x.get("department", ""), x.get("display_name", ""), x.get("staff_code", "")))

    # 若目前尚未建立帳務員職務資料，先退回所有在職員工，方便測試分配效果。
    return sorted(clean, key=lambda x: (x.get("department", ""), x.get("display_name", ""), x.get("staff_code", "")))


def _billing_assigned_staff_for_building(area: str, building_no: str, building_name: str, current_user: dict) -> dict:
    staff_pool = _billing_staff_pool_for_assignment(current_user)

    if not staff_pool:
        return {
            "staff_code": str(current_user.get("staff_code", "") or ""),
            "display_name": str(current_user.get("display_name", "") or "系統管理員"),
            "department": str(current_user.get("department", "") or ""),
            "role": str(current_user.get("role", "") or ""),
            "position_title": str(current_user.get("position_title", "") or ""),
        }

    # 按區 + 大樓做穩定隨機，同一區內不同大樓會分散，但每次重新整理不會亂跳。
    seed = f"{area}|{building_no}|{building_name}"
    digest = _billing_hashlib.sha256(seed.encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(staff_pool)

    return staff_pool[index]



def _billing_current_roc_month() -> str:
    now = _billing_datetime.now()
    roc_year = now.year - 1911
    return f"{roc_year}{now.month:02d}"


def _billing_is_paid(record: dict) -> bool:
    text = str(record.get("payment_status", "") or "")
    if "未繳" in text or "逾期" in text or "異常" in text:
        return False
    if "已繳" in text or "正常" in text or "繳費正常" in text:
        return True
    return False


def _billing_is_delivered(record: dict) -> bool:
    for key in ("bill_delivered", "is_delivered", "delivered"):
        value = record.get(key)
        if value in (1, True, "1", "true", "True", "已發放", "是"):
            return True

    status = str(record.get("delivery_status", "") or record.get("bill_status", "") or "")
    if "已發" in status or "已送" in status:
        return True

    if str(record.get("delivered_at", "") or "").strip():
        return True

    return False




def _billing_is_overdue_unpaid(record: dict) -> bool:
    status = str(record.get("payment_status", "") or "")

    if "已繳" in status or "繳費正常" in status:
        return False

    due_text = str(record.get("billing_due_date", "") or record.get("due_date", "") or "").strip()
    if not due_text:
        return False

    try:
        due_date = _billing_datetime.fromisoformat(due_text[:10]).date()
        overdue_start_date = due_date + _billing_timedelta(days=20)
        today = _billing_datetime.now().date()
        return overdue_start_date <= today
    except Exception:
        return False


def _billing_visible_for_user(record: dict, user: dict) -> bool:
    role = str(user.get("role", "") or "")
    staff_code = str(user.get("staff_code", "") or "")

    if role == "admin" or staff_code == "admin":
        return True

    for key in ("assigned_staff_code", "billing_staff_code", "collector_staff_code", "owner_staff_code"):
        assigned = str(record.get(key, "") or "")
        if assigned and assigned == staff_code:
            return True

    # 目前 demo 帳務資料尚未有帳務員指派欄位。
    # 為了先呈現「不同登入人員看到不同資料」的效果，
    # 非 admin 先用 building_no 做穩定分流；之後會改成 /admin/billing 的正式指派資料。
    building_no = str(record.get("building_no", "") or record.get("building_name", "") or "")
    if not staff_code or not building_no:
        return True

    bucket = sum(ord(ch) for ch in building_no) % 3
    user_bucket = sum(ord(ch) for ch in staff_code) % 3
    return bucket == user_bucket



def _billing_build_monthly_building_summary(user: dict) -> dict:
    today_date = _billing_datetime.now().date()
    today_text = today_date.strftime("%Y-%m-%d")
    current_month_ad = _billing_datetime.now().strftime("%Y-%m")
    current_month_roc = _billing_current_roc_month()

    role = str(user.get("role", "") or "")
    staff_code = str(user.get("staff_code", "") or "")

    # 應發帳單規則：
    # 1. 到期日前 15 天開始列入
    # 2. 到期後 20 天尚未繳費則不再留在應發清單，而歸到逾期未繳清單
    where_parts = [
        "COALESCE(c.billing_due_date, '') <> ''",
        "date(c.billing_due_date, '-15 day') <= date(:today)",
        "date(c.billing_due_date, '+20 day') > date(:today)",
    ]

    params = {
        "today": today_text,
        "month_ad": current_month_ad,
        "month_roc": current_month_roc,
        "staff_code": staff_code,
    }

    with _billing_engine.begin() as conn:
        customer_cols = {
            row[1]
            for row in conn.execute(_billing_sql_text("PRAGMA table_info(customer_accounts)")).fetchall()
        }

        buildings_exists = conn.execute(
            _billing_sql_text("SELECT name FROM sqlite_master WHERE type='table' AND name='buildings'")
        ).fetchone() is not None

        if role != "admin" and staff_code != "admin":
            staff_filters = []
            for col in ("assigned_staff_code", "billing_staff_code", "collector_staff_code", "owner_staff_code"):
                if col in customer_cols:
                    staff_filters.append(f"COALESCE(c.{col}, '') = :staff_code")

            if staff_filters:
                where_parts.append("(" + " OR ".join(staff_filters) + ")")

        c_building_no = "c.building_no" if "building_no" in customer_cols else "''"
        c_building_name = "c.building_name" if "building_name" in customer_cols else "''"
        c_area = "c.area" if "area" in customer_cols else "''"
        c_customer_no = "c.customer_no" if "customer_no" in customer_cols else "''"
        c_customer_name = "c.customer_name" if "customer_name" in customer_cols else ("c.name" if "name" in customer_cols else "''")
        c_phone = (
            "c.customer_phone" if "customer_phone" in customer_cols else
            ("c.contact_phone" if "contact_phone" in customer_cols else
            ("c.phone" if "phone" in customer_cols else
            ("c.mobile" if "mobile" in customer_cols else
            ("c.cellphone" if "cellphone" in customer_cols else
            ("c.tel" if "tel" in customer_cols else "''")))))
        )
        c_address = "COALESCE(c.room_no, c.floor_text)" if "room_no" in customer_cols else ("c.install_address" if "install_address" in customer_cols else ("c.service_address" if "service_address" in customer_cols else "''"))
        c_billing_month = "c.billing_month" if "billing_month" in customer_cols else "''"
        c_billing_due_date = "c.billing_due_date" if "billing_due_date" in customer_cols else "''"
        c_billing_amount = "c.billing_amount" if "billing_amount" in customer_cols else ("c.monthly_fee" if "monthly_fee" in customer_cols else "0")
        c_payment_status = "c.payment_status" if "payment_status" in customer_cols else ("c.arrears_status" if "arrears_status" in customer_cols else "''")
        c_bill_delivery_status = "c.bill_delivery_status" if "bill_delivery_status" in customer_cols else "''"
        c_bill_delivered = "c.bill_delivered" if "bill_delivered" in customer_cols else "0"

        if "billing_due_date" not in customer_cols:
            where_parts = ["1 = 1"]
            if "payment_status" in customer_cols:
                where_parts.append("COALESCE(c.payment_status, '') NOT LIKE '%停用%'")

        join_sql = ""
        b_name_expr = "''"
        b_area_expr = "''"

        if buildings_exists and "building_no" in customer_cols:
            building_cols = {
                row[1]
                for row in conn.execute(_billing_sql_text("PRAGMA table_info(buildings)")).fetchall()
            }

            if "building_no" in building_cols:
                join_sql = "LEFT JOIN buildings b ON b.building_no = c.building_no"
                b_name_expr = "b.name" if "name" in building_cols else ("b.building_name" if "building_name" in building_cols else "''")
                b_area_expr = "b.area" if "area" in building_cols else "''"

        sql = f"""
            SELECT
                c.rowid AS row_key,
                {c_customer_no} AS customer_no,
                {c_customer_name} AS customer_name,
                {c_phone} AS phone,
                {c_address} AS install_address,
                {c_building_no} AS building_no,
                COALESCE({b_name_expr}, {c_building_name}, {c_building_no}, '未命名大樓') AS building_name,
                COALESCE({b_area_expr}, {c_area}, '') AS area,
                COALESCE({c_billing_month}, '') AS billing_month,
                COALESCE({c_billing_due_date}, '') AS billing_due_date,
                COALESCE({c_billing_amount}, 0) AS total_amount,
                COALESCE({c_payment_status}, '') AS payment_status,
                COALESCE({c_bill_delivery_status}, '') AS bill_delivery_status,
                COALESCE({c_bill_delivered}, 0) AS bill_delivered
            FROM customer_accounts c
            {join_sql}
            WHERE {" AND ".join(where_parts)}
            ORDER BY
                area,
                building_name,
                row_key
        """

        rows = conn.execute(_billing_sql_text(sql), params).mappings().fetchall()

    grouped: dict[str, dict] = {}

    for row in rows:
        item = dict(row)
        building_no = str(item.get("building_no", "") or "")
        building_name = str(item.get("building_name", "") or "未命名大樓")
        key = building_no or building_name

        if key not in grouped:
            area_text = str(item.get("area", "") or "")
            assigned_staff = _billing_assigned_staff_for_building(
                area_text,
                building_no,
                building_name,
                user,
            )

            grouped[key] = {
                "building_no": building_no,
                "building_name": building_name,
                "area": area_text,
                "billing_staff_code": assigned_staff.get("staff_code", ""),
                "billing_staff_name": assigned_staff.get("display_name", ""),
                "billing_staff_department": assigned_staff.get("department", ""),
                "billing_staff_role": assigned_staff.get("role", ""),
                "billing_staff_position_title": assigned_staff.get("position_title", ""),
                "bill_count": 0,
                "delivered_count": 0,
                "not_delivered_count": 0,
                "paid_count": 0,
                "unpaid_count": 0,
                "overdue_unpaid_count": 0,
                "total_amount": 0,
                "records": [],
            }

        g = grouped[key]
        amount = float(item.get("total_amount", 0) or 0)

        delivered = False
        if item.get("bill_delivered") in (1, True, "1", "true", "True"):
            delivered = True
        if "已發" in str(item.get("bill_delivery_status", "") or ""):
            delivered = True

        paid = _billing_is_paid(item)

        g["bill_count"] += 1
        g["total_amount"] += amount

        if delivered:
            g["delivered_count"] += 1
        else:
            g["not_delivered_count"] += 1

        if paid:
            g["paid_count"] += 1
        else:
            g["unpaid_count"] += 1

        g["records"].append({
            "customer_no": item.get("customer_no", ""),
            "customer_name": item.get("customer_name", ""),
            "phone": item.get("phone", ""),
            "install_address": item.get("install_address", ""),
            "billing_month": item.get("billing_month", ""),
            "billing_due_date": item.get("billing_due_date", ""),
            "total_amount": amount,
            "payment_status": item.get("payment_status", ""),
            "bill_delivery_status": item.get("bill_delivery_status", ""),
            "delivered": delivered,
            "paid": paid,
            "overdue_unpaid": False,
        })

    # 逾期未繳規則：
    # 到期日 + 20 天 <= 今天 且不是已繳。
    # 這裡另外計算每棟大樓逾期數，因為應發清單不包含已滿 20 天逾期的舊帳單。
    total_overdue_count = 0

    with _billing_engine.begin() as conn:
        customer_cols_for_overdue = {
            row[1]
            for row in conn.execute(_billing_sql_text("PRAGMA table_info(customer_accounts)")).fetchall()
        }

        buildings_exists_for_overdue = conn.execute(
            _billing_sql_text("SELECT name FROM sqlite_master WHERE type='table' AND name='buildings'")
        ).fetchone() is not None

        if "billing_due_date" in customer_cols_for_overdue:
            payment_status_expr_for_overdue = (
                "c.payment_status"
                if "payment_status" in customer_cols_for_overdue
                else ("c.arrears_status" if "arrears_status" in customer_cols_for_overdue else "''")
            )
            overdue_where_parts = [
                "COALESCE(c.billing_due_date, '') <> ''",
                "date(c.billing_due_date, '+20 day') <= date(:today)",
                f"COALESCE({payment_status_expr_for_overdue}, '') NOT LIKE '%已繳%'",
            ]
        else:
            overdue_candidates = []
            if "is_overdue" in customer_cols_for_overdue:
                overdue_candidates.append("COALESCE(c.is_overdue, 0) = 1")
            if "arrears_months" in customer_cols_for_overdue:
                overdue_candidates.append("COALESCE(c.arrears_months, 0) > 0")
            if "payment_status" in customer_cols_for_overdue:
                overdue_candidates.append("COALESCE(c.payment_status, '') NOT LIKE '%已繳%'")
            if "arrears_status" in customer_cols_for_overdue:
                overdue_candidates.append("COALESCE(c.arrears_status, '') <> ''")
            overdue_where_parts = ["(" + " OR ".join(overdue_candidates or ["1 = 0"]) + ")"]

        overdue_params = {
            "today": today_text,
            "staff_code": staff_code,
        }

        if role != "admin" and staff_code != "admin":
            staff_filters = []
            for col in ("assigned_staff_code", "billing_staff_code", "collector_staff_code", "owner_staff_code"):
                if col in customer_cols_for_overdue:
                    staff_filters.append(f"COALESCE(c.{col}, '') = :staff_code")

            if staff_filters:
                overdue_where_parts.append("(" + " OR ".join(staff_filters) + ")")

        c_building_no_for_overdue = "c.building_no" if "building_no" in customer_cols_for_overdue else "''"
        c_building_name_for_overdue = "c.building_name" if "building_name" in customer_cols_for_overdue else "''"
        c_area_for_overdue = "c.area" if "area" in customer_cols_for_overdue else "''"

        overdue_join_sql = ""
        b_name_expr_for_overdue = "''"
        b_area_expr_for_overdue = "''"

        if buildings_exists_for_overdue and "building_no" in customer_cols_for_overdue:
            building_cols_for_overdue = {
                row[1]
                for row in conn.execute(_billing_sql_text("PRAGMA table_info(buildings)")).fetchall()
            }

            if "building_no" in building_cols_for_overdue:
                overdue_join_sql = "LEFT JOIN buildings b ON b.building_no = c.building_no"
                b_name_expr_for_overdue = "b.name" if "name" in building_cols_for_overdue else ("b.building_name" if "building_name" in building_cols_for_overdue else "''")
                b_area_expr_for_overdue = "b.area" if "area" in building_cols_for_overdue else "''"

        overdue_sql = f"""
            SELECT
                {c_building_no_for_overdue} AS building_no,
                COALESCE({b_name_expr_for_overdue}, {c_building_name_for_overdue}, {c_building_no_for_overdue}, '未命名大樓') AS building_name,
                COALESCE({b_area_expr_for_overdue}, {c_area_for_overdue}, '') AS area,
                COUNT(*) AS overdue_unpaid_count
            FROM customer_accounts c
            {overdue_join_sql}
            WHERE {" AND ".join(overdue_where_parts)}
            GROUP BY
                {c_building_no_for_overdue},
                building_name,
                COALESCE({b_area_expr_for_overdue}, {c_area_for_overdue}, '')
        """

        overdue_rows = conn.execute(
            _billing_sql_text(overdue_sql),
            overdue_params,
        ).mappings().fetchall()

    for overdue_row in overdue_rows:
        building_no = str(overdue_row.get("building_no", "") or "")
        building_name = str(overdue_row.get("building_name", "") or "未命名大樓")
        key = building_no or building_name
        overdue_count = int(overdue_row.get("overdue_unpaid_count", 0) or 0)

        total_overdue_count += overdue_count

        if key in grouped:
            grouped[key]["overdue_unpaid_count"] = overdue_count

    buildings = sorted(
        grouped.values(),
        key=lambda x: (str(x.get("area", "")), str(x.get("building_name", ""))),
    )

    summary = {
        "month": current_month_ad,
        "rule": "issue_from_due_date_minus_15_until_due_date_plus_19",
        "rule_label": "到期日前 15 天開始發帳單；到期後 20 天未繳轉逾期",
        "overdue_rule": "due_date_plus_20_days",
        "overdue_rule_label": "到期後 20 天未繳才列入逾期",
        "building_count": len(buildings),
        "bill_count": sum(int(x["bill_count"]) for x in buildings),
        "delivered_count": sum(int(x["delivered_count"]) for x in buildings),
        "not_delivered_count": sum(int(x["not_delivered_count"]) for x in buildings),
        "paid_count": sum(int(x["paid_count"]) for x in buildings),
        "unpaid_count": sum(int(x["unpaid_count"]) for x in buildings),
        "overdue_unpaid_count": total_overdue_count,
        "total_amount": sum(float(x["total_amount"]) for x in buildings),
    }

    return {
        "summary": summary,
        "items": buildings,
    }


@router.get("/api/app/billing/monthly-buildings", summary="手機帳務 APP 讀取應發大樓帳單總覽")
def api_app_billing_monthly_buildings(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _BillingResponse(
            content=_billing_json.dumps(
                {"ok": False, "error": "login required"},
                ensure_ascii=False,
            ),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    result = _billing_build_monthly_building_summary(user)

    return _BillingResponse(
        content=_billing_json.dumps(
            {
                "ok": True,
                "user": {
                    "staff_code": user.get("staff_code", ""),
                    "display_name": user.get("display_name", ""),
                    "department": user.get("department", ""),
                    "role": user.get("role", ""),
                },
                "summary": result["summary"],
                "items": result["items"],
            },
            ensure_ascii=False,
        ),
        media_type="application/json; charset=utf-8",
    )




@router.get("/api/app/billing/overdue-customers", summary="手機帳務 APP 讀取逾期未繳客戶")
def api_app_billing_overdue_customers(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _BillingResponse(
            content=_billing_json.dumps(
                {"ok": False, "error": "login required"},
                ensure_ascii=False,
            ),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    today_text = _billing_datetime.now().strftime("%Y-%m-%d")
    role = str(user.get("role", "") or "")
    staff_code = str(user.get("staff_code", "") or "")

    with _billing_engine.begin() as conn:
        customer_cols = {
            row[1]
            for row in conn.execute(_billing_sql_text("PRAGMA table_info(customer_accounts)")).fetchall()
        }

        buildings_exists = conn.execute(
            _billing_sql_text("SELECT name FROM sqlite_master WHERE type='table' AND name='buildings'")
        ).fetchone() is not None

        where_parts = [
            "COALESCE(c.billing_due_date, '') <> ''",
            "date(c.billing_due_date, '+20 day') <= date(:today)",
            "COALESCE(c.payment_status, '') NOT LIKE '%已繳%'",
        ]

        params = {
            "today": today_text,
            "staff_code": staff_code,
        }

        if role != "admin" and staff_code != "admin":
            staff_filters = []
            for col in ("assigned_staff_code", "billing_staff_code", "collector_staff_code", "owner_staff_code"):
                if col in customer_cols:
                    staff_filters.append(f"COALESCE(c.{col}, '') = :staff_code")

            if staff_filters:
                where_parts.append("(" + " OR ".join(staff_filters) + ")")

        c_building_no = "c.building_no" if "building_no" in customer_cols else "''"
        c_building_name = "c.building_name" if "building_name" in customer_cols else "''"
        c_area = "c.area" if "area" in customer_cols else "''"
        c_customer_no = "c.customer_no" if "customer_no" in customer_cols else "''"
        c_customer_name = "c.customer_name" if "customer_name" in customer_cols else ("c.name" if "name" in customer_cols else "''")
        c_phone = (
            "c.customer_phone" if "customer_phone" in customer_cols else
            ("c.contact_phone" if "contact_phone" in customer_cols else
            ("c.phone" if "phone" in customer_cols else
            ("c.mobile" if "mobile" in customer_cols else
            ("c.cellphone" if "cellphone" in customer_cols else
            ("c.tel" if "tel" in customer_cols else "''")))))
        )
        c_address = "COALESCE(c.room_no, c.floor_text)" if "room_no" in customer_cols else ("c.install_address" if "install_address" in customer_cols else ("c.service_address" if "service_address" in customer_cols else "''"))
        c_billing_month = "c.billing_month" if "billing_month" in customer_cols else "''"
        c_billing_due_date = "c.billing_due_date" if "billing_due_date" in customer_cols else "''"
        c_billing_amount = "c.billing_amount" if "billing_amount" in customer_cols else ("c.monthly_fee" if "monthly_fee" in customer_cols else "0")
        c_payment_status = "c.payment_status" if "payment_status" in customer_cols else ("c.arrears_status" if "arrears_status" in customer_cols else "''")
        c_bill_delivery_status = "c.bill_delivery_status" if "bill_delivery_status" in customer_cols else "''"
        c_bill_delivered = "c.bill_delivered" if "bill_delivered" in customer_cols else "0"

        if "billing_due_date" not in customer_cols:
            where_parts = []
            overdue_candidates = []
            if "is_overdue" in customer_cols:
                overdue_candidates.append("COALESCE(c.is_overdue, 0) = 1")
            if "arrears_months" in customer_cols:
                overdue_candidates.append("COALESCE(c.arrears_months, 0) > 0")
            if "payment_status" in customer_cols:
                overdue_candidates.append("COALESCE(c.payment_status, '') NOT LIKE '%已繳%'")
            where_parts.append("(" + " OR ".join(overdue_candidates or ["1 = 0"]) + ")")

        join_sql = ""
        b_name_expr = "''"
        b_area_expr = "''"

        if buildings_exists and "building_no" in customer_cols:
            building_cols = {
                row[1]
                for row in conn.execute(_billing_sql_text("PRAGMA table_info(buildings)")).fetchall()
            }

            if "building_no" in building_cols:
                join_sql = "LEFT JOIN buildings b ON b.building_no = c.building_no"
                b_name_expr = "b.name" if "name" in building_cols else ("b.building_name" if "building_name" in building_cols else "''")
                b_area_expr = "b.area" if "area" in building_cols else "''"

        sql = f"""
            SELECT
                c.rowid AS row_key,
                {c_customer_no} AS customer_no,
                {c_customer_name} AS customer_name,
                {c_phone} AS phone,
                {c_address} AS install_address,
                {c_building_no} AS building_no,
                COALESCE({b_name_expr}, {c_building_name}, {c_building_no}, '未命名大樓') AS building_name,
                COALESCE({b_area_expr}, {c_area}, '') AS area,
                COALESCE({c_billing_month}, '') AS billing_month,
                COALESCE({c_billing_due_date}, '') AS billing_due_date,
                COALESCE({c_billing_amount}, 0) AS billing_amount,
                COALESCE({c_payment_status}, '') AS payment_status,
                COALESCE({c_bill_delivery_status}, '') AS bill_delivery_status,
                COALESCE({c_bill_delivered}, 0) AS bill_delivered
            FROM customer_accounts c
            {join_sql}
            WHERE {" AND ".join(where_parts)}
            ORDER BY
                billing_due_date ASC,
                area ASC,
                building_name ASC,
                row_key ASC
        """

        rows = conn.execute(_billing_sql_text(sql), params).mappings().fetchall()

    items = []
    for row in rows:
        item = dict(row)

        assigned_staff = _billing_assigned_staff_for_building(
            str(item.get("area", "") or ""),
            str(item.get("building_no", "") or ""),
            str(item.get("building_name", "") or ""),
            user,
        )

        item["billing_staff_code"] = assigned_staff.get("staff_code", "")
        item["billing_staff_name"] = assigned_staff.get("display_name", "")
        item["billing_staff_department"] = assigned_staff.get("department", "")
        item["billing_staff_role"] = assigned_staff.get("role", "")
        item["billing_staff_position_title"] = assigned_staff.get("position_title", "")

        items.append(item)

    return _BillingResponse(
        content=_billing_json.dumps(
            {
                "ok": True,
                "user": {
                    "staff_code": user.get("staff_code", ""),
                    "display_name": user.get("display_name", ""),
                    "department": user.get("department", ""),
                    "role": user.get("role", ""),
                },
                "count": len(items),
                "items": items,
            },
            ensure_ascii=False,
        ),
        media_type="application/json; charset=utf-8",
    )



@router.get("/api/app/billing/tasks", summary="手機帳務 APP 讀取帳務任務")
def api_app_billing_tasks(request: _EmpRequest):
    # 保留舊 API 名稱，避免前一版連結失效；內容改回傳應發大樓帳單總覽。
    return api_app_billing_monthly_buildings(request)


@router.get("/app/billing", response_class=HTMLResponse)
def billing_mobile_app_page(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmpRedirectResponse("/employee/login?next=/app/billing", status_code=303)

    employee_display_name = str(user.get("display_name", "") or "")
    employee_role = str(user.get("role", "") or "")
    employee_staff_code = str(user.get("staff_code", "") or "")

    user_line = employee_display_name or employee_staff_code or "\u767b\u5165\u8005"

    html = """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

  <title>訊南帳務系統｜訊南 ERP</title>

  <style>
    * {
      box-sizing: border-box;
    }

    html, body {
      margin: 0;
      min-height: 100%;
      background: #edf2f7;
      color: #102348;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft JhengHei", sans-serif;
    }

    body {
      display: flex;
      justify-content: center;
    }

    .app-shell {
      width: 100%;
      max-width: 430px;
      min-height: 100vh;
      background: #eef4fb;
      padding-bottom: 70px;
    }
    .sub {
      margin-top: 5px;
      color: rgba(255,255,255,.88);
      font-size: 12px;
      font-weight: 850;
    }






    .content {
      padding: 14px 16px 22px;
    }

    .notice {
      margin: 8px 16px 0;
      height: 42px;
      border-radius: 14px;
      border: 1px solid #fdba74;
      background: #fff7ed;
      color: #c2410c;
      overflow: hidden;
      position: relative;
      box-shadow: 0 8px 22px rgba(15, 23, 42, .06);
    }

    .billing-notice-track {
      display: inline-block;
      white-space: nowrap;
      padding-left: 100%;
      line-height: 42px;
      font-size: 21px;
      font-weight: 1000;
      color: #dc2626;
      animation: billingNoticeMarquee 18s linear infinite;
    }

    @keyframes billingNoticeMarquee {
      0% { transform: translateX(0); }
      100% { transform: translateX(-100%); }
    }

    .summary {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr 1fr;
      gap: 10px;
      margin-top: 14px;
    }

    .summary-card {
      min-height: 76px;
      padding: 11px 9px;
      border-radius: 18px;
      border: 1px solid #d7e1ef;
      background: #fff;
      box-shadow: 0 10px 24px rgba(15,23,42,.08);
    }

    .summary-label {
      color: #64748b;
      font-size: 12px;
      font-weight: 1000;
    }

    .summary-value {
      margin-top: 6px;
      color: #102348;
      font-size: 26px;
      line-height: 1;
      font-weight: 1000;
    }

    .summary-card.clickable {
      cursor: pointer;
    }

    .summary-card.active {
      border-color: #fb7185;
      background: #fff1f2;
    }

    .summary-card.active .summary-label,
    .summary-card.active .summary-value {
      color: #be123c;
    }

    .summary-card.overdue-card {
      border-color: #fecdd3;
      background: #fff1f2;
    }

    .summary-card.overdue-card .summary-label,
    .summary-card.overdue-card .summary-value {
      color: #be123c;
    }

    .section-title {
      margin: 18px 4px 10px;
      color: #475569;
      font-size: 14px;
      font-weight: 1000;
    }

    .building-list {
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
    }

    .building-card {
      padding: 10px 12px;
      border-radius: 14px;
      border: 1px solid #d7e1ef;
      background: #fff;
      box-shadow: 0 5px 14px rgba(15, 23, 42, .05);
    }

    .building-head {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
    }

    .building-title-row {
      display: flex;
      align-items: center;
      justify-content: flex-start;
      gap: 12px;
      min-width: 0;
    }

    .building-title {
      color: #102348;
      font-size: 20px;
      font-weight: 1000;
      line-height: 1.25;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .building-staff-inline {
      flex: 0 0 auto;
      color: #6d35e8;
      font-size: 12px;
      font-weight: 1000;
      line-height: 1.25;
      text-align: center;
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 52px;
    }

    .building-area {
      margin-top: 2px;
      color: #64748b;
      font-size: 12px;
      font-weight: 900;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .building-staff {
      display: none;
    }

    .bill-count {
      min-width: 74px;
      height: 42px;
      padding: 0 12px;
      border-radius: 999px;
      background: #e0e7ff;
      color: #3730a3;
      font-size: 20px;
      line-height: 1;
      font-weight: 1000;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      white-space: nowrap;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 6px;
      margin-top: 9px;
    }

    .stat-line {
      padding: 7px 5px;
      border-radius: 10px;
      background: #f8fafc;
      color: #334155;
      font-size: 11px;
      font-weight: 900;
      line-height: 1.2;
      text-align: center;
    }

    .stat-line.overdue {
      background: #fff1f2;
      color: #be123c;
    }

    .stat-line.clickable {
      cursor: pointer;
    }

    .stat-line.clickable:active {
      transform: scale(.98);
    }

    .stat-line strong {
      display: block;
      margin-top: 3px;
      color: #102348;
      font-size: 17px;
      font-weight: 1000;
    }

    .stat-line.overdue strong {
      color: #be123c;
    }

    .customer-list {
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
    }

    .excel-filter-th {
      position: relative;
      cursor: pointer;
      user-select: none;
    }

    .excel-filter-label {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .excel-filter-icon {
      font-size: 11px;
      color: #be123c;
      font-weight: 1000;
    }

    .excel-filter-menu {
      position: fixed;
      z-index: 9999;
      width: 220px;
      max-width: 78vw;
      max-height: 280px;
      overflow-y: auto;
      overflow-x: hidden;
      padding: 8px;
      border: 1px solid #fecdd3;
      border-radius: 12px;
      background: #fff;
      box-shadow: 0 14px 30px rgba(15, 23, 42, .18);
    }

    .excel-filter-option {
      display: block;
      width: 100%;
      min-height: 34px;
      margin: 0 0 4px 0;
      border: 0;
      border-radius: 9px;
      padding: 7px 10px;
      background: #fff;
      color: #102348;
      text-align: left;
      font-size: 13px;
      font-weight: 900;
      cursor: pointer;
      white-space: nowrap;
      box-sizing: border-box;
    }

    .excel-filter-option:hover {
      background: #fff1f2;
      color: #be123c;
    }

    .excel-filter-option.active {
      background: #be123c;
      color: #fff;
    }

    .excel-filter-option:last-child {
      margin-bottom: 0;
    }

    .phone-link {
      color: #2563eb;
      font-weight: 1000;
      text-decoration: none;
      white-space: nowrap;
    }

    .phone-link:active {
      color: #1d4ed8;
    }

    .overdue-table-wrap {
      overflow-x: auto;
      border-radius: 14px;
      border: 1px solid #fecdd3;
      background: #fff;
      box-shadow: 0 5px 14px rgba(15, 23, 42, .05);
    }

    .overdue-table {
      width: 100%;
      border-collapse: collapse;
      min-width: 660px;
      background: #fff;
    }

    .overdue-table th {
      background: #fff1f2;
      color: #be123c;
      font-size: 13px;
      font-weight: 1000;
      text-align: left;
      padding: 10px 9px;
      border-bottom: 1px solid #fecdd3;
      white-space: nowrap;
    }

    .overdue-table td {
      color: #102348;
      font-size: 13px;
      font-weight: 850;
      padding: 10px 9px;
      border-bottom: 1px solid #f1f5f9;
      vertical-align: top;
      white-space: nowrap;
    }

    .overdue-table tr:last-child td {
      border-bottom: 0;
    }

    .overdue-table .amount {
      text-align: right;
      font-weight: 1000;
    }

    .overdue-table .status {
      color: #be123c;
      font-weight: 1000;
    }

    .overdue-return-box {
      margin-top: 12px;
      display: flex;
      justify-content: center;
    }

    .overdue-return-btn {
      width: 180px;
      height: 48px;
      border: 0;
      border-radius: 16px;
      background: #fff;
      color: #102348;
      font-size: 16px;
      font-weight: 1000;
      box-shadow: 0 8px 20px rgba(15, 23, 42, .08);
      cursor: pointer;
    }

    .customer-row {
      padding: 10px 12px;
      border-radius: 14px;
      border: 1px solid #fecdd3;
      background: #fff;
      box-shadow: 0 5px 14px rgba(15, 23, 42, .05);
    }

    .customer-head {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: flex-start;
    }

    .customer-name {
      color: #102348;
      font-size: 17px;
      font-weight: 1000;
      line-height: 1.25;
    }

    .customer-building {
      margin-top: 3px;
      color: #64748b;
      font-size: 12px;
      font-weight: 900;
    }

    .customer-badge {
      flex: 0 0 auto;
      padding: 5px 10px;
      border-radius: 999px;
      background: #fff1f2;
      color: #be123c;
      font-size: 12px;
      font-weight: 1000;
      white-space: nowrap;
    }

    .customer-meta {
      margin-top: 8px;
      color: #334155;
      font-size: 12px;
      font-weight: 850;
      line-height: 1.45;
      white-space: pre-wrap;
    }

    .empty {
      padding: 18px 14px;
      border-radius: 18px;
      border: 1px dashed #cbd5e1;
      background: #fff;
      color: #64748b;
      text-align: center;
      font-size: 14px;
      font-weight: 1000;
    }

    .bottom-nav {
      position: fixed;
      left: 50%;
      bottom: 0;
      transform: translateX(-50%);
      width: 100%;
      max-width: 430px;
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 4px;
      padding: 8px 8px 12px;
      background: rgba(238,244,251,.96);
      border-top: 1px solid #d7e1ef;
      backdrop-filter: blur(10px);
      z-index: 20;
    }

    .bottom-nav button {
      height: 42px;
      min-width: 0;
      border: 0;
      border-radius: 12px;
      background: #fff;
      color: #102348;
      font-size: 11px;
      font-weight: 1000;
      line-height: 1.1;
      padding: 0 2px;
      box-shadow: 0 6px 14px rgba(15, 23, 42, .08);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .bottom-nav button.primary {
      background: #4f63e8;
      color: #fff;
    }

    .bottom-nav button.green {
      background: #16a34a;
      color: #fff;
    }

    .bottom-nav button.orange {
      background: #f97316;
      color: #fff;
    }

    .bottom-nav button.danger {
      background: #cf3b2f;
      color: #fff;
    }
  </style>
  <link rel="stylesheet" href="/static/app_header_unified.css?v=20260511_title_v1">
</head>

<body>
  <div class="app-shell">
    <section class="hero app-standard-hero">
      <div class="hero-main">
        <span class="hero-logo">
          <img class="hero-logo-img" src="/static/shinnan_home_logo.png" alt="Logo">
        </span>
        <h1 class="hero-title">\u8a0a\u5357\u5e33\u52d9\u7cfb\u7d71</h1>
      </div>
      <div class="hero-sub">__EMPLOYEE_DISPLAY_NAME__</div>
    </section>

    <div class="notice">
        <div id="billing_notice_track" class="billing-notice-track">帳務通知讀取中...</div>
      </div>

      <section class="summary">
        <div class="summary-card clickable" onclick="returnToBuildingList()">
          <div class="summary-label">應發大樓</div>
          <div id="building_count" class="summary-value">-</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">應發帳單</div>
          <div id="bill_count" class="summary-value">-</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">已發放</div>
          <div id="delivered_count" class="summary-value">-</div>
        </div>
        <div id="overdue_summary_card" class="summary-card clickable overdue-card" onclick="showOverdueCustomers()">
          <div class="summary-label">逾期未繳</div>
          <div id="overdue_count" class="summary-value">-</div>
        </div>
      </section>

      <div id="section_title" class="section-title">應發大樓帳單清單</div>
      <section id="building_list" class="building-list">
        <div class="empty">資料讀取中...</div>
      </section>
    </main>

    <nav class="bottom-nav">
      <button type="button" class="orange" onclick="alert('介紹費功能下一階段開放')">介紹費</button>
      <button type="button" class="primary" onclick="loadMonthlyBuildings()">整理</button>
      <button type="button" class="green" onclick="alert('回饋金功能下一階段開放')">回饋金</button>
    </nav>
  </div>

  <script>
    let latestMonthlyBuildingData = null;
    let latestOverdueCustomers = [];
    let currentBillingViewMode = "buildings";
    let currentOverdueBuildingFilter = "全部";
    const CURRENT_BILLING_STAFF_NAME = "__EMPLOYEE_DISPLAY_NAME__";

    function escapeHtml(value) {
      return String(value == null ? "" : value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }


    function escapeAttr(value) {
      return escapeHtml(value).replaceAll('"', "&quot;");
    }

    function normalizePhoneForTel(value) {
      return String(value == null ? "" : value).replace(/[^\\d+]/g, "");
    }

    function renderPhoneLink(value) {
      const raw = String(value == null ? "" : value).trim();
      const tel = normalizePhoneForTel(raw);

      if (!raw || !tel) {
        return "-";
      }

      return `<a class="phone-link" href="tel:${escapeHtml(tel)}">${escapeHtml(raw)}</a>`;
    }


    function buildBuildingFilterMenu(buildingOptions) {
      return `
        <div id="building_filter_menu" class="excel-filter-menu" style="display:none;">
          ${buildingOptions.map(function(name) {
            const active = name === currentOverdueBuildingFilter ? " active" : "";
            return `<button type="button" class="excel-filter-option${active}" onclick="setOverdueBuildingFilter('${escapeAttr(name)}'); event.stopPropagation();">${escapeHtml(name)}</button>`;
          }).join("")}
        </div>
      `;
    }

    function toggleBuildingFilterMenu(event) {
      if (event) event.stopPropagation();

      const menu = document.getElementById("building_filter_menu");
      if (!menu) return;

      const th = event && event.currentTarget ? event.currentTarget : null;
      const rect = th ? th.getBoundingClientRect() : {left: 20, bottom: 120};

      const isOpen = menu.style.display === "block";

      if (isOpen) {
        menu.style.display = "none";
        return;
      }

      menu.style.left = Math.max(8, Math.min(rect.left, window.innerWidth - 230)) + "px";
      menu.style.top = (rect.bottom + 4) + "px";
      menu.style.display = "block";
    }

    document.addEventListener("click", function() {
      const menu = document.getElementById("building_filter_menu");
      if (menu) {
        menu.style.display = "none";
      }
    });


    function getOverdueBuildingOptions(items) {
      const names = [];
      const seen = new Set();

      (Array.isArray(items) ? items : []).forEach(function(item) {
        const name = item.building_name || "未命名大樓";
        if (!seen.has(name)) {
          seen.add(name);
          names.push(name);
        }
      });

      names.sort();
      return ["全部"].concat(names);
    }

    function setOverdueBuildingFilter(name) {
      currentOverdueBuildingFilter = name || "全部";
      renderOverdueCustomers(latestOverdueCustomers || []);

      const menu = document.getElementById("building_filter_menu");
      if (menu) {
        menu.style.display = "none";
      }
    }


    function setText(id, value) {
      const box = document.getElementById(id);
      if (box) box.textContent = value;
    }

    function renderMonthlyBuildings(data) {
      latestMonthlyBuildingData = data || {};
      currentBillingViewMode = "buildings";

      const summary = data.summary || {};
      const items = Array.isArray(data.items) ? data.items : [];
      const list = document.getElementById("building_list");
      const title = document.getElementById("section_title");
      const overdueCard = document.getElementById("overdue_summary_card");

      if (overdueCard) overdueCard.classList.remove("active");

      setText("building_count", summary.building_count ?? 0);
      setText("bill_count", summary.bill_count ?? 0);
      setText("delivered_count", summary.delivered_count ?? 0);

      if (title) {
        title.textContent = "應發大樓帳單清單｜" + items.length + " 棟";
      }

      if (!list) return;

      list.className = "building-list";

      if (!items.length) {
        list.innerHTML = '<div class="empty">目前沒有已達發放日的帳單。</div>';
        return;
      }

      list.innerHTML = items.map(function(item) {
        return `
          <article class="building-card">
            <div class="building-head">
              <div>
                <div class="building-title-row">
                  <div class="building-title">${escapeHtml(item.building_name || "未命名大樓")}</div>
                  <div class="building-staff-inline">${escapeHtml(item.billing_staff_name || "-")}</div>
                </div>
                <div class="building-area">${escapeHtml(item.area || "-")}｜${escapeHtml(item.building_no || "-")}</div>
              </div>
              <div class="bill-count">${escapeHtml(item.bill_count || 0)} 張</div>
            </div>

            <div class="stats-grid">
              <div class="stat-line">已發放<strong>${escapeHtml(item.delivered_count || 0)}</strong></div>
              <div class="stat-line">未發放<strong>${escapeHtml(item.not_delivered_count || 0)}</strong></div>
              <div class="stat-line">已繳費<strong>${escapeHtml(item.paid_count || 0)}</strong></div>
              <div class="stat-line">未繳費<strong>${escapeHtml(item.unpaid_count || 0)}</strong></div>
              <div class="stat-line overdue clickable" onclick="showOverdueCustomersForBuilding('${escapeAttr(item.building_name || "未命名大樓")}')">逾期未繳<strong>${escapeHtml(item.overdue_unpaid_count || 0)}</strong></div>
            </div>
          </article>
        `;
      }).join("");
    }



    function formatShortDate(value) {
      const raw = String(value == null ? "" : value).trim();

      if (!raw) return "-";

      const m = raw.match(/^(\\d{4})-(\\d{2})-(\\d{2})/);
      if (!m) return raw;

      return m[1].slice(2) + "/" + m[2] + "/" + m[3];
    }

    function renderOverdueCustomers(items) {
      const list = document.getElementById("building_list");
      const title = document.getElementById("section_title");
      const overdueCard = document.getElementById("overdue_summary_card");

      currentBillingViewMode = "overdue";

      if (overdueCard) overdueCard.classList.add("active");

      const allRows = Array.isArray(items) ? items : [];
      const rows = currentOverdueBuildingFilter === "全部"
        ? allRows
        : allRows.filter(function(item) {
            return (item.building_name || "未命名大樓") === currentOverdueBuildingFilter;
          });

      const buildingOptions = getOverdueBuildingOptions(allRows);

      if (title) {
        title.textContent = "逾期未繳客戶清單｜" + rows.length + " 戶";
      }

      if (!list) return;

      list.className = "customer-list";


      if (!rows.length) {
        list.innerHTML = `
          <div class="empty">目前沒有逾期未繳客戶。</div>
          <div class="overdue-return-box">
            <button type="button" class="overdue-return-btn" onclick="returnToBuildingList()">返回</button>
          </div>
        `;
        return;
      }

      const tableRows = rows.map(function(item) {
        return `
          <tr>
            <td>${escapeHtml(item.building_name || "未命名大樓")}</td>
            <td>${escapeHtml(item.install_address || "-")}</td>
            <td>${escapeHtml(item.customer_name || item.customer_no || "-")}</td>
            <td>${renderPhoneLink(item.phone || "")}</td>
            <td>${escapeHtml(formatShortDate(item.billing_due_date || "-"))}</td>
            <td class="amount">${escapeHtml(item.billing_amount == null ? 0 : item.billing_amount)}</td>
          </tr>
        `;
      }).join("");

      list.innerHTML = `
        <div class="overdue-table-wrap">
          <table class="overdue-table">
            <thead>
              <tr>
                <th class="excel-filter-th" onclick="toggleBuildingFilterMenu(event)">
                  <span class="excel-filter-label">大樓 <span class="excel-filter-icon">▼</span></span>
                  ${buildBuildingFilterMenu(buildingOptions)}
                </th>
                <th>地址</th>
                <th>客戶</th>
                <th>電話</th>
                <th>到期日</th>
                <th>金額</th>
              </tr>
            </thead>
            <tbody>
              ${tableRows}
            </tbody>
          </table>
        </div>

        <div class="overdue-return-box">
          <button type="button" class="overdue-return-btn" onclick="returnToBuildingList()">返回</button>
        </div>
      `;
    }

    function returnToBuildingList() {
      currentOverdueBuildingFilter = "全部";

      if (latestMonthlyBuildingData) {
        renderMonthlyBuildings(latestMonthlyBuildingData);
        return;
      }

      loadMonthlyBuildings();
    }

    async function loadOverdueCustomers() {
      try {
        const res = await fetch("/api/app/billing/overdue-customers?ts=" + Date.now(), {
          cache: "no-store",
          credentials: "same-origin"
        });

        if (res.status === 401) {
          location.href = "/employee/login?next=/app/billing";
          return;
        }

        const data = await res.json();
        latestOverdueCustomers = Array.isArray(data.items) ? data.items : [];
        setText("overdue_count", data.count ?? latestOverdueCustomers.length);
      } catch (err) {
        latestOverdueCustomers = [];
        setText("overdue_count", 0);
      }
    }


    async function showOverdueCustomersForBuilding(buildingName) {
      currentOverdueBuildingFilter = buildingName || "全部";

      if (!latestOverdueCustomers.length) {
        await loadOverdueCustomers();
      }

      renderOverdueCustomers(latestOverdueCustomers);
    }

    async function showOverdueCustomers() {
      if (!latestOverdueCustomers.length) {
        await loadOverdueCustomers();
      }
      renderOverdueCustomers(latestOverdueCustomers);
    }

    async function loadBillingNotices() {
      const track = document.getElementById("billing_notice_track");
      if (!track) return;

      try {
        const res = await fetch("/api/app/billing/notices?ts=" + Date.now(), {
          cache: "no-store",
          credentials: "same-origin"
        });

        if (res.status === 401) {
          location.href = "/employee/login?next=/app/billing";
          return;
        }

        const data = await res.json();
        const items = Array.isArray(data.items) ? data.items : [];
        const messages = items
          .map(function(item) { return item.message || ""; })
          .filter(Boolean);

        track.textContent = messages.length
          ? messages.join("　　")
          : "目前沒有帳務通知";
      } catch (err) {
        track.textContent = "帳務通知讀取失敗";
      }
    }


    async function loadMonthlyBuildings() {
      const list = document.getElementById("building_list");
      if (list) {
        list.innerHTML = '<div class="empty">資料讀取中...</div>';
      }

      try {
        const res = await fetch("/api/app/billing/monthly-buildings?ts=" + Date.now(), {
          cache: "no-store",
          credentials: "same-origin"
        });

        if (res.status === 401) {
          location.href = "/employee/login?next=/app/billing";
          return;
        }

        const data = await res.json();

        if (!data.ok) {
          if (list) {
            list.innerHTML = '<div class="empty">資料讀取失敗。</div>';
          }
          return;
        }

        renderMonthlyBuildings(data);
        await loadOverdueCustomers();
      } catch (err) {
        if (list) {
          list.innerHTML = '<div class="empty">資料讀取失敗，請稍後再試。</div>';
        }
      }
    }

    loadBillingNotices();
    loadMonthlyBuildings();
    loadOverdueCustomers();
  </script>

  <script src="/static/app_header_actions.js?v=cl17p6"></script>
</body>
</html>
"""

    return (
        html
        .replace("__EMPLOYEE_DISPLAY_NAME__", _billing_escape(user_line))
    )




