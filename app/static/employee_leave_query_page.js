
(function () {
  var allItems = [];

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

  function statusText(value) {
    var s = String(value || "").toLowerCase();
    if (s === "approved") return "\u5df2\u6838\u51c6";
    if (s === "rejected") return "\u5df2\u99c1\u56de";
    if (s === "draft") return "\u8349\u7a3f";
    if (s === "pending" || s === "") return "\u5f85\u5be9\u6838";
    return value || "\u5f85\u5be9\u6838";
  }

  function statusClass(value) {
    var s = String(value || "").toLowerCase();
    if (s === "approved") return "status-approved";
    if (s === "rejected") return "status-rejected";
    if (s === "pending" || s === "") return "status-pending";
    return "";
  }

  function itemDate(item) {
    return item.leave_date || item.rest_date || "";
  }

  function itemType(item) {
    return item.leave_type || item.rest_type || "\u8acb\u5047";
  }

  function itemTime(item) {
    var a = item.start_time || "";
    var b = item.end_time || "";
    if (a && b) return a + " - " + b;
    if (a) return a;
    if (b) return b;
    return "";
  }

  function renderList() {
    var filter = byId("status_filter").value;
    var items = allItems.slice();

    if (filter) {
      items = items.filter(function (i) {
        return String(i.review_status || "").toLowerCase() === filter;
      });
    }

    byId("total_count").textContent = String(allItems.length);
    byId("pending_count").textContent = String(allItems.filter(function (i) {
      var s = String(i.review_status || "").toLowerCase();
      return s === "" || s === "pending";
    }).length);

    if (!items.length) {
      byId("leave_list").innerHTML = "<div class=\"hint\">\u76ee\u524d\u6c92\u6709\u7b26\u5408\u689d\u4ef6\u7684\u5047\u55ae\u3002</div>";
      return;
    }

    byId("leave_list").innerHTML = items.map(function (item) {
      var status = item.review_status || "pending";
      var date = itemDate(item);
      var type = itemType(item);
      var time = itemTime(item);
      var note = item.note || "";
      var updated = item.updated_at || "";

      return "<article class=\"leave-item\">" +
        "<div class=\"leave-top\">" +
          "<div class=\"leave-title\">" + esc(date || "\u672a\u8a2d\u5b9a\u65e5\u671f") + "?" + esc(type) + "</div>" +
          "<div class=\"status-badge " + statusClass(status) + "\">" + esc(statusText(status)) + "</div>" +
        "</div>" +
        "<div class=\"leave-meta\">" +
          (time ? "\u6642\u9593\uff1a" + esc(time) + "<br>" : "") +
          (note ? "\u5099\u8a3b\uff1a" + esc(note) + "<br>" : "") +
          (updated ? "\u66f4\u65b0\uff1a" + esc(updated) : "") +
        "</div>" +
      "</article>";
    }).join("");
  }

  async function loadLeaveSettings() {
    byId("leave_list").innerHTML = "<div class=\"hint\">\u8cc7\u6599\u8f09\u5165\u4e2d...</div>";

    try {
      var res = await fetch("/api/app/employee/leave-settings?ts=" + Date.now(), {
        cache: "no-store",
        credentials: "same-origin"
      });

      var data = await res.json().catch(function () {
        return {};
      });

      if (!res.ok || !data.ok) {
        throw new Error(data.error || "load failed");
      }

      allItems = Array.isArray(data.items) ? data.items : [];
      byId("period_label").textContent = data.period_label || "\u8acb\u5047\u7d00\u9304";
      renderList();
    } catch (e) {
      byId("period_label").textContent = "\u8cc7\u6599\u8f09\u5165\u5931\u6557";
      byId("leave_list").innerHTML = "<div class=\"hint\">\u7121\u6cd5\u8f09\u5165\u5047\u55ae\u8cc7\u6599\u3002</div>";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    byId("reload_btn").addEventListener("click", loadLeaveSettings);
    byId("status_filter").addEventListener("change", renderList);
    loadLeaveSettings();
  });
})();
