from __future__ import annotations

import json as _sales_json
import json as _managers_json
from datetime import datetime as _emp_datetime
from urllib.parse import parse_qs as _emp_parse_qs

from fastapi import APIRouter
from fastapi import Request as _EmpRequest
from fastapi.responses import HTMLResponse
from fastapi.responses import Response as _ManagersResponse
from fastapi.responses import Response as _SalesResponse
from fastapi.responses import RedirectResponse as _EmpRedirectResponse
from sqlalchemy import text as _sales_sql_text
from sqlalchemy import text as _buildings_sql_text

from app.db import engine as _sales_engine
from app.db import engine as _buildings_engine
from app.routes.employee_auth import _employee_current_user_from_request


router = APIRouter(tags=["手機業務 APP"])


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


def _sales_business_records_init():
    with _sales_engine.begin() as conn:
        conn.execute(_sales_sql_text("""
            CREATE TABLE IF NOT EXISTS sales_business_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_no TEXT NOT NULL,
                business_type TEXT DEFAULT '',
                status TEXT DEFAULT '',
                contract_status TEXT DEFAULT '',
                contract_end_date TEXT DEFAULT '',
                feedback_type TEXT DEFAULT '',
                feedback_status TEXT DEFAULT '',
                event_type TEXT DEFAULT '',
                event_status TEXT DEFAULT '',
                event_schedule_date TEXT DEFAULT '',
                important_schedule INTEGER DEFAULT 0,
                next_visit TEXT DEFAULT '',
                owner TEXT DEFAULT '',
                business_note TEXT DEFAULT '',
                demo_type TEXT DEFAULT '',
                created_at TEXT DEFAULT '',
                updated_at TEXT DEFAULT ''
            )
        """))


def api_admin_sales_business_records():
    _sales_business_records_init()
    _buildings_db_init()

    with _sales_engine.begin() as conn:
        rows = conn.execute(_sales_sql_text("""
            SELECT
                s.id AS id,
                s.building_no AS building_no,
                b.name AS building_name,
                b.area AS area,
                b.address AS building_address,
                b.management_company AS management_company,
                b.management_phone AS management_phone,
                b.manager_name AS manager_name,
                b.manager_phone AS manager_phone,
                b.manager_age AS manager_age,
                b.manager_experience AS manager_experience,
                b.manager_interest AS manager_interest,
                b.visit_time AS visit_time,
                b.committee_time AS committee_time,
                b.resident_meeting_time AS resident_meeting_time,
                s.business_type AS business_type,
                s.status AS status,
                s.contract_status AS contract_status,
                s.contract_end_date AS contract_end_date,
                s.feedback_type AS feedback_type,
                s.feedback_status AS feedback_status,
                s.event_type AS event_type,
                s.event_status AS event_status,
                s.event_schedule_date AS event_schedule_date,
                s.important_schedule AS important_schedule,
                s.next_visit AS next_visit,
                s.owner AS owner,
                s.business_note AS business_note,
                s.demo_type AS demo_type,
                s.created_at AS created_at,
                s.updated_at AS updated_at
            FROM sales_business_records s
            LEFT JOIN buildings b ON b.building_no = s.building_no
            ORDER BY s.id DESC
        """)).mappings().fetchall()

    records = []

    for row in rows:
        item = dict(row)
        item["important_schedule"] = bool(item.get("important_schedule"))
        item["management_note"] = (
            "大樓地址：" + str(item.get("building_address") or "") + "\n"
            "管理公司：" + str(item.get("management_company") or "") + "\n"
            "管理室電話：" + str(item.get("management_phone") or "")
        )
        records.append(item)

    return _SalesResponse(
        content=_sales_json.dumps(records, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


# SHINNAN_SALES_MOBILE_APP_START
@router.get("/app/sales", response_class=HTMLResponse)
def sales_mobile_app_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

  <title>訊南業務系統｜訊南 ERP</title>

  <style>
    :root {
      --bg: #eef3f9;
      --card: #ffffff;
      --line: #d7e1ef;
      --text: #102348;
      --muted: #64748b;
      --blue: #365ee8;
      --green: #16a34a;
      --orange: #f97316;
      --purple: #7c3aed;
      --red: #dc2626;
    }

    * {
      box-sizing: border-box;
      -webkit-tap-highlight-color: transparent;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .app {
      min-height: 100vh;
      padding-bottom: 88px;
    }

    .top {
      position: sticky;
      top: 0;
      z-index: 20;
      padding: 14px 14px 10px;
      background: linear-gradient(135deg, #0f766e, #2563eb, #7c3aed);
      color: #fff;
      box-shadow: 0 10px 28px rgba(15, 23, 42, 0.22);
      border-bottom-left-radius: 22px;
      border-bottom-right-radius: 22px;
    }

    .top-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
    }

    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 1000;
      letter-spacing: 0.02em;
    }

    .top-sub {
      margin-top: 4px;
      font-size: 13px;
      font-weight: 800;
      opacity: 0.9;
    }

    .home-btn {
      border: 0;
      border-radius: 12px;
      height: 34px;
      padding: 0 12px;
      background: rgba(255,255,255,0.18);
      color: #fff;
      font-size: 13px;
      font-weight: 1000;
    }

    .summary {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      padding: 12px 12px 4px;
    }

    .summary-card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 10px 8px;
      box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
    }

    .summary-label {
      color: var(--muted);
      font-size: 11px;
      font-weight: 1000;
    }

    .summary-num {
      margin-top: 2px;
      color: var(--text);
      font-size: 24px;
      line-height: 1;
      font-weight: 1000;
    }

    .filters {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding: 8px 12px;
      scrollbar-width: none;
    }

    .filters::-webkit-scrollbar {
      display: none;
    }

    .filter-btn {
      flex: 0 0 auto;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--text);
      height: 34px;
      padding: 0 13px;
      font-size: 13px;
      font-weight: 1000;
    }

    .filter-btn.active {
      background: var(--blue);
      color: #fff;
      border-color: var(--blue);
    }

    .search-box {
      padding: 4px 12px 8px;
    }

    .search-box input {
      width: 100%;
      height: 38px;
      border: 1px solid var(--line);
      border-radius: 13px;
      padding: 0 12px;
      font-size: 14px;
      font-weight: 800;
      outline: none;
    }

    .section-title {
      padding: 6px 14px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 1000;
    }

    .list {
      padding: 0 12px 14px;
      display: grid;
      gap: 10px;
    }

    .case-card {
      border: 1px solid var(--line);
      background: var(--card);
      border-radius: 18px;
      padding: 12px;
      box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
    }

    .case-card.important {
      border-color: #f59e0b;
      background: #fffaf0;
    }

    .case-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 8px;
    }

    .building {
      font-size: 18px;
      font-weight: 1000;
      color: var(--text);
      line-height: 1.25;
    }

    .meta {
      margin-top: 2px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
      line-height: 1.35;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 9px;
      border-radius: 999px;
      background: #eaf2ff;
      color: #1d4ed8;
      font-size: 12px;
      font-weight: 1000;
      white-space: nowrap;
    }

    .pill.green {
      background: #dcfce7;
      color: #166534;
    }

    .pill.orange {
      background: #ffedd5;
      color: #9a3412;
    }

    .pill.purple {
      background: #ede9fe;
      color: #6d28d9;
    }

    .pill.red {
      background: #fee2e2;
      color: #b91c1c;
    }

    .info-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-top: 10px;
    }

    .info {
      background: #f8fafc;
      border-radius: 12px;
      padding: 8px;
    }

    .info-label {
      color: var(--muted);
      font-size: 11px;
      font-weight: 1000;
    }

    .info-value {
      margin-top: 2px;
      color: var(--text);
      font-size: 13px;
      font-weight: 1000;
      line-height: 1.35;
    }

    .note {
      margin-top: 9px;
      padding: 9px;
      border-radius: 12px;
      background: #f8fafc;
      color: #334155;
      font-size: 13px;
      font-weight: 850;
      line-height: 1.45;
      white-space: pre-wrap;
    }

    .empty {
      margin: 12px;
      padding: 18px;
      text-align: center;
      color: var(--muted);
      background: #fff;
      border: 1px dashed var(--line);
      border-radius: 16px;
      font-size: 14px;
      font-weight: 1000;
    }

    .bottom-nav {
      position: fixed;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 30;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      padding: 10px 12px 14px;
      background: rgba(238, 243, 249, 0.94);
      backdrop-filter: blur(10px);
      border-top: 1px solid var(--line);
    }

    .bottom-nav button {
      height: 42px;
      border: 0;
      border-radius: 14px;
      background: #fff;
      color: var(--text);
      font-size: 13px;
      font-weight: 1000;
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    }

    .bottom-nav button.primary {
      background: var(--green);
      color: #fff;
    }

    .modal-mask {
      position: fixed;
      inset: 0;
      z-index: 60;
      display: none;
      align-items: flex-end;
      background: rgba(15, 23, 42, 0.45);
    }

    .modal-mask.show {
      display: flex;
    }

    .modal {
      width: 100%;
      max-height: 86vh;
      overflow-y: auto;
      background: #fff;
      border-top-left-radius: 24px;
      border-top-right-radius: 24px;
      padding: 16px;
      box-shadow: 0 -16px 44px rgba(15, 23, 42, 0.24);
    }

    .modal-title {
      font-size: 22px;
      font-weight: 1000;
      color: var(--text);
      margin-bottom: 6px;
    }

    .modal-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-top: 14px;
    }

    .modal-actions button {
      height: 42px;
      border: 0;
      border-radius: 14px;
      font-size: 14px;
      font-weight: 1000;
    }

    .modal-actions .close {
      background: #64748b;
      color: #fff;
    }

    .modal-actions .call {
      background: var(--green);
      color: #fff;
    }

    @media (min-width: 760px) {
      .app {
        max-width: 520px;
        margin: 0 auto;
        border-left: 1px solid var(--line);
        border-right: 1px solid var(--line);
        background: var(--bg);
      }

      .bottom-nav {
        max-width: 520px;
        margin: 0 auto;
      }
    }
  </style>

<style id="sales_mobile_logout_button_v1">
  .logout-btn {
    background: rgba(220, 38, 38, 0.82) !important;
    color: #fff !important;
  }
</style>




<style id="sales_bottom_nav_employee_settings_v2">
  .bottom-nav {
    position: fixed !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    z-index: 40 !important;
    display: grid !important;
    grid-template-columns: repeat(4, 1fr) !important;
    gap: 8px !important;
    padding: 10px 10px calc(10px + env(safe-area-inset-bottom)) !important;
    background: rgba(238, 243, 249, .94) !important;
    backdrop-filter: blur(12px) !important;
    border-top: 1px solid #d7e1ef !important;
    max-width: 520px !important;
    margin: 0 auto !important;
  }

  .bottom-nav button {
    height: 54px !important;
    border: 0 !important;
    border-radius: 18px !important;
    background: #fff !important;
    color: #102348 !important;
    font-size: 15px !important;
    font-weight: 1000 !important;
    box-shadow: 0 8px 20px rgba(15,23,42,.08) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
    padding: 0 4px !important;
  }

  .bottom-nav button.danger {
    background: #dc2626 !important;
    color: #fff !important;
  }
</style>




  <link rel="stylesheet" href="/static/app_header_unified.css?v=20260508_final">
</head>

<body>
  <div class="app">
    <section class="hero app-standard-hero">
      <div class="hero-main">
        <span class="hero-logo">
          <img class="hero-logo-img" src="/static/shinnan_home_logo.png" alt="Logo">
        </span>
        <h1 class="hero-title">\u8a0a\u5357\u696d\u52d9\u7cfb\u7d71</h1>
      </div>
      <div id="sales_employee_name" class="hero-sub">\u767b\u5165\u8005</div>
    </section>

    <section class="summary">
      <div class="summary-card" onclick="setFilter('今日')">
        <div class="summary-label">今日</div>
        <div id="sum_today" class="summary-num">0</div>
      </div>

      <div class="summary-card" onclick="setFilter('重要')">
        <div class="summary-label">重要</div>
        <div id="sum_important" class="summary-num">0</div>
      </div>

      <div class="summary-card" onclick="setFilter('事件')">
        <div class="summary-label">事件</div>
        <div id="sum_event" class="summary-num">0</div>
      </div>
    </section>

    <nav class="filters">
      <button class="filter-btn active" data-filter="全部" onclick="setFilter('全部')">全部</button>
      <button class="filter-btn" data-filter="今日" onclick="setFilter('今日')">今日</button>
      <button class="filter-btn" data-filter="重要" onclick="setFilter('重要')">重要</button>
      <button class="filter-btn" data-filter="待拜訪" onclick="setFilter('待拜訪')">待拜訪</button>
      <button class="filter-btn" data-filter="合約" onclick="setFilter('合約')">合約</button>
      <button class="filter-btn" data-filter="事件" onclick="setFilter('事件')">事件</button>
    </nav>

    <div class="search-box">
      <input id="keyword" placeholder="搜尋大樓、總幹事、電話、負責業務" oninput="renderList()">
    </div>

    <div id="section_title" class="section-title">全部業務工作</div>
    <main id="list" class="list"></main>

    <div class="bottom-nav">
      <button type="button" onclick="location.href='/app'">APP首頁</button>
      <button type="button" onclick="location.href='/admin/buildings?from=sales_app&ts=' + Date.now()">大樓名錄</button>
      <button type="button" onclick="reloadData()">整理</button>
      <button type="button" class="danger" onclick="location.href='/employee/logout?next=/'">登出</button>
    </div>
  </div>

  <div id="detail_mask" class="modal-mask" onclick="closeDetail(event)">
    <div class="modal" onclick="event.stopPropagation()">
      <div id="detail_title" class="modal-title"></div>
      <div id="detail_body"></div>

      <div class="modal-actions">
        <button class="close" onclick="hideDetail()">關閉</button>
        <button id="call_button" class="call">撥打總幹事</button>
      </div>
    </div>
  </div>

  <script>
    let records = [];
    let currentFilter = "全部";

    function todayText() {
      const d = new Date();
      return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    }

    function esc(v) {
      return String(v ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function isEventActive(item) {
      return item.event_type && item.event_type !== "無" && ["待處理", "處理中", "已回覆"].includes(item.event_status || "");
    }

    function isToday(item) {
      const t = todayText();
      return item.next_visit === t || item.event_schedule_date === t;
    }

    function isContract(item) {
      return item.contract_status === "即將到期" || item.contract_status === "洽談中";
    }

    function buildActionText(item) {
      const parts = [];

      if (item.event_type && item.event_type !== "無") parts.push(item.event_type);
      if (item.event_status && item.event_status !== "無") parts.push(item.event_status);
      if (item.business_type) parts.push(item.business_type);
      if (isContract(item)) parts.push("合約追蹤");
      if (item.feedback_type && item.feedback_type !== "無") parts.push(item.feedback_type);

      return parts.join("｜") || "拜訪管理室";
    }

    function statusPill(item) {
      if (item.important_schedule) return '<span class="pill orange">重要</span>';
      if (isToday(item)) return '<span class="pill green">今日</span>';
      if (isContract(item)) return '<span class="pill purple">合約</span>';
      if (isEventActive(item)) return '<span class="pill red">事件</span>';
      return '<span class="pill">追蹤</span>';
    }

    function setFilter(filter) {
      currentFilter = filter;

      document.querySelectorAll(".filter-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.filter === filter);
      });

      renderList();
    }

    function filterRecords() {
      const keyword = document.getElementById("keyword").value.trim().toLowerCase();

      return records.filter(item => {
        if (currentFilter === "今日" && !isToday(item)) return false;
        if (currentFilter === "重要" && !item.important_schedule) return false;
        if (currentFilter === "待拜訪" && !item.next_visit) return false;
        if (currentFilter === "合約" && !isContract(item)) return false;
        if (currentFilter === "事件" && !isEventActive(item)) return false;

        if (keyword) {
          const hay = [
            item.building_name,
            item.area,
            item.manager_name,
            item.manager_phone,
            item.owner,
            item.business_type,
            item.status,
            item.event_type,
            item.event_status,
            item.contract_status
          ].join(" ").toLowerCase();

          if (!hay.includes(keyword)) return false;
        }

        return true;
      });
    }

    function renderSummary() {
      document.getElementById("sum_today").textContent = records.filter(isToday).length;
      document.getElementById("sum_important").textContent = records.filter(x => x.important_schedule).length;
      document.getElementById("sum_event").textContent = records.filter(isEventActive).length;
    }

    function renderList() {
      renderSummary();

      const rows = filterRecords();
      const box = document.getElementById("list");
      const title = document.getElementById("section_title");

      title.textContent = currentFilter + "業務工作｜" + rows.length + " 筆";

      if (!rows.length) {
        box.innerHTML = '<div class="empty">目前沒有符合條件的業務工作。</div>';
        return;
      }

      box.innerHTML = rows.map((item, index) => {
        const realIndex = records.indexOf(item);

        return `
          <article class="case-card ${item.important_schedule ? "important" : ""}" onclick="showDetail(${realIndex})">
            <div class="case-head">
              <div>
                <div class="building">${esc(item.building_name || "-")}</div>
                <div class="meta">${esc(item.area || "-")}｜負責：${esc(item.owner || "-")}</div>
              </div>
              ${statusPill(item)}
            </div>

            <div class="info-grid">
              <div class="info">
                <div class="info-label">總幹事</div>
                <div class="info-value">${esc(item.manager_name || "-")}<br>${esc(item.manager_phone || "-")}</div>
              </div>

              <div class="info">
                <div class="info-label">下次拜訪</div>
                <div class="info-value">${esc(item.next_visit || "-")}</div>
              </div>

              <div class="info">
                <div class="info-label">狀態</div>
                <div class="info-value">${esc(item.status || "-")}｜${esc(item.contract_status || "-")}</div>
              </div>

              <div class="info">
                <div class="info-label">業務行為</div>
                <div class="info-value">${esc(buildActionText(item))}</div>
              </div>
            </div>

            <div class="note">${esc(item.business_note || "無備註")}</div>
          </article>
        `;
      }).join("");
    }

    function showDetail(index) {
      const item = records[index];
      if (!item) return;

      document.getElementById("detail_title").textContent = item.building_name || "業務資料";

      document.getElementById("detail_body").innerHTML = `
        <div class="info-grid">
          <div class="info">
            <div class="info-label">大樓</div>
            <div class="info-value">${esc(item.building_name || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">區域</div>
            <div class="info-value">${esc(item.area || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">管理公司</div>
            <div class="info-value">${esc(item.management_company || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">管理室電話</div>
            <div class="info-value">${esc(item.management_phone || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">總幹事</div>
            <div class="info-value">${esc(item.manager_name || "-")}<br>${esc(item.manager_phone || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">負責業務</div>
            <div class="info-value">${esc(item.owner || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">業務類型</div>
            <div class="info-value">${esc(item.business_type || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">目前狀態</div>
            <div class="info-value">${esc(item.status || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">合約</div>
            <div class="info-value">${esc(item.contract_status || "-")}<br>${esc(item.contract_end_date || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">事件</div>
            <div class="info-value">${esc(item.event_type || "-")}<br>${esc(item.event_status || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">委員會</div>
            <div class="info-value">${esc(item.committee_time || "-")}</div>
          </div>

          <div class="info">
            <div class="info-label">住戶大會</div>
            <div class="info-value">${esc(item.resident_meeting_time || "-")}</div>
          </div>
        </div>

        <div class="note">${esc(item.business_note || "無備註")}</div>
      `;

      const callBtn = document.getElementById("call_button");
      const phone = item.manager_phone || item.management_phone || "";

      callBtn.onclick = function () {
        if (!phone) {
          alert("沒有可撥打電話");
          return;
        }

        location.href = "tel:" + phone;
      };

      document.getElementById("detail_mask").classList.add("show");
    }

    function hideDetail() {
      document.getElementById("detail_mask").classList.remove("show");
    }

    function closeDetail(event) {
      if (event.target.id === "detail_mask") hideDetail();
    }

    async function reloadData() {
      const box = document.getElementById("list");
      box.innerHTML = '<div class="empty">資料載入中...</div>';

      const res = await fetch("/api/app/sales/business-records?ts=" + Date.now(), {
        cache: "no-store"
      });

      if (!res.ok) {
        box.innerHTML = '<div class="empty">業務 API 讀取失敗：' + res.status + '</div>';
        return;
      }

      records = await res.json();

      records.sort((a, b) => {
        const ai = a.important_schedule ? 0 : 1;
        const bi = b.important_schedule ? 0 : 1;
        if (ai !== bi) return ai - bi;

        const ad = a.next_visit || a.event_schedule_date || "9999-12-31";
        const bd = b.next_visit || b.event_schedule_date || "9999-12-31";

        return String(ad).localeCompare(String(bd));
      });

      renderList();
    }

    reloadData();
  </script>

<script id="sales_header_exact_user_v2">
(function () {
  async function setSalesEmployeeNameFromSession() {
    var box = document.getElementById("sales_employee_name");
    if (!box) return;

    box.textContent = "登入者讀取中...";

    try {
      var res = await fetch("/api/app/employee/profile?ts=" + Date.now(), {
        cache: "no-store",
        credentials: "same-origin"
      });

      if (!res.ok) {
        box.textContent = "登入者";
        return;
      }

      var data = await res.json();
      var profile = data.profile || data.user || data || {};

      var name =
        profile.display_name ||
        profile.name ||
        profile.staff_name ||
        profile.staff_code ||
        "";

      box.textContent = name || "\\u767b\\u5165\\u8005";

    } catch (err) {
      box.textContent = "登入者";
    }
  }

  window.setSalesEmployeeNameFromSession = setSalesEmployeeNameFromSession;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setSalesEmployeeNameFromSession);
  } else {
    setSalesEmployeeNameFromSession();
  }

  window.addEventListener("load", setSalesEmployeeNameFromSession);
  setTimeout(setSalesEmployeeNameFromSession, 300);
  setTimeout(setSalesEmployeeNameFromSession, 1200);
})();
</script>


<script>
(function(){
  function fixSalesUserLabel(){
    var el = document.getElementById("sales_employee_name");
    if (!el) return;
    var t = (el.textContent || "").trim();
    if (t.indexOf("\uff5c") >= 0) t = t.split("\uff5c")[0].trim();
    if (t.indexOf("|") >= 0) t = t.split("|")[0].trim();
    el.textContent = t;
  }
  fixSalesUserLabel();
  setTimeout(fixSalesUserLabel, 100);
  setTimeout(fixSalesUserLabel, 500);
})();
</script>

</body>
</html>
"""
# SHINNAN_SALES_MOBILE_APP_END



# SHINNAN_EMPLOYEE_CURRENT_USER_HELPER_START

@router.get("/api/app/sales/business-records", summary="手機 APP 讀取個人業務工作資料")
def api_app_sales_business_records(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    admin_response = api_admin_sales_business_records()
    raw = admin_response.body.decode("utf-8")
    rows = _managers_json.loads(raw)

    if user.get("role") != "admin":
        owner_name = user.get("display_name") or ""
        rows = [item for item in rows if item.get("owner") == owner_name]

    return _ManagersResponse(
        content=_managers_json.dumps(rows, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


# SHINNAN_SALES_MOBILE_NEW_CASE_START
@router.get("/app/sales/new", response_class=HTMLResponse)
def sales_mobile_new_case_page(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmpRedirectResponse("/employee/login?next=/app/sales/new", status_code=303)

    employee_display_name = str(user.get("display_name", ""))

    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

  <title>新增業務案件｜訊南 ERP</title>

  <style>
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: #eef3f9;
      color: #102348;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .top {
      padding: 18px 16px;
      background: linear-gradient(135deg, #0f766e, #2563eb, #7c3aed);
      color: #fff;
      border-bottom-left-radius: 22px;
      border-bottom-right-radius: 22px;
    }

    h1 {
      margin: 0;
      font-size: 26px;
      font-weight: 1000;
    }

    .sub {
      margin-top: 4px;
      font-size: 14px;
      font-weight: 900;
      opacity: .9;
    }

    form {
      padding: 14px;
    }

    .card {
      background: #fff;
      border: 1px solid #d7e1ef;
      border-radius: 18px;
      padding: 14px;
      box-shadow: 0 8px 22px rgba(15,23,42,.06);
    }

    label {
      display: block;
      margin: 12px 0 6px;
      color: #334155;
      font-size: 14px;
      font-weight: 1000;
    }

    input,
    select,
    textarea {
      width: 100%;
      border: 1px solid #cbd5e1;
      border-radius: 13px;
      padding: 0 12px;
      color: #102348;
      font-size: 16px;
      font-weight: 900;
      outline: none;
      background: #fff;
    }

    input,
    select {
      height: 44px;
    }

    textarea {
      min-height: 110px;
      padding-top: 10px;
      line-height: 1.5;
      resize: vertical;
    }


    .building-picker-row {
      display: grid;
      grid-template-columns: 1fr 96px;
      gap: 8px;
      align-items: center;
    }

    .pick-building-btn {
      height: 44px;
      border: 0;
      border-radius: 13px;
      background: #365ee8;
      color: #fff;
      font-size: 15px;
      font-weight: 1000;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
    }

    .building-hint {
      margin-top: 6px;
      color: #64748b;
      font-size: 12px;
      font-weight: 900;
      line-height: 1.5;
    }

    .check-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 12px;
      font-size: 15px;
      font-weight: 1000;
    }

    .check-row input {
      width: 22px;
      height: 22px;
    }

    .actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-top: 16px;
    }

    button {
      height: 46px;
      border: 0;
      border-radius: 14px;
      font-size: 16px;
      font-weight: 1000;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
    }

    .gray {
      background: #64748b;
      color: #fff;
    }

    .green {
      background: #16a34a;
      color: #fff;
    }

    .msg {
      margin: 14px;
      padding: 12px;
      border-radius: 14px;
      display: none;
      font-size: 15px;
      font-weight: 1000;
    }

    .msg.ok {
      display: block;
      background: #dcfce7;
      color: #166534;
    }

    .msg.err {
      display: block;
      background: #fee2e2;
      color: #991b1b;
    }
  </style>
</head>

<body>
  <section class="top">
    <h1>新增業務案件</h1>
    <div class="sub">登入者：__EMPLOYEE_DISPLAY_NAME__｜案件會自動歸屬此帳號</div>
  </section>

  <div id="msg" class="msg"></div>

  <form id="case_form">
    <div class="card">
      
<label>大樓名稱</label>
      <input type="hidden" name="building_no" id="building_no">
      <div class="building-picker-row">
        <input name="building_name" id="building_name" placeholder="可輸入新大樓，或按選擇帶入既有大樓" required>
        <button type="button" id="pick_building_btn" class="pick-building-btn" onclick="location.href='/admin/buildings?pick=sales_new&ts=' + Date.now()">選擇</button>
      </div>
      <div class="building-hint">既有大樓可由名錄選擇；新大樓可直接輸入名稱，建立案件時會自動建立大樓主資料。</div>


      <label>業務類型</label>
      <select name="business_type">
        <option value="新大樓開發">新大樓開發</option>
        <option value="舊大樓拜訪">舊大樓拜訪</option>
        <option value="合約續約">合約續約</option>
        <option value="管理室拜訪">管理室拜訪</option>
        <option value="業務事件">業務事件</option>
        <option value="回饋處理">回饋處理</option>
      </select>

      <label>目前狀態</label>
      <select name="status">
        <option value="待拜訪">待拜訪</option>
        <option value="已接觸">已接觸</option>
        <option value="已拜訪">已拜訪</option>
        <option value="等管委會">等管委會</option>
        <option value="談約中">談約中</option>
      </select>

      <label>合約狀態</label>
      <select name="contract_status">
        <option value="洽談中">洽談中</option>
        <option value="即將到期">即將到期</option>
        <option value="已簽">已簽</option>
        <option value="無">無</option>
      </select>

      <label>事件類型</label>
      <select name="event_type">
        <option value="無">無</option>
        <option value="管理室要求">管理室要求</option>
        <option value="管委會要求">管委會要求</option>
        <option value="住戶反應">住戶反應</option>
        <option value="合約問題">合約問題</option>
      </select>

      <label>事件狀態</label>
      <select name="event_status">
        <option value="無">無</option>
        <option value="待處理">待處理</option>
        <option value="處理中">處理中</option>
        <option value="已回覆">已回覆</option>
      </select>

      <label>下次拜訪日期</label>
      <input name="next_visit" type="date">

      <label>事件日期</label>
      <input name="event_schedule_date" type="date">

      <div class="check-row">
        <input name="important_schedule" type="checkbox" value="1">
        <span>重要行程，顯示在最上方</span>
      </div>

      <label>備註</label>
      <textarea name="business_note" placeholder="例如：管理室要求重談合約，需帶合約資料與回饋方案。"></textarea>

      <div class="actions">
        <button type="button" class="gray" onclick="location.href='/app/sales?ts=' + Date.now()">取消</button>
        <button type="submit" class="green">建立案件</button>
      </div>
    </div>
  </form>

  <script>
    function showMsg(type, text) {
      const box = document.getElementById("msg");
      box.className = "msg " + type;
      box.textContent = text;
    }

    async function loadBuildings() {
      const sel = document.getElementById("building_select");
      const res = await fetch("/api/admin/buildings?ts=" + Date.now(), {cache: "no-store"});

      if (!res.ok) {
        sel.innerHTML = '<option value="">大樓讀取失敗</option>';
        return;
      }

      const rows = await res.json();

      sel.innerHTML = '<option value="">請選擇大樓</option>' + rows.map(function (b) {
        return '<option value="' + b.building_no + '">' + b.building_no + '｜' + b.name + '｜' + b.area + '</option>';
      }).join("");
    }

    document.getElementById("case_form").addEventListener("submit", async function (event) {
      event.preventDefault();

      const form = new FormData(event.target);
      const res = await fetch("/api/app/sales/business-records/create", {
        method: "POST",
        body: new URLSearchParams(form),
      });

      const data = await res.json();

      if (!res.ok || !data.ok) {
        showMsg("err", data.error || "建立失敗");
        return;
      }

      showMsg("ok", "案件已建立");
      setTimeout(function () {
        location.href = "/app/sales?ts=" + Date.now();
      }, 700);
    });

    loadPickedBuildingFromUrl();
  </script>

  <script id="sales_new_picker_button_fix_v1">
    document.addEventListener("DOMContentLoaded", function () {
      const btn = document.getElementById("pick_building_btn");
      if (!btn) return;

      btn.addEventListener("click", function () {
        location.href = "/admin/buildings?pick=sales_new&ts=" + Date.now();
      });
    });
  </script>

</body>
</html>
""".replace("__EMPLOYEE_DISPLAY_NAME__", employee_display_name)


@router.post("/api/app/sales/business-records/create")
async def api_app_sales_business_records_create(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "login required"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=401,
        )

    raw = (await request.body()).decode("utf-8")
    form = _emp_parse_qs(raw)

    def value(name, default=""):
        return (form.get(name, [default])[0] or default).strip()

    building_no = value("building_no")
    building_name = value("building_name")

    if not building_no and not building_name:
        return _ManagersResponse(
            content=_managers_json.dumps({"ok": False, "error": "請輸入或選擇大樓名稱"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    owner = user.get("display_name") or user.get("staff_code") or ""

    business_type = value("business_type", "舊大樓拜訪")
    status = value("status", "待拜訪")
    contract_status = value("contract_status", "洽談中")
    event_type = value("event_type", "無")
    event_status = value("event_status", "無")
    next_visit = value("next_visit", "")
    event_schedule_date = value("event_schedule_date", "")
    important_schedule = 1 if value("important_schedule", "") == "1" else 0
    business_note = value("business_note", "")

    if not business_note:
        business_note = (
            "業務工作：" + business_type + "\n"
            "負責業務：" + owner + "\n"
            "內容：手機 APP 新增案件。"
        )

    _sales_business_records_init()

    with _sales_engine.begin() as conn:
        # 若是從大樓名錄選擇，會有 building_no。
        # 若是業務直接輸入新大樓名稱，則自動建立大樓主資料。
        if building_no:
            building = conn.execute(
                _sales_sql_text("""
                    SELECT building_no
                    FROM buildings
                    WHERE building_no = :building_no
                    LIMIT 1
                """),
                {"building_no": building_no},
            ).mappings().first()

            if not building:
                return _ManagersResponse(
                    content=_managers_json.dumps({"ok": False, "error": "找不到大樓資料"}, ensure_ascii=False),
                    media_type="application/json; charset=utf-8",
                    status_code=404,
                )
        else:
            existing = conn.execute(
                _sales_sql_text("""
                    SELECT building_no
                    FROM buildings
                    WHERE name = :name
                    LIMIT 1
                """),
                {"name": building_name},
            ).mappings().first()

            if existing:
                building_no = existing["building_no"]
            else:
                next_no = conn.execute(
                    _sales_sql_text("""
                        SELECT COUNT(*)
                        FROM buildings
                        WHERE building_no LIKE 'N%'
                    """)
                ).scalar()

                building_no = "N" + str(int(next_no or 0) + 1).zfill(3)

                table_cols = [
                    row[1]
                    for row in conn.execute(_sales_sql_text("PRAGMA table_info(buildings)")).fetchall()
                ]

                new_building_data = {
                    "building_no": building_no,
                    "name": building_name,
                    "area": "未分區",
                    "address": "",
                    "management_company": "",
                    "management_phone": "",
                    "manager_name": "",
                    "manager_phone": "",
                    "manager_age": "",
                    "manager_experience": "",
                    "manager_interest": "",
                    "visit_time": "",
                    "committee_time": "",
                    "resident_meeting_time": "",
                    "active_users": 0,
                    "total_households": 0,
                    "ip": "",
                    "host": "",
                    "note": "手機業務 APP 新增案件時建立。",
                    "created_at": _emp_datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": _emp_datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                insert_cols = [col for col in new_building_data.keys() if col in table_cols]
                col_sql = ", ".join(insert_cols)
                val_sql = ", ".join([":" + col for col in insert_cols])

                conn.execute(
                    _sales_sql_text(
                        "INSERT INTO buildings (" + col_sql + ") VALUES (" + val_sql + ")"
                    ),
                    {col: new_building_data[col] for col in insert_cols},
                )

        conn.execute(
            _sales_sql_text("""
                INSERT INTO sales_business_records (
                    building_no,
                    business_type,
                    status,
                    contract_status,
                    contract_end_date,
                    feedback_type,
                    feedback_status,
                    event_type,
                    event_status,
                    event_schedule_date,
                    important_schedule,
                    next_visit,
                    owner,
                    business_note,
                    demo_type,
                    created_at,
                    updated_at
                )
                VALUES (
                    :building_no,
                    :business_type,
                    :status,
                    :contract_status,
                    '',
                    '無',
                    '無',
                    :event_type,
                    :event_status,
                    :event_schedule_date,
                    :important_schedule,
                    :next_visit,
                    :owner,
                    :business_note,
                    'mobile_app_created',
                    datetime('now'),
                    datetime('now')
                )
            """),
            {
                "building_no": building_no,
                "business_type": business_type,
                "status": status,
                "contract_status": contract_status,
                "event_type": event_type,
                "event_status": event_status,
                "event_schedule_date": event_schedule_date,
                "important_schedule": important_schedule,
                "next_visit": next_visit,
                "owner": owner,
                "business_note": business_note,
            },
        )

        new_id = conn.execute(_sales_sql_text("SELECT last_insert_rowid()")).scalar()

    return _ManagersResponse(
        content=_managers_json.dumps({"ok": True, "id": new_id}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )
# SHINNAN_SALES_MOBILE_NEW_CASE_END


# SHINNAN_EMPLOYEE_LOGIN_ROUTES_END


