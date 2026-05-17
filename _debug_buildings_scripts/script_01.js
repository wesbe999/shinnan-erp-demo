
// SHINNAN_BUILDING_CREATE_DATA_V1
(function () {
  const ADD_STORAGE_KEY = "shinnan_building_directory_additional_v1";

  function loadAdditionalBuildings() {
    try {
      return JSON.parse(localStorage.getItem(ADD_STORAGE_KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function saveAdditionalBuildings(items) {
    localStorage.setItem(ADD_STORAGE_KEY, JSON.stringify(items));
  }

  function nextBuildingNo() {
    const additional = loadAdditionalBuildings();
    const nums = [];

    try {
      buildings.forEach(function (b) {
        const m = String(b.building_no || "").match(/^B(\d+)$/);
        if (m) nums.push(Number(m[1]));
      });
    } catch (e) {}

    additional.forEach(function (b) {
      const m = String(b.building_no || "").match(/^B(\d+)$/);
      if (m) nums.push(Number(m[1]));
    });

    const next = nums.length ? Math.max(...nums) + 1 : 1;
    return "B" + String(next).padStart(3, "0");
  }

  function openCreateBuildingModal() {
    const modal = document.getElementById("create_building_modal");
    if (modal) modal.classList.add("active");
  }

  function closeCreateBuildingModal() {
    const modal = document.getElementById("create_building_modal");
    if (modal) modal.classList.remove("active");
  }

  function createBuilding() {
    const name = document.getElementById("new_building_name").value.trim();
    const area = document.getElementById("new_building_area").value;
    const address = document.getElementById("new_building_address").value.trim();
    const managementCompany = document.getElementById("new_management_company").value.trim();
    const activeUsers = Number(String(document.getElementById("new_active_users").value || "0").replace(/[^\d]/g, ""));
    const totalHouseholds = Number(String(document.getElementById("new_total_households").value || "0").replace(/[^\d]/g, ""));
    const ip = document.getElementById("new_building_ip").value.trim();

    if (!name) {
      alert("請輸入大樓名稱");
      return;
    }

    if (!address) {
      alert("請輸入地址");
      return;
    }

    const item = {
      building_no: nextBuildingNo(),
      name: name,
      area: area,
      address: address,
      display_address: name + " " + address,
      management_company: managementCompany || "未填",
      active_users: activeUsers,
      total_households: totalHouseholds,
      ip: ip || "未設定"
    };

    const additional = loadAdditionalBuildings();
    additional.push(item);
    saveAdditionalBuildings(additional);

    buildings.push(item);

    closeCreateBuildingModal();
    renderRows();

    document.getElementById("new_building_name").value = "";
    document.getElementById("new_building_address").value = "";
    document.getElementById("new_management_company").value = "";
    document.getElementById("new_active_users").value = "0";
    document.getElementById("new_total_households").value = "0";
    document.getElementById("new_building_ip").value = "";

    alert("大樓資料已新增");
  }

  function patchLoadBuildings() {
    if (window.__shinnanBuildingCreatePatched) return;
    window.__shinnanBuildingCreatePatched = true;

    const oldLoadBuildings = window.loadBuildings || loadBuildings;

    window.loadBuildings = async function () {
      const res = await fetch("/api/admin/buildings?ts=" + Date.now());
      const data = await res.json();
      const merged = data.concat(loadAdditionalBuildings());
      buildings = applyOverrides(merged);
      renderRows();
    };
  }

  document.addEventListener("DOMContentLoaded", function () {
    patchLoadBuildings();

    const createButton = document.getElementById("create_building_button");
    const cancelButton = document.getElementById("cancel_create_building_button");
    const saveButton = document.getElementById("save_create_building_button");

    if (createButton) createButton.addEventListener("click", openCreateBuildingModal);
    if (cancelButton) cancelButton.addEventListener("click", closeCreateBuildingModal);
    if (saveButton) saveButton.addEventListener("click", createBuilding);
  });
})();
