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
