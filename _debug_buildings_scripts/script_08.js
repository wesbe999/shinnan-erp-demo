
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  function safeBack(event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
      if (event.stopImmediatePropagation) event.stopImmediatePropagation();
    }

    const params = new URLSearchParams(location.search);
    const caller = params.get("caller") || "";

    if (caller === "sales") {
      location.href = "/admin/sales";
      return;
    }

    if (caller === "dispatch") {
      location.href = "/admin";
      return;
    }

    const backReturn = localStorage.getItem("xunnan_building_back_return") || "";
    const pickReturn = localStorage.getItem("xunnan_building_pick_return") || "";

    for (const raw of [backReturn, pickReturn]) {
      if (!raw) continue;
      try {
        const u = new URL(raw, location.origin);
        if (u.pathname === "/admin/sales") {
          location.href = "/admin/sales";
          return;
        }
        if (u.pathname === "/admin") {
          location.href = "/admin";
          return;
        }
      } catch (err) {}
    }

    location.href = "/admin";
  }

  window.goBackFromBuildings = safeBack;

  function bindBack() {
    Array.from(document.querySelectorAll("button, a")).forEach(function (el) {
      const txt = String(el.textContent || "").trim();
      if (txt !== "返回上一頁" && txt !== "返回後台" && txt !== "返回首頁") return;

      const clone = el.cloneNode(true);
      clone.textContent = "返回上一頁";
      clone.onclick = safeBack;
      clone.addEventListener("click", safeBack, true);
      el.parentNode.replaceChild(clone, el);
    });
  }

  function valueOf(id) {
    const el = document.getElementById(id);
    return el ? String(el.value || "").trim() : "";
  }

  async function createBuildingToDb(event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
      if (event.stopImmediatePropagation) event.stopImmediatePropagation();
    }

    const name = valueOf("new_building_name");
    const area = valueOf("new_building_area");
    const address = valueOf("new_building_address");
    const managementCompany = valueOf("new_management_company");
    const activeUsers = Number(valueOf("new_active_users").replace(/[^\d]/g, "") || 0);
    const totalHouseholds = Number(valueOf("new_total_households").replace(/[^\d]/g, "") || 0);
    const ip = valueOf("new_building_ip");

    if (!name) {
      alert("請輸入大樓名稱");
      return false;
    }

    const payload = {
      name: name,
      area: area,
      address: address,
      raw_address: address,
      display_address: address,
      management_company: managementCompany,
      active_users: activeUsers,
      total_households: totalHouseholds,
      ip: ip
    };

    try {
      const res = await fetch("/api/admin/buildings", {
        method: "POST",
        headers: {"Content-Type": "application/json; charset=utf-8"},
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(await res.text());
      }

      const modal = document.getElementById("create_building_modal");
      if (modal) modal.classList.remove("active");

      ["new_building_name", "new_building_address", "new_management_company", "new_building_ip"].forEach(function (id) {
        const el = document.getElementById(id);
        if (el) el.value = "";
      });

      const au = document.getElementById("new_active_users");
      const th = document.getElementById("new_total_households");
      if (au) au.value = "0";
      if (th) th.value = "0";

      if (typeof window.loadBuildings === "function") {
        await window.loadBuildings();
      } else {
        location.reload();
      }

      alert("大樓資料已新增");
      return false;
    } catch (err) {
      console.error("create building failed", err);
      alert("新增大樓失敗，請再試一次。");
      return false;
    }
  }

  function bindCreateSave() {
    const btn = document.getElementById("save_create_building_button");
    if (!btn || btn.dataset.cl15g2Bound === "1") return;

    const clone = btn.cloneNode(true);
    clone.dataset.cl15g2Bound = "1";
    clone.onclick = createBuildingToDb;
    clone.addEventListener("click", createBuildingToDb, true);
    btn.parentNode.replaceChild(clone, btn);
  }

  function bindAll() {
    bindBack();
    bindCreateSave();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindAll);
  } else {
    bindAll();
  }

  setTimeout(bindAll, 300);
  setTimeout(bindAll, 900);
})();
