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


def _employee_login_page(error: str = "", next_url: str = "/app", mobile: bool = False):
    if mobile:
        return _employee_login_page_mobile(error, next_url)

    error_html = ""
    if error:
        error_html = f'<div class="err visible">{error}</div>'

    return f"""
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <title>&#x54E1;&#x5DE5;&#x767B;&#x5165;&#xFF5C;&#x8A0A;&#x5357; ERP</title>
  <style>
    * {{ box-sizing: border-box; }}

    html,
    body {{
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
      background: #021208;
    }}

    body {{
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .login-stage {{
      position: relative;
      width: min(100vw, 150vh);
      aspect-ratio: 3 / 2;
      background-image: url("/static/login_bg_gold_green.png?v=cl17h");
      background-size: 100% 100%;
      background-position: center;
      background-repeat: no-repeat;
      box-shadow: 0 0 90px rgba(0, 0, 0, .45);
    }}

    .login-form {{
      position: absolute;
      inset: 0;
      z-index: 2;
    }}

    .field-input {{
      position: absolute;
      left: 33.5%;
      width: 33%;
      height: 6%;
      border: 0;
      border-radius: 30px;
      outline: none;
      background: rgba(255,255,255,0.92);
      color: #0a2a10;
      padding: 0 4%;
      font-size: clamp(14px, 1.6vw, 24px);
      font-weight: 900;
      font-family: inherit;
    }}

    .field-input::placeholder {{
      color: rgba(0,0,0,0.3);
    }}

    .field-input:focus {{
      box-shadow: 0 0 0 2.5px rgba(245, 211, 93, .9), 0 0 20px rgba(245, 211, 93, .3);
    }}

    .staff-input {{ top: 56%; }}
    .pin-input   {{ top: 68%; }}

    /* 帳號/密碼白色標籤 */
    .field-label {{
      position: absolute;
      left: 33.5%;
      color: #ffffff;
      font-size: clamp(11px, 1.1vw, 17px);
      font-weight: 700;
      text-shadow: 0 1px 6px rgba(0,0,0,.8);
    }}
    .staff-label {{ top: 52%; }}
    .pin-label   {{ top: 64%; }}

    .toggle-pin {{
      position: absolute;
      left: 63.5%;
      top: 68%;
      width: 3%;
      height: 6%;
      border: 0;
      background: transparent;
      cursor: pointer;
      font-size: clamp(12px, 1.3vw, 20px);
    }}

    .remember {{
      position: absolute;
      left: 33.5%;
      top: 76%;
      width: 12%;
      height: 4%;
      cursor: pointer;
    }}

    .remember input {{
      width: 100%;
      height: 100%;
      opacity: 0;
      cursor: pointer;
    }}

    /* 青綠色登入按鈕 */
    .submit-button {{
      position: absolute;
      left: 33.5%;
      top: 82%;
      width: 33%;
      height: 6.5%;
      border: 0;
      border-radius: 30px;
      background: linear-gradient(135deg, #0fa86a, #17d68a);
      color: #ffffff;
      font-size: clamp(14px, 1.5vw, 22px);
      font-weight: 900;
      font-family: inherit;
      letter-spacing: .06em;
      cursor: pointer;
      box-shadow: 0 4px 20px rgba(15,168,106,.5);
    }}

    .submit-button:hover {{
      background: linear-gradient(135deg, #0ec077, #1ef59e);
      box-shadow: 0 6px 28px rgba(15,168,106,.7);
    }}

    .err {{
      position: absolute;
      left: 33.5%;
      top: 51%;
      width: 33%;
      padding: 8px 12px;
      border: 1px solid rgba(255, 130, 130, .55);
      border-radius: 10px;
      background: rgba(90, 0, 0, .58);
      color: #ffd5d5;
      font-size: clamp(12px, 1vw, 15px);
      font-weight: 900;
      text-align: center;
      backdrop-filter: blur(8px);
    }}
  </style>
</head>
<body>
  <div class="login-stage">
    <form class="login-form" method="post" action="/employee/login" autocomplete="on">
      {error_html}
      <input type="hidden" name="next" value="{next_url}">
      <input type="hidden" name="login_view" value="desktop">
      <div class="field-label staff-label">帳號</div>
      <input class="field-input staff-input" id="staff_code" name="staff_code" type="text" autocomplete="username" placeholder="請輸入帳號" aria-label="員工帳號">
      <div class="field-label pin-label">密碼</div>
      <input class="field-input pin-input" id="pin" name="pin" type="password" autocomplete="current-password" inputmode="numeric" placeholder="請輸入 PIN 碼" aria-label="PIN 碼">
      <button class="toggle-pin" type="button" onclick="togglePin()" aria-label="顯示或隱藏 PIN">👁</button>
      <label class="remember" aria-label="記住帳號"><input type="checkbox" id="remember_me" name="remember_me" value="1" checked></label>
      <button class="submit-button" type="submit">🔒 登入系統</button>
    </form>
  </div>
  <script>
    (function () {{
      const saved = localStorage.getItem("shinnan_remember_staff_code");
      const cb = document.getElementById("remember_me");
      if (saved && cb && cb.checked) document.getElementById("staff_code").value = saved;
      // 登出後清掉密碼欄，防止瀏覽器自動填入
      document.getElementById("pin").value = "";
    }})();

    function togglePin() {{
      const pin = document.getElementById("pin");
      pin.type = pin.type === "password" ? "text" : "password";
    }}

    document.querySelector(".login-form").addEventListener("submit", function (event) {{
      const code = document.getElementById("staff_code").value.trim();
      const pin = document.getElementById("pin").value.trim();
      const rem = document.getElementById("remember_me").checked;

      if (!code || !pin) {{
        event.preventDefault();
        alert("請輸入員工帳號與 PIN 碼");
        return;
      }}

      if (rem) localStorage.setItem("shinnan_remember_staff_code", code);
      else localStorage.removeItem("shinnan_remember_staff_code");
    }});
  </script>
</body>
</html>
"""


def _employee_login_page_mobile(error: str = "", next_url: str = "/app"):
    error_html = ""
    if error:
        error_html = f'<div class="err" style="display:block">{error}</div>'

    return f"""
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover">
  <title>&#x54E1;&#x5DE5;&#x767B;&#x5165;&#xFF5C;&#x8A0A;&#x5357; ERP</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: 100%; height: 100%;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
      background: #021208;
      overflow-x: hidden;
      overflow-y: auto;
    }}
    .page-wrap {{
      position: relative;
      width: 100vw;
      min-height: 100vh;
    }}
    .bg-img {{
      display: block;
      width: 100%;
      height: auto;
      position: absolute;
      top: 0; left: 0;
    }}
    /* 卡片置中浮在背景上 */
    .card-wrap {{
      position: relative;
      z-index: 2;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 160px 24px 30px;
    }}
    .card {{
      width: 100%;
      max-width: 360px;
      background: rgba(2, 30, 12, 0.88);
      border: 1.5px solid rgba(212,175,55,.55);
      border-radius: 20px;
      padding: 20px 22px 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      backdrop-filter: blur(8px);
      box-shadow: 0 8px 40px rgba(0,0,0,.5);
    }}
    .card-icon {{
      width: 44px; height: 44px;
      background: rgba(255,255,255,.12);
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 22px;
      margin-bottom: 0px;
    }}
    .card-title {{
      color: #ffffff;
      font-size: 20px;
      font-weight: 900;
      letter-spacing: .04em;
    }}
    .card-subtitle {{
      color: rgba(255,255,255,.55);
      font-size: 12px;
      margin-top: -4px;
    }}
    .field-group {{
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .field-label {{
      color: rgba(255,255,255,.7);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .04em;
    }}
    .input-wrap {{
      position: relative;
      display: flex;
      align-items: center;
    }}
    .input-icon {{
      position: absolute; left: 12px;
      color: rgba(212,175,55,.7);
      font-size: 15px;
      pointer-events: none;
    }}
    input[type=text], input[type=password] {{
      width: 100%;
      height: 42px;
      background: rgba(255,255,255,.07);
      border: 1px solid rgba(212,175,55,.35);
      border-radius: 10px;
      color: #ffffff;
      font-size: 15px;
      font-weight: 700;
      padding: 0 40px 0 38px;
      outline: none;
      font-family: inherit;
    }}
    input[type=text]:focus, input[type=password]:focus {{
      border-color: rgba(212,175,55,.8);
      background: rgba(255,255,255,.10);
      box-shadow: 0 0 0 2px rgba(212,175,55,.15);
    }}
    input::placeholder {{ color: rgba(255,255,255,.3); }}
    .toggle-pin {{
      position: absolute; right: 12px;
      background: none; border: none;
      color: rgba(212,175,55,.6); cursor: pointer; font-size: 14px;
    }}
    .remember {{
      width: 100%;
      display: flex; align-items: center; gap: 8px;
      color: rgba(255,255,255,.7); font-size: 13px; font-weight: 700;
      cursor: pointer;
    }}
    .remember input {{ width: 16px; height: 16px; accent-color: #d4af37; cursor: pointer; }}
    .btn-login {{
      width: 100%; height: 44px; border: none; border-radius: 10px;
      background: linear-gradient(135deg, #1a7a3a, #2ec45a);
      color: #ffffff; font-size: 16px; font-weight: 900; cursor: pointer;
      box-shadow: 0 4px 20px rgba(30,138,62,.5);
      letter-spacing: .06em;
      margin-top: 2px;
    }}
    .btn-login:active {{ filter: brightness(.9); }}
    .err {{
      width: 100%;
      padding: 8px 12px; border-radius: 8px;
      background: rgba(200,40,40,.25); border: 1px solid rgba(200,40,40,.4);
      color: #ff9999; font-size: 12px; text-align: center; display: none;
    }}
    .demo-hint {{
      color: rgba(212,175,55,.45);
      font-size: 11px; letter-spacing: .06em;
      margin-top: -4px;
    }}
  </style>
</head>
<body>
  <div class="page-wrap">
    <img class="bg-img" src="/static/mobile_login_bg.png?v=cl17n" alt="">
    <div class="card-wrap">
      <div class="card">
        <div class="card-icon">👤</div>
        <div class="card-title">員工登入</div>
        <div class="card-subtitle">請輸入帳號與 PIN 碼</div>
        <div class="err" id="err_box">{error_html}</div>
        <div class="field-group">
          <div class="field-label">帳號</div>
          <div class="input-wrap">
            <span class="input-icon">👤</span>
            <input id="staff_code" type="text" placeholder="請輸入帳號" autocomplete="username">
          </div>
        </div>
        <div class="field-group">
          <div class="field-label">PIN 碼</div>
          <div class="input-wrap">
            <span class="input-icon">🔐</span>
            <input id="pin" type="password" placeholder="請輸入 PIN 碼" autocomplete="current-password" inputmode="numeric">
            <button class="toggle-pin" type="button" onclick="togglePin(this)" tabindex="-1">👁</button>
          </div>
        </div>
        <label class="remember">
          <input type="checkbox" id="remember_me" {"checked" if True else ""}> 記住帳號
        </label>
        <button class="btn-login" onclick="doLogin()">🔒 登入系統</button>
        <div class="demo-hint">S001 / 0000</div>
      </div>
    </div>
  </div>
  <script>
    (function(){{
      const s = localStorage.getItem("shinnan_remember_staff_code");
      const c = document.getElementById("remember_me");
      if(s && c && c.checked) document.getElementById("staff_code").value = s;
    }})();
    function togglePin(btn){{
      const i = document.getElementById("pin");
      if(i.type==="password"){{i.type="text";btn.textContent="🙈";}}
      else{{i.type="password";btn.textContent="👁";}}
    }}
    function doLogin(){{
      const code = document.getElementById("staff_code").value.trim();
      const pin = document.getElementById("pin").value.trim();
      const rem = document.getElementById("remember_me").checked;
      const err = document.getElementById("err_box");
      if(!code||!pin){{err.textContent="請輸入帳號與 PIN 碼";err.style.display="block";return;}}
      if(rem) localStorage.setItem("shinnan_remember_staff_code",code);
      else localStorage.removeItem("shinnan_remember_staff_code");
      const f=document.createElement("form");
      f.method="POST";f.action="/employee/login";
      [["staff_code",code],["pin",pin],["remember_me",rem?"1":""],["next","{next_url}"],["login_view","mobile"]].forEach(([k,v])=>{{
        const i=document.createElement("input");i.type="hidden";i.name=k;i.value=v;f.appendChild(i);
      }});
      document.body.appendChild(f);f.submit();
    }}
    document.addEventListener("keydown",e=>{{if(e.key==="Enter")doLogin();}});
  </script>
</body>
</html>
"""


@router.get("/employee/login", response_class=_EmpHTMLResponse)
def employee_login_page(next: str = "/app", request: _EmpRequest = None):
    _employee_auth_db_init()
    next_url = _xunnan_employee_normalize_next_url(next)
    # 手機 User-Agent 自動顯示手機版
    ua = (request.headers.get("user-agent", "") if request else "").lower()
    is_mobile = any(k in ua for k in ("mobile", "android", "iphone", "ipad", "ipod"))
    if is_mobile:
        return _employee_login_page_mobile("", next_url)
    return _employee_login_page("", next_url)


@router.get("/employee/login/mobile", response_class=_EmpHTMLResponse)
def employee_login_mobile_page(next: str = "/app"):
    _employee_auth_db_init()
    return _employee_login_page_mobile("", _xunnan_employee_normalize_next_url(next))


@router.post("/employee/login")
async def employee_login_submit(request: _EmpRequest):
    _employee_auth_db_init()

    raw = (await request.body()).decode("utf-8")
    form = _emp_parse_qs(raw)

    staff_code = (form.get("staff_code", [""])[0] or "").strip()
    pin = (form.get("pin", [""])[0] or "").strip()
    next_url = (form.get("next", ["/app"])[0] or "/app").strip()
    login_view = (form.get("login_view", ["desktop"])[0] or "desktop").strip().lower()
    login_mobile = login_view == "mobile"

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
            return _EmpHTMLResponse(_employee_login_page("帳號或 PIN 錯誤。", next_url, mobile=login_mobile), status_code=401)

        if _emp_hash_pin(pin, user["pin_salt"]) != user["pin_hash"]:
            return _EmpHTMLResponse(_employee_login_page("帳號或 PIN 錯誤。", next_url, mobile=login_mobile), status_code=401)

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

    # 判斷 UA：電腦版依角色直接導到對應系統，手機版導到 /app
    ua = (request.headers.get("user-agent", "") if request else "").lower()
    is_mobile = any(k in ua for k in ("mobile", "android", "iphone", "ipad", "ipod"))

    if login_mobile or is_mobile:
        # 手機版：導到 /app（功能選單）
        redirect_url = next_url
    else:
        # 電腦版：next_url 不是 /app 就照用（代表從特定頁面來），否則依角色導向
        if next_url and next_url != "/app":
            redirect_url = next_url
        else:
            role = str(user.get("role") or "").strip()
            staff = str(user.get("staff_code") or "").strip()
            is_admin = staff == "admin" or role == "admin"
            if is_admin:
                redirect_url = "/app/manager"
            elif role == "manager":
                redirect_url = "/app/manager"
            else:
                redirect_url = "/app/dispatch"

    resp = _EmpRedirectResponse(redirect_url, status_code=303)
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
def employee_logout(request: _EmpRequest = None, next: str = ""):
    # 登出後導向：
    # 1. 有 next 參數且合法 → 用 next
    # 2. 手機 UA → 手機登入頁
    # 3. 電腦 → 根目錄入口頁 /
    ua = (request.headers.get("user-agent", "") if request else "").lower()
    is_mobile = any(k in ua for k in ("mobile", "android", "iphone", "ipad", "ipod"))

    if next and next.startswith("/") and not next.startswith("//"):
        dest = next
    elif is_mobile:
        dest = "/employee/login"
    else:
        dest = "/"

    resp = _EmpRedirectResponse(dest, status_code=303)
    resp.delete_cookie(_EMP_COOKIE_NAME, path="/")
    return resp
