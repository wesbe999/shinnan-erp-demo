from fastapi.responses import RedirectResponse
from app.routes.employee_auth import _employee_current_user_from_request
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["router-ipam"])


@router.get("/admin/router-ipam", response_class=HTMLResponse)
def admin_router_ipam_page(request: Request):
    _user = _employee_current_user_from_request(request)
    if not _user:
        return RedirectResponse(f"/employee/login?next=/admin/router-ipam", status_code=303)
    return HTMLResponse("""
<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Router IPAM | Shinnan ERP</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#eef3f9;color:#102348;font-family:"Microsoft JhengHei","Segoe UI",Arial,sans-serif}
.page{width:min(1180px,calc(100% - 32px));margin:24px auto 48px}
.hero{border-radius:22px;padding:26px;background:linear-gradient(135deg,#0f766e,#2563eb);color:#fff;box-shadow:0 18px 44px rgba(15,23,42,.16)}
h1{margin:0 0 10px;font-size:38px;font-weight:1000}
p{margin:0;color:rgba(255,255,255,.92);font-weight:850;line-height:1.7}
.panel{margin-top:16px;background:#fff;border:1px solid #d7e1ef;border-radius:18px;padding:18px;box-shadow:0 10px 26px rgba(15,23,42,.06)}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.item{border:1px solid #dbe5f2;border-radius:14px;padding:14px;background:#fbfdff}
.item b{display:block;margin-bottom:6px;color:#0f5132;font-size:18px}
.btn{display:inline-flex;align-items:center;justify-content:center;height:38px;padding:0 16px;border-radius:11px;background:#0f5132;color:#fff;text-decoration:none;font-weight:1000}
@media(max-width:760px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<main class="page">
  <section class="hero">
    <h1>&#x8def;&#x7531;&#x7ba1;&#x7406;</h1>
    <p>&#x9019;&#x662f; ERP &#x5167;&#x7684; Router / IPAM &#x7ba1;&#x7406;&#x5165;&#x53e3;&#x3002;&#x76ee;&#x524d;&#x4f5c;&#x70ba;&#x7b2c;&#x4e00;&#x968e;&#x6bb5;&#x9801;&#x9762;&#xff0c;&#x4e0d;&#x6703;&#x9023;&#x7dda;&#x6216;&#x4fee;&#x6539; MikroTik RouterOS &#x8a2d;&#x5b9a;&#x3002;</p>
  </section>
  <section class="panel">
    <div class="grid">
      <div class="item"><b>IP / MAC / &#x6236;&#x5225;</b><span>&#x5f8c;&#x7e8c;&#x532f;&#x5165; MikroTik DHCP lease &#x5f8c;&#x7d71;&#x4e00;&#x7ba1;&#x7406;&#x3002;</span></div>
      <div class="item"><b>&#x6b20;&#x8cbb;&#x9396;&#x5b9a;</b><span>&#x5148;&#x5efa;&#x7acb; ERP &#x5f85;&#x540c;&#x6b65;&#x72c0;&#x614b;&#xff0c;&#x78ba;&#x8a8d;&#x5f8c;&#x518d;&#x63a5; RouterOS &#x5beb;&#x5165;&#x3002;</span></div>
      <div class="item"><b>&#x4f7f;&#x7528;&#x91cf;&#x8207;&#x7570;&#x5e38;</b><span>&#x9810;&#x7559;&#x6d41;&#x91cf;&#x7d71;&#x8a08;&#x3001;&#x7570;&#x5e38;&#x544a;&#x8b66;&#x8207;&#x56de;&#x7ac4;&#x6aa2;&#x67e5;&#x3002;</span></div>
      <div class="item"><b>&#x8a0a;&#x865f;&#x6e2c;&#x901f;</b><span>&#x9810;&#x7559;&#x4e2d;&#x83ef;&#x96fb;&#x4fe1;&#x7b49; WAN &#x6e2c;&#x901f;&#x7d50;&#x679c;&#x767b;&#x8a18;&#x8207;&#x8b66;&#x793a;&#x3002;</span></div>
    </div>
  </section>
  <section class="panel"><a class="btn" href="/">&#x8fd4;&#x56de;&#x9996;&#x9801;</a></section>
</main>
<script src='/static/xn_theme.js?v=5'></script>
</body>
</html>
""")