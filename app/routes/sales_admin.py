from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.routes.employee_auth import _employee_current_user_from_request


router = APIRouter(tags=["sales-admin"])


# SHINNAN_SALES_PAGE_ROUTE_START
@router.get("/admin/sales", response_class=HTMLResponse, summary="業務管理系統")
def shinnan_admin_sales_page(request: Request):
    _user = _employee_current_user_from_request(request)
    if not _user:
        return RedirectResponse(f"/employee/login?next=/admin/sales", status_code=303)
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>\u696d\u52d9\u7ba1\u7406\u7cfb\u7d71\uff5c\u4e2d\u592e\u63a7\u7ba1\u7cfb\u7d71</title>
  <style>
    :root {
      --bg:#eef3f9;
      --card:#ffffff;
      --line:#d7e1ef;
      --text:#102348;
      --muted:#64748b;
      --blue:#365ee8;
      --green:#16a34a;
      --orange:#ea580c;
      --red:#dc2626;
      --purple:#7c3aed;
      --teal:#0f766e;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .wrap {
      max-width: 1460px;
      margin: 0 auto;
      padding: 22px;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
    }

    h1 {
      margin: 0;
      font-size: 32px;
      font-weight: 1000;
    }

    .subtitle {
      margin-top: 6px;
      color: var(--muted);
      font-size: 14px;
      font-weight: 800;
    }

    .actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }


    .btn-home { background:#4f7ee8; }
    .btn-green { background:var(--green); }
    .btn-blue { background:var(--blue); }
    .btn-gray { background:#64748b; }
    .btn-orange { background:var(--orange); }
    .btn-purple { background:var(--purple); }

    .stats {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 8px;
      margin-bottom: 10px;
    }

    .stat-card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 8px 12px;
      min-height: 64px;
      box-shadow: 0 8px 20px rgba(15,23,42,.06);
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .stat-label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
      line-height: 1.25;
      white-space: nowrap;
    }

    .stat-number {
      margin-top: 4px;
      font-size: 24px;
      line-height: 1;
      font-weight: 1000;
    }

    .panel {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      box-shadow: 0 12px 34px rgba(15,23,42,.08);
      margin-bottom: 16px;
    }

    .schedule-panel {
      border: 1px solid rgba(37, 99, 235, 0.22);
      background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    }

    .schedule-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 8px;
    }

    .schedule-title {
      font-size: 22px;
      font-weight: 1000;
      color: #102348;
    }

    .schedule-sub {
      color: #64748b;
      font-size: 13px;
      font-weight: 800;
    }

    .schedule-list {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }

    .schedule-card {
      border: 1px solid #dbe7f5;
      border-radius: 16px;
      padding: 12px;
      background: #ffffff;
      box-shadow: 0 10px 24px rgba(15,23,42,.06);
    }

    .schedule-card.important {
      border-color: #f59e0b;
      background: #fffbeb;
    }

    .schedule-card-title {
      font-size: 17px;
      font-weight: 1000;
      margin-bottom: 6px;
    }

    .schedule-card-line {
      color: #475569;
      font-size: 13px;
      font-weight: 800;
      line-height: 1.55;
    }

    .schedule-empty {
      padding: 14px;
      border: 1px dashed #cbd5e1;
      border-radius: 14px;
      color: #64748b;
      font-weight: 800;
      background: #f8fafc;
    }

    .check-row {
      display: flex;
      align-items: center;
      gap: 10px;
      min-height: 36px;
      padding: 8px 10px;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      background: #f8fafc;
      font-weight: 900;
      color: #334155;
    }

    .check-row input {
      width: 18px !important;
      height: 18px !important;
      min-height: 18px !important;
      padding: 0 !important;
    }

    .filters {
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 12px;
      align-items: end;
    }

    label {
      display: block;
      margin-bottom: 5px;
      color: #475569;
      font-size: 14px;
      font-weight: 900;
    }

    input, select, textarea {
      width: 100%;
      height: 36px;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      padding: 0 10px;
      font-size: 15px;
      background: #f8fafc;
      color: var(--text);
    }

    textarea {
      height: 84px;
      padding: 8px 10px;
      resize: vertical;
    }

    table {
      width: 100%;
      border-collapse: collapse;
    }

    th, td {
      padding: 11px 9px;
      border-bottom: 1px solid #e5edf7;
      text-align: left;
      font-size: 14px;
      vertical-align: top;
    }

    th {
      background: #eaf2ff;
      color: #24415f;
      font-weight: 1000;
      white-space: nowrap;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 72px;
      min-height: 24px;
      padding: 3px 9px;
      border-radius: 999px;
      background: #eef2ff;
      color: #3730a3;
      font-size: 13px;
      font-weight: 900;
      white-space: nowrap;
    }

    .pill-green { background:#dcfce7; color:#166534; }
    .pill-orange { background:#ffedd5; color:#9a3412; }
    .pill-blue { background:#dbeafe; color:#1d4ed8; }
    .pill-red { background:#fee2e2; color:#991b1b; }
    .pill-purple { background:#ede9fe; color:#5b21b6; }
    .pill-teal { background:#ccfbf1; color:#115e59; }

    .small-muted {
      color: #64748b;
      font-size: 13px;
      line-height: 1.45;
      margin-top: 3px;
    }

    .modal-mask {
      position: fixed;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      background: rgba(15,23,42,.58);
      z-index: 6000;
      padding: 20px;
    }

    .modal-mask.active {
      display: flex;
    }

    .modal {
      width: min(1180px, 96vw);
      max-height: 90vh;
      overflow: auto;
      background: #fff;
      border-radius: 20px;
      padding: 18px;
      box-shadow: 0 26px 80px rgba(0,0,0,.28);
    }

    .modal-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      font-size: 24px;
      font-weight: 1000;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
    }

    .sales-building-picker-row {
      display: grid;
      grid-template-columns: 1fr 76px;
      gap: 8px;
      align-items: center;
    }

    .sales-building-picker-row button {
      width: 76px;
      padding: 0 8px;
      white-space: nowrap;
    }

    .full { grid-column: 1 / -1; }
    .half { grid-column: span 2; }

    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 14px;
    }

    @media (max-width: 1180px) {
      .stats { grid-template-columns: repeat(5, 1fr); }
      .filters { grid-template-columns: repeat(3, 1fr); }
      .form-grid { grid-template-columns: repeat(2, 1fr); }
      .half { grid-column: 1 / -1; }
      .schedule-list { grid-template-columns: repeat(2, 1fr); }
    }

    @media (max-width: 720px) {
      .wrap { padding: 14px; }
      .stats, .filters, .form-grid { grid-template-columns: 1fr; }
      .schedule-list { grid-template-columns: 1fr; }
      .topbar { align-items: flex-start; flex-direction: column; }
      .actions { justify-content: flex-start; }
      table { min-width: 1100px; }
      .panel { overflow-x: auto; }
    }
  
    

  
    

  
    

  
    

  
    /* SHINNAN_SALES_HEADER_BUTTON_RESTORE_LOGO_MOVE_V4 */
    .sales-unified-header {
      display: grid !important;
      grid-template-columns: minmax(0, 1fr) auto !important;
      align-items: center !important;
      gap: 18px !important;
      padding: 26px 32px !important;
      margin-bottom: 18px !important;
      border-radius: 22px !important;
      border: 1px solid rgba(255,255,255,.34) !important;
      background: linear-gradient(135deg, #3f6471 0%, #365ee8 68%, #7c3aed 100%) !important;
      box-shadow: 0 18px 42px rgba(15,23,42,.14) !important;
      color: #fff !important;
    }

    .sales-title-row {
      display: flex !important;
      align-items: center !important;
      gap: 16px !important;
      min-width: 0 !important;
    }

    .sales-title-logo {
      width: 124px !important;
      height: 94px !important;
      object-fit: contain !important;
      flex: 0 0 auto !important;
      margin: 0 !important;
      transform: translateY(-20px) !important;
      filter: drop-shadow(0 5px 9px rgba(0,0,0,.18)) !important;
      position: relative !important;
      z-index: 1 !important;
    }

    .sales-title-text {
      min-width: 0 !important;
      display: grid !important;
      gap: 8px !important;
      position: relative !important;
      z-index: 2 !important;
    }

    .sales-unified-header h1,
    .sales-unified-header .subtitle {
      text-align: left !important;
    }

    .sales-unified-header .actions {
      justify-content: flex-end !important;
      align-items: center !important;
      margin-left: auto !important;
      justify-self: end !important;
      width: auto !important;
    }
    /* SHINNAN_SALES_TEXT_LEFT_BUTTON_RIGHT_V6_END */

  
    

  
    /* SHINNAN_SALES_MOVE_LOGO_ONLY_V8 */
    .sales-title-row {
      display: flex !important;
      align-items: center !important;
      gap: 24px !important;
      column-gap: 24px !important;
      min-width: 0 !important;
    }

    .sales-title-logo {
      width: 124px !important;
      height: 94px !important;
      object-fit: contain !important;
      flex: 0 0 auto !important;
      margin: 0 !important;
      transform: translate(-42px, -20px) !important;
      filter: drop-shadow(0 5px 9px rgba(0,0,0,.18)) !important;
      position: relative !important;
      z-index: 1 !important;
    }

    .sales-title-text {
      transform: none !important;
    }

    .sales-unified-header .actions {
      justify-content: flex-end !important;
      align-items: center !important;
      margin-left: auto !important;
      justify-self: end !important;
    }
    /* SHINNAN_SALES_MOVE_LOGO_ONLY_V8_END */

  
    /* SHINNAN_SALES_TEXT_TO_LOGO_SH_V9 */
    .sales-title-text {
      transform: translateX(-52px) !important;
    }

    .sales-unified-header h1,
    .sales-unified-header .subtitle {
      text-align: left !important;
    }

    .sales-unified-header .actions {
      justify-content: flex-end !important;
      align-items: center !important;
      margin-left: auto !important;
      justify-self: end !important;
    }
    /* SHINNAN_SALES_TEXT_TO_LOGO_SH_V9_END */

  
    /* SHINNAN_SALES_HEADER_COMPACT_V10 */
    .sales-unified-header {
      min-height: 0 !important;
      padding: 14px 24px !important;
      margin-bottom: 14px !important;
      border-radius: 18px !important;
      grid-template-columns: minmax(0, 1fr) auto !important;
      align-items: center !important;
    }

    .sales-title-row {
      gap: 18px !important;
      column-gap: 18px !important;
      align-items: center !important;
    }

    .sales-title-logo {
      width: 101px !important;
      height: 75px !important;
      transform: translate(-18px, 4px) !important;
    }

    .sales-title-text {
      transform: translateX(-52px) !important;
      gap: 0 !important;
    }

    .sales-unified-header h1 {
      font-size: 30px !important;
      line-height: 1.05 !important;
      margin: 0 !important;
      white-space: nowrap !important;
    }

    .sales-unified-header .subtitle {
      display: none !important;
    }

    .sales-unified-header .actions {
      justify-content: flex-end !important;
      align-items: center !important;
      gap: 8px !important;
      margin-left: auto !important;
      justify-self: end !important;
    }

    .sales-unified-header button {
      height: 32px !important;
      min-height: 32px !important;
      border-radius: 10px !important;
      padding: 0 13px !important;
      font-size: 13px !important;
      font-weight: 900 !important;
      line-height: 1 !important;
    }
    /* SHINNAN_SALES_HEADER_COMPACT_V10_END */

  </style>
<style id="sales_stats_filter_bar_v1">
  /* 統計區改成一欄式快速篩選列 */

  .stats {
    display: flex !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    gap: 8px !important;
    margin: 0 0 10px 0 !important;
    padding: 10px 12px !important;
    border: 1px solid #d7e1ef !important;
    border-radius: 18px !important;
    background: #ffffff !important;
    box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06) !important;
  }

  .stats::before {
    content: "快速篩選";
    display: inline-flex;
    align-items: center;
    height: 30px;
    margin-right: 2px;
    padding: 0 10px;
    border-radius: 999px;
    background: #eaf2ff;
    color: #24415f;
    font-size: 13px;
    font-weight: 1000;
    white-space: nowrap;
  }

  .stat-card {
    min-height: 30px !important;
    height: 30px !important;
    padding: 0 10px !important;
    border-radius: 999px !important;
    border: 1px solid #dbe7f5 !important;
    background: #f8fafc !important;
    box-shadow: none !important;
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    cursor: pointer !important;
    user-select: none !important;
    transition: transform .12s ease, border-color .12s ease, background .12s ease;
    width: auto !important;
  }

  .stat-card:hover {
    transform: translateY(-1px);
    border-color: #365ee8 !important;
    background: #eef4ff !important;
  }

  .stat-card.active {
    border-color: #365ee8 !important;
    background: #365ee8 !important;
    color: #ffffff !important;
  }

  .stat-card.active .stat-label,
  .stat-card.active .stat-number {
    color: #ffffff !important;
  }

  .stat-label {
    color: #475569 !important;
    font-size: 13px !important;
    font-weight: 900 !important;
    line-height: 1 !important;
    white-space: nowrap !important;
  }

  .stat-number {
    margin: 0 !important;
    color: #102348 !important;
    font-size: 16px !important;
    font-weight: 1000 !important;
    line-height: 1 !important;
  }

  .stat-card::after {
    content: "筆";
    color: inherit;
    opacity: .85;
    font-size: 12px;
    font-weight: 900;
  }

  .sales-filter-reset {
    height: 30px;
    border: 1px solid #cbd5e1;
    border-radius: 999px;
    background: #ffffff;
    color: #334155;
    padding: 0 12px;
    font-size: 13px;
    font-weight: 1000;
    cursor: pointer;
  }

  .sales-filter-reset:hover {
    background: #f1f5f9;
  }

  .schedule-panel {
    margin-top: 0 !important;
  }

  @media (max-width: 760px) {
    .stats {
      align-items: stretch !important;
    }

    .stat-card,
    .sales-filter-reset {
      width: 100% !important;
      justify-content: space-between !important;
    }

    .stats::before {
      width: 100%;
      justify-content: center;
    }
  }
</style>
<style id="sales_today_memo_layout_v3">
  /* 今日行程 memo v3：業務欄往左，加入欄位名稱 */

  .schedule-panel {
    padding: 12px 14px !important;
    margin-bottom: 10px !important;
  }

  .schedule-list {
    display: block !important;
  }

  .sales-memo-header,
  .schedule-card {
    display: grid !important;
    grid-template-columns: 80px 210px 90px 260px minmax(520px, 1fr) !important;
    align-items: center !important;
    gap: 10px !important;
  }

  .sales-memo-header {
    margin-bottom: 6px;
    padding: 0 12px;
    color: #64748b;
    font-size: 12px;
    font-weight: 1000;
  }

  .schedule-card {
    min-height: 0 !important;
    padding: 8px 12px !important;
    margin-bottom: 7px !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    border: 1px solid #dbe7f5 !important;
    background: #ffffff !important;
  }

  .schedule-card.important {
    border-color: #f59e0b !important;
    background: #fffaf0 !important;
  }

  .sales-memo-tag {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 64px;
    height: 25px;
    border-radius: 999px;
    padding: 0 8px;
    background: #dbeafe;
    color: #1d4ed8;
    font-size: 13px;
    font-weight: 1000;
  }

  .sales-memo-tag.important {
    background: #fef3c7;
    color: #92400e;
  }

  .sales-memo-building {
    font-size: 17px;
    font-weight: 1000;
    color: #102348;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .sales-memo-owner {
    font-size: 16px;
    font-weight: 1000;
    color: #1e293b;
    white-space: nowrap;
  }

  .sales-memo-contact {
    font-size: 15px;
    font-weight: 900;
    color: #475569;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .sales-memo-action {
    font-size: 15px;
    font-weight: 1000;
    color: #334155;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .schedule-empty {
    padding: 10px 12px !important;
    font-size: 14px !important;
  }

  @media (max-width: 1280px) {
    .sales-memo-header,
    .schedule-card {
      grid-template-columns: 70px 180px 82px 220px minmax(340px, 1fr) !important;
      gap: 8px !important;
    }
  }

  @media (max-width: 900px) {
    .sales-memo-header {
      display: none !important;
    }

    .schedule-card {
      grid-template-columns: 72px 1fr !important;
      gap: 6px 10px !important;
    }

    .sales-memo-owner,
    .sales-memo-contact,
    .sales-memo-action {
      grid-column: 2 / -1;
      white-space: normal;
    }
  }
</style>


<style id="sales_clean_join_api_list_v1">
  /* 業務列表清理：以 JOIN API 回傳資料為準 */

  /* 備註欄已移到下一列，表頭與原本最後一欄隱藏 */
  table thead tr th:last-child {
    display: none !important;
  }

  #sales_rows tr:not(.sales-note-row) td:last-child {
    display: none !important;
  }

  #sales_rows tr.sales-note-row td {
    padding: 0 7px 8px 7px !important;
    border-bottom: 1px solid #e5edf7 !important;
    background: #ffffff !important;
  }

  .sales-note-box {
    margin: 0 !important;
    padding: 7px 10px !important;
    border-radius: 10px !important;
    background: #f8fafc !important;
    border: 1px solid #dbe7f5 !important;
    color: #334155 !important;
    font-size: 13px !important;
    line-height: 1.5 !important;
    white-space: normal !important;
  }

  .sales-note-label {
    display: inline-flex !important;
    align-items: center !important;
    height: 22px !important;
    margin-right: 8px !important;
    padding: 0 8px !important;
    border-radius: 999px !important;
    background: #eaf2ff !important;
    color: #24415f !important;
    font-size: 12px !important;
    font-weight: 1000 !important;
  }

  .sales-note-content {
    font-weight: 800 !important;
  }

  .sales-note-empty {
    color: #94a3b8 !important;
  }

  .sales-manager-link {
    border: 0;
    background: transparent;
    padding: 0;
    color: #1d4ed8;
    font-size: inherit;
    font-weight: 1000;
    cursor: pointer;
    text-align: left;
  }

  .sales-manager-link:hover {
    text-decoration: underline;
  }
</style>


<style id="sales_force_manager_simple_v1">
  /* 業務列表：總幹事欄強制只保留姓名與電話 */

  #sales_rows tr:not(.sales-note-row) td:nth-child(2) {
    min-width: 120px !important;
  }

  #sales_rows tr:not(.sales-note-row) td:nth-child(2) .small-muted:nth-of-type(n+2) {
    display: none !important;
  }

  #sales_rows tr:not(.sales-note-row) td:nth-child(2) .sales-manager-extra {
    display: none !important;
  }

  #sales_rows tr:not(.sales-note-row) td:nth-child(2) {
    line-height: 1.55 !important;
  }

  #sales_rows tr:not(.sales-note-row) td:nth-child(2) button,
  #sales_rows tr:not(.sales-note-row) td:nth-child(2) b {
    display: inline-block !important;
    margin-bottom: 6px !important;
  }
</style>

  <link rel="stylesheet" href="/static/web_title_unified.css?v=20260513_cl9b">
<link rel="stylesheet" href="/static/xn_buttons.css?v=cl_btn_v1">



</head>
<body>
  <div class="wrap">
<section class="web-title web-title-tech" id="xn-page-header">
  <img class="web-title-watermark" src="/static/shinnan_logo_outline_white.png" alt="">
  <div class="web-title-map"></div>
  <div class="web-title-radar"></div>
  <div class="web-title-main">
    <div class="web-title-logo-box">
      <img class="web-title-logo" src="/static/shinnan_logo_gold_transparent.png?v=cl_header_v1" alt="ShinNan Logo">
    </div>
    <div class="web-title-text">
      <h1 class="web-title-system">業務管理系統</h1>
      <div class="web-title-sub">
        <span class="web-title-sub-dot"></span>中央控管系統<span class="web-title-sub-dot"></span>
      </div>
    </div>
  </div>
</section>

    <div class="stats">
      <div class="stat-card"><div class="stat-label">新大樓開發中</div><div class="stat-number" id="stat_developing">0</div></div>
      <div class="stat-card"><div class="stat-label">待拜訪大樓</div><div class="stat-number" id="stat_visit">0</div></div>
      <div class="stat-card"><div class="stat-label">合約即將到期</div><div class="stat-number" id="stat_contract_due">0</div></div>
      <div class="stat-card"><div class="stat-label">待處理事件</div><div class="stat-number" id="stat_events">0</div></div>
      <div class="stat-card"><div class="stat-label">待執行回饋</div><div class="stat-number" id="stat_feedback">0</div></div>
      <div class="stat-card"><div class="stat-label">本月拜訪</div><div class="stat-number" id="stat_month_visit">0</div></div>
    </div>

    <div class="panel schedule-panel">
      <div class="schedule-head">
        <div>
          <div class="schedule-title">今日行程</div>
          <div class="schedule-sub">重要行程會固定排在最上方；有拜訪日期或事件日期的案件也會顯示。</div>
        </div>
        <button class="btn-green" type="button" onclick="openCreateSalesModal()">新增行程</button>
      </div>
      <div id="today_schedule_rows" class="schedule-list">
        <div class="schedule-empty">目前沒有今日行程。</div>
      </div>
    </div>

    <div class="panel">
      <div class="filters">
        <div>
          <label>區域</label>
          <select id="filter_area">
            <option value="全部">全部</option>
            <option>東區</option><option>北區</option><option>北台南</option><option>仁德</option>
            <option>永康</option><option>安平</option><option>高雄</option>
          </select>
        </div>
        <div>
          <label>業務類型</label>
          <select id="filter_business_type">
            <option value="全部">全部</option>
            <option>新社區</option>
            <option>公設線</option>
            <option>續約</option>
            <option>費率調整</option>
          </select>
        </div>
        <div>
          <label>目前狀態</label>
          <select id="filter_status">
            <option value="全部">全部</option>
            <option>追蹤中</option>
            <option>待回覆</option>
            <option>已完成</option>
          </select>
        </div>
        <div>
          <label>合約狀態</label>
          <select id="filter_contract_status">
            <option value="全部">全部</option>
            <option>未簽</option>
            <option>洽談中</option>
            <option>已簽</option>
            <option>即將到期</option>
            <option>已到期</option>
            <option>已續約</option>
            <option>終止</option>
          </select>
        </div>
        <div>
          <label>負責業務</label>
          <select id="filter_owner">
            <option value="全部">全部</option>
            <option>吳文化</option>
            <option>業務一</option>
            <option>業務二</option>
            <option>業務三</option>
          </select>
        </div>
        <div>
          <label>關鍵字</label>
          <input id="filter_keyword" placeholder="大樓、管理公司、窗口、事件">
        </div>
      </div>
    </div>

    <div class="panel">
      <table>
        <thead>
          <tr>
            <th>大樓／管理室</th>
            <th>總幹事</th>
            <th>會議時間</th>
            <th>區域</th>
            <th>業務類型</th>
            <th>目前狀態</th>
            <th>合約</th>
            <th>業務事件</th>
            <th>回饋項目</th>
            <th>下次拜訪</th>
            <th>負責業務</th>
            <th>備註</th>
          </tr>
        </thead>
        <tbody id="sales_rows">
          <tr><td colspan="12">目前沒有資料。</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div id="sales_modal" class="modal-mask">
    <div class="modal">
      <div class="modal-title">
        <span>新增案件</span>
        <button class="btn-gray" type="button" onclick="closeCreateSalesModal()">關閉</button>
      </div>

      <div class="form-grid">
        <div class="full">
          <label>行程設定</label>
          <label class="check-row">
            <input id="new_important_schedule" type="checkbox">
            重要行程，顯示在今日行程最上方
          </label>
        </div>
        <div>
          <label>大樓名稱</label>
          <div class="sales-building-picker-row">
            <input id="new_building_name" placeholder="尚未選擇大樓">
            <button id="sales_choose_building_button" class="btn-purple" type="button">大樓</button>
          </div>
        </div>
        <div>
          <label>區域</label>
          <select id="new_area">
            <option>東區</option><option>北區</option><option>北台南</option><option>仁德</option>
            <option>永康</option><option>安平</option><option>高雄</option>
          </select>
        </div>
        <div>
          <label>管理公司</label>
          <input id="new_management_company">
        </div>
        <div>
          <label>管理室電話</label>
          <input id="new_management_phone">
        </div>

        <div>
          <label>總幹事姓名</label>
          <input id="new_manager_name" placeholder="總幹事姓名">
        </div>
        <div>
          <label>總幹事電話</label>
          <input id="new_manager_phone" placeholder="總幹事電話">
        </div>
        <div>
          <label>總幹事年齡</label>
          <input id="new_manager_age" type="number" min="0" placeholder="年齡">
        </div>
        <div>
          <label>總幹事資歷</label>
          <input id="new_manager_experience" placeholder="例如 5 年">
        </div>
        <div>
          <label>總幹事興趣</label>
          <input id="new_manager_interest" placeholder="例如 茶、釣魚、運動">
        </div>
        <div>
          <label>可拜訪時段</label>
          <input id="new_visit_time" placeholder="例如 平日 10:00-17:00">
        </div>
        <div>
          <label>委員會時間</label>
          <input id="new_committee_time" placeholder="例如 每月第 2 週三 19:00">
        </div>
        <div>
          <label>住戶大會時間</label>
          <input id="new_resident_meeting_time" placeholder="例如 每年 6 月">
        </div>
        <div>
          <label>業務類型</label>
          <select id="new_business_type">
            <option>新大樓開發</option>
            <option>舊大樓拜訪</option>
            <option>合約續約</option>
            <option>管理室拜訪</option>
            <option>業務事件</option>
            <option>回饋處理</option>
          </select>
        </div>
        <div>
          <label>目前狀態</label>
          <select id="new_status">
            <option>未接觸</option>
            <option>已接觸</option>
            <option>已拜訪</option>
            <option>已提案</option>
            <option>等管委會</option>
            <option>談約中</option>
            <option>已簽約</option>
            <option>例行維護</option>
            <option>暫緩</option>
            <option>失敗</option>
          </select>
        </div>

        <div>
          <label>合約狀態</label>
          <select id="new_contract_status">
            <option>未簽</option>
            <option>洽談中</option>
            <option>已簽</option>
            <option>即將到期</option>
            <option>已到期</option>
            <option>已續約</option>
            <option>終止</option>
          </select>
        </div>
        <div>
          <label>合約到期日</label>
          <input id="new_contract_end_date" type="date">
        </div>
        <div>
          <label>回饋項目</label>
          <select id="new_feedback_type">
            <option>無</option>
            <option>現金回饋</option>
            <option>管理費補助</option>
            <option>活動贊助</option>
            <option>設備贈送</option>
            <option>網路優惠</option>
            <option>其他</option>
          </select>
        </div>
        <div>
          <label>回饋狀態</label>
          <select id="new_feedback_status">
            <option>無</option>
            <option>待確認</option>
            <option>已核准</option>
            <option>已執行</option>
            <option>已結清</option>
            <option>暫停</option>
          </select>
        </div>

        <div>
          <label>事件類型</label>
          <select id="new_event_type">
            <option>無</option>
            <option>管委會要求</option>
            <option>住戶反應</option>
            <option>競爭業者進場</option>
            <option>管理室要求</option>
            <option>社區公告協調</option>
            <option>續約爭議</option>
            <option>設備室協調</option>
            <option>其他</option>
          </select>
        </div>
        <div>
          <label>事件狀態</label>
          <select id="new_event_status">
            <option>無</option>
            <option>待處理</option>
            <option>處理中</option>
            <option>已回覆</option>
            <option>已完成</option>
            <option>暫緩</option>
          </select>
        </div>
        <div>
          <label>事件安排日期</label>
          <input id="new_event_schedule_date" type="date">
        </div>
        <div>
          <label>下次拜訪日期</label>
          <input id="new_next_visit" type="date">
        </div>
        <div>
          <label>負責業務</label>
          <select id="new_owner">
            <option>吳文化</option>
            <option>業務一</option>
            <option>業務二</option>
            <option>業務三</option>
          </select>
        </div>

        <div class="half">
          <label>管理室資訊／注意事項</label>
          <textarea id="new_management_note" placeholder="例如：可拜訪時段、窗口習慣、禁忌事項、是否需主管出面"></textarea>
        </div>
        <div class="half">
          <label>業務紀錄／拜訪結果</label>
          <textarea id="new_business_note" placeholder="例如：拜訪內容、管委會反應、下一步、需追蹤事項"></textarea>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn-gray" type="button" onclick="closeCreateSalesModal()">取消</button>
        <button class="btn-green" type="button" onclick="createSalesLead()">建立案件</button>
      </div>
    </div>
  </div>

  <script>
    const STORAGE_KEY = "shinnan_building_business_records_v1";
    var businessRecords = [];

    function byId(id) {
      return document.getElementById(id);
    }

    function escapeHtml(value) {
      return String(value || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    async function loadBusinessRecords() {
      try {
        const res = await fetch("/api/admin/sales/business-records?ts=" + Date.now(), { cache: "no-store" });

        if (!res.ok) {
          console.error("業務資料庫 API 讀取失敗", res.status);
          businessRecords = [];
          return;
        }

        const data = await res.json();

        if (!Array.isArray(data)) {
          console.error("業務資料庫 API 格式錯誤", data);
          businessRecords = [];
          return;
        }

        businessRecords = data;
        window.businessRecords = businessRecords;
        console.log("sales main flow loaded from database:", businessRecords.length);
      } catch (e) {
        console.error("loadBusinessRecords database failed", e);
        businessRecords = [];
      }
    }

    function saveBusinessRecords() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(businessRecords));
    }

    function openCreateSalesModal() {
      byId("sales_modal").classList.add("active");
    }

    function closeCreateSalesModal() {
      byId("sales_modal").classList.remove("active");
    }

    function goBuildingsFromSales() {
      localStorage.setItem("xunnan_building_back_return", "/admin/sales");
      window.location.href = "/admin/buildings?caller=sales";
    }

    function goChooseBuildingFromSalesForm() {
      localStorage.setItem("xunnan_building_pick_return", "/admin/sales?open_sales_modal=1&from_building_pick=1&caller=sales");
      window.location.href = "/admin/buildings?select=1&caller=sales";
    }

    function applyPickedBuildingToSalesForm() {
      const params = new URLSearchParams(window.location.search);
      const shouldOpen =
        params.get("open_sales_modal") === "1" ||
        params.get("from_building_pick") === "1" ||
        params.get("caller") === "sales";

      const raw =
        localStorage.getItem("xunnan_building_pick_result") ||
        localStorage.getItem("xunnan_selected_building");

      if (!raw) {
        if (shouldOpen) {
          setTimeout(function () {
            openCreateSalesModal();
          }, 120);
          window.history.replaceState({}, document.title, "/admin/sales");
        }
        return;
      }

      try {
        const building = JSON.parse(raw);

        if (byId("new_building_name")) {
          byId("new_building_name").value = building.name || "";
        }

        if (byId("new_area") && building.area) {
          byId("new_area").value = building.area;
        }

        if (byId("new_management_company") && building.management_company) {
          byId("new_management_company").value = building.management_company;
        }

        if (byId("new_management_note") && building.raw_address) {
          const oldNote = byId("new_management_note").value.trim();
          const addressLine = "大樓地址：" + building.raw_address;
          byId("new_management_note").value = oldNote ? (oldNote + "\\n" + addressLine) : addressLine;
        }

        localStorage.removeItem("xunnan_building_pick_result");
        localStorage.removeItem("xunnan_selected_building");
        localStorage.removeItem("xunnan_selected_building_no");
        localStorage.removeItem("xunnan_selected_building_name");
        localStorage.removeItem("xunnan_selected_building_area");
        localStorage.removeItem("xunnan_selected_building_raw_address");
        localStorage.removeItem("xunnan_selected_building_address");
        localStorage.removeItem("xunnan_building_pick_return");

        setTimeout(function () {
          openCreateSalesModal();
        }, 120);

        if (shouldOpen) {
          window.history.replaceState({}, document.title, "/admin/sales");
        }
      } catch (err) {
        console.warn("業務系統讀取選擇大樓失敗", err);
      }
    }

    function createSalesLead() {
      const buildingName = byId("new_building_name").value.trim();

      if (!buildingName) {
        alert("請輸入大樓名稱");
        return;
      }

      const item = {
        id: Date.now(),
        building_name: buildingName,
        area: byId("new_area").value,
        management_company: byId("new_management_company").value.trim(),
        management_phone: byId("new_management_phone").value.trim(),
        manager_name: byId("new_manager_name").value.trim(),
        manager_phone: byId("new_manager_phone").value.trim(),
        manager_age: byId("new_manager_age").value.trim(),
        manager_experience: byId("new_manager_experience").value.trim(),
        manager_interest: byId("new_manager_interest").value.trim(),
        visit_time: byId("new_visit_time").value.trim(),
        committee_time: byId("new_committee_time").value.trim(),
        resident_meeting_time: byId("new_resident_meeting_time").value.trim(),
        business_type: byId("new_business_type").value,
        status: byId("new_status").value,
        contract_status: byId("new_contract_status").value,
        contract_end_date: byId("new_contract_end_date").value,
        feedback_type: byId("new_feedback_type").value,
        feedback_status: byId("new_feedback_status").value,
        event_type: byId("new_event_type").value,
        event_status: byId("new_event_status").value,
        event_schedule_date: byId("new_event_schedule_date").value,
        important_schedule: byId("new_important_schedule").checked,
        next_visit: byId("new_next_visit").value,
        owner: byId("new_owner").value,
        management_note: byId("new_management_note").value.trim(),
        business_note: byId("new_business_note").value.trim(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      businessRecords.unshift(item);
      saveBusinessRecords();
      closeCreateSalesModal();
      clearCreateForm();
      renderBusinessRecords();
    }

    function clearCreateForm() {
      [
        "new_building_name",
        "new_management_company",
        "new_management_phone",
        "new_manager_name",
        "new_manager_phone",
        "new_manager_age",
        "new_manager_experience",
        "new_manager_interest",
        "new_visit_time",
        "new_committee_time",
        "new_resident_meeting_time",
        "new_contract_end_date",
        "new_event_schedule_date",
        "new_next_visit",
        "new_management_note",
        "new_business_note"
      ].forEach(function (id) {
        byId(id).value = "";
      });

      byId("new_business_type").value = "新大樓開發";
      byId("new_status").value = "未接觸";
      byId("new_contract_status").value = "未簽";
      byId("new_feedback_type").value = "無";
      byId("new_feedback_status").value = "無";
      byId("new_event_type").value = "無";
      byId("new_event_status").value = "無";
      byId("new_important_schedule").checked = false;
    }

    function statusClass(status) {
      if (status === "已簽約" || status === "已簽") return "pill pill-green";
      if (status === "談約中" || status === "已提案" || status === "等管委會") return "pill pill-orange";
      if (status === "失敗" || status === "終止") return "pill pill-red";
      if (status === "例行維護") return "pill pill-teal";
      return "pill pill-blue";
    }

    function contractClass(status) {
      if (status === "已簽" || status === "已續約") return "pill pill-green";
      if (status === "即將到期" || status === "已到期") return "pill pill-orange";
      if (status === "終止") return "pill pill-red";
      return "pill pill-purple";
    }

    function feedbackText(item) {
      if (!item.feedback_type || item.feedback_type === "無") return "-";
      return item.feedback_type + "｜" + (item.feedback_status || "未設定");
    }

    function eventText(item) {
      if (!item.event_type || item.event_type === "無") return "-";
      return item.event_type + "｜" + (item.event_status || "未設定");
    }

    function isContractDueSoon(item) {
      if (!item.contract_end_date) return false;
      if (!["已簽", "即將到期", "已到期"].includes(item.contract_status)) return false;

      const today = new Date();
      const end = new Date(item.contract_end_date + "T00:00:00");
      if (isNaN(end.getTime())) return false;

      const diffDays = Math.ceil((end - today) / 86400000);
      return diffDays <= 60;
    }

    function hasOpenSalesEvent(item) {
      const eventType = String((item && item.event_type) || "").trim();
      const eventStatus = String((item && item.event_status) || "").trim();
      return eventType && eventType !== "無" && !["", "無", "已完成", "完成"].includes(eventStatus);
    }

    function isThisMonth(dateText) {
      if (!dateText) return false;
      const now = new Date();
      const ym = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0");
      return String(dateText).startsWith(ym);
    }

    function filteredRecords() {
      const area = byId("filter_area").value;
      const businessType = byId("filter_business_type").value;
      const status = byId("filter_status").value;
      const contractStatus = byId("filter_contract_status").value;
      const owner = byId("filter_owner").value;
      const keyword = byId("filter_keyword").value.trim().toLowerCase();

      return businessRecords.filter(function (item) {
        if (area !== "全部" && item.area !== area) return false;
        if (businessType !== "全部" && item.business_type !== businessType) return false;
        if (status !== "全部" && item.status !== status) return false;
        if (contractStatus !== "全部" && item.contract_status !== contractStatus) return false;
        if (owner !== "全部" && item.owner !== owner) return false;

        if (keyword) {
          const hay = [
            item.building_name,
            item.management_company,
            item.management_phone,
            item.manager_name,
            item.manager_phone,
            item.manager_age,
            item.manager_experience,
            item.manager_interest,
            item.committee_time,
            item.resident_meeting_time,
            item.business_type,
            item.status,
            item.contract_status,
            item.feedback_type,
            item.feedback_status,
            item.event_type,
            item.event_status,
            item.event_schedule_date,
            item.important_schedule ? "重要行程" : "",
            item.management_note,
            item.business_note
          ].join(" ").toLowerCase();

          if (!hay.includes(keyword)) return false;
        }

        return true;
      });
    }

    function updateStats() {
      byId("stat_developing").textContent = businessRecords.filter(function (item) {
        return item.business_type === "新社區" && !["已完成"].includes(item.status);
      }).length;

      byId("stat_visit").textContent = businessRecords.filter(function (item) {
        return item.next_visit;
      }).length;

      byId("stat_contract_due").textContent = businessRecords.filter(isContractDueSoon).length;

      byId("stat_events").textContent = businessRecords.filter(function (item) {
        return hasOpenSalesEvent(item);
      }).length;

      byId("stat_feedback").textContent = businessRecords.filter(function (item) {
        return item.feedback_type !== "無" && ["待確認", "已核准"].includes(item.feedback_status);
      }).length;

      byId("stat_month_visit").textContent = businessRecords.filter(function (item) {
        return isThisMonth(item.next_visit);
      }).length;
    }

    function localDateText() {
      const now = new Date();
      return now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0") + "-" + String(now.getDate()).padStart(2, "0");
    }

    function hasActiveEvent(item) {
      return hasOpenSalesEvent(item);
    }

    function scheduleReason(item, today) {
      const reasons = [];

      if (item.important_schedule) {
        reasons.push("重要");
      }

      if (item.next_visit === today) {
        reasons.push("今日拜訪");
      } else if (item.next_visit) {
        reasons.push("拜訪：" + item.next_visit);
      }

      if (item.event_schedule_date === today) {
        reasons.push("今日事件");
      } else if (item.event_schedule_date) {
        reasons.push("事件：" + item.event_schedule_date);
      } else if (hasActiveEvent(item)) {
        reasons.push("待處理事件");
      }

      return reasons.join("｜") || "行程";
    }

    function renderTodaySchedule() {
      const box = byId("today_schedule_rows");
      if (!box) return;

      const today = localDateText();

      const items = businessRecords.filter(function (item) {
        return Boolean(item.important_schedule)
          || item.next_visit === today
          || item.event_schedule_date === today
          || hasActiveEvent(item);
      }).sort(function (a, b) {
        const ai = a.important_schedule ? 0 : 1;
        const bi = b.important_schedule ? 0 : 1;
        if (ai !== bi) return ai - bi;

        const ad = a.next_visit || a.event_schedule_date || "9999-12-31";
        const bd = b.next_visit || b.event_schedule_date || "9999-12-31";
        return String(ad).localeCompare(String(bd));
      });

      if (!items.length) {
        box.innerHTML = '<div class="schedule-empty">目前沒有今日行程。</div>';
        return;
      }

      box.innerHTML = items.map(function (item) {
        const cls = item.important_schedule ? "schedule-card important" : "schedule-card";
        return `
          <div class="${cls}">
            <div class="schedule-card-title">${escapeHtml(item.building_name)}</div>
            <div class="schedule-card-line">${escapeHtml(scheduleReason(item, today))}</div>
            <div class="schedule-card-line">區域：${escapeHtml(item.area || "-")}｜負責：${escapeHtml(item.owner || "-")}</div>
            <div class="schedule-card-line">總幹事：${escapeHtml(item.manager_name || "-")}｜${escapeHtml(item.manager_phone || "-")}</div>
            <div class="schedule-card-line">事件：${escapeHtml(eventText(item))}</div>
          </div>
        `;
      }).join("");
    }

    function renderBusinessRecords() {
      const rows = byId("sales_rows");
      const data = filteredRecords();

      updateStats();
      renderTodaySchedule();

      if (!data.length) {
        rows.innerHTML = "<tr><td colspan='12'>目前沒有符合條件的大樓業務紀錄。</td></tr>";
        return;
      }

      rows.innerHTML = data.map(function (item) {
        return `
          <tr>
            <td>
              <b>${escapeHtml(item.building_name)}</b>
              <div class="small-muted">${escapeHtml(item.management_company || "未填管理公司")}</div>
              <div class="small-muted">管理室：${escapeHtml(item.management_phone || "未填電話")}</div>
            </td>
            <td>
              <button class="sales-manager-link" type="button" onclick="openSalesManagerModalByName('${escapeHtml(item.manager_name || "")}')">${escapeHtml(item.manager_name || "未填")}</button>
              <div class="small-muted">${escapeHtml(item.manager_phone || "未填電話")}</div>
              <div class="small-muted">${escapeHtml(item.manager_age ? item.manager_age + " 歲" : "")}${item.manager_experience ? "｜資歷：" + escapeHtml(item.manager_experience) : ""}</div>
            </td>
            <td>
              <div>委員會：${escapeHtml(item.committee_time || "-")}</div>
              <div class="small-muted">住戶大會：${escapeHtml(item.resident_meeting_time || "-")}</div>
            </td>
            <td>${escapeHtml(item.area)}</td>
            <td><span class="pill pill-teal">${escapeHtml(item.business_type)}</span></td>
            <td><span class="${statusClass(item.status)}">${escapeHtml(item.status)}</span></td>
            <td>
              <span class="${contractClass(item.contract_status)}">${escapeHtml(item.contract_status)}</span>
              <div class="small-muted">${escapeHtml(item.contract_end_date || "-")}</div>
            </td>
            <td>${escapeHtml(eventText(item))}</td>
            <td>${escapeHtml(feedbackText(item))}</td>
            <td>${escapeHtml(item.next_visit || "-")}</td>
            <td>${escapeHtml(item.owner)}</td>
            <td>
              <div>${escapeHtml(item.business_note || "-")}</div>
              <div class="small-muted">${escapeHtml(item.management_note || "")}</div>
            </td>
          </tr>
        `;
      }).join("");
    }

    ["filter_area", "filter_business_type", "filter_status", "filter_contract_status", "filter_owner", "filter_keyword"].forEach(function (id) {
      byId(id).addEventListener("input", renderBusinessRecords);
      byId(id).addEventListener("change", renderBusinessRecords);
    });

    async function bootSalesPage() {
      await loadBusinessRecords();
      renderBusinessRecords();
      applyPickedBuildingToSalesForm();

      const debug = document.getElementById("sales_db_debug_count");
      if (debug) {
        debug.textContent = "資料庫已載入 " + businessRecords.length + " 筆業務資料";
      }
    }

    bootSalesPage();
  </script>

  <script id="sales_button_recovery_v1">
    (function () {
      function go(url) {
        window.location.href = url;
      }

      function safeBack() {
        if (document.referrer) {
          try {
            var ref = new URL(document.referrer);
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

      function openSalesCreateModalSafe() {
        var modal = document.getElementById("sales_modal");
        if (modal) {
          modal.classList.add("active");
          return;
        }

        if (typeof window.openCreateSalesModal === "function") {
          window.openCreateSalesModal();
          return;
        }

        alert("新增業務案件視窗尚未載入，請重新整理頁面。");
      }

      function bindSalesButtons() {
        var home = document.getElementById("sales_btn_home");
        var back = document.getElementById("sales_btn_back");
        var buildings = document.getElementById("sales_btn_buildings");
        var managers = document.getElementById("sales_btn_managers");
        var create = document.getElementById("sales_btn_create");

        if (home) {
          home.onclick = function () {
            go("/");
          };
        }

        if (back) {
          back.onclick = function () {
            safeBack();
          };
        }

        if (buildings) {
          buildings.onclick = function () {
            localStorage.setItem("xunnan_building_back_return", "/admin/sales");
            go("/admin/buildings?caller=sales");
          };
        }

        if (managers) {
          managers.onclick = function () {
            go("/admin/sales/managers");
          };
        }

        if (create) {
          create.onclick = function () {
            openSalesCreateModalSafe();
          };
        }
      }

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bindSalesButtons);
      } else {
        bindSalesButtons();
      }

      setTimeout(bindSalesButtons, 300);
    })();
  </script>


  <script id="sales_building_picker_recovery_v1">
    (function () {
      function openSalesBuildingPicker() {
        localStorage.setItem(
          "xunnan_building_pick_return",
          "/admin/sales?open_sales_modal=1&from_building_pick=1&caller=sales"
        );
        localStorage.setItem("xunnan_building_back_return", "/admin/sales");
        window.location.href = "/admin/buildings?select=1&caller=sales";
      }

      window.goChooseBuildingFromSalesForm = openSalesBuildingPicker;

      function bindSalesBuildingButton() {
        var btn = document.getElementById("sales_choose_building_button");
        if (!btn) return;

        btn.onclick = function (event) {
          event.preventDefault();
          openSalesBuildingPicker();
        };
      }

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bindSalesBuildingButton);
      } else {
        bindSalesBuildingButton();
      }

      setTimeout(bindSalesBuildingButton, 300);
      setTimeout(bindSalesBuildingButton, 800);
    })();
  </script>
<script id="sales_stats_filter_bar_v1">
(function () {
  if (!location.pathname.includes("/admin/sales")) return;

  let quickMode = "all";

  const modeMap = [
    { id: "stat_developing", mode: "developing" },
    { id: "stat_visit", mode: "visit" },
    { id: "stat_contract_due", mode: "contract_due" },
    { id: "stat_events", mode: "events" },
    { id: "stat_feedback", mode: "feedback" },
    { id: "stat_month_visit", mode: "month_visit" }
  ];

  function clearNormalFilters() {
    const ids = [
      "filter_area",
      "filter_business_type",
      "filter_status",
      "filter_contract_status",
      "filter_owner"
    ];

    ids.forEach(function (id) {
      const el = document.getElementById(id);
      if (el) el.value = "全部";
    });

    const keyword = document.getElementById("filter_keyword");
    if (keyword) keyword.value = "";
  }

  function updateActiveStatCards() {
    modeMap.forEach(function (item) {
      const number = document.getElementById(item.id);
      const card = number ? number.closest(".stat-card") : null;
      if (!card) return;

      if (quickMode === item.mode) {
        card.classList.add("active");
      } else {
        card.classList.remove("active");
      }
    });
  }

  function isContractDueSoonLocal(item) {
    if (!item || !item.contract_end_date) return false;
    if (!["已簽", "即將到期", "已到期"].includes(item.contract_status)) return false;

    const today = new Date();
    const end = new Date(item.contract_end_date + "T00:00:00");
    if (isNaN(end.getTime())) return false;

    const diffDays = Math.ceil((end - today) / 86400000);
    return diffDays <= 60;
  }

  function isThisMonthLocal(dateText) {
    if (!dateText) return false;

    const now = new Date();
    const ym = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0");

    return String(dateText).startsWith(ym);
  }

  function hasOpenSalesEventLocal(item) {
    const eventType = String((item && item.event_type) || "").trim();
    const eventStatus = String((item && item.event_status) || "").trim();
    return eventType && eventType !== "無" && !["", "無", "已完成", "完成"].includes(eventStatus);
  }

  function matchQuickMode(item) {
    if (quickMode === "all") return true;

    if (quickMode === "developing") {
      return item.business_type === "新社區" && !["已完成"].includes(item.status);
    }

    if (quickMode === "visit") {
      return Boolean(item.next_visit);
    }

    if (quickMode === "contract_due") {
      return isContractDueSoonLocal(item);
    }

    if (quickMode === "events") {
      return hasOpenSalesEventLocal(item);
    }

    if (quickMode === "feedback") {
      return item.feedback_type !== "無" && ["待確認", "已核准"].includes(item.feedback_status);
    }

    if (quickMode === "month_visit") {
      return isThisMonthLocal(item.next_visit);
    }

    return true;
  }

  function installQuickFilterWrapper() {
    if (window.__salesQuickFilterInstalled === true) return;
    if (typeof filteredRecords !== "function") return;

    window.__salesOriginalFilteredRecords = filteredRecords;

    filteredRecords = function () {
      const base = window.__salesOriginalFilteredRecords();
      return base.filter(matchQuickMode);
    };

    window.__salesQuickFilterInstalled = true;
  }

  function bindStatClicks() {
    installQuickFilterWrapper();

    modeMap.forEach(function (item) {
      const number = document.getElementById(item.id);
      const card = number ? number.closest(".stat-card") : null;
      if (!card) return;

      card.title = "點擊篩選：" + String(card.textContent || "").trim();

      card.onclick = function () {
        clearNormalFilters();
        quickMode = quickMode === item.mode ? "all" : item.mode;
        updateActiveStatCards();

        if (typeof renderBusinessRecords === "function") {
          renderBusinessRecords();
        }
      };
    });

    const stats = document.querySelector(".stats");
    if (stats && !document.getElementById("sales_filter_reset_btn")) {
      const btn = document.createElement("button");
      btn.id = "sales_filter_reset_btn";
      btn.className = "sales-filter-reset";
      btn.type = "button";
      btn.textContent = "全部";
      btn.onclick = function () {
        quickMode = "all";
        clearNormalFilters();
        updateActiveStatCards();

        if (typeof renderBusinessRecords === "function") {
          renderBusinessRecords();
        }
      };

      stats.appendChild(btn);
    }

    updateActiveStatCards();
  }

  function moveStatsAboveSchedule() {
    const wrap = document.querySelector(".wrap");
    const stats = document.querySelector(".stats");
    const schedule = document.querySelector(".schedule-panel");

    if (!wrap || !stats || !schedule) return;

    if (stats.compareDocumentPosition(schedule) & Node.DOCUMENT_POSITION_PRECEDING) {
      wrap.insertBefore(stats, schedule);
    }
  }

  function bootStatsFilterBar() {
    moveStatsAboveSchedule();
    bindStatClicks();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootStatsFilterBar);
  } else {
    bootStatsFilterBar();
  }

  setTimeout(bootStatsFilterBar, 300);
  setTimeout(bootStatsFilterBar, 900);
})();
</script>
<div id="sales_manager_modal_sub" class="sales-manager-modal-sub"></div>
      </div>
      <button class="sales-manager-modal-close" type="button" onclick="closeSalesManagerModal()">關閉</button>
    </div>
    <div id="sales_manager_modal_body" class="sales-manager-grid"></div>
  </div>
</div>
<script id="sales_today_memo_layout_v3">
(function () {
  if (!location.pathname.includes("/admin/sales")) return;

  function safeEscape(value) {
    if (typeof escapeHtml === "function") {
      return escapeHtml(value);
    }

    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function todayText() {
    const d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }

  function eventActive(item) {
    return hasOpenSalesEventLocal(item);
  }

  function buildActionText(item) {
    const parts = [];

    if (item.event_type && item.event_type !== "無") {
      parts.push(item.event_type);
    }

    if (item.event_status && item.event_status !== "無") {
      parts.push(item.event_status);
    }

    if (item.business_type) {
      parts.push(item.business_type);
    }

    if (item.contract_status === "洽談中" || item.contract_status === "即將到期") {
      parts.push("合約追蹤");
    }

    if (item.feedback_type && item.feedback_type !== "無") {
      parts.push(item.feedback_type);
    }

    if (!parts.length && item.next_visit) {
      parts.push("拜訪管理室");
    }

    return parts.join("｜") || "-";
  }

  function renderTodayScheduleMemoV3() {
    const box = document.getElementById("today_schedule_rows");
    if (!box) return;

    const rows = Array.isArray(window.businessRecords || businessRecords)
      ? (window.businessRecords || businessRecords)
      : [];

    const today = todayText();

    const items = rows.filter(function (item) {
      return Boolean(item.important_schedule)
        || item.next_visit === today
        || item.event_schedule_date === today
        || eventActive(item);
    }).sort(function (a, b) {
      const ai = a.important_schedule ? 0 : 1;
      const bi = b.important_schedule ? 0 : 1;
      if (ai !== bi) return ai - bi;

      const ad = a.next_visit || a.event_schedule_date || "9999-12-31";
      const bd = b.next_visit || b.event_schedule_date || "9999-12-31";
      return String(ad).localeCompare(String(bd));
    });

    if (!items.length) {
      box.innerHTML = '<div class="schedule-empty">目前沒有今日行程。</div>';
      return;
    }

    const header = `
      <div class="sales-memo-header">
        <div>類型</div>
        <div>大樓</div>
        <div>負責業務</div>
        <div>總幹事／電話</div>
        <div>業務行為</div>
      </div>
    `;

    const body = items.map(function (item) {
      const important = Boolean(item.important_schedule);
      const tag = important ? "重要" : "今日";
      const cls = important ? "schedule-card important" : "schedule-card";
      const contact = (item.manager_name || "-") + "｜" + (item.manager_phone || "-");

      return `
        <div class="${cls}">
          <div><span class="sales-memo-tag ${important ? "important" : ""}">${tag}</span></div>
          <div class="sales-memo-building">${safeEscape(item.building_name || "-")}</div>
          <div class="sales-memo-owner">${safeEscape(item.owner || "-")}</div>
          <div class="sales-memo-contact">${safeEscape(contact)}</div>
          <div class="sales-memo-action">${safeEscape(buildActionText(item))}</div>
        </div>
      `;
    }).join("");

    box.innerHTML = header + body;
  }

  const oldRenderBusinessRecords = window.renderBusinessRecords || (typeof renderBusinessRecords === "function" ? renderBusinessRecords : null);

  if (oldRenderBusinessRecords && window.__salesTodayMemoV3Wrapped !== true) {
    window.__salesTodayMemoV3Wrapped = true;

    renderBusinessRecords = function () {
      oldRenderBusinessRecords();
      setTimeout(renderTodayScheduleMemoV3, 0);
    };
  }

  window.renderTodaySchedule = renderTodayScheduleMemoV3;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderTodayScheduleMemoV3);
  } else {
    renderTodayScheduleMemoV3();
  }

  setTimeout(renderTodayScheduleMemoV3, 300);
  setTimeout(renderTodayScheduleMemoV3, 900);
})();
</script>


<script id="sales_clean_join_api_list_v1">
(function () {
  if (!location.pathname.includes("/admin/sales")) return;

  function safeText(value) {
    return String(value || "").trim();
  }

  function normalizeNoteText(value) {
    let raw = safeText(value);

    raw = raw
      .replace(/\\s+/g, " ")
      .replace(/業務工作：/g, "工作：")
      .replace(/負責業務：/g, "負責：")
      .replace(/內容：/g, "內容：")
      .trim();

    return raw || "無備註";
  }

  function findRecordByManagerName(name) {
    name = safeText(name);
    const rows = Array.isArray(window.businessRecords || businessRecords)
      ? (window.businessRecords || businessRecords)
      : [];

    return rows.find(function (item) {
      return safeText(item.manager_name) === name;
    }) || null;
  }

  function openManagerMiniInfo(name) {
    const item = findRecordByManagerName(name);

    if (!item) {
      alert("找不到總幹事資料：" + name);
      return;
    }

    alert(
      "總幹事：" + (item.manager_name || "-") + "\n" +
      "電話：" + (item.manager_phone || "-") + "\n" +
      "管理公司：" + (item.management_company || "-") + "\n" +
      "服務大樓：" + (item.building_name || "-") + "\n" +
      "可拜訪時段：" + (item.visit_time || "-") + "\n" +
      "委員會時間：" + (item.committee_time || "-") + "\n" +
      "住戶大會：" + (item.resident_meeting_time || "-")
    );
  }

  window.openManagerMiniInfo = openManagerMiniInfo;

  function cleanManagerCells() {
    const tbody = document.getElementById("sales_rows");
    if (!tbody) return;

    Array.from(tbody.querySelectorAll("tr")).forEach(function (row) {
      if (row.classList.contains("sales-note-row")) return;

      const cells = row.querySelectorAll("td");
      if (cells.length < 2) return;

      const managerCell = cells[1];

      // 取得姓名
      let name = "";
      const link = managerCell.querySelector(".sales-manager-link");
      const btn = managerCell.querySelector("button");
      const bold = managerCell.querySelector("b");

      if (link) name = link.textContent.trim();
      else if (btn) name = btn.textContent.trim();
      else if (bold) name = bold.textContent.trim();
      else {
        const firstLine = managerCell.textContent.split(/\n/)[0] || "";
        name = firstLine.trim();
      }

      // 取得電話：找第一個像電話的文字
      let phone = "";
      const text = managerCell.textContent || "";
      const phoneMatch = text.match(/09\\d{8}|0\\d{1,2}-\\d{6,8}|未填電話/);
      if (phoneMatch) phone = phoneMatch[0];

      managerCell.innerHTML = `
        <button class="sales-manager-link" type="button" onclick="openManagerMiniInfo('${name.replaceAll("'", "\\'")}')">${name || "未填"}</button>
        <div class="small-muted">${phone || "未填電話"}</div>
      `;
    });
  }

  function rebuildNoteRowsFromBusinessNote() {
    const tbody = document.getElementById("sales_rows");
    if (!tbody) return;

    // 先移除舊備註列
    Array.from(tbody.querySelectorAll("tr.sales-note-row")).forEach(function (row) {
      row.remove();
    });

    const records = Array.isArray(window.businessRecords || businessRecords)
      ? (window.businessRecords || businessRecords)
      : [];

    const dataRows = Array.from(tbody.querySelectorAll("tr")).filter(function (row) {
      return !row.classList.contains("sales-note-row");
    });

    dataRows.forEach(function (row, index) {
      const cells = Array.from(row.children);
      if (!cells.length) return;

      // 空資料列不處理
      if (cells.length === 1 && cells[0].colSpan > 1) return;

      const item = records[index] || {};
      const note = normalizeNoteText(item.business_note || "");

      const visibleCount = cells.filter(function (cell) {
        return window.getComputedStyle(cell).display !== "none";
      }).length;

      const noteRow = document.createElement("tr");
      noteRow.className = "sales-note-row";

      const noteCell = document.createElement("td");
      noteCell.colSpan = Math.max(1, visibleCount);
      noteCell.innerHTML = `
        <div class="sales-note-box">
          <span class="sales-note-label">業務備註</span>
          <span class="sales-note-content">${note}</span>
        </div>
      `;

      noteRow.appendChild(noteCell);
      row.insertAdjacentElement("afterend", noteRow);
    });
  }

  function applyCleanJoinApiList() {
    cleanManagerCells();
    rebuildNoteRowsFromBusinessNote();
  }

  const oldRender = window.renderBusinessRecords || (typeof renderBusinessRecords === "function" ? renderBusinessRecords : null);

  if (oldRender && window.__salesCleanJoinApiListWrapped !== true) {
    window.__salesCleanJoinApiListWrapped = true;

    renderBusinessRecords = function () {
      oldRender();
      setTimeout(applyCleanJoinApiList, 0);
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyCleanJoinApiList);
  } else {
    applyCleanJoinApiList();
  }

  setTimeout(applyCleanJoinApiList, 300);
  setTimeout(applyCleanJoinApiList, 900);
})();
</script>


<script id="sales_force_manager_simple_v1">
(function () {
  if (!location.pathname.includes("/admin/sales")) return;

  function extractPhone(text) {
    const match = String(text || "").match(/09\\d{8}|0\\d{1,2}-\\d{6,8}|未填電話/);
    return match ? match[0] : "未填電話";
  }

  function extractName(cell) {
    const link = cell.querySelector(".sales-manager-link");
    if (link) return link.textContent.trim();

    const btn = cell.querySelector("button");
    if (btn) return btn.textContent.trim();

    const bold = cell.querySelector("b");
    if (bold) return bold.textContent.trim();

    const raw = String(cell.textContent || "")
      .split(/\n/)
      .map(x => x.trim())
      .filter(Boolean);

    return raw[0] || "未填";
  }

  function forceManagerSimple() {
    const tbody = document.getElementById("sales_rows");
    if (!tbody) return;

    Array.from(tbody.querySelectorAll("tr")).forEach(function (row) {
      if (row.classList.contains("sales-note-row")) return;

      const cells = row.querySelectorAll("td");
      if (cells.length < 2) return;

      const cell = cells[1];

      if (cell.dataset.managerSimpleDone === "1") return;

      const name = extractName(cell);
      const phone = extractPhone(cell.textContent);

      const safeName = name.replaceAll("'", "\\'");

      cell.innerHTML = `
        <button class="sales-manager-link" type="button" onclick="openManagerMiniInfo('${safeName}')">${name}</button>
        <div class="small-muted">${phone}</div>
      `;

      cell.dataset.managerSimpleDone = "1";
    });
  }

  function resetAndApply() {
    const tbody = document.getElementById("sales_rows");
    if (tbody) {
      Array.from(tbody.querySelectorAll("td[data-manager-simple-done]")).forEach(function (td) {
        delete td.dataset.managerSimpleDone;
      });
    }

    forceManagerSimple();
  }

  const oldRender = window.renderBusinessRecords || (typeof renderBusinessRecords === "function" ? renderBusinessRecords : null);

  if (oldRender && window.__salesForceManagerSimpleWrapped !== true) {
    window.__salesForceManagerSimpleWrapped = true;

    renderBusinessRecords = function () {
      oldRender();
      setTimeout(resetAndApply, 0);
      setTimeout(resetAndApply, 100);
    };
  }

  const observerTarget = document.getElementById("sales_rows");

  if (observerTarget && window.__salesForceManagerSimpleObserver !== true) {
    window.__salesForceManagerSimpleObserver = true;

    const observer = new MutationObserver(function () {
      setTimeout(forceManagerSimple, 0);
    });

    observer.observe(observerTarget, {
      childList: true,
      subtree: true
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", resetAndApply);
  } else {
    resetAndApply();
  }

  setTimeout(resetAndApply, 300);
  setTimeout(resetAndApply, 900);
})();
</script>



<script id="sales_owner_from_employee_profiles_v1">
(function () {
  if (!location.pathname.includes("/admin/sales")) return;

  async function loadSalesOwnersFromEmployeeProfiles() {
    try {
      const res = await fetch("/api/admin/employees?department=" + encodeURIComponent("業務部") + "&ts=" + Date.now(), {
        cache: "no-store"
      });

      if (!res.ok) {
        console.warn("業務人員 API 讀取失敗", res.status);
        return;
      }

      const rows = await res.json();
      const names = rows
        .filter(function (item) {
          return item && item.display_name && item.employment_status !== "離職" && Number(item.app_access || 0) === 1;
        })
        .map(function (item) {
          return item.display_name;
        });

      if (!names.length) {
        console.warn("沒有可用的業務人員資料");
        return;
      }

      const filterOwner = document.getElementById("filter_owner");
      const newOwner = document.getElementById("new_owner");

      if (filterOwner) {
        const oldValue = filterOwner.value || "全部";
        filterOwner.innerHTML =
          '<option value="全部">全部</option>' +
          names.map(function (name) {
            return '<option value="' + escapeAttr(name) + '">' + escapeHtml(name) + '</option>';
          }).join("");

        filterOwner.value = names.includes(oldValue) || oldValue === "全部" ? oldValue : "全部";

        if (typeof renderBusinessRecords === "function") {
          renderBusinessRecords();
        }
      }

      if (newOwner) {
        const oldValue = newOwner.value || "";
        newOwner.innerHTML = names.map(function (name) {
          return '<option value="' + escapeAttr(name) + '">' + escapeHtml(name) + '</option>';
        }).join("");

        newOwner.value = names.includes(oldValue) ? oldValue : names[0];
      }

      window.xunnanSalesOwners = names;
      console.log("業務 owner 已從 employee_profiles 載入", names);
    } catch (err) {
      console.error("業務 owner 載入失敗", err);
    }
  }

  function escapeHtml(v) {
    return String(v ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function escapeAttr(v) {
    return escapeHtml(v);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadSalesOwnersFromEmployeeProfiles);
  } else {
    loadSalesOwnersFromEmployeeProfiles();
  }

  setTimeout(loadSalesOwnersFromEmployeeProfiles, 500);
})();
</script>


<script id="cl15i4_sales_admin_final_recovery_v1">
(function () {
  if (!location.pathname.includes("/admin/sales")) return;

  function esc(value) {
    return String(value == null ? "" : value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function getRecords() {
    if (Array.isArray(window.businessRecords)) return window.businessRecords;
    try {
      if (Array.isArray(businessRecords)) return businessRecords;
    } catch (err) {}
    return [];
  }

  function currentFilter(id) {
    const el = document.getElementById(id);
    return el ? String(el.value || "全部") : "全部";
  }

  function keywordValue() {
    const el = document.getElementById("filter_keyword");
    return el ? String(el.value || "").trim().toLowerCase() : "";
  }

  function matchRecord(item) {
    const area = currentFilter("filter_area");
    const businessType = currentFilter("filter_business_type");
    const status = currentFilter("filter_status");
    const contractStatus = currentFilter("filter_contract_status");
    const owner = currentFilter("filter_owner");
    const keyword = keywordValue();

    if (area !== "全部" && String(item.area || "") !== area) return false;
    if (businessType !== "全部" && String(item.business_type || "") !== businessType) return false;
    if (status !== "全部" && String(item.status || "") !== status) return false;
    if (contractStatus !== "全部" && String(item.contract_status || "") !== contractStatus) return false;
    if (owner !== "全部" && String(item.owner || "") !== owner) return false;

    if (keyword) {
      const hay = [
        item.building_name,
        item.area,
        item.management_company,
        item.management_phone,
        item.manager_name,
        item.manager_phone,
        item.business_type,
        item.status,
        item.contract_status,
        item.feedback_type,
        item.feedback_status,
        item.event_type,
        item.event_status,
        item.next_visit,
        item.owner,
        item.business_note,
        item.management_note
      ].join(" ").toLowerCase();

      if (!hay.includes(keyword)) return false;
    }

    return true;
  }

  function statusClass(status) {
    if (status === "已完成") return "pill pill-green";
    if (status === "待回覆") return "pill pill-orange";
    if (status === "追蹤中") return "pill pill-blue";
    return "pill pill-blue";
  }

  function contractClass(status) {
    if (status === "已簽" || status === "已續約") return "pill pill-green";
    if (status === "即將到期" || status === "已到期") return "pill pill-orange";
    if (status === "終止") return "pill pill-red";
    return "pill pill-purple";
  }

  function eventText(item) {
    if (!item.event_type || item.event_type === "無") return "-";
    return item.event_type + "｜" + (item.event_status || "未設定");
  }

  function feedbackText(item) {
    if (!item.feedback_type || item.feedback_type === "無") return "-";
    return item.feedback_type + "｜" + (item.feedback_status || "未設定");
  }

  function finalRenderSalesRows() {
    const rows = document.getElementById("sales_rows");
    if (!rows) return;

    const records = getRecords();
    if (!records.length) {
      rows.innerHTML = "<tr><td colspan='12'>目前沒有載入業務資料。</td></tr>";
      return;
    }

    const data = records.filter(matchRecord);

    if (!data.length) {
      rows.innerHTML = "<tr><td colspan='12'>目前沒有符合條件的大樓業務紀錄。</td></tr>";
      return;
    }

    rows.innerHTML = data.map(function (item) {
      return `
        <tr>
          <td>
            <b>${esc(item.building_name || item.building_no || "-")}</b>
            <div class="small-muted">${esc(item.management_company || "未填管理公司")}</div>
            <div class="small-muted">管理室：${esc(item.management_phone || "未填電話")}</div>
          </td>
          <td>
            <button class="sales-manager-link" type="button">${esc(item.manager_name || "未填")}</button>
            <div class="small-muted">${esc(item.manager_phone || "未填電話")}</div>
          </td>
          <td>
            <div>委員會：${esc(item.committee_time || "-")}</div>
            <div class="small-muted">住戶大會：${esc(item.resident_meeting_time || "-")}</div>
          </td>
          <td>${esc(item.area || "-")}</td>
          <td><span class="pill pill-teal">${esc(item.business_type || "-")}</span></td>
          <td><span class="${statusClass(item.status)}">${esc(item.status || "-")}</span></td>
          <td>
            <span class="${contractClass(item.contract_status)}">${esc(item.contract_status || "-")}</span>
            <div class="small-muted">${esc(item.contract_end_date || "-")}</div>
          </td>
          <td>${esc(eventText(item))}</td>
          <td>${esc(feedbackText(item))}</td>
          <td>${esc(item.next_visit || "-")}</td>
          <td>${esc(item.owner || "-")}</td>
          <td>
            <div>${esc(item.business_note || "-")}</div>
            <div class="small-muted">${esc(item.management_note || "")}</div>
          </td>
        </tr>
      `;
    }).join("");
  }

  window.cl15i4FinalRenderSalesRows = finalRenderSalesRows;

  function bindFinalFilters() {
    ["filter_area", "filter_business_type", "filter_status", "filter_contract_status", "filter_owner", "filter_keyword"].forEach(function (id) {
      const el = document.getElementById(id);
      if (!el || el.dataset.cl15i4Bound === "1") return;
      el.dataset.cl15i4Bound = "1";
      el.addEventListener("input", function () { setTimeout(finalRenderSalesRows, 0); });
      el.addEventListener("change", function () { setTimeout(finalRenderSalesRows, 0); });
    });
  }

  async function reloadSalesRowsFromAdminApi() {
    try {
      const res = await fetch("/api/admin/sales/business-records?ts=" + Date.now(), {cache: "no-store"});
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      if (Array.isArray(data)) {
        window.businessRecords = data;
        try { businessRecords = data; } catch (err) {}
      }
    } catch (err) {
      console.error("CL15I4 sales admin reload failed", err);
    }

    bindFinalFilters();
    finalRenderSalesRows();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", reloadSalesRowsFromAdminApi);
  } else {
    reloadSalesRowsFromAdminApi();
  }

  setTimeout(reloadSalesRowsFromAdminApi, 500);
})();
</script>


</body>
</html>
"""
# SHINNAN_SALES_PAGE_ROUTE_END
