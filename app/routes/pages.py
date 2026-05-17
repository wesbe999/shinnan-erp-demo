from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pages"])


# SHINNAN_ADMIN_PAGE_MOVED_TO_ADMIN_DISPATCH_START
# /admin route moved to app/routes/admin_dispatch.py
# SHINNAN_ADMIN_PAGE_MOVED_TO_ADMIN_DISPATCH_END


# SHINNAN_BILLING_ROUTE_BRIDGE_START_REMOVED_CLEANUP_STEP1_20260502
# This obsolete route block was removed during pages.py cleanup step 1.
# SHINNAN_BILLING_ROUTE_BRIDGE_END_REMOVED_CLEANUP_STEP1_20260502


@router.get("/admin/import", response_class=HTMLResponse)
def admin_import_page(request: Request):
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


  <script src="/static/app_header_actions.js?v=cl17p3"></script>
</body>
</html>
    """)
