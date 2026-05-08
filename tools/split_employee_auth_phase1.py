from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

pages_path = ROOT / "app" / "routes" / "pages.py"
main_path = ROOT / "app" / "main.py"
employee_auth_path = ROOT / "app" / "routes" / "employee_auth.py"

pages = pages_path.read_text(encoding="utf-8")
main = main_path.read_text(encoding="utf-8")

employee_auth_code = r'''import hashlib as _emp_hashlib
import secrets as _emp_secrets
from datetime import datetime as _emp_datetime, timedelta as _emp_timedelta
from urllib.parse import parse_qs as _emp_parse_qs, quote as _emp_quote

from fastapi import APIRouter
from fastapi import Request as _EmpRequest
from fastapi.responses import HTMLResponse as _EmpHTMLResponse
from fastapi.responses import RedirectResponse as _EmpRedirectResponse
from sqlalchemy import text as _emp_sql_text

from app.db import engine as _emp_engine


router = APIRouter(tags=["員工登入"])


_EMP_COOKIE_NAME = "xunnan_employee_session"


def _emp_hash_pin(pin: str, salt: str) -> str:
    raw = (str(pin) + ":" + str(salt)).encode("utf-8")
    return _emp_hashlib.sha256(raw).hexdigest()


def _employee_auth_db_init():
    with _emp_engine.begin() as conn:
        conn.execute(_emp_sql_text("""
            CREATE TABLE IF NOT EXISTS employee_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                department TEXT DEFAULT '',
                role TEXT DEFAULT 'employee',
                pin_salt TEXT NOT NULL,
                pin_hash TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))

        conn.execute(_emp_sql_text("""
            CREATE TABLE IF NOT EXISTS employee_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE NOT NULL,
                staff_code TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))

        count = conn.execute(_emp_sql_text("SELECT COUNT(*) FROM employee_accounts")).scalar()

        if count == 0:
            seed_users = [
                ("sales01", "業務一", "業務部", "sales", "1111"),
                ("sales02", "業務二", "業務部", "sales", "2222"),
                ("sales03", "業務三", "業務部", "sales", "3333"),
                ("wesbe", "吳文化", "業務部", "admin", "9999"),
                ("admin", "系統管理員", "管理部", "admin", "0000"),
            ]

            for staff_code, display_name, department, role, pin in seed_users:
                salt = _emp_secrets.token_hex(8)
                pin_hash = _emp_hash_pin(pin, salt)

                conn.execute(
                    _emp_sql_text("""
                        INSERT INTO employee_accounts (
                            staff_code, display_name, department, role,
                            pin_salt, pin_hash, enabled,
                            created_at, updated_at
                        )
                        VALUES (
                            :staff_code, :display_name, :department, :role,
                            :pin_salt, :pin_hash, 1,
                            datetime('now'), datetime('now')
                        )
                    """),
                    {
                        "staff_code": staff_code,
                        "display_name": display_name,
                        "department": department,
                        "role": role,
                        "pin_salt": salt,
                        "pin_hash": pin_hash,
                    },
                )


def _employee_current_user_from_request(request):
    _employee_auth_db_init()

    token = request.cookies.get(_EMP_COOKIE_NAME, "")

    if not token:
        return None

    with _emp_engine.begin() as conn:
        row = conn.execute(
            _emp_sql_text("""
                SELECT
                    a.staff_code,
                    a.display_name,
                    a.department,
                    a.role
                FROM employee_sessions s
                JOIN employee_accounts a ON a.staff_code = s.staff_code
                WHERE s.session_token = :token
                  AND a.enabled = 1
                  AND datetime(s.expires_at) > datetime('now')
                LIMIT 1
            """),
            {"token": token},
        ).mappings().first()

    if not row:
        return None

    return dict(row)


def _employee_login_page(error: str = "", next_url: str = "/app/dispatch"):
    error_html = ""
    if error:
        error_html = f'<div class="error">{error}</div>'

    return f"""
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <title>員工登入｜訊南 ERP</title>
  <style>
    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #0f172a, #1e3a8a, #7c3aed);
      color: #102348;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
      padding: 18px;
    }}

    .card {{
      width: 100%;
      max-width: 420px;
      background: #ffffff;
      border-radius: 24px;
      padding: 24px;
      box-shadow: 0 24px 80px rgba(0,0,0,.28);
    }}

    h1 {{
      margin: 0 0 8px;
      font-size: 30px;
      font-weight: 1000;
      color: #102348;
    }}

    .sub {{
      color: #64748b;
      font-size: 14px;
      font-weight: 900;
      margin-bottom: 20px;
      line-height: 1.5;
    }}

    label {{
      display: block;
      margin: 12px 0 6px;
      color: #334155;
      font-size: 14px;
      font-weight: 1000;
    }}

    input {{
      width: 100%;
      height: 46px;
      border: 1px solid #cbd5e1;
      border-radius: 14px;
      padding: 0 14px;
      font-size: 18px;
      font-weight: 900;
      outline: none;
    }}

    button {{
      width: 100%;
      height: 48px;
      margin-top: 18px;
      border: 0;
      border-radius: 14px;
      background: #365ee8;
      color: #fff;
      font-size: 18px;
      font-weight: 1000;
      cursor: pointer;
    }}

    .error {{
      margin: 12px 0;
      padding: 10px 12px;
      border-radius: 12px;
      background: #fee2e2;
      color: #991b1b;
      font-size: 14px;
      font-weight: 1000;
    }}

    .hint {{
      margin-top: 14px;
      color: #64748b;
      font-size: 12px;
      font-weight: 800;
      line-height: 1.6;
    }}
  </style>
</head>

<body>
  <form class="card" method="post" action="/employee/login">
    <h1>員工登入</h1>
    <div class="sub">請輸入員工帳號與 PIN 碼後進入系統。</div>

    {error_html}

    <input type="hidden" name="next" value="{next_url}">

    <label>員工帳號</label>
    <input name="staff_code" autocomplete="username" placeholder="例如 sales01 / wesbe" required>

    <label>PIN 碼</label>
    <input name="pin" type="password" inputmode="numeric" autocomplete="current-password" placeholder="請輸入 PIN" required>

    <button type="submit">登入</button>

    <div class="hint">
      測試帳號：sales01 / 1111、sales02 / 2222、sales03 / 3333、wesbe / 9999、admin / 0000
    </div>
  </form>
</body>
</html>
"""


@router.get("/employee/login", response_class=_EmpHTMLResponse)
def employee_login_page(next: str = "/app/dispatch"):
    _employee_auth_db_init()
    return _employee_login_page("", next)


@router.post("/employee/login")
async def employee_login_submit(request: _EmpRequest):
    _employee_auth_db_init()

    raw = (await request.body()).decode("utf-8")
    form = _emp_parse_qs(raw)

    staff_code = (form.get("staff_code", [""])[0] or "").strip()
    pin = (form.get("pin", [""])[0] or "").strip()
    next_url = (form.get("next", ["/app/dispatch"])[0] or "/app/dispatch").strip()

    if not next_url.startswith("/"):
        next_url = "/app/dispatch"

    with _emp_engine.begin() as conn:
        user = conn.execute(
            _emp_sql_text("""
                SELECT staff_code, display_name, department, role, pin_salt, pin_hash, enabled
                FROM employee_accounts
                WHERE staff_code = :staff_code
                LIMIT 1
            """),
            {"staff_code": staff_code},
        ).mappings().first()

        if not user or int(user["enabled"] or 0) != 1:
            return _EmpHTMLResponse(_employee_login_page("帳號或 PIN 錯誤。", next_url), status_code=401)

        if _emp_hash_pin(pin, user["pin_salt"]) != user["pin_hash"]:
            return _EmpHTMLResponse(_employee_login_page("帳號或 PIN 錯誤。", next_url), status_code=401)

        token = _emp_secrets.token_urlsafe(32)
        expires = (_emp_datetime.now() + _emp_timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")

        conn.execute(
            _emp_sql_text("""
                INSERT INTO employee_sessions (
                    session_token, staff_code, expires_at, created_at
                )
                VALUES (
                    :session_token, :staff_code, :expires_at, datetime('now')
                )
            """),
            {
                "session_token": token,
                "staff_code": staff_code,
                "expires_at": expires,
            },
        )

    resp = _EmpRedirectResponse(next_url, status_code=303)
    resp.set_cookie(
        key=_EMP_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=12 * 60 * 60,
        path="/",
    )
    return resp


@router.get("/employee/logout")
def employee_logout(next: str = "/app/dispatch"):
    if not next.startswith("/"):
        next = "/app/dispatch"

    resp = _EmpRedirectResponse("/employee/login?next=" + _emp_quote(next), status_code=303)
    resp.delete_cookie(_EMP_COOKIE_NAME, path="/")
    return resp
'''

employee_auth_path.write_text(employee_auth_code, encoding="utf-8")

start_marker = '@router.get("/employee/login", response_class=_EmpHTMLResponse)'
end_marker = '@router.get("/api/app/sales/business-records", summary="手機 APP 讀取個人業務工作資料")'

start = pages.find(start_marker)
if start == -1:
    raise SystemExit("找不到 /employee/login 起點，停止修改。")

end = pages.find(end_marker, start)
if end == -1:
    raise SystemExit("找不到 /api/app/sales/business-records 結束點，停止修改。")

replacement = '''# SHINNAN_EMPLOYEE_LOGIN_ROUTES_MOVED_TO_employee_auth_py_START
# GET  /employee/login
# POST /employee/login
# GET  /employee/logout
# 已搬移至 app/routes/employee_auth.py
# SHINNAN_EMPLOYEE_LOGIN_ROUTES_MOVED_TO_employee_auth_py_END


'''

pages = pages[:start] + replacement + pages[end:]
pages_path.write_text(pages, encoding="utf-8")

import_line = "from app.routes.employee_auth import router as employee_auth_router\n"
if import_line not in main:
    target = "from app.routes.pages import router as pages_router\n"
    if target not in main:
        raise SystemExit("main.py 找不到 pages_router import，停止修改。")
    main = main.replace(target, import_line + "\n" + target)

include_line = "app.include_router(employee_auth_router)\n"
if include_line not in main:
    target = "app.include_router(pages_router)\n"
    if target not in main:
        raise SystemExit("main.py 找不到 pages_router include，停止修改。")
    main = main.replace(target, include_line + "\n" + target)

main_path.write_text(main, encoding="utf-8")

print("employee_auth_split_phase1_ok")
print("created:", employee_auth_path)
print("updated:", pages_path)
print("updated:", main_path)
