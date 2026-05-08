    let allTickets = [];
    let currentFilter = "全部";

    function esc(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function todayText() {
      const d = new Date();
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      return y + "-" + m + "-" + day;
    }

    function ticketTodayValue(item) {
      const appointment = String((item && item.appointment_date) || "").slice(0, 10);
      if (appointment) return appointment;

      const created = String((item && item.created_at) || "").slice(0, 10);
      return created;
    }

    function isActive(item) {
      return !["已完成", "已完工", "取消", "已取消"].includes(item.status || "");
    }

    function appointmentText(item) {
      const d = item.appointment_date || "";
      const t = item.appointment_time || "";

      if (!d && !t) return "-";
      return [d, t].filter(Boolean).join(" ");
    }

    function statusTone(status) {
      const s = String(status || "").trim();

      if (s === "待派工" || s === "未派工" || s === "已建立" || s === "已指派") return "state-wait";
      if (s === "已領取") return "state-claim";
      if (s === "施工中") return "state-work";
      if (s === "已完工" || s === "已完成") return "state-done";

      return "state-other";
    }

    function customerText(item) {
      return item.customer_name || item.contact_name || "-";
    }

    function phoneText(item) {
      return item.contact_phone || item.customer_phone || "-";
    }

    function addressText(item) {
      return item.service_address || item.address || "-";
    }

    function engineerText(item) {
      return item.assigned_engineer || "未指派";
    }

    function buildAutoLeaveReminder() {
      const now = new Date();
      const month = now.getMonth() + 1;
      const day = now.getDate();

      if (month % 2 !== 0 || day < 20) return "";

      let nextMonth = month + 1;
      if (nextMonth > 12) nextMonth = 1;

      return "請盡速設定 " + month + "-" + nextMonth + " 月的假表，請假需附上證明照片。";
    }


/* XN_DISPATCH_FRONTEND_PROXY_UI_V1 */
let currentDispatchUser = null;

function renderDispatchProxyUserV1(user) {
  currentDispatchUser = user || null;

  const banner = document.getElementById("dispatch_proxy_user_banner");
  const heroSub = document.querySelector(".hero-sub");

  if (!user) {
    if (banner) {
      banner.className = "proxy-user-banner normal";
      banner.textContent = "";
    }
    return;
  }

  const displayName = user.display_name || user.staff_code || "";
  const loginCode = user.login_staff_code || "";
  const ownerCode = user.permission_owner_code || user.staff_code || "";
  const isProxy = !!user.is_proxy_mode;

  if (heroSub) {
    if (isProxy) {
      heroSub.textContent = displayName;
    } else {
      heroSub.textContent = displayName;
    }
  }

  if (!banner) return;

  if (isProxy) {
    banner.className = "proxy-user-banner proxy";
    banner.textContent = "目前以「" + displayName + "」身分代理操作｜登入者：" + loginCode + "｜權限來源：" + ownerCode;
  } else {
    banner.className = "proxy-user-banner normal";
    banner.textContent = "";
  }
}
/* XN_DISPATCH_FRONTEND_PROXY_UI_V1_END */

    async function loadEmergencyNotices() {
      const track = document.getElementById("emergency_track");
      if (!track) return;

      try {
        const res = await fetch("/api/app/dispatch/emergency-notices?ts=" + Date.now(), {
          cache: "no-store",
          credentials: "same-origin"
        });

        if (res.status === 401) {
          track.classList.add("warning");
          track.textContent = "請先登入以接收緊急通知";
          return;
        }

        if (!res.ok) {
          track.classList.add("warning");
          track.textContent = "緊急通知讀取失敗";
          return;
        }

        const data = await res.json();
        const items = Array.isArray(data.items) ? data.items : [];

        if (!items.length) {
          const autoLeaveReminder = buildAutoLeaveReminder();

          if (autoLeaveReminder) {
            track.classList.add("warning");
            track.textContent = autoLeaveReminder;
          } else {
            track.classList.remove("warning");
            track.textContent = "目前沒有緊急通知";
          }

          return;
        }

        track.classList.add("warning");
        track.textContent = items.map(function (item) {
          const title = item.title || "緊急通知";
          const message = item.message || "";
          return "【" + title + "】" + message;
        }).join("　｜　");

      } catch (err) {
        track.classList.add("warning");
        track.textContent = "緊急通知讀取失敗";
      }
    }

async function loadTickets() {
      const list = document.getElementById("list");

      try {
        if (list) {
          list.innerHTML = '<div class="empty">\u6d3e\u5de5\u6848\u4ef6\u8b80\u53d6\u4e2d...</div>';
        }

        const res = await fetch("/api/app/dispatch/tickets?ts=" + Date.now(), {
          cache: "no-store",
          credentials: "same-origin"
        });

        if (res.status === 401) {
          if (list) {
            list.innerHTML = '<div class="empty">\u767b\u5165\u72c0\u614b\u5df2\u5931\u6548\uff0c\u8acb\u91cd\u65b0\u767b\u5165\u3002</div>';
          }
          setTimeout(function () {
            location.href = "/employee/login?next=/app/dispatch";
          }, 700);
          return;
        }

        if (!res.ok) {
          const errText = await res.text();
          if (list) {
            list.innerHTML = '<div class="empty">\u6d3e\u5de5\u8cc7\u6599\u8b80\u53d6\u5931\u6557\uff1aHTTP ' + res.status + '<br>' + esc(errText.slice(0, 260)) + '</div>';
          }
          return;
        }

        const data = await res.json();

        if (typeof renderDispatchProxyUserV1 === "function") {
          renderDispatchProxyUserV1(data.user || null);
        }

        allTickets = Array.isArray(data.items) ? data.items : [];

        refreshAreaFilter();
        renderTickets();

      } catch (err) {
        const msg = String(err && err.message ? err.message : err);
        if (list) {
          list.innerHTML = '<div class="empty">\u624b\u6a5f\u7aef\u6e32\u67d3\u932f\u8aa4\uff1a<br>' + esc(msg) + '</div>';
        }
      }
    }



function filteredTickets() {
      const keywordEl = document.getElementById("keyword");
      const keyword = keywordEl ? keywordEl.value.trim().toLowerCase() : "";

      const areaEl = document.getElementById("area_filter");
      const selectedArea = areaEl ? areaEl.value : "\u5168\u90e8";

      const today = todayText();

      return allTickets.filter(function (item) {
        if (selectedArea && selectedArea !== "\u5168\u90e8" && String(item.dispatch_area || "") !== selectedArea) return false;

        if (currentFilter === "\u4eca\u65e5" && ticketTodayValue(item) !== today) return false;
        if (currentFilter === "\u672a\u5b8c\u6210" && !isActive(item)) return false;
        if (currentFilter === "\u65bd\u5de5\u4e2d" && item.status !== "\u65bd\u5de5\u4e2d" && item.status !== "\u5df2\u9818\u53d6") return false;
        if (currentFilter === "\u5df2\u5b8c\u6210" && item.status !== "\u5df2\u5b8c\u6210" && item.status !== "\u5df2\u5b8c\u5de5") return false;

        if (keyword) {
          const hay = [
            item.customer_name,
            item.contact_name,
            item.contact_phone,
            item.service_address,
            item.case_type,
            item.status,
            item.assigned_engineer,
            item.dispatch_area
          ].join(" ").toLowerCase();

          if (!hay.includes(keyword)) return false;
        }

        return true;
      });
    }


function refreshAreaFilter() {
      const areaEl = document.getElementById("area_filter");
      if (!areaEl) return;

      const current = areaEl.value || "\u5168\u90e8";

      const areas = Array.from(new Set(
        allTickets.map(function (item) {
          return String(item.dispatch_area || "").trim();
        }).filter(Boolean)
      )).sort();

      areaEl.innerHTML = '<option value="\\u5168\\u90e8">\\u5168\\u90e8\\u5340\\u57df</option>' + areas.map(function (area) {
        return '<option value="' + esc(area) + '">' + esc(area) + '</option>';
      }).join("");

      areaEl.value = areas.includes(current) ? current : "\u5168\u90e8";
    }



function renderStats() {
      const today = todayText();

      const todayCount = allTickets.filter(function (item) {
        return ticketTodayValue(item) === today;
      }).length;

      const activeCount = allTickets.filter(isActive).length;
      const totalCount = allTickets.length;

      const todayEl = document.getElementById("stat_today");
      const activeEl = document.getElementById("stat_active");
      const totalEl = document.getElementById("stat_total");

      if (todayEl) todayEl.textContent = todayCount;
      if (activeEl) activeEl.textContent = activeCount;
      if (totalEl) totalEl.textContent = totalCount;
    }


function renderTickets() {
      renderStats();

      const items = filteredTickets();
      const title = document.getElementById("section_title");
      const box = document.getElementById("list");

      if (title) {
        title.textContent = currentFilter + "\u6d3e\u5de5\u6848\u4ef6\uff5c" + items.length + " \u7b46";
      }

      if (!box) return;

      if (!items.length) {
        box.innerHTML = '<div class="empty">\u76ee\u524d\u6c92\u6709\u7b26\u5408\u689d\u4ef6\u7684\u6d3e\u5de5\u6848\u4ef6\u3002<br>API \u5df2\u8b80\u53d6 ' + allTickets.length + ' \u7b46\u3002</div>';
        return;
      }

      box.innerHTML = items.map(function (item) {
        const status = item.status || "-";
        const tone = statusTone(status);
        const customer = customerText(item);
        const type = item.case_type || "\u5176\u4ed6";
        const phone = phoneText(item);
        const address = addressText(item);
        const appointment = appointmentText(item);
        const engineer = engineerText(item);

        return `
          <article class="ticket-card ${tone}" data-ticket-id="${Number(item.id || 0)}" onclick="openTicketPreview(${Number(item.id || 0)})">
            <div class="ticket-top">
              <div class="ticket-main">
                <div class="ticket-customer">${esc(customer)}</div>
                <div class="ticket-type">${esc(type)}</div>
              </div>
              <span class="status-pill">${esc(status)}</span>
            </div>

            <div class="ticket-phone">${esc(phone)}</div>
            <div class="ticket-address">${esc(address)}</div>

            <div class="ticket-footer">
              <div class="ticket-time">\u7d04\u5de5\uff1a${esc(appointment)}</div>
              <div class="ticket-engineer">${esc(engineer)}</div>
            </div>
          </article>
        `;
      }).join("");
    }



    
/* XN_APP_WORKFLOW_PAGES_JS_V1 */

let currentTicketId = null;
let signaturePadReady = false;
let signatureHasInk = false;

function currentTicket() {
      return allTickets.find(function (item) {
        return Number(item.id || 0) === Number(currentTicketId || 0);
      }) || null;
    }

function moneyText(value) {
      const n = Number(value || 0);
      if (!Number.isFinite(n)) return "0";
      return Math.round(n).toLocaleString("zh-TW");
    }

function showListPage() {
      currentTicketId = null;

      const statGrid = document.querySelector(".stat-grid");
      const filterRow = document.querySelector(".filter-row");
      const keyword = document.getElementById("keyword");
      const areaFilter = document.getElementById("area_filter");
      const sectionTitle = document.getElementById("section_title");
      const list = document.getElementById("list");
      const detail = document.getElementById("ticket_detail_page");
      const finish = document.getElementById("ticket_finish_page");
      const create = document.getElementById("ticket_create_page");

      if (statGrid) statGrid.style.display = "";
      if (filterRow) filterRow.style.display = "";
      if (keyword) keyword.style.display = "";
      if (areaFilter) areaFilter.style.display = "";
      if (sectionTitle) sectionTitle.style.display = "";
      if (list) list.style.display = "";

      if (detail) detail.classList.remove("active");
      if (finish) finish.classList.remove("active");
      if (create) create.classList.remove("active");

      renderTickets();
      window.scrollTo({top: 0, behavior: "smooth"});
    }


function showDetailPage() {
      const statGrid = document.querySelector(".stat-grid");
      const filterRow = document.querySelector(".filter-row");
      const keyword = document.getElementById("keyword");
      const areaFilter = document.getElementById("area_filter");
      const sectionTitle = document.getElementById("section_title");
      const list = document.getElementById("list");
      const detail = document.getElementById("ticket_detail_page");
      const finish = document.getElementById("ticket_finish_page");
      const create = document.getElementById("ticket_create_page");

      if (statGrid) statGrid.style.display = "none";
      if (filterRow) filterRow.style.display = "none";
      if (keyword) keyword.style.display = "none";
      if (areaFilter) areaFilter.style.display = "none";
      if (sectionTitle) sectionTitle.style.display = "none";
      if (list) list.style.display = "none";

      if (detail) detail.classList.add("active");
      if (finish) finish.classList.remove("active");
      if (create) create.classList.remove("active");

      window.scrollTo({top: 0, behavior: "smooth"});
    }


function showFinishPage() {
      const detail = document.getElementById("ticket_detail_page");
      const finish = document.getElementById("ticket_finish_page");
      const create = document.getElementById("ticket_create_page");

      if (detail) detail.classList.remove("active");
      if (finish) finish.classList.add("active");
      if (create) create.classList.remove("active");

      renderFinishPage();
      window.scrollTo({top: 0, behavior: "smooth"});
    }


function navigationAddress(item) {
      return item.navigation_address || item.building_address || item.service_address || "";
    }

function callCustomer(item) {
      const phone = phoneText(item).replace(/[^0-9+]/g, "");
      if (!phone) {
        alert("\u6c92\u6709\u53ef\u64a5\u6253\u7684\u96fb\u8a71\u3002");
        return;
      }
      location.href = "tel:" + phone;
    }

function navigateCustomer(item) {
      const addr = navigationAddress(item);
      if (!addr) {
        alert("\u6c92\u6709\u53ef\u5c0e\u822a\u7684\u5730\u5740\u3002");
        return;
      }
      window.open("https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(addr), "_blank");
    }

function dispatchPriceHtml(item) {
      const install = item.install_detail || null;
      const ret = item.return_detail || null;

      function feePart(label, value) {
        const n = Number(value || 0);
        if (!n) return "";
        return `${label} NT$ ${moneyText(n)}`;
      }

      if (install) {
        const construction = Number(install.construction_fee || install.install_fee || 0);
        const deposit = Number(install.deposit_amount || 0);
        const other1 = Number(install.other_fee_1 || 0);
        const other2 = Number(install.other_fee_2 || 0);
        const m1 = Number(install.monthly_fee_1 || install.monthly_fee || 0);
        const m2 = Number(install.monthly_fee_2 || 0);
        const m3 = Number(install.monthly_fee_3 || 0);
        const months = Number(install.month_count || 1);
        const monthlySum = m1 + m2 + m3;
        const calculated = construction + deposit + other1 + other2 + (monthlySum * months);
        const total = Number(install.total_amount || calculated);

        const parts = [
          feePart("\u5b89\u88dd\u8cbb", construction),
          feePart("\u62bc\u91d1", deposit),
          feePart("\u5176\u4ed6\u8cbb\u7528 1", other1),
          feePart("\u5176\u4ed6\u8cbb\u7528 2", other2)
        ].filter(Boolean);

        const monthlyParts = [
          feePart("\u6708\u79df\u8cbb 1", m1),
          feePart("\u6708\u79df\u8cbb 2", m2),
          feePart("\u6708\u79df\u8cbb 3", m3)
        ].filter(Boolean);

        let formula = "";

        if (parts.length) {
          formula += parts.join(" + ");
        }

        if (monthlyParts.length) {
          if (formula) formula += " + ";
          formula += "(" + monthlyParts.join(" + ") + ") \u00d7 " + moneyText(months) + " \u6708";
        }

        if (!formula) {
          return '<div class="workflow-note">\u672c\u6848\u4ef6\u6c92\u6709\u6d3e\u5de5\u50f9\u683c\u3002</div>';
        }

        return `
          <div class="compact-price-formula">
            <div class="price-formula-line">${esc(formula)}</div>
            <div class="price-formula-total">= NT$ ${moneyText(total)} \u5143</div>
          </div>
        `;
      }

      if (ret) {
        const deposit = Number(ret.deposit_amount || 0);
        const refund = Number(ret.refund_amount || 0);
        const deduction = Number(ret.deduction_amount || 0);
        const device = Number(ret.device_fee || 0);
        const cleaning = Number(ret.cleaning_fee || 0);
        const other = Number(ret.other_fee || 0);
        const total = Number(ret.total_amount || 0);

        const parts = [
          feePart("\u62bc\u91d1", deposit),
          feePart("\u9000\u8cbb\u91d1\u984d", refund),
          feePart("\u6263\u6b3e\u91d1\u984d", deduction),
          feePart("\u8a2d\u5099\u8cbb", device),
          feePart("\u6e05\u6f54\u8cbb", cleaning),
          feePart("\u5176\u4ed6\u8cbb\u7528", other)
        ].filter(Boolean);

        if (!parts.length && !total) {
          return '<div class="workflow-note">\u672c\u6848\u4ef6\u6c92\u6709\u6d3e\u5de5\u50f9\u683c\u3002</div>';
        }

        return `
          <div class="compact-price-formula">
            <div class="price-formula-line">${esc(parts.join(" + ") || "\u9000\u6a5f\u7d50\u7b97")}</div>
            <div class="price-formula-total">= NT$ ${moneyText(total)} \u5143</div>
          </div>
        `;
      }

      return '<div class="workflow-note">\u672c\u6848\u4ef6\u6c92\u6709\u6d3e\u5de5\u50f9\u683c\u3002</div>';
    }



function renderDetailPage(item) {
      currentTicketId = Number(item.id || 0);

      const box = document.getElementById("ticket_detail_content");
      if (!box) return;

      const status = item.status || "-";
      const customer = customerText(item);
      const type = item.case_type || "\u5176\u4ed6";
      const phone = phoneText(item);
      const address = addressText(item);
      const appointment = appointmentText(item);
      const engineer = engineerText(item);
      const area = item.dispatch_area || "-";
      const desc = item.description || "-";
      const note = item.internal_note || "-";

      box.innerHTML = `
        <div class="workflow-card">
          <div class="workflow-top">
            <div>
              <div class="workflow-name">${esc(customer)}</div>
              <div class="workflow-type">${esc(type)}</div>
            </div>
            <div class="workflow-status">${esc(status)}</div>
          </div>

          <div class="workflow-info">
            <div class="workflow-row"><div class="label">\u96fb\u8a71</div><div>${esc(phone)}</div></div>
            <div class="workflow-row"><div class="label">\u5730\u5740</div><div class="workflow-address">${esc(address)}</div></div>
            <div class="workflow-row"><div class="label">\u7d04\u5de5</div><div>${esc(appointment)}</div></div>
            <div class="workflow-row"><div class="label">\u5340\u57df</div><div>${esc(area)}</div></div>
            <div class="workflow-row"><div class="label">\u5de5\u7a0b\u5e2b</div><div>${esc(engineer)}</div></div>
          </div>
        </div>

        <details class="workflow-section" open>
          <summary>\u6848\u4ef6\u5167\u5bb9</summary>
          <div class="workflow-section-body">
            <div class="workflow-row"><div class="label">\u8aaa\u660e</div><div class="workflow-note">${esc(desc)}</div></div>
            <div style="height:10px"></div>
            <div class="workflow-row"><div class="label">\u5167\u90e8\u5099\u8a3b</div><div class="workflow-note">${esc(note)}</div></div>
          </div>
        </details>

        <details class="workflow-section" open>
          <summary>\u6d3e\u5de5\u50f9\u683c\uff08\u53ea\u8b80\uff09</summary>
          <div class="workflow-section-body">
            ${dispatchPriceHtml(item)}
          </div>
        </details>

        <details class="workflow-section" open>
          <summary>\u65bd\u5de5\u5b89\u6392</summary>
          <div class="workflow-section-body">
            <div class="form-grid">
              <div class="work-date-time-row">
                <div class="form-row">
                  <label>\u65bd\u5de5\u65e5\u671f</label>
                  <input id="work_date" type="date" value="${esc(item.appointment_date || "")}" oninput="updateClaimButtonState()">
                </div>
                <div class="form-row">
                  <label>\u65bd\u5de5\u6642\u9593</label>
                  <input id="work_time" type="time" value="${esc(item.appointment_time || "")}" oninput="updateClaimButtonState()">
                </div>
              </div>
              <div class="preview-text">\u65bd\u5de5\u65e5\u671f\u8207\u6642\u9593\u90fd\u586b\u5beb\u5f8c\uff0c\u624d\u80fd\u9818\u53d6\u6848\u4ef6\u3002</div>
            </div>
          </div>
        </details>

        <div class="action-panel workflow-detail-actions">
          <div class="action-row">
            <button class="action-btn blue" onclick="callCustomer(currentTicket())">\u4e00\u9375\u64a5\u865f</button>
            <button class="action-btn orange" onclick="navigateCustomer(currentTicket())">\u4e00\u9375\u5c0e\u822a</button>
          </div>
          <div class="action-row">
            <button id="claim_btn" class="action-btn green" onclick="claimTicketPreview()" disabled>\u9818\u53d6\u6848\u4ef6</button>
            <button class="action-btn gray" onclick="showListPage()">\u8fd4\u56de\u5217\u8868</button>
          </div>
          <button class="action-btn blue next-btn" onclick="showFinishPage()">\u4e0b\u4e00\u6b65</button>
        </div>
      `;

      updateClaimButtonState();
      showDetailPage();
    }



function updateClaimButtonState() {
      const btn = document.getElementById("claim_btn");
      const d = document.getElementById("work_date");
      const t = document.getElementById("work_time");
      if (!btn || !d || !t) return;
      btn.disabled = !(d.value && t.value);
    }

function claimTicketPreview() {
      alert("\u4e0b\u4e00\u968e\u6bb5\u6703\u63a5\u4e0a\u9818\u53d6\u6848\u4ef6 API\uff0c\u76ee\u524d\u5148\u78ba\u8a8d\u756b\u9762\u6d41\u7a0b\u3002");
    }

function actualPriceDefaults(item) {
      const install = item.install_detail || null;
      const ret = item.return_detail || null;

      if (install) {
        return {
          construction_fee: Number(install.construction_fee || install.install_fee || 0),
          deposit_amount: Number(install.deposit_amount || 0),
          other_fee_1: Number(install.other_fee_1 || 0),
          other_fee_2: Number(install.other_fee_2 || 0),
          monthly_fee_1: Number(install.monthly_fee_1 || install.monthly_fee || 0),
          monthly_fee_2: Number(install.monthly_fee_2 || 0),
          monthly_fee_3: Number(install.monthly_fee_3 || 0),
          total_amount: Number(install.total_amount || 0)
        };
      }

      if (ret) {
        return {
          deposit_amount: Number(ret.deposit_amount || 0),
          refund_amount: Number(ret.refund_amount || 0),
          deduction_amount: Number(ret.deduction_amount || 0),
          device_fee: Number(ret.device_fee || 0),
          cleaning_fee: Number(ret.cleaning_fee || 0),
          other_fee: Number(ret.other_fee || 0),
          total_amount: Number(ret.total_amount || 0)
        };
      }

      return { total_amount: 0 };
    }

function renderFinishPriceForm(item) {
      const d = actualPriceDefaults(item);
      const isInstall = !!item.install_detail;
      const isReturn = !!item.return_detail;

      if (isInstall) {
        return `
          <div class="form-grid">
            <div class="two-cols">
              <div class="form-row"><label>\u5b89\u88dd\u8cbb</label><input id="actual_construction_fee" type="number" value="${d.construction_fee}"></div>
              <div class="form-row"><label>\u62bc\u91d1</label><input id="actual_deposit_amount" type="number" value="${d.deposit_amount}"></div>
            </div>
            <div class="two-cols">
              <div class="form-row"><label>\u5176\u4ed6\u8cbb\u7528 1</label><input id="actual_other_fee_1" type="number" value="${d.other_fee_1}"></div>
              <div class="form-row"><label>\u5176\u4ed6\u8cbb\u7528 2</label><input id="actual_other_fee_2" type="number" value="${d.other_fee_2}"></div>
            </div>
            <div class="two-cols">
              <div class="form-row"><label>\u6708\u79df\u8cbb 1</label><input id="actual_monthly_fee_1" type="number" value="${d.monthly_fee_1}"></div>
              <div class="form-row"><label>\u6708\u79df\u8cbb 2</label><input id="actual_monthly_fee_2" type="number" value="${d.monthly_fee_2}"></div>
            </div>
            <div class="two-cols">
              <div class="form-row"><label>\u6708\u79df\u8cbb 3</label><input id="actual_monthly_fee_3" type="number" value="${d.monthly_fee_3}"></div>
              <div class="form-row"><label>\u81e8\u6642\u8ffd\u52a0\u8cbb\u7528</label><input id="actual_extra_fee" type="number" value="0"></div>
            </div>
          </div>
        `;
      }

      if (isReturn) {
        return `
          <div class="form-grid">
            <div class="two-cols">
              <div class="form-row"><label>\u62bc\u91d1</label><input id="actual_return_deposit" type="number" value="${d.deposit_amount}"></div>
              <div class="form-row"><label>\u9000\u8cbb\u91d1\u984d</label><input id="actual_refund_amount" type="number" value="${d.refund_amount}"></div>
            </div>
            <div class="two-cols">
              <div class="form-row"><label>\u6263\u6b3e\u91d1\u984d</label><input id="actual_deduction_amount" type="number" value="${d.deduction_amount}"></div>
              <div class="form-row"><label>\u8a2d\u5099\u8cbb</label><input id="actual_device_fee" type="number" value="${d.device_fee}"></div>
            </div>
            <div class="two-cols">
              <div class="form-row"><label>\u6e05\u6f54\u8cbb</label><input id="actual_cleaning_fee" type="number" value="${d.cleaning_fee}"></div>
              <div class="form-row"><label>\u81e8\u6642\u8ffd\u52a0\u8cbb\u7528</label><input id="actual_extra_fee" type="number" value="${d.other_fee}"></div>
            </div>
          </div>
        `;
      }

      return `
        <div class="form-grid">
          <div class="form-row">
            <label>\u5be6\u969b\u7e3d\u91d1\u984d</label>
            <input id="actual_total_amount" type="number" value="${d.total_amount}">
          </div>
          <div class="form-row">
            <label>\u81e8\u6642\u8ffd\u52a0\u8cbb\u7528</label>
            <input id="actual_extra_fee" type="number" value="0">
          </div>
        </div>
      `;
    }

function renderFinishPage() {
      const item = currentTicket();
      if (!item) return showListPage();

      const box = document.getElementById("ticket_finish_content");
      if (!box) return;

      const workDate = document.getElementById("work_date") ? document.getElementById("work_date").value : "";
      const workTime = document.getElementById("work_time") ? document.getElementById("work_time").value : "";

      box.innerHTML = `
        <div class="workflow-card">
          <div class="workflow-top">
            <div>
              <div class="workflow-name">${esc(customerText(item))}</div>
              <div class="workflow-type">${esc(item.case_type || "\u5176\u4ed6")}</div>
            </div>
            <div class="workflow-status">${esc(item.status || "-")}</div>
          </div>
          <div class="workflow-info">
            <div class="workflow-row"><div class="label">\u96fb\u8a71</div><div>${esc(phoneText(item))}</div></div>
            <div class="workflow-row"><div class="label">\u5730\u5740</div><div class="workflow-address">${esc(addressText(item))}</div></div>
          </div>
        </div>

        <details class="workflow-section" open>
          <summary>\u5be6\u969b\u50f9\u683c\uff08\u53ef\u4fee\u6539\uff09</summary>
          <div class="workflow-section-body">
            ${renderFinishPriceForm(item)}
          </div>
        </details>

        <details class="workflow-section" open>
          <summary>\u4f7f\u7528\u671f\u9593</summary>
          <div class="workflow-section-body">
            <div class="form-grid">
              <div class="work-date-time-row">
                <div class="form-row"><label>\u958b\u59cb\u65e5</label><input id="service_start_date" type="date"></div>
                <div class="form-row"><label>\u5230\u671f\u65e5</label><input id="service_end_date" type="date"></div>
              </div>
              <div class="work-date-time-row">
                <div class="form-row"><label>\u7e3d\u5171\u6708\u6578</label><input id="service_months" type="number" min="0" value="1"></div>
                <div class="form-row"><label>\u65bd\u5de5\u6642\u9593</label><input id="final_work_time" type="time" value="${esc(workTime)}"></div>
              </div>
              <div class="form-row"><label>\u65bd\u5de5\u65e5\u671f</label><input id="final_work_date" type="date" value="${esc(workDate)}"></div>
              <div class="preview-text">\u5be6\u969b\u5b8c\u5de5\u6642\u9593\u6703\u5728\u4e00\u9375\u9001\u51fa\u6642\u7531\u7cfb\u7d71\u81ea\u52d5\u5beb\u5165\u3002</div>
            </div>
          </div>
        </details>

        <details class="workflow-section" open>
          <summary>\u65bd\u5de5\u5099\u8a3b</summary>
          <div class="workflow-section-body">
            <div class="form-row">
              <label>\u5b8c\u5de5\u5099\u8a3b</label>
              <textarea id="completion_note" placeholder="\u8acb\u8f38\u5165\u5be6\u969b\u65bd\u5de5\u5167\u5bb9\u3001\u7570\u5e38\u72c0\u6cc1\u6216\u88dc\u5145\u8aaa\u660e"></textarea>
            </div>
          </div>
        </details>

        <details class="workflow-section" open>
          <summary>\u65bd\u5de5\u7167\u7247</summary>
          <div class="workflow-section-body">
            <div class="form-grid">
              <div class="photo-input">
                <label>\u65bd\u5de5\u524d\u7167\u7247</label>
                <input id="before_photos" type="file" accept="image/*" multiple>
                <div class="preview-text">\u53ef\u4e0a\u50b3\u65bd\u5de5\u524d\u7167\u7247\u3002</div>
              </div>
              <div class="photo-input">
                <label>\u65bd\u5de5\u5f8c\u7167\u7247</label>
                <input id="after_photos" type="file" accept="image/*" multiple>
                <div class="preview-text">\u53ef\u4e0a\u50b3\u65bd\u5de5\u5f8c\u7167\u7247\u3002</div>
              </div>
            </div>
          </div>
        </details>

        <details class="workflow-section" open>
          <summary>\u5ba2\u6236\u7c3d\u540d</summary>
          <div class="workflow-section-body">
            <div class="signature-box">
              <canvas id="customer_signature_canvas"></canvas>
            </div>
            <div class="action-row" style="margin-top:10px">
              <button class="action-btn gray" onclick="clearSignature()">\u6e05\u9664\u7c3d\u540d</button>
              <button class="action-btn blue" onclick="confirmSignature()">\u78ba\u8a8d\u7c3d\u540d</button>
            </div>
          </div>
        </details>

        <div class="action-panel">
          <button class="action-btn green" onclick="submitFinishPreview()">\u4e00\u9375\u9001\u51fa</button>
          <button class="action-btn gray" onclick="showDetailPage()">\u8fd4\u56de\u6848\u4ef6</button>
        </div>
      `;

      setupSignatureCanvas();
    }



function setupSignatureCanvas() {
      const canvas = document.getElementById("customer_signature_canvas");
      if (!canvas) return;

      const rect = canvas.getBoundingClientRect();
      canvas.width = Math.max(300, Math.floor(rect.width));
      canvas.height = 180;

      const ctx = canvas.getContext("2d");
      ctx.lineWidth = 3;
      ctx.lineCap = "round";
      ctx.strokeStyle = "#0f172a";

      let drawing = false;

      function point(e) {
        const r = canvas.getBoundingClientRect();
        const touch = e.touches && e.touches.length ? e.touches[0] : e;
        return { x: touch.clientX - r.left, y: touch.clientY - r.top };
      }

      function start(e) {
        e.preventDefault();
        drawing = true;
        const p = point(e);
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
      }

      function move(e) {
        if (!drawing) return;
        e.preventDefault();
        const p = point(e);
        ctx.lineTo(p.x, p.y);
        ctx.stroke();
        signatureHasInk = true;
      }

      function end(e) {
        drawing = false;
      }

      canvas.onmousedown = start;
      canvas.onmousemove = move;
      canvas.onmouseup = end;
      canvas.onmouseleave = end;

      canvas.ontouchstart = start;
      canvas.ontouchmove = move;
      canvas.ontouchend = end;

      signatureHasInk = false;
    }

function clearSignature() {
      const canvas = document.getElementById("customer_signature_canvas");
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      signatureHasInk = false;
    }

function confirmSignature() {
      if (!signatureHasInk) {
        alert("\u8acb\u5148\u8acb\u5ba2\u6236\u7c3d\u540d\u3002");
        return;
      }
      alert("\u7c3d\u540d\u5df2\u78ba\u8a8d\u3002");
    }

function submitFinishPreview() {
      alert("\u4e0b\u4e00\u968e\u6bb5\u6703\u63a5\u4e0a\u4e00\u9375\u9001\u51fa API\uff0c\u9001\u51fa\u5f8c\u624d\u6703\u66f4\u65b0\u8cc7\u6599\u5eab\u3002");
    }

/* XN_APP_WORKFLOW_PAGES_JS_V1_END */







/* XN_APP_CREATE_PAGE_JS_V1 */

let createBuildingDirectory = [];

function createVal(id) {
      const el = document.getElementById(id);
      return el ? String(el.value || "").trim() : "";
    }

function createNumber(id) {
      const raw = createVal(id).replace(/[^\d.-]/g, "");
      const n = Number(raw || 0);
      return Number.isFinite(n) ? n : 0;
    }

function createMoney(n) {
      const v = Number(n || 0);
      return Number.isFinite(v) ? v.toLocaleString("zh-TW") : "0";
    }

function createIsHouse(value) {
      const s = String(value || "").trim().toUpperCase();
      return s === "HOUSE" || s.startsWith("HOUSE-") || s === "\u900f\u5929";
    }

function createNormalizeBuildingName(value) {
      const s = String(value || "").trim();
      if (!s) return "";
      if (createIsHouse(s)) return "\u900f\u5929";
      return s;
    }

async function loadCreateBuildingDirectory() {
      try {
        const res = await fetch("/api/admin/buildings?ts=" + Date.now(), {
          cache: "no-store",
          credentials: "same-origin"
        });

        if (!res.ok) throw new Error("building api failed");

        const data = await res.json();
        if (Array.isArray(data)) {
          createBuildingDirectory = data;
        } else if (Array.isArray(data.items)) {
          createBuildingDirectory = data.items;
        } else if (Array.isArray(data.buildings)) {
          createBuildingDirectory = data.buildings;
        } else {
          createBuildingDirectory = [];
        }
      } catch (err) {
        console.warn("load buildings failed", err);
        createBuildingDirectory = [];
      }
    }

function populateCreateBuildingList() {
      const area = createVal("create_dispatch_area");
      const select = document.getElementById("create_building_select");
      if (!select) return;

      const rows = [];
      const seen = new Set();

      createBuildingDirectory.forEach(function (b) {
        const bArea = String(b.area || b.dispatch_area || "").trim();
        if (area && bArea && bArea !== area) return;

        const name = String(b.name || b.building_name || b.title || "").trim();
        if (!name) return;

        if (seen.has(name)) return;
        seen.add(name);

        rows.push({
          name: name,
          area: bArea,
          address: String(b.address || b.raw_address || "").trim()
        });
      });

      select.innerHTML = "";
      select.appendChild(new Option("\u8acb\u9078\u64c7\u5927\u6a13", ""));
      select.appendChild(new Option("\u900f\u5929", "HOUSE"));

      rows.sort(function (a, b) {
        return a.name.localeCompare(b.name, "zh-Hant");
      }).forEach(function (row) {
        const opt = new Option(row.name, row.name);
        opt.dataset.address = row.address || "";
        select.appendChild(opt);
      });

      populateCreateCustomerList();
    }

function populateCreateCustomerList() {
      const area = createVal("create_dispatch_area");
      const building = createVal("create_building_select");
      const select = document.getElementById("create_customer_picker");

      if (!select) return;

      select.innerHTML = "";
      select.appendChild(new Option("\u8acb\u9078\u64c7\u5ba2\u6236", ""));

      if (!area || !building) return;

      (allTickets || []).forEach(function (item, index) {
        if (String(item.dispatch_area || "") !== area) return;

        const itemBuildingName = createNormalizeBuildingName(
          item.building_name ||
          item.building_title ||
          item.community_name ||
          item.building ||
          item.building_no ||
          ""
        );

        const selectedName = createNormalizeBuildingName(building);

        if (selectedName === "\u900f\u5929") {
          if (itemBuildingName !== "\u900f\u5929") return;
        } else {
          const itemAddress = String(item.service_address || item.address || "");
          if (itemBuildingName !== selectedName && !itemAddress.includes(selectedName)) return;
        }

        const customer = String(item.customer_name || item.contact_name || "").trim();
        const phone = String(item.contact_phone || item.phone || "").trim();
        const address = String(item.service_address || item.address || "").trim();

        if (!customer && !phone && !address) return;

        const label = [customer, phone, address].filter(Boolean).join(" / ");
        const opt = new Option(label, String(index));
        select.appendChild(opt);
      });
    }

function applyCreateBuildingSelect() {
      const select = document.getElementById("create_building_select");
      const address = document.getElementById("create_service_address");

      if (!select) return;

      const selected = select.options[select.selectedIndex];
      const rawAddress = selected ? String(selected.dataset.address || "") : "";

      if (address && rawAddress && !createIsHouse(select.value)) {
        address.placeholder = "\u5927\u6a13\u5730\u5740\uff1a" + rawAddress + "\uff0c\u8acb\u88dc\u6a13\u5c64\u9580\u724c";
      } else if (address) {
        address.placeholder = "\u8acb\u8f38\u5165\u5b8c\u6574\u4f4f\u5740";
      }

      populateCreateCustomerList();
    }

function applyCreateCustomerPicker() {
      const picker = document.getElementById("create_customer_picker");
      if (!picker || !picker.value) return;

      const item = (allTickets || [])[Number(picker.value)];
      if (!item) return;

      const name = document.getElementById("create_customer_name");
      const phone = document.getElementById("create_phone");
      const address = document.getElementById("create_service_address");

      if (name) name.value = item.customer_name || item.contact_name || "";
      if (phone) phone.value = item.contact_phone || item.phone || "";
      if (address) address.value = item.service_address || item.address || "";
    }

function updateCreateInstallPreview() {
      const box = document.getElementById("create_install_preview");
      if (!box) return;

      const installFee = createNumber("create_install_fee");
      const deposit = createNumber("create_install_deposit");
      const monthly1 = createNumber("create_monthly_fee_1");
      const monthly2 = createNumber("create_monthly_fee_2");
      const monthly3 = createNumber("create_monthly_fee_3");
      const months = Math.max(1, Number(createVal("create_install_month_count") || 1));
      const other1 = createNumber("create_other_fee_1");
      const other2 = createNumber("create_other_fee_2");

      const total = installFee + deposit + other1 + other2 + ((monthly1 + monthly2 + monthly3) * months);

      const parts = [];
      if (installFee) parts.push("\u5b89\u88dd\u8cbb " + createMoney(installFee));
      if (deposit) parts.push("\u62bc\u91d1 " + createMoney(deposit));
      if (other1) parts.push("\u5176\u4ed6\u8cbb\u75281 " + createMoney(other1));
      if (other2) parts.push("\u5176\u4ed6\u8cbb\u75282 " + createMoney(other2));

      const monthParts = [];
      if (monthly1) monthParts.push("\u6708\u79df\u8cbb1 " + createMoney(monthly1));
      if (monthly2) monthParts.push("\u6708\u79df\u8cbb2 " + createMoney(monthly2));
      if (monthly3) monthParts.push("\u6708\u79df\u8cbb3 " + createMoney(monthly3));

      let formula = parts.join(" + ");
      if (monthParts.length) {
        if (formula) formula += " + ";
        formula += "(" + monthParts.join(" + ") + ") \u00d7 " + months + "\u6708";
      }

      if (!formula) formula = "\u5c1a\u672a\u8f38\u5165\u6d3e\u5de5\u50f9\u683c";

      box.innerHTML = `
        <div>${formula}</div>
        <div class="create-price-total">\u5408\u8a08\uff1aNT$ ${createMoney(total)} \u5143</div>
      `;
    }

function updateCreateRepairPreview() {
      const box = document.getElementById("create_repair_preview");
      if (!box) return;

      const fee1 = createNumber("create_repair_fee_1");
      const fee2 = createNumber("create_repair_fee_2");
      const total = fee1 + fee2;

      const parts = [];
      if (fee1) parts.push("\u5176\u4ed6\u6536\u8cbb1 " + createMoney(fee1));
      if (fee2) parts.push("\u5176\u4ed6\u6536\u8cbb2 " + createMoney(fee2));

      box.innerHTML = `
        <div>${parts.length ? parts.join(" + ") : "\u5c1a\u672a\u8f38\u5165\u7dad\u4fee\u6536\u8cbb"}</div>
        <div class="create-price-total">\u5408\u8a08\uff1aNT$ ${createMoney(total)} \u5143</div>
      `;
    }

function toggleCreatePriceFields() {
      const type = createVal("create_case_type");
      const installBox = document.getElementById("create_install_section");
      const repairBox = document.getElementById("create_repair_section");
      const returnBox = document.getElementById("create_return_section");

      if (installBox) installBox.style.display = type === "\u88dd\u6a5f" ? "" : "none";
      if (repairBox) repairBox.style.display = type === "\u7dad\u4fee" ? "" : "none";
      if (returnBox) returnBox.style.display = type === "\u9000\u6a5f" ? "" : "none";

      updateCreateInstallPreview();
      updateCreateRepairPreview();
    }

function buildCreatePayloadPreview() {
      const caseType = createVal("create_case_type");
      const buildingSelect = createVal("create_building_select");
      const maintenanceFee1 = createNumber("create_repair_fee_1");
      const maintenanceFee2 = createNumber("create_repair_fee_2");

      const extraFees = {
        maintenance_fee_1: maintenanceFee1,
        maintenance_fee_2: maintenanceFee2,
        maintenance_total: maintenanceFee1 + maintenanceFee2
      };

      const payload = {
        dispatch_area: createVal("create_dispatch_area"),
        case_type: caseType,
        customer_name: createVal("create_customer_name"),
        contact_name: createVal("create_customer_name"),
        contact_phone: createVal("create_phone"),
        service_address: createVal("create_service_address"),
        appointment_date: createVal("create_appointment_date") || null,
        appointment_time: createVal("create_appointment_time") || null,
        assigned_engineer: createVal("create_engineer") || null,
        building_no: createIsHouse(buildingSelect) ? "HOUSE" : buildingSelect,
        description: createVal("create_description"),
        internal_note: createVal("create_internal_note"),
        extra_fees_data: JSON.stringify(extraFees)
      };

      if (caseType === "\u88dd\u6a5f") {
        const installFee = createNumber("create_install_fee");
        const deposit = createNumber("create_install_deposit");
        const monthly1 = createNumber("create_monthly_fee_1");
        const monthly2 = createNumber("create_monthly_fee_2");
        const monthly3 = createNumber("create_monthly_fee_3");
        const months = Math.max(1, Number(createVal("create_install_month_count") || 1));
        const other1 = createNumber("create_other_fee_1");
        const other2 = createNumber("create_other_fee_2");

        payload.install_detail = {
          construction_fee: installFee,
          deposit_amount: deposit,
          monthly_fee: monthly1 + monthly2 + monthly3,
          month_count: months,
          other_fee: other1 + other2,
          other_fee_note: JSON.stringify({
            other_fee_1: other1,
            other_fee_2: other2,
            monthly_fee_1: monthly1,
            monthly_fee_2: monthly2,
            monthly_fee_3: monthly3
          })
        };
      }

      if (caseType === "\u9000\u6a5f") {
        payload.return_detail = {
          deposit_amount: createNumber("create_return_deposit"),
          other_fee: createNumber("create_return_other"),
          other_fee_note: JSON.stringify({
            refund_amount: createNumber("create_return_refund"),
            deduction_amount: createNumber("create_return_deduction")
          })
        };
      }

      return payload;
    }

function renderCreatePage() {
      const box = document.getElementById("ticket_create_content");
      if (!box) return;

      box.innerHTML = `
        <h2 class="create-page-title">\u65b0\u589e\u6848\u4ef6</h2>
        <div class="create-page-subtitle">\u624b\u6a5f\u7248\u6b04\u4f4d\u5c0d\u9f4a\u96fb\u8166\u7248\u65b0\u589e\u6848\u4ef6\u6d41\u7a0b\u3002</div>

        <div class="create-card">
          <div class="create-card-title">\u6848\u4ef6\u57fa\u672c\u8cc7\u6599</div>
          <div class="create-grid">
            <div class="create-two-cols">
              <div class="create-field">
                <label>\u5340\u57df</label>
                <select id="create_dispatch_area" onchange="populateCreateBuildingList()">
                  <option value="">\u8acb\u9078\u64c7</option>
                  <option value="\u6771\u5340">\u6771\u5340</option>
                  <option value="\u5317\u5340">\u5317\u5340</option>
                  <option value="\u5317\u53f0\u5357">\u5317\u53f0\u5357</option>
                  <option value="\u4ec1\u5fb7">\u4ec1\u5fb7</option>
                  <option value="\u6c38\u5eb7">\u6c38\u5eb7</option>
                  <option value="\u5b89\u5e73">\u5b89\u5e73</option>
                  <option value="\u5317\u9ad8">\u5317\u9ad8</option>
                  <option value="\u5357\u9ad8">\u5357\u9ad8</option>
                </select>
              </div>

              <div class="create-field">
                <label>\u6848\u4ef6\u985e\u578b</label>
                <select id="create_case_type" onchange="toggleCreatePriceFields()">
                  <option value="\u88dd\u6a5f">\u88dd\u6a5f</option>
                  <option value="\u7dad\u4fee">\u7dad\u4fee</option>
                  <option value="\u9000\u6a5f">\u9000\u6a5f</option>
                  <option value="\u5de1\u6aa2">\u5de1\u6aa2</option>
                  <option value="\u5176\u4ed6">\u5176\u4ed6</option>
                </select>
              </div>
            </div>

            <div class="create-field">
              <label>\u5de5\u7a0b\u5e2b</label>
              <select id="create_engineer">
                <option value="">\u672a\u6307\u6d3e</option>
              </select>
            </div>
          </div>
        </div>

        <div class="create-card">
          <div class="create-card-title">\u5ba2\u6236\u8207\u5730\u5740</div>
          <div class="create-grid">
            <div class="create-two-cols">
              <div class="create-field">
                <label>\u5ba2\u6236\u59d3\u540d</label>
                <input id="create_customer_name" placeholder="\u8acb\u8f38\u5165\u5ba2\u6236\u59d3\u540d">
              </div>

              <div class="create-field">
                <label>\u96fb\u8a71</label>
                <input id="create_phone" placeholder="\u8acb\u8f38\u5165\u96fb\u8a71" inputmode="tel">
              </div>
            </div>

            <div class="create-two-cols">
              <div class="create-field">
                <label>\u5927\u6a13\u540d\u55ae</label>
                <select id="create_building_select" onchange="applyCreateBuildingSelect()">
                  <option value="">\u8acb\u5148\u9078\u64c7\u5340\u57df</option>
                </select>
              </div>

              <div class="create-field">
                <label>\u65e2\u6709\u5ba2\u6236</label>
                <select id="create_customer_picker" onchange="applyCreateCustomerPicker()">
                  <option value="">\u8acb\u9078\u64c7\u5ba2\u6236</option>
                </select>
              </div>
            </div>

            <div class="create-field">
              <label>\u4f4f\u5740</label>
              <input id="create_service_address" placeholder="\u8acb\u8f38\u5165\u5b8c\u6574\u4f4f\u5740">
              <div class="create-help">\u9078\u64c7\u5340\u57df\u5f8c\u6703\u5217\u51fa\u5927\u6a13\u540d\u55ae\uff1b\u9078\u64c7\u65e2\u6709\u5ba2\u6236\u5f8c\u6703\u81ea\u52d5\u5e36\u5165\u8cc7\u6599\u3002</div>
            </div>
          </div>
        </div>

        <div class="create-card">
          <div class="create-card-title">\u7d04\u5de5\u6642\u9593</div>
          <div class="create-date-time-row">
            <div class="create-field">
              <label>\u7d04\u5de5\u65e5\u671f</label>
              <input id="create_appointment_date" type="date">
            </div>

            <div class="create-field">
              <label>\u7d04\u5de5\u6642\u9593</label>
              <input id="create_appointment_time" type="time">
            </div>
          </div>
        </div>

        <div id="create_install_section" class="create-card">
          <div class="create-card-title">\u88dd\u6a5f\u6d3e\u5de5\u50f9\u683c</div>
          <div class="create-grid">
            <div class="create-two-cols">
              <div class="create-field">
                <label>\u5b89\u88dd\u8cbb</label>
                <input id="create_install_fee" type="number" inputmode="decimal" value="0" oninput="updateCreateInstallPreview()">
              </div>
              <div class="create-field">
                <label>\u62bc\u91d1</label>
                <input id="create_install_deposit" type="number" inputmode="decimal" value="0" oninput="updateCreateInstallPreview()">
              </div>
            </div>

            <div class="create-two-cols">
              <div class="create-field">
                <label>\u6708\u79df\u8cbb1</label>
                <input id="create_monthly_fee_1" type="number" inputmode="decimal" value="0" oninput="updateCreateInstallPreview()">
              </div>
              <div class="create-field">
                <label>\u6708\u79df\u8cbb2</label>
                <input id="create_monthly_fee_2" type="number" inputmode="decimal" value="0" oninput="updateCreateInstallPreview()">
              </div>
            </div>

            <div class="create-two-cols">
              <div class="create-field">
                <label>\u6708\u79df\u8cbb3</label>
                <input id="create_monthly_fee_3" type="number" inputmode="decimal" value="0" oninput="updateCreateInstallPreview()">
              </div>
              <div class="create-field">
                <label>\u6708\u6578</label>
                <input id="create_install_month_count" type="number" inputmode="numeric" min="1" value="1" oninput="updateCreateInstallPreview()">
              </div>
            </div>

            <div class="create-two-cols">
              <div class="create-field">
                <label>\u5176\u4ed6\u8cbb\u75281</label>
                <input id="create_other_fee_1" type="number" inputmode="decimal" value="0" oninput="updateCreateInstallPreview()">
              </div>
              <div class="create-field">
                <label>\u5176\u4ed6\u8cbb\u75282</label>
                <input id="create_other_fee_2" type="number" inputmode="decimal" value="0" oninput="updateCreateInstallPreview()">
              </div>
            </div>

            <div id="create_install_preview" class="create-price-preview"></div>
          </div>
        </div>

        <div id="create_repair_section" class="create-card" style="display:none">
          <div class="create-card-title">\u7dad\u4fee\u6536\u8cbb</div>
          <div class="create-two-cols">
            <div class="create-field">
              <label>\u5176\u4ed6\u6536\u8cbb1</label>
              <input id="create_repair_fee_1" type="number" inputmode="decimal" value="0" oninput="updateCreateRepairPreview()">
            </div>
            <div class="create-field">
              <label>\u5176\u4ed6\u6536\u8cbb2</label>
              <input id="create_repair_fee_2" type="number" inputmode="decimal" value="0" oninput="updateCreateRepairPreview()">
            </div>
          </div>
          <div id="create_repair_preview" class="create-price-preview"></div>
        </div>

        <div id="create_return_section" class="create-card" style="display:none">
          <div class="create-card-title">\u9000\u6a5f\u6d3e\u5de5\u50f9\u683c</div>
          <div class="create-two-cols">
            <div class="create-field">
              <label>\u62bc\u91d1</label>
              <input id="create_return_deposit" type="number" inputmode="decimal" value="0">
            </div>
            <div class="create-field">
              <label>\u9000\u8cbb</label>
              <input id="create_return_refund" type="number" inputmode="decimal" value="0">
            </div>
          </div>

          <div class="create-two-cols" style="margin-top:10px">
            <div class="create-field">
              <label>\u6263\u6b3e</label>
              <input id="create_return_deduction" type="number" inputmode="decimal" value="0">
            </div>
            <div class="create-field">
              <label>\u5176\u4ed6\u8cbb\u7528</label>
              <input id="create_return_other" type="number" inputmode="decimal" value="0">
            </div>
          </div>
        </div>

        <div class="create-card">
          <div class="create-card-title">\u6848\u4ef6\u8aaa\u660e</div>
          <div class="create-grid">
            <div class="create-field">
              <label>\u6d3e\u5de5\u5167\u5bb9</label>
              <textarea id="create_description" placeholder="\u8acb\u8f38\u5165\u6d3e\u5de5\u5167\u5bb9\u3001\u6ce8\u610f\u4e8b\u9805\u6216\u5ba2\u6236\u9700\u6c42"></textarea>
            </div>
            <div class="create-field">
              <label>\u5167\u90e8\u5099\u8a3b</label>
              <textarea id="create_internal_note" placeholder="\u7d66\u516c\u53f8\u5167\u90e8\u6216\u5de5\u7a0b\u5e2b\u7684\u5099\u8a3b"></textarea>
            </div>
          </div>
        </div>

        <div class="create-actions">
          <div class="create-actions-row">
            <button class="create-action-btn gray" onclick="showListPage()">\u8fd4\u56de\u5217\u8868</button>
            <button class="create-action-btn green" onclick="submitCreatePreview()">\u5efa\u7acb\u6848\u4ef6</button>
          </div>
        </div>
      `;

      loadCreateBuildingDirectory().then(function () {
        populateCreateBuildingList();
      });

      toggleCreatePriceFields();
      updateCreateInstallPreview();
      updateCreateRepairPreview();
    }

function showCreatePage() {
      const statGrid = document.querySelector(".stat-grid");
      const filterRow = document.querySelector(".filter-row");
      const keyword = document.getElementById("keyword");
      const areaFilter = document.getElementById("area_filter");
      const sectionTitle = document.getElementById("section_title");
      const list = document.getElementById("list");
      const detail = document.getElementById("ticket_detail_page");
      const finish = document.getElementById("ticket_finish_page");
      const create = document.getElementById("ticket_create_page");

      if (statGrid) statGrid.style.display = "none";
      if (filterRow) filterRow.style.display = "none";
      if (keyword) keyword.style.display = "none";
      if (areaFilter) areaFilter.style.display = "none";
      if (sectionTitle) sectionTitle.style.display = "none";
      if (list) list.style.display = "none";

      if (detail) detail.classList.remove("active");
      if (finish) finish.classList.remove("active");
      if (create) create.classList.add("active");

      renderCreatePage();
      window.scrollTo({top: 0, behavior: "smooth"});
    }

async function submitCreatePreview() {
      const payload = buildCreatePayloadPreview();

      if (!payload.dispatch_area) {
        alert("\u8acb\u9078\u64c7\u5340\u57df\u3002");
        return;
      }

      if (!payload.customer_name || !payload.contact_phone || !payload.service_address) {
        alert("\u8acb\u586b\u5beb\u5ba2\u6236\u59d3\u540d\u3001\u96fb\u8a71\u8207\u4f4f\u5740\u3002");
        return;
      }

      const btn = event && event.target ? event.target : null;
      if (btn) {
        btn.disabled = true;
        btn.textContent = "\u9001\u51fa\u4e2d...";
      }

      try {
        const res = await fetch("/api/tickets", {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        });

        const data = await res.json().catch(function () { return {}; });

        if (!res.ok) {
          const msg = data.detail || data.error || "\u5efa\u7acb\u6848\u4ef6\u5931\u6557";
          throw new Error(msg);
        }

        alert("\u6848\u4ef6\u5df2\u5efa\u7acb\uff0c\u96fb\u8166\u7248\u5df2\u540c\u6b65\u3002");

        if (typeof loadTickets === "function") {
          await loadTickets();
        }

        showListPage();
      } catch (err) {
        alert(String(err && err.message ? err.message : err));
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.textContent = "\u5efa\u7acb\u6848\u4ef6";
        }
      }
    }

/* XN_APP_CREATE_PAGE_JS_V1_END */







function openTicketPreview(id) {
      const item = allTickets.find(function (ticket) {
        return Number(ticket.id || 0) === Number(id || 0);
      });

      if (!item) {
        alert("\u627e\u4e0d\u5230\u6848\u4ef6\u8cc7\u6599\u3002");
        return;
      }

      renderDetailPage(item);
    }


    document.querySelectorAll(".chip").forEach(function (btn) {
      btn.addEventListener("click", function () {
        document.querySelectorAll(".chip").forEach(function (b) {
          b.classList.remove("active");
        });

        btn.classList.add("active");
        currentFilter = btn.dataset.filter || "全部";
        renderTickets();
      });
    });

    document.getElementById("keyword").addEventListener("input", renderTickets);
    const areaFilterEl = document.getElementById("area_filter");
    if (areaFilterEl) {
      areaFilterEl.addEventListener("change", renderTickets);
    }

    loadEmergencyNotices();
    loadTickets();
    setInterval(loadEmergencyNotices, 30000);
  
    




    




/* XN_APP_FILTER_STAT_FIX_V1 */

function xunnanIsUnclaimedTicket(item) {
      const s = String((item && item.status) || "").trim();
      return ["", "\u5f85\u6d3e\u5de5", "\u672a\u6d3e\u5de5", "\u5df2\u5efa\u7acb", "\u5df2\u6307\u6d3e"].includes(s);
    }

function xunnanIsClaimedTicket(item) {
      const s = String((item && item.status) || "").trim();
      return ["\u5df2\u9818\u53d6", "\u65bd\u5de5\u4e2d"].includes(s);
    }

function xunnanIsUnfinishedTicket(item) {
      const s = String((item && item.status) || "").trim();
      return !["\u5df2\u5b8c\u6210", "\u5df2\u5b8c\u5de5", "\u5b8c\u6210"].includes(s);
    }

function filteredTickets() {
      const keywordEl = document.getElementById("keyword");
      const keyword = keywordEl ? keywordEl.value.trim().toLowerCase() : "";

      const areaEl = document.getElementById("area_filter");
      const selectedArea = areaEl ? areaEl.value : "\u5168\u90e8";

      const today = typeof todayText === "function" ? todayText() : "";

      return allTickets.filter(function (item) {
        if (selectedArea && selectedArea !== "\u5168\u90e8" && String(item.dispatch_area || "") !== selectedArea) return false;

        if (currentFilter === "\u4eca\u65e5" && typeof ticketTodayValue === "function" && ticketTodayValue(item) !== today) return false;
        if (currentFilter === "\u672a\u9818\u7528" && !xunnanIsUnclaimedTicket(item)) return false;
        if (currentFilter === "\u5df2\u9818\u7528" && !xunnanIsClaimedTicket(item)) return false;
        if (currentFilter === "\u672a\u5b8c\u6210" && !xunnanIsUnfinishedTicket(item)) return false;
        if (currentFilter === "\u5df2\u5b8c\u6210" && !["\u5df2\u5b8c\u6210", "\u5df2\u5b8c\u5de5", "\u5b8c\u6210"].includes(String(item.status || "").trim())) return false;

        if (keyword) {
          const hay = [
            item.customer_name,
            item.contact_name,
            item.contact_phone,
            item.service_address,
            item.case_type,
            item.status,
            item.assigned_engineer,
            item.dispatch_area
          ].join(" ").toLowerCase();

          if (!hay.includes(keyword)) return false;
        }

        return true;
      });
    }

function xunnanSetFilterFromStat(filterName) {
      currentFilter = filterName;

      document.querySelectorAll("[data-filter]").forEach(function (btn) {
        if (String(btn.dataset.filter || "") === filterName) {
          btn.classList.add("active");
        } else {
          btn.classList.remove("active");
        }
      });

      renderTickets();
      xunnanPatchStatCards();
    }

function xunnanPatchFilterButtons() {
      document.querySelectorAll("[data-filter]").forEach(function (btn) {
        if (btn.dataset.filter === "\u672a\u5b8c\u6210") {
          btn.dataset.filter = "\u672a\u9818\u7528";
          btn.textContent = "\u672a\u9818\u7528";
        }

        if (btn.dataset.filter === "\u65bd\u5de5\u4e2d") {
          btn.dataset.filter = "\u5df2\u9818\u7528";
          btn.textContent = "\u5df2\u9818\u7528";
        }
      });
    }

function xunnanPatchStatCards() {
      const cards = Array.from(document.querySelectorAll(".stat-card, .stat"));

      if (cards.length < 3) return;

      const today = typeof todayText === "function" ? todayText() : "";

      const todayCount = allTickets.filter(function (item) {
        return typeof ticketTodayValue === "function" ? ticketTodayValue(item) === today : false;
      }).length;

      const unclaimedCount = allTickets.filter(xunnanIsUnclaimedTicket).length;
      const unfinishedCount = allTickets.filter(xunnanIsUnfinishedTicket).length;

      const configs = [
        { label: "\u4eca\u65e5", count: todayCount, filter: "\u4eca\u65e5" },
        { label: "\u672a\u9818\u7528", count: unclaimedCount, filter: "\u672a\u9818\u7528" },
        { label: "\u672a\u5b8c\u6210", count: unfinishedCount, filter: "\u672a\u5b8c\u6210" }
      ];

      configs.forEach(function (cfg, idx) {
        const card = cards[idx];
        if (!card) return;

        const labelNode = card.querySelector(".stat-label, .label, div:first-child");
        const valueNode = card.querySelector(".stat-value, .value, strong, div:last-child");

        if (labelNode) labelNode.textContent = cfg.label;
        if (valueNode) valueNode.textContent = String(cfg.count);

        card.onclick = function () {
          xunnanSetFilterFromStat(cfg.filter);
        };
      });
    }

document.addEventListener("DOMContentLoaded", function () {
      xunnanPatchFilterButtons();

      const oldRenderStats = typeof renderStats === "function" ? renderStats : null;
      if (oldRenderStats && !window.__xunnanRenderStatsPatched) {
        window.__xunnanRenderStatsPatched = true;
        renderStats = function () {
          oldRenderStats();
          xunnanPatchStatCards();
          xunnanPatchFilterButtons();
        };
      }

      setTimeout(function () {
        xunnanPatchStatCards();
        xunnanPatchFilterButtons();
      }, 300);
    });

/* XN_APP_FILTER_STAT_FIX_V1_END */
