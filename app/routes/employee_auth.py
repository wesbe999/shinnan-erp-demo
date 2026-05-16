import hashlib as _emp_hashlib
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
                ("admin", "系統管理員", "管理部", "admin", "1234"),
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



def _xunnan_employee_normalize_next_url(value: str) -> str:
    text = str(value or "").strip()

    if not text or not text.startswith("/") or text.startswith("//"):
        return "/app"

    if text.startswith("/employee/login"):
        return "/app"

    base = text.split("?", 1)[0]
    module_home_paths = {
        "/app/dispatch",
        "/app/sales",
        "/app/billing",
        "/app/engineering",
        "/app/maintenance",
        "/app/manager",
    }

    if base in module_home_paths:
        return "/app"

    return text


def _employee_login_page(error: str = "", next_url: str = "/app"):
    error_html = ""
    if error:
        error_html = error

    remember_checked = True
    next_qs = f"?next={next_url}" if next_url and next_url != "/app" else ""

    return f"""
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <title>員工登入｜訊南 ERP</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    html, body {{
      width: 100%;
      height: 100%;
    }}

    body {{
      min-height: 100vh;
      min-width: 100vw;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
      overflow: hidden;
      background-color: #04120e;
      background-image: url("/static/login_bg_clean.png?v=cl16l");
      background-size: auto 100vh;
      background-position: center center;
      background-repeat: no-repeat;
    }}

    .card {{
      position: relative;
      z-index: 2;
      width: 60.2vh;
      max-width: calc(100vw - 32px);
      height: calc(93.1vh - 50px);
      background: #ffffff;
      border-radius: 20px;
      padding: 20px 22px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}

    label {{
      display: block;
      margin: 0 0 5px;
      color: #1b4332;
      font-size: 13px;
      font-weight: 1000;
    }}

    .field + .field {{
      margin-top: 10px;
    }}

    input {{
      width: 100%;
      height: 44px;
      border: 1.5px solid #d1d5db;
      border-radius: 12px;
      background: #f8fafc;
      color: #102348;
      padding: 0 12px;
      font-size: 16px;
      font-weight: 900;
      outline: none;
    }}

    input:focus {{
      border-color: #15803d;
      box-shadow: 0 0 0 3px rgba(21, 128, 61, .14);
    }}

    .remember {{
      display: flex;
      align-items: center;
      gap: 7px;
      margin-top: 10px;
      color: #334155;
      font-size: 13px;
      font-weight: 900;
      cursor: pointer;
    }}

    .remember input {{
      width: 16px;
      height: 16px;
      accent-color: #15803d;
    }}

    .btn-login {{
      width: 100%;
      height: 46px;
      margin-top: 16px;
      border: none;
      border-radius: 12px;
      background: linear-gradient(135deg, #064e2f, #15803d);
      color: #ffffff;
      font-size: 16px;
      font-weight: 1000;
      cursor: pointer;
      letter-spacing: .04em;
    }}

    .btn-login:hover {{ background: linear-gradient(135deg, #064e2f, #166534); }}
    .btn-login:active {{ transform: scale(.985); }}

    .err {{
      margin-top: 10px;
      padding: 8px 12px;
      border-radius: 10px;
      background: #fee2e2;
      color: #991b1b;
      font-size: 13px;
      font-weight: 900;
      display: none;
    }}
  

</style>
</head>
<body>
  <div class="card">
    <div class="field">
      <label for="staff_code">帳號</label>
      <input id="staff_code" type="text" placeholder="請輸入帳號" autocomplete="username" inputmode="text">
    </div>
    <div class="field">
      <label for="pin">PIN 碼</label>
      <input id="pin" type="password" placeholder="請輸入 PIN 碼" autocomplete="current-password" inputmode="numeric">
    </div>
    <label class="remember">
      <input type="checkbox" id="remember_me" {"checked" if remember_checked else ""}> 記住帳號
    </label>
    <div class="err" id="err_box">{error_html}</div>
    <button class="btn-login" onclick="doLogin()">🔐 登入系統</button>
  </div>

  <script>
    (function () {{
      const saved = localStorage.getItem("shinnan_remember_staff_code");
      const cb = document.getElementById("remember_me");
      if (saved && cb && cb.checked) {{
        document.getElementById("staff_code").value = saved;
      }}
    }})();

    async function doLogin() {{
      const code = document.getElementById("staff_code").value.trim();
      const pin  = document.getElementById("pin").value.trim();
      const rem  = document.getElementById("remember_me").checked;
      const err  = document.getElementById("err_box");

      if (!code || !pin) {{
        err.textContent = "請輸入帳號與 PIN 碼";
        err.style.display = "block";
        return;
      }}

      if (rem) localStorage.setItem("shinnan_remember_staff_code", code);
      else localStorage.removeItem("shinnan_remember_staff_code");

      const form = document.createElement("form");
      form.method = "POST";
      form.action = "/employee/login{next_qs}";
      [["staff_code", code], ["pin", pin], ["remember_me", rem ? "1" : ""]].forEach(function ([k, v]) {{
        const i = document.createElement("input");
        i.type = "hidden"; i.name = k; i.value = v;
        form.appendChild(i);
      }});
      document.body.appendChild(form);
      form.submit();
    }}

    document.addEventListener("keydown", function (e) {{
      if (e.key === "Enter") doLogin();
    }});
  </script>
</body>
</html>
"""
@router.get("/employee/login", response_class=_EmpHTMLResponse)
def employee_login_page(next: str = "/app"):
    _employee_auth_db_init()
    return _employee_login_page("", _xunnan_employee_normalize_next_url(next))


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
def employee_logout(next: str = "/employee/login?next=/app"):
    default_next = "/employee/login?next=/app"

    if not next or not next.startswith("/") or next.startswith("//"):
        next = default_next

    if next == "/":
        next = default_next

    resp = _EmpRedirectResponse(next, status_code=303)
    resp.delete_cookie(_EMP_COOKIE_NAME, path="/")
    return resp
