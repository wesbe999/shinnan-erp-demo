from __future__ import annotations

import json

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from app.config import data_file
from app.services.demo_data import generate_billing_records
from app.routes.employee_auth import _employee_current_user_from_request

router = APIRouter(tags=["帳務系統"])


_BILLING_NOTICES_FILE = data_file("billing_notices.json")


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


@router.get("/admin/billing", response_class=HTMLResponse, summary="帳務系統")
def billing_page(request: Request):
    current_user = _employee_current_user_from_request(request)
    if not current_user:
        return RedirectResponse("/employee/login?next=/admin/billing", status_code=303)

    records_json = json.dumps(generate_billing_records(), ensure_ascii=False)

    html = """
<!doctype html>
<html lang="zh-Hant">
<head>
  
  
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
<meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>訊南ERP｜帳務系統</title>

  <style>
    :root {
      --bg: #eef3f9;
      --card: #ffffff;
      --line: #d7e1ef;
      --text: #102348;
      --muted: #64748b;
      --blue: #2f80ed;
      --green: #16a34a;
      --orange: #ea580c;
      --red: #dc2626;
      --purple: #7c3aed;
      --gray: #64748b;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Microsoft JhengHei", "Segoe UI", Arial, sans-serif;
    }

    .topbar {
      background: linear-gradient(120deg, #0f766e, #2563eb);
      color: white;
      padding: 18px 34px;
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.18);
    }

    .topbar h1 {
      margin: 0;
      font-size: 32px;
      font-weight: 1000;
      letter-spacing: 2px;
    }

    .topbar p {
      margin: 6px 0 0;
      font-size: 16px;
      font-weight: 800;
      opacity: .92;
    }

    .page {
      width: min(1680px, calc(100% - 36px));
      margin: 18px auto 36px;
    }

    .toolbar {
      display: grid;
      grid-template-columns: 120px 180px minmax(520px, 1fr) 90px 90px 120px 120px;
      gap: 10px;
      align-items: center;
      margin-bottom: 14px;
      background: rgba(255,255,255,0.52);
      padding: 12px 16px;
      border-radius: 18px;
      border: 1px solid var(--line);
    }

    button, select, input {
      font-family: inherit;
      font-size: 16px;
    }

    button {
      border: 0;
      border-radius: 12px;
      padding: 8px 10px;
      min-height: 40px;
      color: white;
      font-weight: 1000;
      cursor: pointer;
      box-shadow: 0 4px 10px rgba(15, 23, 42, 0.10);
      white-space: nowrap;
    }

    .btn-blue { background: var(--blue); }
    .btn-green { background: var(--green); }
    .btn-orange { background: var(--orange); }
    .btn-gray { background: var(--gray); }
    .btn-purple { background: var(--purple); }
    .btn-red {
      background: #ffe4e6;
      color: #ff0000;
      border: 1px solid #ffb3bd;
      box-shadow: none;
    }

    input, select {
      width: 100%;
      height: 42px;
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      padding: 0 12px;
      background: white;
      color: var(--text);
      outline: none;
    }

    #global_search {
      height: 46px;
      font-size: 18px;
      border-radius: 14px;
    }

    .tabs {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 10px 0 14px;
    }

    .tab-button {
      background: white;
      color: var(--text);
      border: 1px solid var(--line);
      box-shadow: none;
      min-width: 120px;
      min-height: 42px;
    }

    .tab-button.active {
      background: var(--blue);
      color: white;
      border-color: var(--blue);
    }

    .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 18px;
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
      margin-bottom: 16px;
    }

    .card-title {
      font-size: 24px;
      font-weight: 1000;
      margin-bottom: 14px;
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
    }

    .hint {
      font-size: 14px;
      color: var(--muted);
      font-weight: 800;
    }

    .summary-row {
      display: grid;
      grid-template-columns: repeat(5, minmax(150px, 1fr));
      gap: 12px;
      margin: 10px 0 14px;
    }

    .summary-box {
      min-height: 104px;
      background: white;
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px 18px;
      box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .summary-label {
      color: #6b7280;
      font-size: 15px;
      font-weight: 1000;
      margin-bottom: 8px;
    }

    .summary-value {
      color: #111827;
      font-size: 34px;
      line-height: 1;
      font-weight: 1000;
    }

    .summary-value.red {
      color: #dc2626;
    }

    .table-wrap {
      border: 1px solid var(--line);
      border-radius: 18px;
      background: white;
      overflow-x: auto;
      overflow-y: visible;
    }

    table {
      width: 100%;
      min-width: 1560px;
      border-collapse: collapse;
      table-layout: fixed;
    }

    th {
      background: #f1f5f9;
      color: #334155;
      text-align: left;
      padding: 12px 10px;
      font-size: 14px;
      font-weight: 1000;
      border-bottom: 1px solid var(--line);
      white-space: normal;
      line-height: 1.35;
    }

    td {
      padding: 12px 10px;
      border-bottom: 1px solid #edf2f7;
      font-size: 14px;
      font-weight: 850;
      vertical-align: middle;
      line-height: 1.45;
      white-space: normal;
      word-break: break-word;
      overflow-wrap: anywhere;
    }

    tr:hover td {
      background: #f8fbff;
    }

    #tab_customers th:nth-child(1), #tab_customers td:nth-child(1) { width: 90px; }
    #tab_customers th:nth-child(2), #tab_customers td:nth-child(2) { width: 140px; }
    #tab_customers th:nth-child(3), #tab_customers td:nth-child(3) { width: 120px; }
    #tab_customers th:nth-child(4), #tab_customers td:nth-child(4) { width: 320px; }
    #tab_customers th:nth-child(5), #tab_customers td:nth-child(5) { width: 120px; }
    #tab_customers th:nth-child(6), #tab_customers td:nth-child(6) { width: 120px; }
    #tab_customers th:nth-child(7), #tab_customers td:nth-child(7) { width: 90px; text-align: center; }
    #tab_customers th:nth-child(8), #tab_customers td:nth-child(8) { width: 115px; text-align: center; }
    #tab_customers th:nth-child(9), #tab_customers td:nth-child(9) { width: 80px; text-align: center; }
    #tab_customers th:nth-child(10), #tab_customers td:nth-child(10) { width: 100px; text-align: right; }
    #tab_customers th:nth-child(11), #tab_customers td:nth-child(11) { width: 105px; text-align: right; }
    #tab_customers th:nth-child(12), #tab_customers td:nth-child(12) { width: 120px; text-align: center; }
    #tab_customers th:nth-child(13), #tab_customers td:nth-child(13) { width: 78px; text-align: center; }

    .pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      padding: 0 12px;
      min-width: 72px;
      height: 34px;
      font-size: 14px;
      font-weight: 1000;
      line-height: 1;
      white-space: nowrap;
      word-break: keep-all;
      writing-mode: horizontal-tb;
    }

    .pill-purple {
      background: #ede9fe;
      color: #5b21b6;
    }

    .pill-green {
      background: #dcfce7;
      color: #166534;
      border: 1px solid #bbf7d0;
      min-width: 92px;
    }

    .pill-red {
      background: #ffe4e6;
      color: #ff0000;
      border: 1px solid #ffb3bd;
      min-width: 92px;
    }

    .status-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 54px;
      width: 54px;
      height: 32px;
      padding: 0 8px;
      border-radius: 10px;
      font-size: 13px;
      box-shadow: none;
    }

    .tab-panel {
      display: none;
    }

    .tab-panel.active {
      display: block;
    }

    .notice-list {
      display: grid;
      gap: 10px;
    }

    .notice-area-title {
      margin: 12px 0 2px 0;
      padding: 8px 14px;
      border-radius: 999px;
      background: #ffe4e6;
      color: #ff0000;
      font-size: 18px;
      font-weight: 1000;
      border: 1px solid #ffb3bd;
      width: fit-content;
    }

    .notice-item {
      border: 1px solid #fecaca;
      background: #fff1f2;
      border-radius: 16px;
      padding: 12px 16px;
      color: #ff0000;
      font-weight: 1000;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: center;
    }

    .notice-normal {
      border: 1px solid #bbf7d0;
      background: #f0fdf4;
      color: #15803d;
    }

    .empty {
      padding: 20px;
      color: var(--muted);
      font-weight: 900;
    }

    @media (max-width: 1200px) {
      .toolbar {
        grid-template-columns: 1fr 1fr;
      }

      #global_search {
        grid-column: span 2;
      }

      .summary-row {
        grid-template-columns: repeat(2, 1fr);
      }
    }
  
    /* SHINNAN_BILLING_AREA_GROUP_ROW_START */
    .area-group-row td {
      background: #eaf2ff !important;
      color: #102348 !important;
      font-size: 20px !important;
      font-weight: 1000 !important;
      padding: 14px 16px !important;
      border-top: 2px solid #c7d8f2 !important;
      border-bottom: 2px solid #c7d8f2 !important;
      letter-spacing: 2px !important;
    }

    .area-group-label {
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      min-width: 120px !important;
      height: 42px !important;
      padding: 0 20px !important;
      border-radius: 999px !important;
      background: #ede9fe !important;
      color: #5b21b6 !important;
      font-size: 20px !important;
      font-weight: 1000 !important;
      white-space: nowrap !important;
    }
    /* SHINNAN_BILLING_AREA_GROUP_ROW_END */

  
    /* SHINNAN_BILLING_COMPACT_ROWS_NAME_ADDRESS_START */

    /* 表格列高縮小 */
    #tab_customers th {
      padding-top: 6px !important;
      padding-bottom: 6px !important;
      font-size: 13px !important;
      line-height: 1.2 !important;
    }

    #tab_customers td {
      padding-top: 5px !important;
      padding-bottom: 5px !important;
      font-size: 13px !important;
      line-height: 1.25 !important;
      vertical-align: middle !important;
    }

    /* 區域分隔列也壓低 */
    .area-group-row td {
      padding-top: 7px !important;
      padding-bottom: 7px !important;
    }

    .area-group-label {
      height: 30px !important;
      min-width: 90px !important;
      font-size: 15px !important;
      padding: 0 14px !important;
    }

    /* 客戶名稱欄：縮小約一半 */
    #tab_customers th:nth-child(2),
    #tab_customers td:nth-child(2) {
      width: 72px !important;
      max-width: 72px !important;
      white-space: normal !important;
      word-break: keep-all !important;
      overflow-wrap: normal !important;
    }

    /* 裝機地址欄：減少約 1/3 */
    #tab_customers th:nth-child(4),
    #tab_customers td:nth-child(4) {
      width: 210px !important;
      max-width: 210px !important;
      white-space: normal !important;
      word-break: break-word !important;
      overflow-wrap: anywhere !important;
    }

    /* 膠囊與按鈕跟著壓低 */
    #tab_customers .pill {
      height: 28px !important;
      min-height: 28px !important;
      padding: 0 10px !important;
      font-size: 12px !important;
    }

    #tab_customers .status-button {
      height: 28px !important;
      min-height: 28px !important;
      width: 48px !important;
      min-width: 48px !important;
      font-size: 12px !important;
      border-radius: 9px !important;
    }

    /* SHINNAN_BILLING_COMPACT_ROWS_NAME_ADDRESS_END */

  
    /* SHINNAN_BILLING_CUSTOMER_DETAIL_HISTORY_START */

    /* 收據單號、確認編號各縮小約 1/3 */
    #tab_customers th:nth-child(5),
    #tab_customers td:nth-child(5) {
      width: 80px !important;
      max-width: 80px !important;
      font-size: 12px !important;
    }

    #tab_customers th:nth-child(6),
    #tab_customers td:nth-child(6) {
      width: 80px !important;
      max-width: 80px !important;
      font-size: 12px !important;
    }

    #tab_customers th:nth-child(7),
    #tab_customers td:nth-child(7) {
      width: 105px !important;
      max-width: 105px !important;
      text-align: center !important;
    }

    .customer-row {
      cursor: pointer !important;
    }

    .customer-row:hover td {
      background: #eef6ff !important;
    }

    .customer-detail-mask {
      position: fixed;
      inset: 0;
      z-index: 200;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: rgba(15, 23, 42, 0.58);
    }

    .customer-detail-mask.active {
      display: flex;
    }

    .customer-detail-modal {
      width: min(1180px, 100%);
      max-height: 92vh;
      overflow: auto;
      background: #ffffff;
      border-radius: 26px;
      border: 1px solid #d7e1ef;
      box-shadow: 0 28px 90px rgba(15, 23, 42, 0.34);
      padding: 24px;
    }

    .customer-detail-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
    }

    .customer-detail-title {
      font-size: 30px;
      font-weight: 1000;
      color: #102348;
    }

    .customer-detail-close {
      width: 88px;
      height: 40px;
      border-radius: 12px;
      border: 0;
      background: #64748b;
      color: white;
      font-size: 16px;
      font-weight: 1000;
      cursor: pointer;
    }

    .customer-detail-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 18px;
    }

    .customer-detail-field {
      background: #f8fbff;
      border: 1px solid #d7e1ef;
      border-radius: 16px;
      padding: 14px;
    }

    .customer-detail-label {
      color: #64748b;
      font-size: 13px;
      font-weight: 1000;
      margin-bottom: 6px;
    }

    .customer-detail-value {
      color: #102348;
      font-size: 18px;
      font-weight: 1000;
      line-height: 1.35;
      word-break: break-word;
    }

    .payment-history-title {
      font-size: 22px;
      font-weight: 1000;
      margin: 12px 0;
      color: #102348;
    }

    .payment-history-wrap {
      border: 1px solid #d7e1ef;
      border-radius: 18px;
      overflow: auto;
    }

    .payment-history-table {
      width: 100%;
      min-width: 900px;
      border-collapse: collapse;
      table-layout: fixed;
    }

    .payment-history-table th {
      background: #f1f5f9;
      padding: 10px;
      font-size: 14px;
      font-weight: 1000;
      color: #334155;
      border-bottom: 1px solid #d7e1ef;
    }

    .payment-history-table td {
      padding: 10px;
      font-size: 14px;
      font-weight: 850;
      border-bottom: 1px solid #edf2f7;
      text-align: center;
    }

    @media (max-width: 900px) {
      .customer-detail-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    @media (max-width: 560px) {
      .customer-detail-grid {
        grid-template-columns: 1fr;
      }
    }

    /* SHINNAN_BILLING_CUSTOMER_DETAIL_HISTORY_END */

      /* SHINNAN_BILLING_FIT_ALL_COLUMNS_START */

    /* 客戶清單：強制全部欄位塞進畫面，不使用橫向捲動 */
    #tab_customers .table-wrap {
      overflow-x: visible !important;
      overflow-y: visible !important;
      width: 100% !important;
    }

    #tab_customers table {
      width: 100% !important;
      min-width: 0 !important;
      table-layout: fixed !important;
      border-collapse: collapse !important;
    }

    #tab_customers th,
    #tab_customers td {
      padding: 5px 4px !important;
      font-size: 11px !important;
      line-height: 1.18 !important;
      vertical-align: middle !important;
      white-space: normal !important;
      word-break: break-word !important;
      overflow-wrap: anywhere !important;
    }

    #tab_customers th {
      font-size: 11px !important;
      font-weight: 1000 !important;
      text-align: center !important;
    }

    /* 13 欄寬度重新分配：地址最大，其餘壓縮 */
    #tab_customers th:nth-child(1),
    #tab_customers td:nth-child(1) {
      width: 5.2% !important;
    }

    #tab_customers th:nth-child(2),
    #tab_customers td:nth-child(2) {
      width: 5.4% !important;
    }

    #tab_customers th:nth-child(3),
    #tab_customers td:nth-child(3) {
      width: 6.4% !important;
    }

    /* 裝機地址：保留最大空間 */
    #tab_customers th:nth-child(4),
    #tab_customers td:nth-child(4) {
      width: 20.5% !important;
      font-size: 11px !important;
      line-height: 1.2 !important;
    }

    /* 收據單號 */
    #tab_customers th:nth-child(5),
    #tab_customers td:nth-child(5) {
      width: 7.2% !important;
      font-size: 10.5px !important;
    }

    /* 確認編號 */
    #tab_customers th:nth-child(6),
    #tab_customers td:nth-child(6) {
      width: 7.2% !important;
      font-size: 10.5px !important;
    }

    /* 裝機時間 */
    #tab_customers th:nth-child(7),
    #tab_customers td:nth-child(7) {
      width: 7.2% !important;
      text-align: center !important;
      font-size: 10.5px !important;
    }

    /* 繳費期限 */
    #tab_customers th:nth-child(8),
    #tab_customers td:nth-child(8) {
      width: 7.2% !important;
      text-align: center !important;
      font-size: 10.5px !important;
    }

    /* 逾期天數 */
    #tab_customers th:nth-child(9),
    #tab_customers td:nth-child(9) {
      width: 4.4% !important;
      text-align: center !important;
    }

    /* 月租費 */
    #tab_customers th:nth-child(10),
    #tab_customers td:nth-child(10) {
      width: 5.5% !important;
      text-align: right !important;
    }

    /* 應繳金額 */
    #tab_customers th:nth-child(11),
    #tab_customers td:nth-child(11) {
      width: 5.8% !important;
      text-align: right !important;
    }

    /* 繳費狀態 */
    #tab_customers th:nth-child(12),
    #tab_customers td:nth-child(12) {
      width: 8.5% !important;
      text-align: center !important;
    }

    /* 異常 */
    #tab_customers th:nth-child(13),
    #tab_customers td:nth-child(13) {
      width: 4.5% !important;
      text-align: center !important;
    }

    #tab_customers .pill {
      min-width: 0 !important;
      height: 24px !important;
      padding: 0 6px !important;
      font-size: 10.5px !important;
      border-radius: 999px !important;
      white-space: nowrap !important;
      word-break: keep-all !important;
    }

    #tab_customers .status-button {
      min-width: 36px !important;
      width: 36px !important;
      height: 24px !important;
      padding: 0 4px !important;
      font-size: 10.5px !important;
      border-radius: 8px !important;
      white-space: nowrap !important;
    }

    .area-group-row td {
      padding: 5px 8px !important;
    }

    .area-group-label {
      height: 26px !important;
      min-width: 78px !important;
      padding: 0 12px !important;
      font-size: 13px !important;
    }

    /* 頁面左右留白縮小，給表格更多寬度 */
    .page {
      width: calc(100% - 16px) !important;
      max-width: none !important;
      margin-left: 8px !important;
      margin-right: 8px !important;
    }

    .card {
      padding: 12px !important;
    }

    /* SHINNAN_BILLING_FIT_ALL_COLUMNS_END */
  
    /* SHINNAN_BILLING_CUSTOMER_DETAIL_EXTENDED_START */
    .customer-detail-mask {
      position: fixed;
      inset: 0;
      z-index: 200;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: rgba(15, 23, 42, 0.58);
    }

    .customer-detail-mask.active {
      display: flex;
    }

    .customer-detail-modal {
      width: min(1280px, 100%);
      max-height: 92vh;
      overflow: auto;
      background: #ffffff;
      border-radius: 26px;
      border: 1px solid #d7e1ef;
      box-shadow: 0 28px 90px rgba(15, 23, 42, 0.34);
      padding: 24px;
    }

    .customer-detail-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
    }

    .customer-detail-title {
      font-size: 30px;
      font-weight: 1000;
      color: #102348;
    }

    .customer-detail-close {
      width: 88px;
      height: 40px;
      border-radius: 12px;
      border: 0;
      background: #64748b;
      color: white;
      font-size: 16px;
      font-weight: 1000;
      cursor: pointer;
    }

    .customer-detail-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 18px;
    }

    .customer-detail-field {
      background: #f8fbff;
      border: 1px solid #d7e1ef;
      border-radius: 16px;
      padding: 14px;
    }

    .customer-detail-label {
      color: #64748b;
      font-size: 13px;
      font-weight: 1000;
      margin-bottom: 6px;
    }

    .customer-detail-value {
      color: #102348;
      font-size: 18px;
      font-weight: 1000;
      line-height: 1.35;
      word-break: break-word;
    }

    .detail-section-title {
      font-size: 22px;
      font-weight: 1000;
      margin: 18px 0 10px;
      color: #102348;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .detail-two-column {
      display: grid;
      grid-template-columns: 1.15fr .85fr;
      gap: 16px;
      align-items: start;
    }

    .detail-table-wrap {
      border: 1px solid #d7e1ef;
      border-radius: 18px;
      overflow: auto;
      background: #ffffff;
    }

    .detail-table {
      width: 100%;
      min-width: 880px;
      border-collapse: collapse;
      table-layout: fixed;
    }

    .detail-table th {
      background: #f1f5f9;
      padding: 10px;
      font-size: 14px;
      font-weight: 1000;
      color: #334155;
      border-bottom: 1px solid #d7e1ef;
      text-align: center;
    }

    .detail-table td {
      padding: 10px;
      font-size: 14px;
      font-weight: 850;
      border-bottom: 1px solid #edf2f7;
      text-align: center;
      word-break: break-word;
    }

    .change-log-box {
      border: 1px solid #d7e1ef;
      border-radius: 18px;
      background: #ffffff;
      padding: 14px;
    }

    .change-input-grid {
      display: grid;
      grid-template-columns: 1fr 120px;
      gap: 10px;
      margin-bottom: 12px;
    }

    .change-input-grid input {
      height: 42px;
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      padding: 0 12px;
      font-size: 15px;
      font-family: inherit;
    }

    .change-input-grid button {
      height: 42px;
      border: 0;
      border-radius: 12px;
      background: #2f80ed;
      color: white;
      font-size: 15px;
      font-weight: 1000;
      cursor: pointer;
    }

    .change-log-list {
      display: grid;
      gap: 8px;
      max-height: 360px;
      overflow: auto;
      padding-right: 4px;
    }

    .change-log-item {
      border: 1px solid #d7e1ef;
      background: #f8fbff;
      border-radius: 14px;
      padding: 10px 12px;
    }

    .change-log-time {
      color: #64748b;
      font-size: 12px;
      font-weight: 900;
      margin-bottom: 4px;
    }

    .change-log-text {
      color: #102348;
      font-size: 15px;
      font-weight: 900;
      line-height: 1.45;
      word-break: break-word;
    }

    .empty-change-log {
      color: #64748b;
      font-weight: 900;
      padding: 12px;
      text-align: center;
    }

    @media (max-width: 1000px) {
      .customer-detail-grid {
        grid-template-columns: repeat(2, 1fr);
      }

      .detail-two-column {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 560px) {
      .customer-detail-grid {
        grid-template-columns: 1fr;
      }

      .change-input-grid {
        grid-template-columns: 1fr;
      }
    }
    /* SHINNAN_BILLING_CUSTOMER_DETAIL_EXTENDED_END */

  
    /* SHINNAN_CUSTOMER_DETAIL_SWITCH_BUTTONS_START */
    .detail-switch-bar {
      display: flex;
      gap: 12px;
      margin: 18px 0 14px;
    }

    .detail-switch-button {
      min-width: 180px;
      height: 46px;
      border: 0;
      border-radius: 14px;
      background: #e2e8f0;
      color: #102348;
      font-size: 17px;
      font-weight: 1000;
      cursor: pointer;
      box-shadow: 0 4px 10px rgba(15, 23, 42, 0.08);
    }

    .detail-switch-button.active {
      background: #2f80ed;
      color: #ffffff;
    }

    .detail-panel {
      display: none;
    }

    .detail-panel.active {
      display: block;
    }

    .detail-section-title {
      font-size: 22px;
      font-weight: 1000;
      margin: 12px 0;
      color: #102348;
    }

    .detail-two-column {
      display: block !important;
    }
    /* SHINNAN_CUSTOMER_DETAIL_SWITCH_BUTTONS_END */

      /* SHINNAN_BILLING_SUMMARY_ONE_ROW_COMPACT_START */

    .summary-row {
      display: grid !important;
      grid-template-columns: repeat(5, 1fr) !important;
      gap: 10px !important;
      margin: 8px 0 12px !important;
    }

    .summary-box {
      min-height: 82px !important;
      height: 82px !important;
      padding: 10px 14px !important;
      border-radius: 16px !important;
      background: #ffffff !important;
      border: 1px solid #d7e1ef !important;
      box-shadow: 0 6px 14px rgba(15, 23, 42, 0.05) !important;
      display: flex !important;
      flex-direction: column !important;
      justify-content: center !important;
      align-items: flex-start !important;
    }

    .summary-label {
      color: #6b7280 !important;
      font-size: 13px !important;
      font-weight: 1000 !important;
      margin: 0 0 6px 0 !important;
      line-height: 1.1 !important;
      white-space: nowrap !important;
    }

    .summary-value {
      color: #111827 !important;
      font-size: 30px !important;
      line-height: 1 !important;
      font-weight: 1000 !important;
      margin: 0 !important;
      white-space: nowrap !important;
    }

    .summary-value.red {
      color: #dc2626 !important;
    }

    #summary_area {
      font-size: 24px !important;
    }

    @media (max-width: 1200px) {
      .summary-row {
        grid-template-columns: repeat(3, 1fr) !important;
      }
    }

    @media (max-width: 760px) {
      .summary-row {
        grid-template-columns: repeat(2, 1fr) !important;
      }
    }

    @media (max-width: 520px) {
      .summary-row {
        grid-template-columns: 1fr !important;
      }
    }

    /* SHINNAN_BILLING_SUMMARY_ONE_ROW_COMPACT_END */
      /* SHINNAN_BILLING_SUMMARY_HALF_WIDTH_START */

    .summary-row {
      display: grid !important;
      grid-template-columns: repeat(5, 150px) !important;
      justify-content: start !important;
      gap: 10px !important;
      margin: 8px 0 12px !important;
    }

    .summary-box {
      width: 150px !important;
      min-width: 150px !important;
      max-width: 150px !important;
      height: 78px !important;
      min-height: 78px !important;
      padding: 8px 12px !important;
      border-radius: 14px !important;
    }

    .summary-label {
      font-size: 12px !important;
      margin-bottom: 5px !important;
    }

    .summary-value {
      font-size: 26px !important;
      line-height: 1 !important;
    }

    #summary_area {
      font-size: 22px !important;
    }

    @media (max-width: 900px) {
      .summary-row {
        grid-template-columns: repeat(2, 150px) !important;
      }
    }

    @media (max-width: 420px) {
      .summary-row {
        grid-template-columns: 1fr !important;
      }

      .summary-box {
        width: 100% !important;
        max-width: none !important;
      }
    }

    /* SHINNAN_BILLING_SUMMARY_HALF_WIDTH_END */
      /* SHINNAN_BILLING_TOOLBAR_INLINE_SEARCH_BUTTONS_START */

    .toolbar {
      display: grid !important;
      grid-template-columns: 120px 180px minmax(520px, 1fr) 72px 72px 120px 120px !important;
      gap: 8px !important;
      align-items: center !important;
      width: 100% !important;
      padding: 10px 12px !important;
      border-radius: 18px !important;
      margin-bottom: 12px !important;
    }

    #global_search {
      height: 46px !important;
      min-height: 46px !important;
      font-size: 18px !important;
      border-radius: 14px !important;
    }

    #search_button,
    #clear_button {
      width: 72px !important;
      min-width: 72px !important;
      max-width: 72px !important;
      height: 38px !important;
      min-height: 38px !important;
      padding: 4px 8px !important;
      font-size: 15px !important;
      border-radius: 11px !important;
      justify-self: start !important;
      box-shadow: 0 3px 8px rgba(15, 23, 42, 0.10) !important;
    }

    #create_customer_button {
      width: 120px !important;
      min-width: 120px !important;
      max-width: 120px !important;
      height: 40px !important;
      min-height: 40px !important;
      font-size: 15px !important;
      border-radius: 12px !important;
    }

    .toolbar button[onclick*="開立發票"],
    .toolbar button.btn-orange {
      width: 120px !important;
      min-width: 120px !important;
      max-width: 120px !important;
      height: 40px !important;
      min-height: 40px !important;
      font-size: 15px !important;
      border-radius: 12px !important;
    }

    .toolbar input,
    .toolbar select {
      height: 42px !important;
      min-height: 42px !important;
      font-size: 16px !important;
      border-radius: 12px !important;
    }

    @media (max-width: 1200px) {
      .toolbar {
        grid-template-columns: 1fr 1fr !important;
      }

      #global_search {
        grid-column: span 2 !important;
      }

      #search_button,
      #clear_button,
      #create_customer_button,
      .toolbar button.btn-orange {
        width: 100% !important;
        max-width: none !important;
      }
    }

    @media (max-width: 620px) {
      .toolbar {
        grid-template-columns: 1fr !important;
      }

      #global_search {
        grid-column: span 1 !important;
      }
    }

    /* SHINNAN_BILLING_TOOLBAR_INLINE_SEARCH_BUTTONS_END */
  
    /* SHINNAN_BILLING_ACTION_TABS_FIXED_ROW_START */

    .toolbar {
      display: grid !important;
      grid-template-columns: 120px 170px minmax(760px, 1fr) 70px 70px !important;
      gap: 8px !important;
      align-items: center !important;
      width: 100% !important;
      padding: 10px 12px !important;
      border-radius: 18px !important;
      margin-bottom: 12px !important;
    }

    #global_search {
      width: 100% !important;
      height: 44px !important;
      min-height: 44px !important;
      font-size: 17px !important;
      border-radius: 13px !important;
      grid-column: auto !important;
    }

    #search_button,
    #clear_button {
      width: 70px !important;
      min-width: 70px !important;
      max-width: 70px !important;
      height: 36px !important;
      min-height: 36px !important;
      padding: 4px 6px !important;
      font-size: 14px !important;
      border-radius: 10px !important;
    }

    .toolbar button {
      height: 38px !important;
      min-height: 38px !important;
      padding: 4px 8px !important;
      font-size: 14px !important;
      border-radius: 10px !important;
    }

    .tabs {
      display: flex !important;
      flex-direction: row !important;
      align-items: center !important;
      justify-content: flex-start !important;
      gap: 12px !important;
      margin: 12px 0 14px !important;
      flex-wrap: nowrap !important;
    }

    .tabs .tab-button {
      width: 180px !important;
      min-width: 180px !important;
      max-width: 180px !important;
      height: 58px !important;
      min-height: 58px !important;
      padding: 0 18px !important;
      border-radius: 18px !important;
      font-size: 22px !important;
      font-weight: 1000 !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      white-space: nowrap !important;
      box-shadow: 0 6px 14px rgba(15, 23, 42, 0.10) !important;
    }

    .create-tab-button {
      background: #7c3aed !important;
      color: #ffffff !important;
      border: 0 !important;
    }

    .invoice-tab-button {
      background: #ea580c !important;
      color: #ffffff !important;
      border: 0 !important;
    }

    .tab-button[data-tab="customers"] {
      background: #2f80ed !important;
      color: #ffffff !important;
      border: 0 !important;
    }

    @media (max-width: 1200px) {
      .toolbar {
        grid-template-columns: 120px 170px minmax(420px, 1fr) 70px 70px !important;
      }
    }

    /* SHINNAN_BILLING_ACTION_TABS_FIXED_ROW_END */

      /* SHINNAN_BILLING_ACTION_BUTTONS_TRUE_EQUAL_START */

    .tabs {
      display: flex !important;
      flex-direction: row !important;
      align-items: center !important;
      justify-content: flex-start !important;
      gap: 16px !important;
      flex-wrap: nowrap !important;
      width: auto !important;
    }

    .tabs #create_customer_button,
    .tabs .invoice-tab-button,
    .tabs .tab-button[data-tab="customers"] {
      width: 180px !important;
      min-width: 180px !important;
      max-width: 180px !important;
      flex-grow: 0 !important;
      flex-shrink: 0 !important;
      flex-basis: 180px !important;
      align-self: flex-start !important;

      height: 58px !important;
      min-height: 58px !important;
      padding: 0 18px !important;
      border-radius: 18px !important;
      font-size: 22px !important;
      font-weight: 1000 !important;

      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      white-space: nowrap !important;
    }

    .tabs #create_customer_button {
      background: #7c3aed !important;
      color: #ffffff !important;
      border: 0 !important;
    }

    .tabs .invoice-tab-button {
      background: #ea580c !important;
      color: #ffffff !important;
      border: 0 !important;
    }

    .tabs .tab-button[data-tab="customers"] {
      background: #2f80ed !important;
      color: #ffffff !important;
      border: 0 !important;
    }

    /* 防止舊樣式把第一顆按鈕拉滿 */
    .tabs #create_customer_button.create-tab-button,
    .tabs button#create_customer_button {
      width: 180px !important;
      max-width: 180px !important;
      flex: 0 0 180px !important;
    }

    /* SHINNAN_BILLING_ACTION_BUTTONS_TRUE_EQUAL_END */
  
    /* SHINNAN_BILLING_SUMMARY_FILTER_CARDS_START */

    .summary-box {
      cursor: pointer !important;
      user-select: none !important;
      transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease, background .12s ease !important;
    }

    .summary-box:hover {
      transform: translateY(-2px) !important;
      box-shadow: 0 10px 22px rgba(15, 23, 42, 0.12) !important;
      border-color: #93c5fd !important;
      background: #f8fbff !important;
    }

    .summary-box.summary-filter-active {
      border-color: #2f80ed !important;
      background: #eef6ff !important;
      box-shadow: 0 10px 22px rgba(47, 128, 237, 0.16) !important;
    }

    .summary-box.summary-filter-abnormal-active {
      border-color: #ff9aaa !important;
      background: #fff1f2 !important;
      box-shadow: 0 10px 22px rgba(220, 38, 38, 0.14) !important;
    }

    /* SHINNAN_BILLING_SUMMARY_FILTER_CARDS_END */

  
    /* SHINNAN_BILLING_PRINT_CUSTOMER_LIST_START */

    .customer-list-title-row {
      display: flex !important;
      align-items: center !important;
      justify-content: space-between !important;
      gap: 12px !important;
    }

    .print-list-button {
      width: 120px !important;
      height: 40px !important;
      min-height: 40px !important;
      border: 0 !important;
      border-radius: 12px !important;
      background: #0f766e !important;
      color: #ffffff !important;
      font-size: 15px !important;
      font-weight: 1000 !important;
      cursor: pointer !important;
      box-shadow: 0 4px 10px rgba(15, 23, 42, 0.10) !important;
      white-space: nowrap !important;
    }

    @media print {
      body {
        background: white !important;
      }

      .topbar,
      .toolbar,
      .tabs,
      .summary-row,
      .print-list-button,
      .customer-detail-mask {
        display: none !important;
      }

      .page {
        width: 100% !important;
        margin: 0 !important;
      }

      .card {
        border: 0 !important;
        box-shadow: none !important;
        padding: 0 !important;
      }

      .card-title {
        font-size: 22px !important;
        margin-bottom: 10px !important;
      }

      #tab_customers .table-wrap {
        overflow: visible !important;
        border: 0 !important;
      }

      #tab_customers table {
        width: 100% !important;
        min-width: 0 !important;
        table-layout: fixed !important;
      }

      #tab_customers th,
      #tab_customers td {
        font-size: 9px !important;
        padding: 4px 3px !important;
        color: #000 !important;
      }

      .area-group-row td {
        font-size: 12px !important;
        padding: 5px !important;
      }
    }

    /* SHINNAN_BILLING_PRINT_CUSTOMER_LIST_END */

      /* SHINNAN_FEE_CALC_NOTE_START */
    .fee-note {
      margin-top: 10px;
      color: #64748b;
      font-size: 13px;
      font-weight: 900;
    }

    #detail_install_fee,
    #detail_deposit {
      background: #f8fafc !important;
      color: #64748b !important;
    }
    /* SHINNAN_FEE_CALC_NOTE_END */
  
    /* SHINNAN_MODAL_FEE_CALC_BLOCK_START */
    .detail-fee-card {
      background: #f8fbff;
      border: 1px solid #d7e1ef;
      border-radius: 18px;
      padding: 14px;
      margin: 10px 0 16px;
    }

    .detail-fee-title {
      font-size: 22px;
      font-weight: 1000;
      color: #102348;
      margin-bottom: 12px;
    }

    .fee-form-row {
      display: flex;
      flex-wrap: wrap;
      align-items: end;
      gap: 10px;
    }

    .fee-field {
      display: grid;
      gap: 5px;
    }

    .fee-field label {
      font-size: 13px;
      font-weight: 1000;
      color: #64748b;
      white-space: nowrap;
    }

    .fee-field input {
      width: 104px;
      height: 38px;
      border: 1px solid #cbd5e1;
      border-radius: 11px;
      padding: 0 10px;
      font-size: 15px;
      font-weight: 900;
      color: #102348;
      text-align: right;
      font-family: inherit;
    }

    #detail_install_fee,
    #detail_deposit {
      background: #f8fafc !important;
      color: #64748b !important;
      border-color: #cbd5e1 !important;
    }

    .fee-field.fee-total input {
      width: 136px;
      background: #fff7ed;
      border-color: #fdba74;
      color: #9a3412;
      font-weight: 1000;
    }

    .fee-symbol {
      height: 38px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      font-weight: 1000;
      color: #102348;
      padding-bottom: 2px;
    }

    .fee-note {
      margin-top: 10px;
      color: #64748b;
      font-size: 13px;
      font-weight: 900;
    }
    /* SHINNAN_MODAL_FEE_CALC_BLOCK_END */

  
    /* SHINNAN_FIX_FEE_TWO_ROWS_EQUIPMENT_START */
    .fee-display-row {
      margin-bottom: 12px !important;
    }

    .fee-calc-row {
      margin-top: 4px !important;
    }

    .detail-switch-bar {
      display: flex !important;
      flex-direction: row !important;
      gap: 12px !important;
      flex-wrap: wrap !important;
      margin: 18px 0 14px !important;
    }

    .detail-switch-button {
      min-width: 180px !important;
      height: 46px !important;
      border: 0 !important;
      border-radius: 14px !important;
      background: #e2e8f0 !important;
      color: #102348 !important;
      font-size: 17px !important;
      font-weight: 1000 !important;
      cursor: pointer !important;
      box-shadow: 0 4px 10px rgba(15, 23, 42, 0.08) !important;
    }

    .detail-switch-button.active {
      background: #2f80ed !important;
      color: #ffffff !important;
    }
    /* SHINNAN_FIX_FEE_TWO_ROWS_EQUIPMENT_END */

  
    /* BILLING_HEADER_LOGO_FIX_START */
    .billing-title-row {
      display: flex;
      align-items: center;
      gap: 18px;
    }

    .billing-title-logo {
      width: 72px;
      height: 52px;
      object-fit: contain;
      display: block;
      filter: drop-shadow(0 4px 8px rgba(0,0,0,.18));
    }

    .billing-title-text {
      display: grid;
      gap: 6px;
    }
    /* BILLING_HEADER_LOGO_FIX_END */

</style>

<style id="billing_notice_panel_style_v1">
  #billing_notice_panel {
    background: #fff7ed;
    border: 2px solid #fdba74;
    border-radius: 16px;
    padding: 12px 14px;
    margin: 12px 0 14px;
    box-shadow: 0 6px 18px rgba(15,23,42,.06);
  }

  #billing_notice_panel .billing-notice-title {
    font-size: 20px;
    font-weight: 1000;
    color: #c2410c;
    line-height: 1.2;
  }

  #billing_notice_panel .billing-notice-subtitle {
    margin-top: 3px;
    color: #9a3412;
    font-size: 13px;
    font-weight: 900;
    line-height: 1.25;
  }

  .billing-notice-input-box {
    margin-top: 10px;
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto auto;
    gap: 8px;
    align-items: stretch;
  }

  #billing_notice_input {
    width: 100%;
    height: 38px;
    min-height: 38px;
    max-height: 120px;
    padding: 7px 10px;
    border: 0;
    border-radius: 12px;
    background: #fff;
    color: #102348;
    font-size: 14px;
    font-weight: 900;
    line-height: 1.35;
    outline: none;
    resize: vertical;
    box-shadow: inset 0 0 0 1px #fdba74;
  }

  .billing-notice-send,
  .billing-notice-clear {
    height: 38px;
    border: 0;
    border-radius: 12px;
    padding: 0 14px;
    color: #fff;
    font-size: 13px;
    font-weight: 1000;
    cursor: pointer;
  }

  .billing-notice-send {
    background: #ea580c;
  }

  .billing-notice-clear {
    background: #64748b;
  }

  #billing_notice_display {
    margin-top: 9px;
  }

  .billing-notice-empty {
    min-height: 34px;
    display: flex;
    align-items: center;
    color: #9a3412;
    font-size: 13px;
    font-weight: 900;
  }

  .billing-notice-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 56px;
    align-items: center;
    gap: 8px;
    min-height: 38px;
    border-bottom: 1px solid #fed7aa;
  }

  .billing-notice-row:last-child {
    border-bottom: 0;
  }

  .billing-notice-text {
    color: #7c2d12;
    font-size: 13px;
    font-weight: 900;
    line-height: 1.35;
  }

  .billing-notice-delete {
    width: 54px;
    height: 28px;
    border: 0;
    border-radius: 10px;
    background: #dc2626;
    color: #fff;
    font-size: 12px;
    font-weight: 1000;
    cursor: pointer;
  }
</style>

</head>

<body>
  <div class="topbar">
    <div class="billing-title-row">
      <img class="billing-title-logo" src="/erp-static/shinnan_home_logo.png" alt="訊南 Logo">
      <div class="billing-title-text">
        <h1>帳務系統</h1>
      </div>
    </div>
    <p>統一測試資料來源：大樓、客戶、會計同步顯示</p>
  </div>

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
      <button class="btn-blue" type="button" onclick="location.href='/'">返回首頁</button>

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

</body>
</html>
"""
    return html.replace("__RECORDS_JSON__", records_json)




