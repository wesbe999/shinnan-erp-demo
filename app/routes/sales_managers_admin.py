import json as _managers_json

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.responses import Response as _ManagersResponse
from sqlalchemy import text as _managers_sql_text

from app.db import engine as _managers_engine

router = APIRouter(tags=["sales-managers-admin"])


# SHINNAN_SALES_MANAGERS_PAGE_ROUTE_START
@router.get("/admin/sales/managers", response_class=HTMLResponse)
def admin_sales_managers_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>總幹事名錄｜訊南 ERP</title>
  <style>
    body {
      margin: 0;
      background: #eef3f9;
      color: #102348;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .wrap {
      max-width: 1680px;
      margin: 0 auto;
      padding: 22px;
    }

    .hero {
      border-radius: 24px;
      padding: 28px;
      background: linear-gradient(135deg, #2f7b7b, #365ee8, #7c3aed);
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
      grid-template-columns: auto auto 220px 1fr;
      gap: 12px;
      align-items: center;
      margin: 16px 0;
    }

    button, select, input {
      height: 42px;
      border-radius: 12px;
      border: 1px solid #cbd5e1;
      font-size: 16px;
      font-weight: 900;
      padding: 0 14px;
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

    .card {
      background: #fff;
      border: 1px solid #d7e1ef;
      border-radius: 22px;
      padding: 14px;
      box-shadow: 0 12px 34px rgba(15,23,42,.07);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }

    th {
      background: #eaf2ff;
      color: #203a5f;
      font-size: 15px;
      font-weight: 1000;
      text-align: left;
      padding: 12px 10px;
    }

    td {
      border-bottom: 1px solid #e5edf7;
      padding: 12px 10px;
      font-size: 15px;
      font-weight: 800;
      vertical-align: top;
      line-height: 1.55;
      color: #102348;
    }

    .muted {
      color: #64748b;
      font-size: 13px;
      font-weight: 800;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 10px;
      border-radius: 999px;
      background: #eaf2ff;
      color: #1d4ed8;
      font-size: 13px;
      font-weight: 1000;
    }

    .empty {
      padding: 28px;
      text-align: center;
      color: #64748b;
      font-weight: 900;
    }

    @media (max-width: 900px) {
      .toolbar {
        grid-template-columns: 1fr;
      }

      table {
        min-width: 1100px;
      }

      .card {
        overflow-x: auto;
      }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>總幹事名錄</h1>
      <div class="sub">由 manager_contacts 資料表提供，不再從工程師名錄讀取。</div>
    </section>

    <div class="toolbar">
      <button type="button" onclick="history.back()">返回上一頁</button>
      <button type="button" class="gray" onclick="location.href='/admin/sales'">回業務系統</button>
      <select id="area_filter">
        <option value="全部">全部區域</option>
      </select>
      <input id="keyword_filter" placeholder="搜尋總幹事 / 電話 / 大樓 / 管理公司">
    </div>

    <div class="card">
      <table>
        <thead>
          <tr>
            <th style="width:90px;">編號</th>
            <th style="width:150px;">總幹事</th>
            <th style="width:140px;">電話</th>
            <th style="width:170px;">管理公司</th>
            <th style="width:190px;">服務大樓</th>
            <th style="width:90px;">區域</th>
            <th style="width:120px;">資歷</th>
            <th style="width:170px;">興趣</th>
            <th style="width:180px;">可拜訪時段</th>
            <th>會議資訊</th>
          </tr>
        </thead>
        <tbody id="manager_rows">
          <tr><td colspan="10" class="empty">資料載入中...</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <script>
    let managerRows = [];

    function esc(v) {
      return String(v ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    async function loadManagers() {
      const res = await fetch("/api/admin/sales/managers?ts=" + Date.now(), {cache: "no-store"});

      if (!res.ok) {
        document.getElementById("manager_rows").innerHTML =
          '<tr><td colspan="10" class="empty">總幹事 API 讀取失敗：' + res.status + '</td></tr>';
        return;
      }

      managerRows = await res.json();
      buildAreaFilter();
      renderManagers();
    }

    function buildAreaFilter() {
      const sel = document.getElementById("area_filter");
      const areas = Array.from(new Set(managerRows.map(x => x.area).filter(Boolean))).sort();

      sel.innerHTML = '<option value="全部">全部區域</option>' +
        areas.map(a => '<option value="' + esc(a) + '">' + esc(a) + '</option>').join("");
    }

    function filteredManagers() {
      const area = document.getElementById("area_filter").value;
      const keyword = document.getElementById("keyword_filter").value.trim().toLowerCase();

      return managerRows.filter(function (item) {
        if (area !== "全部" && item.area !== area) return false;

        if (keyword) {
          const hay = [
            item.name,
            item.phone,
            item.management_company,
            item.building_name,
            item.area,
            item.interest,
            item.committee_time,
            item.resident_meeting_time
          ].join(" ").toLowerCase();

          if (!hay.includes(keyword)) return false;
        }

        return true;
      });
    }

    function renderManagers() {
      const box = document.getElementById("manager_rows");
      const rows = filteredManagers();

      if (!rows.length) {
        box.innerHTML = '<tr><td colspan="10" class="empty">沒有符合條件的總幹事資料。</td></tr>';
        return;
      }

      box.innerHTML = rows.map(function (item) {
        return `
          <tr>
            <td>${esc(item.manager_code || "-")}</td>
            <td>
              <b>${esc(item.name || "-")}</b>
              <div class="muted">${esc(item.age || "-")} 歲</div>
            </td>
            <td>${esc(item.phone || "-")}</td>
            <td>${esc(item.management_company || "-")}</td>
            <td>
              <b>${esc(item.building_name || "-")}</b>
              <div class="muted">${esc(item.building_no || "-")}</div>
            </td>
            <td><span class="pill">${esc(item.area || "-")}</span></td>
            <td>${esc(item.experience || "-")}</td>
            <td>${esc(item.interest || "-")}</td>
            <td>${esc(item.visit_time || "-")}</td>
            <td>
              <div>委員會：${esc(item.committee_time || "-")}</div>
              <div class="muted">住戶大會：${esc(item.resident_meeting_time || "-")}</div>
            </td>
          </tr>
        `;
      }).join("");
    }

    document.getElementById("area_filter").addEventListener("change", renderManagers);
    document.getElementById("keyword_filter").addEventListener("input", renderManagers);

    loadManagers();
  </script>

  <script src="/static/app_header_actions.js?v=cl17p6"></script>
<script src='/static/xn_theme.js?v=1'></script>
</body>
</html>
"""

# SHINNAN_SALES_MANAGERS_PAGE_ROUTE_END


# SHINNAN_SALES_DEMO_SEED_ROUTE_START_REMOVED_CLEANUP_STEP1_20260502
# This obsolete route block was removed during pages.py cleanup step 1.
# SHINNAN_SALES_DEMO_SEED_ROUTE_END_REMOVED_CLEANUP_STEP1_20260502





# SHINNAN_SALES_WORK_DEMO_SEED_ROUTE_START_REMOVED_CLEANUP_STEP1_20260502
# This obsolete route block was removed during pages.py cleanup step 1.
# SHINNAN_SALES_WORK_DEMO_SEED_ROUTE_END_REMOVED_CLEANUP_STEP1_20260502


# SHINNAN_MANAGER_CONTACTS_API_START
def _manager_contacts_db_init():
    with _managers_engine.begin() as conn:
        conn.execute(_managers_sql_text("""
            CREATE TABLE IF NOT EXISTS manager_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manager_code TEXT DEFAULT '',
                name TEXT NOT NULL,
                phone TEXT DEFAULT '',
                age TEXT DEFAULT '',
                management_company TEXT DEFAULT '',
                experience TEXT DEFAULT '',
                interest TEXT DEFAULT '',
                visit_time TEXT DEFAULT '',
                committee_time TEXT DEFAULT '',
                resident_meeting_time TEXT DEFAULT '',
                building_no TEXT DEFAULT '',
                building_name TEXT DEFAULT '',
                area TEXT DEFAULT '',
                note TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))


@router.get("/api/admin/sales/managers", summary="讀取總幹事名錄")
def api_admin_sales_managers():
    _manager_contacts_db_init()

    with _managers_engine.begin() as conn:
        rows = conn.execute(_managers_sql_text("""
            SELECT
                manager_code,
                name,
                phone,
                age,
                management_company,
                experience,
                interest,
                visit_time,
                committee_time,
                resident_meeting_time,
                building_no,
                building_name,
                area,
                note
            FROM manager_contacts
            ORDER BY CAST(substr(building_no, 2) AS INTEGER) ASC, id ASC
        """)).mappings().fetchall()

    return _ManagersResponse(
        content=_managers_json.dumps([dict(row) for row in rows], ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )
# SHINNAN_MANAGER_CONTACTS_API_END
