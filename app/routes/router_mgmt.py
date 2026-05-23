from app.routes.employee_auth import _employee_current_user_from_request
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy import text as _sql
from app.db import engine as _engine
import asyncio
import subprocess
import platform

try:
    import httpx
    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False

router = APIRouter(tags=["router-mgmt"])

# ──────────────────────────────────────────────
# NMS 設定
# ──────────────────────────────────────────────
_NMS_BASE    = "http://211.23.120.73:82"
_NMS_USER    = "sys_01"
_NMS_PASS    = "1@3$"
_NMS_TIMEOUT = 15

# 全域 NMS session（cookie 快取）
_nms_cookies: dict[str, str] = {}

def _ddns_from_serial(serial: str | None) -> str:
    serial = (serial or "").strip().lower()
    if not serial:
        return ""
    return f"{serial}.sn.mynetname.net"

async def _nms_ensure_login() -> bool:
    """確保已登入 NMS，回傳是否成功。"""
    global _nms_cookies
    async with httpx.AsyncClient(timeout=_NMS_TIMEOUT, follow_redirects=True) as c:
        # 先試查看是否已登入
        if _nms_cookies:
            r = await c.get(
                f"{_NMS_BASE}/app/r2/?op=devices&action=list_online",
                cookies=_nms_cookies,
            )
            if "裝置列表" in r.text or "SF_" in r.text:
                return True
        # 重新登入
        r = await c.post(
            f"{_NMS_BASE}/check_login.php",
            data={"member": _NMS_USER, "password": _NMS_PASS, "login": "登入"},
            headers={"Referer": f"{_NMS_BASE}/"},
        )
        _nms_cookies = dict(r.cookies)
        return "裝置列表" in r.text or "SF_" in r.text or bool(_nms_cookies)

async def _nms_fetch_devices(offline: bool = False) -> list[dict]:
    """從 NMS 抓裝置列表，解析後回傳。"""
    from html.parser import HTMLParser

    action = "list_offline" if offline else "list_online"
    await _nms_ensure_login()

    async with httpx.AsyncClient(timeout=_NMS_TIMEOUT, follow_redirects=True) as c:
        r = await c.get(
            f"{_NMS_BASE}/app/r2/?op=devices&action={action}",
            cookies=_nms_cookies,
        )

    # 解析 button[title] 結構
    class _Parser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.devices = []
            self._in_btn  = False
            self._cur     = {}
            self._text    = ""
            self._last_did = ""

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == "input" and a.get("name") == "DID":
                self._last_did = a.get("value", "")
            if tag == "button" and "title" in a:
                css = a.get("class", "")
                status = "online" if "SF_1" in css else (
                    "offline" if "SF_0" in css else (
                    "warning" if "SF_2" in css else "unknown"))
                lines = a["title"].split("\n")
                serial = lines[3].strip() if len(lines) > 3 else ""
                self._cur = {
                    "did":      self._last_did,
                    "name":     "",
                    "model":    lines[1].strip() if len(lines) > 1 else "",
                    "identity": lines[2].strip() if len(lines) > 2 else "",
                    "serial":   serial,
                    "ddns":     _ddns_from_serial(serial),
                    "status":   status,
                    "community":lines[0].strip() if lines else "",
                }
                self._in_btn = True
                self._text   = ""
        def handle_data(self, data):
            if self._in_btn:
                self._text += data
        def handle_endtag(self, tag):
            if tag == "button" and self._in_btn:
                self._cur["name"] = self._text.strip()
                self.devices.append(self._cur)
                self._in_btn = False
                self._cur    = {}

    p = _Parser()
    p.feed(r.text)
    return p.devices

async def _nms_fetch_detail(did: str) -> str:
    """取得單台裝置詳情 HTML。"""
    await _nms_ensure_login()
    async with httpx.AsyncClient(timeout=_NMS_TIMEOUT, follow_redirects=True) as c:
        r = await c.post(
            f"{_NMS_BASE}/app/r2/?op=devices&action=info",
            data={"DID": did},
            cookies=_nms_cookies,
        )
    return r.text


# ──────────────────────────────────────────────
# 資料庫：取得大樓列表
# ──────────────────────────────────────────────
def _fetch_router_buildings():
    with _engine.begin() as conn:
        rows = conn.execute(_sql("""
            SELECT building_no, name, area, ip
            FROM buildings
            WHERE ip IS NOT NULL AND ip != ''
            ORDER BY area, CAST(substr(building_no, 2) AS INTEGER)
        """)).mappings().fetchall()
    return [dict(r) for r in rows]

# ──────────────────────────────────────────────
# API：大樓列表
# ──────────────────────────────────────────────
@router.get("/api/router-mgmt/buildings")
def api_router_buildings():
    return JSONResponse(_fetch_router_buildings())

# ──────────────────────────────────────────────
# DB 查詢：r2_devices 資料表
# ──────────────────────────────────────────────
def _fetch_r2_devices_from_db(offline: bool = False) -> list[dict]:
    try:
        with _engine.begin() as conn:
            where = "WHERE class_name = 'SF_0'" if offline else "WHERE class_name != 'SF_0'"
            rows = conn.execute(_sql(f"""
                SELECT device_id, building_name, community, device_no as identity,
                       model, serial, routeros_version, management_ip, management_port,
                       management_url, circuit_no, bandwidth, uptime, checked_at,
                       class_name, form_id
                FROM r2_devices
                {where}
                ORDER BY community
            """)).mappings().fetchall()
        result = []
        for r in rows:
            d = dict(r)
            cn = d.get("class_name", "SF_1")
            d["status"] = "offline" if cn == "SF_0" else ("warning" if cn in ("SF_2","SF_4") else "online")
            d["did"]    = d["device_id"]
            d["name"]   = d["community"] or d["building_name"]
            d["ddns"]   = _ddns_from_serial(d.get("serial"))
            result.append(d)
        return result
    except Exception:
        return []

# ──────────────────────────────────────────────
# API：NMS 裝置列表（DB 優先，live=true 爬 NMS）
# ──────────────────────────────────────────────
@router.get("/api/router-mgmt/nms-devices")
async def api_nms_devices(offline: bool = False, live: bool = False):
    try:
        if not live:
            devices = _fetch_r2_devices_from_db(offline=offline)
            if devices:
                return JSONResponse({"ok": True, "devices": devices, "source": "db"})
        devices = await _nms_fetch_devices(offline=offline)
        return JSONResponse({"ok": True, "devices": devices, "source": "nms"})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=502)

# ──────────────────────────────────────────────
# API：NMS 裝置詳情（ERP proxy）
# ──────────────────────────────────────────────
@router.get("/api/router-mgmt/nms-device/{did}")
async def api_nms_device_detail(did: str):
    try:
        html = await _nms_fetch_detail(did)
        # 解析關鍵資訊
        import re
        def _pick(label: str) -> str:
            m = re.search(rf"{label}[：:]\s*(.+)", html)
            return m.group(1).strip() if m else ""
        # 找圖片（img src）
        imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)
        img_urls = []
        for src in imgs:
            if src.startswith("http"):
                img_urls.append(src)
            elif src.startswith("/"):
                img_urls.append(f"{_NMS_BASE}{src}")
            else:
                img_urls.append(f"{_NMS_BASE}/app/r2/{src}")
        serial = _pick("序號")
        return JSONResponse({
            "ok": True,
            "serial":   serial,
            "ddns":     _ddns_from_serial(serial),
            "model":    _pick("型號"),
            "name":     _pick("社區"),
            "identity": _pick("編號"),
            "version":  _pick("版本"),
            "uptime":   _pick("運行"),
            "circuit":  _pick("電路"),
            "lastCheck":_pick("檢查"),
            "images":   img_urls,
        })
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=502)


# ──────────────────────────────────────────────
# 頁面 HTML
# ──────────────────────────────────────────────
_ROUTER_MGMT_HTML = r"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>路由管理 | Shinnan ERP</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#e6edf3;font-family:"Microsoft JhengHei","Segoe UI",sans-serif;min-height:100vh}

/* ── Header ── */
.top-bar{
  display:flex;align-items:center;justify-content:space-between;
  padding:10px 24px;background:#161b22;border-bottom:1px solid #30363d;
  position:sticky;top:0;z-index:100;
}
.top-bar .title{font-size:17px;font-weight:700;color:#d4af37;letter-spacing:.04em}
.top-bar .subtitle{font-size:12px;color:#8b949e;margin-top:2px}
.header-btn{
  height:28px;padding:0 12px;border-radius:6px;border:1px solid #30363d;
  background:#21262d;color:#c9d1d9;font-size:12px;cursor:pointer;
  text-decoration:none;display:inline-flex;align-items:center;gap:6px;
}
.header-btn:hover{background:#30363d;color:#fff}
.header-btns{display:flex;gap:8px}

/* ── Main Tabs (大樓管理 / NMS狀態) ── */
.main-tabs{
  background:#161b22;border-bottom:2px solid #21262d;
  padding:0 24px;display:flex;gap:0;
}
.main-tab{
  padding:12px 20px;font-size:14px;font-weight:700;color:#8b949e;
  background:transparent;border:none;border-bottom:3px solid transparent;
  cursor:pointer;transition:.15s;letter-spacing:.03em;
  display:flex;align-items:center;gap:8px;
}
.main-tab:hover{color:#e6edf3}
.main-tab.active{color:#d4af37;border-bottom-color:#d4af37}
.main-tab .dot{
  width:8px;height:8px;border-radius:50%;background:#484f58;
}
.main-tab.active .dot{background:#d4af37;box-shadow:0 0 6px #d4af3780}

/* ── 頁面區塊 ── */
.page-section{display:none}
.page-section.active{display:block}

/* ── 區域 Tabs ── */
.tabs-wrap{
  background:#161b22;border-bottom:1px solid #21262d;
  padding:0 24px;display:flex;gap:4px;overflow-x:auto;
}
.tab-btn{
  padding:10px 16px;font-size:13px;font-weight:600;color:#8b949e;
  background:transparent;border:none;border-bottom:2px solid transparent;
  cursor:pointer;white-space:nowrap;transition:.15s;
}
.tab-btn:hover{color:#e6edf3}
.tab-btn.active{color:#d4af37;border-bottom-color:#d4af37}
.tab-count{
  display:inline-flex;align-items:center;justify-content:center;
  background:#21262d;border-radius:10px;padding:1px 7px;
  font-size:11px;margin-left:5px;
}

/* ── Toolbar ── */
.toolbar{
  padding:14px 24px;display:flex;align-items:center;gap:12px;
  background:#0d1117;border-bottom:1px solid #21262d;flex-wrap:wrap;
}
.search-box{
  flex:1;max-width:320px;height:32px;padding:0 12px;
  background:#161b22;border:1px solid #30363d;border-radius:6px;
  color:#e6edf3;font-size:13px;outline:none;
}
.search-box:focus{border-color:#d4af37}
.search-box::placeholder{color:#484f58}
.total-label{font-size:12px;color:#8b949e;margin-left:auto}
.toolbar-btn{
  height:32px;padding:0 14px;border-radius:6px;border:1px solid #30363d;
  background:#21262d;color:#c9d1d9;font-size:12px;cursor:pointer;
  display:inline-flex;align-items:center;gap:6px;
}
.toolbar-btn:hover{background:#30363d;border-color:#58a6ff;color:#58a6ff}
.toolbar-btn.active{background:#0d2136;border-color:#58a6ff;color:#58a6ff}

/* ── 大樓 Grid ── */
.grid-wrap{padding:20px 24px}
.buildings-grid{
  display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;
}
.bcard{
  background:#161b22;border:1px solid #30363d;border-radius:10px;
  padding:14px;transition:.15s;
}
.bcard:hover{border-color:#d4af3770;background:#1c2128}
.bcard .bno{font-size:11px;color:#8b949e;margin-bottom:4px}
.bcard .bname{font-size:14px;font-weight:700;color:#e6edf3;margin-bottom:8px;line-height:1.3}
.bcard .bip{
  font-size:12px;font-family:"Courier New",monospace;color:#58a6ff;
  background:#0d1117;border-radius:4px;padding:3px 7px;
  display:inline-block;margin-bottom:10px;
}
.bcard .bip.no-ip{color:#484f58;font-family:inherit}
.btn-row{display:flex;flex-wrap:wrap;gap:5px;margin-top:10px}
.conn-btn{
  display:inline-flex;align-items:center;gap:4px;height:26px;padding:0 9px;
  border-radius:5px;font-size:11px;font-weight:600;text-decoration:none;
  cursor:pointer;transition:.15s;border:1px solid;
}
.conn-btn.green{background:#1f3a2a;border-color:#2ea04326;color:#3fb950}
.conn-btn.green:hover{background:#2ea04320;border-color:#3fb950;color:#7ee787}
.conn-btn.blue{background:#0d2136;border-color:#1f6feb40;color:#58a6ff}
.conn-btn.blue:hover{background:#1f6feb20;border-color:#58a6ff;color:#79c0ff}
.conn-btn.orange{background:#2d1f0a;border-color:#e3b34126;color:#e3b341}
.conn-btn.orange:hover{background:#e3b34115;border-color:#e3b341;color:#f0c050}
.conn-btn.red{background:#2d0f0f;border-color:#f8514926;color:#f85149}
.conn-btn.red:hover{background:#f8514915;border-color:#f85149;color:#ff7b72}
.conn-btn.disabled{color:#484f58;background:#161b22;border-color:#30363d;cursor:not-allowed;pointer-events:none}
.area-badge{
  display:inline-block;font-size:10px;padding:1px 6px;border-radius:4px;
  background:#21262d;color:#8b949e;margin-left:6px;vertical-align:middle;
}

/* ── NMS 狀態區 ── */
.nms-stats{
  display:flex;gap:12px;padding:16px 24px;
  background:#0d1117;border-bottom:1px solid #21262d;flex-wrap:wrap;
}
.stat-chip{
  display:flex;align-items:center;gap:8px;
  background:#161b22;border:1px solid #30363d;border-radius:8px;
  padding:8px 14px;min-width:100px;
}
.stat-chip .s-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.s-dot.online {background:#3fb950;box-shadow:0 0 8px #3fb95080}
.s-dot.offline{background:#f85149;box-shadow:0 0 8px #f8514980}
.s-dot.warning{background:#e3b341;box-shadow:0 0 8px #e3b34180}
.stat-chip .s-num{font-size:20px;font-weight:700}
.stat-chip .s-lbl{font-size:11px;color:#8b949e}
.nms-loading{
  padding:60px 24px;text-align:center;color:#484f58;font-size:14px;
}
.spin{
  display:inline-block;width:24px;height:24px;border:2px solid #30363d;
  border-top-color:#d4af37;border-radius:50%;animation:spin .8s linear infinite;
  vertical-align:middle;margin-right:8px;
}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── NMS 裝置 Grid ── */
.nms-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(130px,1fr));
  gap:6px;padding:20px 24px;
}
.nchip{
  padding:8px 10px;border-radius:7px;cursor:pointer;
  transition:.12s;border:1px solid transparent;
  position:relative;overflow:hidden;
}
.nchip:hover{filter:brightness(1.15);transform:translateY(-1px)}
.nchip.online {background:#1a3a20;border-color:#2ea04340}
.nchip.offline{background:#2d1010;border-color:#f8514940}
.nchip.warning{background:#2d2010;border-color:#e3b34140}
.nchip .nc-name{font-size:11px;font-weight:700;line-height:1.3;color:#e6edf3}
.nchip .nc-id  {font-size:10px;color:#8b949e;margin-top:3px;font-family:"Courier New",monospace}
.nchip .nc-ddns{font-size:9px;color:#6e7681;margin-top:2px;font-family:"Courier New",monospace;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nchip .nc-dot {
  position:absolute;top:6px;right:6px;
  width:6px;height:6px;border-radius:50%;
}
.nchip.online  .nc-dot{background:#3fb950}
.nchip.offline .nc-dot{background:#f85149}
.nchip.warning .nc-dot{background:#e3b341}

/* ── NMS 詳情 Modal ── */
.modal-bg{
  display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);
  z-index:200;align-items:center;justify-content:center;padding:20px;
}
.modal-bg.open{display:flex}
.modal{
  background:#161b22;border:1px solid #30363d;border-radius:14px;
  width:min(820px,100%);max-height:90vh;overflow-y:auto;
  box-shadow:0 24px 64px rgba(0,0,0,.5);
}
.modal-head{
  display:flex;align-items:center;justify-content:space-between;
  padding:16px 20px;border-bottom:1px solid #30363d;
  position:sticky;top:0;background:#161b22;z-index:10;
}
.modal-head h2{font-size:16px;color:#d4af37;font-weight:700}
.modal-close{
  background:none;border:none;color:#8b949e;font-size:22px;
  cursor:pointer;line-height:1;padding:0 4px;
}
.modal-close:hover{color:#fff}
.modal-body{padding:20px}
.info-grid{
  display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
  gap:10px;margin-bottom:20px;
}
.info-item{background:#0d1117;border-radius:8px;padding:12px}
.info-item .i-label{font-size:11px;color:#8b949e;margin-bottom:4px}
.info-item .i-val{font-size:13px;font-weight:700;color:#e6edf3;word-break:break-all}
.i-val.green{color:#3fb950}
.i-val.mono{font-family:"Courier New",monospace;font-size:12px}
.chart-section h3{font-size:13px;color:#8b949e;margin:16px 0 8px;font-weight:600}
.chart-img{
  width:100%;border-radius:8px;border:1px solid #30363d;
  background:#0d1117;display:block;
}
.modal-loading{padding:40px;text-align:center;color:#484f58}

/* ── Empty ── */
.empty{text-align:center;padding:60px 0;color:#484f58;font-size:14px}

/* ── Responsive ── */
@media(max-width:600px){
  .buildings-grid{grid-template-columns:1fr 1fr}
  .nms-grid{grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:4px}
  .grid-wrap,.modal-body{padding:12px}
  .toolbar,.nms-stats{padding:10px 12px}
  .tabs-wrap,.main-tabs{padding:0 12px}
  .top-bar{padding:8px 12px}
}
</style>
</head>
<body>

<header class="top-bar">
  <div>
    <div class="title">路由管理</div>
    <div class="subtitle">Router Management</div>
  </div>
  <div class="header-btns">
    <a class="header-btn" href="/">返回首頁</a>
    <a class="header-btn" href="/employee/logout"
       onclick="localStorage.removeItem('xunnan_admin_token');localStorage.removeItem('xunnan_auth_token');localStorage.removeItem('xunnan_admin_role');localStorage.removeItem('xunnan_login_role')">登出</a>
  </div>
</header>

<!-- 主分頁：大樓管理 / NMS狀態 -->
<div class="main-tabs">
  <button class="main-tab active" onclick="switchMain('buildings',this)">
    <span class="dot"></span>大樓管理
  </button>
  <button class="main-tab" onclick="switchMain('nms',this)">
    <span class="dot"></span>NMS 網管狀態
  </button>
</div>

<!-- ══ 大樓管理 Section ══ -->
<div class="page-section active" id="sec-buildings">
  <nav class="tabs-wrap" id="tabs"></nav>
  <div class="toolbar">
    <input class="search-box" id="searchInput" type="text" placeholder="搜尋大樓名稱 / IP...">
    <span class="total-label" id="totalLabel"></span>
  </div>
  <div class="grid-wrap">
    <div class="buildings-grid" id="grid"></div>
  </div>
</div>

<!-- ══ NMS 狀態 Section ══ -->
<div class="page-section" id="sec-nms">
  <div class="toolbar">
    <input class="search-box" id="nmsSearch" type="text" placeholder="搜尋社區名稱 / 主機名稱...">
    <button class="toolbar-btn" id="offlineBtn" onclick="toggleOffline()">顯示離線</button>
    <button class="toolbar-btn" onclick="loadNms(true,false)">↺ 快取更新</button>
    <button class="toolbar-btn" onclick="loadNms(true,true)" title="直接連 NMS 取得最新狀態">🌐 即時更新</button>
    <span class="total-label" id="nmsTotalLabel"></span>
  </div>
  <div class="nms-stats" id="nmsStats" style="display:none">
    <div class="stat-chip"><span class="s-dot online"></span><div><div class="s-num" id="cntOnline">-</div><div class="s-lbl">在線</div></div></div>
    <div class="stat-chip"><span class="s-dot offline"></span><div><div class="s-num" id="cntOffline">-</div><div class="s-lbl">離線</div></div></div>
    <div class="stat-chip"><span class="s-dot warning"></span><div><div class="s-num" id="cntWarning">-</div><div class="s-lbl">警告</div></div></div>
  </div>
  <div id="nmsContent">
    <div class="nms-loading" id="nmsLoading" style="display:none">
      <span class="spin"></span>正在連線 NMS...
    </div>
    <div class="nms-grid" id="nmsGrid"></div>
  </div>
</div>

<!-- ══ NMS 詳情 Modal ══ -->
<div class="modal-bg" id="modalBg" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <div class="modal-head">
      <h2 id="modalTitle">裝置詳情</h2>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body" id="modalBody">
      <div class="modal-loading"><span class="spin"></span>載入中...</div>
    </div>
  </div>
</div>

<script>
// ─── 大樓管理 ───────────────────────────────
const AREAS_ORDER = ['東區','北區','安平','永康','高雄','北台南',''];
const AREA_LABEL  = {'':'未分區'};

let allData    = [];
let currentArea = '__ALL__';
let searchVal   = '';

async function loadBuildings(){
  const res = await fetch('/api/router-mgmt/buildings');
  allData = await res.json();
  buildTabs();
  render();
}

function buildTabs(){
  const counts = {'__ALL__': allData.length};
  for(const b of allData){ const a=b.area??''; counts[a]=(counts[a]||0)+1; }
  const areas = [...AREAS_ORDER.filter(a=>counts[a]>0)];
  for(const a of Object.keys(counts)) if(!areas.includes(a)&&a!=='__ALL__') areas.push(a);
  const tabs = document.getElementById('tabs');
  tabs.innerHTML = tabHTML('__ALL__','全部',counts['__ALL__']);
  for(const a of areas){ if(a!=='__ALL__') tabs.innerHTML += tabHTML(a,AREA_LABEL[a]||a,counts[a]||0); }
  tabs.querySelectorAll('.tab-btn').forEach(btn=>{
    btn.addEventListener('click',()=>{
      currentArea=btn.dataset.area;
      tabs.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      render();
    });
  });
  tabs.querySelector('[data-area="__ALL__"]').classList.add('active');
}

function tabHTML(area,label,count){
  return `<button class="tab-btn" data-area="${area}">${label}<span class="tab-count">${count}</span></button>`;
}

function render(){
  const q = searchVal.trim().toLowerCase();
  let list = allData;
  if(currentArea!=='__ALL__') list = list.filter(b=>(b.area??'')===currentArea);
  if(q) list = list.filter(b=>b.name.toLowerCase().includes(q)||b.ip.toLowerCase().includes(q)||b.building_no.toLowerCase().includes(q));
  document.getElementById('totalLabel').textContent=`共 ${list.length} 棟`;
  const grid = document.getElementById('grid');
  if(!list.length){ grid.innerHTML='<div class="empty" style="grid-column:1/-1">無符合資料</div>'; return; }
  grid.innerHTML = list.map(b=>{
    const ip=b.ip||'', base=ip?`http://${ip}`:'';
    const areaBadge=(currentArea==='__ALL__'&&b.area)?`<span class="area-badge">${b.area}</span>`:'';
    const btn=(label,hash,cls)=>base
      ?`<a class="conn-btn ${cls}" href="${base}/webfig/#${hash}" onclick="(function(url){var hash=url.split('#')[1]||'';var base=url.split('/webfig/')[0];var w=window.open(base+'/','_blank');w.name='autologin=admin|pear';var t=setInterval(function(){try{if(w.document&&w.document.getElementById('password')){w.document.getElementById('password').value='pear';if(w.dologin){w.dologin();}clearInterval(t);setTimeout(function(){try{w.location.replace(base+'/webfig/#'+hash);}catch(e){}},2000);}}catch(e){}},300);})(this.href);return false;">${label}</a>`
      :`<span class="conn-btn disabled">${label}</span>`;
    return `<div class="bcard">
<div class="bno">${b.building_no}${areaBadge}</div>
<div class="bname">${b.name}</div>
${ip?`<div class="bip">${ip}</div>`:'<div class="bip no-ip">無 IP</div>'}
<div class="btn-row">
  ${btn('🖥️ 主頁','','green')}
  ${btn('🔗 IP綁定','ip-binding','blue')}
  ${btn('📋 LOG','log','orange')}
  ${btn('🔒 封鎖','ip-firewall/address-lists','red')}
</div>
<div class="btn-row">${btn('📡 DHCP','dhcp-server/leases','blue')}</div>
</div>`;
  }).join('');
}

document.getElementById('searchInput').addEventListener('input',e=>{ searchVal=e.target.value; render(); });

// ─── NMS 狀態 ───────────────────────────────
let nmsData     = [];
let nmsLoaded   = false;
let nmsOffline  = false;
let nmsSearchQ  = '';

function switchMain(section, btn){
  document.querySelectorAll('.main-tab').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.page-section').forEach(s=>s.classList.remove('active'));
  document.getElementById('sec-'+section).classList.add('active');
  if(section==='nms' && !nmsLoaded) loadNms(false);
}

async function loadNms(force=false, live=false){
  if(!force && nmsLoaded) return;
  document.getElementById('nmsLoading').style.display='block';
  document.getElementById('nmsGrid').innerHTML='';
  document.getElementById('nmsStats').style.display='none';
  try{
    const url=`/api/router-mgmt/nms-devices?offline=${nmsOffline}&live=${live}`;
    const r = await fetch(url);
    const j = await r.json();
    if(!j.ok){ throw new Error(j.error||'NMS 連線失敗'); }
    nmsData   = j.devices;
    nmsLoaded = true;
    renderNms();
  }catch(e){
    document.getElementById('nmsGrid').innerHTML=`<div class="empty" style="grid-column:1/-1;color:#f85149">⚠ ${e.message}</div>`;
  }finally{
    document.getElementById('nmsLoading').style.display='none';
  }
}

function renderNms(){
  const q = nmsSearchQ.trim().toLowerCase();
  let list = nmsData;
  if(q) list=list.filter(d=>d.name.toLowerCase().includes(q)||d.identity.toLowerCase().includes(q)||d.community.toLowerCase().includes(q)||(d.ddns||'').toLowerCase().includes(q));

  const online  = nmsData.filter(d=>d.status==='online').length;
  const offline = nmsData.filter(d=>d.status==='offline').length;
  const warning = nmsData.filter(d=>d.status==='warning').length;
  document.getElementById('cntOnline').textContent  = online;
  document.getElementById('cntOffline').textContent = offline;
  document.getElementById('cntWarning').textContent = warning;
  document.getElementById('nmsStats').style.display ='flex';
  document.getElementById('nmsTotalLabel').textContent=`共 ${list.length} 台`;

  const grid=document.getElementById('nmsGrid');
  if(!list.length){ grid.innerHTML='<div class="empty" style="grid-column:1/-1">無符合裝置</div>'; return; }
  grid.innerHTML=list.map(d=>`
<div class="nchip ${d.status}" onclick="openDeviceModal('${d.did}','${esc(d.name)}','${d.status}')">
  <div class="nc-dot"></div>
  <div class="nc-name">${esc(d.name)}</div>
  <div class="nc-id">${esc(d.identity||d.model||'')}</div>
  <div class="nc-ddns" title="${esc(d.ddns||'')}">${esc(d.ddns||'-')}</div>
</div>`).join('');
}

document.getElementById('nmsSearch').addEventListener('input',e=>{ nmsSearchQ=e.target.value; if(nmsLoaded)renderNms(); });

function toggleOffline(){
  nmsOffline=!nmsOffline;
  nmsLoaded=false;
  const btn=document.getElementById('offlineBtn');
  btn.textContent=nmsOffline?'顯示在線':'顯示離線';
  btn.classList.toggle('active',nmsOffline);
  loadNms(true);
}

// ─── Modal 詳情 ─────────────────────────────
async function openDeviceModal(did, name, status){
  document.getElementById('modalTitle').textContent=name;
  document.getElementById('modalBody').innerHTML='<div class="modal-loading"><span class="spin"></span>載入中...</div>';
  document.getElementById('modalBg').classList.add('open');
  try{
    const r=await fetch(`/api/router-mgmt/nms-device/${did}`);
    const d=await r.json();
    if(!d.ok) throw new Error(d.error||'無法取得詳情');

    const statusColor = status==='online'?'green':(status==='offline'?'red':'orange');
    const statusText  = status==='online'?'在線':(status==='offline'?'離線':'警告');

    // 圖表分組：日/週/月 各兩張（負載+流量）
    const imgs = d.images||[];
    const chartLabels=['日負載','日流量','週負載','週流量','月負載','月流量'];
    const chartsHTML = imgs.slice(0,6).map((url,i)=>`
<div>
  <h3>${chartLabels[i]||'圖表'}</h3>
  <img class="chart-img" src="${url}" alt="${chartLabels[i]||''}" loading="lazy">
</div>`).join('');

    document.getElementById('modalBody').innerHTML=`
<div class="info-grid">
  <div class="info-item"><div class="i-label">社區名稱</div><div class="i-val">${d.name||name}</div></div>
  <div class="info-item"><div class="i-label">狀態</div><div class="i-val ${statusColor}">${statusText}</div></div>
  <div class="info-item"><div class="i-label">型號</div><div class="i-val">${d.model||'-'}</div></div>
  <div class="info-item"><div class="i-label">版本</div><div class="i-val mono">${d.version||'-'}</div></div>
  <div class="info-item"><div class="i-label">編號</div><div class="i-val mono">${d.identity||'-'}</div></div>
  <div class="info-item"><div class="i-label">序號</div><div class="i-val mono">${d.serial||'-'}</div></div>
  <div class="info-item"><div class="i-label">DDNS</div><div class="i-val mono">${d.ddns||'-'}</div></div>
  <div class="info-item"><div class="i-label">運行時間</div><div class="i-val">${d.uptime||'-'}</div></div>
  <div class="info-item"><div class="i-label">電路</div><div class="i-val">${d.circuit||'-'}</div></div>
  <div class="info-item"><div class="i-label">最後檢查</div><div class="i-val">${d.lastCheck||'-'}</div></div>
</div>
${chartsHTML?`<div class="chart-section">${chartsHTML}</div>`:''}`;
  }catch(e){
    document.getElementById('modalBody').innerHTML=`<div style="color:#f85149;padding:20px">⚠ ${e.message}</div>`;
  }
}

function closeModal(){
  document.getElementById('modalBg').classList.remove('open');
}

document.addEventListener('keydown',e=>{ if(e.key==='Escape') closeModal(); });

function esc(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

// ─── 啟動 ───────────────────────────────────
loadBuildings();
</script>
<script src='/static/xn_theme.js?v=1'></script>
</body>
</html>"""


# ──────────────────────────────────────────────
# 路由
# ──────────────────────────────────────────────
@router.get("/router-mgmt", response_class=HTMLResponse)
def router_mgmt_page(request: Request):
    _user = _employee_current_user_from_request(request)
    if not _user:
        return RedirectResponse(f"/employee/login?next=/router-mgmt", status_code=303)
    return HTMLResponse(_ROUTER_MGMT_HTML)


@router.get("/api/router-mgmt/ping")
def api_ping(ip: str, no: str, request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    # 取出純 IP（去掉 port）
    ip_only = ip.split(':')[0]
    try:
        if platform.system() == "Windows":
            cmd = ["ping", "-n", "1", "-w", "2000", ip_only]
        else:
            cmd = ["ping", "-c", "1", "-W", "2", ip_only]
        result = subprocess.run(cmd, capture_output=True, timeout=5)
        alive = result.returncode == 0
    except Exception:
        alive = False
    return JSONResponse({"building_no": no, "ip": ip, "alive": alive})
