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
    html, body {{ width: 100%; height: 100%; font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif; }}
    body {{
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      /* 深綠漸層背景，仿城市夜景 */
      background: radial-gradient(ellipse at 50% 0%, #0a3d1f 0%, #021208 55%, #000e06 100%);
    }}
    /* 底圖疊加 */
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      background-image: url("/static/login_gold_green_transparent.png?v=cl17c");
      background-size: cover;
      background-position: center 30%;
      opacity: 0.55;
      z-index: 0;
    }}
    .top-section, .card {{ position: relative; z-index: 1; }}
    /* 頂部 logo 區 */
    .top-section {{
      display: flex; flex-direction: column; align-items: center;
      margin-bottom: 24px; text-align: center;
    }}
    .logo-img {{
      width: 100px; height: auto;
      filter: drop-shadow(0 2px 16px rgba(212,175,55,.6));
      margin-bottom: 10px;
    }}
    .sys-title {{
      color: #ffffff; font-size: 28px; font-weight: 1000;
      text-shadow: 0 2px 16px rgba(0,0,0,.8);
      letter-spacing: .04em;
    }}
    .sys-sub {{
      margin-top: 7px; color: #d4af37;
      font-size: 14px; font-weight: 900; letter-spacing: .16em;
    }}
    .sys-sub span {{ margin: 0 6px; opacity: .6; }}
    /* Card */
    .card {{
      width: min(90vw, 400px);
      background: rgba(3, 22, 12, 0.78);
      border: 1px solid rgba(212,175,55,.35);
      border-radius: 18px;
      padding: 26px 26px 20px;
      box-shadow:
        0 0 0 1px rgba(212,175,55,.08),
        inset 0 1px 0 rgba(212,175,55,.1),
        0 30px 80px rgba(0,0,0,.7);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
    }}
    .card-title {{
      text-align: center; color: #ffffff;
      font-size: 21px; font-weight: 1000; margin-bottom: 4px;
    }}
    .card-sub {{
      text-align: center; color: rgba(255,255,255,.45);
      font-size: 13px; margin-bottom: 20px;
    }}
    /* Fields */
    .field {{ margin-bottom: 13px; }}
    label {{ display: block; color: rgba(255,255,255,.75); font-size: 12.5px; font-weight: 1000; margin-bottom: 5px; letter-spacing: .04em; }}
    .input-wrap {{ position: relative; display: flex; align-items: center; }}
    .input-icon {{ position: absolute; left: 12px; color: #d4af37; font-size: 14px; pointer-events: none; opacity: .8; }}
    input[type=text], input[type=password] {{
      width: 100%; height: 46px;
      background: rgba(0, 15, 8, 0.7);
      border: 1px solid rgba(212,175,55,.3);
      border-radius: 10px;
      color: #ffffff; font-size: 15px; font-weight: 900;
      padding: 0 38px 0 36px;
      outline: none; font-family: inherit;
      transition: border-color .2s, box-shadow .2s;
    }}
    input[type=text]::placeholder, input[type=password]::placeholder {{ color: rgba(255,255,255,.25); }}
    input[type=text]:focus, input[type=password]:focus {{
      border-color: rgba(212,175,55,.7);
      box-shadow: 0 0 0 3px rgba(212,175,55,.1);
      background: rgba(0, 20, 10, 0.8);
    }}
    .toggle-pin {{
      position: absolute; right: 11px; background: none; border: none;
      color: rgba(212,175,55,.6); cursor: pointer; font-size: 14px; padding: 4px;
    }}
    .remember {{
      display: flex; align-items: center; gap: 7px;
      margin-bottom: 16px; color: rgba(255,255,255,.6);
      font-size: 12.5px; font-weight: 900; cursor: pointer;
    }}
    .remember input {{ width: 15px; height: 15px; accent-color: #d4af37; }}
    .btn-login {{
      width: 100%; height: 48px; border: none; border-radius: 10px;
      background: linear-gradient(135deg, #166430 0%, #1e8a3e 50%, #25a84c 100%);
      color: #ffffff; font-size: 16px; font-weight: 1000; cursor: pointer;
      letter-spacing: .06em;
      box-shadow: 0 4px 20px rgba(30,138,62,.45), 0 1px 0 rgba(255,255,255,.1) inset;
      transition: filter .15s, transform .1s;
    }}
    .btn-login:hover {{ filter: brightness(1.1); }}
    .btn-login:active {{ transform: scale(.98); }}
    .err {{
      margin-top: 10px; padding: 8px 12px; border-radius: 8px;
      background: rgba(200,40,40,.2); border: 1px solid rgba(200,40,40,.35);
      color: #ff9999; font-size: 12.5px; font-weight: 900;
      display: none; text-align: center;
    }}
    .demo-hint {{
      margin-top: 13px; text-align: center;
      color: rgba(212,175,55,.45); font-size: 11.5px; letter-spacing: .08em;
    }}
    @media (max-height: 700px) {{
      .top-section {{ margin-bottom: 14px; }}
      .logo-img {{ width: 70px; }}
      .sys-title {{ font-size: 22px; }}
      .card {{ padding: 18px 20px 14px; }}
    }}
  </style>
</head>
<body>
  <div class="top-section">
    <img class="logo-img" src="/static/shinnan_logo_gold_transparent.png" alt="ShinNan">
    <div class="sys-title">訊南工作管理系統</div>
    <div class="sys-sub">高效<span>·</span>整合<span>·</span>智慧<span>·</span>穩定</div>
  </div>
  <div class="card">
    <div class="card-title">員工登入</div>
    <div class="card-sub">請輸入員工帳號與 PIN 碼後進入系統。</div>
    <div class="field">
      <label>員工帳號</label>
      <div class="input-wrap">
        <span class="input-icon">👤</span>
        <input id="staff_code" type="text" placeholder="請輸入員工帳號（如：S001）" autocomplete="username">
      </div>
    </div>
    <div class="field">
      <label>PIN 碼</label>
      <div class="input-wrap">
        <span class="input-icon">🔐</span>
        <input id="pin" type="password" placeholder="請輸入 PIN 碼" autocomplete="current-password" inputmode="numeric">
        <button class="toggle-pin" type="button" onclick="togglePin(this)" tabindex="-1">👁</button>
      </div>
    </div>
    <label class="remember">
      <input type="checkbox" id="remember_me" {"checked" if remember_checked else ""}> 記住帳號
    </label>
    <div class="err" id="err_box">{error_html}</div>
    <button class="btn-login" onclick="doLogin()">🔒 &nbsp;登入系統</button>
    <div class="demo-hint">S001 / 0000</div>
  </div>
  <script>
    (function () {{
      const saved = localStorage.getItem("shinnan_remember_staff_code");
      const cb = document.getElementById("remember_me");
      if (saved && cb && cb.checked) {{ document.getElementById("staff_code").value = saved; }}
    }})();
    function togglePin(btn) {{
      const inp = document.getElementById("pin");
      if (inp.type === "password") {{ inp.type = "text"; btn.textContent = "🙈"; }}
      else {{ inp.type = "password"; btn.textContent = "👁"; }}
    }}
    async function doLogin() {{
      const code = document.getElementById("staff_code").value.trim();
      const pin  = document.getElementById("pin").value.trim();
      const rem  = document.getElementById("remember_me").checked;
      const err  = document.getElementById("err_box");
      if (!code || !pin) {{ err.textContent = "請輸入帳號與 PIN 碼"; err.style.display = "block"; return; }}
      if (rem) localStorage.setItem("shinnan_remember_staff_code", code);
      else localStorage.removeItem("shinnan_remember_staff_code");
      const form = document.createElement("form");
      form.method = "POST";
      form.action = "/employee/login{next_qs}";
      [["staff_code", code], ["pin", pin], ["remember_me", rem ? "1" : ""]].forEach(function([k,v]) {{
        const i = document.createElement("input");
        i.type = "hidden"; i.name = k; i.value = v;
        form.appendChild(i);
      }});
      document.body.appendChild(form);
      form.submit();
    }}
    document.addEventListener("keydown", function(e) {{ if (e.key === "Enter") doLogin(); }});
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
    next_url = (form.get("next", ["/app"])[0] or "/app").strip()

    if not next_url.startswith("/"):
        next_url = "/app"

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
