from __future__ import annotations
import json as _employee_settings_json
from datetime import datetime as _employee_settings_datetime

from fastapi import APIRouter
from fastapi import Request as _EmpRequest
from fastapi.responses import HTMLResponse as _EmployeeSettingsHTMLResponse
from fastapi.responses import Response as _EmployeeSettingsResponse
from fastapi.responses import RedirectResponse as _EmployeeSettingsRedirectResponse
from sqlalchemy import text as _employee_settings_sql_text

from app.db import engine as _employee_settings_engine
from app.routes.employee_auth import _employee_current_user_from_request, _emp_hash_pin

router = APIRouter()



def _calc_annual_leave_days_for_employee_settings(hire_date_text):
    from datetime import date, datetime

    if not hire_date_text:
        return 0

    try:
        hire_date = datetime.strptime(str(hire_date_text)[:10], "%Y-%m-%d").date()
    except Exception:
        return 0

    today = date.today()

    if hire_date > today:
        return 0

    years = today.year - hire_date.year
    if (today.month, today.day) < (hire_date.month, hire_date.day):
        years -= 1

    # 未滿 6 個月
    months = (today.year - hire_date.year) * 12 + today.month - hire_date.month
    if today.day < hire_date.day:
        months -= 1

    if months < 6:
        return 0

    if years < 1:
        return 3
    if years < 2:
        return 7
    if years < 3:
        return 10
    if years < 5:
        return 14
    if years < 10:
        return 15

    return min(30, 15 + (years - 10 + 1))

def _employee_settings_db_init():
    with _employee_settings_engine.begin() as conn:
        conn.execute(_employee_settings_sql_text("""
            CREATE TABLE IF NOT EXISTS employee_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                department TEXT DEFAULT '',
                role TEXT DEFAULT 'employee',
                position_title TEXT DEFAULT '',
                gender TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                employment_status TEXT DEFAULT '在職',
                hire_date TEXT DEFAULT '',
                permission_scope TEXT DEFAULT '',
                app_access TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))

        conn.execute(_employee_settings_sql_text("""
            CREATE TABLE IF NOT EXISTS employee_holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                holiday_date TEXT UNIQUE NOT NULL,
                holiday_name TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))

        conn.execute(_employee_settings_sql_text("""
            CREATE TABLE IF NOT EXISTS employee_rest_months (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                rest_dates TEXT DEFAULT '[]',
                note TEXT DEFAULT '',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(staff_code, year, month)
            )
        """))

        conn.execute(_employee_settings_sql_text("""
            CREATE TABLE IF NOT EXISTS employee_proxy_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT UNIQUE NOT NULL,
                proxy_staff_code TEXT DEFAULT '',
                proxy_display_name TEXT DEFAULT '',
                enabled INTEGER DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))

        conn.execute(_employee_settings_sql_text("""
            CREATE TABLE IF NOT EXISTS employee_leave_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT NOT NULL,
                leave_type TEXT DEFAULT '',
                start_date TEXT DEFAULT '',
                end_date TEXT DEFAULT '',
                reason TEXT DEFAULT '',
                status TEXT DEFAULT '申請中',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))





@router.get("/api/app/employee/profile", summary="\u53d6\u5f97\u54e1\u5de5\u500b\u4eba\u8cc7\u6599")
def api_app_employee_profile(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()
    try:
        _employee_proxy_accept_ensure_columns()
    except NameError:
        pass

    staff_code = str(user.get("staff_code") or "").strip()
    display_name = str(user.get("display_name") or "").strip() or staff_code
    department = str(user.get("department") or "").strip()
    role = str(user.get("role") or "employee").strip() or "employee"

    now_text = _employee_settings_datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with _employee_settings_engine.begin() as conn:
        # ?? employee_profiles ????????????????????
        profile_cols = [row[1] for row in conn.execute(_employee_settings_sql_text("PRAGMA table_info(employee_profiles)")).fetchall()]
        wanted_cols = {
            "position_title": "TEXT DEFAULT ''",
            "job_grade": "TEXT DEFAULT ''",
            "phone": "TEXT DEFAULT ''",
            "email": "TEXT DEFAULT ''",
            "hire_date": "TEXT DEFAULT ''",
            "employment_status": "TEXT DEFAULT '??'",
            "permission_scope": "TEXT DEFAULT ''",
            "updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
        }

        for col, ddl in wanted_cols.items():
            if col not in profile_cols:
                try:
                    conn.execute(_employee_settings_sql_text(f"ALTER TABLE employee_profiles ADD COLUMN {col} {ddl}"))
                except Exception:
                    pass

        profile = conn.execute(
            _employee_settings_sql_text("""
                SELECT *
                FROM employee_profiles
                WHERE staff_code = :staff_code
                LIMIT 1
            """),
            {"staff_code": staff_code},
        ).mappings().first()

        if not profile:
            conn.execute(
                _employee_settings_sql_text("""
                    INSERT INTO employee_profiles (
                        staff_code,
                        display_name,
                        department,
                        role,
                        position_title,
                        job_grade,
                        phone,
                        email,
                        hire_date,
                        employment_status,
                        permission_scope,
                        updated_at
                    )
                    VALUES (
                        :staff_code,
                        :display_name,
                        :department,
                        :role,
                        '',
                        '',
                        '',
                        '',
                        '',
                        '\u5728\u8077',
                        '',
                        :updated_at
                    )
                """),
                {
                    "staff_code": staff_code,
                    "display_name": display_name,
                    "department": department,
                    "role": role,
                    "updated_at": now_text,
                },
            )
        else:
            # ??????????????????????????
            if not str(profile.get("display_name") or "").strip():
                conn.execute(
                    _employee_settings_sql_text("""
                        UPDATE employee_profiles
                        SET display_name = :display_name,
                            updated_at = :updated_at
                        WHERE staff_code = :staff_code
                    """),
                    {"staff_code": staff_code, "display_name": display_name, "updated_at": now_text},
                )

            if department and not str(profile.get("department") or "").strip():
                conn.execute(
                    _employee_settings_sql_text("""
                        UPDATE employee_profiles
                        SET department = :department,
                            updated_at = :updated_at
                        WHERE staff_code = :staff_code
                    """),
                    {"staff_code": staff_code, "department": department, "updated_at": now_text},
                )

            if role and not str(profile.get("role") or "").strip():
                conn.execute(
                    _employee_settings_sql_text("""
                        UPDATE employee_profiles
                        SET role = :role,
                            updated_at = :updated_at
                        WHERE staff_code = :staff_code
                    """),
                    {"staff_code": staff_code, "role": role, "updated_at": now_text},
                )

        profile = conn.execute(
            _employee_settings_sql_text("""
                SELECT *
                FROM employee_profiles
                WHERE staff_code = :staff_code
                LIMIT 1
            """),
            {"staff_code": staff_code},
        ).mappings().first()

        profile_dict = dict(profile or {})
        if not profile_dict:
            profile_dict = {
                "staff_code": staff_code,
                "display_name": display_name,
                "department": department,
                "role": role,
                "position_title": "",
                "job_grade": "",
                "phone": "",
                "email": "",
                "hire_date": "",
                "employment_status": "\u5728\u8077",
                "permission_scope": "",
            }

        # ??????????
        proxy_cols = [row[1] for row in conn.execute(_employee_settings_sql_text("PRAGMA table_info(employee_proxy_settings)")).fetchall()]
        proxy_wanted_cols = {
            "proxy_one_staff_code": "TEXT DEFAULT ''",
            "proxy_one_name": "TEXT DEFAULT ''",
            "proxy_two_staff_code": "TEXT DEFAULT ''",
            "proxy_two_name": "TEXT DEFAULT ''",
            "updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
        }

        for col, ddl in proxy_wanted_cols.items():
            if col not in proxy_cols:
                try:
                    conn.execute(_employee_settings_sql_text(f"ALTER TABLE employee_proxy_settings ADD COLUMN {col} {ddl}"))
                except Exception:
                    pass

        proxy = conn.execute(
            _employee_settings_sql_text("""
                SELECT *
                FROM employee_proxy_settings
                WHERE staff_code = :staff_code
                LIMIT 1
            """),
            {"staff_code": staff_code},
        ).mappings().first()

        if not proxy:
            conn.execute(
                _employee_settings_sql_text("""
                    INSERT INTO employee_proxy_settings (
                        staff_code,
                        proxy_one_staff_code,
                        proxy_one_name,
                        proxy_two_staff_code,
                        proxy_two_name,
                        updated_at
                    )
                    VALUES (:staff_code, '', '', '', '', :updated_at)
                """),
                {"staff_code": staff_code, "updated_at": now_text},
            )

            proxy = conn.execute(
                _employee_settings_sql_text("""
                    SELECT *
                    FROM employee_proxy_settings
                    WHERE staff_code = :staff_code
                    LIMIT 1
                """),
                {"staff_code": staff_code},
            ).mappings().first()

        # ??????? leave_date ? start_date?
        leave_cols = [row[1] for row in conn.execute(_employee_settings_sql_text("PRAGMA table_info(employee_leave_settings)")).fetchall()]
        date_col = "leave_date" if "leave_date" in leave_cols else "start_date"

        leave_summary = {}

        if date_col in leave_cols:
            leave_rows = conn.execute(
                _employee_settings_sql_text(f"""
                    SELECT leave_type, COUNT(*) AS count
                    FROM employee_leave_settings
                    WHERE staff_code = :staff_code
                      AND substr(COALESCE({date_col}, ''), 1, 4) = strftime('%Y', 'now')
                    GROUP BY leave_type
                """),
                {"staff_code": staff_code},
            ).mappings().fetchall()

            for row in leave_rows:
                leave_summary[str(row.get("leave_type") or "")] = int(row.get("count") or 0)

        represented_rows = conn.execute(
            _employee_settings_sql_text("""
                SELECT staff_code, display_name, department
                FROM employee_profiles
                WHERE staff_code IN (
                    SELECT staff_code
                    FROM employee_proxy_settings
                    WHERE (proxy_one_staff_code = :staff_code AND COALESCE(proxy_one_status, '') = 'accepted')
                       OR (proxy_two_staff_code = :staff_code AND COALESCE(proxy_two_status, '') = 'accepted')
                )
                ORDER BY staff_code
            """),
            {"staff_code": staff_code},
        ).mappings().fetchall()

    annual_leave_total = _calc_annual_leave_days_for_employee_settings(profile_dict.get("hire_date", ""))
    annual_leave_used = int(leave_summary.get("\u7279\u4f11", 0) or 0)
    annual_leave_remaining = max(0, annual_leave_total - annual_leave_used)

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps(
            {
                "ok": True,
                "profile": profile_dict,
                "leave_summary": leave_summary,
                "annual_leave_total": annual_leave_total,
                "annual_leave_used": annual_leave_used,
                "annual_leave_remaining": annual_leave_remaining,
                "proxy": dict(proxy or {}),
                "represented_employees": [dict(row) for row in represented_rows],
            },
            ensure_ascii=False,
        ),
        media_type="application/json; charset=utf-8",
    )





@router.post("/api/app/employee/change-password", summary="\u8b8a\u66f4\u54e1\u5de5 PIN")
async def api_app_employee_change_password(request: _EmpRequest):
    import secrets

    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    try:
        data = await request.json()
    except Exception:
        data = {}

    old_pin = str(data.get("old_pin", "") or "").strip()
    new_pin = str(data.get("new_pin", "") or "").strip()
    new_pin2 = str(data.get("new_pin2", "") or "").strip()

    if not old_pin or not new_pin or not new_pin2:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "\u8acb\u8f38\u5165\u539f PIN \u8207\u65b0 PIN"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    if new_pin != new_pin2:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "\u5169\u6b21\u65b0 PIN \u4e0d\u4e00\u81f4"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    if len(new_pin) < 4:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "PIN \u81f3\u5c11 4 \u78bc"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    staff_code = str(user.get("staff_code") or "").strip()

    with _employee_settings_engine.begin() as conn:
        account = conn.execute(
            _employee_settings_sql_text("""
                SELECT staff_code, pin_salt, pin_hash, enabled
                FROM employee_accounts
                WHERE staff_code = :staff_code
                LIMIT 1
            """),
            {"staff_code": staff_code},
        ).mappings().first()

        if not account:
            return _EmployeeSettingsResponse(
                content=_employee_settings_json.dumps({"ok": False, "error": "\u627e\u4e0d\u5230\u54e1\u5de5\u5e33\u865f"}, ensure_ascii=False),
                media_type="application/json; charset=utf-8",
                status_code=404,
            )

        if int(account.get("enabled") or 0) != 1:
            return _EmployeeSettingsResponse(
                content=_employee_settings_json.dumps({"ok": False, "error": "\u627e\u4e0d\u5230\u54e1\u5de5\u5e33\u865f"}, ensure_ascii=False),
                media_type="application/json; charset=utf-8",
                status_code=403,
            )

        old_hash = _emp_hash_pin(old_pin, account["pin_salt"])

        if old_hash != str(account["pin_hash"] or ""):
            return _EmployeeSettingsResponse(
                content=_employee_settings_json.dumps({"ok": False, "error": "\u539f PIN \u4e0d\u6b63\u78ba"}, ensure_ascii=False),
                media_type="application/json; charset=utf-8",
                status_code=403,
            )

        new_salt = secrets.token_hex(8)
        new_hash = _emp_hash_pin(new_pin, new_salt)

        conn.execute(
            _employee_settings_sql_text("""
                UPDATE employee_accounts
                SET pin_salt = :pin_salt,
                    pin_hash = :pin_hash,
                    updated_at = datetime('now', 'localtime')
                WHERE staff_code = :staff_code
            """),
            {
                "pin_salt": new_salt,
                "pin_hash": new_hash,
                "staff_code": staff_code,
            },
        )

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps({"ok": True, "message": "password updated"}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )



# XN_REST_WEEKEND_REQUIRED_V1_START
def _employee_settings_month_required_rest_days(year: int, month: int) -> int:
    """計算當月應休天數：週六、週日 + 公司國定假日，日期重複只算一次。"""
    import calendar

    try:
        year = int(year)
        month = int(month)
        _, days_in_month = calendar.monthrange(year, month)
    except Exception:
        return 8

    rest_dates = set()

    for day in range(1, days_in_month + 1):
        # calendar.weekday: Monday=0 ... Sunday=6
        if calendar.weekday(year, month, day) in (5, 6):
            rest_dates.add(f"{year:04d}-{month:02d}-{day:02d}")

    start_date = f"{year:04d}-{month:02d}-01"
    end_date = f"{year:04d}-{month:02d}-{days_in_month:02d}"

    try:
        with _employee_settings_engine.begin() as conn:
            rows = conn.execute(
                _employee_settings_sql_text("""
                    SELECT holiday_date
                    FROM company_holidays
                    WHERE enabled = 1
                      AND holiday_date >= :start_date
                      AND holiday_date <= :end_date
                """),
                {"start_date": start_date, "end_date": end_date},
            ).mappings().fetchall()

        for row in rows:
            key = str(row.get("holiday_date") or "").strip()[:10]
            if key:
                rest_dates.add(key)
    except Exception:
        pass

    return max(0, len(rest_dates))
# XN_REST_WEEKEND_REQUIRED_V1_END


@router.get("/api/app/employee/holidays", summary="讀取公司國定假日表")
def api_app_employee_holidays(request: _EmpRequest, year: int):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()

    with _employee_settings_engine.begin() as conn:
        rows = conn.execute(
            _employee_settings_sql_text("""
                SELECT holiday_date, title
                FROM company_holidays
                WHERE enabled = 1
                  AND substr(holiday_date, 1, 4) = :year
                ORDER BY holiday_date
            """),
            {"year": str(year)},
        ).mappings().fetchall()

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps({"ok": True, "items": [dict(row) for row in rows]}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.get("/api/app/employee/rest-month", summary="讀取員工月休設定")
def api_app_employee_rest_month(request: _EmpRequest, year: int, month: int):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()
    staff_code = user.get("staff_code") or ""

    with _employee_settings_engine.begin() as conn:
        row = conn.execute(
            _employee_settings_sql_text("""
                SELECT year, month, required_rest_days, selected_dates, rest_count, confirm_incomplete, review_status
                FROM employee_rest_month_settings
                WHERE staff_code = :staff_code
                  AND year = :year
                  AND month = :month
                LIMIT 1
            """),
            {"staff_code": staff_code, "year": year, "month": month},
        ).mappings().first()

    required_rest_days = _employee_settings_month_required_rest_days(year, month)

    if row:
        try:
            selected_dates = _employee_settings_json.loads(row["selected_dates"] or "[]")
        except Exception:
            selected_dates = []
    else:
        selected_dates = []

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps(
            {
                "ok": True,
                "year": year,
                "month": month,
                "required_rest_days": required_rest_days,
                "selected_dates": selected_dates,
                "rest_count": len(selected_dates),
            },
            ensure_ascii=False,
        ),
        media_type="application/json; charset=utf-8",
    )


@router.post("/api/app/employee/rest-month/save", summary="儲存員工月休設定")
async def api_app_employee_rest_month_save(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()

    raw = await request.body()
    try:
        data = _employee_settings_json.loads(raw.decode("utf-8") or "{}")
    except Exception:
        data = {}

    year = int(data.get("year") or 0)
    month = int(data.get("month") or 0)
    selected_dates = data.get("selected_dates") or []
    force = bool(data.get("force") or False)

    if not year or not month:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "缺少年月"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    required_rest_days = _employee_settings_month_required_rest_days(year, month)
    rest_count = len(selected_dates)

    if rest_count < required_rest_days and not force:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps(
                {
                    "ok": False,
                    "need_confirm": True,
                    "missing": required_rest_days - rest_count,
                    "error": f"您本月休假尚缺 {required_rest_days - rest_count:g} 天未選。",
                },
                ensure_ascii=False,
            ),
            media_type="application/json; charset=utf-8",
            status_code=409,
        )

    staff_code = user.get("staff_code") or ""

    with _employee_settings_engine.begin() as conn:
        conn.execute(
            _employee_settings_sql_text("""
                INSERT INTO employee_rest_month_settings (
                    staff_code,
                    display_name,
                    department,
                    year,
                    month,
                    required_rest_days,
                    selected_dates,
                    rest_count,
                    confirm_incomplete,
                    review_status,
                    created_at,
                    updated_at
                )
                VALUES (
                    :staff_code,
                    :display_name,
                    :department,
                    :year,
                    :month,
                    :required_rest_days,
                    :selected_dates,
                    :rest_count,
                    :confirm_incomplete,
                    '待審核',
                    datetime('now'),
                    datetime('now')
                )
                ON CONFLICT(staff_code, year, month)
                DO UPDATE SET
                    selected_dates = excluded.selected_dates,
                    rest_count = excluded.rest_count,
                    confirm_incomplete = excluded.confirm_incomplete,
                    review_status = '待審核',
                    updated_at = datetime('now')
            """),
            {
                "staff_code": staff_code,
                "display_name": user.get("display_name") or "",
                "department": user.get("department") or "",
                "year": year,
                "month": month,
                "required_rest_days": required_rest_days,
                "selected_dates": _employee_settings_json.dumps(selected_dates, ensure_ascii=False),
                "rest_count": rest_count,
                "confirm_incomplete": 1 if rest_count < required_rest_days else 0,
            },
        )

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps({"ok": True}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )



# XN_REST_QUERY_DASHBOARD_V1_START
def _employee_settings_year_total_rest_days(year: int) -> int:
    """計算指定年度總假日：週六、週日 + 公司國定假日，日期重複只算一次。"""
    import calendar

    try:
        year = int(year)
    except Exception:
        year = _employee_settings_datetime.now().year

    rest_dates = set()

    for month in range(1, 13):
        try:
            _, days_in_month = calendar.monthrange(year, month)
        except Exception:
            continue

        for day in range(1, days_in_month + 1):
            if calendar.weekday(year, month, day) in (5, 6):
                rest_dates.add(f"{year:04d}-{month:02d}-{day:02d}")

    try:
        with _employee_settings_engine.begin() as conn:
            rows = conn.execute(
                _employee_settings_sql_text("""
                    SELECT holiday_date
                    FROM company_holidays
                    WHERE enabled = 1
                      AND substr(holiday_date, 1, 4) = :year
                """),
                {"year": str(year)},
            ).mappings().fetchall()

        for row in rows:
            key = str(row.get("holiday_date") or "").strip()[:10]
            if key:
                rest_dates.add(key)
    except Exception:
        pass

    return len(rest_dates)


@router.get("/api/app/employee/rest-query", summary="員工休假查詢摘要與當月假表")
def api_app_employee_rest_query(request: _EmpRequest, year: int = 0, month: int = 0):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()

    now = _employee_settings_datetime.now()
    try:
        year = int(year or now.year)
    except Exception:
        year = now.year

    try:
        month = int(month or now.month)
    except Exception:
        month = now.month

    if month < 1 or month > 12:
        month = now.month

    staff_code = str(user.get("staff_code") or "").strip()

    annual_total = _employee_settings_year_total_rest_days(year)
    used_dates = set()
    monthly_items = []

    with _employee_settings_engine.begin() as conn:
        rows = conn.execute(
            _employee_settings_sql_text("""
                SELECT
                    year,
                    month,
                    selected_dates,
                    rest_count,
                    review_status,
                    updated_at
                FROM employee_rest_month_settings
                WHERE staff_code = :staff_code
                  AND year = :year
                ORDER BY month ASC
            """),
            {"staff_code": staff_code, "year": year},
        ).mappings().fetchall()

    for row in rows:
        row_month = int(row.get("month") or 0)
        review_status = str(row.get("review_status") or "待審核")
        updated_at = str(row.get("updated_at") or "")

        try:
            dates = _employee_settings_json.loads(row.get("selected_dates") or "[]")
        except Exception:
            dates = []

        if not isinstance(dates, list):
            dates = []

        for date_text in dates:
            key = str(date_text or "").strip()[:10]
            if not key:
                continue

            if key.startswith(f"{year:04d}-"):
                used_dates.add(key)

            if row_month == month and key.startswith(f"{year:04d}-{month:02d}-"):
                monthly_items.append({
                    "rest_date": key,
                    "rest_type": "排休",
                    "review_status": review_status,
                    "updated_at": updated_at,
                    "readonly": True,
                })

    monthly_items.sort(key=lambda item: item.get("rest_date") or "")

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps(
            {
                "ok": True,
                "year": year,
                "month": month,
                "annual_total_rest_days": annual_total,
                "annual_used_rest_days": len(used_dates),
                "monthly_items": monthly_items,
            },
            ensure_ascii=False,
        ),
        media_type="application/json; charset=utf-8",
    )
# XN_REST_QUERY_DASHBOARD_V1_END




# XN_PROXY_ACCEPT_FLOW_V1_START
def _employee_proxy_accept_ensure_columns():
    wanted_cols = {
        "display_name": "TEXT DEFAULT ''",
        "department": "TEXT DEFAULT ''",
        "proxy_one_staff_code": "TEXT DEFAULT ''",
        "proxy_one_name": "TEXT DEFAULT ''",
        "proxy_one_status": "TEXT DEFAULT ''",
        "proxy_one_requested_at": "TEXT DEFAULT ''",
        "proxy_one_accepted_at": "TEXT DEFAULT ''",
        "proxy_two_staff_code": "TEXT DEFAULT ''",
        "proxy_two_name": "TEXT DEFAULT ''",
        "proxy_two_status": "TEXT DEFAULT ''",
        "proxy_two_requested_at": "TEXT DEFAULT ''",
        "proxy_two_accepted_at": "TEXT DEFAULT ''",
        "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
        "updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
    }

    with _employee_settings_engine.begin() as conn:
        conn.execute(_employee_settings_sql_text("""
            CREATE TABLE IF NOT EXISTS employee_proxy_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT UNIQUE NOT NULL,
                proxy_staff_code TEXT DEFAULT '',
                proxy_display_name TEXT DEFAULT '',
                enabled INTEGER DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))

        cols = [row[1] for row in conn.execute(_employee_settings_sql_text("PRAGMA table_info(employee_proxy_settings)")).fetchall()]

        for col, ddl in wanted_cols.items():
            if col not in cols:
                try:
                    conn.execute(_employee_settings_sql_text(f"ALTER TABLE employee_proxy_settings ADD COLUMN {col} {ddl}"))
                except Exception:
                    pass


def _employee_proxy_accept_resolve_value(conn, value):
    raw = str(value or "").strip()

    if not raw:
        return "", ""

    parts = [p.strip() for p in raw.split("｜") if p.strip()]
    candidates = []

    if parts:
        candidates.append(parts[0])

    if len(parts) >= 2:
        candidates.append(parts[1])

    candidates.append(raw)

    for candidate in candidates:
        row = conn.execute(
            _employee_settings_sql_text("""
                SELECT staff_code, display_name
                FROM employee_profiles
                WHERE staff_code = :value
                   OR display_name = :value
                LIMIT 1
            """),
            {"value": candidate},
        ).mappings().first()

        if row:
            return str(row.get("staff_code") or "").strip(), str(row.get("display_name") or "").strip()

    return raw, raw


@router.get("/api/app/employee/proxy/pending-requests", summary="讀取待同意代理人邀請")
def api_app_employee_proxy_pending_requests(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()
    _employee_proxy_accept_ensure_columns()

    staff_code = str(user.get("staff_code") or "").strip()
    items = []

    with _employee_settings_engine.begin() as conn:
        rows = conn.execute(
            _employee_settings_sql_text("""
                SELECT
                    p.staff_code AS requester_staff_code,
                    COALESCE(ep.display_name, p.display_name, p.staff_code) AS requester_name,
                    COALESCE(ep.department, p.department, '') AS requester_department,
                    p.proxy_one_staff_code,
                    p.proxy_one_name,
                    p.proxy_one_status,
                    p.proxy_one_requested_at,
                    p.proxy_two_staff_code,
                    p.proxy_two_name,
                    p.proxy_two_status,
                    p.proxy_two_requested_at
                FROM employee_proxy_settings p
                LEFT JOIN employee_profiles ep ON ep.staff_code = p.staff_code
                WHERE (p.proxy_one_staff_code = :staff_code AND COALESCE(p.proxy_one_status, '') = 'pending')
                   OR (p.proxy_two_staff_code = :staff_code AND COALESCE(p.proxy_two_status, '') = 'pending')
                ORDER BY p.updated_at DESC
            """),
            {"staff_code": staff_code},
        ).mappings().fetchall()

    for row in rows:
        if str(row.get("proxy_one_staff_code") or "") == staff_code and str(row.get("proxy_one_status") or "") == "pending":
            items.append({
                "requester_staff_code": row.get("requester_staff_code") or "",
                "requester_name": row.get("requester_name") or "",
                "requester_department": row.get("requester_department") or "",
                "slot": "one",
                "requested_at": row.get("proxy_one_requested_at") or "",
            })

        if str(row.get("proxy_two_staff_code") or "") == staff_code and str(row.get("proxy_two_status") or "") == "pending":
            items.append({
                "requester_staff_code": row.get("requester_staff_code") or "",
                "requester_name": row.get("requester_name") or "",
                "requester_department": row.get("requester_department") or "",
                "slot": "two",
                "requested_at": row.get("proxy_two_requested_at") or "",
            })

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps({"ok": True, "items": items}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.post("/api/app/employee/proxy/respond", summary="同意或拒絕代理人邀請")
async def api_app_employee_proxy_respond(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()
    _employee_proxy_accept_ensure_columns()

    try:
        data = await request.json()
    except Exception:
        data = {}

    responder_staff_code = str(user.get("staff_code") or "").strip()
    requester_staff_code = str(data.get("requester_staff_code") or "").strip()
    slot = str(data.get("slot") or "").strip().lower()
    action = str(data.get("action") or "accept").strip().lower()

    if slot not in ("one", "two"):
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "代理欄位錯誤"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    if action not in ("accept", "reject"):
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "回覆動作錯誤"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    if not requester_staff_code:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "缺少申請人工號"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    status_value = "accepted" if action == "accept" else "rejected"
    proxy_col = f"proxy_{slot}_staff_code"
    status_col = f"proxy_{slot}_status"
    accepted_col = f"proxy_{slot}_accepted_at"

    with _employee_settings_engine.begin() as conn:
        result = conn.execute(
            _employee_settings_sql_text(f"""
                UPDATE employee_proxy_settings
                SET {status_col} = :status_value,
                    {accepted_col} = CASE WHEN :status_value = 'accepted' THEN datetime('now') ELSE '' END,
                    updated_at = datetime('now')
                WHERE staff_code = :requester_staff_code
                  AND {proxy_col} = :responder_staff_code
                  AND COALESCE({status_col}, '') = 'pending'
            """),
            {
                "status_value": status_value,
                "requester_staff_code": requester_staff_code,
                "responder_staff_code": responder_staff_code,
            },
        )

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps({"ok": True, "updated": int(result.rowcount or 0), "status": status_value}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )
# XN_PROXY_ACCEPT_FLOW_V1_END



@router.get("/api/app/employee/list-for-proxy", summary="代理人選單")
def api_app_employee_list_for_proxy(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()
    _employee_proxy_accept_ensure_columns()

    staff_code = str(user.get("staff_code") or "").strip()

    with _employee_settings_engine.begin() as conn:
        rows = conn.execute(
            _employee_settings_sql_text("""
                SELECT staff_code, display_name, department, position_title
                FROM employee_profiles
                WHERE staff_code <> :staff_code
                  AND COALESCE(employment_status, '在職') IN ('在職', '', '??')
                ORDER BY staff_code
            """),
            {"staff_code": staff_code},
        ).mappings().fetchall()

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps({"ok": True, "items": [dict(row) for row in rows]}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.post("/api/app/employee/proxy/save", summary="儲存代理人設定")
async def api_app_employee_proxy_save(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()
    _employee_proxy_accept_ensure_columns()

    try:
        data = await request.json()
    except Exception:
        data = {}

    proxy_one_raw = str(data.get("proxy_one_staff_code", "") or data.get("proxy_one", "") or "").strip()
    proxy_two_raw = str(data.get("proxy_two_staff_code", "") or data.get("proxy_two", "") or "").strip()

    staff_code = str(user.get("staff_code") or "").strip()

    with _employee_settings_engine.begin() as conn:
        proxy_one, proxy_one_name = _employee_proxy_accept_resolve_value(conn, proxy_one_raw)
        proxy_two, proxy_two_name = _employee_proxy_accept_resolve_value(conn, proxy_two_raw)

        old = conn.execute(
            _employee_settings_sql_text("""
                SELECT *
                FROM employee_proxy_settings
                WHERE staff_code = :staff_code
                LIMIT 1
            """),
            {"staff_code": staff_code},
        ).mappings().first()

        old_one_code = str((old or {}).get("proxy_one_staff_code") or "")
        old_two_code = str((old or {}).get("proxy_two_staff_code") or "")
        old_one_status = str((old or {}).get("proxy_one_status") or "")
        old_two_status = str((old or {}).get("proxy_two_status") or "")

        def next_status(new_code, old_code, old_status):
            if not new_code:
                return ""
            if new_code == old_code and old_status == "accepted":
                return "accepted"
            return "pending"

        proxy_one_status = next_status(proxy_one, old_one_code, old_one_status)
        proxy_two_status = next_status(proxy_two, old_two_code, old_two_status)

        conn.execute(
            _employee_settings_sql_text("""
                INSERT INTO employee_proxy_settings (
                    staff_code,
                    display_name,
                    department,
                    proxy_one_staff_code,
                    proxy_one_name,
                    proxy_one_status,
                    proxy_one_requested_at,
                    proxy_one_accepted_at,
                    proxy_two_staff_code,
                    proxy_two_name,
                    proxy_two_status,
                    proxy_two_requested_at,
                    proxy_two_accepted_at,
                    created_at,
                    updated_at
                )
                VALUES (
                    :staff_code,
                    :display_name,
                    :department,
                    :proxy_one_staff_code,
                    :proxy_one_name,
                    :proxy_one_status,
                    CASE WHEN :proxy_one_status = 'pending' THEN datetime('now') ELSE '' END,
                    CASE WHEN :proxy_one_status = 'accepted' THEN COALESCE((SELECT proxy_one_accepted_at FROM employee_proxy_settings WHERE staff_code = :staff_code), '') ELSE '' END,
                    :proxy_two_staff_code,
                    :proxy_two_name,
                    :proxy_two_status,
                    CASE WHEN :proxy_two_status = 'pending' THEN datetime('now') ELSE '' END,
                    CASE WHEN :proxy_two_status = 'accepted' THEN COALESCE((SELECT proxy_two_accepted_at FROM employee_proxy_settings WHERE staff_code = :staff_code), '') ELSE '' END,
                    datetime('now'),
                    datetime('now')
                )
                ON CONFLICT(staff_code)
                DO UPDATE SET
                    display_name = excluded.display_name,
                    department = excluded.department,

                    proxy_one_staff_code = excluded.proxy_one_staff_code,
                    proxy_one_name = excluded.proxy_one_name,
                    proxy_one_status = excluded.proxy_one_status,
                    proxy_one_requested_at = CASE WHEN excluded.proxy_one_status = 'pending' THEN datetime('now') ELSE proxy_one_requested_at END,
                    proxy_one_accepted_at = CASE WHEN excluded.proxy_one_status = 'accepted' THEN proxy_one_accepted_at ELSE '' END,

                    proxy_two_staff_code = excluded.proxy_two_staff_code,
                    proxy_two_name = excluded.proxy_two_name,
                    proxy_two_status = excluded.proxy_two_status,
                    proxy_two_requested_at = CASE WHEN excluded.proxy_two_status = 'pending' THEN datetime('now') ELSE proxy_two_requested_at END,
                    proxy_two_accepted_at = CASE WHEN excluded.proxy_two_status = 'accepted' THEN proxy_two_accepted_at ELSE '' END,

                    updated_at = datetime('now')
            """),
            {
                "staff_code": staff_code,
                "display_name": user.get("display_name") or "",
                "department": user.get("department") or "",
                "proxy_one_staff_code": proxy_one,
                "proxy_one_name": proxy_one_name,
                "proxy_one_status": proxy_one_status,
                "proxy_two_staff_code": proxy_two,
                "proxy_two_name": proxy_two_name,
                "proxy_two_status": proxy_two_status,
            },
        )

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps(
            {
                "ok": True,
                "proxy_one_status": proxy_one_status,
                "proxy_two_status": proxy_two_status,
            },
            ensure_ascii=False,
        ),
        media_type="application/json; charset=utf-8",
    )



# XN_PROXY_CONTEXT_V1_START
def _employee_proxy_context_available_targets(login_staff_code: str):
    login_staff_code = str(login_staff_code or "").strip()

    if not login_staff_code:
        return []

    _employee_proxy_accept_ensure_columns()

    with _employee_settings_engine.begin() as conn:
        rows = conn.execute(
            _employee_settings_sql_text("""
                SELECT
                    ep.staff_code,
                    ep.display_name,
                    ep.department,
                    ep.role,
                    ep.position_title
                FROM employee_profiles ep
                WHERE ep.staff_code IN (
                    SELECT staff_code
                    FROM employee_proxy_settings
                    WHERE (proxy_one_staff_code = :login_staff_code AND COALESCE(proxy_one_status, '') = 'accepted')
                       OR (proxy_two_staff_code = :login_staff_code AND COALESCE(proxy_two_status, '') = 'accepted')
                )
                ORDER BY ep.staff_code
            """),
            {"login_staff_code": login_staff_code},
        ).mappings().fetchall()

    return [dict(row) for row in rows]


def _employee_proxy_context_find_target(login_staff_code: str, acting_staff_code: str):
    login_staff_code = str(login_staff_code or "").strip()
    acting_staff_code = str(acting_staff_code or "").strip()

    if not login_staff_code or not acting_staff_code:
        return None

    for item in _employee_proxy_context_available_targets(login_staff_code):
        if str(item.get("staff_code") or "").strip() == acting_staff_code:
            return item

    return None


def _employee_proxy_context_build(request: _EmpRequest, user: dict):
    login_staff_code = str(user.get("staff_code") or "").strip()
    login_display_name = str(user.get("display_name") or "").strip() or login_staff_code
    login_department = str(user.get("department") or "").strip()
    login_role = str(user.get("role") or "").strip()

    available_targets = _employee_proxy_context_available_targets(login_staff_code)

    cookie_acting_staff_code = str(request.cookies.get("xunnan_acting_staff_code") or "").strip()
    target = _employee_proxy_context_find_target(login_staff_code, cookie_acting_staff_code)

    if target:
        acting_staff_code = str(target.get("staff_code") or "").strip()
        acting_display_name = str(target.get("display_name") or "").strip() or acting_staff_code
        acting_department = str(target.get("department") or "").strip()
        acting_role = str(target.get("role") or "").strip()
        is_proxy_mode = True
    else:
        acting_staff_code = login_staff_code
        acting_display_name = login_display_name
        acting_department = login_department
        acting_role = login_role
        is_proxy_mode = False

    return {
        "ok": True,
        "is_proxy_mode": is_proxy_mode,
        "login_staff_code": login_staff_code,
        "login_display_name": login_display_name,
        "login_department": login_department,
        "login_role": login_role,
        "acting_staff_code": acting_staff_code,
        "acting_display_name": acting_display_name,
        "acting_department": acting_department,
        "acting_role": acting_role,
        "permission_owner_code": acting_staff_code,
        "permission_owner_name": acting_display_name,
        "available_targets": available_targets,
    }


@router.get("/api/app/employee/proxy/context", summary="讀取目前代理身分上下文")
def api_app_employee_proxy_context(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()
    _employee_proxy_accept_ensure_columns()

    data = _employee_proxy_context_build(request, user)

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps(data, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.post("/api/app/employee/proxy/switch", summary="切換代理身分")
async def api_app_employee_proxy_switch(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()
    _employee_proxy_accept_ensure_columns()

    try:
        data = await request.json()
    except Exception:
        data = {}

    login_staff_code = str(user.get("staff_code") or "").strip()
    acting_staff_code = str(data.get("acting_staff_code") or data.get("staff_code") or "").strip()

    target = _employee_proxy_context_find_target(login_staff_code, acting_staff_code)

    if not target:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "你沒有此員工的代理權限"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=403,
        )

    response_data = {
        "ok": True,
        "message": "proxy switched",
        "login_staff_code": login_staff_code,
        "acting_staff_code": acting_staff_code,
        "permission_owner_code": acting_staff_code,
        "acting_display_name": target.get("display_name") or acting_staff_code,
    }

    res = _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps(response_data, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )

    res.set_cookie(
        key="xunnan_acting_staff_code",
        value=acting_staff_code,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 12,
        path="/",
    )

    res.set_cookie(
        key="xunnan_permission_owner_code",
        value=acting_staff_code,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 12,
        path="/",
    )

    return res


@router.post("/api/app/employee/proxy/clear", summary="結束代理身分")
async def api_app_employee_proxy_clear(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    res = _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps({"ok": True, "message": "proxy cleared"}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )

    res.delete_cookie("xunnan_acting_staff_code", path="/")
    res.delete_cookie("xunnan_permission_owner_code", path="/")

    return res
# XN_PROXY_CONTEXT_V1_END


# XN_PROXY_OWNER_REVOKE_V1_START
@router.post("/api/app/employee/proxy/revoke", summary="被代理者強制撤銷代理")
async def api_app_employee_proxy_revoke(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()
    _employee_proxy_accept_ensure_columns()

    try:
        data = await request.json()
    except Exception:
        data = {}

    owner_staff_code = str(user.get("staff_code") or "").strip()
    slot = str(data.get("slot") or "").strip().lower()

    if slot not in ("one", "two"):
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "代理欄位錯誤"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    code_col = f"proxy_{slot}_staff_code"
    name_col = f"proxy_{slot}_name"
    status_col = f"proxy_{slot}_status"
    requested_col = f"proxy_{slot}_requested_at"
    accepted_col = f"proxy_{slot}_accepted_at"

    with _employee_settings_engine.begin() as conn:
        result = conn.execute(
            _employee_settings_sql_text(f"""
                UPDATE employee_proxy_settings
                SET {code_col} = '',
                    {name_col} = '',
                    {status_col} = '',
                    {requested_col} = '',
                    {accepted_col} = '',
                    updated_at = datetime('now')
                WHERE staff_code = :owner_staff_code
                  AND COALESCE({code_col}, '') <> ''
            """),
            {"owner_staff_code": owner_staff_code},
        )

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps(
            {
                "ok": True,
                "message": "proxy revoked",
                "slot": slot,
                "updated": int(result.rowcount or 0),
            },
            ensure_ascii=False,
        ),
        media_type="application/json; charset=utf-8",
    )
# XN_PROXY_OWNER_REVOKE_V1_END



@router.get("/api/app/employee/leave-settings", summary="員工讀取自己的請假設定")
def api_app_employee_leave_settings(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()
    staff_code = user.get("staff_code") or ""

    with _employee_settings_engine.begin() as conn:
        rows = conn.execute(
            _employee_settings_sql_text("""
                SELECT
                    id,
                    staff_code,
                    display_name,
                    department,
                    period_label,
                    leave_date,
                    leave_type,
                    start_time,
                    end_time,
                    proof_required,
                    note,
                    review_status,
                    created_at,
                    updated_at
                FROM employee_leave_settings
                WHERE staff_code = :staff_code
                ORDER BY leave_date DESC, id DESC
                LIMIT 100
            """),
            {"staff_code": staff_code},
        ).mappings().fetchall()

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps(
            {
                "ok": True,
                "period_label": _employee_leave_period_label(),
                "items": [dict(row) for row in rows],
            },
            ensure_ascii=False,
        ),
        media_type="application/json; charset=utf-8",
    )


@router.post("/api/app/employee/leave-settings/create", summary="員工新增請假設定")
async def api_app_employee_leave_settings_create(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    _employee_settings_db_init()

    raw = await request.body()
    try:
        data = _employee_settings_json.loads(raw.decode("utf-8") or "{}")
    except Exception:
        data = {}

    def value(name, default=""):
        return str(data.get(name, default) or default).strip()

    leave_date = value("leave_date")
    leave_type = value("leave_type")
    start_time = value("start_time")
    end_time = value("end_time")
    note = value("note")
    proof_image_data = value("proof_image_data")

    raw_leave_dates = data.get("leave_dates") or []
    leave_dates = []

    if isinstance(raw_leave_dates, list):
        for item in raw_leave_dates:
            v = str(item or "").strip()[:10]
            if v and v not in leave_dates:
                leave_dates.append(v)

    if leave_date and leave_date not in leave_dates:
        leave_dates.insert(0, leave_date)

    leave_dates = sorted([v for v in leave_dates if v])

    if leave_dates:
        leave_date = leave_dates[0]

    if not leave_date or not leave_type:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "請填寫日期與假別"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    proof_required = 1 if leave_type in ["病假", "公假", "喪假", "其他需證明"] else 0

    if proof_required and not proof_image_data:
        return _EmployeeSettingsResponse(
            content=_employee_settings_json.dumps({"ok": False, "error": "此假別需附上證明照片"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    new_ids = []

    with _employee_settings_engine.begin() as conn:
        for one_leave_date in leave_dates:
            conn.execute(
                _employee_settings_sql_text("""
                    INSERT INTO employee_leave_settings (
                        staff_code,
                        display_name,
                        department,
                        period_label,
                        leave_date,
                        leave_type,
                        start_time,
                        end_time,
                        proof_required,
                        proof_image_data,
                        note,
                        review_status,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        :staff_code,
                        :display_name,
                        :department,
                        :period_label,
                        :leave_date,
                        :leave_type,
                        :start_time,
                        :end_time,
                        :proof_required,
                        :proof_image_data,
                        :note,
                        '待審核',
                        datetime('now'),
                        datetime('now')
                    )
                """),
                {
                    "staff_code": user.get("staff_code") or "",
                    "display_name": user.get("display_name") or "",
                    "department": user.get("department") or "",
                    "period_label": _employee_leave_period_label(),
                    "leave_date": one_leave_date,
                    "leave_type": leave_type,
                    "start_time": start_time,
                    "end_time": end_time,
                    "proof_required": proof_required,
                    "proof_image_data": proof_image_data,
                    "note": note,
                },
            )

            new_ids.append(conn.execute(_employee_settings_sql_text("SELECT last_insert_rowid()")).scalar())

    new_id = new_ids[0] if new_ids else None

    return _EmployeeSettingsResponse(
        content=_employee_settings_json.dumps({"ok": True, "id": new_id, "ids": new_ids, "count": len(new_ids)}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )



@router.get("/app/employee/settings", response_class=_EmployeeSettingsHTMLResponse)
def employee_settings_page(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsRedirectResponse("/employee/login?next=/app/employee/settings", status_code=303)

    employee_display_name = str(user.get("display_name") or user.get("staff_code") or "\u767b\u5165\u8005")
    raw_return_to = str(request.query_params.get("return_to", "") or "").strip()

    def _safe_return_to(value: str) -> str:
        if not value or not value.startswith("/") or value.startswith("//"):
            return "/app/dispatch"
        if value.startswith("/employee/login") or value.startswith("/app/employee/settings"):
            return "/app/dispatch"
        return value

    employee_settings_return_to = _safe_return_to(raw_return_to)

    html = """
<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>員工設定｜訊南 ERP</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#eef3f9;color:#102348;font-family:"Noto Sans TC","Microsoft JhengHei",Arial,sans-serif;padding-bottom:92px}
.app-shell{max-width:520px;margin:0 auto;min-height:100vh;background:#eef3f9}
.content{padding:14px 16px 18px}
.card{background:#fff;border:1px solid #d7e1ef;border-radius:20px;padding:14px;box-shadow:0 8px 22px rgba(15,23,42,.06);margin-bottom:14px}
.profile-main{text-align:center;font-size:26px;font-weight:1000}
.profile-sub{text-align:center;color:#64748b;font-size:15px;font-weight:900;margin-top:6px}
.summary-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:14px}
.summary-card{border-radius:16px;background:#f8fafc;border:1px solid #e2e8f0;padding:10px 8px;text-align:center}
.summary-label{color:#64748b;font-size:12px;font-weight:1000}
.summary-value{font-size:24px;font-weight:1000}
.info-box{margin-top:12px;border-radius:16px;background:#fff7ed;border:1px solid #fdba74;padding:10px 12px;font-size:15px;font-weight:900;line-height:1.55}
.proxy-box{margin-top:12px;border-radius:16px;background:#eef6ff;border:1px solid #bfdbfe;padding:10px 12px;font-size:14px;font-weight:900;line-height:1.55}
.proxy-actions{display:grid;gap:8px;margin-top:8px}
.proxy-btn{width:100%;min-height:44px;border:0;border-radius:14px;background:#365ee8;color:#fff;font-size:15px;font-weight:1000}
.proxy-btn.gray{background:#64748b}
.proxy-btn.red{background:#dc2626}
.menu-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.menu-btn{height:64px;border:0;border-radius:18px;background:#fff;color:#102348;box-shadow:0 8px 20px rgba(15,23,42,.08);font-size:16px;font-weight:1000}
.modal-mask{position:fixed;inset:0;background:rgba(15,23,42,.46);z-index:50;display:none;align-items:flex-end;justify-content:center}
.modal-mask.active{display:flex}
.modal{width:100%;max-width:520px;max-height:88vh;overflow-y:auto;background:#fff;border-top-left-radius:26px;border-top-right-radius:26px;padding:18px 16px calc(20px + env(safe-area-inset-bottom))}
.modal-head{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;margin-bottom:12px}
.modal-title{font-size:24px;font-weight:1000}
.close-btn{width:78px;height:40px;border:0;border-radius:14px;background:#64748b;color:#fff;font-size:16px;font-weight:1000}
.form-card{border-radius:18px;background:#f8fafc;border:1px solid #e2e8f0;padding:14px;margin-bottom:12px}
label{display:block;color:#475569;font-size:14px;font-weight:1000;margin:12px 0 6px}
input,select,textarea{width:100%;min-height:46px;border-radius:15px;border:1px solid #cbd5e1;padding:0 14px;color:#102348;font-size:16px;font-weight:900;background:#fff}
textarea{min-height:84px;padding:12px 14px}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.hint{color:#64748b;font-size:13px;font-weight:850;line-height:1.45;margin-top:6px}
.primary-btn{width:100%;height:52px;border:0;border-radius:18px;background:#16a34a;color:#fff;font-size:18px;font-weight:1000;margin-top:14px}
.calendar-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin:10px 0 14px}
.day-cell,.week-cell{min-height:42px;border-radius:12px;border:1px solid #d8e2ef;background:#fff;font-weight:900}
.week-cell{border:0;background:transparent;color:#475569}
.day-cell.blank{visibility:hidden}
.day-cell.weekend,.day-cell.holiday{background:#fff1f2;border-color:#fecdd3}
.day-cell.selected{border:2px solid #dc2626;background:#fff7ed}
.leave-list{display:grid;gap:10px}
.leave-item{border-radius:16px;background:#f8fafc;border:1px solid #e2e8f0;padding:12px}
.leave-main{font-size:17px;font-weight:1000}
.leave-sub{margin-top:5px;color:#64748b;font-size:13px;font-weight:900;line-height:1.4}
.bottom-nav{position:fixed;left:0;right:0;bottom:0;padding:12px 14px calc(12px + env(safe-area-inset-bottom));background:rgba(238,243,249,.94);display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:520px;margin:0 auto;border-top:1px solid #d7e1ef}
.bottom-nav button{height:54px;border:0;border-radius:18px;background:#fff;color:#102348;font-size:16px;font-weight:1000}
.bottom-nav button.primary{background:#365ee8;color:#fff}
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
        <h1 class="hero-title">\u8a0a\u5357\u5de5\u4f5c\u7ba1\u7406\u7cfb\u7d71</h1>
      </div>
      <div id="hero_sub" class="hero-sub">__EMPLOYEE_DISPLAY_NAME__</div>
    </section>

<main class="content">
<section class="card">
  <div id="profile_main" class="profile-main">資料載入中...</div>
  <div id="profile_sub" class="profile-sub"></div>
  <div class="summary-grid">
    <div class="summary-card"><div class="summary-label">今年特休總數</div><div id="annual_total" class="summary-value">0</div></div>
    <div class="summary-card"><div class="summary-label">已請特休</div><div id="annual_used" class="summary-value">0</div></div>
    <div class="summary-card"><div class="summary-label">剩餘特休</div><div id="annual_remaining" class="summary-value">0</div></div>
  </div>
  <div class="info-box">
    <div><b>目前代理人：</b><span id="proxy_current">尚未設定</span></div>
    <div><b>目前代理誰：</b><span id="proxy_representing">無</span></div>
  </div>
  <div class="proxy-box">
    <div><b>目前身分：</b><span id="proxy_context_current">本人</span></div>
    <div><b>權限來源：</b><span id="proxy_context_permission">本人</span></div>
    <div id="proxy_context_actions" class="proxy-actions"></div>
  </div>
</section>

<section class="card">
  <div class="menu-grid">
    <button class="menu-btn" onclick="openPanel('password')">密碼設定</button>
    <button class="menu-btn" onclick="openPanel('rest')">休假設定</button>
    <button class="menu-btn" onclick="openPanel('leave')">請假設定</button>
    <button class="menu-btn" onclick="openPanel('query')">休假查詢</button>
    <button class="menu-btn" onclick="openPanel('proxy')">代理人設定</button>
  </div>
</section>
</main>

<nav class="bottom-nav">
  <button onclick="location.href='__RETURN_TO__'">返回上一頁</button>
  <button class="primary" onclick="loadAll()">重新整理</button>
</nav>
</div>

<div id="modal_mask" class="modal-mask">
<section class="modal">
<div class="modal-head"><div id="modal_title" class="modal-title">設定</div><button class="close-btn" onclick="closePanel()">關閉</button></div>

<div id="panel_password" class="panel">
<div class="form-card">
<label>舊密碼</label><input id="old_pin" type="password" inputmode="numeric">
<label>新密碼</label><input id="new_pin" type="password" inputmode="numeric">
<label>再次輸入新密碼</label><input id="new_pin2" type="password" inputmode="numeric">
<button class="primary-btn" onclick="changePassword()">儲存密碼</button>
</div>
</div>

<div id="panel_rest" class="panel">
<div class="form-card">
<div class="grid-2"><select id="rest_year" onchange="loadRestMonth()"></select><select id="rest_month" onchange="loadRestMonth()"></select></div>
<div id="rest_summary" class="hint">請選擇排休日期</div>
<div id="calendar_grid" class="calendar-grid"></div>
<button class="primary-btn" onclick="saveRestMonth(false)">完成並送出</button>
</div>
</div>

<div id="panel_leave" class="panel">
<div class="form-card">
<label>假別</label><select id="leave_type"><option value="事假">事假</option><option value="病假">病假（需證明）</option><option value="公假">公假（需證明）</option><option value="喪假">喪假（需證明）</option><option value="特休">特休</option><option value="其他需證明">其他需證明</option></select>
<label>日期</label><input id="leave_date_display" readonly onclick="toggleLeaveCalendar()" placeholder="請選擇請假日期">
<div id="leave_calendar_box" style="display:none;margin-top:8px">
<div class="grid-2"><select id="leave_calendar_year" onchange="renderLeaveCalendar()"></select><select id="leave_calendar_month" onchange="renderLeaveCalendar()"></select></div>
<div id="leave_calendar_summary" class="hint">請選擇請假日期</div>
<div id="leave_calendar_grid" class="calendar-grid"></div>
<button class="primary-btn" onclick="toggleLeaveCalendar()">完成選日期</button>
</div>
<div class="grid-2"><div><label>開始時間</label><input id="start_time" type="time"></div><div><label>結束時間</label><input id="end_time" type="time"></div></div>
<label>證明照片</label><input id="proof_photo" type="file" accept="image/*">
<label>備註</label><textarea id="note"></textarea>
<button class="primary-btn" onclick="submitLeaveSetting()">送出請假</button>
</div>
</div>

<div id="panel_query" class="panel">
<div id="query_summary" class="form-card">查詢資料載入中...</div>
<div class="form-card"><div id="leave_list" class="leave-list">資料載入中...</div></div>
</div>

<div id="panel_proxy" class="panel">
<div class="form-card">
<label>代理人一</label><input id="proxy_one" list="proxy_employee_options" autocomplete="off">
<label>代理人二</label><input id="proxy_two" list="proxy_employee_options" autocomplete="off">
<datalist id="proxy_employee_options"></datalist>
<button class="primary-btn" onclick="saveProxy()">儲存代理人</button>
</div>
</div>

</section>
</div>

<script>
let profileData=null, selectedRestDates=[], requiredRestDays=8, holidayMap={}, leaveDates=[], leaveHolidayMap={};

function esc(v){return String(v??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}
function byId(id){return document.getElementById(id)}
function hidePanels(){document.querySelectorAll(".panel").forEach(p=>p.style.display="none")}
function openPanel(name){hidePanels();byId("modal_mask").classList.add("active");byId("panel_"+name).style.display="block";byId("modal_title").textContent={password:"密碼設定",rest:"休假設定",leave:"請假設定",query:"休假查詢",proxy:"代理人設定"}[name]||"設定"; if(name==="rest")loadRestMonth(); if(name==="query")loadRestQuery(); if(name==="proxy")loadProxyOptions(); if(name==="leave")initLeaveCalendar();}
function closePanel(){byId("modal_mask").classList.remove("active");hidePanels()}
function dateKey(y,m,d){return y+"-"+String(m).padStart(2,"0")+"-"+String(d).padStart(2,"0")}
function rocYear(y){return Number(y)-1911}
function fileToBase64(file){return new Promise((resolve,reject)=>{if(!file){resolve("");return}const r=new FileReader();r.onload=()=>resolve(String(r.result||""));r.onerror=reject;r.readAsDataURL(file)})}

async function loadProfile(){
  const res=await fetch("/api/app/employee/profile?ts="+Date.now(),{cache:"no-store",credentials:"same-origin"});
  if(res.status===401){location.href="/employee/login?next=/app/employee/settings";return}
  const data=await res.json(); profileData=data;
  const p=data.profile||{};
  byId("profile_main").textContent=(p.display_name||"-")+"｜"+(p.staff_code||"-");
  byId("profile_sub").textContent=(p.department||"-")+"｜"+(p.position_title||"未設定職稱")+"｜角色："+(p.role||"-");
  byId("hero_sub").textContent=p.display_name||p.staff_code||"\u767b\u5165\u8005";
  byId("annual_total").textContent=data.annual_leave_total??0;
  byId("annual_used").textContent=data.annual_leave_used??0;
  byId("annual_remaining").textContent=data.annual_leave_remaining??0;
  const proxy=data.proxy||{};
  const names=[];
  function line(name,status){if(!name)return""; if(status==="accepted")return name+"（已同意）"; if(status==="pending")return name+"（審核中）"; return name}
  const one=line(proxy.proxy_one_name||proxy.proxy_one_staff_code,proxy.proxy_one_status);
  const two=line(proxy.proxy_two_name||proxy.proxy_two_staff_code,proxy.proxy_two_status);
  if(one)names.push(one); if(two)names.push(two);
  byId("proxy_current").textContent=names.length?names.join("、"):"尚未設定";
  const reps=data.represented_employees||[];
  byId("proxy_representing").textContent=reps.length?reps.map(x=>x.display_name||x.staff_code).join("、"):"無";
}

async function loadProxyContext(){
  const res=await fetch("/api/app/employee/proxy/context?ts="+Date.now(),{cache:"no-store",credentials:"same-origin"});
  const ctx=await res.json();
  const current=byId("proxy_context_current"), permission=byId("proxy_context_permission"), actions=byId("proxy_context_actions");
  if(!ctx.ok){actions.innerHTML="<div class='hint'>代理資料讀取失敗</div>";return}
  let html="";
  if(ctx.is_proxy_mode){
    current.textContent="代理 "+(ctx.acting_display_name||ctx.acting_staff_code);
    permission.textContent=ctx.permission_owner_name||ctx.permission_owner_code;
    html += `<button class="proxy-btn gray" onclick="clearProxy()">結束代理，切回本人</button>`;
  }else{
    current.textContent="本人";
    permission.textContent="本人";
    (ctx.available_targets||[]).forEach(t=>{html += `<button class="proxy-btn" onclick="switchProxy('${esc(t.staff_code)}')">切換為代理 ${esc(t.display_name||t.staff_code)}${t.department?"｜"+esc(t.department):""}</button>`});
  }
  const proxy=(profileData&&profileData.proxy)||{};
  function revoke(slot,code,name,status){if(!code)return; const st=status==="accepted"?"已同意":(status==="pending"?"審核中":status||""); html += `<button class="proxy-btn red" onclick="revokeProxy('${slot}')">撤銷代理 ${esc(name||code)}${st?"｜"+esc(st):""}</button>`}
  revoke("one",proxy.proxy_one_staff_code,proxy.proxy_one_name,proxy.proxy_one_status);
  revoke("two",proxy.proxy_two_staff_code,proxy.proxy_two_name,proxy.proxy_two_status);
  actions.innerHTML=html||"<div class='hint'>目前沒有代理設定。</div>";
}

async function switchProxy(code){
  const res=await fetch("/api/app/employee/proxy/switch",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json; charset=utf-8"},body:JSON.stringify({acting_staff_code:code})});
  const data=await res.json().catch(()=>({}));
  if(!res.ok||!data.ok){alert(data.error||"切換代理失敗");return}
  alert("已切換為代理："+(data.acting_display_name||code));
  await loadAll();
}
async function clearProxy(){
  const res=await fetch("/api/app/employee/proxy/clear",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json; charset=utf-8"},body:JSON.stringify({})});
  const data=await res.json().catch(()=>({}));
  if(!res.ok||!data.ok){alert(data.error||"結束代理失敗");return}
  alert("已切回本人");
  location.reload();
}
async function revokeProxy(slot){
  if(!confirm("確定要撤銷這個代理人嗎？"))return;
  const res=await fetch("/api/app/employee/proxy/revoke",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json; charset=utf-8"},body:JSON.stringify({slot})});
  const data=await res.json().catch(()=>({}));
  if(!res.ok||!data.ok){alert(data.error||"撤銷代理失敗");return}
  alert("已撤銷代理。對方重新整理或重新登入後會回到本人權限。");
  await loadAll();
}

async function changePassword(){
  const res=await fetch("/api/app/employee/change-password",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json; charset=utf-8"},body:JSON.stringify({old_pin:byId("old_pin").value,new_pin:byId("new_pin").value,new_pin2:byId("new_pin2").value})});
  const data=await res.json().catch(()=>({}));
  if(!res.ok||!data.ok){alert(data.error||"密碼修改失敗");return}
  alert("密碼已更新"); ["old_pin","new_pin","new_pin2"].forEach(id=>byId(id).value=""); closePanel();
}

function initMonthOptions(){
  const now=new Date(), y=byId("rest_year"), m=byId("rest_month");
  y.innerHTML=""; for(let yy=now.getFullYear()-1;yy<=now.getFullYear()+1;yy++)y.innerHTML+=`<option value="${yy}">${yy} 年</option>`; y.value=now.getFullYear();
  m.innerHTML=""; for(let mm=1;mm<=12;mm++)m.innerHTML+=`<option value="${mm}">${mm} 月</option>`; m.value=now.getMonth()+1;
}
async function loadHolidays(year){
  holidayMap={}; const res=await fetch("/api/app/employee/holidays?year="+year+"&ts="+Date.now(),{cache:"no-store",credentials:"same-origin"}); if(!res.ok)return;
  const data=await res.json(); (data.items||[]).forEach(i=>holidayMap[i.holiday_date]=i.title||"國定假日");
}
async function loadRestMonth(){
  const y=Number(byId("rest_year").value), m=Number(byId("rest_month").value); await loadHolidays(y);
  const res=await fetch(`/api/app/employee/rest-month?year=${y}&month=${m}&ts=${Date.now()}`,{cache:"no-store",credentials:"same-origin"});
  const data=await res.json(); selectedRestDates=data.selected_dates||[]; requiredRestDays=Number(data.required_rest_days||8); renderRestCalendar(y,m);
}
function renderRestCalendar(y,m){
  const box=byId("calendar_grid"), days=new Date(y,m,0).getDate(), start=new Date(y,m-1,1).getDay(); let html=["日","一","二","三","四","五","六"].map(w=>`<button class="week-cell" disabled>${w}</button>`).join("");
  for(let i=0;i<start;i++)html+=`<button class="day-cell blank"></button>`;
  for(let d=1;d<=days;d++){const key=dateKey(y,m,d), wk=new Date(y,m-1,d).getDay(), sel=selectedRestDates.includes(key), hol=holidayMap[key]; html+=`<button class="day-cell ${wk===0||wk===6?"weekend":""} ${hol?"holiday":""} ${sel?"selected":""}" onclick="toggleRestDate('${key}')">${d}${hol?`<br><small>${esc(hol)}</small>`:""}</button>`}
  box.innerHTML=html; const missing=Math.max(0,requiredRestDays-selectedRestDates.length); byId("rest_summary").textContent=`已選 ${selectedRestDates.length} 天｜應選 ${requiredRestDays} 天${missing?`｜尚缺 ${missing} 天`:"｜已達標"}`;
}
function toggleRestDate(k){selectedRestDates=selectedRestDates.includes(k)?selectedRestDates.filter(x=>x!==k):selectedRestDates.concat([k]).sort(); renderRestCalendar(Number(byId("rest_year").value),Number(byId("rest_month").value))}
async function saveRestMonth(force){
  const y=Number(byId("rest_year").value), m=Number(byId("rest_month").value);
  const res=await fetch("/api/app/employee/rest-month/save",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json; charset=utf-8"},body:JSON.stringify({year:y,month:m,selected_dates:selectedRestDates,force:Boolean(force)})});
  const data=await res.json().catch(()=>({}));
  if(res.status===409&&data.need_confirm){if(confirm(data.error+" 是否仍要繼續送出？"))saveRestMonth(true);return}
  if(!res.ok||!data.ok){alert(data.error||"休假設定儲存失敗");return}
  alert("休假設定已送出"); closePanel();
}

function initLeaveCalendar(){
  const now=new Date(), y=byId("leave_calendar_year"), m=byId("leave_calendar_month");
  if(!y.options.length){for(let yy=now.getFullYear()-1;yy<=now.getFullYear()+1;yy++)y.innerHTML+=`<option value="${yy}">民國${rocYear(yy)}年</option>`; y.value=now.getFullYear();}
  if(!m.options.length){for(let mm=1;mm<=12;mm++)m.innerHTML+=`<option value="${mm}">${mm}月</option>`; m.value=now.getMonth()+1;}
  updateLeaveDisplay();
}
function toggleLeaveCalendar(){const box=byId("leave_calendar_box"); box.style.display=box.style.display==="none"?"block":"none"; renderLeaveCalendar();}
async function renderLeaveCalendar(){
  initLeaveCalendar(); const y=Number(byId("leave_calendar_year").value), m=Number(byId("leave_calendar_month").value);
  leaveHolidayMap={}; try{const res=await fetch(`/api/app/employee/holidays?year=${y}&ts=${Date.now()}`,{cache:"no-store",credentials:"same-origin"}); const data=await res.json(); (data.items||[]).forEach(i=>leaveHolidayMap[i.holiday_date]=i.title||"國定假日")}catch(e){}
  const box=byId("leave_calendar_grid"), days=new Date(y,m,0).getDate(), start=new Date(y,m-1,1).getDay(); let html=["日","一","二","三","四","五","六"].map(w=>`<button class="week-cell" disabled>${w}</button>`).join("");
  for(let i=0;i<start;i++)html+=`<button class="day-cell blank"></button>`;
  for(let d=1;d<=days;d++){const key=dateKey(y,m,d), wk=new Date(y,m-1,d).getDay(), sel=leaveDates.includes(key), hol=leaveHolidayMap[key]; html+=`<button class="day-cell ${wk===0||wk===6?"weekend":""} ${hol?"holiday":""} ${sel?"selected":""}" onclick="toggleLeaveDate('${key}')">${d}${hol?`<br><small>${esc(hol)}</small>`:""}</button>`}
  box.innerHTML=html; updateLeaveDisplay();
}
function toggleLeaveDate(k){leaveDates=leaveDates.includes(k)?leaveDates.filter(x=>x!==k):leaveDates.concat([k]).sort(); renderLeaveCalendar();}
function updateLeaveDisplay(){byId("leave_date_display").value=leaveDates.join("、"); byId("leave_calendar_summary").textContent=leaveDates.length?`已選 ${leaveDates.length} 天`:"請選擇請假日期";}
async function submitLeaveSetting(){
  if(!leaveDates.length){alert("請選擇請假日期");return}
  const type=byId("leave_type").value, file=byId("proof_photo").files[0];
  if(["病假","公假","喪假","其他需證明"].includes(type)&&!file){alert("此假別需附上證明照片");return}
  const proof=await fileToBase64(file);
  const res=await fetch("/api/app/employee/leave-settings/create",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json; charset=utf-8"},body:JSON.stringify({leave_type:type,leave_date:leaveDates[0],leave_dates:leaveDates,start_time:byId("start_time").value,end_time:byId("end_time").value,note:byId("note").value,proof_image_data:proof})});
  const data=await res.json().catch(()=>({})); if(!res.ok||!data.ok){alert(data.error||"送出失敗");return}
  alert(`已送出請假申請，共 ${leaveDates.length} 天`); leaveDates=[]; ["start_time","end_time","note","proof_photo","leave_date_display"].forEach(id=>byId(id).value=""); closePanel(); loadAll();
}

async function loadRestQuery(){
  const now=new Date(); const y=now.getFullYear(), m=now.getMonth()+1;
  const res=await fetch(`/api/app/employee/rest-query?year=${y}&month=${m}&ts=${Date.now()}`,{cache:"no-store",credentials:"same-origin"}); const data=await res.json().catch(()=>({}));
  byId("query_summary").innerHTML=`今年總共假日：${esc(data.annual_total_rest_days||0)} 天<br>已休：${esc(data.annual_used_rest_days||0)} 天`;
  const items=data.monthly_items||[]; byId("leave_list").innerHTML=items.length?items.map(i=>`<div class="leave-item"><div class="leave-main">${esc(i.rest_date)}｜${esc(i.rest_type||"排休")}｜${esc(i.review_status||"待審核")}</div><div class="leave-sub">${esc(i.updated_at||"")}</div></div>`).join(""):"<div class='hint'>本月尚無已設定休假。</div>";
}

async function loadProxyOptions(){
  const res=await fetch("/api/app/employee/list-for-proxy?ts="+Date.now(),{cache:"no-store",credentials:"same-origin"}); const data=await res.json().catch(()=>({}));
  const list=byId("proxy_employee_options"); list.innerHTML=(data.items||[]).map(i=>`<option value="${esc(i.staff_code+"｜"+i.display_name+"｜"+i.department)}"></option>`).join("");
  const p=(profileData&&profileData.proxy)||{}; byId("proxy_one").value=p.proxy_one_staff_code?`${p.proxy_one_staff_code}｜${p.proxy_one_name||""}`:""; byId("proxy_two").value=p.proxy_two_staff_code?`${p.proxy_two_staff_code}｜${p.proxy_two_name||""}`:"";
}
function proxyCode(raw){raw=String(raw||"").trim(); return raw.includes("｜")?raw.split("｜")[0].trim():raw}
async function saveProxy(){
  const res=await fetch("/api/app/employee/proxy/save",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json; charset=utf-8"},body:JSON.stringify({proxy_one_staff_code:proxyCode(byId("proxy_one").value),proxy_two_staff_code:proxyCode(byId("proxy_two").value)})});
  const data=await res.json().catch(()=>({})); if(!res.ok||!data.ok){alert(data.error||"代理人設定失敗");return}
  alert("代理人邀請已送出，待對方同意後才會生效。"); closePanel(); loadAll();
}

async function checkPendingProxy(){
  const res=await fetch("/api/app/employee/proxy/pending-requests?ts="+Date.now(),{cache:"no-store",credentials:"same-origin"}); if(!res.ok)return;
  const data=await res.json(); for(const item of data.items||[]){if(confirm(`${item.requester_name||item.requester_staff_code} 指定你為代理人，是否同意？`)){await fetch("/api/app/employee/proxy/respond",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json; charset=utf-8"},body:JSON.stringify({requester_staff_code:item.requester_staff_code,slot:item.slot,action:"accept"})}); alert("已同意代理人邀請");}}
}

async function loadAll(){await loadProfile(); await loadProxyContext();}
initMonthOptions(); initLeaveCalendar(); hidePanels(); loadAll(); setTimeout(checkPendingProxy,800);
</script>

<script>
(function(){
  function tuneAppHomeHeader(){
  }
  tuneAppHomeHeader();
  setTimeout(tuneAppHomeHeader, 300);
})();
</script>


<script>
(function(){
  function fixHeroSub(){
  }
  fixHeroSub();
  setTimeout(fixHeroSub, 100);
  setTimeout(fixHeroSub, 500);
})();
</script>

</body>
</html>
"""
    return (
        html
        .replace("__EMPLOYEE_DISPLAY_NAME__", employee_display_name)
        .replace("__RETURN_TO__", employee_settings_return_to)
    )
# SHINNAN_EMPLOYEE_SETTINGS_END



# XN_UNIFIED_APP_HOME_V1_START
@router.get("/app", response_class=_EmployeeSettingsHTMLResponse)
def unified_mobile_app_home(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsRedirectResponse("/employee/login?next=/app", status_code=303)

    _employee_settings_db_init()

    staff_code = str(user.get("staff_code") or "").strip()
    display_name = str(user.get("display_name") or "").strip() or staff_code
    department = str(user.get("department") or "").strip()
    role = str(user.get("role") or "").strip()

    app_access = []

    with _employee_settings_engine.begin() as conn:
        row = conn.execute(
            _employee_settings_sql_text("""
                SELECT app_access
                FROM employee_profiles
                WHERE staff_code = :staff_code
                LIMIT 1
            """),
            {"staff_code": staff_code},
        ).mappings().first()

        if row:
            raw = str(row.get("app_access") or "").strip()
            if raw:
                try:
                    parsed = _employee_settings_json.loads(raw)
                    if isinstance(parsed, list):
                        app_access = [str(x) for x in parsed]
                except Exception:
                    app_access = [x.strip() for x in raw.split(",") if x.strip()]

    is_admin = staff_code == "admin" or role == "admin"

    def can_open(key: str) -> bool:
        if is_admin:
            return True
        if key == "manager":
            return role == "manager" or "manager" in app_access or "admin" in app_access
        return key in app_access

    modules = [
        ("dispatch", "\u6d3e\u5de5\u7cfb\u7d71", "\u4eca\u65e5\u6848\u4ef6\u3001\u9818\u55ae\u3001\u65bd\u5de5\u6d41\u7a0b\u3001\u5b8c\u5de5\u56de\u5831", "/app/dispatch"),
        ("billing", "\u5e33\u52d9\u7cfb\u7d71", "\u5927\u6a13\u5e33\u55ae\u3001\u903e\u671f\u672a\u7e73\u3001\u5e33\u52d9\u4efb\u52d9", "/app/billing"),
        ("sales", "\u696d\u52d9\u7cfb\u7d71", "\u5927\u6a13\u62dc\u8a2a\u3001\u5408\u7d04\u8ffd\u8e64\u3001\u4e8b\u4ef6\u7ba1\u7406", "/app/sales"),
        ("engineering", "\u5de5\u7a0b\u7cfb\u7d71", "\u5de5\u7a0b\u6848\u4ef6\u3001\u65bd\u5de5\u7ba1\u7406\u3001\u5c08\u6848\u9032\u5ea6", "/app/engineering"),
        ("manager", "\u4e3b\u7ba1\u4e2d\u5fc3", "\u90e8\u9580\u6848\u4ef6\u3001\u5f85\u5be9\u6838\u3001\u4eba\u54e1\u72c0\u6cc1\u8207\u90e8\u9580\u7d71\u8a08", "/app/manager"),
    ]

    module_cards = []

    for key, title, desc, href in modules:
        if can_open(key):
            module_cards.append(f"""
              <a class="card module-card" href="{href}">
                <div class="card-title">{title}</div>
                <div class="card-desc">{desc}</div>
              </a>
            """)

    if not module_cards:
        module_cards.append("""
          <div class="card disabled-card">
            <div class="card-title">尚未開放權限模組</div>
            <div class="card-desc">目前帳號只有一般性功能。若需要派工、帳務、業務等功能，請由後台權限管理開通。</div>
          </div>
        """)

    user_line = user.get("display_name") or user.get("staff_code") or user.get("username") or "\u767b\u5165\u8005"

    html = f"""
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <title>訊南工作管理系統 首頁｜訊南 ERP</title>
  <style>
    * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
    body {{
      margin: 0;
      background: #eef3f9;
      color: #102348;
      font-family: "Noto Sans TC","Microsoft JhengHei",Arial,sans-serif;
    }}
    .app {{
      width: 100%;
      max-width: 520px;
      min-height: 100vh;
      margin: 0 auto;
      background: #eef3f9;
      padding-bottom: 22px;
    }}
    .content {{
      padding: 14px;
    }}
    .section-title {{
      margin: 14px 4px 9px;
      color: #475569;
      font-size: 15px;
      font-weight: 1000;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }}
    .card {{
      min-height: 98px;
      padding: 14px;
      border-radius: 20px;
      border: 1px solid #d7e1ef;
      background: #fff;
      color: #102348;
      text-decoration: none;
      box-shadow: 0 8px 22px rgba(15,23,42,.07);
      display: block;
    }}
    .card-title {{
      font-size: 19px;
      font-weight: 1000;
      line-height: 1.15;
    }}
    .card-desc {{
      margin-top: 7px;
      color: #64748b;
      font-size: 13px;
      line-height: 1.4;
      font-weight: 850;
    }}
    .general-card {{
      border-color: #bfdbfe;
      background: linear-gradient(135deg,#ffffff,#eff6ff);
    }}
    .module-card {{
      border-color: #c7d2fe;
    }}
    .disabled-card {{
      grid-column: 1 / -1;
      background: #f8fafc;
      border-style: dashed;
    }}
    .footer-actions {{
      margin-top: 16px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }}
    .btn {{
      height: 48px;
      border: 0;
      border-radius: 17px;
      background: #fff;
      color: #102348;
      font-size: 16px;
      font-weight: 1000;
      box-shadow: 0 8px 20px rgba(15,23,42,.08);
    }}
    .btn.red {{
      background: #dc2626;
      color: #fff;
    }}
    @media (max-width: 380px) {{
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
  <link rel="stylesheet" href="/static/app_header_unified.css?v=20260511_title_v1">
</head>
<body>
  <div class="app">
    
    <section class="hero app-standard-hero">
      <div class="hero-main">
        <span class="hero-logo">
          <img class="hero-logo-img" src="/static/shinnan_home_logo.png" alt="Logo">
        </span>
        <h1 class="hero-title">\u8a0a\u5357\u5de5\u4f5c\u7ba1\u7406\u7cfb\u7d71</h1>
      </div>
      <div class="hero-sub">{user_line}</div>
    </section>

    <main class="content">
      <div class="section-title">一般性功能</div>
      <section class="grid">
        <a class="card general-card" href="/app/employee/settings?return_to=/app">
          <div class="card-title">員工設定</div>
          <div class="card-desc">個人資料、PIN、代理人、假表與請假相關設定。</div>
        </a>
        <a class="card general-card" href="/app/employee/settings?return_to=/app#leave">
          <div class="card-title">請假申請</div>
          <div class="card-desc">無紙化請假、查看自己的申請與休假狀態。</div>
        </a>
        <a class="card general-card" href="/app/employee/settings?return_to=/app#rest">
          <div class="card-title">排休設定</div>
          <div class="card-desc">設定月休假表，送主管與人事審核。</div>
        </a>
        <a class="card general-card" href="/app/tools/calculator">
          <div class="card-title">實用工具</div>
          <div class="card-desc">預留計算機、常用換算、工作輔助工具。</div>
        </a>
      </section>

      <div class="section-title">權限模組</div>
      <section class="grid">
        {''.join(module_cards)}
      </section>

      <div class="footer-actions">
        <button class="btn" onclick="location.reload()">重新整理</button>
        <button class="btn red" onclick="location.href='/employee/logout?next=/employee/login'">登出</button>
      </div>
    </main>
  </div>
</body>
</html>
"""

    return _EmployeeSettingsHTMLResponse(content=html)
# XN_UNIFIED_APP_HOME_V1_END


# XN_APP_CALCULATOR_TOOL_V1_START
@router.get("/app/tools/calculator", response_class=_EmployeeSettingsHTMLResponse)
def unified_mobile_app_calculator(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmployeeSettingsRedirectResponse("/employee/login?next=/app/tools/calculator", status_code=303)

    display_name = str(user.get("display_name") or "").strip() or str(user.get("staff_code") or "")
    department = str(user.get("department") or "").strip()
    user_line = user.get("display_name") or user.get("staff_code") or user.get("username") or "\u767b\u5165\u8005"

    html = f"""
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <title>計算機｜訊南工作管理系統</title>
  <style>
    * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
    body {{
      margin:0;
      background:#eef3f9;
      color:#102348;
      font-family:"Noto Sans TC","Microsoft JhengHei",Arial,sans-serif;
    }}
    .app {{
      max-width:520px;
      min-height:100vh;
      margin:0 auto;
      background:#eef3f9;
      padding-bottom:20px;
    }}
    .content {{ padding:14px; }}
    .calc {{
      background:#fff;
      border:1px solid #d7e1ef;
      border-radius:24px;
      padding:14px;
      box-shadow:0 8px 22px rgba(15,23,42,.07);
    }}
    #display {{
      width:100%;
      height:64px;
      border:1px solid #cbd5e1;
      border-radius:18px;
      padding:0 14px;
      font-size:28px;
      font-weight:1000;
      text-align:right;
      color:#102348;
      background:#f8fafc;
      margin-bottom:12px;
    }}
    .keys {{
      display:grid;
      grid-template-columns:repeat(4,1fr);
      gap:9px;
    }}
    button {{
      height:58px;
      border:0;
      border-radius:18px;
      background:#fff;
      color:#102348;
      font-size:22px;
      font-weight:1000;
      box-shadow:0 7px 18px rgba(15,23,42,.08);
    }}
    button.op {{ background:#dbeafe; color:#1d4ed8; }}
    button.equal {{ background:#16a34a; color:#fff; }}
    button.clear {{ background:#fee2e2; color:#991b1b; }}
    .bottom {{
      display:grid;
      grid-template-columns:1fr 1fr;
      gap:10px;
      margin-top:14px;
    }}
    .bottom button {{
      height:50px;
      font-size:16px;
    }}
    .red {{ background:#dc2626 !important; color:#fff !important; }}
  </style>
  <link rel="stylesheet" href="/static/app_header_unified.css?v=20260511_title_v1">
</head>
<body>
  <div class="app">
    <section class="hero app-standard-hero">
      <div class="hero-main">
        <span class="hero-logo">
          <img class="hero-logo-img" src="/static/shinnan_home_logo.png" alt="Logo">
        </span>
        <h1 class="hero-title">\u5be6\u7528\u5de5\u5177</h1>
      </div>
      <div class="hero-sub">{user_line}</div>
    </section>

    <main class="content">
      <section class="calc">
        <input id="display" value="0" readonly>
        <div class="keys">
          <button class="clear" onclick="clearDisplay()">C</button>
          <button onclick="backspace()">⌫</button>
          <button class="op" onclick="appendValue('%')">%</button>
          <button class="op" onclick="appendValue('/')">÷</button>

          <button onclick="appendValue('7')">7</button>
          <button onclick="appendValue('8')">8</button>
          <button onclick="appendValue('9')">9</button>
          <button class="op" onclick="appendValue('*')">×</button>

          <button onclick="appendValue('4')">4</button>
          <button onclick="appendValue('5')">5</button>
          <button onclick="appendValue('6')">6</button>
          <button class="op" onclick="appendValue('-')">−</button>

          <button onclick="appendValue('1')">1</button>
          <button onclick="appendValue('2')">2</button>
          <button onclick="appendValue('3')">3</button>
          <button class="op" onclick="appendValue('+')">＋</button>

          <button onclick="appendValue('0')">0</button>
          <button onclick="appendValue('00')">00</button>
          <button onclick="appendValue('.')">.</button>
          <button class="equal" onclick="calculate()">=</button>
        </div>
      </section>

      <div class="bottom">
        <button onclick="location.href='/app'">APP首頁</button>
        <button class="red" onclick="location.href='/employee/logout?next=/employee/login'">登出</button>
      </div>
    </main>
  </div>

<script>
function display() {{
  return document.getElementById("display");
}}

function appendValue(v) {{
  const d = display();
  if (d.value === "0" || d.value === "錯誤") d.value = "";
  d.value += v;
}}

function clearDisplay() {{
  display().value = "0";
}}

function backspace() {{
  const d = display();
  d.value = d.value.length > 1 ? d.value.slice(0, -1) : "0";
}}

function calculate() {{
  const d = display();
  try {{
    const expr = d.value.replace(/[^0-9.+\\-*/%()]/g, "");
    const result = Function('"use strict"; return (' + expr + ')')();
    d.value = Number.isFinite(result) ? String(Math.round(result * 100000000) / 100000000) : "錯誤";
  }} catch (e) {{
    d.value = "錯誤";
  }}
}}
</script>
</body>
</html>
"""
    return _EmployeeSettingsHTMLResponse(content=html)
# XN_APP_CALCULATOR_TOOL_V1_END


# XN_MANAGER_CENTER_SIMPLE_V2_START
@router.get("/app/manager", response_class=_EmployeeSettingsHTMLResponse)
def manager_center_mobile_app_v2(request: _EmpRequest):
    user = _employee_current_user_from_request(request)
    if not user:
        return _EmployeeSettingsRedirectResponse("/employee/login?next=/app/manager", status_code=303)

    staff_code = str(user.get("staff_code") or "")
    display_name = str(user.get("display_name") or staff_code)
    department = str(user.get("department") or "")
    role = str(user.get("role") or "")

    if role not in ("admin", "manager") and staff_code != "admin":
        return _EmployeeSettingsHTMLResponse("<h2>\u6c92\u6709\u4e3b\u7ba1\u4e2d\u5fc3\u6b0a\u9650</h2><button onclick=\"location.href='/app'\">\u8fd4\u56deAPP\u9996\u9801</button>", status_code=403)

    user_line = user.get("display_name") or user.get("staff_code") or user.get("username") or "\u767b\u5165\u8005"

    return _EmployeeSettingsHTMLResponse(f"""
<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>\u4e3b\u7ba1\u4e2d\u5fc3\uff5c\u8a0a\u5357 ERP</title>
<style>
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: #eef3f9;
  color: #102348;
  font-family: 'Microsoft JhengHei', Arial, sans-serif;
}}
.app-shell {{
  max-width: 520px;
  margin: 0 auto;
  min-height: 100vh;
  background: #eef3f9;
}}
.content {{ padding: 16px; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.card {{
  background: white;
  border: 1px solid #d7e1ef;
  border-radius: 20px;
  padding: 18px;
  text-decoration: none;
  color: #102348;
  box-shadow: 0 8px 22px rgba(15,23,42,.08);
}}
.card-title {{ font-size: 22px; font-weight: 1000; }}
.card-desc {{ margin-top: 8px; color: #64748b; font-size: 14px; font-weight: 800; line-height: 1.4; }}
.bottom {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 18px; }}
button {{ height: 50px; border: 0; border-radius: 16px; background: white; color: #102348; font-size: 17px; font-weight: 1000; }}
.red {{ background: #dc2626; color: white; }}
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
        <h1 class="hero-title">\u4e3b\u7ba1\u4e2d\u5fc3</h1>
      </div>
      <div class="hero-sub">{user_line}</div>
    </section>

  <main class="content">
    <div class="grid">
      <a class="card" href="/app/manager/department-cases"><div class="card-title">\u90e8\u9580\u6848\u4ef6</div><div class="card-desc">\u67e5\u770b\u90e8\u9580\u4eca\u65e5\u6848\u4ef6\u3001\u6848\u4ef6\u8ca0\u8f09\u8207\u65bd\u5de5\u4eba\u54e1\u6307\u6d3e\u3002</div></a>
      <a class="card" href="/app/manager/approvals"><div class="card-title">\u5f85\u5be9\u6838</div><div class="card-desc">\u8655\u7406\u8acb\u5047\u3001\u6392\u4f11\u6708\u8868\u8207\u5176\u4ed6\u5f85\u5be9\u6838\u4e8b\u9805\u3002</div></a>
      <a class="card" href="/app/manager/staff-status"><div class="card-title">\u4eba\u54e1\u72c0\u6cc1</div><div class="card-desc">\u67e5\u770b\u90e8\u9580\u4eba\u54e1\u51fa\u52e4\u3001\u4f11\u5047\u8207\u5de5\u4f5c\u72c0\u614b\u3002</div></a>
      <a class="card" href="/app/manager/stats"><div class="card-title">\u90e8\u9580\u7d71\u8a08</div><div class="card-desc">\u67e5\u770b\u90e8\u9580\u6848\u4ef6\u6578\u3001\u8ca0\u8f09\u3001\u4eba\u529b\u8207\u71df\u904b\u7d71\u8a08\u3002</div></a>
    </div>
    <div class="bottom">
      <button onclick="location.href='/app'">APP\u9996\u9801</button>
      <button class="red" onclick="location.href='/employee/logout?next=/employee/login'">\u767b\u51fa</button>
    </div>
  </main>
</div>
</body>
</html>
""")
# XN_MANAGER_CENTER_SIMPLE_V2_END


