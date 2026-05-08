from fastapi.responses import RedirectResponse as _LoginRedirectResponse, JSONResponse as _LoginJSONResponse
from sqlalchemy import text as _login_sql_text
from app.db import engine as _login_engine

from pathlib import Path

from fastapi import FastAPI

from app.routes.billing import router as billing_router

from fastapi.responses import HTMLResponse

from fastapi.staticfiles import StaticFiles

from app.routes.home import router as home_router

from app.db import Base, engine

from app.routes.auth import router as auth_router

from app.routes.notices import router as notices_router

from app.routes.communities import router as communities_router

from app.routes.mobile import router as mobile_router

from app.routes.employee_auth import router as employee_auth_router
from app.routes.employee_app import router as employee_app_router
from app.routes.sales_app import router as sales_app_router
from app.modules.dispatch.module import register as register_dispatch_module
from app.routes.billing_app import router as billing_app_router
from app.routes.engineering_app import router as engineering_app_router
from app.routes.hr_admin import router as hr_admin_router
from app.routes.hr_employee_adjust import router as hr_employee_adjust_router

from app.routes.admin_dispatch import router as admin_dispatch_router
from app.routes.pages import router as pages_router

from app.routes.tickets import router as tickets_router



Base.metadata.create_all(bind=engine)



BASE_DIR = Path(__file__).resolve().parent

STATIC_DIR = BASE_DIR / "static"

STATIC_DIR.mkdir(parents=True, exist_ok=True)



app = FastAPI(

    title="訊南科技派工系統 API",

    version="1.0.0",

    description="訊南科技派工系統 v1 後端 API。",

    docs_url="/docs",

    redoc_url="/redoc",

)





app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.mount("/erp-static", StaticFiles(directory=str(STATIC_DIR)), name="erp_static")

app.include_router(auth_router)

app.include_router(notices_router)

app.include_router(communities_router)

app.include_router(mobile_router)

app.include_router(employee_auth_router)
app.include_router(employee_app_router)
app.include_router(sales_app_router)
register_dispatch_module(app)
app.include_router(billing_router)
app.include_router(billing_app_router)
app.include_router(engineering_app_router)
app.include_router(hr_admin_router)
app.include_router(hr_employee_adjust_router)

app.include_router(admin_dispatch_router)
app.include_router(pages_router)

app.include_router(tickets_router)



@app.get("/", response_class=HTMLResponse)

def shinnan_erp_root_page():

    return """

<!doctype html>

<html lang="zh-Hant">

<head>

<meta charset="utf-8">

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Shinnan ERP｜訊南ERP系統</title>

<style>

*{box-sizing:border-box}

body{

  margin:0;

  min-height:100vh;

  font-family:"Microsoft JhengHei","Segoe UI",Arial,sans-serif;

  color:white;

  background:

    radial-gradient(circle at 15% 10%,rgba(0,255,255,.28),transparent 30%),

    radial-gradient(circle at 85% 20%,rgba(98,0,255,.30),transparent 34%),

    linear-gradient(135deg,#06111f,#0f3158 55%,#111827);

}

body:before{

  content:"";

  position:fixed;

  inset:0;

  background-image:

    linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),

    linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);

  background-size:42px 42px;

  pointer-events:none;

}

.wrap{

  position:relative;

  z-index:1;

  width:min(1180px,calc(100% - 40px));

  min-height:100vh;

  margin:auto;

  display:grid;

  grid-template-columns:1.05fr .95fr;

  gap:34px;

  align-items:center;

  padding:48px 0;

}

.card,.panel{

  border:1px solid rgba(255,255,255,.2);

  background:rgba(255,255,255,.1);

  backdrop-filter:blur(18px);

  border-radius:34px;

  box-shadow:0 28px 80px rgba(0,0,0,.38), inset 0 1px 0 rgba(255,255,255,.28);

}

.card{padding:40px}

.panel{padding:28px}

.brand{

  display:flex;

  align-items:center;

  gap:22px;

  margin-bottom:30px;

}



.logo{

  width:150px;

  height:92px;

  border-radius:0;

  background:transparent;

  box-shadow:none;

  overflow:visible;

  flex:0 0 auto;

}

.logo-img{

  width:150px;

  height:auto;

  display:block;

  object-fit:contain;

}



.zh{

  font-size:46px;

  font-weight:1000;

  letter-spacing:2px;

}

.en{

  margin-top:8px;

  font-size:22px;

  font-weight:900;

  letter-spacing:6px;

  color:#38e8ff;

}

.headline{

  font-size:56px;

  line-height:1.12;

  font-weight:1000;

  margin:20px 0;

}

.headline span{

  color:#38e8ff;

  text-shadow:0 0 26px rgba(56,232,255,.45);

}

.desc{

  color:#b7d7f7;

  font-size:20px;

  line-height:1.8;

  font-weight:700;

}

.status{

  margin-top:30px;

  font-size:15px;

  font-weight:900;

  color:#dcfce7;

}

.status:before{

  content:"";

  display:inline-block;

  width:12px;

  height:12px;

  margin-right:10px;

  border-radius:50%;

  background:#22c55e;

  box-shadow:0 0 18px #22c55e;

}

.panel-title{

  font-size:25px;

  font-weight:1000;

  margin-bottom:18px;

}

.grid{

  display:grid;

  grid-template-columns:1fr 1fr;

  gap:16px;

}

.module{

  min-height:116px;

  text-decoration:none;

  color:white;

  border-radius:24px;

  padding:20px;

  border:1px solid rgba(255,255,255,.18);

  background:linear-gradient(135deg,rgba(255,255,255,.18),rgba(255,255,255,.06));

  box-shadow:0 18px 28px rgba(0,0,0,.26), inset 0 1px 0 rgba(255,255,255,.25);

  transition:.16s;

}

.module:hover{

  transform:translateY(-5px);

  border-color:#38e8ff;

  box-shadow:0 26px 42px rgba(0,0,0,.36),0 0 28px rgba(56,232,255,.18);

}

.module-name{

  font-size:24px;

  font-weight:1000;

  margin-bottom:10px;

}

.module-desc{

  color:#cde5ff;

  font-size:14px;

  font-weight:700;

  line-height:1.55;

}

.footer{

  grid-column:1/-1;

  text-align:center;

  color:rgba(220,240,255,.7);

  font-size:13px;

  font-weight:700;

}

@media(max-width:900px){

  .wrap{grid-template-columns:1fr}

  .headline{font-size:42px}

  .zh{font-size:36px}

}

@media(max-width:560px){

  .wrap{width:calc(100% - 24px);padding:28px 0}

  .card,.panel{padding:22px;border-radius:26px}

  .grid{grid-template-columns:1fr}

  .logo{width:76px;height:76px}

  .zh{font-size:30px}

  .en{font-size:16px;letter-spacing:4px}

  .headline{font-size:34px}

}

/* shinnan-home-compact-v1 */

.wrap{

  min-height: 100vh !important;

  padding: 24px 0 !important;

  gap: 42px !important;

  align-items: center !important;

}



.card,

.panel{

  border-radius: 26px !important;

}



.card{

  padding: 26px !important;

}



.panel{

  padding: 20px !important;

}



.brand{

  gap: 16px !important;

  margin-bottom: 16px !important;

}



.logo{

  width: 72px !important;

  height: 72px !important;

  border-radius: 22px !important;

}











.zh{

  font-size: 34px !important;

}



.en{

  margin-top: 5px !important;

  font-size: 15px !important;

  letter-spacing: 4px !important;

}



.headline{

  font-size: 40px !important;

  line-height: 1.08 !important;

  margin: 12px 0 12px !important;

}



.desc{

  font-size: 16px !important;

  line-height: 1.55 !important;

}



.status{

  margin-top: 16px !important;

  font-size: 12px !important;

}



.panel-title{

  font-size: 21px !important;

  margin-bottom: 12px !important;

}



.grid{

  gap: 11px !important;

}



.module{

  min-height: 86px !important;

  border-radius: 18px !important;

  padding: 14px !important;

}



.module-name{

  font-size: 20px !important;

  margin-bottom: 6px !important;

}



.module-desc{

  font-size: 12px !important;

  line-height: 1.38 !important;

}



.footer{

  margin-top: -10px !important;

  font-size: 11px !important;

}

/* shinnan-home-compact-v1-end */

/* shinnan-home-equal-height-only-v1 */

.wrap {

  align-items: stretch !important;

}



.card,

.panel {

  min-height: 520px !important;

  height: 520px !important;

}



.card {

  display: flex !important;

  flex-direction: column !important;

  justify-content: center !important;

}



.panel {

  display: flex !important;

  flex-direction: column !important;

}



.grid {

  flex: 1 !important;

  align-content: start !important;

}



@media(max-width:900px){

  .card,

  .panel {

    height: auto !important;

    min-height: auto !important;

  }

}

/* shinnan-home-equal-height-only-v1-end */





/* SHINNAN_HOME_LOGO_SIZE_START */
.logo{
  width: 78px !important;
  height: 58px !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  overflow: visible !important;
  flex: 0 0 auto !important;
}

.logo:before,
.logo:after{
  display: none !important;
  content: none !important;
}

.logo-img{
  width: 78px !important;
  height: auto !important;
  display: block !important;
  object-fit: contain !important;
  background: transparent !important;
}
/* SHINNAN_HOME_LOGO_SIZE_END */





/* SHINNAN_HOME_LOGO_LAYOUT_FIX_V2 */
.erp-home-logo {
  width: 124px !important;
  height: 94px !important;
  object-fit: contain !important;
  flex: 0 0 auto !important;
  margin: 0 !important;
  transform: translate(18px, -28px) !important;
  filter: drop-shadow(0 5px 9px rgba(0,0,0,.18)) !important;
}

.brand,
.brand-row,
.hero-brand,
.logo-row,
.hero-title-row,
.left-brand,
.erp-brand {
  display: flex !important;
  align-items: center !important;
  gap: 22px !important;
  column-gap: 42px !important;
}

.erp-home-logo img,
img.erp-home-logo {
  max-width: 124px !important;
  max-height: 94px !important;
}
/* SHINNAN_HOME_LOGO_LAYOUT_FIX_V2_END */


/* SHINNAN_HOME_LOGO_ALIGN_UP_V3 */
.erp-home-logo {
  transform: translateY(-16px) !important;
}
/* SHINNAN_HOME_LOGO_ALIGN_UP_V3_END */








/* SHINNAN_HOME_LOGO_POSITION_ONLY_V6 */
img.erp-home-logo,
.erp-home-logo {
  width: 124px !important;
  height: 94px !important;
  transform: translate(18px, -28px) !important;
}
/* SHINNAN_HOME_LOGO_POSITION_ONLY_V6_END */

</style>

</head>

<body>

<div class="wrap">

  <section class="card">

    <div class="brand">

      <div class="logo"><img class="logo-img erp-home-logo" src="/erp-static/shinnan_home_logo.png" alt="ShinNan Logo"></div>

      <div>

        <div class="zh">訊南ERP系統</div>

        <div class="en">SHINNAN ERP</div>

      </div>

    </div>



    <div class="headline">電信營運管理<br><span>一站式中樞</span></div>

    <div class="desc">

      整合派工、帳務、客戶、大樓、業務與工程資料，讓公司管理與現場作業能在同一套平台快速銜接。

    </div>

    <div class="status">SHINNAN TELECOM OPERATION PLATFORM ONLINE</div>

  </section>



  <section class="panel">

    <div class="panel-title">請選擇系統入口</div>

    <div class="grid">

      <a class="module" href="/admin">

        <div class="module-name">派工系統</div>

        <div class="module-desc">案件建立、工程師指派、派工管理、完工追蹤與公司端後台。</div>

      </a>

      <a class="module" href="/admin/sales">
        <div class="module-name">業務系統</div>
        <div class="module-desc">大樓接觸、合約、拜訪、事件與回饋管理。</div>
      </a>

<a class="module" href="/admin/billing">

          <div class="module-name">帳務系統</div>

          <div class="module-desc">費用、押金、月租、材料與財務同步管理。</div>

        </a>

<a class="module" href="#" onclick="return openAdminModule('/admin?module=engineering')">

          <div class="module-name">工程系統</div>

          <div class="module-desc">拉線施工、線路建設、工程進度與施工紀錄管理。</div>

        </a>

<a class="module" href="/admin/hr">

          <div class="module-name">人事系統</div>

          <div class="module-desc">員工名冊、帳號、部門、職稱、休假與代理人設定。</div>

        </a>



<a class="module" href="#" onclick="return openAdminModule('/admin/buildings')">

          <div class="module-name">大樓資料</div>

          <div class="module-desc">社區大樓、設備 IP、管理公司、住戶數與大樓資料管理。</div>

        </a>

<a class="module" href="/admin/customers">
        <div class="module-name">客戶資料</div>
        <div class="module-desc">客戶資料、服務方案、帳務狀態、設備資訊與住戶名冊。</div>
      </a>

<a class="module" href="#" onclick="return openAdminModule('/admin/import')">

          <div class="module-name">匯入資料</div>

          <div class="module-desc">Excel、CSV、JSON、DB / SQL 資料匯入與預覽。</div>

        </a>

    </div>

  </section>



  <div class="footer">© Shinnan ERP System｜訊南科技內部管理平台</div>

</div>

<script>

// shinnan-entry-auth-router-v1

function isAdminLoggedIn() {

  const adminToken = localStorage.getItem("xunnan_admin_token") || "";

  const adminRole = localStorage.getItem("xunnan_admin_role") || "";

  const authToken = localStorage.getItem("xunnan_auth_token") || "";

  const loginRole = localStorage.getItem("xunnan_login_role") || "";



  if (adminToken && adminRole === "admin") return true;

  if (authToken && loginRole === "admin") {

    localStorage.setItem("xunnan_admin_token", authToken);

    localStorage.setItem("xunnan_admin_role", "admin");

    return true;

  }



  return false;

}



function openAdminModule(path) {

  if (isAdminLoggedIn()) {

    window.location.href = path;

  } else {

    window.location.href = "/employee/login?next=" + encodeURIComponent(path);

  }

  return false;

}

</script>
</body>

</html>

"""


# SHINNAN_EMPLOYEE_LOGIN_MIDDLEWARE_START
_LOGIN_COOKIE_NAME = "xunnan_employee_session"

def _xunnan_employee_session_valid(token: str) -> bool:
    if not token:
        return False

    try:
        with _login_engine.begin() as conn:
            row = conn.execute(
                _login_sql_text("""
                    SELECT s.session_token
                    FROM employee_sessions s
                    JOIN employee_accounts a ON a.staff_code = s.staff_code
                    WHERE s.session_token = :token
                      AND a.enabled = 1
                      AND datetime(s.expires_at) > datetime('now')
                    LIMIT 1
                """),
                {"token": token},
            ).first()

        return row is not None
    except Exception:
        return False


@app.middleware("http")
async def xunnan_employee_login_middleware(request, call_next):
    path = request.url.path

    protected = (
        path.startswith("/app/")
        or path.startswith("/api/app/")
    )

    if protected:
        token = request.cookies.get(_LOGIN_COOKIE_NAME, "")

        if not _xunnan_employee_session_valid(token):
            if path.startswith("/api/"):
                return _LoginJSONResponse(
                    {"ok": False, "error": "login required"},
                    status_code=401,
                )

            next_url = str(request.url.path)
            if request.url.query:
                next_url += "?" + request.url.query

            return _LoginRedirectResponse(
                "/employee/login?next=" + next_url,
                status_code=303,
            )

    return await call_next(request)
# SHINNAN_EMPLOYEE_LOGIN_MIDDLEWARE_END

# SHINNAN_FORCE_REMOVE_CLEAR_TEST_API_START
# 強制移除危險測試清除 API，避免誤刪正式派工資料
from fastapi.responses import JSONResponse as _ShinnanBlockJSONResponse

app.router.routes = [
    route for route in app.router.routes
    if not (
        getattr(route, "path", "") == "/api/tickets/test/clear"
        and "DELETE" in getattr(route, "methods", set())
    )
]

@app.delete("/api/tickets/test/clear", summary="測試清除派工資料 API 已永久停用")
def shinnan_disabled_clear_test_tickets_api():
    return _ShinnanBlockJSONResponse(
        status_code=403,
        content={"detail": "此測試清除 API 已永久停用，避免誤刪正式派工資料。"},
    )
# SHINNAN_FORCE_REMOVE_CLEAR_TEST_API_END











