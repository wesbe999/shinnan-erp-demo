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
      background: #021208;
      padding-top: 30vh;
    }}
    /* 底圖疊加 */
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      background-image: url("/static/login_bg_gold_green.png?v=cl17f");
      background-size: cover;
      background-position: center top;
      opacity: 0.92;
      z-index: 0;
    }}
    .top-section {{ display: none; }}
    .card {{ position: relative; z-index: 1; margin-bottom: 5vh; }}
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
      width: min(86vw, 320px);
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
      background-image: url("/static/login_bg_gold_green.png?v=cl17g");
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
      left: 33.66%;
      width: 32.62%;
      height: 5.08%;
      border: 0;
      border-radius: 12px;
      outline: none;
      background: transparent;
      color: #ffffff;
      padding: 0 3.9%;
      font-size: clamp(16px, 1.65vw, 27px);
      font-weight: 1000;
      font-family: inherit;
      text-shadow: 0 2px 8px rgba(0, 0, 0, .7);
    }}

    .field-input::placeholder {{
      color: transparent;
    }}

    .field-input:not(:placeholder-shown) {{
      background: linear-gradient(90deg, transparent 0 10.5%, rgba(0, 15, 8, .92) 10.5% 100%);
    }}

    .pin-input:not(:placeholder-shown) {{
      background: linear-gradient(90deg, transparent 0 10.5%, rgba(0, 15, 8, .92) 10.5% 89%, transparent 89% 100%);
    }}

    .field-input:focus {{
      box-shadow: 0 0 0 2px rgba(245, 211, 93, .85), 0 0 24px rgba(245, 211, 93, .24);
    }}

    .staff-input {{ top: 58.98%; }}
    .pin-input {{ top: 69.33%; }}

    .toggle-pin {{
      position: absolute;
      left: 63.35%;
      top: 69.33%;
      width: 3.0%;
      height: 5.08%;
      border: 0;
      background: transparent;
      cursor: pointer;
    }}

    .remember {{
      position: absolute;
      left: 33.66%;
      top: 76.35%;
      width: 10.8%;
      height: 3.6%;
      cursor: pointer;
    }}

    .remember input {{
      width: 100%;
      height: 100%;
      opacity: 0;
      cursor: pointer;
    }}

    .submit-button {{
      position: absolute;
      left: 33.66%;
      top: 81.74%;
      width: 32.62%;
      height: 5.86%;
      border: 0;
      border-radius: 12px;
      background: transparent;
      color: transparent;
      cursor: pointer;
    }}

    .submit-button:focus-visible,
    .submit-button:hover {{
      box-shadow: 0 0 0 2px rgba(255, 220, 89, .85), 0 0 28px rgba(30, 168, 76, .36);
    }}

    .err {{
      position: absolute;
      left: 33.66%;
      top: 54.5%;
      width: 32.62%;
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
      <input class="field-input staff-input" id="staff_code" name="staff_code" type="text" autocomplete="username" placeholder=" " aria-label="&#x54E1;&#x5DE5;&#x5E33;&#x865F;">
      <input class="field-input pin-input" id="pin" name="pin" type="password" autocomplete="current-password" inputmode="numeric" placeholder=" " aria-label="PIN &#x78BC;">
      <button class="toggle-pin" type="button" onclick="togglePin()" aria-label="&#x986F;&#x793A;&#x6216;&#x96B1;&#x85CF; PIN"></button>
      <label class="remember" aria-label="&#x8A18;&#x4F4F;&#x5E33;&#x865F;"><input type="checkbox" id="remember_me" name="remember_me" value="1" checked></label>
      <button class="submit-button" type="submit">&#x767B;&#x5165;&#x7CFB;&#x7D71;</button>
    </form>
  </div>
  <script>
    (function () {{
      const saved = localStorage.getItem("shinnan_remember_staff_code");
      const cb = document.getElementById("remember_me");
      if (saved && cb && cb.checked) document.getElementById("staff_code").value = saved;
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
    /* 整個版面：圖片寬度 = 100vw，高度依比例撐開 */
    .page-wrap {{
      position: relative;
      width: 100vw;
    }}
    .bg-img {{
      display: block;
      width: 100%;
      height: auto;
    }}
    /* 表單用絕對定位疊在圖片上，用百分比對齊白色框 */
    /* 底圖 1086x1448，白色框約 top:38% ~ bottom:67%，left:9% ~ right:91% */
    .form-area {{
      position: absolute;
      top: 40%;
      left: 50%;
      transform: translateX(-50%);
      width: 74%;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .input-wrap {{
      position: relative;
      display: flex;
      align-items: center;
    }}
    .input-icon {{
      position: absolute;
      left: 11px;
      color: rgba(212,175,55,.8);
      font-size: 14px;
      pointer-events: none;
    }}
    input[type=text], input[type=password] {{
      width: 100%;
      height: 44px;
      background: rgba(0, 15, 8, 0.80);
      border: 1px solid rgba(212,175,55,.45);
      border-radius: 10px;
      color: #ffffff;
      font-size: 15px;
      font-weight: 700;
      padding: 0 36px 0 34px;
      outline: none;
      font-family: inherit;
    }}
    input[type=text]:focus, input[type=password]:focus {{
      border-color: rgba(212,175,55,.85);
      box-shadow: 0 0 0 2px rgba(212,175,55,.15);
    }}
    input::placeholder {{ color: rgba(255,255,255,.35); }}
    .toggle-pin {{
      position: absolute; right: 10px;
      background: none; border: none;
      color: rgba(212,175,55,.6); cursor: pointer; font-size: 13px;
    }}
    .remember {{
      display: flex; align-items: center; gap: 6px;
      color: rgba(255,255,255,.75); font-size: 12px; font-weight: 700;
    }}
    .remember input {{ width: 14px; height: 14px; accent-color: #d4af37; }}
    .btn-login {{
      width: 100%; height: 46px; border: none; border-radius: 10px;
      background: linear-gradient(135deg, #166430, #25a84c);
      color: #ffffff; font-size: 16px; font-weight: 900; cursor: pointer;
      box-shadow: 0 4px 16px rgba(30,138,62,.45);
      letter-spacing: .05em;
    }}
    .err {{
      padding: 7px 10px; border-radius: 8px;
      background: rgba(200,40,40,.25); border: 1px solid rgba(200,40,40,.4);
      color: #ff9999; font-size: 12px; text-align: center; display: none;
    }}
    .demo-hint {{
      text-align: center; color: rgba(212,175,55,.5);
      font-size: 11px; letter-spacing: .06em;
    }}
  </style>
</head>
<body>
  <div class="page-wrap">
    <img class="bg-img" src="/static/mobile_login_bg.png?v=cl17n" alt="">
    <div class="form-area">
      <div class="err" id="err_box">{error_html}</div>
      <div class="input-wrap">
        <span class="input-icon">👤</span>
        <input id="staff_code" type="text" placeholder="帳號（如：S001）" autocomplete="username">
      </div>
      <div class="input-wrap">
        <span class="input-icon">🔐</span>
        <input id="pin" type="password" placeholder="PIN 碼" autocomplete="current-password" inputmode="numeric">
        <button class="toggle-pin" type="button" onclick="togglePin(this)" tabindex="-1">👁</button>
      </div>
      <label class="remember">
        <input type="checkbox" id="remember_me" {"checked" if True else ""}> 記住帳號
      </label>
      <button class="btn-login" onclick="doLogin()">🔒 登入系統</button>
      <div class="demo-hint">S001 / 0000</div>
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
