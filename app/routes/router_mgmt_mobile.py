from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy import text as _sql
from app.db import engine as _engine
from app.routes.employee_auth import _employee_current_user_from_request

router = APIRouter(tags=["router-mgmt-mobile"])


def _fetch_buildings():
    with _engine.begin() as conn:
        rows = conn.execute(_sql("""
            SELECT building_no, name, area, address, ip
            FROM buildings
            WHERE ip IS NOT NULL AND ip != ''
            ORDER BY area, CAST(SUBSTR(building_no,2) AS INTEGER)
        """)).mappings().fetchall()
    return [dict(r) for r in rows]


@router.get("/api/router-mgmt-mobile/buildings")
def api_mobile_buildings(request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    return JSONResponse(_fetch_buildings())



_MOBILE_HTML = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="路由管理">
<meta name="theme-color" content="#184d3b">
<link rel="manifest" href="/static/router_mgmt_manifest.json">
<link rel="apple-touch-icon" href="/static/pwa_icon_192.png">
<title>路由管理｜訊南</title>
<link rel="stylesheet" href="/static/app_header_unified.css?v=20260511_title_v1">
<style>
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{background:#f0f2f5;font-family:"Microsoft JhengHei","Segoe UI",sans-serif;min-height:100vh;padding-bottom:32px}

/* ── Page wrap ── */
.page-wrap{max-width:600px;margin:0 auto}

/* ── Hero ── */
.hero{margin:0 0 0 0;border-radius:0!important;border-left:none!important;border-right:none!important}

/* ── 分區列 ── */
.area-bar{
  display:flex;gap:8px;overflow-x:auto;
  padding:12px 14px;background:#fff;
  border-bottom:1px solid #e5e7eb;
  scrollbar-width:none;
}
.area-bar::-webkit-scrollbar{display:none}
.area-btn{
  flex-shrink:0;height:32px;padding:0 14px;
  border-radius:16px;border:1.5px solid #d1d5db;
  background:#fff;color:#6b7280;font-size:13px;font-weight:600;
  cursor:pointer;transition:.15s;white-space:nowrap;
  font-family:inherit;
}
.area-btn.active{background:#16a34a;border-color:#16a34a;color:#fff}
.area-btn:active{opacity:.75}

/* ── 搜尋 ── */
.search-wrap{padding:10px 14px;background:#fff;border-bottom:1px solid #e5e7eb}
.search-box{
  width:100%;height:38px;padding:0 14px 0 36px;
  border:1.5px solid #d1d5db;border-radius:10px;
  background:#f9fafb url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='2'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cpath d='m21 21-4.35-4.35'/%3E%3C/svg%3E") no-repeat 10px center;
  color:#111827;font-size:14px;font-family:inherit;outline:none;
}
.search-box:focus{border-color:#16a34a;background-color:#fff}
.search-box::placeholder{color:#9ca3af}

/* ── 結果列 ── */
.result-bar{
  display:flex;align-items:center;justify-content:space-between;
  padding:8px 14px;background:#f9fafb;border-bottom:1px solid #e5e7eb;
}
.result-count{font-size:12px;color:#6b7280}
.result-hint{font-size:11px;color:#9ca3af}

/* ── 大樓列表 ── */
.building-list{padding:8px 14px;display:flex;flex-direction:column;gap:8px}

/* ── 大樓卡片 ── */
.bcard{
  background:#fff;border-radius:12px;
  box-shadow:0 1px 3px rgba(0,0,0,.08);
  padding:14px;
  display:flex;align-items:center;gap:12px;
}

/* 狀態燈 */
.status-dot{
  flex-shrink:0;width:12px;height:12px;border-radius:50%;
  background:#d1d5db;
  box-shadow:0 0 0 3px rgba(209,213,219,.3);
  transition:.3s;
}
.status-dot.online{
  background:#16a34a;
  box-shadow:0 0 0 3px rgba(22,163,74,.2);
  animation:pulse-green 2s infinite;
}
.status-dot.offline{
  background:#ef4444;
  box-shadow:0 0 0 3px rgba(239,68,68,.2);
}
@keyframes pulse-green{
  0%,100%{box-shadow:0 0 0 3px rgba(22,163,74,.2)}
  50%{box-shadow:0 0 0 6px rgba(22,163,74,.05)}
}

/* 大樓資訊 */
.binfo{flex:1;min-width:0}
.bname{font-size:15px;font-weight:700;color:#111827;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bno{font-size:11px;color:#9ca3af;margin-top:2px}
.bip{font-size:11px;font-family:monospace;color:#6b7280;margin-top:1px}

/* 按鈕群 */
.bactions{display:flex;flex-direction:column;gap:6px;flex-shrink:0}
.btn-rb{
  height:34px;padding:0 12px;border-radius:8px;
  background:#1d4ed8;border:none;color:#fff;
  font-size:12px;font-weight:700;font-family:inherit;
  cursor:pointer;white-space:nowrap;
  display:flex;align-items:center;gap:5px;
}
.btn-rb:active{opacity:.8}
.btn-nav{
  height:28px;padding:0 10px;border-radius:7px;
  background:#f3f4f6;border:1px solid #e5e7eb;color:#9ca3af;
  font-size:11px;font-weight:600;font-family:inherit;
  cursor:not-allowed;
  display:flex;align-items:center;gap:4px;
}
.btn-detail{
  height:28px;padding:0 10px;border-radius:7px;
  background:#f3f4f6;border:1px solid #e5e7eb;color:#9ca3af;
  font-size:11px;font-weight:600;font-family:inherit;
  cursor:not-allowed;
  display:flex;align-items:center;gap:4px;
}

/* ── 空狀態 ── */
.empty{text-align:center;padding:60px 0;color:#9ca3af;font-size:14px}

/* ── Loading ── */
.loading{text-align:center;padding:40px 0;color:#9ca3af;font-size:14px}
</style>
</head>
<body>
<div class="page-wrap">

  <!-- Header -->
  <section class="hero app-standard-hero">
    <div class="hero-main">
      <span class="hero-logo"><img class="hero-logo-img" src="/static/shinnan_home_logo.png" alt="Logo"></span>
      <h1 class="hero-title">路由管理</h1>
    </div>
    <div class="hero-sub" id="userLine">載入中...</div>
  </section>

  <!-- 分區列 -->
  <div class="area-bar" id="areaBar"></div>

  <!-- 搜尋 -->
  <div class="search-wrap">
    <input class="search-box" id="searchInput" type="text" placeholder="搜尋大樓名稱 / IP...">
  </div>

  <!-- 結果列 -->
  <div class="result-bar">
    <span class="result-count" id="resultCount">載入中...</span>
    <span class="result-hint">綠燈=在線｜紅燈=離線</span>
  </div>

  <!-- 大樓列表 -->
  <div class="building-list" id="buildingList">
    <div class="loading">資料載入中...</div>
  </div>

</div>

<script src="/static/app_header_actions.js?v=cl17p6"></script>
<script>
const AREAS_ORDER = ['東區','北區','安平','永康','高雄','北台南',''];
const AREA_LABEL  = {'':'未分區'};

let allData = [];
let currentArea = '__ALL__';
let searchVal = '';
let pingResults = {};

// ── 初始化 ──
async function init() {
  // 取得使用者名稱
  try {
    const ur = await fetch('/api/employee/me');
    if (ur.ok) {
      const u = await ur.json();
      document.getElementById('userLine').textContent =
        (u.display_name || u.staff_code || '') + (u.role ? '｜' + u.role : '');
    }
  } catch(e) {}

  // 載入大樓資料
  const res = await fetch('/api/router-mgmt-mobile/buildings');
  if (!res.ok) { window.location.href = '/employee/login?next=/router-mgmt-mobile'; return; }
  allData = await res.json();

  buildAreaBar();
  render();

  // 開始 ping
  startPing();
}

// ── 分區按鈕 ──
function buildAreaBar() {
  const counts = {'__ALL__': allData.length};
  for (const b of allData) {
    const a = b.area ?? '';
    counts[a] = (counts[a] || 0) + 1;
  }
  const areas = ['__ALL__', ...AREAS_ORDER.filter(a => counts[a])];
  for (const a of Object.keys(counts)) {
    if (!areas.includes(a)) areas.push(a);
  }

  const bar = document.getElementById('areaBar');
  bar.innerHTML = areas.map(a => {
    const label = a === '__ALL__' ? '全部' : (AREA_LABEL[a] || a);
    const cnt = counts[a] || 0;
    return `<button class="area-btn${a === currentArea ? ' active' : ''}"
      onclick="selectArea('${a.replace(/'/g,"\\'")}')">
      ${label} ${cnt}
    </button>`;
  }).join('');
}

// ── 選分區 ──
function selectArea(area) {
  currentArea = area;
  buildAreaBar();
  render();
}

// ── 渲染列表 ──
function render() {
  const q = searchVal.trim().toLowerCase();
  let list = currentArea === '__ALL__'
    ? allData
    : allData.filter(b => (b.area ?? '') === currentArea);
  if (q) list = list.filter(b =>
    b.name.toLowerCase().includes(q) ||
    (b.ip || '').toLowerCase().includes(q) ||
    b.building_no.toLowerCase().includes(q)
  );

  document.getElementById('resultCount').textContent = `共 ${list.length} 棟`;

  const el = document.getElementById('buildingList');
  if (!list.length) {
    el.innerHTML = '<div class="empty">無符合資料</div>';
    return;
  }

  el.innerHTML = list.map(b => {
    const ip = b.ip || '';
    const ping = pingResults[b.building_no];
    const dotClass = ping === undefined ? '' : (ping ? 'online' : 'offline');
    const rbUrl = ip ? `http://${ip}` : '';

    return `<div class="bcard">
  <div class="status-dot ${dotClass}" id="dot_${b.building_no}" title="${ping === undefined ? '檢測中' : (ping ? '在線' : '離線')}"></div>
  <div class="binfo">
    <div class="bname">${esc(b.name)}</div>
    <div class="bno">${esc(b.building_no)}${b.area ? '｜' + esc(b.area) : ''}</div>
    ${ip ? `<div class="bip">${esc(ip)}</div>` : ''}
  </div>
  <div class="bactions">
    ${rbUrl
      ? `<button class="btn-rb" onclick="openRB('${rbUrl}')">🖥️ 進入RB</button>`
      : `<button class="btn-rb" style="opacity:.4;cursor:not-allowed">🖥️ 進入RB</button>`
    }
    ${b.address
      ? `<button class="btn-nav" onclick="openNav('${esc(b.address)}')" style="color:#d97706;border-color:#fbbf24;cursor:pointer">📍 導航</button>`
      : `<button class="btn-nav" title="無地址資料">📍 導航</button>`
    }
    <button class="btn-detail" title="詳細資訊開發中">📋 詳情</button>
  </div>
</div>`;
  }).join('');
}

// ── 開啟導航 ──
function openNav(address) {
  const url = 'https://www.google.com/maps/dir/?api=1&destination=' + encodeURIComponent(address);
  window.open(url, '_blank');
}

// ── 開啟 RB ──
function openRB(url) {
  const w = window.open(url, '_blank');
  w.name = 'autologin=admin|pear';
  var t = setInterval(function() {
    try {
      if (w.document && w.document.getElementById('password')) {
        w.document.getElementById('password').value = 'pear';
        if (w.dologin) { w.dologin(); }
        clearInterval(t);
      }
    } catch(e) {}
  }, 300);
}

// ── Ping ──
async function pingBuilding(b) {
  try {
    const res = await fetch(`/api/router-mgmt/ping?ip=${encodeURIComponent(b.ip)}&no=${b.building_no}`, {signal: AbortSignal.timeout(8000)});
    if (!res.ok) return;
    const data = await res.json();
    pingResults[b.building_no] = data.alive;
    const dot = document.getElementById('dot_' + b.building_no);
    if (dot) {
      dot.className = 'status-dot ' + (data.alive ? 'online' : 'offline');
      dot.title = data.alive ? '在線' : '離線';
    }
  } catch(e) {}
}

function startPing() {
  // 分批 ping，每批 5 台，間隔 300ms
  const batch = 5;
  let idx = 0;
  function nextBatch() {
    const slice = allData.slice(idx, idx + batch);
    if (!slice.length) return;
    slice.forEach(b => { if (b.ip) pingBuilding(b); });
    idx += batch;
    if (idx < allData.length) setTimeout(nextBatch, 300);
  }
  nextBatch();
}

function esc(s) {
  return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

document.getElementById('searchInput').addEventListener('input', e => {
  searchVal = e.target.value;
  render();
});

init();
</script>
<script src="/static/app_header_actions.js?v=cl17p6"></script>
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/static/router_mgmt_sw.js')
    .then(() => console.log('SW registered'))
    .catch(e => console.log('SW error:', e));
}
</script>
</body>
</html>"""


@router.get("/router-mgmt-mobile", response_class=HTMLResponse)
def router_mgmt_mobile_page(request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return RedirectResponse("/employee/login/mobile?next=/router-mgmt-mobile", status_code=303)
    return HTMLResponse(_MOBILE_HTML)
