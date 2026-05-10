import json as _employee_profile_json

from fastapi import APIRouter
from fastapi.responses import Response as _EmployeeProfileResponse
from sqlalchemy import text as _employee_profile_sql_text

from app.db import engine as _employee_profile_engine

router = APIRouter(tags=["employee-profiles-admin"])


# SHINNAN_EMPLOYEE_PROFILES_API_START
def _employee_profiles_db_init():
    with _employee_profile_engine.begin() as conn:
        table_exists = conn.execute(
            _employee_profile_sql_text(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'employee_profiles' LIMIT 1"
            )
        ).first()

        if not table_exists:
            conn.execute(_employee_profile_sql_text("""
                CREATE TABLE IF NOT EXISTS employee_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_code TEXT UNIQUE NOT NULL,
                    display_name TEXT NOT NULL,
                    department TEXT DEFAULT '',
                    role TEXT DEFAULT '',
                    position_title TEXT DEFAULT '',
                    gender TEXT DEFAULT '',
                    phone TEXT DEFAULT '',
                    email TEXT DEFAULT '',
                    employment_status TEXT DEFAULT '在職',
                    hire_date TEXT DEFAULT '',
                    permission_scope TEXT DEFAULT '',
                    app_access INTEGER DEFAULT 1,
                    note TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """))



@router.get("/api/admin/employees", summary="讀取員工主檔")
def api_admin_employees(
    department: str = "全部",
    role: str = "全部",
    status: str = "全部",
    q: str = "",
):
    _employee_profiles_db_init()

    where = []
    params = {}

    if department and department != "全部":
        where.append("department = :department")
        params["department"] = department

    if role and role != "全部":
        where.append("role = :role")
        params["role"] = role

    if status and status != "全部":
        where.append("employment_status = :status")
        params["status"] = status

    if q:
        where.append("""
            (
                staff_code LIKE :q OR
                display_name LIKE :q OR
                phone LIKE :q OR
                department LIKE :q OR
                position_title LIKE :q
            )
        """)
        params["q"] = "%" + q + "%"

    where_sql = ""
    if where:
        where_sql = "WHERE " + " AND ".join(where)

    with _employee_profile_engine.begin() as conn:
        cols = [row[1] for row in conn.execute(_employee_profile_sql_text("PRAGMA table_info(employee_profiles)")).fetchall()]
        note_expr = "note" if "note" in cols else "'' AS note"

        rows = conn.execute(
            _employee_profile_sql_text(f"""
                SELECT
                    staff_code,
                    display_name,
                    department,
                    role,
                    position_title,
                    gender,
                    phone,
                    email,
                    employment_status,
                    hire_date,
                    permission_scope,
                    app_access,
                    {note_expr},
                    created_at,
                    updated_at
                FROM employee_profiles
                {where_sql}
                ORDER BY
                    CASE department
                        WHEN '管理部' THEN 1
                        WHEN '業務部' THEN 2
                        WHEN '工程部' THEN 3
                        WHEN '維修部' THEN 4
                        WHEN '北高' THEN 5
                        WHEN '南高' THEN 6
                        WHEN '東區' THEN 7
                        WHEN '安平' THEN 8
                        WHEN '北區' THEN 9
                        WHEN '永康' THEN 10
                        WHEN '北台南' THEN 11
                        WHEN '帳務部' THEN 12
                        WHEN '人事部' THEN 13
                        WHEN '客服部' THEN 14
                        WHEN '倉管部' THEN 15
                        WHEN '專案部' THEN 16
                        WHEN '產品部' THEN 17
                        ELSE 99
                    END,
                    staff_code
            """),
            params,
        ).mappings().fetchall()

    return _EmployeeProfileResponse(
        content=_employee_profile_json.dumps([dict(row) for row in rows], ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )
# SHINNAN_EMPLOYEE_PROFILES_API_END
