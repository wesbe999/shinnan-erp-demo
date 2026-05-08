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

  <style>
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
      background: #eef3fa;
      color: #102348;
    }

    .hero {
      background: linear-gradient(135deg, #2f7f74, #315eea, #7c3aed);
      color: #ffffff;
      padding: 30px 34px;
      border-radius: 0 0 28px 28px;
      box-shadow: 0 16px 38px rgba(15, 23, 42, 0.18);
    }

    .hero-title {
      font-size: 42px;
      font-weight: 1000;
      letter-spacing: 2px;
      margin-bottom: 10px;
    }

    .hero-subtitle {
      font-size: 20px;
      font-weight: 800;
      opacity: 0.92;
    }

    .page {
      width: min(1480px, calc(100vw - 40px));
      margin: 0 auto;
      padding: 24px 0 40px;
    }

    .toolbar {
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 22px 0;
    }

    .home-button {
      height: 40px;
      border: 0;
      border-radius: 12px;
      background: #4f7ee8;
      color: #ffffff;
      font-size: 16px;
      font-weight: 1000;
      padding: 0 18px;
      cursor: pointer;
      box-shadow: 0 6px 14px rgba(15, 23, 42, 0.12);
    }

    .hint {
      color: #64748b;
      font-size: 15px;
      font-weight: 800;
    }

    .import-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }

    .import-card {
      background: #ffffff;
      border: 1px solid #d7e1ef;
      border-radius: 22px;
      padding: 20px;
      box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
    }

    .import-card-title {
      font-size: 24px;
      font-weight: 1000;
      margin-bottom: 8px;
      color: #102348;
    }

    .import-card-desc {
      color: #64748b;
      font-size: 15px;
      font-weight: 800;
      line-height: 1.55;
      min-height: 94px;
    }

    .format-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      height: 30px;
      padding: 0 12px;
      border-radius: 999px;
      font-size: 14px;
      font-weight: 1000;
      margin-bottom: 14px;
    }

    .excel {
      background: #dcfce7;
      color: #166534;
    }

    .csv {
      background: #e0f2fe;
      color: #075985;
    }

    .json {
      background: #f3e8ff;
      color: #6b21a8;
    }

    .db {
      background: #ffedd5;
      color: #9a3412;
    }

    .import-button {
      width: 100%;
      height: 42px;
      border: 0;
      border-radius: 14px;
      color: #ffffff;
      font-size: 16px;
      font-weight: 1000;
      cursor: pointer;
      margin-top: 14px;
    }

    .btn-excel {
      background: #16a34a;
    }

    .btn-csv {
      background: #0284c7;
    }

    .btn-json {
      background: #7c3aed;
    }

    .btn-db {
      background: #ea580c;
    }

    .panel {
      background: #ffffff;
      border: 1px solid #d7e1ef;
      border-radius: 22px;
      padding: 22px;
      box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
    }

    .panel-title {
      font-size: 26px;
      font-weight: 1000;
      margin-bottom: 16px;
    }

    .form-grid {
      display: grid;
      grid-template-columns: 220px 1fr 180px;
      gap: 14px;
      align-items: end;
    }

    label {
      display: block;
      color: #64748b;
      font-size: 14px;
      font-weight: 1000;
      margin-bottom: 6px;
    }

    select,
    input[type="file"] {
      width: 100%;
      height: 42px;
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      background: #ffffff;
      color: #102348;
      padding: 0 12px;
      font-size: 15px;
      font-weight: 900;
      font-family: inherit;
    }

    .preview-button {
      width: 100%;
      height: 42px;
      border: 0;
      border-radius: 12px;
      background: #f97316;
      color: white;
      font-size: 16px;
      font-weight: 1000;
      cursor: pointer;
    }

    .notice-box {
      margin-top: 18px;
      padding: 14px 16px;
      border: 1px dashed #94a3b8;
      border-radius: 16px;
      background: #f8fbff;
      color: #475569;
      font-size: 15px;
      font-weight: 800;
      line-height: 1.6;
    }

    .preview-area {
      margin-top: 18px;
      border: 1px solid #d7e1ef;
      border-radius: 16px;
      overflow: hidden;
      display: none;
    }

    .preview-header {
      background: #f1f5f9;
      padding: 12px 14px;
      font-size: 16px;
      font-weight: 1000;
    }

    .preview-content {
      padding: 14px;
      color: #64748b;
      font-weight: 800;
      line-height: 1.6;
    }

    .warning-box {
      margin-top: 14px;
      padding: 12px 14px;
      border-radius: 14px;
      background: #fff7ed;
      border: 1px solid #fdba74;
      color: #9a3412;
      font-size: 14px;
      font-weight: 900;
      line-height: 1.5;
    }

    @media (max-width: 1180px) {
      .import-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 760px) {
      .import-grid {
        grid-template-columns: 1fr;
      }

      .form-grid {
        grid-template-columns: 1fr;
      }

      .hero-title {
        font-size: 34px;
      }
    }
  </style>
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

  <script>
    let currentImportFormat = "excel";

    function selectImportFormat(format) {
      currentImportFormat = format;

      const fileInput = document.getElementById("import_file");
      const notice = document.getElementById("import_notice");

      if (format === "excel") {
        fileInput.accept = ".xlsx";
        notice.textContent = "目前選擇：Excel 匯入。適合公司日常人工整理資料。";
      }

      if (format === "csv") {
        fileInput.accept = ".csv";
        notice.textContent = "目前選擇：CSV 匯入。適合大量資料與舊系統匯出，建議使用 UTF-8 with BOM。";
      }

      if (format === "json") {
        fileInput.accept = ".json";
        notice.textContent = "目前選擇：JSON 匯入。適合 API、外部系統或程式資料交換。";
      }

      if (format === "db") {
        fileInput.accept = ".db,.sqlite,.sqlite3,.sql";
        notice.textContent = "目前選擇：DB / SQL 匯入。適合舊系統資料庫搬移，需先分析資料表結構再匯入。";
      }
    }

    function previewImport() {
      const fileInput = document.getElementById("import_file");
      const type = document.getElementById("import_type").value;
      const previewArea = document.getElementById("preview_area");
      const previewContent = document.getElementById("preview_content");

      previewArea.style.display = "block";

      if (!fileInput.files || !fileInput.files.length) {
        previewContent.textContent = "尚未選擇檔案。";
        return;
      }

      const file = fileInput.files[0];

      previewContent.innerHTML = `
        <div>匯入格式：${currentImportFormat.toUpperCase()}</div>
        <div>資料類型：${type}</div>
        <div>檔案名稱：${file.name}</div>
        <div>檔案大小：${Math.round(file.size / 1024)} KB</div>
        <div style="margin-top:8px;">下一步可接後端解析 API，先檢查欄位，再確認寫入資料庫。</div>
      `;
    }
  </script>
</body>
</html>
    """)
