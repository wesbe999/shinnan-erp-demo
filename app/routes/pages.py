from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.routes.employee_auth import _employee_current_user_from_request

router = APIRouter(tags=["pages"])


# SHINNAN_ADMIN_PAGE_MOVED_TO_ADMIN_DISPATCH_START
# /admin route moved to app/routes/admin_dispatch.py
# SHINNAN_ADMIN_PAGE_MOVED_TO_ADMIN_DISPATCH_END


# SHINNAN_BILLING_ROUTE_BRIDGE_START_REMOVED_CLEANUP_STEP1_20260502
# This obsolete route block was removed during pages.py cleanup step 1.
# SHINNAN_BILLING_ROUTE_BRIDGE_END_REMOVED_CLEANUP_STEP1_20260502


@router.get("/admin/import", response_class=HTMLResponse)
def admin_import_page(request: Request):
    _user = _employee_current_user_from_request(request)
    if not _user:
        return RedirectResponse("/employee/login?next=/admin/import", status_code=303)
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <title>資料匯入｜訊南 ERP 系統</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <link rel="stylesheet" href="/static/admin_import.css?v=20260508">

</head>

<body>
  <div class="hero">
    <div class="hero-title">資料匯入</div>
    <div class="hero-subtitle">Excel / CSV / JSON / DB 匯入，先預覽檢查，再寫入訊南 ERP 系統。</div>
  </div>

  <main class="page">
    <div class="toolbar">
      <button type="button" class="home-button" onclick="goBackFromBuildings()">返回上一頁</button>
      <span class="hint">請先選擇匯入格式與資料類型，上傳後先預覽，不會立即寫入資料庫。</span>
    </div>

    <section class="import-grid">
      <div class="import-card">
        <div class="format-badge excel">Excel .xlsx</div>
        <div class="import-card-title">Excel 匯入</div>
        <div class="import-card-desc">
          適合公司日常使用。可匯入客戶、大樓、帳務、派工、人事資料。
        </div>
        <button type="button" class="import-button btn-excel" onclick="selectImportFormat('excel')">選擇 Excel 匯入</button>
      </div>

      <div class="import-card">
        <div class="format-badge csv">CSV .csv</div>
        <div class="import-card-title">CSV 匯入</div>
        <div class="import-card-desc">
          適合大量資料或舊系統匯出。建議使用 UTF-8 with BOM 避免中文亂碼。
        </div>
        <button type="button" class="import-button btn-csv" onclick="selectImportFormat('csv')">選擇 CSV 匯入</button>
      </div>

      <div class="import-card">
        <div class="format-badge json">JSON .json</div>
        <div class="import-card-title">JSON 匯入</div>
        <div class="import-card-desc">
          適合系統串接、API 資料交換、手機端或外部程式自動匯入。
        </div>
        <button type="button" class="import-button btn-json" onclick="selectImportFormat('json')">選擇 JSON 匯入</button>
      </div>

      <div class="import-card">
        <div class="format-badge db">DB / SQL</div>
        <div class="import-card-title">資料庫匯入</div>
        <div class="import-card-desc">
          適合舊電腦或舊系統使用 SQL / SQLite 資料庫時搬移資料。
        </div>
        <button type="button" class="import-button btn-db" onclick="selectImportFormat('db')">選擇 DB 匯入</button>
      </div>
    </section>

    <section class="panel">
      <div class="panel-title">匯入設定</div>

      <div class="form-grid">
        <div>
          <label>匯入資料類型</label>
          <select id="import_type">
            <option value="customers">客戶資料</option>
            <option value="buildings">大樓資料</option>
            <option value="billing">會計資料</option>
            <option value="tickets">派工案件</option>
            <option value="staff">人事資料</option>
            <option value="database">舊系統資料庫</option>
          </select>
        </div>

        <div>
          <label>選擇檔案</label>
          <input id="import_file" type="file" accept=".xlsx,.csv,.json,.db,.sqlite,.sqlite3,.sql">
        </div>

        <div>
          <label>目前格式</label>
          <button type="button" class="preview-button" id="preview_button" onclick="previewImport()">預覽資料</button>
        </div>
      </div>

      <div class="notice-box" id="import_notice">
        目前選擇：Excel 匯入。此頁先建立匯入入口與預覽流程，後續再接正式解析與資料庫寫入。
      </div>

      <div class="warning-box">
        DB / SQL 匯入建議只提供給系統管理者使用。舊系統資料庫通常需要先分析資料表結構，再對應到訊南 ERP 的客戶、大樓、帳務、派工與人事欄位。
      </div>

      <div class="preview-area" id="preview_area">
        <div class="preview-header">預覽結果</div>
        <div class="preview-content" id="preview_content">
          尚未選擇檔案。
        </div>
      </div>
    </section>
  </main>

  <script src="/static/admin_import.js?v=20260508"></script>


  <script src="/static/app_header_actions.js?v=cl17p6"></script>
</body>
</html>
    """)


# SHINNAN_THEME_PAGE_START
@router.get("/theme", response_class=HTMLResponse)
def theme_page(request: Request):
    return HTMLResponse("""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>主題設定｜訊南 ERP</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:"Microsoft JhengHei","Noto Sans TC",Arial,sans-serif;background:#0a1a10;color:#f0ead6;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:40px 20px 60px;}
h1{font-size:28px;font-weight:1000;letter-spacing:4px;color:#d4af37;margin-bottom:6px;text-align:center;}
.sub{font-size:13px;color:#8aab8f;margin-bottom:30px;text-align:center;letter-spacing:1px;}
.theme-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px;width:100%;max-width:920px;margin-bottom:36px;}
.theme-card{position:relative;border-radius:18px;cursor:pointer;border:2px solid rgba(255,255,255,.08);transition:.2s;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.4);}
.theme-card:hover{transform:translateY(-4px);box-shadow:0 16px 40px rgba(0,0,0,.5);}
.theme-card.active{border-color:#d4af37;box-shadow:0 0 0 3px rgba(212,175,55,.35),0 16px 40px rgba(0,0,0,.5);}
.theme-preview{height:110px;position:relative;}
.theme-preview-bar{height:26px;display:flex;align-items:center;padding:0 12px;gap:6px;background:rgba(0,0,0,.25);}
.theme-preview-dot{width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,.3);}
.theme-preview-ttl{font-size:11px;font-weight:1000;opacity:.9;letter-spacing:2px;}
.theme-preview-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px;padding:7px 10px;}
.theme-preview-card{border-radius:7px;height:28px;}
.theme-info{padding:12px 14px;background:rgba(0,0,0,.25);}
.theme-name{font-size:14px;font-weight:1000;color:#f0ead6;margin-bottom:3px;}
.theme-desc{font-size:11px;color:#8aab8f;}
.apply-btn{width:100%;padding:9px;border:none;font-size:12px;font-weight:1000;cursor:pointer;transition:.15s;letter-spacing:1px;}
.current-badge{background:rgba(212,175,55,.15);border:1px solid rgba(212,175,55,.3);color:#d4af37;padding:5px 16px;border-radius:999px;font-size:12px;font-weight:1000;margin-bottom:28px;letter-spacing:1px;}
.back-btn{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.08);border:1px solid rgba(212,175,55,.3);color:#d4af37;padding:10px 24px;border-radius:12px;font-size:14px;font-weight:1000;cursor:pointer;text-decoration:none;transition:.15s;letter-spacing:1px;}
.back-btn:hover{background:rgba(212,175,55,.15);}
</style>
</head>
<body>
<h1>🎨 主題設定</h1>
<div class="sub">選擇訊南 ERP 系統的視覺主題，套用後即時生效</div>
<div class="current-badge" id="current-label">載入中...</div>
<div class="theme-grid" id="theme-grid"></div>
<a href="/" class="back-btn">← 返回首頁</a>
<script>
const THEMES=[
  {id:"default",name:"深綠（預設）",desc:"訊南品牌色，沉穩專業",hf:"#0f3320",ht:"#1a5c38",ac:"#d4af37",c1:"#1e5c31",c2:"rgba(212,175,55,.25)",bb:"#1a5c38",bc:"#d4af37"},
  {id:"navy",name:"深藍商務",desc:"科技感，數據導向工作首選",hf:"#0d1f3c",ht:"#1a3a6b",ac:"#60a5fa",c1:"#1e3a7a",c2:"rgba(96,165,250,.25)",bb:"#1a3a6b",bc:"#60a5fa"},
  {id:"purple",name:"深紫典雅",desc:"優雅神秘，彰顯品味",hf:"#1a0a2e",ht:"#3b1a6b",ac:"#c084fc",c1:"#3b1a7a",c2:"rgba(192,132,252,.25)",bb:"#3b1a6b",bc:"#c084fc"},
  {id:"crimson",name:"深紅熱情",desc:"熱情積極，強調行動力",hf:"#2a0a0a",ht:"#6b1a1a",ac:"#f87171",c1:"#7a1a1a",c2:"rgba(248,113,113,.25)",bb:"#6b1a1a",bc:"#f87171"},
  {id:"slate",name:"深灰簡約",desc:"極簡現代，聚焦內容",hf:"#0f172a",ht:"#1e293b",ac:"#94a3b8",c1:"#1e293b",c2:"rgba(148,163,184,.25)",bb:"#1e293b",bc:"#94a3b8"},
  {id:"amber",name:"深褐金曜",desc:"大地色系，溫暖可靠",hf:"#1c1004",ht:"#4a2c0a",ac:"#fbbf24",c1:"#4a2c0a",c2:"rgba(251,191,36,.25)",bb:"#4a2c0a",bc:"#fbbf24"},
];
let cur=localStorage.getItem("xn_theme")||"default";
function render(){
  const g=document.getElementById("theme-grid");
  g.innerHTML=THEMES.map(t=>`
    <div class="theme-card ${t.id===cur?"active":""}" onclick="apply('${t.id}')">
      <div class="theme-preview" style="background:linear-gradient(135deg,${t.hf},${t.ht})">
        <div class="theme-preview-bar"><div class="theme-preview-dot"></div><div class="theme-preview-dot"></div><div class="theme-preview-ttl" style="color:${t.ac}">ShinNan ERP</div></div>
        <div class="theme-preview-grid">
          <div class="theme-preview-card" style="background:${t.c1}"></div>
          <div class="theme-preview-card" style="background:${t.c2};border:1px solid ${t.ac}44"></div>
          <div class="theme-preview-card" style="background:${t.c1};opacity:.6"></div>
          <div class="theme-preview-card" style="background:${t.c1};opacity:.3"></div>
        </div>
      </div>
      <div class="theme-info"><div class="theme-name">${t.name}</div><div class="theme-desc">${t.desc}</div></div>
      <button class="apply-btn" style="background:${t.bb};color:${t.bc}">${t.id===cur?"✓ 目前使用":"套用主題"}</button>
    </div>`).join("");
  const c=THEMES.find(t=>t.id===cur);
  document.getElementById("current-label").textContent="目前使用：" + (c?c.name:"深綠（預設）");
}
function apply(id){
  cur=id;
  localStorage.setItem("xn_theme",id);
  const t=THEMES.find(t=>t.id===id);
  if(t) localStorage.setItem("xn_theme_data",JSON.stringify(t));
  render();
}
render();
</script>
</body></html>""")
# SHINNAN_THEME_PAGE_END
