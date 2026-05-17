
    let buildings = [];
    let sortField = 'building_no';
    let sortAsc = true;
    const STORAGE_KEY = "shinnan_building_directory_overrides_v2";

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function goBackFromBuildings() {
      const params = new URLSearchParams(window.location.search);
      const caller = params.get("caller") || "";

      const pickReturn = localStorage.getItem("xunnan_building_pick_return") || "";
      const backReturn = localStorage.getItem("xunnan_building_back_return") || "";

      if (caller === "sales") {
        localStorage.removeItem("xunnan_building_back_return");
        window.location.href = "/admin/sales";
        return;
      }

      if (caller === "dispatch") {
        localStorage.removeItem("xunnan_building_back_return");
        window.location.href = "/admin";
        return;
      }

      if (backReturn) {
        localStorage.removeItem("xunnan_building_back_return");
        window.location.href = backReturn;
        return;
      }

      if (pickReturn) {
        if (pickReturn.includes("/admin/sales")) {
          window.location.href = "/admin/sales";
          return;
        }

        if (pickReturn.includes("/admin")) {
          window.location.href = "/admin";
          return;
        }
      }

      if (document.referrer) {
        try {
          const ref = new URL(document.referrer);

          if (ref.pathname === "/admin/sales") {
            window.location.href = "/admin/sales";
            return;
          }

          if (ref.pathname === "/admin") {
            window.location.href = "/admin";
            return;
          }

          if (ref.pathname && ref.pathname !== window.location.pathname) {
            history.back();
            return;
          }
        } catch (err) {
          history.back();
          return;
        }
      }

      window.location.href = "/admin";
    }

    function loadOverrides() {
      try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      } catch (e) {
        return {};
      }
    }

    function saveOverride(buildingNo, field, value) {
      const overrides = loadOverrides();
      if (!overrides[buildingNo]) overrides[buildingNo] = {};
      overrides[buildingNo][field] = value;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(overrides));
    }

    function applyOverrides(data) {
      const overrides = loadOverrides();

      return data.map(function (item) {
        if (overrides[item.building_no]) {
          return Object.assign({}, item, overrides[item.building_no]);
        }
        return item;
      });
    }

    async function loadBuildings() {
      const res = await fetch("/api/admin/buildings?ts=" + Date.now());
      const data = await res.json();
      buildings = applyOverrides(data);
      renderRows();
    }

    function getFiltered() {
      const areaEl = document.getElementById("area_filter");
      const area = areaEl.value;
      const isAllArea = !area || areaEl.selectedIndex === 0;
      const keyword = document.getElementById("keyword").value.trim().toLowerCase();

      return buildings.filter(function (b) {
        if (!isAllArea && b.area !== area) return false;
        if (!keyword) return true;

        return [
          b.building_no,
          b.name,
          b.area,
          b.address,
          b.management_company,
          b.ip
        ].join(" ").toLowerCase().includes(keyword);
      });
    }

    function sortBy(field) {
      if (sortField === field) {
        sortAsc = !sortAsc;
      } else {
        sortField = field;
        sortAsc = true;
      }
      renderRows();
    }

    function getSorted(data) {
      const numFields = ['active_users', 'total_households'];
      return data.slice().sort(function (a, b) {
        let va = a[sortField] ?? '';
        let vb = b[sortField] ?? '';
        if (sortField === 'building_no') {
          va = parseInt(String(va).replace(/[^0-9]/g, '')) || 0;
          vb = parseInt(String(vb).replace(/[^0-9]/g, '')) || 0;
        } else if (numFields.includes(sortField)) {
          va = parseFloat(va) || 0;
          vb = parseFloat(vb) || 0;
        } else {
          va = String(va).toLowerCase();
          vb = String(vb).toLowerCase();
        }
        if (va < vb) return sortAsc ? -1 : 1;
        if (va > vb) return sortAsc ? 1 : -1;
        return 0;
      });
    }

    function updateSortIcons() {
      const fields = ['building_no','name','area','address','management_company','active_users','total_households','ip'];
      fields.forEach(function (f) {
        const el = document.getElementById('sort_' + f);
        if (!el) return;
        if (f === sortField) {
          el.textContent = sortAsc ? ' ▲' : ' ▼';
          el.style.color = '#0f6b3b';
        } else {
          el.textContent = ' ⇅';
          el.style.color = '#bbb';
        }
      });
    }

    function renderRows() {
      const rows = document.getElementById("rows");
      const data = getSorted(getFiltered());
      updateSortIcons();

      rows.innerHTML = data.map(function (b) {
        return `
          <tr data-building-no="${escapeHtml(b.building_no)}">
            <td>${escapeHtml(b.building_no)}</td>
            <td contenteditable="true" data-field="name">${escapeHtml(b.name)}</td>
            <td contenteditable="true" data-field="area"><span class="pill">${escapeHtml(b.area)}</span></td>
            <td contenteditable="true" data-field="address">${escapeHtml(b.address)}</td>
            <td contenteditable="true" data-field="management_company">${escapeHtml(b.management_company)}</td>
            <td contenteditable="true" data-field="active_users">${escapeHtml(b.active_users)}</td>
            <td contenteditable="true" data-field="total_households">${escapeHtml(b.total_households)}</td>
            <td contenteditable="true" data-field="ip">${escapeHtml(b.ip)}</td>
            <td><button class="btn-small" type="button" onclick="hostLogin('${escapeHtml(b.ip)}')">主機登入</button></td>
            <td><button class="btn-small btn-danger" type="button" onclick="deleteBuilding('${escapeHtml(b.building_no)}', '${escapeHtml(b.name)}')">刪除</button></td>
          </tr>
        `;
      }).join("");

      bindEditableCells();
    }

    function bindEditableCells() {
      document.querySelectorAll("td[contenteditable='true']").forEach(function (cell) {
        cell.addEventListener("blur", function () {
          const tr = cell.closest("tr");
          const buildingNo = tr.dataset.buildingNo;
          const field = cell.dataset.field;
          const value = cell.innerText.trim();

          saveOverride(buildingNo, field, value);

          const item = buildings.find(b => b.building_no === buildingNo);
          if (item) item[field] = value;

          renderRows();
        });

        cell.addEventListener("keydown", function (event) {
          if (event.key === "Enter") {
            event.preventDefault();
            cell.blur();
          }
        });
      });
    }

    function hostLogin(ip) {
      alert("主機登入：" + ip);
    }

    async function deleteBuilding(buildingNo, name) {
      if (!confirm("確定要刪除「" + name + "」（" + buildingNo + "）？\n刪除後無法復原。")) return;
      try {
        const res = await fetch("/api/admin/buildings/" + encodeURIComponent(buildingNo), {
          method: "DELETE",
          credentials: "same-origin",
        });
        const data = await res.json().catch(function () { return {}; });
        if (!res.ok || !data.ok) {
          alert("刪除失敗：" + (data.error || res.status));
          return;
        }
        buildings = buildings.filter(function (b) { return b.building_no !== buildingNo; });
        renderRows();
      } catch (e) {
        alert("刪除失敗：" + e.message);
      }
    }
    function chooseBuilding(buildingNo) {
      const b = buildings.find(item => item.building_no === buildingNo);
      if (!b) return;

      const fullAddress = `${b.name} ${b.address}`;

      const result = {
        building_no: b.building_no,
        name: b.name,
        area: b.area,
        raw_address: b.address,
        address: fullAddress,
        management_company: b.management_company,
        ip: b.ip
      };

      localStorage.setItem("xunnan_building_pick_result", JSON.stringify(result));
      localStorage.setItem("xunnan_selected_building_no", result.building_no);
      localStorage.setItem("xunnan_selected_building_name", result.name);
      localStorage.setItem("xunnan_selected_building_area", result.area);
      localStorage.setItem("xunnan_selected_building_raw_address", result.raw_address);
      localStorage.setItem("xunnan_selected_building_address", result.address);

      const returnUrl = localStorage.getItem("xunnan_building_pick_return") || "/admin";
      window.location.href = returnUrl;
    }

    document.getElementById("area_filter").addEventListener("change", renderRows);
    document.getElementById("keyword").addEventListener("input", renderRows);

    loadBuildings();
  