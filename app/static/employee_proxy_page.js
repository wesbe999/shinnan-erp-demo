
(function () {
  var employees = [];

  function byId(id) {
    return document.getElementById(id);
  }

  function esc(v) {
    return String(v == null ? "" : v)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll("\"", "&quot;")
      .replaceAll("'", "&#039;");
  }

  function employeeLabel(item) {
    var code = item.staff_code || "";
    var name = item.display_name || "";
    var dept = item.department || "";
    if (code && name) {
      return code + "?" + name + (dept ? "?" + dept : "");
    }
    return code || name || "";
  }

  function fillEmployeeOptions() {
    var datalist = byId("proxy_employee_options");
    datalist.innerHTML = "";

    employees.forEach(function (item) {
      var opt = document.createElement("option");
      opt.value = employeeLabel(item);
      datalist.appendChild(opt);
    });
  }

  async function loadEmployees() {
    var res = await fetch("/api/app/employee/list-for-proxy?ts=" + Date.now(), {
      cache: "no-store",
      credentials: "same-origin"
    });

    var data = await res.json().catch(function () {
      return {};
    });

    if (!res.ok || !data.ok) {
      throw new Error(data.error || "list failed");
    }

    employees = Array.isArray(data.items) ? data.items : [];
    fillEmployeeOptions();
  }

  async function loadPendingRequests() {
    var box = byId("pending_proxy_list");
    box.innerHTML = "<div class=\"hint\">\u8cc7\u6599\u8f09\u5165\u4e2d...</div>";

    try {
      var res = await fetch("/api/app/employee/proxy/pending-requests?ts=" + Date.now(), {
        cache: "no-store",
        credentials: "same-origin"
      });

      var data = await res.json().catch(function () {
        return {};
      });

      if (!res.ok || !data.ok) {
        throw new Error(data.error || "pending failed");
      }

      var items = Array.isArray(data.items) ? data.items : [];

      if (!items.length) {
        box.innerHTML = "<div class=\"hint\">\u76ee\u524d\u6c92\u6709\u5f85\u540c\u610f\u4ee3\u7406\u9080\u8acb\u3002</div>";
        return;
      }

      box.innerHTML = items.map(function (item) {
        var slot = item.slot || "";
        var requester = item.requester_name || item.requester_staff_code || "";
        var dept = item.requester_department || "";
        return "<article class=\"pending-item\">" +
          "<div class=\"pending-title\">" + esc(requester) + " \u9080\u8acb\u4f60\u6210\u70ba\u4ee3\u7406\u4eba</div>" +
          "<div class=\"pending-meta\">" + esc(dept) + (slot ? "?" + esc(slot) : "") + "</div>" +
          "<div class=\"pending-actions\">" +
            "<button class=\"accept-btn\" data-code=\"" + esc(item.requester_staff_code || "") + "\" data-slot=\"" + esc(slot) + "\" data-status=\"accepted\">\u540c\u610f</button>" +
            "<button class=\"reject-btn\" data-code=\"" + esc(item.requester_staff_code || "") + "\" data-slot=\"" + esc(slot) + "\" data-status=\"rejected\">\u62d2\u7d55</button>" +
          "</div>" +
        "</article>";
      }).join("");

      Array.prototype.forEach.call(box.querySelectorAll("button[data-code]"), function (btn) {
        btn.addEventListener("click", function () {
          respondProxy(btn.getAttribute("data-code"), btn.getAttribute("data-slot"), btn.getAttribute("data-status"));
        });
      });
    } catch (e) {
      box.innerHTML = "<div class=\"hint\">\u5f85\u540c\u610f\u9080\u8acb\u8f09\u5165\u5931\u6557\u3002</div>";
    }
  }

  async function respondProxy(requesterStaffCode, slot, status) {
    var res = await fetch("/api/app/employee/proxy/respond", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({
        requester_staff_code: requesterStaffCode,
        slot: slot,
        status: status
      })
    });

    var data = await res.json().catch(function () {
      return {};
    });

    if (!res.ok || !data.ok) {
      alert(data.error || "\u4ee3\u7406\u9080\u8acb\u56de\u8986\u5931\u6557");
      return;
    }

    alert(status === "accepted" ? "\u5df2\u540c\u610f\u4ee3\u7406\u9080\u8acb" : "\u5df2\u62d2\u7d55\u4ee3\u7406\u9080\u8acb");
    loadPendingRequests();
  }

  async function saveProxy() {
    var one = byId("proxy_one").value.trim();
    var two = byId("proxy_two").value.trim();

    var res = await fetch("/api/app/employee/proxy/save", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({
        proxy_one: one,
        proxy_two: two,
        proxy_one_staff_code: one,
        proxy_two_staff_code: two
      })
    });

    var data = await res.json().catch(function () {
      return {};
    });

    if (!res.ok || !data.ok) {
      alert(data.error || "\u4ee3\u7406\u4eba\u5132\u5b58\u5931\u6557");
      return;
    }

    var s1 = data.proxy_one_status || "";
    var s2 = data.proxy_two_status || "";

    byId("proxy_status").textContent =
      "\u4ee3\u7406\u4eba\u5df2\u5132\u5b58\u3002" +
      (s1 ? "\u4ee3\u7406\u4eba\u4e00\u72c0\u614b\uff1a" + s1 + "\u3002" : "") +
      (s2 ? "\u4ee3\u7406\u4eba\u4e8c\u72c0\u614b\uff1a" + s2 + "\u3002" : "");

    alert("\u4ee3\u7406\u4eba\u5df2\u5132\u5b58\uff0c\u82e5\u70ba\u65b0\u4ee3\u7406\u4eba\u9700\u7b49\u5c0d\u65b9\u540c\u610f\u3002");
  }

  async function loadAll() {
    byId("proxy_status").textContent = "\u4ee3\u7406\u4eba\u8cc7\u6599\u8f09\u5165\u4e2d...";

    try {
      await loadEmployees();
      await loadPendingRequests();
      byId("proxy_status").textContent = "\u54e1\u5de5\u9078\u55ae\u5df2\u8f09\u5165\uff0c\u5171 " + employees.length + " \u4eba\u53ef\u9078\u3002";
    } catch (e) {
      byId("proxy_status").textContent = "\u4ee3\u7406\u4eba\u8cc7\u6599\u8f09\u5165\u5931\u6557\u3002";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    byId("save_proxy_btn").addEventListener("click", saveProxy);
    byId("reload_proxy_btn").addEventListener("click", loadAll);
    loadAll();
  });
})();
