import json as _customers_json

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.responses import Response as _CustomersResponse
from sqlalchemy import text as _customers_sql_text

from app.db import engine as _customers_engine
from app.routes.buildings_admin import _buildings_db_init

router = APIRouter(tags=["customers-admin"])


# SHINNAN_CUSTOMER_BILLING_DETAIL_START
@router.get("/api/admin/customers/billing", summary="讀取單一客戶帳務資料")
def api_admin_customer_billing(customer_no: str):
    _customer_accounts_db_init()
    _buildings_db_init()
    _customer_billing_tables_init()

    with _customers_engine.begin() as conn:
        row = conn.execute(
            _customers_sql_text("""
                SELECT
                    c.id,
                    c.customer_no,
                    c.customer_name,
                    c.customer_phone,
                    c.customer_type,
                    c.building_no,
                    b.name AS building_name,
                    b.area AS area,
                    b.address AS building_address,
                    c.floor_text,
                    c.room_no,
                    c.service_address,
                    c.service_type,
                    c.package_name,
                    c.monthly_fee,
                    c.install_date,
                    c.contract_status,
                    c.account_status,
                    c.payment_method,
                    c.billing_day,
                    c.arrears_status,
                    c.equipment_no,
                    c.cm_mac,
                    c.ip_address,
                    c.signal_note,
                    c.billing_note,
                    c.service_note,
                    c.created_at,
                    c.updated_at
                FROM customer_accounts c
                LEFT JOIN buildings b ON b.building_no = c.building_no
                WHERE c.customer_no = :customer_no
                LIMIT 1
            """),
            {"customer_no": customer_no},
        ).mappings().first()

    if not row:
        return _CustomersResponse(
            content=_customers_json.dumps({"ok": False, "error": "customer not found"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=404,
        )

    return _CustomersResponse(
        content=_customers_json.dumps({"ok": True, "item": dict(row)}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.get("/admin/customers/billing", response_class=HTMLResponse)
def admin_customer_billing_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>客戶帳務資料｜訊南 ERP</title>
  <style>
    body {
      margin: 0;
      background: #eef3f9;
      color: #102348;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .wrap {
      max-width: 1180px;
      margin: 0 auto;
      padding: 18px;
    }

    .hero {
      border-radius: 20px;
      padding: 22px;
      background: linear-gradient(135deg, #0f766e, #2563eb, #7c3aed);
      color: #fff;
      margin-bottom: 14px;
      box-shadow: 0 18px 48px rgba(15,23,42,.18);
    }

    h1 {
      margin: 0 0 8px;
      font-size: 36px;
      font-weight: 1000;
    }

    .toolbar {
      display: flex;
      gap: 10px;
      margin-bottom: 14px;
    }

    button {
      height: 36px;
      border: 0;
      border-radius: 10px;
      padding: 0 14px;
      background: #365ee8;
      color: #fff;
      font-size: 14px;
      font-weight: 1000;
      cursor: pointer;
    }

    button.gray {
      background: #64748b;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }

    .card {
      background: #fff;
      border: 1px solid #d7e1ef;
      border-radius: 16px;
      padding: 14px;
      box-shadow: 0 10px 26px rgba(15,23,42,.06);
    }

    .card.full {
      grid-column: 1 / -1;
    }

    .label {
      color: #64748b;
      font-size: 12px;
      font-weight: 1000;
      margin-bottom: 4px;
    }

    .value {
      color: #102348;
      font-size: 17px;
      font-weight: 1000;
      line-height: 1.45;
      white-space: pre-wrap;
    }

    .muted {
      color: #64748b;
      font-size: 13px;
      font-weight: 800;
      margin-top: 4px;
    }

    @media (max-width: 760px) {
      .grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1 id="title">客戶帳務資料</h1>
      <div id="subtitle">資料載入中...</div>
    </section>

    <div class="toolbar">
      <button type="button" onclick="history.back()">返回上一頁</button>
      <button type="button" class="gray" onclick="location.href='/?ts=' + Date.now()">回入口</button>
      <button type="button" onclick="location.href='/admin/customers?ts=' + Date.now()">客人名冊</button>
    </div>

    <div id="content" class="grid"></div>
  </div>

  <script>
    function esc(v) {
      return String(v ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function card(label, value, extra) {
      return `
        <div class="card ${extra || ""}">
          <div class="label">${esc(label)}</div>
          <div class="value">${esc(value || "-")}</div>
        </div>
      `;
    }

    async function loadBilling() {
      const params = new URLSearchParams(location.search);
      const customerNo = params.get("customer_no") || "";

      if (!customerNo) {
        document.getElementById("content").innerHTML = card("錯誤", "缺少 customer_no", "full");
        return;
      }

      const res = await fetch("/api/admin/customers/billing?customer_no=" + encodeURIComponent(customerNo) + "&ts=" + Date.now(), {cache: "no-store"});

      if (!res.ok) {
        document.getElementById("content").innerHTML = card("錯誤", "讀取失敗：" + res.status, "full");
        return;
      }

      const data = await res.json();
      const item = data.item || {};

      document.getElementById("title").textContent = item.customer_name + "｜帳務資料";
      document.getElementById("subtitle").textContent = item.customer_no + "｜" + item.building_name + "｜" + item.room_no;

      document.getElementById("content").innerHTML = [
        card("客戶編號", item.customer_no),
        card("客戶姓名", item.customer_name),
        card("聯絡電話", item.customer_phone),
        card("大樓", item.building_name + "（" + item.building_no + "）"),
        card("服務地址", item.service_address),
        card("戶別", item.room_no),
        card("服務類型", item.service_type),
        card("方案", item.package_name),
        card("月租費", item.monthly_fee),
        card("帳號狀態", item.account_status),
        card("合約狀態", item.contract_status),
        card("裝機日", item.install_date),
        card("繳費方式", item.payment_method),
        card("帳單日", item.billing_day),
        card("欠費狀態", item.arrears_status),
        card("設備編號", item.equipment_no),
        card("CM MAC", item.cm_mac),
        card("IP", item.ip_address),
        card("訊號備註", item.signal_note || "-", "full"),
        card("帳務備註", item.billing_note || "-", "full"),
        card("服務備註", item.service_note || "-", "full")
      ].join("");
    }

    loadBilling();
  </script>
</body>
</html>
"""
# SHINNAN_CUSTOMER_BILLING_DETAIL_END


@router.get("/admin/customers", response_class=HTMLResponse)
def admin_customers_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>客人名冊｜訊南 ERP</title>
  <style>
    body {
      margin: 0;
      background: #eef3f9;
      color: #102348;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .wrap {
      max-width: 1760px;
      margin: 0 auto;
      padding: 22px;
    }

    .hero {
      border-radius: 24px;
      padding: 28px;
      background: linear-gradient(135deg, #0f766e, #2563eb, #7c3aed);
      color: #fff;
      box-shadow: 0 20px 60px rgba(15,23,42,.18);
      margin-bottom: 16px;
    }

    h1 {
      margin: 0 0 10px;
      font-size: 44px;
      line-height: 1.1;
      font-weight: 1000;
    }

    .sub {
      font-size: 18px;
      font-weight: 900;
      opacity: .92;
    }

    .toolbar {
      display: grid;
      grid-template-columns: auto auto 220px 220px 220px 1fr auto;
      gap: 10px;
      align-items: center;
      margin: 16px 0;
    }

    button, select, input {
      height: 40px;
      border-radius: 12px;
      border: 1px solid #cbd5e1;
      font-size: 15px;
      font-weight: 900;
      padding: 0 12px;
      box-sizing: border-box;
    }

    button {
      border: 0;
      background: #365ee8;
      color: #fff;
      cursor: pointer;
    }

    button.gray {
      background: #64748b;
    }

    .summary {
      margin-bottom: 10px;
      color: #475569;
      font-size: 14px;
      font-weight: 900;
    }

    .card {
      background: #fff;
      border: 1px solid #d7e1ef;
      border-radius: 22px;
      padding: 14px;
      box-shadow: 0 12px 34px rgba(15,23,42,.07);
      overflow-x: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      min-width: 1500px;
    }

    th {
      background: #eaf2ff;
      color: #203a5f;
      font-size: 14px;
      font-weight: 1000;
      text-align: left;
      padding: 10px 8px;
    }

    td {
      border-bottom: 1px solid #e5edf7;
      padding: 9px 8px;
      font-size: 14px;
      font-weight: 800;
      vertical-align: top;
      line-height: 1.45;
      color: #102348;
    }

    .muted {
      color: #64748b;
      font-size: 12px;
      font-weight: 800;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 23px;
      padding: 2px 9px;
      border-radius: 999px;
      background: #eaf2ff;
      color: #1d4ed8;
      font-size: 12px;
      font-weight: 1000;
    }

    .pill.green {
      background: #dcfce7;
      color: #166534;
    }

    .pill.orange {
      background: #ffedd5;
      color: #9a3412;
    }

    .pill.gray {
      background: #f1f5f9;
      color: #475569;
    }

    .pager {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: 8px;
      margin-top: 12px;
      font-weight: 900;
      color: #475569;
    }

    .empty {
      padding: 28px;
      text-align: center;
      color: #64748b;
      font-weight: 900;
    }

    @media (max-width: 1200px) {
      .toolbar {
        grid-template-columns: 1fr 1fr;
      }
    }
  </style>

<style id="customer_page_compact_v2">
  /* 客人名冊：工具列與列表緊湊版 */

  .wrap {
    max-width: 1760px !important;
    padding: 12px !important;
  }

  .hero {
    padding: 16px 20px !important;
    border-radius: 18px !important;
    margin-bottom: 8px !important;
  }

  h1 {
    font-size: 32px !important;
    margin-bottom: 4px !important;
  }

  .sub {
    font-size: 14px !important;
    line-height: 1.35 !important;
  }

  .toolbar {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    align-items: center !important;
    margin: 8px 0 !important;
  }

  .toolbar button {
    width: auto !important;
    min-width: 78px !important;
    height: 32px !important;
    padding: 0 12px !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    white-space: nowrap !important;
  }

  .toolbar button.gray {
    background: #2f7b7b !important;
  }

  .toolbar select {
    width: auto !important;
    min-width: 106px !important;
    max-width: 145px !important;
    height: 32px !important;
    padding: 0 8px !important;
    border-radius: 9px !important;
    font-size: 13px !important;
  }

  #limit_filter {
    min-width: 110px !important;
    max-width: 128px !important;
  }

  #keyword_filter {
    width: 360px !important;
    min-width: 240px !important;
    max-width: 420px !important;
    height: 32px !important;
    padding: 0 10px !important;
    border-radius: 9px !important;
    font-size: 13px !important;
  }

  .summary {
    margin: 4px 0 6px !important;
    font-size: 12px !important;
  }

  .card {
    padding: 7px !important;
    border-radius: 15px !important;
  }

  table {
    min-width: 1220px !important;
  }

  th {
    padding: 6px 6px !important;
    font-size: 12px !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
  }

  td {
    padding: 4px 6px !important;
    font-size: 12px !important;
    line-height: 1.22 !important;
    vertical-align: middle !important;
  }

  td b {
    font-size: 12px !important;
    line-height: 1.2 !important;
  }

  .muted {
    font-size: 10px !important;
    line-height: 1.15 !important;
    margin-top: 1px !important;
  }

  .pill {
    min-height: 18px !important;
    padding: 1px 6px !important;
    font-size: 10px !important;
  }

  .pager {
    margin-top: 6px !important;
    gap: 6px !important;
    font-size: 12px !important;
  }

  .pager button {
    height: 28px !important;
    font-size: 12px !important;
  }

  .customer-link {
    color: #1d4ed8 !important;
    font-weight: 1000 !important;
    text-decoration: none !important;
  }

  .customer-link:hover {
    text-decoration: underline !important;
  }

  @media (max-width: 900px) {
    #keyword_filter {
      width: 100% !important;
      max-width: none !important;
    }
  }
</style>

<style id="customer_area_address_layout_v1">
  /* 客人名冊：區域移到第 2 格，大樓縮小，地址加大，列高壓縮 */

  .card {
    padding: 4px !important;
  }

  table {
    min-width: 1320px !important;
  }

  th {
    padding: 4px 5px !important;
    font-size: 12px !important;
    line-height: 1.15 !important;
    white-space: nowrap !important;
  }

  td {
    padding: 3px 5px !important;
    font-size: 12px !important;
    line-height: 1.15 !important;
    height: 30px !important;
    vertical-align: middle !important;
  }

  td b,
  td a {
    font-size: 12px !important;
    line-height: 1.15 !important;
  }

  .muted {
    font-size: 10px !important;
    line-height: 1.1 !important;
    margin-top: 0 !important;
  }

  .pill {
    min-height: 16px !important;
    padding: 0 5px !important;
    font-size: 10px !important;
    line-height: 16px !important;
  }

  .customer-address-cell {
    max-width: 360px !important;
    white-space: normal !important;
    line-height: 1.18 !important;
  }

  .customer-building-cell {
    max-width: 120px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
  }

  .customer-service-cell {
    max-width: 190px !important;
    white-space: normal !important;
    line-height: 1.18 !important;
  }

  .customer-link {
    color: #1d4ed8 !important;
    font-weight: 1000 !important;
    text-decoration: none !important;
  }

  .customer-link:hover {
    text-decoration: underline !important;
  }
</style>


<style id="customer_address_service_fix_v1">
  /* 客人名冊：地址改為服務地址，戶別欄取消，大樓欄縮小 */

  table {
    min-width: 1180px !important;
  }

  th,
  td {
    padding: 3px 5px !important;
    font-size: 12px !important;
    line-height: 1.15 !important;
    height: 30px !important;
    vertical-align: middle !important;
  }

  .customer-building-cell {
    max-width: 115px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
  }

  .customer-address-cell {
    min-width: 230px !important;
    max-width: 360px !important;
    white-space: normal !important;
    line-height: 1.18 !important;
    font-weight: 1000 !important;
  }

  .customer-service-cell {
    max-width: 190px !important;
    white-space: normal !important;
    line-height: 1.18 !important;
  }

  .pill {
    min-height: 16px !important;
    padding: 0 5px !important;
    font-size: 10px !important;
    line-height: 16px !important;
  }

  .muted {
    font-size: 10px !important;
    line-height: 1.1 !important;
  }
</style>

</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>客人名冊</h1>
      <div class="sub">由 customer_accounts 資料表提供，並透過 building_no 關聯大樓主資料。</div>
    </section>

    <div class="toolbar">
      <button type="button" onclick="history.back()">返回上一頁</button>
      <button type="button" class="gray" onclick="location.href='/?ts=' + Date.now()">回入口</button>

      <select id="area_filter">
        <option value="全部">全部區域</option>
      </select>

      <select id="status_filter">
        <option value="全部">全部狀態</option>
        <option value="正常">正常</option>
        <option value="IP限制">IP限制</option>
        <option value="停用">停用</option>
        <option value="退租">退租</option>
      </select>

      <select id="limit_filter">
        <option value="100">每頁 100 筆</option>
        <option value="300" selected>每頁 300 筆</option>
        <option value="500">每頁 500 筆</option>
        <option value="1000">每頁 1000 筆</option>
      </select>

      <input id="keyword_filter" placeholder="搜尋客戶編號 / 姓名 / 電話 / 大樓 / 戶別">

      <button type="button" onclick="reloadCustomers(true)">搜尋</button>
    </div>

    <div id="summary" class="summary">資料載入中...</div>

    <div class="card">
      <table>
        <thead>
          <tr>
            <th style="width:110px;">客戶編號</th>
            <th style="width:150px;">客戶</th>
            <th style="width:150px;">電話</th>
            <th style="width:190px;">大樓</th>
            <th style="width:80px;">區域</th>
            <th style="width:120px;">戶別</th>
            <th style="width:150px;">服務</th>
            <th style="width:90px;">月租</th>
            <th style="width:120px;">狀態</th>
            <th style="width:140px;">帳務</th>
            <th style="width:180px;">設備</th>
            <th>備註</th>
          </tr>
        </thead>
        <tbody id="customer_rows">
          <tr><td colspan="12" class="empty">資料載入中...</td></tr>
        </tbody>
      </table>

      <div class="pager">
        <button type="button" class="gray" onclick="prevPage()">上一頁</button>
        <span id="page_info">第 1 頁</span>
        <button type="button" onclick="nextPage()">下一頁</button>
      </div>
    </div>
  </div>

  <script>
    let currentOffset = 0;
    let currentLimit = 300;
    let currentTotal = 0;
    let areaOptionsBuilt = false;

    function esc(v) {
      return String(v ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function statusClass(status) {
      if (status === "啟用中") return "green";
      if (status === "待裝機") return "orange";
      return "gray";
    }

    async function buildAreaFilter() {
      if (areaOptionsBuilt) return;

      const res = await fetch("/api/admin/buildings?ts=" + Date.now(), {cache: "no-store"});
      const rows = await res.json();
      const areas = Array.from(new Set(rows.map(x => x.area).filter(Boolean))).sort();
      const sel = document.getElementById("area_filter");

      sel.innerHTML = '<option value="全部">全部區域</option>' +
        areas.map(a => '<option value="' + esc(a) + '">' + esc(a) + '</option>').join("");

      areaOptionsBuilt = true;
    }

    async function reloadCustomers(reset) {
      if (reset) currentOffset = 0;

      currentLimit = Number(document.getElementById("limit_filter").value || 300);

      const params = new URLSearchParams();
      params.set("limit", currentLimit);
      params.set("offset", currentOffset);
      params.set("area", document.getElementById("area_filter").value || "全部");
      params.set("status", document.getElementById("status_filter").value || "全部");
      params.set("q", document.getElementById("keyword_filter").value || "");
      params.set("ts", Date.now());

      const res = await fetch("/api/admin/customers?" + params.toString(), {cache: "no-store"});

      if (!res.ok) {
        document.getElementById("customer_rows").innerHTML =
          '<tr><td colspan="12" class="empty">客人 API 讀取失敗：' + res.status + '</td></tr>';
        return;
      }

      const data = await res.json();
      currentTotal = data.total || 0;

      renderCustomers(data.items || []);
      renderSummary();
    }

    function renderSummary() {
      const page = Math.floor(currentOffset / currentLimit) + 1;
      const start = currentTotal ? currentOffset + 1 : 0;
      const end = Math.min(currentOffset + currentLimit, currentTotal);

      document.getElementById("summary").textContent =
        "共 " + currentTotal + " 筆，目前顯示 " + start + " - " + end + " 筆";

      document.getElementById("page_info").textContent = "第 " + page + " 頁";
    }

    function renderCustomers(rows) {
      const box = document.getElementById("customer_rows");

      if (!rows.length) {
        box.innerHTML = '<tr><td colspan="12" class="empty">沒有符合條件的客戶資料。</td></tr>';
        return;
      }

      box.innerHTML = rows.map(function (item) {
        return `
          <tr>
            <td>${esc(item.customer_no)}</td>
            <td>
              <b>${esc(item.customer_name)}</b>
              <div class="muted">${esc(item.customer_type || "-")}</div>
            </td>
            <td>${esc(item.customer_phone || "-")}</td>
            <td>
              <b>${esc(item.building_name || "-")}</b>
              <div class="muted">${esc(item.building_no || "-")}</div>
            </td>
            <td><span class="pill">${esc(item.area || "-")}</span></td>
            <td>
              ${esc(item.floor_text || "-")}
              <div class="muted">${esc(item.room_no || "-")}</div>
            </td>
            <td>
              <b>${esc(item.service_type || "-")}</b>
              <div class="muted">${esc(item.package_name || "-")}</div>
            </td>
            <td>${esc(item.monthly_fee || 0)}</td>
            <td><span class="pill ${statusClass(item.account_status)}">${esc(item.account_status || "-")}</span></td>
            <td>
              ${esc(item.payment_method || "-")}
              <div class="muted">帳單日：${esc(item.billing_day || "-")}</div>
              <div class="muted">${esc(item.arrears_status || "-")}</div>
            </td>
            <td>
              ${esc(item.equipment_no || "-")}
              <div class="muted">${esc(item.cm_mac || "-")}</div>
            </td>
            <td>
              <div>${esc(item.service_note || "-")}</div>
              <div class="muted">${esc(item.billing_note || "")}</div>
            </td>
          </tr>
        `;
      }).join("");
    }

    function prevPage() {
      currentOffset = Math.max(0, currentOffset - currentLimit);
      reloadCustomers(false);
    }

    function nextPage() {
      if (currentOffset + currentLimit >= currentTotal) return;
      currentOffset += currentLimit;
      reloadCustomers(false);
    }

    document.getElementById("area_filter").addEventListener("change", function () { reloadCustomers(true); });
    document.getElementById("status_filter").addEventListener("change", function () { reloadCustomers(true); });
    document.getElementById("limit_filter").addEventListener("change", function () { reloadCustomers(true); });
    document.getElementById("keyword_filter").addEventListener("keydown", function (event) {
      if (event.key === "Enter") reloadCustomers(true);
    });

    buildAreaFilter().then(function () {
      reloadCustomers(true);
    });
  </script>


<script id="customer_billing_links_v1">
(function () {
  if (!location.pathname.includes("/admin/customers")) return;

  function esc2(v) {
    return String(v ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function billingUrl(customerNo) {
    return "/admin/customers/billing?customer_no=" + encodeURIComponent(customerNo || "");
  }

  window.renderCustomers = function (rows) {
    const box = document.getElementById("customer_rows");

    if (!rows.length) {
      box.innerHTML = '<tr><td colspan="12" class="empty">沒有符合條件的客戶資料。</td></tr>';
      return;
    }

    box.innerHTML = rows.map(function (item) {
      const url = billingUrl(item.customer_no);

      return `
        <tr>
          <td>
            <a class="customer-link" href="${url}">${esc2(item.customer_no)}</a>
          </td>
          <td>
            <a class="customer-link" href="${url}">${esc2(item.customer_name)}</a>
            <div class="muted">${esc2(item.customer_type || "-")}</div>
          </td>
          <td>${esc2(item.customer_phone || "-")}</td>
          <td>
            <a class="customer-link" href="${url}">${esc2(item.building_name || "-")}</a>
            <div class="muted">${esc2(item.building_no || "-")}</div>
          </td>
          <td><span class="pill">${esc2(item.area || "-")}</span></td>
          <td>
            <a class="customer-link" href="${url}">${esc2(item.floor_text || "-")}</a>
            <div class="muted">
              <a class="customer-link" href="${url}">${esc2(item.room_no || "-")}</a>
            </div>
          </td>
          <td>
            <b>${esc2(item.service_type || "-")}</b>
            <div class="muted">${esc2(item.package_name || "-")}</div>
          </td>
          <td>${esc2(item.monthly_fee || 0)}</td>
          <td><span class="pill ${statusClass(item.account_status)}">${esc2(item.account_status || "-")}</span></td>
          <td>
            ${esc2(item.payment_method || "-")}
            <div class="muted">帳單日：${esc2(item.billing_day || "-")}</div>
            <div class="muted">${esc2(item.arrears_status || "-")}</div>
          </td>
          <td>
            ${esc2(item.equipment_no || "-")}
            <div class="muted">${esc2(item.cm_mac || "-")}</div>
          </td>
          <td>
            <div>${esc2(item.service_note || "-")}</div>
            <div class="muted">${esc2(item.billing_note || "")}</div>
          </td>
        </tr>
      `;
    }).join("");
  };
})();
</script>


<script id="customer_area_address_layout_v1">
(function () {
  if (!location.pathname.includes("/admin/customers")) return;

  function esc2(v) {
    return String(v ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function billingUrl(customerNo) {
    return "/admin/customers/billing?customer_no=" + encodeURIComponent(customerNo || "");
  }

  function patchCustomerHeader() {
    const heads = document.querySelectorAll("table thead tr th");
    if (!heads || heads.length < 9) return;

    const labels = [
      "客戶編號",
      "區域",
      "客戶",
      "電話",
      "大樓",
      "地址",
      "戶別",
      "服務",
      "月租",
      "狀態",
      "帳務",
      "備註"
    ];

    heads.forEach(function (th, index) {
      if (labels[index]) th.textContent = labels[index];
    });
  }

  window.renderCustomers = function (rows) {
    const box = document.getElementById("customer_rows");

    patchCustomerHeader();

    if (!rows.length) {
      box.innerHTML = '<tr><td colspan="12" class="empty">沒有符合條件的客戶資料。</td></tr>';
      return;
    }

    box.innerHTML = rows.map(function (item) {
      const url = billingUrl(item.customer_no);
      const address = item.service_address || item.building_address || "-";

      return `
        <tr>
          <td>
            <a class="customer-link" href="${url}">${esc2(item.customer_no)}</a>
          </td>

          <td>
            <span class="pill">${esc2(item.area || "-")}</span>
          </td>

          <td>
            <a class="customer-link" href="${url}">${esc2(item.customer_name)}</a>
            <div class="muted">${esc2(item.customer_type || "-")}</div>
          </td>

          <td>${esc2(item.customer_phone || "-")}</td>

          <td class="customer-building-cell">
            <a class="customer-link" href="${url}">${esc2(item.building_name || "-")}</a>
            <div class="muted">${esc2(item.building_no || "-")}</div>
          </td>

          <td class="customer-address-cell">${esc2(address)}</td>

          <td>
            <a class="customer-link" href="${url}">${esc2(item.room_no || "-")}</a>
          </td>

          <td class="customer-service-cell">
            <b>${esc2(item.service_type || "-")}</b>
            <div class="muted">${esc2(item.package_name || "-")}</div>
          </td>

          <td><b>${esc2(item.monthly_fee || 0)}</b></td>

          <td><span class="pill ${statusClass(item.account_status)}">${esc2(item.account_status || "-")}</span></td>

          <td>
            ${esc2(item.payment_method || "-")}
            <div class="muted">${esc2(item.arrears_status || "-")}</div>
          </td>

          <td>
            <div>${esc2(item.service_note || "-")}</div>
            <div class="muted">${esc2(item.billing_note || "")}</div>
          </td>
        </tr>
      `;
    }).join("");
  };

  patchCustomerHeader();
  setTimeout(patchCustomerHeader, 300);
})();
</script>


<script id="customer_address_service_fix_v1">
(function () {
  if (!location.pathname.includes("/admin/customers")) return;

  function esc3(v) {
    return String(v ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function billingUrl(customerNo) {
    return "/admin/customers/billing?customer_no=" + encodeURIComponent(customerNo || "");
  }

  function patchCustomerHeaderV2() {
    const heads = document.querySelectorAll("table thead tr th");
    if (!heads || heads.length < 8) return;

    const labels = [
      "客戶編號",
      "區域",
      "客戶",
      "電話",
      "大樓",
      "地址",
      "服務",
      "月租",
      "狀態",
      "帳務",
      "備註"
    ];

    heads.forEach(function (th, index) {
      if (labels[index]) th.textContent = labels[index];
    });
  }

  window.renderCustomers = function (rows) {
    const box = document.getElementById("customer_rows");

    patchCustomerHeaderV2();

    if (!rows.length) {
      box.innerHTML = '<tr><td colspan="11" class="empty">沒有符合條件的客戶資料。</td></tr>';
      return;
    }

    box.innerHTML = rows.map(function (item) {
      const url = billingUrl(item.customer_no);

      /*
        重要：
        地址欄只顯示 customer_accounts.service_address。
        不再組合 building_address + room_no。
      */
      const serviceAddress = item.service_address || item.room_no || "-";
      const buildingName = item.building_name || (item.building_no === "HOUSE" ? "透天" : "-");

      return `
        <tr>
          <td>
            <a class="customer-link" href="${url}">${esc3(item.customer_no)}</a>
          </td>

          <td>
            <span class="pill">${esc3(item.area || "-")}</span>
          </td>

          <td>
            <a class="customer-link" href="${url}">${esc3(item.customer_name)}</a>
            <div class="muted">${esc3(item.customer_type || "-")}</div>
          </td>

          <td>${esc3(item.customer_phone || "-")}</td>

          <td class="customer-building-cell">
            <a class="customer-link" href="${url}">${esc3(buildingName)}</a>
            <div class="muted">${esc3(item.building_no || "-")}</div>
          </td>

          <td class="customer-address-cell">
            <a class="customer-link" href="${url}">${esc3(serviceAddress)}</a>
          </td>

          <td class="customer-service-cell">
            <b>${esc3(item.service_type || "-")}</b>
            <div class="muted">${esc3(item.package_name || "-")}</div>
          </td>

          <td><b>${esc3(item.monthly_fee || 0)}</b></td>

          <td><span class="pill ${statusClass(item.account_status)}">${esc3(item.account_status || "-")}</span></td>

          <td>
            ${esc3(item.payment_method || "-")}
            <div class="muted">${esc3(item.arrears_status || "-")}</div>
          </td>

          <td>
            <div>${esc3(item.service_note || "-")}</div>
            <div class="muted">${esc3(item.billing_note || "")}</div>
          </td>
        </tr>
      `;
    }).join("");
  };

  patchCustomerHeaderV2();
  setTimeout(patchCustomerHeaderV2, 300);
})();
</script>


<script id="customer_address_room_only_v1">
(function () {
  if (!location.pathname.includes("/admin/customers")) return;

  function escRoomOnly(v) {
    return String(v ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function billingUrl(customerNo) {
    return "/admin/customers/billing?customer_no=" + encodeURIComponent(customerNo || "");
  }

  function displayAddress(item) {
    if (item.building_no === "HOUSE") {
      return item.service_address || "-";
    }

    return item.service_address || item.room_no || "-";
  }

  window.renderCustomers = function (rows) {
    const box = document.getElementById("customer_rows");

    if (!rows.length) {
      box.innerHTML = '<tr><td colspan="11" class="empty">沒有符合條件的客戶資料。</td></tr>';
      return;
    }

    box.innerHTML = rows.map(function (item) {
      const url = billingUrl(item.customer_no);
      const serviceAddress = displayAddress(item);
      const buildingName = item.building_name || (item.building_no === "HOUSE" ? "透天" : "-");

      return `
        <tr>
          <td>
            <a class="customer-link" href="${url}">${escRoomOnly(item.customer_no)}</a>
          </td>

          <td>
            <span class="pill">${escRoomOnly(item.area || "-")}</span>
          </td>

          <td>
            <a class="customer-link" href="${url}">${escRoomOnly(item.customer_name)}</a>
            <div class="muted">${escRoomOnly(item.customer_type || "-")}</div>
          </td>

          <td>${escRoomOnly(item.customer_phone || "-")}</td>

          <td class="customer-building-cell">
            <a class="customer-link" href="${url}">${escRoomOnly(buildingName)}</a>
            <div class="muted">${escRoomOnly(item.building_no || "-")}</div>
          </td>

          <td class="customer-address-cell">
            <a class="customer-link" href="${url}">${escRoomOnly(serviceAddress)}</a>
          </td>

          <td class="customer-service-cell">
            <b>${escRoomOnly(item.service_type || "-")}</b>
            <div class="muted">${escRoomOnly(item.package_name || "-")}</div>
          </td>

          <td><b>${escRoomOnly(item.monthly_fee || 0)}</b></td>

          <td><span class="pill ${statusClass(item.account_status)}">${escRoomOnly(item.account_status || "-")}</span></td>

          <td>
            ${escRoomOnly(item.payment_method || "-")}
            <div class="muted">${escRoomOnly(item.arrears_status || "-")}</div>
          </td>

          <td>
            <div>${escRoomOnly(item.service_note || "-")}</div>
            <div class="muted">${escRoomOnly(item.billing_note || "")}</div>
          </td>
        </tr>
      `;
    }).join("");
  };
})();
</script>

  <script src="/static/app_header_actions.js?v=cl17p4"></script>
</body>
</html>
"""



# SHINNAN_CUSTOMER_BILLING_TABLES_HELPER_START
def _customer_billing_tables_init():
    with _customers_engine.begin() as conn:
        conn.execute(_customers_sql_text("""
            CREATE TABLE IF NOT EXISTS billing_service_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_code TEXT UNIQUE NOT NULL,
                plan_name TEXT NOT NULL,
                plan_label TEXT DEFAULT '',
                monthly_fee INTEGER DEFAULT 0,
                billing_category TEXT DEFAULT '',
                enabled INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))
        plan_columns = {row[1] for row in conn.execute(_customers_sql_text("PRAGMA table_info(billing_service_plans)")).fetchall()}
        billing_plan_required = {
            "plan_code": "TEXT DEFAULT ''",
            "plan_name": "TEXT DEFAULT ''",
            "plan_label": "TEXT DEFAULT ''",
            "monthly_fee": "INTEGER DEFAULT 0",
            "billing_category": "TEXT DEFAULT ''",
            "enabled": "INTEGER DEFAULT 1",
            "created_at": "TEXT DEFAULT ''",
            "updated_at": "TEXT DEFAULT ''",
        }

        for column, definition in billing_plan_required.items():
            if column not in plan_columns:
                conn.execute(_customers_sql_text(f"ALTER TABLE billing_service_plans ADD COLUMN {column} {definition}"))

        conn.execute(_customers_sql_text("""
            CREATE TABLE IF NOT EXISTS customer_service_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_no TEXT NOT NULL,
                plan_code TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))
        item_columns = {row[1] for row in conn.execute(_customers_sql_text("PRAGMA table_info(customer_service_items)")).fetchall()}
        service_item_required = {
            "customer_no": "TEXT DEFAULT ''",
            "plan_code": "TEXT DEFAULT ''",
            "enabled": "INTEGER DEFAULT 1",
            "created_at": "TEXT DEFAULT ''",
            "updated_at": "TEXT DEFAULT ''",
        }

        for column, definition in service_item_required.items():
            if column not in item_columns:
                conn.execute(_customers_sql_text(f"ALTER TABLE customer_service_items ADD COLUMN {column} {definition}"))
# SHINNAN_CUSTOMER_BILLING_TABLES_HELPER_END


# SHINNAN_CUSTOMER_ACCOUNTS_API_START
def _ensure_customer_accounts_columns(conn):
    existing = {row[1] for row in conn.execute(_customers_sql_text("PRAGMA table_info(customer_accounts)")).fetchall()}
    required = {
        "customer_phone": "TEXT DEFAULT ''",
        "customer_type": "TEXT DEFAULT ''",
        "floor_text": "TEXT DEFAULT ''",
        "room_no": "TEXT DEFAULT ''",
        "service_address": "TEXT DEFAULT ''",
        "service_type": "TEXT DEFAULT ''",
        "package_name": "TEXT DEFAULT ''",
        "monthly_fee": "INTEGER DEFAULT 0",
        "install_date": "TEXT DEFAULT ''",
        "contract_status": "TEXT DEFAULT ''",
        "account_status": "TEXT DEFAULT ''",
        "payment_method": "TEXT DEFAULT ''",
        "billing_day": "INTEGER DEFAULT 0",
        "arrears_status": "TEXT DEFAULT ''",
        "equipment_no": "TEXT DEFAULT ''",
        "cm_mac": "TEXT DEFAULT ''",
        "ip_address": "TEXT DEFAULT ''",
        "signal_note": "TEXT DEFAULT ''",
        "billing_note": "TEXT DEFAULT ''",
        "service_note": "TEXT DEFAULT ''",
        "created_at": "TEXT DEFAULT ''",
        "updated_at": "TEXT DEFAULT ''",
    }

    for column, definition in required.items():
        if column not in existing:
            conn.execute(_customers_sql_text(f"ALTER TABLE customer_accounts ADD COLUMN {column} {definition}"))

    refreshed = existing | required.keys()
    if "phone" in refreshed:
        conn.execute(_customers_sql_text("""
            UPDATE customer_accounts
            SET customer_phone = COALESCE(NULLIF(customer_phone, ''), phone, '')
            WHERE COALESCE(customer_phone, '') = ''
        """))
    if "address" in refreshed:
        conn.execute(_customers_sql_text("""
            UPDATE customer_accounts
            SET service_address = COALESCE(NULLIF(service_address, ''), address, '')
            WHERE COALESCE(service_address, '') = ''
        """))
    if "service_status" in refreshed:
        conn.execute(_customers_sql_text("""
            UPDATE customer_accounts
            SET account_status = COALESCE(NULLIF(account_status, ''), service_status, '')
            WHERE COALESCE(account_status, '') = ''
        """))
    if "payment_status" in refreshed:
        conn.execute(_customers_sql_text("""
            UPDATE customer_accounts
            SET arrears_status = COALESCE(NULLIF(arrears_status, ''), payment_status, '')
            WHERE COALESCE(arrears_status, '') = ''
        """))
    if "plan_name" in refreshed:
        conn.execute(_customers_sql_text("""
            UPDATE customer_accounts
            SET package_name = COALESCE(NULLIF(package_name, ''), plan_name, '')
            WHERE COALESCE(package_name, '') = ''
        """))


def _customer_accounts_db_init():
    with _customers_engine.begin() as conn:
        conn.execute(_customers_sql_text("""
            CREATE TABLE IF NOT EXISTS customer_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_no TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                customer_phone TEXT DEFAULT '',
                customer_type TEXT DEFAULT '',
                building_no TEXT NOT NULL,
                floor_text TEXT DEFAULT '',
                room_no TEXT DEFAULT '',
                service_address TEXT DEFAULT '',
                service_type TEXT DEFAULT '',
                package_name TEXT DEFAULT '',
                monthly_fee INTEGER DEFAULT 0,
                install_date TEXT DEFAULT '',
                contract_status TEXT DEFAULT '',
                account_status TEXT DEFAULT '',
                payment_method TEXT DEFAULT '',
                billing_day INTEGER DEFAULT 0,
                arrears_status TEXT DEFAULT '',
                equipment_no TEXT DEFAULT '',
                cm_mac TEXT DEFAULT '',
                ip_address TEXT DEFAULT '',
                signal_note TEXT DEFAULT '',
                billing_note TEXT DEFAULT '',
                service_note TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))
        _ensure_customer_accounts_columns(conn)


@router.get("/api/admin/customers", summary="讀取客人名冊")
def api_admin_customers(
    q: str = "",
    area: str = "全部",
    building_no: str = "",
    status: str = "全部",
    limit: int = 300,
    offset: int = 0,
):
    _customer_accounts_db_init()
    _buildings_db_init()
    _customer_billing_tables_init()

    limit = max(1, min(int(limit or 300), 1000))
    offset = max(0, int(offset or 0))

    where = []
    params = {
        "limit": limit,
        "offset": offset,
    }

    if q:
        where.append("""
            (
                c.customer_no LIKE :q OR
                c.customer_name LIKE :q OR
                c.customer_phone LIKE :q OR
                b.name LIKE :q OR
                c.room_no LIKE :q
            )
        """)
        params["q"] = f"%{q}%"

    if area and area != "全部":
        where.append("b.area = :area")
        params["area"] = area

    if building_no:
        where.append("c.building_no = :building_no")
        params["building_no"] = building_no

    if status and status != "全部":
        status_aliases = {
            "啟用中": "正常",
            "暫停": "停用",
            "已退租": "退租",
        }
        normalized_status = status_aliases.get(status, status)
        where.append("c.account_status = :status")
        params["status"] = normalized_status

    where_sql = ""
    if where:
        where_sql = "WHERE " + " AND ".join(where)

    with _customers_engine.begin() as conn:
        total = conn.execute(
            _customers_sql_text(f"""
                SELECT COUNT(*)
                FROM customer_accounts c
                LEFT JOIN buildings b ON b.building_no = c.building_no
                {where_sql}
            """),
            params,
        ).scalar()

        rows = conn.execute(
            _customers_sql_text(f"""
                SELECT
                    c.id,
                    c.customer_no,
                    c.customer_name,
                    c.customer_phone,
                    c.customer_type,
                    c.building_no,
                    b.name AS building_name,
                    b.area AS area,
                    b.address AS building_address,
                    c.floor_text,
                    c.room_no,
                    c.service_address,
                    COALESCE(svc.service_type, c.service_type) AS service_type,
                    COALESCE(svc.package_name, c.package_name) AS package_name,
                    COALESCE(svc.monthly_fee, c.monthly_fee) AS monthly_fee,
                    c.install_date,
                    c.contract_status,
                    c.account_status,
                    c.payment_method,
                    c.billing_day,
                    c.arrears_status,
                    c.equipment_no,
                    c.cm_mac,
                    c.ip_address,
                    c.signal_note,
                    c.billing_note,
                    c.service_note,
                    c.created_at,
                    c.updated_at
                FROM customer_accounts c
                LEFT JOIN buildings b ON b.building_no = c.building_no
                LEFT JOIN (
                    SELECT
                        i.customer_no,
                        GROUP_CONCAT(p.plan_name, '＋') AS service_type,
                        GROUP_CONCAT(p.plan_label, '＋') AS package_name,
                        SUM(p.monthly_fee) AS monthly_fee
                    FROM customer_service_items i
                    LEFT JOIN billing_service_plans p ON p.plan_code = i.plan_code
                    WHERE i.enabled = 1
                    GROUP BY i.customer_no
                ) svc ON svc.customer_no = c.customer_no
                {where_sql}
                ORDER BY CAST(substr(c.building_no, 2) AS INTEGER) ASC, c.floor_text ASC, c.room_no ASC, c.customer_no ASC
                LIMIT :limit OFFSET :offset
            """),
            params,
        ).mappings().fetchall()

    return _CustomersResponse(
        content=_customers_json.dumps(
            {
                "total": total,
                "limit": limit,
                "offset": offset,
                "items": [dict(row) for row in rows],
            },
            ensure_ascii=False,
        ),
        media_type="application/json; charset=utf-8",
    )
# SHINNAN_CUSTOMER_ACCOUNTS_API_END
