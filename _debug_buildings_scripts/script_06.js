
(function () {
  function esc(v) {
    return String(v == null ? "" : v)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function setDebug(text) {
    var box = document.getElementById("dispatch_recovery_debug_box");
    if (!box) {
      box = document.createElement("div");
      box.id = "dispatch_recovery_debug_box";
      box.style.cssText = "display:none;";
      var anchor = document.querySelector(".stats-grid") || document.getElementById("list") || document.body.firstChild;
      if (anchor && anchor.parentNode) {
        anchor.parentNode.insertBefore(box, anchor);
      } else {
        document.body.insertBefore(box, document.body.firstChild);
      }
    }
    box.textContent = text;
  }

  function isActive(item) {
    var s = String(item.status || "");
    return s !== "已完成" && s !== "取消" && s !== "作廢";
  }

  function renderItems(items, user) {
    var list = document.getElementById("list");
    if (!list) {
      setDebug("補救渲染失敗：找不到 #list");
      return;
    }

    document.querySelectorAll(".stat-card .stat-value").forEach(function (el, idx) {
      if (idx === 0) {
        var today = new Date().toISOString().slice(0, 10);
        el.textContent = items.filter(function (x) { return x.appointment_date === today; }).length;
      }
      if (idx === 1) {
        el.textContent = items.filter(function (x) {
          return x.status === "施工中" || x.status === "已領取";
        }).length;
      }
      if (idx === 2) {
        el.textContent = items.length;
      }
    });

    if (!items.length) {
      list.innerHTML = '<div class="empty">目前沒有派工案件。</div>';
      return;
    }

    list.innerHTML = items.map(function (item) {
      return `
        <div class="ticket-card">
          <div class="ticket-title">${esc(item.ticket_no || "-")}｜${esc(item.case_type || "-")}</div>
          <div class="ticket-sub">${esc(item.customer_name || "-")}｜${esc(item.customer_no || "-")}｜${esc(item.building_no || "-")}</div>
          <div class="ticket-grid">
            <div class="info">
              <div class="info-label">狀態</div>
              <div class="info-value">${esc(item.status || "-")}</div>
            </div>
            <div class="info">
              <div class="info-label">預約</div>
              <div class="info-value">${esc(item.appointment_date || "-")} ${esc(item.appointment_time || "")}</div>
            </div>
            <div class="info">
              <div class="info-label">工程師</div>
              <div class="info-value">${esc(item.assigned_engineer || "-")}｜${esc(item.assigned_engineer_staff_code || "-")}</div>
            </div>
            <div class="info">
              <div class="info-label">地址</div>
              <div class="info-value">${esc(item.service_address || "-")}</div>
            </div>
          </div>
        </div>
      `;
    }).join("");
  }

  async function recoveryLoadDispatchTickets() {
    try {
      setDebug("補救讀取：準備抓派工 API");

      var res = await fetch("/api/app/dispatch/tickets?ts=" + Date.now(), {
        cache: "no-store",
        credentials: "same-origin"
      });

      setDebug("補救讀取：HTTP " + res.status);

      if (res.status === 401) {
        setDebug("補救讀取：401，登入已失效");
        location.href = "/employee/login?next=/app/dispatch";
        return;
      }

      if (!res.ok) {
        var txt = await res.text();
        setDebug("補救讀取失敗：HTTP " + res.status);
        var list = document.getElementById("list");
        if (list) list.innerHTML = '<div class="empty">補救讀取失敗：HTTP ' + res.status + '<br>' + esc(txt.slice(0, 300)) + '</div>';
        return;
      }

      var data = await res.json();
      var items = data.items || [];

      setDebug("補救讀取：OK｜使用者：" + ((data.user && data.user.display_name) || "-") + "｜案件：" + items.length);

      renderItems(items, data.user || {});
    } catch (err) {
      var msg = String(err && err.message ? err.message : err);
      setDebug("補救讀取錯誤：" + msg);
      var list = document.getElementById("list");
      if (list) list.innerHTML = '<div class="empty">補救讀取錯誤：<br>' + esc(msg) + '</div>';
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", recoveryLoadDispatchTickets);
  } else {
    recoveryLoadDispatchTickets();
  }

  setTimeout(recoveryLoadDispatchTickets, 800);
})();
