
(function () {
  var leaveDates = [];
  var leaveHolidayMap = {};

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

  function initLeaveCalendarOptions() {
    var now = new Date();
    var y = byId("leave_calendar_year");
    var m = byId("leave_calendar_month");

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

    y.addEventListener("change", renderLeaveCalendar);
    m.addEventListener("change", renderLeaveCalendar);
  }

  async function loadLeaveHolidays(year) {
    leaveHolidayMap = {};
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
          leaveHolidayMap[key] = item.title || "\u570b\u5b9a\u5047\u65e5";
        }
      });

      var count = Object.keys(leaveHolidayMap).length;
      byId("holiday_status").textContent = count
        ? "\u570b\u5b9a\u5047\u65e5\uff1a\u5df2\u8f09\u5165 " + count + " \u7b46\uff0c\u65e5\u66c6\u4e0a\u6703\u4ee5\u7d05\u8272\u6a19\u793a\u3002"
        : "\u570b\u5b9a\u5047\u65e5\uff1a\u4eca\u5e74\u76ee\u524d\u6c92\u6709\u8cc7\u6599\u3002";
    } catch (e) {
      byId("holiday_status").textContent = "\u570b\u5b9a\u5047\u65e5\uff1a\u8f09\u5165\u5931\u6557\u3002";
    }
  }

  async function renderLeaveCalendar() {
    var y = Number(byId("leave_calendar_year").value);
    var m = Number(byId("leave_calendar_month").value);

    await loadLeaveHolidays(y);

    var box = byId("leave_calendar_grid");
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
      var selected = leaveDates.indexOf(key) >= 0;
      var holiday = leaveHolidayMap[key] || "";

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
        toggleLeaveDate(btn.getAttribute("data-date"));
      });
    });

    updateLeaveDisplay();
  }

  function toggleLeaveDate(key) {
    if (leaveDates.indexOf(key) >= 0) {
      leaveDates = leaveDates.filter(function (x) {
        return x !== key;
      });
    } else {
      leaveDates = leaveDates.concat([key]).sort();
    }

    renderLeaveCalendar();
  }

  function updateLeaveDisplay() {
    byId("leave_date_display").value = leaveDates.join("\u3001");
    byId("leave_calendar_summary").textContent = leaveDates.length
      ? "\u5df2\u9078 " + leaveDates.length + " \u5929"
      : "\u8acb\u9078\u64c7\u8acb\u5047\u65e5\u671f";
  }

  function readFileAsDataUrl(file) {
    return new Promise(function (resolve, reject) {
      if (!file) {
        resolve("");
        return;
      }
      var reader = new FileReader();
      reader.onload = function () {
        resolve(String(reader.result || ""));
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  async function submitLeaveSetting() {
    if (!leaveDates.length) {
      alert("\u8acb\u9078\u64c7\u8acb\u5047\u65e5\u671f");
      return;
    }

    var type = byId("leave_type").value;
    var file = byId("proof_photo").files[0];
    var needProof = ["\u75c5\u5047", "\u516c\u5047", "\u55aa\u5047", "\u5176\u4ed6\u9700\u8b49\u660e"].indexOf(type) >= 0;

    if (needProof && !file) {
      alert("\u6b64\u5047\u5225\u9700\u9644\u4e0a\u8b49\u660e\u7167\u7247");
      return;
    }

    var proof = await readFileAsDataUrl(file);

    var res = await fetch("/api/app/employee/leave-settings/create", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({
        leave_type: type,
        leave_date: leaveDates[0],
        leave_dates: leaveDates,
        start_time: byId("start_time").value,
        end_time: byId("end_time").value,
        note: byId("note").value,
        proof_image_data: proof
      })
    });

    var data = await res.json().catch(function () {
      return {};
    });

    if (!res.ok || !data.ok) {
      alert(data.error || "\u9001\u51fa\u5931\u6557");
      return;
    }

    alert("\u5df2\u9001\u51fa\u8acb\u5047\u7533\u8acb\uff0c\u5171 " + leaveDates.length + " \u5929");
    location.href = "/app";
  }

  function clearLeaveForm() {
    leaveDates = [];
    byId("start_time").value = "";
    byId("end_time").value = "";
    byId("note").value = "";
    byId("proof_photo").value = "";
    updateLeaveDisplay();
    renderLeaveCalendar();
  }

  document.addEventListener("DOMContentLoaded", function () {
    initLeaveCalendarOptions();
    renderLeaveCalendar();

    byId("submit_leave_btn").addEventListener("click", submitLeaveSetting);
    byId("clear_leave_btn").addEventListener("click", clearLeaveForm);
  });
})();
