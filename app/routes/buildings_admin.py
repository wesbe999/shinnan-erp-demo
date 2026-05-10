import json as _buildings_json

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse, Response as _BuildingsResponse
from sqlalchemy import text as _buildings_sql_text

from app.db import engine as _buildings_engine


router = APIRouter(tags=["buildings-admin"])


# SHINNAN_BUILDINGS_DB_API_HELPER_START
def _ensure_buildings_columns(conn):
    existing = {row[1] for row in conn.execute(_buildings_sql_text("PRAGMA table_info(buildings)")).fetchall()}
    required = {
        "raw_address": "TEXT DEFAULT ''",
        "display_address": "TEXT DEFAULT ''",
        "management_company": "TEXT DEFAULT ''",
        "management_phone": "TEXT DEFAULT ''",
        "manager_name": "TEXT DEFAULT ''",
        "manager_phone": "TEXT DEFAULT ''",
        "manager_age": "TEXT DEFAULT ''",
        "manager_experience": "TEXT DEFAULT ''",
        "manager_interest": "TEXT DEFAULT ''",
        "visit_time": "TEXT DEFAULT ''",
        "committee_time": "TEXT DEFAULT ''",
        "resident_meeting_time": "TEXT DEFAULT ''",
        "active_users": "INTEGER DEFAULT 0",
        "total_households": "INTEGER DEFAULT 0",
        "ip": "TEXT DEFAULT ''",
        "host": "TEXT DEFAULT ''",
        "note": "TEXT DEFAULT ''",
        "created_at": "TEXT DEFAULT ''",
        "updated_at": "TEXT DEFAULT ''",
    }

    for column, definition in required.items():
        if column not in existing:
            conn.execute(_buildings_sql_text(f"ALTER TABLE buildings ADD COLUMN {column} {definition}"))


def _buildings_db_init():
    with _buildings_engine.begin() as conn:
        conn.execute(_buildings_sql_text("""
            CREATE TABLE IF NOT EXISTS buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_no TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                area TEXT DEFAULT '',
                address TEXT DEFAULT '',
                raw_address TEXT DEFAULT '',
                display_address TEXT DEFAULT '',
                management_company TEXT DEFAULT '',
                management_phone TEXT DEFAULT '',
                manager_name TEXT DEFAULT '',
                manager_phone TEXT DEFAULT '',
                manager_age TEXT DEFAULT '',
                manager_experience TEXT DEFAULT '',
                manager_interest TEXT DEFAULT '',
                visit_time TEXT DEFAULT '',
                committee_time TEXT DEFAULT '',
                resident_meeting_time TEXT DEFAULT '',
                active_users INTEGER DEFAULT 0,
                total_households INTEGER DEFAULT 0,
                ip TEXT DEFAULT '',
                host TEXT DEFAULT '',
                note TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))
        _ensure_buildings_columns(conn)


def _fetch_buildings_from_db():
    _buildings_db_init()

    with _buildings_engine.begin() as conn:
        rows = conn.execute(_buildings_sql_text("""
            SELECT
                building_no,
                name,
                area,
                address,
                raw_address,
                display_address,
                management_company,
                management_phone,
                manager_name,
                manager_phone,
                manager_age,
                manager_experience,
                manager_interest,
                visit_time,
                committee_time,
                resident_meeting_time,
                active_users,
                total_households,
                ip,
                host,
                note
            FROM buildings
            ORDER BY building_no ASC
        """)).mappings().fetchall()

    return [dict(row) for row in rows]
# SHINNAN_BUILDINGS_DB_API_HELPER_END


@router.get("/api/admin/buildings")
def api_admin_buildings():
    buildings = _fetch_buildings_from_db()

    return _BuildingsResponse(
        content=_buildings_json.dumps(buildings, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.get("/api/admin/buildings/status")
def api_admin_building_status():
    offline_building_nos = {"B001", "B014"}
    warning_building_nos = {"B027"}
    items = []

    for building in _fetch_buildings_from_db():
        building_no = building.get("building_no")
        online = building_no not in offline_building_nos
        disconnect_count = 2 if building_no in warning_building_nos else (1 if not online else 0)

        items.append({
            "building_no": building_no,
            "name": building.get("name"),
            "area": building.get("area"),
            "ip": building.get("ip"),
            "online": online,
            "disconnect_count": disconnect_count,
            "status": "離線" if not online else ("異常" if disconnect_count >= 2 else "正常"),
        })

    return JSONResponse(items)


@router.get("/admin/buildings", response_class=HTMLResponse)
def admin_buildings_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>訊南ERP｜大樓名錄</title>
  <style>
    :root {
      --bg: #eef3f9;
      --card: #ffffff;
      --line: #d7e1ef;
      --text: #102348;
      --muted: #64748b;
      --blue: #365ee8;
      --purple: #7c3aed;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Microsoft JhengHei", "Segoe UI", Arial, sans-serif;
    }

    .topbar {
      background: linear-gradient(120deg, #0f766e, #2563eb, #7c3aed);
      color: white;
      padding: 28px 34px;
    }

    .topbar h1 {
      margin: 0;
      font-size: 42px;
      font-weight: 1000;
      letter-spacing: 2px;
    }

    .topbar p {
      margin: 14px 0 0;
      font-size: 20px;
      font-weight: 900;
      opacity: .95;
    }

    .page {
      width: min(1680px, calc(100% - 36px));
      margin: 24px auto 42px;
    }

    .toolbar {
      display: grid;
      grid-template-columns: 150px 150px 220px minmax(420px, 1fr);
      gap: 14px;
      align-items: center;
      margin-bottom: 22px;
    }

    button, select, input {
      font-family: inherit;
      font-size: 18px;
    }

    button {
      border: 0;
      border-radius: 14px;
      padding: 13px 18px;
      color: white;
      font-weight: 1000;
      cursor: pointer;
      background: var(--blue);
    }

    input, select {
      width: 100%;
      height: 52px;
      border: 1px solid #cbd5e1;
      border-radius: 14px;
      padding: 0 16px;
      background: white;
      color: var(--text);
      outline: none;
    }

    .card {
      background: white;
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 24px;
      box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    }

    .hint {
      color: var(--muted);
      font-size: 14px;
      font-weight: 900;
      margin-bottom: 14px;
    }

    table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0 12px;
    }

    th {
      text-align: left;
      padding: 12px 14px;
      color: #475569;
      font-size: 16px;
      font-weight: 1000;
      white-space: nowrap;
    }

    td {
      background: white;
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      padding: 14px;
      font-size: 17px;
      font-weight: 900;
      vertical-align: middle;
    }

    td:first-child {
      border-left: 1px solid var(--line);
      border-radius: 14px 0 0 14px;
    }

    td:last-child {
      border-right: 1px solid var(--line);
      border-radius: 0 14px 14px 0;
    }

    td[contenteditable="true"] {
      background: #fffdf4;
      cursor: text;
      outline: none;
    }

    td[contenteditable="true"]:focus {
      background: #fff7d6;
      box-shadow: inset 0 0 0 2px #f59e0b;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      padding: 7px 14px;
      background: #ede9fe;
      color: #5b21b6;
      font-weight: 1000;
    }

    .btn-small {
      min-width: 100px;
      height: 42px;
      padding: 8px 14px;
      border-radius: 12px;
      font-size: 16px;
    }

    @media (max-width: 900px) {
      .toolbar { grid-template-columns: 1fr; }
      table { min-width: 1100px; }
      .card { overflow-x: auto; }
    }
      /* SHINNAN_BUILDING_AREA_PILL_HORIZONTAL_START */
    .pill {
      display: inline-flex !important;
      flex-direction: row !important;
      align-items: center !important;
      justify-content: center !important;
      min-width: 101px !important;
      height: 42px !important;
      padding: 0 18px !important;
      border-radius: 999px !important;
      background: #ede9fe !important;
      color: #5b21b6 !important;
      font-weight: 1000 !important;
      font-size: 20px !important;
      line-height: 1 !important;
      white-space: nowrap !important;
      word-break: keep-all !important;
      writing-mode: horizontal-tb !important;
    }

    td[data-field="area"] {
      min-width: 110px !important;
      width: 110px !important;
      text-align: center !important;
      white-space: nowrap !important;
      word-break: keep-all !important;
    }

    td[data-field="area"] * {
      white-space: nowrap !important;
      word-break: keep-all !important;
      writing-mode: horizontal-tb !important;
    }
    /* SHINNAN_BUILDING_AREA_PILL_HORIZONTAL_END */
  
    /* SHINNAN_BUILDING_TABLE_WIDTH_V2_START */
    table {
      table-layout: fixed !important;
    }

    th:nth-child(1), td:nth-child(1) { width: 101px !important; }
    th:nth-child(2), td:nth-child(2) { width: 150px !important; }
    th:nth-child(3), td:nth-child(3) { width: 105px !important; }
    th:nth-child(4), td:nth-child(4) { width: 32% !important; }
    th:nth-child(5), td:nth-child(5) { width: 145px !important; }
    th:nth-child(6), td:nth-child(6) { width: 86px !important; text-align: center !important; }
    th:nth-child(7), td:nth-child(7) { width: 86px !important; text-align: center !important; }
    th:nth-child(8), td:nth-child(8) { width: 140px !important; }
    th:nth-child(9), td:nth-child(9) { width: 86px !important; text-align: center !important; }
    th:nth-child(10), td:nth-child(10) { width: 86px !important; text-align: center !important; }

    .btn-small {
      min-width: 68px !important;
      width: 68px !important;
      height: 36px !important;
      padding: 6px 8px !important;
      border-radius: 10px !important;
      font-size: 14px !important;
      white-space: nowrap !important;
    }

    td[data-field="address"] {
      font-size: 18px !important;
      line-height: 1.35 !important;
      word-break: break-word !important;
      overflow-wrap: anywhere !important;
    }

    .modal-mask {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.58);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 100;
      padding: 20px;
    }

    .modal-mask.active {
      display: flex;
    }

    .modal {
      width: min(920px, 100%);
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 24px;
      box-shadow: 0 26px 80px rgba(0,0,0,.32);
    }

    .modal-title {
      font-size: 28px;
      font-weight: 1000;
      margin-bottom: 18px;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
    }

    .field label {
      display: block;
      color: #64748b;
      font-size: 14px;
      font-weight: 1000;
      margin-bottom: 6px;
    }

    .field input,
    .field select {
      width: 100%;
      height: 46px;
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      padding: 0 12px;
      font-size: 16px;
    }

    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 18px;
    }

    .btn-gray {
      background: #64748b !important;
    }

    @media (max-width: 900px) {
      .form-grid {
        grid-template-columns: 1fr;
      }
    }
    /* SHINNAN_BUILDING_TABLE_WIDTH_V2_END */

      /* SHINNAN_BUILDING_COLUMN_WIDTH_FINAL_START */
    table {
      width: 100% !important;
      table-layout: fixed !important;
    }

    /* 編號 */
    th:nth-child(1), td:nth-child(1) {
      width: 70px !important;
    }

    /* 大樓名稱：縮小 */
    th:nth-child(2), td:nth-child(2) {
      width: 125px !important;
    }

    /* 區域 */
    th:nth-child(3), td:nth-child(3) {
      width: 95px !important;
      text-align: center !important;
    }

    /* 地址：加寬，主要空間給地址 */
    th:nth-child(4), td:nth-child(4) {
      width: 34% !important;
      min-width: 360px !important;
    }

    /* 管理公司 */
    th:nth-child(5), td:nth-child(5) {
      width: 120px !important;
    }

    /* 用戶數量 */
    th:nth-child(6), td:nth-child(6) {
      width: 70px !important;
      text-align: center !important;
    }

    /* 住戶總數 */
    th:nth-child(7), td:nth-child(7) {
      width: 70px !important;
      text-align: center !important;
    }

    /* IP */
    th:nth-child(8), td:nth-child(8) {
      width: 135px !important;
    }

    /* 主機 */
    th:nth-child(9), td:nth-child(9) {
      width: 72px !important;
      text-align: center !important;
    }

    /* 選擇 */
    th:nth-child(10), td:nth-child(10) {
      width: 72px !important;
      text-align: center !important;
    }

    .btn-small {
      min-width: 58px !important;
      width: 58px !important;
      height: 34px !important;
      padding: 4px 6px !important;
      border-radius: 9px !important;
      font-size: 13px !important;
      white-space: nowrap !important;
    }

    td[data-field="name"] {
      white-space: normal !important;
      word-break: keep-all !important;
      line-height: 1.35 !important;
    }

    td[data-field="address"] {
      white-space: normal !important;
      word-break: break-word !important;
      overflow-wrap: anywhere !important;
      font-size: 18px !important;
      line-height: 1.35 !important;
    }
    /* SHINNAN_BUILDING_COLUMN_WIDTH_FINAL_END */
      
      
  </style>

<style id="buildings_button_center_fix_v1">
  /* 大樓名錄：所有按鈕文字垂直置中，修正手機/電腦版字體偏下 */
  button,
  .btn,
  .button,
  [role="button"] {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
    text-align: center !important;
  }
</style>

<style id="buildings_mobile_cards_v1">
  /* 手機版大樓名錄改成卡片式 */
  @media (max-width: 760px) {
    body {
      overflow-x: hidden !important;
    }

    .wrap,
    main,
    .container,
    .page,
    .content {
      max-width: 100% !important;
      padding-left: 10px !important;
      padding-right: 10px !important;
      box-sizing: border-box !important;
    }

    table {
      width: 100% !important;
      min-width: 0 !important;
      border-collapse: separate !important;
      border-spacing: 0 10px !important;
    }

    table thead {
      display: none !important;
    }

    table tbody {
      display: block !important;
      width: 100% !important;
    }

    table tbody tr {
      display: grid !important;
      grid-template-columns: 1fr 1fr !important;
      gap: 8px 10px !important;
      width: 100% !important;
      margin: 0 0 10px !important;
      padding: 14px !important;
      background: #ffffff !important;
      border: 1px solid #d7e1ef !important;
      border-radius: 18px !important;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08) !important;
      box-sizing: border-box !important;
    }

    table tbody tr td {
      display: block !important;
      width: auto !important;
      min-width: 0 !important;
      max-width: none !important;
      padding: 0 !important;
      border: 0 !important;
      background: transparent !important;
      color: #102348 !important;
      font-size: 14px !important;
      line-height: 1.35 !important;
      font-weight: 900 !important;
      white-space: normal !important;
      word-break: break-word !important;
    }

    table tbody tr td::before {
      content: attr(data-label);
      display: block;
      margin-bottom: 3px;
      color: #64748b;
      font-size: 11px;
      line-height: 1.2;
      font-weight: 1000;
    }

    /* 編號 */
    table tbody tr td:nth-child(1) {
      grid-column: 1 / 2 !important;
      color: #64748b !important;
      font-size: 13px !important;
    }

    /* 大樓名稱 */
    table tbody tr td:nth-child(2) {
      grid-column: 1 / -1 !important;
      font-size: 22px !important;
      font-weight: 1000 !important;
      color: #1d4ed8 !important;
    }

    table tbody tr td:nth-child(2)::before {
      display: none !important;
    }

    /* 區域 */
    table tbody tr td:nth-child(3) {
      grid-column: 1 / 2 !important;
    }

    /* 地址 */
    table tbody tr td:nth-child(4) {
      grid-column: 1 / -1 !important;
      font-size: 15px !important;
    }

    /* 管理公司 */
    table tbody tr td:nth-child(5) {
      grid-column: 1 / 2 !important;
    }

    /* 用戶數量 */
    table tbody tr td:nth-child(6) {
      grid-column: 2 / 3 !important;
    }

    /* 住戶總數 */
    table tbody tr td:nth-child(7) {
      grid-column: 1 / 2 !important;
    }

    /* IP */
    table tbody tr td:nth-child(8) {
      grid-column: 2 / 3 !important;
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace !important;
      font-size: 13px !important;
    }

    /* 主機欄手機先隱藏，避免佔空間 */
    table tbody tr td:nth-child(9) {
      display: none !important;
    }

    /* 選擇按鈕 */
    table tbody tr td:last-child {
      grid-column: 1 / -1 !important;
      margin-top: 4px !important;
    }

    table tbody tr td:last-child button,
    table tbody tr td:last-child a,
    table tbody tr td:last-child .btn {
      width: 100% !important;
      height: 38px !important;
      border-radius: 12px !important;
      font-size: 15px !important;
      font-weight: 1000 !important;
    }

    /* 詳細資料彈窗按鈕也修正置中 */
    .modal button,
    .dialog button,
    .popup button,
    [id*="modal"] button,
    [class*="modal"] button {
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      line-height: 1 !important;
      padding-top: 0 !important;
      padding-bottom: 0 !important;
    }
  }
</style>


<style id="buildings_mobile_hide_select_v1">
  @media (max-width: 760px) {
    table tbody tr td:last-child {
      display: none !important;
    }

    table tbody tr {
      padding-bottom: 14px !important;
    }
  }
</style>


<style id="buildings_sales_new_picker_v1">
  @media (max-width: 760px) {
    body:not(.sales-building-picker) table tbody tr td:last-child {
      display: none !important;
    }

    body.sales-building-picker table tbody tr td:last-child {
      display: block !important;
      grid-column: 1 / -1 !important;
      margin-top: 6px !important;
    }

    body.sales-building-picker table tbody tr td:last-child button,
    body.sales-building-picker table tbody tr td:last-child a,
    body.sales-building-picker table tbody tr td:last-child .btn {
      width: 100% !important;
      height: 40px !important;
      border-radius: 13px !important;
      font-size: 15px !important;
      font-weight: 1000 !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      line-height: 1 !important;
    }
  }
</style>

</head>

<body>
  <div class="topbar">
    
<style id="hide_building_host_column_v1">
  /* 大樓名錄列表隱藏「主機」欄位；API 與詳細資料仍保留 */
  table thead tr th:nth-child(9),
  table tbody tr td:nth-child(9) {
    display: none !important;
  }
</style>

<h1>大樓名錄</h1>
    <p>每區 10 棟｜地址 / 管理公司 / 用戶數量 / 住戶總數 / 主機登入 / 選擇大樓</p>
  </div>

  <main class="page">
    <div class="toolbar">
      <button type="button" onclick="location.href='/'">返回上一頁</button>
      <button type="button" id="create_building_button">新增資料</button>

      <select id="area_filter">
        <option value="全部">全部區域</option>
        <option value="東區">東區</option>
        <option value="北區">北區</option>
        <option value="北台南">北台南</option>
        <option value="仁德">仁德</option>
        <option value="永康">永康</option>
        <option value="安平">安平</option>
        <option value="南高">南高</option>
        <option value="北高">北高</option>
        <option value="透天">透天</option>
      </select>

      <input id="keyword" placeholder="搜尋大樓 / 地址 / 管理公司 / IP">
    </div>

    <section class="card">
      <div class="hint">提示：大樓名稱、區域、地址、管理公司、用戶數量、住戶總數、IP 可直接點擊修改。選擇大樓時會帶出「大樓名稱 + 地址」。</div>

      <table>
        <thead>
          <tr>
            <th>編號</th>
            <th>大樓名稱</th>
            <th>區域</th>
            <th>地址</th>
            <th>管理公司</th>
            <th>用戶數量</th>
            <th>住戶總數</th>
            <th>IP</th>
            <th>主機</th>
            <th>選擇</th>
          </tr>
        </thead>
        <tbody id="rows"></tbody>
      </table>
    </section>
  </main>

  <script>
    let buildings = [];
    const STORAGE_KEY = "shinnan_building_directory_overrides_v2";

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function goBackFromBuildings() {
      const params = new URLSearchParams(window.location.search);
      const caller = params.get("caller") || "";

      const pickReturn = localStorage.getItem("xunnan_building_pick_return") || "";
      const backReturn = localStorage.getItem("xunnan_building_back_return") || "";

      if (caller === "sales") {
        localStorage.removeItem("xunnan_building_back_return");
        window.location.href = "/admin/sales";
        return;
      }

      if (caller === "dispatch") {
        localStorage.removeItem("xunnan_building_back_return");
        window.location.href = "/admin";
        return;
      }

      if (backReturn) {
        localStorage.removeItem("xunnan_building_back_return");
        window.location.href = backReturn;
        return;
      }

      if (pickReturn) {
        if (pickReturn.includes("/admin/sales")) {
          window.location.href = "/admin/sales";
          return;
        }

        if (pickReturn.includes("/admin")) {
          window.location.href = "/admin";
          return;
        }
      }

      if (document.referrer) {
        try {
          const ref = new URL(document.referrer);

          if (ref.pathname === "/admin/sales") {
            window.location.href = "/admin/sales";
            return;
          }

          if (ref.pathname === "/admin") {
            window.location.href = "/admin";
            return;
          }

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

      if (caller === "dispatch") {
        window.location.href = "/admin";
        return;
      }

      if (returnUrl) {
        if (returnUrl.includes("/admin/sales")) {
          window.location.href = "/admin/sales";
          return;
        }

        if (returnUrl.includes("/admin")) {
          window.location.href = "/admin";
          return;
        }
      }

      if (document.referrer && document.referrer !== window.location.href) {
        history.back();
        return;
      }

      window.location.href = "/admin";
    }

    function loadOverrides() {
      try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      } catch (e) {
        return {};
      }
    }

    function saveOverride(buildingNo, field, value) {
      const overrides = loadOverrides();
      if (!overrides[buildingNo]) overrides[buildingNo] = {};
      overrides[buildingNo][field] = value;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(overrides));
    }

    function applyOverrides(data) {
      const overrides = loadOverrides();

      return data.map(function (item) {
        if (overrides[item.building_no]) {
          return Object.assign({}, item, overrides[item.building_no]);
        }
        return item;
      });
    }

    async function loadBuildings() {
      const res = await fetch("/api/admin/buildings?ts=" + Date.now());
      const data = await res.json();
      buildings = applyOverrides(data);
      renderRows();
    }

    function getFiltered() {
      const area = document.getElementById("area_filter").value;
      const keyword = document.getElementById("keyword").value.trim().toLowerCase();

      return buildings.filter(function (b) {
        if (area !== "全部" && b.area !== area) return false;
        if (!keyword) return true;

        return [
          b.building_no,
          b.name,
          b.area,
          b.address,
          b.management_company,
          b.ip
        ].join(" ").toLowerCase().includes(keyword);
      });
    }

    function renderRows() {
      const rows = document.getElementById("rows");
      const data = getFiltered();

      rows.innerHTML = data.map(function (b) {
        return `
          <tr data-building-no="${escapeHtml(b.building_no)}">
            <td>${escapeHtml(b.building_no)}</td>
            <td contenteditable="true" data-field="name">${escapeHtml(b.name)}</td>
            <td contenteditable="true" data-field="area"><span class="pill">${escapeHtml(b.area)}</span></td>
            <td contenteditable="true" data-field="address">${escapeHtml(b.address)}</td>
            <td contenteditable="true" data-field="management_company">${escapeHtml(b.management_company)}</td>
            <td contenteditable="true" data-field="active_users">${escapeHtml(b.active_users)}</td>
            <td contenteditable="true" data-field="total_households">${escapeHtml(b.total_households)}</td>
            <td contenteditable="true" data-field="ip">${escapeHtml(b.ip)}</td>
            <td><button class="btn-small" type="button" onclick="hostLogin('${escapeHtml(b.ip)}')">主機登入</button></td>
            <td><button class="btn-small" type="button" onclick="chooseBuilding('${escapeHtml(b.building_no)}')">選擇</button></td>
          </tr>
        `;
      }).join("");

      bindEditableCells();
    }

    function bindEditableCells() {
      document.querySelectorAll("td[contenteditable='true']").forEach(function (cell) {
        cell.addEventListener("blur", function () {
          const tr = cell.closest("tr");
          const buildingNo = tr.dataset.buildingNo;
          const field = cell.dataset.field;
          const value = cell.innerText.trim();

          saveOverride(buildingNo, field, value);

          const item = buildings.find(b => b.building_no === buildingNo);
          if (item) item[field] = value;

          renderRows();
        });

        cell.addEventListener("keydown", function (event) {
          if (event.key === "Enter") {
            event.preventDefault();
            cell.blur();
          }
        });
      });
    }

    function hostLogin(ip) {
      alert("主機登入：" + ip);
    }

    function chooseBuilding(buildingNo) {
      const b = buildings.find(item => item.building_no === buildingNo);
      if (!b) return;

      const fullAddress = `${b.name} ${b.address}`;

      const result = {
        building_no: b.building_no,
        name: b.name,
        area: b.area,
        raw_address: b.address,
        address: fullAddress,
        management_company: b.management_company,
        ip: b.ip
      };

      localStorage.setItem("xunnan_building_pick_result", JSON.stringify(result));
      localStorage.setItem("xunnan_selected_building_no", result.building_no);
      localStorage.setItem("xunnan_selected_building_name", result.name);
      localStorage.setItem("xunnan_selected_building_area", result.area);
      localStorage.setItem("xunnan_selected_building_raw_address", result.raw_address);
      localStorage.setItem("xunnan_selected_building_address", result.address);

      const returnUrl = localStorage.getItem("xunnan_building_pick_return") || "/admin";
      window.location.href = returnUrl;
    }

    document.getElementById("area_filter").addEventListener("change", renderRows);
    document.getElementById("keyword").addEventListener("input", renderRows);

    loadBuildings();
  </script>

  <div id="create_building_modal" class="modal-mask">
    <div class="modal">
      <div class="modal-title">新增大樓資料</div>

      <div class="form-grid">
        <div class="field">
          <label>大樓名稱</label>
          <input id="new_building_name" placeholder="例如 維冠大樓">
        </div>

        <div class="field">
          <label>區域</label>
          <select id="new_building_area">
            <option value="東區">東區</option>
            <option value="北區">北區</option>
            <option value="北台南">北台南</option>
            <option value="仁德">仁德</option>
            <option value="永康">永康</option>
            <option value="安平">安平</option>
            <option value="南高">南高</option>
            <option value="北高">北高</option>
            <option value="透天">透天</option>
          </select>
        </div>

        <div class="field">
          <label>地址</label>
          <input id="new_building_address" placeholder="例如 A棟1F-1">
        </div>

        <div class="field">
          <label>管理公司</label>
          <input id="new_management_company" placeholder="例如 安信管理">
        </div>

        <div class="field">
          <label>用戶數量</label>
          <input id="new_active_users" value="0">
        </div>

        <div class="field">
          <label>住戶總數</label>
          <input id="new_total_households" value="0">
        </div>

        <div class="field">
          <label>IP</label>
          <input id="new_building_ip" placeholder="例如 192.168.10.99">
        </div>
      </div>

      <div class="modal-actions">
        <button type="button" class="btn-gray" id="cancel_create_building_button">取消</button>
        <button type="button" id="save_create_building_button">新增資料</button>
      </div>
    </div>
  </div>


<script>
// SHINNAN_BUILDING_CREATE_DATA_V1
(function () {
  const ADD_STORAGE_KEY = "shinnan_building_directory_additional_v1";

  function loadAdditionalBuildings() {
    try {
      return JSON.parse(localStorage.getItem(ADD_STORAGE_KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function saveAdditionalBuildings(items) {
    localStorage.setItem(ADD_STORAGE_KEY, JSON.stringify(items));
  }

  function nextBuildingNo() {
    const additional = loadAdditionalBuildings();
    const nums = [];

    try {
      buildings.forEach(function (b) {
        const m = String(b.building_no || "").match(/^B(\\d+)$/);
        if (m) nums.push(Number(m[1]));
      });
    } catch (e) {}

    additional.forEach(function (b) {
      const m = String(b.building_no || "").match(/^B(\\d+)$/);
      if (m) nums.push(Number(m[1]));
    });

    const next = nums.length ? Math.max(...nums) + 1 : 1;
    return "B" + String(next).padStart(3, "0");
  }

  function openCreateBuildingModal() {
    const modal = document.getElementById("create_building_modal");
    if (modal) modal.classList.add("active");
  }

  function closeCreateBuildingModal() {
    const modal = document.getElementById("create_building_modal");
    if (modal) modal.classList.remove("active");
  }

  function createBuilding() {
    const name = document.getElementById("new_building_name").value.trim();
    const area = document.getElementById("new_building_area").value;
    const address = document.getElementById("new_building_address").value.trim();
    const managementCompany = document.getElementById("new_management_company").value.trim();
    const activeUsers = Number(String(document.getElementById("new_active_users").value || "0").replace(/[^\\d]/g, ""));
    const totalHouseholds = Number(String(document.getElementById("new_total_households").value || "0").replace(/[^\\d]/g, ""));
    const ip = document.getElementById("new_building_ip").value.trim();

    if (!name) {
      alert("請輸入大樓名稱");
      return;
    }

    if (!address) {
      alert("請輸入地址");
      return;
    }

    const item = {
      building_no: nextBuildingNo(),
      name: name,
      area: area,
      address: address,
      display_address: name + " " + address,
      management_company: managementCompany || "未填",
      active_users: activeUsers,
      total_households: totalHouseholds,
      ip: ip || "未設定"
    };

    const additional = loadAdditionalBuildings();
    additional.push(item);
    saveAdditionalBuildings(additional);

    buildings.push(item);

    closeCreateBuildingModal();
    renderRows();

    document.getElementById("new_building_name").value = "";
    document.getElementById("new_building_address").value = "";
    document.getElementById("new_management_company").value = "";
    document.getElementById("new_active_users").value = "0";
    document.getElementById("new_total_households").value = "0";
    document.getElementById("new_building_ip").value = "";

    alert("大樓資料已新增");
  }

  function patchLoadBuildings() {
    if (window.__shinnanBuildingCreatePatched) return;
    window.__shinnanBuildingCreatePatched = true;

    const oldLoadBuildings = window.loadBuildings || loadBuildings;

    window.loadBuildings = async function () {
      const res = await fetch("/api/admin/buildings?ts=" + Date.now());
      const data = await res.json();
      const merged = data.concat(loadAdditionalBuildings());
      buildings = applyOverrides(merged);
      renderRows();
    };
  }

  document.addEventListener("DOMContentLoaded", function () {
    patchLoadBuildings();

    const createButton = document.getElementById("create_building_button");
    const cancelButton = document.getElementById("cancel_create_building_button");
    const saveButton = document.getElementById("save_create_building_button");

    if (createButton) createButton.addEventListener("click", openCreateBuildingModal);
    if (cancelButton) cancelButton.addEventListener("click", closeCreateBuildingModal);
    if (saveButton) saveButton.addEventListener("click", createBuilding);
  });
})();
</script>



<script id="shinnan_buildings_simple_back_v1">
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  function goBackFromBuildingsSimple(event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    if (window.history.length > 1) {
      window.history.back();
      return;
    }

    window.location.href = "/admin";
  }

  window.goBackFromBuildings = goBackFromBuildingsSimple;

  function bindBackButtons() {
    Array.from(document.querySelectorAll("button, a")).forEach(function (el) {
      const text = String(el.textContent || "").trim();

      if (text === "返回上一頁" || text === "返回後台" || text === "返回首頁") {
        el.textContent = "返回上一頁";
        el.onclick = goBackFromBuildingsSimple;
        el.addEventListener("click", goBackFromBuildingsSimple, true);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindBackButtons);
  } else {
    bindBackButtons();
  }

  setTimeout(bindBackButtons, 300);
  setTimeout(bindBackButtons, 800);
})();
</script>


<style id="shinnan_building_detail_modal_style_v1">
  .building-name-link {
    border: 0;
    background: transparent;
    color: #1d4ed8;
    font-size: inherit;
    font-weight: 1000;
    cursor: pointer;
    padding: 0;
    text-align: left;
  }

  .building-name-link:hover {
    text-decoration: underline;
  }

  .building-detail-mask {
    position: fixed;
    inset: 0;
    display: none;
    align-items: center;
    justify-content: center;
    background: rgba(15, 23, 42, 0.58);
    z-index: 9000;
    padding: 20px;
  }

  .building-detail-mask.active {
    display: flex;
  }

  .building-detail-modal {
    width: min(1180px, 96vw);
    max-height: 90vh;
    overflow: auto;
    background: #ffffff;
    border-radius: 22px;
    box-shadow: 0 28px 90px rgba(0,0,0,0.30);
    padding: 20px;
    color: #102348;
    font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
  }

  .building-detail-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 14px;
    margin-bottom: 14px;
    border-bottom: 1px solid #dbe7f5;
    padding-bottom: 12px;
  }

  .building-detail-title {
    font-size: 30px;
    font-weight: 1000;
    line-height: 1.2;
  }

  .building-detail-sub {
    margin-top: 6px;
    color: #64748b;
    font-size: 14px;
    font-weight: 800;
  }

  .building-detail-close {
    height: 34px;
    min-width: 78px;
    border: 0;
    border-radius: 10px;
    background: #64748b;
    color: #fff;
    font-size: 15px;
    font-weight: 900;
    cursor: pointer;
  }

  .building-detail-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
  }

  .building-detail-card {
    border: 1px solid #dbe7f5;
    border-radius: 16px;
    background: #f8fbff;
    padding: 12px;
  }

  .building-detail-card.full {
    grid-column: 1 / -1;
  }

  .building-detail-card.half {
    grid-column: span 2;
  }

  .building-detail-label {
    color: #64748b;
    font-size: 13px;
    font-weight: 900;
    margin-bottom: 5px;
  }

  .building-detail-value {
    color: #102348;
    font-size: 16px;
    font-weight: 1000;
    line-height: 1.45;
    white-space: pre-wrap;
  }

  .building-detail-section {
    grid-column: 1 / -1;
    margin-top: 4px;
    padding: 8px 10px;
    border-radius: 12px;
    background: #eaf2ff;
    color: #24415f;
    font-size: 17px;
    font-weight: 1000;
  }

  @media (max-width: 980px) {
    .building-detail-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 640px) {
    .building-detail-grid {
      grid-template-columns: 1fr;
    }

    .building-detail-card.half {
      grid-column: 1 / -1;
    }
  }
</style>

<div id="building_detail_mask" class="building-detail-mask">
  <div class="building-detail-modal">
    <div class="building-detail-head">
      <div>
        <div id="building_detail_title" class="building-detail-title">大樓詳細資料</div>
        <div id="building_detail_sub" class="building-detail-sub"></div>
      </div>
      <button class="building-detail-close" type="button" onclick="window.closeBuildingDetailModal && window.closeBuildingDetailModal()">關閉</button>
    </div>

    <div id="building_detail_body" class="building-detail-grid"></div>
  </div>
</div>

<script id="shinnan_building_detail_modal_v1">
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  const BUSINESS_STORAGE_KEY = "shinnan_building_business_records_v1";

  function safeText(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function readJson(key, fallback) {
    try {
      return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback));
    } catch (err) {
      return fallback;
    }
  }

  function normalizeName(value) {
    return String(value || "").trim();
  }

  function findBusinessRecordForBuilding(building) {
    const records = readJson(BUSINESS_STORAGE_KEY, []);
    const buildingName = normalizeName(building.name || building.building_name);

    if (!Array.isArray(records) || !buildingName) return null;

    return records.find(function (item) {
      return normalizeName(item.building_name) === buildingName;
    }) || null;
  }

  function card(label, value, extraClass) {
    return `
      <div class="building-detail-card ${extraClass || ""}">
        <div class="building-detail-label">${safeText(label)}</div>
        <div class="building-detail-value">${safeText(value || "-")}</div>
      </div>
    `;
  }

  function section(title) {
    return `<div class="building-detail-section">${safeText(title)}</div>`;
  }

  window.closeBuildingDetailModal = function () {
    const mask = document.getElementById("building_detail_mask");
    if (mask) mask.classList.remove("active");
  };

  window.openBuildingDetailModal = function (building) {
    building = building || {};

    const record = findBusinessRecordForBuilding(building) || {};
    const title = document.getElementById("building_detail_title");
    const sub = document.getElementById("building_detail_sub");
    const body = document.getElementById("building_detail_body");
    const mask = document.getElementById("building_detail_mask");

    if (!body || !mask) return;

    const buildingName = building.name || building.building_name || record.building_name || "未命名大樓";

    if (title) title.textContent = buildingName;
    if (sub) {
      sub.textContent =
        "區域：" + (building.area || record.area || "-") +
        "｜地址：" + (building.raw_address || building.address || "-");
    }

    body.innerHTML = [
      section("大樓基本資料"),
      card("編號", building.building_no || building.no || ""),
      card("區域", building.area || record.area || ""),
      card("地址", building.raw_address || building.address || ""),
      card("管理公司", building.management_company || record.management_company || ""),
      card("用戶數量", building.active_users ?? building.user_count ?? ""),
      card("住戶總數", building.total_households ?? building.households ?? ""),
      card("IP", building.ip || ""),
      card("主機", building.host || building.main_host || ""),

      section("管理室／總幹事"),
      card("管理室電話", record.management_phone || ""),
      card("總幹事姓名", record.manager_name || ""),
      card("總幹事電話", record.manager_phone || ""),
      card("總幹事年齡", record.manager_age ? record.manager_age + " 歲" : ""),
      card("總幹事資歷", record.manager_experience || ""),
      card("總幹事興趣", record.manager_interest || ""),
      card("可拜訪時段", record.visit_time || ""),
      card("管理室資訊／注意事項", record.management_note || "", "full"),

      section("會議／合約"),
      card("委員會時間", record.committee_time || ""),
      card("住戶大會時間", record.resident_meeting_time || ""),
      card("合約狀態", record.contract_status || ""),
      card("合約到期日", record.contract_end_date || ""),

      section("業務資訊"),
      card("業務類型", record.business_type || ""),
      card("目前狀態", record.status || ""),
      card("負責業務", record.owner || ""),
      card("下次拜訪", record.next_visit || ""),
      card("業務事件", record.event_type && record.event_type !== "無" ? record.event_type + "｜" + (record.event_status || "") : ""),
      card("事件安排日期", record.event_schedule_date || ""),
      card("回饋項目", record.feedback_type && record.feedback_type !== "無" ? record.feedback_type + "｜" + (record.feedback_status || "") : ""),
      card("業務紀錄／拜訪結果", record.business_note || "", "full")
    ].join("");

    mask.classList.add("active");
  };

  function bindExistingBuildingNameCells() {
    const rows = Array.from(document.querySelectorAll("tbody tr"));

    rows.forEach(function (row) {
      const cells = row.querySelectorAll("td");
      if (cells.length < 2) return;

      const nameCell = cells[1];
      if (nameCell.querySelector(".building-name-link")) return;

      const name = nameCell.textContent.trim();
      if (!name) return;

      const building = {
        building_no: cells[0] ? cells[0].textContent.trim() : "",
        name: name,
        area: cells[2] ? cells[2].textContent.trim() : "",
        address: cells[3] ? cells[3].textContent.trim() : "",
        raw_address: cells[3] ? cells[3].textContent.trim() : "",
        management_company: cells[4] ? cells[4].textContent.trim() : "",
        active_users: cells[5] ? cells[5].textContent.trim() : "",
        total_households: cells[6] ? cells[6].textContent.trim() : "",
        ip: cells[7] ? cells[7].textContent.trim() : "",
        host: cells[8] ? cells[8].textContent.trim() : ""
      };

      nameCell.innerHTML = "";
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "building-name-link";
      btn.textContent = name;
      btn.onclick = function () {
        window.openBuildingDetailModal(building);
      };
      nameCell.appendChild(btn);
    });
  }

  document.addEventListener("click", function (event) {
    const mask = document.getElementById("building_detail_mask");
    if (event.target === mask) {
      window.closeBuildingDetailModal();
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindExistingBuildingNameCells);
  } else {
    bindExistingBuildingNameCells();
  }

  setTimeout(bindExistingBuildingNameCells, 500);
  setTimeout(bindExistingBuildingNameCells, 1000);
})();
</script>

<script id="shinnan_buildings_render_recovery_v1">
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  const ADD_STORAGE_KEY = "shinnan_building_directory_additional_v1";
  const OVERRIDE_STORAGE_KEY = "shinnan_building_directory_overrides_v1";

  function safeText(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function readJson(key, fallback) {
    try {
      return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback));
    } catch (err) {
      return fallback;
    }
  }

  function getAreaFilter() {
    const el = document.getElementById("area_filter");
    return el ? el.value : "全部";
  }

  function getKeyword() {
    const el = document.getElementById("keyword");
    return el ? el.value.trim().toLowerCase() : "";
  }

  function getRowsBox() {
    return (
      document.getElementById("building_rows") ||
      document.getElementById("building_table_body") ||
      document.querySelector("tbody")
    );
  }

  function normalizeBuilding(item) {
    const name = item.name || item.building_name || "";
    const rawAddress = item.raw_address || item.address || item.display_address || "";

    return {
      building_no: item.building_no || item.no || "",
      name: name,
      area: item.area || "",
      address: rawAddress,
      raw_address: rawAddress,
      management_company: item.management_company || "",
      active_users: item.active_users ?? item.user_count ?? "",
      total_households: item.total_households ?? item.households ?? "",
      ip: item.ip || "",
      host: item.host || item.main_host || ""
    };
  }

  function mergeData(apiData) {
    const additional = readJson(ADD_STORAGE_KEY, []);
    const overrides = readJson(OVERRIDE_STORAGE_KEY, {});

    let data = Array.isArray(apiData) ? apiData.slice() : [];

    if (Array.isArray(additional) && additional.length) {
      data = data.concat(additional);
    }

    data = data.map(function (item) {
      const normalized = normalizeBuilding(item);
      const override = overrides[normalized.building_no] || {};
      return Object.assign({}, normalized, override);
    });

    return data;
  }

  function filteredBuildings(data) {
    const area = getAreaFilter();
    const keyword = getKeyword();

    return data.filter(function (b) {
      if (area !== "全部" && b.area !== area) return false;

      if (!keyword) return true;

      const hay = [
        b.building_no,
        b.name,
        b.area,
        b.address,
        b.management_company,
        b.active_users,
        b.total_households,
        b.ip,
        b.host
      ].join(" ").toLowerCase();

      return hay.includes(keyword);
    });
  }

  function chooseBuildingRecovery(b) {
    const result = {
      building_no: b.building_no || "",
      name: b.name || "",
      area: b.area || "",
      address: b.name && b.address ? b.name + " " + b.address : (b.address || ""),
      raw_address: b.address || "",
      management_company: b.management_company || "",
      ip: b.ip || ""
    };

    localStorage.setItem("xunnan_building_pick_result", JSON.stringify(result));
    localStorage.setItem("xunnan_selected_building_no", result.building_no);
    localStorage.setItem("xunnan_selected_building_name", result.name);
    localStorage.setItem("xunnan_selected_building_area", result.area);
    localStorage.setItem("xunnan_selected_building_raw_address", result.raw_address);
    localStorage.setItem("xunnan_selected_building_address", result.address);

    const returnUrl = localStorage.getItem("xunnan_building_pick_return");

    if (returnUrl) {
      window.location.href = returnUrl;
      return;
    }

    const params = new URLSearchParams(window.location.search);
    const caller = params.get("caller") || "";

    if (caller === "sales") {
      window.location.href = "/admin/sales?open_sales_modal=1&from_building_pick=1&caller=sales";
      return;
    }

    window.location.href = "/admin?open_create=1&from_building_pick=1";
  }

  window.__shinnanBuildingChooseRecovery = chooseBuildingRecovery;

  function renderBuildingsRecovery(data) {
    const rows = getRowsBox();
    if (!rows) return;

    const filtered = filteredBuildings(data);

    if (!filtered.length) {
      rows.innerHTML = '<tr><td colspan="10">目前沒有符合條件的大樓資料。</td></tr>';
      return;
    }

    rows.innerHTML = filtered.map(function (b, index) {
      const encoded = encodeURIComponent(JSON.stringify(b));

      return `
        <tr>
          <td>${safeText(b.building_no)}</td>
          <td>
            <button
              class="building-name-link"
              type="button"
              onclick="window.openBuildingDetailModal && window.openBuildingDetailModal(JSON.parse(decodeURIComponent('${encoded}')))"
            >${safeText(b.name)}</button>
          </td>
          <td>${safeText(b.area)}</td>
          <td>${safeText(b.address)}</td>
          <td>${safeText(b.management_company)}</td>
          <td>${safeText(b.active_users)}</td>
          <td>${safeText(b.total_households)}</td>
          <td>${safeText(b.ip)}</td>
          <td>${safeText(b.host || "-")}</td>
          <td>
            <button
              class="btn-blue"
              type="button"
              onclick="window.__shinnanBuildingChooseRecovery(JSON.parse(decodeURIComponent('${encoded}')))"
            >選擇</button>
          </td>
        </tr>
      `;
    }).join("");
  }

  async function loadBuildingsRecovery() {
    try {
      const res = await fetch("/api/admin/buildings?ts=" + Date.now(), {cache: "no-store"});
      const apiData = await res.json();
      const data = mergeData(apiData);

      window.__shinnanBuildingsRecoveryData = data;
      renderBuildingsRecovery(data);
    } catch (err) {
      console.error("大樓名錄救援渲染失敗", err);

      const rows = getRowsBox();
      if (rows) {
        rows.innerHTML = '<tr><td colspan="10">大樓資料讀取失敗，請查看瀏覽器 Console。</td></tr>';
      }
    }
  }

  function bindRecoveryFilters() {
    const area = document.getElementById("area_filter");
    const keyword = document.getElementById("keyword");

    if (area) {
      area.onchange = function () {
        renderBuildingsRecovery(window.__shinnanBuildingsRecoveryData || []);
      };
    }

    if (keyword) {
      keyword.oninput = function () {
        renderBuildingsRecovery(window.__shinnanBuildingsRecoveryData || []);
      };
    }
  }

  function startRecovery() {
    bindRecoveryFilters();
    loadBuildingsRecovery();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startRecovery);
  } else {
    startRecovery();
  }

  setTimeout(startRecovery, 500);
})();
</script>



<script id="buildings_mobile_cards_v1">
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  function applyBuildingMobileLabels() {
    const tables = Array.from(document.querySelectorAll("table"));
    if (!tables.length) return;

    tables.forEach(function (table) {
      const headers = Array.from(table.querySelectorAll("thead th")).map(function (th) {
        return (th.textContent || "").trim();
      });

      if (!headers.length) {
        // 若沒有表頭，就用目前大樓名錄預設欄位
        headers.push("編號", "大樓名稱", "區域", "地址", "管理公司", "用戶數量", "住戶總數", "IP", "主機", "選擇");
      }

      table.querySelectorAll("tbody tr").forEach(function (tr) {
        Array.from(tr.children).forEach(function (td, index) {
          if (!td.getAttribute("data-label")) {
            td.setAttribute("data-label", headers[index] || "");
          }
        });
      });
    });
  }

  function fixButtonVerticalCenter() {
    document.querySelectorAll("button, .btn, .button, [role='button']").forEach(function (btn) {
      btn.style.display = "inline-flex";
      btn.style.alignItems = "center";
      btn.style.justifyContent = "center";
      btn.style.lineHeight = "1";
    });
  }

  function applyAll() {
    applyBuildingMobileLabels();
    fixButtonVerticalCenter();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyAll);
  } else {
    applyAll();
  }

  setTimeout(applyAll, 300);
  setTimeout(applyAll, 900);

  const observer = new MutationObserver(function () {
    setTimeout(applyAll, 0);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
})();
</script>


<script id="buildings_sales_new_picker_v1">
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  const params = new URLSearchParams(location.search);
  const isPicker = params.get("pick") === "sales_new";

  if (isPicker) {
    document.body.classList.add("sales-building-picker");
    document.title = "選擇大樓｜訊南 ERP";
  }

  function pickUrl(buildingNo, buildingName) {
    return "/app/sales/new?building_no=" +
      encodeURIComponent(buildingNo || "") +
      "&building_name=" +
      encodeURIComponent(buildingName || "") +
      "&ts=" + Date.now();
  }

  function applySalesNewPicker() {
    if (!isPicker) return;

    document.querySelectorAll("table tbody tr").forEach(function (tr) {
      const cells = Array.from(tr.children);

      if (cells.length < 2) return;

      const buildingNo = (cells[0].textContent || "").trim();
      const buildingName = (cells[1].textContent || "").trim();

      const last = cells[cells.length - 1];
      if (!last) return;

      last.innerHTML = "";

      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = "選擇此大樓";
      btn.onclick = function () {
        location.href = pickUrl(buildingNo, buildingName);
      };

      last.appendChild(btn);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applySalesNewPicker);
  } else {
    applySalesNewPicker();
  }

  setTimeout(applySalesNewPicker, 300);
  setTimeout(applySalesNewPicker, 900);

  const observer = new MutationObserver(function () {
    setTimeout(applySalesNewPicker, 0);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
})();

</script>

<script id="shinnan_dispatch_recovery_render_v1">
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
</script>

</body>
</html>
"""
# SHINNAN_BUILDINGS_PAGE_RESTORE_END

