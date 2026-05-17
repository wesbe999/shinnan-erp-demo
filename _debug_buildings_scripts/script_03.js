
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  const BUSINESS_STORAGE_KEY = "shinnan_building_business_records_v1";

  function safeText(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function readJson(key, fallback) {
    try {
      return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback));
    } catch (err) {
      return fallback;
    }
  }

  function normalizeName(value) {
    return String(value || "").trim();
  }

  function findBusinessRecordForBuilding(building) {
    const records = readJson(BUSINESS_STORAGE_KEY, []);
    const buildingName = normalizeName(building.name || building.building_name);

    if (!Array.isArray(records) || !buildingName) return null;

    return records.find(function (item) {
      return normalizeName(item.building_name) === buildingName;
    }) || null;
  }

  function card(label, value, extraClass) {
    return `
      <div class="building-detail-card ${extraClass || ""}">
        <div class="building-detail-label">${safeText(label)}</div>
        <div class="building-detail-value">${safeText(value || "-")}</div>
      </div>
    `;
  }

  function section(title) {
    return `<div class="building-detail-section">${safeText(title)}</div>`;
  }

  window.closeBuildingDetailModal = function () {
    const mask = document.getElementById("building_detail_mask");
    if (mask) mask.classList.remove("active");
  };

  window.openBuildingDetailModal = function (building) {
    building = building || {};

    const record = findBusinessRecordForBuilding(building) || {};
    const title = document.getElementById("building_detail_title");
    const sub = document.getElementById("building_detail_sub");
    const body = document.getElementById("building_detail_body");
    const mask = document.getElementById("building_detail_mask");

    if (!body || !mask) return;

    const buildingName = building.name || building.building_name || record.building_name || "未命名大樓";

    if (title) title.textContent = buildingName;
    if (sub) {
      sub.textContent =
        "區域：" + (building.area || record.area || "-") +
        "｜地址：" + (building.raw_address || building.address || "-");
    }

    body.innerHTML = [
      section("大樓基本資料"),
      card("編號", building.building_no || building.no || ""),
      card("區域", building.area || record.area || ""),
      card("地址", building.raw_address || building.address || ""),
      card("管理公司", building.management_company || record.management_company || ""),
      card("用戶數量", building.active_users ?? building.user_count ?? ""),
      card("住戶總數", building.total_households ?? building.households ?? ""),
      card("IP", building.ip || ""),
      card("主機", building.host || building.main_host || ""),

      section("管理室／總幹事"),
      card("管理室電話", record.management_phone || ""),
      card("總幹事姓名", record.manager_name || ""),
      card("總幹事電話", record.manager_phone || ""),
      card("總幹事年齡", record.manager_age ? record.manager_age + " 歲" : ""),
      card("總幹事資歷", record.manager_experience || ""),
      card("總幹事興趣", record.manager_interest || ""),
      card("可拜訪時段", record.visit_time || ""),
      card("管理室資訊／注意事項", record.management_note || "", "full"),

      section("會議／合約"),
      card("委員會時間", record.committee_time || ""),
      card("住戶大會時間", record.resident_meeting_time || ""),
      card("合約狀態", record.contract_status || ""),
      card("合約到期日", record.contract_end_date || ""),

      section("業務資訊"),
      card("業務類型", record.business_type || ""),
      card("目前狀態", record.status || ""),
      card("負責業務", record.owner || ""),
      card("下次拜訪", record.next_visit || ""),
      card("業務事件", record.event_type && record.event_type !== "無" ? record.event_type + "｜" + (record.event_status || "") : ""),
      card("事件安排日期", record.event_schedule_date || ""),
      card("回饋項目", record.feedback_type && record.feedback_type !== "無" ? record.feedback_type + "｜" + (record.feedback_status || "") : ""),
      card("業務紀錄／拜訪結果", record.business_note || "", "full")
    ].join("");

    mask.classList.add("active");
  };

  function bindExistingBuildingNameCells() {
    const rows = Array.from(document.querySelectorAll("tbody tr"));

    rows.forEach(function (row) {
      const cells = row.querySelectorAll("td");
      if (cells.length < 2) return;

      const nameCell = cells[1];
      if (nameCell.querySelector(".building-name-link")) return;

      const name = nameCell.textContent.trim();
      if (!name) return;

      const building = {
        building_no: cells[0] ? cells[0].textContent.trim() : "",
        name: name,
        area: cells[2] ? cells[2].textContent.trim() : "",
        address: cells[3] ? cells[3].textContent.trim() : "",
        raw_address: cells[3] ? cells[3].textContent.trim() : "",
        management_company: cells[4] ? cells[4].textContent.trim() : "",
        active_users: cells[5] ? cells[5].textContent.trim() : "",
        total_households: cells[6] ? cells[6].textContent.trim() : "",
        ip: cells[7] ? cells[7].textContent.trim() : "",
        host: cells[8] ? cells[8].textContent.trim() : ""
      };

      nameCell.innerHTML = "";
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "building-name-link";
      btn.textContent = name;
      btn.onclick = function () {
        window.openBuildingDetailModal(building);
      };
      nameCell.appendChild(btn);
    });
  }

  document.addEventListener("click", function (event) {
    const mask = document.getElementById("building_detail_mask");
    if (event.target === mask) {
      window.closeBuildingDetailModal();
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindExistingBuildingNameCells);
  } else {
    bindExistingBuildingNameCells();
  }

  setTimeout(bindExistingBuildingNameCells, 500);
  setTimeout(bindExistingBuildingNameCells, 1000);
})();
