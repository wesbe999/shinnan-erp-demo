
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  function goBackFromBuildingsSimple(event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
      if (event.stopImmediatePropagation) event.stopImmediatePropagation();
    }

    const params = new URLSearchParams(window.location.search);
    const caller = params.get("caller") || "";

    if (caller === "sales") {
      window.location.href = "/admin/sales";
      return;
    }

    if (caller === "dispatch") {
      window.location.href = "/admin";
      return;
    }

    const backReturn = localStorage.getItem("xunnan_building_back_return") || "";
    const pickReturn = localStorage.getItem("xunnan_building_pick_return") || "";

    const candidates = [backReturn, pickReturn];

    for (const raw of candidates) {
      if (!raw) continue;
      try {
        const u = new URL(raw, window.location.origin);
        if (u.pathname === "/admin/sales") {
          window.location.href = "/admin/sales";
          return;
        }
        if (u.pathname === "/admin") {
          window.location.href = "/admin";
          return;
        }
      } catch (err) {}
    }

    window.location.href = "/admin";
  }

  window.goBackFromBuildings = goBackFromBuildingsSimple;

  function bindBackButtons() {
    Array.from(document.querySelectorAll("button, a")).forEach(function (el) {
      const text = String(el.textContent || "").trim();

      if (text === "返回上一頁" || text === "返回後台" || text === "返回首頁") {
        el.textContent = "返回上一頁";
        el.onclick = goBackFromBuildingsSimple;
        el.addEventListener("click", goBackFromBuildingsSimple, true);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindBackButtons);
  } else {
    bindBackButtons();
  }

  setTimeout(bindBackButtons, 300);
  setTimeout(bindBackButtons, 800);
})();
