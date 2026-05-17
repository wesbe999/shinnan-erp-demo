
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  const params = new URLSearchParams(location.search);
  const isPicker = params.get("pick") === "sales_new";

  if (isPicker) {
    document.body.classList.add("sales-building-picker");
    document.title = "選擇大樓｜訊南 ERP";
  }

  function pickUrl(buildingNo, buildingName) {
    return "/app/sales/new?building_no=" +
      encodeURIComponent(buildingNo || "") +
      "&building_name=" +
      encodeURIComponent(buildingName || "") +
      "&ts=" + Date.now();
  }

  function applySalesNewPicker() {
    if (!isPicker) return;

    document.querySelectorAll("table tbody tr").forEach(function (tr) {
      const cells = Array.from(tr.children);

      if (cells.length < 2) return;

      const buildingNo = (cells[0].textContent || "").trim();
      const buildingName = (cells[1].textContent || "").trim();

      const last = cells[cells.length - 1];
      if (!last) return;

      last.innerHTML = "";

      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = "選擇此大樓";
      btn.onclick = function () {
        location.href = pickUrl(buildingNo, buildingName);
      };

      last.appendChild(btn);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applySalesNewPicker);
  } else {
    applySalesNewPicker();
  }

  setTimeout(applySalesNewPicker, 300);
  setTimeout(applySalesNewPicker, 900);

  const observer = new MutationObserver(function () {
    setTimeout(applySalesNewPicker, 0);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
})();

