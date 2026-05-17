from fastapi.responses import RedirectResponse as _LoginRedirectResponse, JSONResponse as _LoginJSONResponse
from sqlalchemy import text as _login_sql_text
from app.db import engine as _login_engine

from pathlib import Path

from fastapi import FastAPI

from app.routes.billing import router as billing_router

from fastapi.responses import HTMLResponse

from fastapi.staticfiles import StaticFiles

from app.db import Base, engine, seed_demo_database_if_needed

from app.routes.notices import router as notices_router

from app.routes.communities import router as communities_router

from app.routes.mobile import router as mobile_router

from app.routes.employee_auth import router as employee_auth_router
from app.routes.employee_app import router as employee_app_router
from app.routes.sales_app import router as sales_app_router
from app.modules.dispatch.module import register as register_dispatch_module
from app.routes.billing_app import router as billing_app_router
from app.routes.engineering_app import router as engineering_app_router
from app.routes.maintenance_app import router as maintenance_app_router
from app.routes.hr_admin import router as hr_admin_router
from app.routes.hr_employee_adjust import router as hr_employee_adjust_router

from app.routes.admin_dispatch import router as admin_dispatch_router
from app.routes.buildings_admin import router as buildings_admin_router
from app.routes.sales_admin import router as sales_admin_router
from app.routes.sales_records_admin import router as sales_records_admin_router
from app.routes.customers_admin import router as customers_admin_router
from app.routes.sales_managers_admin import router as sales_managers_admin_router
from app.routes.ticket_customer_link_admin import router as ticket_customer_link_admin_router
from app.routes.employee_profiles_admin import router as employee_profiles_admin_router
from app.routes.stats_admin import router as stats_admin_router
from app.routes.router_ipam import router as router_ipam_router
from app.routes.pages import router as pages_router

from app.routes.tickets import router as tickets_router



seed_demo_database_if_needed()

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
app.include_router(maintenance_app_router)
app.include_router(hr_admin_router)
app.include_router(hr_employee_adjust_router)

app.include_router(admin_dispatch_router)
app.include_router(buildings_admin_router)
app.include_router(sales_admin_router)
app.include_router(sales_records_admin_router)
app.include_router(customers_admin_router)
app.include_router(sales_managers_admin_router)
app.include_router(ticket_customer_link_admin_router)
app.include_router(employee_profiles_admin_router)
app.include_router(stats_admin_router)
app.include_router(router_ipam_router)
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
<title>Shinnan ERP</title>
<style>
*{box-sizing:border-box}
html,body{
min-height:100vh;
  font-family:"Microsoft JhengHei","Segoe UI",Arial,sans-serif;
  color:#f4fff4;
  background:
    radial-gradient(circle at 14% 18%,rgba(128,255,74,.10),transparent 24%),
    radial-gradient(circle at 22% 78%,rgba(116,255,58,.16),transparent 30%),
    radial-gradient(circle at 62% 42%,rgba(58,180,76,.12),transparent 34%),
    radial-gradient(circle at 88% 14%,rgba(40,120,62,.22),transparent 28%),
    linear-gradient(135deg,#0a2015 0%,#143d24 28%,#1e5f31 52%,#102f1d 74%,#07160f 100%);
  overflow:hidden;
}
body{
  min-height:100vh;
  font-family:"Microsoft JhengHei","Segoe UI",Arial,sans-serif;
  color:#f4fff4;
  background:
    radial-gradient(circle at 32% 80%,rgba(126,255,61,.16),transparent 26%),
    radial-gradient(circle at 72% 18%,rgba(115,255,66,.12),transparent 28%),
    linear-gradient(135deg,#102e1d 0%,#1b5a2e 46%,#0b1f15 100%);
  overflow:hidden;
}
body:before{
content:"";
  position:fixed;
  inset:0;
  pointer-events:none;
  background-image:
    linear-gradient(rgba(164,255,92,.040) 1px,transparent 1px),
    linear-gradient(90deg,rgba(164,255,92,.032) 1px,transparent 1px),
    radial-gradient(circle at 1px 1px,rgba(166,255,92,.18) 1px,transparent 0);
  background-size:64px 64px,64px 64px,20px 20px;
  opacity:.72;
}
body:after{
content:"";
  position:fixed;
  inset:0;
  pointer-events:none;
  background:
    linear-gradient(90deg,rgba(0,0,0,.28),transparent 22%,transparent 72%,rgba(0,0,0,.26)),
    linear-gradient(180deg,rgba(255,255,255,.035),transparent 22%,rgba(0,0,0,.16) 100%),
    radial-gradient(ellipse at 30% 105%,rgba(158,255,68,.16),transparent 42%),
    radial-gradient(ellipse at 78% 0%,rgba(70,255,100,.07),transparent 36%);
  opacity:.95;
}
.shell{
position:relative;
  z-index:1;
  width:100vw;
  height:100vh;
  padding:16px 24px;
  overflow:hidden;
}
.portal{
position:relative;
  width:100%;
  height:100%;
  display:grid;
  grid-template-columns:48% 52%;
  height:100%;
  gap:28px;
  padding:24px 34px;
  border:1px solid rgba(143,255,73,.78);
  border-radius:24px;
  background:
    radial-gradient(circle at 18% 20%,rgba(255,255,255,.045),transparent 22%),
    radial-gradient(circle at 24% 82%,rgba(150,255,70,.085),transparent 34%),
    radial-gradient(circle at 60% 18%,rgba(100,255,90,.055),transparent 38%),
    linear-gradient(90deg,rgba(5,24,15,.82),rgba(16,62,32,.62) 46%,rgba(7,28,18,.76)),
    linear-gradient(180deg,rgba(255,255,255,.035),transparent 34%,rgba(0,0,0,.18));
  box-shadow:
    0 22px 64px rgba(0,0,0,.34),
    inset 0 1px 0 rgba(225,255,210,.08),
    inset 0 0 90px rgba(143,255,73,.055),
    0 0 24px rgba(143,255,73,.14);
  overflow:hidden;
}
.portal:before{
content:"";
  display:none;
}
.portal:after{
content:"";
  display:none;
}
.hero{
position:relative;
  min-width:0;
  display:flex;
  flex-direction:column;
  justify-content:flex-start;
  padding:0 34px 16px 24px;
}
.brand{
display:flex;
  align-items:center;
  gap:4px;
  margin-bottom:40px;
}
.logo-wrap{
  position:relative;
  display:inline-block;
  margin-left:-60px;
}
.logo-starburst{
  position:absolute;
  top:50%;
  left:50%;
  transform:translate(-50%,-52%);
  width:420px;
  height:420px;
  pointer-events:none;
  z-index:0;
  opacity:0.92;
}
.logo-img{
  width:132px;
  height:auto;
  object-fit:contain;
  display:block;
  position:relative;
  z-index:1;
  filter:drop-shadow(0 4px 12px rgba(0,0,0,.5));
}

.brand > div{
  transform:translateX(-39px);
}

.brand-zh{
color:#fff;
  font-size:32px;
  font-weight:1000;
  letter-spacing:5px;
  white-space:nowrap;
}
.brand-en{
margin-top:8px;
  color:#d4af37;
  font-size:14px;
  font-weight:900;
  letter-spacing:10px;
  white-space:nowrap;
}
.headline{
color:#fff;
  font-size:46px;
  line-height:1.04;
  font-weight:1000;
  letter-spacing:5px;
  text-shadow:0 0 18px rgba(255,255,255,.12);
  white-space:nowrap;
}
.headline-sub{
margin-top:12px;
  display:flex;
  align-items:center;
  gap:18px;
  color:#d4af37;
  font-size:34px;
  font-weight:1000;
  letter-spacing:6px;
  text-shadow:0 0 16px rgba(164,255,67,.24);
  white-space:nowrap;
}
.headline-sub:before,
.headline-sub:after{
  content:"";
  width:74px;
  height:3px;
  background:linear-gradient(90deg,transparent,#d4af37,transparent);
  box-shadow:0 0 14px rgba(164,255,67,.34);
}
.desc{
  position:absolute;
  left:24px;
  right:24px;
  bottom:28px;
  z-index:2;
  color:#e9f8e9;
  font-size:13.5px;
  line-height:1.55;
  font-weight:700;
  letter-spacing:.5px;
}
.status{
margin-top:24px;
  display:flex;
  align-items:center;
  gap:12px;
  color:#f8fff7;
  font-size:13px;
  font-weight:900;
  letter-spacing:.7px;
}
.status:before{
  content:"";
  width:14px;
  height:14px;
  border-radius:50%;
  background:#d4af37;
  box-shadow:0 0 18px rgba(145,255,62,.7);
}
.world{
display:none;
}

.world:before{
  content:"";
  position:absolute;
  left:0;
  right:0;
  bottom:18px;
  height:150px;
  background:
    radial-gradient(ellipse at 31% 110%,transparent 0 42%,rgba(160,255,80,.34) 42.2%,transparent 42.7% 100%),
    radial-gradient(ellipse at 31% 110%,transparent 0 55%,rgba(160,255,80,.24) 55.2%,transparent 55.7% 100%),
    radial-gradient(ellipse at 31% 110%,transparent 0 69%,rgba(160,255,80,.16) 69.2%,transparent 69.7% 100%);
  opacity:.78;
}
.world:after{
  content:"";
  position:absolute;
  left:12px;
  right:28px;
  bottom:54px;
  height:95px;
  background:
    linear-gradient(8deg,transparent 0 22%,rgba(206,255,188,.16) 22.1%,transparent 22.45% 100%),
    linear-gradient(-10deg,transparent 0 48%,rgba(150,255,76,.18) 48.1%,transparent 48.45% 100%),
    linear-gradient(18deg,transparent 0 64%,rgba(150,255,76,.13) 64.1%,transparent 64.42% 100%);
  opacity:.82;
}





.star-overlay{
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  object-fit:cover;
  pointer-events:none;
  mix-blend-mode:screen;
  opacity:0.55;
  z-index:0;
}
.world-img{
  position:absolute;
  left:-114px;
  right:auto;
  top:auto;
  bottom:-27px;
  width:255%;
  height:648px;
  object-fit:fill;
  pointer-events:none;
  opacity:.82;
  mix-blend-mode:screen;
  filter:drop-shadow(0 0 16px rgba(255,255,255,.14));
  z-index:1;
}


.panel{
min-width:0;
  display:flex;
  flex-direction:column;
  justify-content:flex-start;
  padding:0 0 10px 0;
  height:100%;
  min-height:0;
  overflow:hidden;
}
.panel-title{
display:flex;
  align-items:center;
  gap:15px;
  margin:0 0 14px;
  color:#d4af37;
  font-size:23px;
  font-weight:1000;
  letter-spacing:5px;
  white-space:nowrap;
}
.panel-title:before{
  content:"";
  width:10px;
  height:10px;
  border-radius:50%;
  background:#d4af37;
  box-shadow:0 0 18px rgba(145,255,62,.75);
}
.panel-title:after{
  content:"";
  flex:1;
  height:2px;
  background:linear-gradient(90deg,rgba(164,255,67,.72),rgba(164,255,67,.16),transparent);
}
.grid{
display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  grid-template-rows:repeat(4,1fr);
  gap:7px;
  flex:1;
  min-height:0;
  overflow:hidden;
}
.module{
position:relative;
  min-height:0;
  height:100%;
  display:flex;
  flex-direction:column;
  justify-content:center;
  padding:10px 36px 10px 16px;
  text-decoration:none;
  color:#fff;
  border:1px solid rgba(152,255,77,.55);
  border-radius:14px;
  background:
    linear-gradient(135deg,rgba(24,96,42,.40),rgba(8,34,20,.58)),
    radial-gradient(circle at 18% 20%,rgba(164,255,67,.09),transparent 28%);
  box-shadow:
    inset 0 1px 0 rgba(235,255,225,.10),
    0 10px 20px rgba(0,0,0,.20);
  overflow:hidden;
  transition:.16s ease;
}
.module-wip{
  opacity:0.55;
  cursor:default;
  background:repeating-linear-gradient(
    45deg,
    transparent,
    transparent 6px,
    rgba(255,255,255,.03) 6px,
    rgba(255,255,255,.03) 12px
  );
}
.module-wip .mi svg{
  opacity:0.5;
}
.module-wip .arrow{
  opacity:0.3;
}
.module-wip:hover{
  transform:none !important;
  border-color:rgba(255,255,255,.12) !important;
  box-shadow:none !important;
  cursor:not-allowed;
}
.module:hover{
  transform:translateY(-3px);
  border-color:#e8c84a;
  box-shadow:
    0 20px 36px rgba(0,0,0,.30),
    0 0 24px rgba(152,255,77,.18),
    inset 0 0 18px rgba(152,255,77,.07);
}
.mi{
width:36px;
  height:32px;
  display:flex;
  align-items:center;
  justify-content:flex-start;
  color:#d4af37;
  margin-bottom:6px;
}
.mi svg{
width:31px;
  height:31px;
  stroke:currentColor;
  fill:none;
  stroke-width:2;
  stroke-linecap:round;
  stroke-linejoin:round;
}
.module-name{
font-size:18px;
  font-weight:1000;
  letter-spacing:2px;
  margin-bottom:4px;
  white-space:nowrap;
}
.module-desc{
color:#e3f7e0;
  font-size:11.5px;
  font-weight:760;
  line-height:1.38;
  word-break:keep-all;
  overflow-wrap:normal;
}
.arrow{
position:absolute;
  right:16px;
  top:50%;
  transform:translateY(-50%);
  color:#d4af37;
  font-size:26px;
  font-weight:700;
  line-height:1;
}
.footer{
  position:absolute;
  left:50px;
  right:50px;
  bottom:6px;
  text-align:center;
  color:rgba(255,210,92,.82);
  font-size:16px;
  font-weight:900;
  letter-spacing:10px;
  text-shadow:0 0 16px rgba(255,210,92,.38);
}
@media(max-width:1380px){
  .shell{padding:10px 16px}
  .portal{gap:24px;padding:20px 28px}
  .hero{padding:0 26px 54px 20px}
  .brand{margin-bottom:32px}
  .logo-img{width:105px}
  .brand-zh{font-size:29px}
  .brand-en{font-size:13px}
  .headline{font-size:43px}
  .headline-sub{font-size:31px}
  .desc{font-size:15px;line-height:1.58;margin-top:22px}
  .status{font-size:12px;margin-top:20px}
  .world-img{
  position:absolute;
  left:-114px;
  right:auto;
  top:auto;
  bottom:-27px;
  width:255%;
  height:648px;
  object-fit:fill;
  pointer-events:none;
  opacity:.82;
  mix-blend-mode:screen;
  filter:drop-shadow(0 0 16px rgba(255,255,255,.14));
  z-index:1;
}
  .panel{padding:0 0 8px 0}
  .panel-title{font-size:19px;margin-bottom:8px}
  .grid{gap:10px}
  .module{min-height:0;padding:10px 32px 10px 15px}
  .mi{width:32px;height:28px;margin-bottom:5px}
  .mi svg{width:28px;height:28px}
  .module-name{font-size:18px}
  .module-desc{font-size:11.5px;line-height:1.34}
}
</style>
</head>
<body>
<div class="shell">
  <main class="portal">
    <section class="hero">
      <div class="brand">
        <div class="logo-wrap"><svg class="logo-starburst" viewBox="-210 -210 420 420" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fff8c0" stop-opacity="0.95"/>
      <stop offset="25%" stop-color="#ffd040" stop-opacity="0.7"/>
      <stop offset="60%" stop-color="#ffaa00" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="#ff8800" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow2" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffe080" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#ffcc00" stop-opacity="0"/>
    </radialGradient>
    <filter id="blur1"><feGaussianBlur stdDeviation="1.2"/></filter>
    <filter id="blur2"><feGaussianBlur stdDeviation="3"/></filter>
    <filter id="blur3"><feGaussianBlur stdDeviation="7"/></filter>
  </defs>
  <!-- 大光暈 -->
  <circle cx="0" cy="0" r="90" fill="url(#glow2)" filter="url(#blur3)"/>
  <!-- 中光暈 -->
  <circle cx="0" cy="0" r="45" fill="url(#glow)" filter="url(#blur2)"/>
  <!-- 主光芒 x4（長） -->
  <polygon points="0,-2 0,-190 0,2" fill="none" stroke="#ffe090" stroke-width="1.5" opacity="0.85" filter="url(#blur1)"/>
  <polygon points="0,-2 0,-190 0,2" fill="none" stroke="#ffe090" stroke-width="1.5" opacity="0.85" filter="url(#blur1)" transform="rotate(90)"/>
  <polygon points="0,-2 0,-190 0,2" fill="none" stroke="#ffe090" stroke-width="1.5" opacity="0.85" filter="url(#blur1)" transform="rotate(180)"/>
  <polygon points="0,-2 0,-190 0,2" fill="none" stroke="#ffe090" stroke-width="1.5" opacity="0.85" filter="url(#blur1)" transform="rotate(270)"/>
  <!-- 主光芒漸變填充 -->
  <defs>
    <linearGradient id="ray0" x1="0" y1="0" x2="0" y2="-1" gradientUnits="objectBoundingBox">
      <stop offset="0%" stop-color="#fff5a0" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#ffd000" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <polygon points="-1.5,0 0,-195 1.5,0" fill="#ffe888" opacity="0.7" filter="url(#blur1)"/>
  <polygon points="-1.5,0 0,-195 1.5,0" fill="#ffe888" opacity="0.7" filter="url(#blur1)" transform="rotate(90)"/>
  <polygon points="-1.5,0 0,-195 1.5,0" fill="#ffe888" opacity="0.7" filter="url(#blur1)" transform="rotate(180)"/>
  <polygon points="-1.5,0 0,-195 1.5,0" fill="#ffe888" opacity="0.7" filter="url(#blur1)" transform="rotate(270)"/>
  <!-- 斜光芒 x4（稍短） -->
  <polygon points="-1,0 0,-145 1,0" fill="#ffd060" opacity="0.55" filter="url(#blur1)" transform="rotate(45)"/>
  <polygon points="-1,0 0,-145 1,0" fill="#ffd060" opacity="0.55" filter="url(#blur1)" transform="rotate(135)"/>
  <polygon points="-1,0 0,-145 1,0" fill="#ffd060" opacity="0.55" filter="url(#blur1)" transform="rotate(225)"/>
  <polygon points="-1,0 0,-145 1,0" fill="#ffd060" opacity="0.55" filter="url(#blur1)" transform="rotate(315)"/>
  <!-- 細光芒 x8（短） -->
  <polygon points="-0.7,0 0,-90 0.7,0" fill="#ffcc40" opacity="0.4" transform="rotate(22.5)"/>
  <polygon points="-0.7,0 0,-90 0.7,0" fill="#ffcc40" opacity="0.4" transform="rotate(67.5)"/>
  <polygon points="-0.7,0 0,-90 0.7,0" fill="#ffcc40" opacity="0.4" transform="rotate(112.5)"/>
  <polygon points="-0.7,0 0,-90 0.7,0" fill="#ffcc40" opacity="0.4" transform="rotate(157.5)"/>
  <polygon points="-0.7,0 0,-90 0.7,0" fill="#ffcc40" opacity="0.4" transform="rotate(202.5)"/>
  <polygon points="-0.7,0 0,-90 0.7,0" fill="#ffcc40" opacity="0.4" transform="rotate(247.5)"/>
  <polygon points="-0.7,0 0,-90 0.7,0" fill="#ffcc40" opacity="0.4" transform="rotate(292.5)"/>
  <polygon points="-0.7,0 0,-90 0.7,0" fill="#ffcc40" opacity="0.4" transform="rotate(337.5)"/>
  <!-- 中心亮核 -->
  <circle cx="0" cy="0" r="10" fill="#fffbe0" opacity="0.95" filter="url(#blur2)"/>
  <circle cx="0" cy="0" r="4" fill="#ffffff" opacity="1"/>
</svg><img class="logo-img" src="/erp-static/shinnan_home_logo.png" alt="ShinNan Logo"></div>
        <div>
          <div class="brand-zh">\u8a0a\u5357 ERP \u7cfb\u7d71</div>
          <div class="brand-en">SHINNAN ERP</div>
        </div>
      </div>
      <div class="headline">\u96fb\u4fe1\u71df\u904b\u7ba1\u7406</div>
      <div class="headline-sub">\u4e00\u7ad9\u5f0f\u4e2d\u6a1e</div>
      
      <div class="desc">\u6574\u5408\u6d3e\u5de5\u3001\u5e33\u52d9\u3001\u5ba2\u6236\u3001\u5927\u6a13\u3001\u696d\u52d9\u8207\u5de5\u7a0b\u8cc7\u6599\uff0c\u8b93\u516c\u53f8\u7ba1\u7406\u8207\u73fe\u5834\u4f5c\u696d\u80fd\u5728\u540c\u4e00\u5957\u5e73\u53f0\u5feb\u901f\u8854\u63a5\u3002</div>

      <img class="star-overlay" src="/static/star_overlay_black_to_transparent.png" alt="">
      <img class="world-img" src="/erp-static/home_globe_wire_transparent_stronger.png?v=20260512211904" alt="">

    </section>

    <section class="panel">
      <div class="panel-title">\u8acb\u9078\u64c7\u7cfb\u7d71\u5165\u53e3</div>
      <div class="grid">
        <a class="module" href="#" onclick="return openAdminModule('/admin/router-ipam')"><div class="mi"><svg viewBox="0 0 24 24"><path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/><circle cx="8" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="10" cy="18" r="2"/></svg></div><div><div class="module-name">\u8def\u7531\u7ba1\u7406</div><div class="module-desc">IP\u3001MAC\u3001\u6236\u5225\u3001\u901f\u7387\u8207\u6b20\u8cbb\u9396\u5b9a\u7ba1\u7406\u3002</div></div><div class="arrow">&rsaquo;</div></a>
        <a class="module" href="/admin"><div class="mi"><svg viewBox="0 0 24 24"><path d="M3 7h11v8H3z"/><path d="M14 10h4l3 3v2h-7z"/><circle cx="6" cy="17" r="2"/><circle cx="18" cy="17" r="2"/></svg></div><div><div class="module-name">\u6d3e\u5de5\u7cfb\u7d71</div><div class="module-desc">\u6848\u4ef6\u5efa\u7acb\u3001\u5de5\u7a0b\u5e2b\u6307\u6d3e\u3001\u6d3e\u5de5\u7ba1\u7406\u8207\u5b8c\u5de5\u8ffd\u8e64\u3002</div></div><div class="arrow">&rsaquo;</div></a>
        <a class="module" href="/admin/sales"><div class="mi"><svg viewBox="0 0 24 24"><path d="M4 19V9"/><path d="M10 19V5"/><path d="M16 19v-7"/><path d="M3 19h18"/><path d="M7 9l3-4 4 7 5-8"/></svg></div><div><div class="module-name">\u696d\u52d9\u7cfb\u7d71</div><div class="module-desc">\u5927\u6a13\u63a5\u89f8\u3001\u5408\u7d04\u3001\u62dc\u8a2a\u3001\u4e8b\u4ef6\u8207\u56de\u994b\u7ba1\u7406\u3002</div></div><div class="arrow">&rsaquo;</div></a>
        <a class="module" href="/admin/billing"><div class="mi"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v10"/><path d="M15 9.5c-.8-.8-4-.9-4 1 0 2 4 1 4 3 0 2-3.2 1.8-4.4.8"/></svg></div><div><div class="module-name">\u5e33\u52d9\u7cfb\u7d71</div><div class="module-desc">\u8cbb\u7528\u3001\u62bc\u91d1\u3001\u6708\u79df\u3001\u6750\u6599\u8207\u8ca1\u52d9\u540c\u6b65\u7ba1\u7406\u3002</div></div><div class="arrow">&rsaquo;</div></a>
        <a class="module" href="#" onclick="return openAdminModule('/admin/engineering')"><div class="mi"><svg viewBox="0 0 24 24"><path d="M14 7l3-3 3 3-3 3z"/><path d="M5 20l8-8"/><path d="M6 6l12 12"/><path d="M4 8l4-4"/></svg></div><div><div class="module-name">\u5de5\u7a0b\u7cfb\u7d71</div><div class="module-desc">\u62c9\u7dda\u65bd\u5de5\u3001\u7dda\u8def\u5efa\u8a2d\u3001\u5de5\u7a0b\u9032\u5ea6\u8207\u7d00\u9304\u7ba1\u7406\u3002</div></div><div class="arrow">&rsaquo;</div></a>
        <a class="module" href="/admin/hr"><div class="mi"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 14.5-4 16 0"/></svg></div><div><div class="module-name">\u4eba\u4e8b\u7cfb\u7d71</div><div class="module-desc">\u54e1\u5de5\u540d\u518a\u3001\u5e33\u865f\u3001\u90e8\u9580\u3001\u8077\u7a31\u3001\u4f11\u5047\u8207\u4ee3\u7406\u8a2d\u5b9a\u3002</div></div><div class="arrow">&rsaquo;</div></a>
        <a class="module" href="#" onclick="return openAdminModule('/admin/buildings')"><div class="mi"><svg viewBox="0 0 24 24"><path d="M5 21V5h8v16"/><path d="M13 9h6v12"/><path d="M8 8h2M8 12h2M8 16h2M16 13h1M16 17h1"/></svg></div><div><div class="module-name">\u5927\u6a13\u8cc7\u6599</div><div class="module-desc">\u793e\u5340\u5927\u6a13\u3001\u8a2d\u5099IP\u3001\u7ba1\u7406\u516c\u53f8\u8207\u4f4f\u6236\u8cc7\u6599\u3002</div></div><div class="arrow">&rsaquo;</div></a>
        <a class="module" href="/admin/customers"><div class="mi"><svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"/><path d="M3 20c1-4 11-4 12 0"/><circle cx="17" cy="10" r="2.5"/><path d="M15 20c.7-2.6 5.4-2.6 6 0"/></svg></div><div><div class="module-name">\u5ba2\u6236\u8cc7\u6599</div><div class="module-desc">\u5ba2\u6236\u8cc7\u6599\u3001\u670d\u52d9\u65b9\u6848\u3001\u5e33\u52d9\u72c0\u614b\u8207\u8a2d\u5099\u8cc7\u8a0a\u3002</div></div><div class="arrow">&rsaquo;</div></a>
        <a class="module" href="#" onclick="return openAdminModule('/admin/stats')"><div class="mi"><svg viewBox="0 0 24 24"><path d="M4 4h16v16H4z"/><path d="M8 8h8M8 12h8M8 16h5"/></svg></div><div><div class="module-name">\u8cc7\u6599\u7d71\u8a08</div><div class="module-desc">營運資料彙整分析，產生統計與管理報告。</div></div><div class="arrow">&rsaquo;</div></a>
        <a class="module" href="#" onclick="return openAdminModule('/admin/import')"><div class="mi"><svg viewBox="0 0 24 24"><ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/><path d="M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/></svg></div><div><div class="module-name">\u532f\u5165\u8cc7\u6599</div><div class="module-desc">Excel/CSV/JSON\u3001\u5305\u62ecSQL\u8cc7\u6599\u532f\u5165\u3002</div></div><div class="arrow">&rsaquo;</div></a>
      <div class="module module-wip">
        <div class="mi"><svg viewBox="0 0 24 24"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg></div>
        <div><div class="module-name">施工中</div><div class="module-desc">功能開發中，敬請期待。</div></div>
        <div class="arrow">&rsaquo;</div>
      </div>
      <div class="module module-wip">
        <div class="mi"><svg viewBox="0 0 24 24"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg></div>
        <div><div class="module-name">施工中</div><div class="module-desc">功能開發中，敬請期待。</div></div>
        <div class="arrow">&rsaquo;</div>
      </div>
     
      </div>
    </section>
    <div class="footer">SHINNAN ERP SYSTEM</div>
  </main>
</div>

<script>
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

            next_base = next_url.split("?", 1)[0]
            if next_base in {
                "/app/dispatch",
                "/app/sales",
                "/app/sales/new",
                "/app/billing",
                "/app/engineering",
                "/app/maintenance",
                "/app/manager",
            }:
                next_url = "/app"

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











