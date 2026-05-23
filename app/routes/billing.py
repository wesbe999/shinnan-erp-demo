from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from app.config import data_file
from app.routes.employee_auth import _employee_current_user_from_request
from sqlalchemy import text as _sql

router = APIRouter(tags=["帳務系統"])

# DB 連線：統一使用 config.database_url()，與主程式共用同一個 DB
from app.db import engine as _billing_engine

_BILLING_NOTICES_FILE = data_file("billing_notices.json")


def _load_billing_records_from_db(user: dict) -> list[dict]:
    """從 customer_accounts DB 讀取帳單資料"""
    role = str(user.get("role", "") or "")
    staff_code = str(user.get("staff_code", "") or "")
    today = datetime.now().strftime("%Y-%m-%d")

    with _billing_engine.begin() as conn:
        # 確認欄位存在
        cols_rows = conn.execute(_sql("PRAGMA table_info(customer_accounts)")).fetchall()
        cols = {r[1] for r in cols_rows}

        # 篩選條件：到期日前15天到逾期後90天
        where = [
            "COALESCE(billing_due_date, '') != ''",
            "date(billing_due_date, '-15 day') <= date(:today)",
            "date(billing_due_date, '+90 day') > date(:today)",
        ]

        params = {"today": today, "staff_code": staff_code}

        # 非 admin 只看自己負責的
        if role != "admin" and staff_code != "admin":
            staff_filters = []
            for col in ("assigned_staff_code", "billing_staff_code", "collector_staff_code", "owner_staff_code"):
                if col in cols:
                    staff_filters.append(f"COALESCE({col}, '') = :staff_code")
            if staff_filters:
                where.append("(" + " OR ".join(staff_filters) + ")")

        where_sql = " AND ".join(where)

        # 欄位安全取用
        def _col(name, default="''"):
            return name if name in cols else default

        sql = f"""
            SELECT
                id,
                {_col('customer_no')} AS customer_no,
                {_col('customer_name')} AS customer_name,
                {_col('customer_phone', _col('phone'))} AS phone,
                {_col('area')} AS area,
                {_col('building_no')} AS building_no,
                {_col('building_name')} AS building_name,
                {_col('install_address', _col('service_address', _col('address')))} AS install_address,
                {_col('billing_due_date')} AS due_date,
                {_col('billing_month')} AS year_month,
                {_col('monthly_fee', '0')} AS monthly_fee,
                {_col('payment_status')} AS payment_status,
                {_col('arrears_months', '0')} AS arrears_months,
                {_col('arrears_status')} AS arrears_status,
                {_col('collected_date')} AS collected_date,
                {_col('collected_amount', '0')} AS collected_amount,
                {_col('billing_memo')} AS billing_memo,
                {_col('billing_staff_code')} AS billing_staff_code,
                {_col('account_status')} AS account_status,
                {_col('service_status')} AS service_status,
                {_col('plan_name')} AS plan_name,
                {_col('overdue_fee', '0')} AS overdue_fee
            FROM customer_accounts
            WHERE {where_sql}
            ORDER BY billing_due_date ASC
            LIMIT 500
        """

        rows = conn.execute(_sql(sql), params).fetchall()
        col_names = [
            'id','customer_no','customer_name','phone','area','building_no',
            'building_name','install_address','due_date','year_month','monthly_fee',
            'payment_status','arrears_months','arrears_status','collected_date',
            'collected_amount','billing_memo','billing_staff_code','account_status',
            'service_status','plan_name','overdue_fee'
        ]

        records = []
        for row in rows:
            r = dict(zip(col_names, row))
            # 計算逾期天數
            try:
                due = datetime.strptime(r['due_date'], "%Y-%m-%d")
                r['overdue_days'] = max(0, (datetime.now() - due).days)
            except:
                r['overdue_days'] = 0
            # 計算總金額
            r['total_amount'] = (r.get('monthly_fee') or 0) + (r.get('overdue_fee') or 0)
            r['notice_label'] = '異常' if r['overdue_days'] > 20 else '正常'
            # 補齊前端需要的欄位
            r['billing_no'] = f"R{r['id']:08d}"
            r['confirm_no'] = r.get('customer_no', '')
            r['invoice_no'] = ''
            r['install_time'] = r.get('year_month', '')
            r['change_fee'] = 0
            r['material_fee'] = 0
            # 統一 payment_status 格式
            ps = str(r.get('payment_status') or '')
            if ps in ('正常', '已繳費', '繳費正常'):
                r['payment_status'] = '繳費正常'
                r['notice_label'] = '正常'
            elif ps in ('逾期', '逾期未繳', '繳費異常', '欠費'):
                r['payment_status'] = '繳費異常'
                r['notice_label'] = '異常'
            else:
                r['payment_status'] = '繳費正常' if r['overdue_days'] <= 20 else '繳費異常'
                r['notice_label'] = '正常' if r['overdue_days'] <= 20 else '異常'
            records.append(r)

    return records


def _load_billing_notices() -> list[dict]:
    if not _BILLING_NOTICES_FILE.exists():
        return []

    try:
        data = json.loads(_BILLING_NOTICES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

    if isinstance(data, dict):
        data = data.get("notices", [])

    if not isinstance(data, list):
        return []

    notices = []
    for item in data:
        if isinstance(item, dict):
            message = str(item.get("message") or "").strip()
        else:
            message = str(item or "").strip()
        if message:
            notices.append({"message": message})
    return notices


def _save_billing_notices(notices: list[dict]) -> None:
    _BILLING_NOTICES_FILE.parent.mkdir(parents=True, exist_ok=True)
    _BILLING_NOTICES_FILE.write_text(
        json.dumps({"notices": notices}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@router.get("/api/billing/notices")
@router.get("/api/app/billing/notices")
def api_billing_notices():
    notices = _load_billing_notices()
    return JSONResponse({"ok": True, "notices": notices, "items": notices})


@router.post("/api/billing/notices")
def api_billing_notices_save(payload: dict):
    notices = _load_billing_notices()

    if "delete_index" in payload:
        try:
            index = int(payload.get("delete_index"))
        except Exception:
            index = -1
        if 0 <= index < len(notices):
            notices.pop(index)
    else:
        message = str(payload.get("message") or "").strip()
        if message:
            notices.append({"message": message})

    _save_billing_notices(notices)
    return JSONResponse({"ok": True, "notices": notices, "items": notices})


@router.patch("/api/billing/customer/{customer_id}")
async def api_billing_update_customer(customer_id: int, request: Request):
    """電腦版帳務：更新客戶繳費狀態到 DB"""
    user = _employee_current_user_from_request(request)
    if not user:
        return JSONResponse({"ok": False, "error": "login required"}, status_code=401)

    payload = await request.json()
    allowed = {
        "payment_status", "collected_date", "collected_amount",
        "billing_memo", "billing_staff_code", "arrears_status",
        "arrears_months", "overdue_fee", "is_overdue", "ip_limited",
        "last_payment_date", "billing_due_date", "billing_month",
    }
    updates = {k: v for k, v in payload.items() if k in allowed}
    if not updates:
        return JSONResponse({"ok": False, "error": "no valid fields"}, status_code=400)

    updates["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    set_sql = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = customer_id

    with _billing_engine.begin() as conn:
        result = conn.execute(
            _sql(f"UPDATE customer_accounts SET {set_sql} WHERE id = :id"),
            updates
        )
        if result.rowcount == 0:
            return JSONResponse({"ok": False, "error": "not found"}, status_code=404)

    return JSONResponse({"ok": True})


@router.get("/admin/billing", response_class=HTMLResponse, summary="帳務系統")
def billing_page(request: Request):
    current_user = _employee_current_user_from_request(request)
    if not current_user:
        return RedirectResponse("/employee/login?next=/admin/billing", status_code=303)

    records_json = json.dumps(_load_billing_records_from_db(current_user), ensure_ascii=False)

    html = """
<!doctype html>
<html lang="zh-Hant">
<head>

<meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>\u5e33\u52d9\u7cfb\u7d71\uff5c\u4e2d\u592e\u63a7\u7ba1\u7cfb\u7d71</title>

  



  <link rel="stylesheet" href="/static/web_title_unified.css?v=xn_v1">
<link rel="stylesheet" href="/static/xn_buttons.css?v=xn_v1">
<link rel="stylesheet" href="/static/billing.css?v=xn_v4">
<link rel="stylesheet" href="/static/billing_notice.css?v=xn_v1">



  




</head>

<body>

  <div id="customer_detail_modal" class="customer-detail-mask">
    <div class="customer-detail-modal">
      <div class="customer-detail-header">
        <div class="customer-detail-title">客戶詳細資料</div>
        <button type="button" class="customer-detail-close" onclick="closeCustomerDetail()">關閉</button>
      </div>

      <div class="customer-detail-grid">
        <div class="customer-detail-field">
          <div class="customer-detail-label">客戶編號</div>
          <div id="detail_customer_no" class="customer-detail-value">-</div>
        </div>

        <div class="customer-detail-field">
          <div class="customer-detail-label">客戶名稱</div>
          <div id="detail_customer_name" class="customer-detail-value">-</div>
        </div>

        <div class="customer-detail-field">
          <div class="customer-detail-label">電話</div>
          <div id="detail_phone" class="customer-detail-value">-</div>
        </div>

        <div class="customer-detail-field">
          <div class="customer-detail-label">區域</div>
          <div id="detail_area" class="customer-detail-value">-</div>
        </div>

        <div class="customer-detail-field">
          <div class="customer-detail-label">裝機地址</div>
          <div id="detail_install_address" class="customer-detail-value">-</div>
        </div>

        <div class="customer-detail-field">
          <div class="customer-detail-label">裝機時間</div>
          <div id="detail_install_time" class="customer-detail-value">-</div>
        </div>

        <div class="customer-detail-field">
          <div class="customer-detail-label">目前狀態</div>
          <div id="detail_payment_status" class="customer-detail-value">-</div>
        </div>

        <div class="customer-detail-field">
          <div class="customer-detail-label">應繳金額</div>
          <div id="detail_total_amount" class="customer-detail-value">-</div>
        </div>
      </div>

      
      
      

      
      <!-- SHINNAN_MODAL_FEE_CALC_BLOCK_START -->
      <div class="detail-fee-card">
        <div class="detail-fee-title">費用計算</div>

        <div class="fee-form-row fee-display-row">
          <div class="fee-field">
            <label>安裝費</label>
            <input id="detail_install_fee" value="0" inputmode="numeric">
          </div>

          <div class="fee-field">
            <label>押金</label>
            <input id="detail_deposit" value="0" inputmode="numeric">
          </div>
        </div>

        <div class="fee-form-row fee-calc-row">
          <div class="fee-symbol">(</div>

          <div class="fee-field">
            <label>月租費1</label>
            <input id="detail_monthly_fee_1" value="0" inputmode="numeric" oninput="calculateDetailFeeTotal()">
          </div>

          <div class="fee-symbol">+</div>

          <div class="fee-field">
            <label>月租費2</label>
            <input id="detail_monthly_fee_2" value="0" inputmode="numeric" oninput="calculateDetailFeeTotal()">
          </div>

          <div class="fee-symbol">+</div>

          <div class="fee-field">
            <label>月租費3</label>
            <input id="detail_monthly_fee_3" value="0" inputmode="numeric" oninput="calculateDetailFeeTotal()">
          </div>

          <div class="fee-symbol">)</div>
          <div class="fee-symbol">×</div>

          <div class="fee-field">
            <label>繳費月數</label>
            <input id="detail_payment_months" value="1" inputmode="numeric" oninput="calculateDetailFeeTotal()">
          </div>

          <div class="fee-symbol">=</div>

          <div class="fee-field fee-total">
            <label>應繳金額／帳單金額</label>
            <input id="detail_fee_total" value="0" readonly>
          </div>
        </div>

        <div class="fee-note">安裝費與押金僅供顯示，不列入帳單金額；帳單金額 =（月租費1 + 月租費2 + 月租費3）× 繳費月數。</div>

        <div style="margin-top:12px;display:flex;gap:10px;align-items:center;">
          <button type="button" onclick="confirmPaymentToDb()" class="btn-green">✅ 登記收費</button>
          <button type="button" onclick="markOverdueToDb()" class="btn-danger">⚠️ 標記逾期</button>
          <span id="billing_save_status" style="font-size:13px;color:#1a6b3a;"></span>
        </div>
      </div>
      <!-- SHINNAN_MODAL_FEE_CALC_BLOCK_END -->

      <div class="detail-switch-bar">
        <button type="button" id="show_payment_history_button" class="detail-switch-button active" onclick="showCustomerDetailPanel('payment')">歷屆繳費紀錄</button>
        <button type="button" id="show_change_log_button" class="detail-switch-button" onclick="showCustomerDetailPanel('change')">異動紀錄</button>
        <button type="button" id="show_equipment_button" class="detail-switch-button" onclick="showCustomerDetailPanel('equipment')">租借設備</button>
      </div>

      <section id="customer_detail_payment_panel" class="detail-panel active">
        <div class="detail-section-title">歷屆繳費紀錄</div>

        <div class="detail-table-wrap">
          <table class="detail-table">
            <thead>
              <tr>
                <th>期別</th>
                <th>收據單號</th>
                <th>確認編號</th>
                <th>繳費期限</th>
                <th>月租費</th>
                <th>異動費</th>
                <th>材料費</th>
                <th>應繳金額</th>
                <th>狀態</th>
              </tr>
            </thead>
            <tbody id="payment_history_rows"></tbody>
          </table>
        </div>
      </section>

      <section id="customer_detail_change_panel" class="detail-panel">
        <div class="detail-section-title">異動紀錄</div>

        <div class="change-log-box">
          <div class="change-input-grid">
            <input id="change_log_input" placeholder="輸入異動紀錄，例如：更改電話、補開發票、調整月租">
            <button type="button" onclick="addChangeLog()">新增紀錄</button>
          </div>

          <div id="change_log_list" class="change-log-list"></div>
        </div>
      </section>

    </div>
  </div>
<section class="web-title web-title-tech" id="xn-page-header">
  <img class="web-title-watermark" src="/static/shinnan_logo_outline_white.png" alt="">
  <div class="web-title-map"></div>
  <div class="web-title-radar"></div>
  <div class="web-title-main">
    <div class="web-title-logo-box">
      <img class="web-title-logo" src="/static/shinnan_logo_gold_transparent.png?v=cl_header_v1" alt="ShinNan Logo">
    </div>
    <div class="web-title-text">
      <h1 class="web-title-system">帳務系統</h1>
      <div class="web-title-sub">
        <span class="web-title-sub-dot"></span>中央控管系統<span class="web-title-sub-dot"></span>
      </div>
    </div>
  </div>
  <div class="xn-header-actions">
    <button type="button" style="background:#1a6b3a !important;border:1.5px solid #d4af37 !important" onclick="document.getElementById('create_customer_button') && document.getElementById('create_customer_button').click()">＋ 建立資料</button>
    <button type="button" style="background:#b45309 !important;border:1.5px solid #d4af37 !important" onclick="alert('開立發票功能下一步串接')">🧾 開立發票</button>
    <button type="button" style="background:#6b3fa0 !important;border:1.5px solid #d4af37 !important" onclick="window.location.href='/'">🏠 首頁</button>
    <button type="button" class="danger" style="border:1.5px solid #d4af37 !important" onclick="window.location.href='/employee/logout?next=/'">登出</button>
  </div>
</section>

  <main class="page">

<div id="billing_notice_panel">
  <div class="billing-notice-title">帳務通知</div>
  <div class="billing-notice-subtitle">可送出帳務 APP 跑馬燈通知；每條通知可個別刪除。</div>

  <div class="billing-notice-input-box">
    <textarea id="billing_notice_input" placeholder="輸入帳務通知，按送出後會顯示在帳務 APP 跑馬燈。"></textarea>
    <button id="save_billing_notice_button" class="billing-notice-send" type="button">送出</button>
    <button id="clear_billing_notice_button" class="billing-notice-clear" type="button">清除</button>
  </div>

  <div id="billing_notice_display">
    <div class="billing-notice-empty">目前沒有帳務通知。</div>
  </div>
</div>


    <div class="toolbar">

      <select id="area_filter">
        <option value="全部">全部區域</option>
      </select>

      <input id="global_search" placeholder="搜尋客戶名稱 / 電話 / 社區 / 收據單號 / 確認編號 / 裝機地址">

      <button class="btn-green" type="button" id="search_button">查詢</button>
      <button class="btn-gray" type="button" id="clear_button">清除</button>
    </div>

    <div class="tabs">
      <button class="tab-button create-tab-button" type="button" id="create_customer_button">建立資料</button>
      <button class="tab-button invoice-tab-button" type="button" onclick="alert('開立發票功能下一步串接')">開立發票</button>
      <button class="tab-button active" data-tab="customers" type="button">客戶清單</button>
    </div>

    <section id="tab_customers" class="tab-panel active">
      <div class="summary-row">
        <div class="summary-box">
          <div class="summary-label">目前筆數</div>
          <div id="summary_count" class="summary-value">0</div>
        </div>
        <div class="summary-box">
          <div class="summary-label">正常繳費</div>
          <div id="summary_normal" class="summary-value">0</div>
        </div>
        <div class="summary-box">
          <div class="summary-label">繳費異常</div>
          <div id="summary_abnormal" class="summary-value red">0</div>
        </div>
        <div class="summary-box">
          <div class="summary-label">應收總額</div>
          <div id="summary_amount" class="summary-value">0</div>
        </div>
        <div class="summary-box">
          <div class="summary-label">目前區域</div>
          <div id="summary_area" class="summary-value" style="font-size:28px">全部</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title customer-list-title-row">
          <span>客戶清單</span>
          <button type="button" class="print-list-button" onclick="printCustomerList()">列印清單</button>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>客戶編號</th>
                <th>客戶名稱</th>
                <th>電話</th>
                <th>裝機地址</th>
                <th>收據單號</th>
                <th>確認編號</th>
                <th>裝機時間</th>
                <th>繳費期限</th>
                <th>逾期天數</th>
                <th>月租費</th>
                <th>應繳金額</th>
                <th>繳費狀態</th>
                <th>異常</th>
              </tr>
            </thead>
            <tbody id="customer_rows"></tbody>
          </table>
        </div>
      </div>
    </section>

    <section id="tab_notice" class="tab-panel">
      <div class="card">
        <div class="card-title">
          <span>繳費異常通知</span>
          <span class="hint">選擇全部區域時，會依區域分隔。</span>
        </div>
        <div id="notice_list" class="notice-list"></div>
      </div>
    </section>
  </main>

  <script>
    const BASE_RECORDS = __RECORDS_JSON__;
    let records = [];
    let filtered = [];
    let summaryStatusFilter = "all";

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function money(value) {
      return Number(value || 0).toLocaleString();
    }

    function loadBuildingOverrides() {
      const keys = [
        "shinnan_building_directory_overrides_v2",
        "shinnan_building_directory_overrides_v1"
      ];

      for (const key of keys) {
        try {
          const data = JSON.parse(localStorage.getItem(key) || "{}");
          if (data && typeof data === "object") return data;
        } catch (e) {}
      }

      return {};
    }

    function applyBuildingOverrides(list) {
      const overrides = loadBuildingOverrides();

      return list.map(function (record) {
        const patch = overrides[record.building_no];

        if (!patch) return Object.assign({}, record);

        const next = Object.assign({}, record);

        if (patch.area) next.area = patch.area;
        if (patch.name) next.building_name = patch.name;

        if (patch.address || patch.name) {
          const oldName = record.building_name || "";
          let unit = String(record.install_address || "").replace(oldName, "").trim();

          if (patch.address) {
            unit = patch.address;
          }

          next.install_address = (next.building_name || oldName) + " " + unit;
        }

        return next;
      });
    }

    function setupAreas() {
      const select = document.getElementById("area_filter");
      const areas = Array.from(new Set(records.map(r => r.area))).filter(Boolean);

      areas.forEach(function (area) {
        if (select.querySelector(`option[value="${area}"]`)) return;
        const option = document.createElement("option");
        option.value = area;
        option.textContent = area;
        select.appendChild(option);
      });
    }

    function applyFilters() {
      const area = document.getElementById("area_filter").value;
      const keyword = document.getElementById("global_search").value.trim().toLowerCase();

      filtered = records.filter(function (r) {
        if (area !== "全部" && r.area !== area) return false;

        if (summaryStatusFilter === "normal" && r.payment_status !== "繳費正常") return false;
        if (summaryStatusFilter === "abnormal" && r.payment_status !== "繳費異常") return false;

        if (!keyword) return true;

        const hay = [
          r.customer_no,
          r.customer_name,
          r.phone,
          r.area,
          r.building_name,
          r.install_address,
          r.billing_no,
          r.confirm_no,
          r.year_month,
          r.invoice_no
        ].join(" ").toLowerCase();

        return hay.includes(keyword);
      });

      renderAll();
    }

    function clearFilters() {
      document.getElementById("area_filter").value = "全部";
      document.getElementById("global_search").value = "";
      summaryStatusFilter = "all";
      updateSummaryCardActive();
      filtered = [...records];
      renderAll();
    }

    function renderAll() {
      renderCustomers();
      renderSummary();
      renderNotices();
    }

    function renderCustomers() {
      const tbody = document.getElementById("customer_rows");

      if (!filtered.length) {
        tbody.innerHTML = "<tr><td colspan='13' class='empty'>沒有符合條件的客戶資料。</td></tr>";
        return;
      }

      const areaOrder = Array.from(new Set(records.map(r => r.area))).filter(Boolean);
      const selectedArea = document.getElementById("area_filter").value;

      let html = "";

      areaOrder.forEach(function (area) {
        if (selectedArea !== "全部" && area !== selectedArea) return;

        const areaRows = filtered
          .filter(r => r.area === area)
          .sort(function (a, b) {
            const addrA = String(a.install_address || "");
            const addrB = String(b.install_address || "");
            return addrA.localeCompare(addrB, "zh-Hant");
          });

        if (!areaRows.length) return;

        html += `
          <tr class="area-group-row">
            <td colspan="13"><span class="area-group-label">${escapeHtml(area)}</span></td>
          </tr>
        `;

        html += areaRows.map(function (r) {
          const abnormal = r.payment_status === "繳費異常";
          const statusClass = abnormal ? "pill-red" : "pill-green";
          const actionClass = abnormal ? "btn-red" : "btn-green";
          const actionText = abnormal ? "異常" : "正常";

          return `
            <tr class="customer-row" onclick="openCustomerDetail('${escapeHtml(r.customer_no)}')">
              <td>${escapeHtml(r.customer_no)}</td>
              <td>${escapeHtml(r.customer_name)}</td>
              <td>${escapeHtml(r.phone)}</td>
              <td>${escapeHtml(r.install_address)}</td>
              <td>${escapeHtml(r.billing_no)}</td>
              <td>${escapeHtml(r.confirm_no)}</td>
              <td>${escapeHtml(r.install_time || r.year_month)}</td>
              <td>${escapeHtml(r.due_date)}</td>
              <td>${escapeHtml(r.overdue_days)}</td>
              <td>${money(r.monthly_fee)}</td>
              <td>${money(r.total_amount)}</td>
              <td><span class="pill ${statusClass}">${escapeHtml(r.payment_status)}</span></td>
              <td><button class="status-button ${actionClass}" type="button">${actionText}</button></td>
            </tr>
          `;
        }).join("");
      });

      tbody.innerHTML = html;
    }


    function renderSummary() {
      const abnormal = filtered.filter(r => r.payment_status === "繳費異常").length;
      const normal = filtered.length - abnormal;
      const amount = filtered.reduce((sum, r) => sum + Number(r.total_amount || 0), 0);
      const area = document.getElementById("area_filter").value;

      document.getElementById("summary_count").textContent = filtered.length;
      document.getElementById("summary_normal").textContent = normal;
      document.getElementById("summary_abnormal").textContent = abnormal;
      document.getElementById("summary_amount").textContent = money(amount);
      document.getElementById("summary_area").textContent = area;
    }

    function renderNotices() {
      const box = document.getElementById("notice_list");
      const selectedArea = document.getElementById("area_filter").value;
      const rows = filtered.filter(r => r.payment_status === "繳費異常");

      if (!rows.length) {
        box.innerHTML = `<div class="notice-item notice-normal"><div>目前篩選範圍內沒有繳費異常的客戶。</div><span class="pill pill-green">繳費正常</span></div>`;
        return;
      }

      if (selectedArea !== "全部") {
        box.innerHTML = rows.map(function (r) {
          return `
            <div class="notice-item">
              <div>${escapeHtml(r.customer_name)}｜${escapeHtml(r.phone)}｜${escapeHtml(r.building_name)}｜異常 ${r.overdue_days} 天｜應繳 ${money(r.total_amount)}</div>
              <span class="pill pill-red">繳費異常</span>
            </div>
          `;
        }).join("");
        return;
      }

      const areas = Array.from(new Set(rows.map(r => r.area))).filter(Boolean);
      let html = "";

      areas.forEach(function (area) {
        const areaRows = rows.filter(r => r.area === area);
        html += `<div class="notice-area-title">${escapeHtml(area)}</div>`;
        html += areaRows.map(function (r) {
          return `
            <div class="notice-item">
              <div>${escapeHtml(r.customer_name)}｜${escapeHtml(r.phone)}｜${escapeHtml(r.building_name)}｜異常 ${r.overdue_days} 天｜應繳 ${money(r.total_amount)}</div>
              <span class="pill pill-red">繳費異常</span>
            </div>
          `;
        }).join("");
      });

      box.innerHTML = html;
    }




    // SHINNAN_CUSTOMER_DETAIL_SWITCH_BUTTONS_JS_START
    function showCustomerDetailPanel(panelName) {
      const paymentPanel = document.getElementById("customer_detail_payment_panel");
      const changePanel = document.getElementById("customer_detail_change_panel");
      const paymentButton = document.getElementById("show_payment_history_button");
      const changeButton = document.getElementById("show_change_log_button");

      if (!paymentPanel || !changePanel || !paymentButton || !changeButton) return;

      paymentPanel.classList.remove("active");
      changePanel.classList.remove("active");
      paymentButton.classList.remove("active");
      changeButton.classList.remove("active");

      if (panelName === "change") {
        changePanel.classList.add("active");
        changeButton.classList.add("active");
      } else {
        paymentPanel.classList.add("active");
        paymentButton.classList.add("active");
      }
    }
    // SHINNAN_CUSTOMER_DETAIL_SWITCH_BUTTONS_JS_END


    // SHINNAN_BILLING_CUSTOMER_DETAIL_HISTORY_JS_START
    let currentDetailCustomerNo = "";

    function changeLogKey(customerNo) {
      return "shinnan_customer_change_logs_" + customerNo;
    }

    function loadChangeLogs(customerNo) {
      try {
        return JSON.parse(localStorage.getItem(changeLogKey(customerNo)) || "[]");
      } catch (e) {
        return [];
      }
    }

    function saveChangeLogs(customerNo, logs) {
      localStorage.setItem(changeLogKey(customerNo), JSON.stringify(logs));
    }

    function closeCustomerDetail() {
      const modal = document.getElementById("customer_detail_modal");
      if (modal) modal.classList.remove("active");
      currentDetailCustomerNo = "";
    }

    function makeHistoryRecords(baseRecord) {
      const result = [];
      const baseAmount = Number(baseRecord.monthly_fee || 0);
      const today = new Date();

      for (let i = 11; i >= 0; i--) {
        const d = new Date(today);
        d.setMonth(today.getMonth() - i);

        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, "0");
        const dueDate = year + "-" + month + "-10";

        const period = year + "-" + month;
        const isCurrentRecord = i === 0;
        const abnormal = isCurrentRecord && baseRecord.payment_status === "繳費異常";

        const changeFee = (d.getMonth() % 5 === 0) ? 200 : 0;
        const materialFee = (d.getMonth() % 7 === 0) ? 300 : 0;
        const total = baseAmount + changeFee + materialFee;

        result.push({
          period: period,
          billing_no: String(baseRecord.billing_no || "R000000000") + "-" + month,
          confirm_no: String(baseRecord.confirm_no || "CN000000000") + "-" + month,
          due_date: dueDate,
          monthly_fee: baseAmount,
          change_fee: changeFee,
          material_fee: materialFee,
          total_amount: total,
          payment_status: abnormal ? "繳費異常" : "繳費正常"
        });
      }

      return result;
    }

    function renderPaymentHistory(customerRecords) {
      const rows = document.getElementById("payment_history_rows");
      const base = customerRecords[0];
      const history = makeHistoryRecords(base);

      rows.innerHTML = history.map(function (r) {
        const abnormal = r.payment_status === "繳費異常";
        const statusClass = abnormal ? "pill-red" : "pill-green";

        return `
          <tr>
            <td>${escapeHtml(r.period)}</td>
            <td>${escapeHtml(r.billing_no)}</td>
            <td>${escapeHtml(r.confirm_no)}</td>
            <td>${escapeHtml(r.due_date)}</td>
            <td>${money(r.monthly_fee)}</td>
            <td>${money(r.change_fee)}</td>
            <td>${money(r.material_fee)}</td>
            <td>${money(r.total_amount)}</td>
            <td><span class="pill ${statusClass}">${escapeHtml(r.payment_status)}</span></td>
          </tr>
        `;
      }).join("");
    }

    function renderChangeLogs(customerNo) {
      const list = document.getElementById("change_log_list");
      const logs = loadChangeLogs(customerNo);

      if (!logs.length) {
        list.innerHTML = `<div class="empty-change-log">目前沒有異動紀錄。</div>`;
        return;
      }

      list.innerHTML = logs.map(function (item) {
        return `
          <div class="change-log-item">
            <div class="change-log-time">${escapeHtml(item.time)}</div>
            <div class="change-log-text">${escapeHtml(item.text)}</div>
          </div>
        `;
      }).join("");
    }

    function addChangeLog() {
      if (!currentDetailCustomerNo) {
        alert("尚未選擇客戶");
        return;
      }

      const input = document.getElementById("change_log_input");
      const value = input.value.trim();

      if (!value) {
        alert("請輸入異動紀錄");
        return;
      }

      const logs = loadChangeLogs(currentDetailCustomerNo);
      const now = new Date();

      logs.unshift({
        time: now.toLocaleString("zh-TW", { hour12: false }),
        text: value
      });

      saveChangeLogs(currentDetailCustomerNo, logs);
      input.value = "";
      renderChangeLogs(currentDetailCustomerNo);
    }


    // SHINNAN_MODAL_FEE_CALC_BLOCK_JS_START
    function parseFeeNumber(value) {
      const cleaned = String(value || "0").replace(/[^\\d]/g, "");
      return cleaned ? Number(cleaned) : 0;
    }

    function setFeeInputValue(id, value) {
      const el = document.getElementById(id);
      if (el) el.value = String(value ?? 0);
    }

    function calculateDetailFeeTotal() {
      const monthly1 = parseFeeNumber(document.getElementById("detail_monthly_fee_1")?.value);
      const monthly2 = parseFeeNumber(document.getElementById("detail_monthly_fee_2")?.value);
      const monthly3 = parseFeeNumber(document.getElementById("detail_monthly_fee_3")?.value);
      const months = parseFeeNumber(document.getElementById("detail_payment_months")?.value) || 0;

      const total = (monthly1 + monthly2 + monthly3) * months;

      const totalInput = document.getElementById("detail_fee_total");
      if (totalInput) totalInput.value = money(total);

      return total;
    }

    function fillDetailFeeCalculator(record) {
      setFeeInputValue("detail_install_fee", 0);
      setFeeInputValue("detail_deposit", 0);
      setFeeInputValue("detail_monthly_fee_1", record.monthly_fee || 0);
      setFeeInputValue("detail_monthly_fee_2", 0);
      setFeeInputValue("detail_monthly_fee_3", 0);
      setFeeInputValue("detail_payment_months", 1);
      calculateDetailFeeTotal();
    }
    // SHINNAN_MODAL_FEE_CALC_BLOCK_JS_END



    // SHINNAN_FIX_EQUIPMENT_PANEL_JS_START
    function equipmentLogKey(customerNo) {
      return "shinnan_customer_equipment_logs_" + customerNo;
    }

    function loadEquipmentLogs(customerNo) {
      try {
        return JSON.parse(localStorage.getItem(equipmentLogKey(customerNo)) || "[]");
      } catch (e) {
        return [];
      }
    }

    function saveEquipmentLogs(customerNo, logs) {
      localStorage.setItem(equipmentLogKey(customerNo), JSON.stringify(logs));
    }

    function renderEquipmentLogs(customerNo) {
      const list = document.getElementById("equipment_log_list");
      if (!list) return;

      const logs = loadEquipmentLogs(customerNo);

      if (!logs.length) {
        list.innerHTML = `<div class="empty-change-log">目前沒有租借設備紀錄。</div>`;
        return;
      }

      list.innerHTML = logs.map(function (item) {
        return `
          <div class="change-log-item">
            <div class="change-log-time">${escapeHtml(item.time)}</div>
            <div class="change-log-text">${escapeHtml(item.text)}</div>
          </div>
        `;
      }).join("");
    }

    function addEquipmentLog() {
      if (!currentDetailCustomerNo) {
        alert("尚未選擇客戶");
        return;
      }

      const input = document.getElementById("equipment_log_input");
      const value = input.value.trim();

      if (!value) {
        alert("請輸入租借設備");
        return;
      }

      const logs = loadEquipmentLogs(currentDetailCustomerNo);
      const now = new Date();

      logs.unshift({
        time: now.toLocaleString("zh-TW", { hour12: false }),
        text: value
      });

      saveEquipmentLogs(currentDetailCustomerNo, logs);
      input.value = "";
      renderEquipmentLogs(currentDetailCustomerNo);
    }

    function showCustomerDetailPanel(panelName) {
      const paymentPanel = document.getElementById("customer_detail_payment_panel");
      const changePanel = document.getElementById("customer_detail_change_panel");
      const equipmentPanel = document.getElementById("customer_detail_equipment_panel");

      const paymentButton = document.getElementById("show_payment_history_button");
      const changeButton = document.getElementById("show_change_log_button");
      const equipmentButton = document.getElementById("show_equipment_button");

      [paymentPanel, changePanel, equipmentPanel].forEach(function (panel) {
        if (panel) panel.classList.remove("active");
      });

      [paymentButton, changeButton, equipmentButton].forEach(function (button) {
        if (button) button.classList.remove("active");
      });

      if (panelName === "change") {
        if (changePanel) changePanel.classList.add("active");
        if (changeButton) changeButton.classList.add("active");
        return;
      }

      if (panelName === "equipment") {
        if (equipmentPanel) equipmentPanel.classList.add("active");
        if (equipmentButton) equipmentButton.classList.add("active");
        if (currentDetailCustomerNo) renderEquipmentLogs(currentDetailCustomerNo);
        return;
      }

      if (paymentPanel) paymentPanel.classList.add("active");
      if (paymentButton) paymentButton.classList.add("active");
    }
    // SHINNAN_FIX_EQUIPMENT_PANEL_JS_END


    // ── 登記收費到 DB ──
    async function confirmPaymentToDb() {
      if (!currentDetailCustomerNo) { alert('尚未選擇客戶'); return; }
      const record = records.find(r => String(r.customer_no) === String(currentDetailCustomerNo));
      if (!record || !record.id) { alert('找不到客戶資料'); return; }

      const total = parseFeeNumber(document.getElementById('detail_fee_total')?.value);
      const today = new Date().toISOString().slice(0, 10);

      const status = document.getElementById('billing_save_status');
      status.textContent = '儲存中...';
      status.style.color = '#64748b';

      try {
        const res = await fetch('/api/billing/customer/' + record.id, {
          method: 'PATCH',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            payment_status: '已繳費',
            collected_date: today,
            collected_amount: total,
            arrears_status: '無欠費',
            arrears_months: 0,
            last_payment_date: today,
          })
        });
        const data = await res.json();
        if (data.ok) {
          status.textContent = '✅ 已登記收費';
          status.style.color = '#16a34a';
          record.payment_status = '已繳費';
          record.collected_date = today;
          record.collected_amount = total;
        } else {
          status.textContent = '❌ 儲存失敗';
          status.style.color = '#dc2626';
        }
      } catch(e) {
        status.textContent = '❌ 網路錯誤';
        status.style.color = '#dc2626';
      }
    }

    async function markOverdueToDb() {
      if (!currentDetailCustomerNo) { alert('尚未選擇客戶'); return; }
      const record = records.find(r => String(r.customer_no) === String(currentDetailCustomerNo));
      if (!record || !record.id) { alert('找不到客戶資料'); return; }

      if (!confirm('確認標記為逾期未繳？')) return;

      const status = document.getElementById('billing_save_status');
      status.textContent = '儲存中...';

      try {
        const res = await fetch('/api/billing/customer/' + record.id, {
          method: 'PATCH',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            payment_status: '逾期未繳',
            arrears_status: '逾期未繳',
            is_overdue: 1,
          })
        });
        const data = await res.json();
        if (data.ok) {
          status.textContent = '⚠️ 已標記逾期';
          status.style.color = '#dc2626';
          record.payment_status = '逾期未繳';
        } else {
          status.textContent = '❌ 儲存失敗';
          status.style.color = '#dc2626';
        }
      } catch(e) {
        status.textContent = '❌ 網路錯誤';
        status.style.color = '#dc2626';
      }
    }

    function openCustomerDetail(customerNo) {
      const customerRecords = records.filter(function (r) {
        return String(r.customer_no) === String(customerNo);
      });

      if (!customerRecords.length) return;

      currentDetailCustomerNo = customerNo;

      const first = customerRecords[0];

      document.getElementById("detail_customer_no").textContent = first.customer_no || "-";
      document.getElementById("detail_customer_name").textContent = first.customer_name || "-";
      document.getElementById("detail_phone").textContent = first.phone || "-";
      document.getElementById("detail_area").textContent = first.area || "-";
      document.getElementById("detail_install_address").textContent = first.install_address || "-";
      document.getElementById("detail_install_time").textContent = first.install_time || first.year_month || "-";
      document.getElementById("detail_payment_status").textContent = first.payment_status || "-";
      document.getElementById("detail_total_amount").textContent = money(first.total_amount || 0);

      fillDetailFeeCalculator(first);
      renderPaymentHistory(customerRecords);
      renderChangeLogs(customerNo);
      renderEquipmentLogs(customerNo);

      showCustomerDetailPanel("payment");
      document.getElementById("customer_detail_modal").classList.add("active");
    }

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeCustomerDetail();
      }

      if (event.key === "Enter" && document.activeElement && document.activeElement.id === "change_log_input") {
        addChangeLog();
      }
    });

    document.addEventListener("click", function (event) {
      const modal = document.getElementById("customer_detail_modal");
      if (!modal) return;
      if (event.target === modal) {
        closeCustomerDetail();
      }
    });
    // SHINNAN_BILLING_CUSTOMER_DETAIL_HISTORY_JS_END



    // SHINNAN_BILLING_PRINT_CUSTOMER_LIST_JS_START
    function printCustomerList() {
      window.print();
    }
    // SHINNAN_BILLING_PRINT_CUSTOMER_LIST_JS_END


    document.querySelectorAll(".tab-button").forEach(function (button) {
      button.addEventListener("click", function () {
        const tab = button.getAttribute("data-tab");

        document.querySelectorAll(".tab-button").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));

        button.classList.add("active");
        document.getElementById("tab_" + tab).classList.add("active");
      });
    });


    // SHINNAN_BILLING_SUMMARY_FILTER_CARDS_JS_START
    function updateSummaryCardActive() {
      const countCard = document.getElementById("summary_count")?.closest(".summary-box");
      const normalCard = document.getElementById("summary_normal")?.closest(".summary-box");
      const abnormalCard = document.getElementById("summary_abnormal")?.closest(".summary-box");

      [countCard, normalCard, abnormalCard].forEach(function (card) {
        if (!card) return;
        card.classList.remove("summary-filter-active");
        card.classList.remove("summary-filter-abnormal-active");
      });

      if (summaryStatusFilter === "all" && countCard) {
        countCard.classList.add("summary-filter-active");
      }

      if (summaryStatusFilter === "normal" && normalCard) {
        normalCard.classList.add("summary-filter-active");
      }

      if (summaryStatusFilter === "abnormal" && abnormalCard) {
        abnormalCard.classList.add("summary-filter-abnormal-active");
      }
    }

    function setSummaryStatusFilter(mode) {
      summaryStatusFilter = mode;
      updateSummaryCardActive();
      applyFilters();
    }

    function installSummaryCardFilters() {
      const countCard = document.getElementById("summary_count")?.closest(".summary-box");
      const normalCard = document.getElementById("summary_normal")?.closest(".summary-box");
      const abnormalCard = document.getElementById("summary_abnormal")?.closest(".summary-box");

      if (countCard && countCard.dataset.filterReady !== "1") {
        countCard.dataset.filterReady = "1";
        countCard.title = "點擊顯示全部客戶";
        countCard.addEventListener("click", function () {
          setSummaryStatusFilter("all");
        });
      }

      if (normalCard && normalCard.dataset.filterReady !== "1") {
        normalCard.dataset.filterReady = "1";
        normalCard.title = "點擊只顯示正常繳費客戶";
        normalCard.addEventListener("click", function () {
          setSummaryStatusFilter("normal");
        });
      }

      if (abnormalCard && abnormalCard.dataset.filterReady !== "1") {
        abnormalCard.dataset.filterReady = "1";
        abnormalCard.title = "點擊只顯示繳費異常客戶";
        abnormalCard.addEventListener("click", function () {
          setSummaryStatusFilter("abnormal");
        });
      }

      updateSummaryCardActive();
    }
    // SHINNAN_BILLING_SUMMARY_FILTER_CARDS_JS_END


    document.getElementById("search_button").addEventListener("click", applyFilters);
    document.getElementById("clear_button").addEventListener("click", clearFilters);
    document.getElementById("area_filter").addEventListener("change", applyFilters);
    document.getElementById("global_search").addEventListener("keydown", function (event) {
      if (event.key === "Enter") applyFilters();
    });

    document.getElementById("create_customer_button").addEventListener("click", function () {
      alert("建立資料功能下一步串接。");
    });

    records = applyBuildingOverrides(BASE_RECORDS);
    setupAreas();
    installSummaryCardFilters();
    clearFilters();
  </script>



<script id="billing_notice_panel_script_v1">
(function () {
  function esc(v) {
    return String(v == null ? "" : v)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function renderBillingNoticeDisplay(notices) {
    const display = document.getElementById("billing_notice_display");
    if (!display) return;

    const items = Array.isArray(notices) ? notices : [];

    if (!items.length) {
      display.innerHTML = '<div class="billing-notice-empty">目前沒有帳務通知。</div>';
      return;
    }

    display.innerHTML = items.map(function (item, index) {
      return `
        <div class="billing-notice-row">
          <div class="billing-notice-text">${index + 1}. ${esc(item.message || "")}</div>
          <button type="button" class="billing-notice-delete" onclick="window.deleteBillingNotice(${index})">刪除</button>
        </div>
      `;
    }).join("");
  }

  async function loadBillingNotice() {
    try {
      const res = await fetch("/api/billing/notices?ts=" + Date.now(), {cache: "no-store"});
      if (!res.ok) return;
      const data = await res.json();
      renderBillingNoticeDisplay(data.notices || []);
    } catch (err) {
      console.warn("帳務通知讀取失敗", err);
    }
  }

  async function saveBillingNotice() {
    const input = document.getElementById("billing_notice_input");
    if (!input) return;

    const text = input.value.trim();

    if (!text) {
      alert("請先輸入帳務通知內容");
      return;
    }

    const res = await fetch("/api/billing/notices", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: text})
    });

    if (!res.ok) {
      alert("帳務通知送出失敗");
      return;
    }

    const data = await res.json();
    input.value = "";
    renderBillingNoticeDisplay(data.notices || []);
    alert("帳務通知已送出");
  }

  async function clearBillingNoticeInput() {
    const input = document.getElementById("billing_notice_input");
    if (input) input.value = "";
  }

  window.deleteBillingNotice = async function(index) {
    const res = await fetch("/api/billing/notices", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({delete_index: index})
    });

    if (!res.ok) {
      alert("帳務通知刪除失敗");
      return;
    }

    const data = await res.json();
    renderBillingNoticeDisplay(data.notices || []);
  };

  function bindBillingNoticePanel() {
    const save = document.getElementById("save_billing_notice_button");
    const clear = document.getElementById("clear_billing_notice_button");

    if (save) save.addEventListener("click", saveBillingNotice);
    if (clear) clear.addEventListener("click", clearBillingNoticeInput);

    loadBillingNotice();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindBillingNoticePanel);
  } else {
    bindBillingNoticePanel();
  }
})();
</script>


<script>
(function () {
  function text(v) {
    return String(v || "").trim();
  }

  function setName(name) {
    var el = document.getElementById("web_title_user_name");
    if (!el) return;
    el.textContent = text(name) || "-";
  }

  function fallbackName() {
    var keys = [
      "xunnan_employee_display_name",
      "xunnan_display_name",
      "xunnan_employee_name",
      "xunnan_engineer_name",
      "xunnan_admin_name"
    ];
    for (var i = 0; i < keys.length; i += 1) {
      try {
        var v = localStorage.getItem(keys[i]) || sessionStorage.getItem(keys[i]);
        if (text(v)) return v;
      } catch (e) {}
    }
    return "";
  }

  setName(fallbackName() || "\u767b\u5165\u8005");

  fetch("/api/app/employee/profile?ts=" + Date.now(), {
    cache: "no-store",
    credentials: "same-origin"
  })
    .then(function (res) {
      if (!res || !res.ok) return null;
      return res.json();
    })
    .then(function (data) {
      if (!data) return;
      var p = data.profile || data.data || data;
      var name =
        p.display_name ||
        p.acting_display_name ||
        p.login_display_name ||
        p.staff_code ||
        data.display_name ||
        data.staff_code ||
        "";
      setName(name || fallbackName() || "\u767b\u5165\u8005");
    })
    .catch(function () {
      setName(fallbackName() || "\u767b\u5165\u8005");
    });
})();
</script>


<script id="cl15j1_billing_layout_unify_script_v1">
(function () {
  if (!location.pathname.includes("/admin/billing")) return;

  document.body.classList.add("cl15j1-billing-layout");

  function textOf(el) {
    return String(el && el.textContent ? el.textContent : "").replace(/\\s+/g, "");
  }

  function findButtonByText(labels) {
    const buttons = Array.from(document.querySelectorAll("button"));
    return buttons.find(function (btn) {
      const t = textOf(btn);
      return labels.some(function (label) { return t === label; });
    }) || null;
  }

  function findTabByText(labels) {
    const buttons = Array.from(document.querySelectorAll("button"));
    return buttons.find(function (btn) {
      const t = textOf(btn);
      return labels.some(function (label) { return t === label; });
    }) || null;
  }

  function cloneButton(source, label) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = label;

    if (source) {
      btn.onclick = function (event) {
        event.preventDefault();
        event.stopPropagation();
        source.click();
      };
    }

    return btn;
  }


  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", installHeaderActions);
  } else {
    installHeaderActions();
  }

  setTimeout(installHeaderActions, 300);
  setTimeout(installHeaderActions, 900);
})();
</script>


<script id="cl15j7_calculator_button_animation_script_v1">
(function () {
  function getCalcButtons() {
    return Array.from(document.querySelectorAll([
      ".calculator button",
      ".calculator-grid button",
      ".calc button",
      ".calc-grid button",
      ".tool-calculator button",
      ".calculator-key",
      ".calc-key",
      ".calc-btn",
      "[data-calc-key]",
      "[data-calculator-key]"
    ].join(",")));
  }

  function bindButton(btn) {
    if (!btn || btn.dataset.cl15j7CalcBound === "1") return;
    btn.dataset.cl15j7CalcBound = "1";

    function press() {
      btn.classList.add("cl15j7-calc-pressed");
    }

    function release() {
      window.setTimeout(function () {
        btn.classList.remove("cl15j7-calc-pressed");
      }, 90);
    }

    btn.addEventListener("pointerdown", press, {passive: true});
    btn.addEventListener("pointerup", release, {passive: true});
    btn.addEventListener("pointerleave", release, {passive: true});
    btn.addEventListener("blur", release, {passive: true});
  }

  function bindAll() {
    getCalcButtons().forEach(bindButton);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindAll);
  } else {
    bindAll();
  }

  setTimeout(bindAll, 300);
  setTimeout(bindAll, 900);
})();
</script>


</body>
</html>
"""
    return html.replace("__RECORDS_JSON__", records_json)



