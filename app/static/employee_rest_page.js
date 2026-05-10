
(function () {
  var selectedRestDates = [];
  var requiredRestDays = 8;
  var holidayMap = {};

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

  function dateKey(y, m, d) {
    return y + "-" + String(m).padStart(2, "0") + "-" + String(d).padStart(2, "0");
  }

  function initMonthOptions() {
    var now = new Date();
    var y = byId("rest_year");
    var m = byId("rest_month");

    y.innerHTML = "";
    for (var yy = now.getFullYear() - 1; yy <= now.getFullYear() + 1; yy++) {
      var yo = document.createElement("option");
      yo.value = String(yy);
      yo.textContent = yy + " \u5e74";
      y.appendChild(yo);
    }
    y.value = String(now.getFullYear());

    m.innerHTML = "";
    for (var mm = 1; mm <= 12; mm++) {
      var mo = document.createElement("option");
      mo.value = String(mm);
      mo.textContent = mm + " \u6708";
      m.appendChild(mo);
    }
    m.value = String(now.getMonth() + 1);

    y.addEventListener("change", loadRestMonth);
    m.addEventListener("change", loadRestMonth);
    byId("reload_rest_btn").addEventListener("click", loadRestMonth);
    byId("save_rest_btn").addEventListener("click", function () {
      saveRestMonth(false);
    });
  }

  async function loadHolidays(year) {
    holidayMap = {};
    byId("holiday_status").textContent = "\u570b\u5b9a\u5047\u65e5\uff1a\u8f09\u5165\u4e2d...";

    try {
      var res = await fetch("/api/app/employee/holidays?year=" + encodeURIComponent(year) + "&ts=" + Date.now(), {
        cache: "no-store",
        credentials: "same-origin"
      });

      if (!res.ok) {
        throw new Error("holiday api failed");
      }

      var data = await res.json();

      (data.items || []).forEach(function (item) {
        var key = String(item.holiday_date || "").slice(0, 10);
        if (key) {
          holidayMap[key] = item.title || "\u570b\u5b9a\u5047\u65e5";
        }
      });

      var count = Object.keys(holidayMap).length;
      byId("holiday_status").textContent = count
        ? "\u570b\u5b9a\u5047\u65e5\uff1a\u5df2\u8f09\u5165 " + count + " \u7b46\uff0c\u6703\u5728\u65e5\u66c6\u4e0a\u4ee5\u7d05\u8272\u6a19\u793a\u3002"
        : "\u570b\u5b9a\u5047\u65e5\uff1a\u4eca\u5e74\u76ee\u524d\u6c92\u6709\u8cc7\u6599\u3002";
    } catch (e) {
      byId("holiday_status").textContent = "\u570b\u5b9a\u5047\u65e5\uff1a\u8f09\u5165\u5931\u6557\u3002";
    }
  }

  async function loadRestMonth() {
    var now = new Date();
    var y = Number(byId("rest_year").value || now.getFullYear());
    var m = Number(byId("rest_month").value || now.getMonth() + 1);

    byId("rest_summary").textContent = "\u6392\u4f11\u8cc7\u6599\u8f09\u5165\u4e2d...";

    await loadHolidays(y);

    try {
      var res = await fetch("/api/app/employee/rest-month?year=" + y + "&month=" + m + "&ts=" + Date.now(), {
        cache: "no-store",
        credentials: "same-origin"
      });

      if (!res.ok) {
        throw new Error("rest api failed");
      }

      var data = await res.json();
      selectedRestDates = Array.isArray(data.selected_dates) ? data.selected_dates : [];
      requiredRestDays = Number(data.required_rest_days || 8);
    } catch (e) {
      selectedRestDates = [];
      requiredRestDays = 8;
      byId("rest_summary").textContent = "\u6392\u4f11\u8cc7\u6599\u8f09\u5165\u5931\u6557\uff0c\u5148\u986f\u793a\u7a7a\u767d\u6708\u66c6\u3002";
    }

    renderRestCalendar(y, m);
  }

  function renderRestCalendar(y, m) {
    var box = byId("calendar_grid");
    var days = new Date(y, m, 0).getDate();
    var start = new Date(y, m - 1, 1).getDay();

    var html = ["\u65e5", "\u4e00", "\u4e8c", "\u4e09", "\u56db", "\u4e94", "\u516d"].map(function (w) {
      return "<button class=\"week-cell\" disabled>" + w + "</button>";
    }).join("");

    for (var i = 0; i < start; i++) {
      html += "<button class=\"day-cell blank\" disabled></button>";
    }

    for (var d = 1; d <= days; d++) {
      var key = dateKey(y, m, d);
      var wk = new Date(y, m - 1, d).getDay();
      var selected = selectedRestDates.indexOf(key) >= 0;
      var holiday = holidayMap[key] || "";

      var cls = [
        "day-cell",
        (wk === 0 || wk === 6) ? "weekend" : "",
        holiday ? "holiday" : "",
        selected ? "selected" : ""
      ].join(" ");

      html += "<button class=\"" + cls + "\" data-date=\"" + key + "\">" +
        d +
        (holiday ? "<br><small>" + esc(holiday) + "</small>" : "") +
        "</button>";
    }

    box.innerHTML = html;

    Array.prototype.forEach.call(box.querySelectorAll(".day-cell[data-date]"), function (btn) {
      btn.addEventListener("click", function () {
        toggleRestDate(btn.getAttribute("data-date"));
      });
    });

    var missing = Math.max(0, requiredRestDays - selectedRestDates.length);
    byId("rest_summary").textContent =
      "\u5df2\u9078 " + selectedRestDates.length +
      " \u5929\uff5c\u61c9\u9078 " + requiredRestDays +
      " \u5929" +
      (missing ? "\uff5c\u5c1a\u7f3a " + missing + " \u5929" : "\uff5c\u5df2\u9054\u6a19");
  }

  function toggleRestDate(key) {
    if (selectedRestDates.indexOf(key) >= 0) {
      selectedRestDates = selectedRestDates.filter(function (x) {
        return x !== key;
      });
    } else {
      selectedRestDates = selectedRestDates.concat([key]).sort();
    }

    renderRestCalendar(Number(byId("rest_year").value), Number(byId("rest_month").value));
  }

  async function saveRestMonth(force) {
    var y = Number(byId("rest_year").value);
    var m = Number(byId("rest_month").value);

    var res = await fetch("/api/app/employee/rest-month/save", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({
        year: y,
        month: m,
        selected_dates: selectedRestDates,
        force: Boolean(force)
      })
    });

    var data = await res.json().catch(function () {
      return {};
    });

    if (res.status === 409 && data.need_confirm) {
      if (confirm((data.error || "\u672c\u6708\u6392\u4f11\u5929\u6578\u4e0d\u8db3") + "\n\u662f\u5426\u4ecd\u8981\u7e7c\u7e8c\u9001\u51fa\uff1f")) {
        saveRestMonth(true);
      }
      return;
    }

    if (!res.ok || !data.ok) {
      alert(data.error || "\u6392\u4f11\u8a2d\u5b9a\u5132\u5b58\u5931\u6557");
      return;
    }

    alert("\u6392\u4f11\u8a2d\u5b9a\u5df2\u9001\u51fa");
    location.href = "/app";
  }

  document.addEventListener("DOMContentLoaded", function () {
    initMonthOptions();
    loadRestMonth();
  });
})();
