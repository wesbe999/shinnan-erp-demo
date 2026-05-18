from fastapi.responses import RedirectResponse
from app.routes.employee_auth import _employee_current_user_from_request
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.routes.router_mgmt import _fetch_router_buildings

router = APIRouter(tags=["router-mgmt-mobile"])


_MOBILE_HTML = r"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>路由管理 Mobile | Shinnan ERP</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{background:#0d1117;color:#e6edf3;font-family:"Microsoft JhengHei","Segoe UI",sans-serif;min-height:100vh;overscroll-behavior:none}

/* ── Top Bar ── */
.top-bar{
  position:sticky;top:0;z-index:50;
  background:#161b22;border-bottom:1px solid #30363d;
  padding:0 16px;height:52px;
  display:flex;align-items:center;justify-content:space-between;
}
.top-bar .title{font-size:16px;font-weight:700;color:#d4af37}
.top-bar .back-btn{
  font-size:13px;color:#8b949e;
  background:none;border:none;cursor:pointer;padding:6px 0;
  display:flex;align-items:center;gap:4px;
}
.top-bar .back-btn:active{color:#e6edf3}

/* ── Search ── */
.search-wrap{
  padding:10px 16px;background:#0d1117;
  border-bottom:1px solid #21262d;
  position:sticky;top:52px;z-index:40;
}
.search-box{
  width:100%;height:38px;padding:0 14px;
  background:#161b22;border:1px solid #30363d;border-radius:8px;
  color:#e6edf3;font-size:14px;outline:none;
}
.search-box:focus{border-color:#d4af37}
.search-box::placeholder{color:#484f58}

/* ── Layer ── */
.layer{display:none}
.layer.active{display:block}

/* ── 第一層：分區 ── */
.area-list{padding:12px 16px;display:flex;flex-direction:column;gap:8px}
.area-card{
  background:#161b22;border:1px solid #30363d;border-radius:12px;
  padding:16px;display:flex;align-items:center;justify-content:space-between;
  cursor:pointer;transition:.12s;
}
.area-card:active{background:#1c2128;border-color:#d4af3750}
.area-card .area-name{font-size:16px;font-weight:700;color:#e6edf3}
.area-card .area-meta{display:flex;align-items:center;gap:8px}
.area-card .area-count{
  font-size:13px;color:#8b949e;
  background:#21262d;border-radius:6px;padding:2px 8px;
}
.area-card .area-arrow{color:#484f58;font-size:18px}

/* ── 第二層：大樓列表 ── */
.building-list{padding:8px 16px 80px;display:flex;flex-direction:column;gap:1px}
.building-item{background:#161b22;border-bottom:1px solid #21262d}
.building-item:first-child{border-radius:12px 12px 0 0}
.building-item:last-child{border-radius:0 0 12px 12px;border-bottom:none}
.building-item:only-child{border-radius:12px}

.building-header{
  padding:14px 16px;display:flex;align-items:center;justify-content:space-between;
  cursor:pointer;
}
.building-header:active{background:#1c2128}
.building-info .b-name{font-size:15px;font-weight:700;color:#e6edf3}
.building-info .b-ip{font-size:12px;font-family:"Courier New",monospace;color:#58a6ff;margin-top:3px}
.building-info .b-ip.no-ip{color:#484f58;font-family:inherit}
.building-arrow{
  color:#484f58;font-size:16px;transition:transform .2s;flex-shrink:0;
}
.building-item.open .building-arrow{transform:rotate(90deg);color:#d4af37}

/* ── 展開面板 ── */
.building-panel{
  display:none;padding:0 16px 14px;
  display:grid;grid-template-columns:1fr 1fr;gap:8px;
  overflow:hidden;max-height:0;transition:max-height .25s ease;
}
.building-item.open .building-panel{max-height:200px}

.action-btn{
  display:flex;align-items:center;justify-content:center;gap:6px;
  height:44px;border-radius:10px;border:1px solid;
  font-size:13px;font-weight:700;text-decoration:none;
  cursor:pointer;transition:.12s;
}
.action-btn:active{opacity:.75}
.btn-home{background:#1f3a2a;border-color:#2ea04330;color:#3fb950}
.btn-bind{background:#0d2136;border-color:#1f6feb30;color:#58a6ff}
.btn-log {background:#2d1f0a;border-color:#e3b34130;color:#e3b341}
.btn-block{background:#2d0f0f;border-color:#f8514930;color:#f85149}
.btn-dhcp{background:#0d2136;border-color:#1f6feb30;color:#58a6ff;grid-column:1/-1}

/* ── 空狀態 ── */
.empty{text-align:center;padding:60px 0;color:#484f58;font-size:14px}

/* ── 結果計數 ── */
.result-label{
  font-size:12px;color:#8b949e;padding:8px 16px 4px;
}
</style>
</head>
<body>

<header class="top-bar">
  <button class="back-btn" id="backBtn" onclick="goBack()">&#8592; 返回</button>
  <div class="title" id="topTitle">路由管理</div>
  <a style="font-size:12px;color:#8b949e;text-decoration:none" href="/router-mgmt">電腦版</a>
</header>

<div class="search-wrap" id="searchWrap" style="display:none">
  <input class="search-box" id="searchInput" type="text" placeholder="搜尋大樓名稱 / IP...">
</div>

<!-- 第一層：分區 -->
<div class="layer active" id="layer1">
  <div class="area-list" id="areaList"></div>
</div>

<!-- 第二層：大樓列表 -->
<div class="layer" id="layer2">
  <div class="result-label" id="resultLabel"></div>
  <div class="building-list" id="buildingList"></div>
</div>

<script>
const AREAS_ORDER = ['東區','北區','安平','永康','高雄','北台南',''];
const AREA_LABEL  = {'':'未分區'};

let allData = [];
let currentArea = '';
let currentLayer = 1;
let searchVal = '';

async function init(){
  const res = await fetch('/api/router-mgmt/buildings');
  allData = await res.json();
  buildAreaList();
}

/* ── 第一層 ── */
function buildAreaList(){
  const counts = {};
  for(const b of allData){
    const a = b.area ?? '';
    counts[a] = (counts[a]||0)+1;
  }
  const areas = [...AREAS_ORDER.filter(a=>counts[a])];
  for(const a of Object.keys(counts)) if(!areas.includes(a)) areas.push(a);

  const el = document.getElementById('areaList');
  el.innerHTML = areas.map(a=>`
    <div class="area-card" onclick="enterArea('${a.replace(/'/g,"\\'")}')">
      <span class="area-name">${AREA_LABEL[a]||a}</span>
      <span class="area-meta">
        <span class="area-count">${counts[a]} 棟</span>
        <span class="area-arrow">›</span>
      </span>
    </div>
  `).join('');
}

/* ── 進入第二層 ── */
function enterArea(area){
  currentArea = area;
  currentLayer = 2;
  document.getElementById('topTitle').textContent = AREA_LABEL[area]||area;
  document.getElementById('backBtn').style.display = 'flex';
  document.getElementById('searchWrap').style.display = 'block';
  document.getElementById('layer1').classList.remove('active');
  document.getElementById('layer2').classList.add('active');
  searchVal = '';
  document.getElementById('searchInput').value = '';
  renderBuildings();
}

/* ── 渲染大樓列表 ── */
function renderBuildings(){
  const q = searchVal.trim().toLowerCase();
  let list = allData.filter(b=>(b.area??'')=== currentArea);
  if(q) list = list.filter(b=>
    b.name.toLowerCase().includes(q) ||
    (b.ip||'').toLowerCase().includes(q)
  );

  document.getElementById('resultLabel').textContent = `共 ${list.length} 棟`;
  const el = document.getElementById('buildingList');

  if(!list.length){
    el.innerHTML = '<div class="empty">無符合資料</div>';
    return;
  }

  el.innerHTML = list.map(b=>{
    const ip   = b.ip||'';
    const base = ip ? `http://${ip}` : '';
    const btn  = (label, hash, cls) => base
      ? `<a class="action-btn ${cls}" href="${base}/webfig/#${hash}" onclick="window.open(this.href);return false;">${label}</a>`
      : `<span class="action-btn ${cls}" style="opacity:.35;pointer-events:none">${label}</span>`;
    return `
<div class="building-item" id="bi_${b.building_no}">
  <div class="building-header" onclick="toggleBuilding('${b.building_no}')">
    <div class="building-info">
      <div class="b-name">${esc(b.name)}</div>
      <div class="b-ip ${ip?'':'no-ip'}">${ip||'無 IP'}</div>
    </div>
    <span class="building-arrow">›</span>
  </div>
  <div class="building-panel" id="bp_${b.building_no}">
    ${btn('🖥️ 主頁',   '',                        'btn-home')}
    ${btn('🔗 IP綁定', 'ip-binding',               'btn-bind')}
    ${btn('📋 LOG',    'log',                      'btn-log')}
    ${btn('🔒 封鎖',   'ip-firewall/address-lists','btn-block')}
    ${btn('📡 DHCP',   'dhcp-server/leases',       'btn-dhcp')}
  </div>
</div>`;
  }).join('');
}

/* ── 展開/收合 ── */
function toggleBuilding(no){
  const item  = document.getElementById('bi_'+no);
  const panel = document.getElementById('bp_'+no);
  const isOpen = item.classList.contains('open');

  document.querySelectorAll('.building-item.open').forEach(el=>{
    el.classList.remove('open');
    el.querySelector('.building-panel').style.display='none';
  });

  if(!isOpen){
    item.classList.add('open');
    panel.style.display='grid';
  }
}

/* ── 返回 ── */
function goBack(){
  if(currentLayer===2){
    currentLayer=1;
    document.getElementById('topTitle').textContent='路由管理';
    document.getElementById('searchWrap').style.display='none';
    document.getElementById('layer2').classList.remove('active');
    document.getElementById('layer1').classList.add('active');
    document.getElementById('backBtn').style.display='none';
  } else {
    window.location.href='/app';
  }
}

function esc(s){ return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') }

document.getElementById('searchInput').addEventListener('input',e=>{
  searchVal=e.target.value; renderBuildings();
});
document.getElementById('backBtn').style.display='none';

init();
</script>
</body>
</html>"""


@router.get("/router-mgmt-mobile", response_class=HTMLResponse)
def router_mgmt_mobile_page(request: Request):
    _user = _employee_current_user_from_request(request)
    if not _user:
        return RedirectResponse(f"/employee/login?next=/router-mgmt-mobile", status_code=303)
    return HTMLResponse(_MOBILE_HTML)
