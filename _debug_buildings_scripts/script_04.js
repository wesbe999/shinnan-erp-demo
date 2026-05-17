
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  function applyBuildingMobileLabels() {
    const tables = Array.from(document.querySelectorAll("table"));
    if (!tables.length) return;

    tables.forEach(function (table) {
      const headers = Array.from(table.querySelectorAll("thead th")).map(function (th) {
        return (th.textContent || "").trim();
      });

      if (!headers.length) {
        // 若沒有表頭，就用目前大樓名錄預設欄位
        headers.push("編號", "大樓名稱", "區域", "地址", "管理公司", "用戶數量", "住戶總數", "IP", "主機", "選擇");
      }

      table.querySelectorAll("tbody tr").forEach(function (tr) {
        Array.from(tr.children).forEach(function (td, index) {
          if (!td.getAttribute("data-label")) {
            td.setAttribute("data-label", headers[index] || "");
          }
        });
      });
    });
  }

  function fixButtonVerticalCenter() {
    document.querySelectorAll("button, .btn, .button, [role='button']").forEach(function (btn) {
      btn.style.display = "inline-flex";
      btn.style.alignItems = "center";
      btn.style.justifyContent = "center";
      btn.style.lineHeight = "1";
    });
  }

  function applyAll() {
    applyBuildingMobileLabels();
    fixButtonVerticalCenter();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyAll);
  } else {
    applyAll();
  }

  setTimeout(applyAll, 300);
  setTimeout(applyAll, 900);

  const observer = new MutationObserver(function () {
    setTimeout(applyAll, 0);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
})();
