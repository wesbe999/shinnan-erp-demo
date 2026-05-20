from __future__ import annotations

import json
from html import escape as _eng_escape

from fastapi import APIRouter
from fastapi import Request as _EmpRequest
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse as _EmpRedirectResponse
from sqlalchemy import text as _sql_text

from app.routes.employee_auth import _employee_current_user_from_request
from app.db import engine


router = APIRouter(tags=["工程系統 APP"])


_ENGINEERING_CASES = [{'id': 'ENG-FLOW-001', 'building': '東方紐約', 'project': '大樓網路建設', 'stage': 'initial_survey', 'owner_unit': '各區負責工務', 'owner_name': '北區工務', 'planned_date': '2026-05-03', 'startDate': '2026-05-03', 'endDate': '2026-06-15', 'amount': '', 'note': '初步了解社區需求、工程範圍、設備數量與樓層限制。'}, {'id': 'ENG-FLOW-002', 'building': '仁義新城', 'project': '攝影機增設', 'stage': 'business_review', 'owner_unit': '業務(公司)', 'owner_name': '業務部', 'planned_date': '2026-05-06', 'startDate': '2026-05-20', 'endDate': '2026-05-24', 'amount': '', 'note': '需評估合作條件與投資性，確認是否進入細勘。'}, {'id': 'ENG-FLOW-003', 'building': '北安御品', 'project': '網路與監視器整合', 'stage': 'detailed_survey', 'owner_unit': '維修、工程部', 'owner_name': '工程部', 'planned_date': '2026-05-08', 'startDate': '2026-05-10', 'endDate': '2026-05-18', 'amount': '', 'note': '勘驗場地、規劃線路與機器數量，訂定開工與完工時間。'}, {'id': 'ENG-FLOW-004', 'building': '永華麗景', 'project': '管道與機房改善', 'stage': 'outsourced_survey', 'owner_unit': '外包', 'owner_name': '外包廠商', 'planned_date': '2026-05-10', 'startDate': '2026-05-12', 'endDate': '2026-06-05', 'amount': '', 'note': '評估施工可能性並產出線路圖。'}, {'id': 'ENG-FLOW-005', 'building': '成功國宅', 'project': '網路設備更換', 'stage': 'quotation', 'owner_unit': '業務(公司)', 'owner_name': '業務部', 'planned_date': '2026-05-12', 'startDate': '2026-06-01', 'endDate': '2026-06-04', 'amount': '120000', 'note': '準備報價單、施工公告與完工公告。'}, {'id': 'ENG-FLOW-006', 'building': '小北世家', 'project': '停車場攝影機補點', 'stage': 'construction', 'owner_unit': '維修、工程、專案部', 'owner_name': '工程部', 'planned_date': '2026-05-14', 'startDate': '2026-06-10', 'endDate': '2026-06-13', 'amount': '', 'note': '施工中，需記錄材料領用、施工照片與日報。'}, {'id': 'ENG-FLOW-007', 'building': '嘉樂首府', 'project': '光纖主幹改善', 'stage': 'acceptance', 'owner_unit': '維修、工程、專案部', 'owner_name': '專案部', 'planned_date': '2026-05-16', 'startDate': '2026-05-02', 'endDate': '2026-05-12', 'amount': '', 'note': '需與當區工程師與社區共同驗收。'}, {'id': 'ENG-FLOW-008', 'building': '勝利雅築', 'project': '社區弱電箱整理', 'stage': 'billing', 'owner_unit': '業務(公司)', 'owner_name': '業務部', 'planned_date': '2026-05-20', 'startDate': '2026-04-20', 'endDate': '2026-05-01', 'amount': '85000', 'note': '確認請款是否入帳，以及合作條件是否實施。'}, {'id': 'ENG-FLOW-009', 'building': '安平國宅', 'project': '電梯口攝影機施工', 'stage': 'construction', 'owner_unit': '維修、工程、專案部', 'owner_name': '維修部', 'planned_date': '2026-05-22', 'startDate': '2026-05-05', 'endDate': '2026-05-28', 'amount': '', 'note': '施工跨月底，需持續追蹤進度。'}, {'id': 'ENG-FLOW-010', 'building': '中正名門', 'project': '機房設備移機', 'stage': 'closed', 'owner_unit': '業務(公司)', 'owner_name': '業務部', 'planned_date': '2026-05-25', 'startDate': '2026-04-20', 'endDate': '2026-04-30', 'amount': '60000', 'note': '已完成請款並結案。'}]
_ENGINEERING_STAGES = [{'key': 'initial_survey', 'label': '初勘', 'unit': '各區負責工務'}, {'key': 'business_review', 'label': '業務評估', 'unit': '業務(公司)'}, {'key': 'detailed_survey', 'label': '細勘', 'unit': '維修、工程部'}, {'key': 'outsourced_survey', 'label': '外包細勘', 'unit': '外包'}, {'key': 'quotation', 'label': '報價', 'unit': '業務(公司)'}, {'key': 'construction', 'label': '施工', 'unit': '維修、工程、專案部'}, {'key': 'acceptance', 'label': '完工驗收', 'unit': '維修、工程、專案部'}, {'key': 'billing', 'label': '請款', 'unit': '業務(公司)'}, {'key': 'closed', 'label': '已結案', 'unit': '業務(公司)'}, {'key': 'ended', 'label': '已終止', 'unit': '業務(公司)'}]



# CL15L7B_ENGINEERING_TRANSFER_TICKET_LOADER_START
def _eng_safe_text(value) -> str:
    return str(value or "").strip()


def _eng_ticket_stage(status: str) -> str:
    value = _eng_safe_text(status)

    if value in {"\u5df2\u5b8c\u5de5", "\u5df2\u7d50\u6848"}:
        return "closed"

    if value in {"\u5df2\u9818\u53d6", "\u8655\u7406\u4e2d", "\u65bd\u5de5\u4e2d"}:
        return "construction"

    return "construction"


def _load_engineering_transfer_cases():
    dept = "\u5de5\u7a0b\u90e8"

    try:
        with engine.begin() as conn:
            exists = conn.execute(
                _sql_text("""
                    SELECT COUNT(*)
                    FROM sqlite_master
                    WHERE type = 'table'
                      AND name = 'tickets'
                """)
            ).scalar()

            if not int(exists or 0):
                return []

            rows = conn.execute(
                _sql_text("""
                    SELECT
                        t.id AS id,
                        t.ticket_no AS ticket_no,
                        t.case_type AS case_type,
                        t.status AS status,
                        t.customer_name AS customer_name,
                        t.contact_name AS contact_name,
                        t.service_address AS service_address,
                        t.appointment_date AS appointment_date,
                        t.appointment_time AS appointment_time,
                        t.dispatch_area AS dispatch_area,
                        t.description AS description,
                        t.transfer_note AS transfer_note,
                        t.transfer_origin_ticket_id AS transfer_origin_ticket_id,
                        t.transfer_source_department AS transfer_source_department,
                        t.transfer_target_department AS transfer_target_department,
                        t.transfer_status AS transfer_status,
                        t.created_at AS created_at,
                        b.name AS building_name
                    FROM tickets t
                    LEFT JOIN buildings b
                      ON b.building_no = t.building_no
                    WHERE (
                        COALESCE(t.dispatch_area, '') = :dept
                        OR COALESCE(t.transfer_target_department, '') = :dept
                    )
                      AND COALESCE(t.status, '') NOT IN (
                        '\u5df2\u53d6\u6d88',
                        '\u4f4f\u6236\u53d6\u6d88',
                        '\u9000\u56de'
                      )
                    ORDER BY t.id DESC
                    LIMIT 80
                """),
                {"dept": dept},
            ).mappings().fetchall()
    except Exception:
        return []

    items = []

    for row in rows:
        ticket_id = int(row.get("id") or 0)
        ticket_no = _eng_safe_text(row.get("ticket_no")) or ("T" + str(ticket_id))
        case_type = _eng_safe_text(row.get("case_type")) or "\u8f49\u6d3e\u6848\u4ef6"
        status = _eng_safe_text(row.get("status"))
        building = (
            _eng_safe_text(row.get("building_name"))
            or _eng_safe_text(row.get("customer_name"))
            or _eng_safe_text(row.get("service_address"))
            or "\u8f49\u6d3e\u6848\u4ef6"
        )

        source = _eng_safe_text(row.get("transfer_source_department"))
        note_parts = []

        if source:
            note_parts.append("\u4f86\u6e90\u55ae\u4f4d\uff1a" + source)

        if _eng_safe_text(row.get("transfer_note")):
            note_parts.append("\u8f49\u6d3e\u5099\u8a3b\uff1a" + _eng_safe_text(row.get("transfer_note")))

        if _eng_safe_text(row.get("description")):
            note_parts.append("\u6848\u4ef6\u8aaa\u660e\uff1a" + _eng_safe_text(row.get("description")))

        if _eng_safe_text(row.get("service_address")):
            note_parts.append("\u670d\u52d9\u5730\u5740\uff1a" + _eng_safe_text(row.get("service_address")))

        planned = _eng_safe_text(row.get("appointment_date")) or _eng_safe_text(row.get("created_at"))[:10]

        items.append({
            "id": "TICKET-" + str(ticket_id),
            "ticket_id": ticket_id,
            "ticket_no": ticket_no,
            "building": building,
            "project": "\u8f49\u6d3e\uff1a" + case_type,
            "stage": _eng_ticket_stage(status),
            "owner_unit": dept,
            "owner_name": dept,
            "planned_date": planned,
            "startDate": planned,
            "endDate": planned,
            "amount": "",
            "note": "\n".join(note_parts) if note_parts else "\u7531\u6d3e\u5de5\u7cfb\u7d71\u8f49\u6d3e\u81f3\u5de5\u7a0b\u90e8\u3002",
            "source": "tickets",
            "status": status,
            "transfer_status": _eng_safe_text(row.get("transfer_status")),
        })

    return items


def _load_engineering_cases():
    transfer_cases = _load_engineering_transfer_cases()
    return transfer_cases + list(_ENGINEERING_CASES)


# CL15L7B_ENGINEERING_TRANSFER_TICKET_LOADER_END


def _current_user_line(user: dict) -> str:
    return str(user.get("display_name", "") or user.get("staff_code", "") or "\u767b\u5165\u8005")


@router.get("/app/engineering", response_class=HTMLResponse)
def engineering_mobile_app_page(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmpRedirectResponse("/employee/login?next=/app/engineering", status_code=303)

    cases_json = json.dumps(_load_engineering_cases(), ensure_ascii=False)
    stages_json = json.dumps(_ENGINEERING_STAGES, ensure_ascii=False)

    html = """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

  <title>訊南工程系統｜訊南 ERP</title>

  <style>
    * { box-sizing: border-box; }

    html, body {
      margin: 0;
      min-height: 100%;
      background: #edf2f7;
      color: #102348;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft JhengHei", sans-serif;
    }

    body {
      display: flex;
      justify-content: center;
    }

    .app-shell {
      width: 100%;
      max-width: 430px;
      min-height: 100vh;
      background: #eef4fb;
      padding-bottom: 94px;
    }


    .title {
      margin: 0;
      padding: 0;
      transform: translateY(-2px);
      font-size: 28px;
      line-height: 1;
      font-weight: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      letter-spacing: 0.02em;
    }

    .title-logo,







    .content {
      padding: 14px 16px 22px;
    }

    .summary {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-bottom: 14px;
    }

    .summary-card {
      min-height: 74px;
      padding: 11px 10px;
      border-radius: 17px;
      border: 1px solid #d7e1ef;
      background: #fff;
      box-shadow: 0 10px 24px rgba(15,23,42,.08);
    }

    .summary-label {
      color: #64748b;
      font-size: 12px;
      font-weight: 1000;
    }

    .summary-value {
      margin-top: 7px;
      color: #102348;
      font-size: 25px;
      line-height: 1;
      font-weight: 1000;
    }

    .section-title {
      margin: 18px 4px 10px;
      color: #475569;
      font-size: 15px;
      font-weight: 1000;
    }

    .case-list {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
      padding: 2px 2px 12px;
    }

    .case-card {
      width: 100%;
      padding: 14px 15px;
      border: 1px solid #d7e1ef;
      border-radius: 20px;
      background: #fff;
      text-align: left;
      box-shadow: 0 10px 26px rgba(15, 23, 42, .08);
      cursor: pointer;
    }

    .case-card:active {
      transform: scale(.99);
    }

    .case-head {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: start;
    }

    .case-title {
      color: #102348;
      font-size: 19px;
      font-weight: 1000;
      line-height: 1.25;
    }

    .case-id {
      margin-top: 4px;
      color: #64748b;
      font-size: 14px;
      font-weight: 950;
      line-height: 1.25;
    }

    .stage-badge {
      min-width: 78px;
      min-height: 38px;
      padding: 8px 10px;
      border-radius: 999px;
      background: #e0e7ff;
      color: #3730a3;
      font-size: 13px;
      font-weight: 1000;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      white-space: nowrap;
      border: 2px solid transparent;
    }

    .stage-badge.selected-action {
      background: #fff1f2 !important;
      color: #be123c !important;
      border-color: #e11d48 !important;
      border-radius: 12px !important;
      box-shadow: 0 0 0 3px rgba(225, 29, 72, .10);
    }

    .stage-badge.initial_survey { background:#fef3c7; color:#92400e; }
    .stage-badge.business_review { background:#dbeafe; color:#1d4ed8; }
    .stage-badge.detailed_survey { background:#e0f2fe; color:#0369a1; }
    .stage-badge.outsourced_survey { background:#fae8ff; color:#86198f; }
    .stage-badge.quotation { background:#ffedd5; color:#c2410c; }
    .stage-badge.construction { background:#dcfce7; color:#166534; }
    .stage-badge.acceptance { background:#ede9fe; color:#5b21b6; }
    .stage-badge.billing { background:#ccfbf1; color:#0f766e; }
    .stage-badge.closed { background:#e2e8f0; color:#334155; }
    .stage-badge.ended { background:#fee2e2; color:#991b1b; }

    .case-meta {
      margin-top: 11px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 7px;
    }

    .meta-box {
      padding: 8px 9px;
      border-radius: 12px;
      background: #f8fafc;
      color: #334155;
      font-size: 12px;
      font-weight: 900;
      line-height: 1.35;
    }

    .meta-box strong {
      display: block;
      margin-top: 2px;
      color: #102348;
      font-size: 14px;
      font-weight: 1000;
    }

    .case-note {
      margin-top: 9px;
      padding: 9px 10px;
      border-radius: 12px;
      background: #f8fafc;
      color: #475569;
      font-size: 12px;
      font-weight: 900;
      line-height: 1.45;
      white-space: pre-wrap;
    }

    .detail-panel {
      display: none;
    }

    .detail-card {
      padding: 14px 15px;
      border: 1px solid #d7e1ef;
      border-radius: 20px;
      background: #fff;
      box-shadow: 0 10px 26px rgba(15, 23, 42, .08);
      margin-bottom: 12px;
    }

    .detail-title {
      color: #102348;
      font-size: 20px;
      font-weight: 1000;
      line-height: 1.25;
    }

    .detail-sub {
      margin-top: 5px;
      color: #64748b;
      font-size: 14px;
      font-weight: 950;
      line-height: 1.35;
    }

    .detail-box-grid {
      margin-top: 10px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .detail-box {
      padding: 10px 11px;
      border-radius: 14px;
      background: #f8fafc;
      color: #334155;
      font-size: 13px;
      font-weight: 1000;
      line-height: 1.35;
    }

    .detail-box strong {
      display: block;
      margin-top: 4px;
      color: #102348;
      font-size: 18px;
      font-weight: 1000;
    }

    .clickable-unit {
      cursor: pointer;
      border: 2px solid transparent;
    }

    .clickable-unit:active {
      transform: scale(.99);
      border-color: #4f63e8;
      background: #eef4ff;
    }

    .flow-line {
      margin-top: 12px;
      display: grid;
      grid-template-columns: 1fr;
      gap: 7px;
    }

    .flow-step {
      display: grid;
      grid-template-columns: 34px minmax(0,1fr) auto;
      gap: 8px;
      align-items: center;
      padding: 8px 10px;
      border-radius: 13px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      color: #334155;
      font-size: 13px;
      font-weight: 1000;
    }

    .flow-dot {
      width: 26px;
      height: 26px;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: #e2e8f0;
      color: #334155;
      font-size: 12px;
      font-weight: 1000;
    }

    .flow-step.done .flow-dot {
      background: #dcfce7;
      color: #166534;
    }

    .flow-step.current {
      border-color: #4f63e8;
      background: #eef4ff;
      color: #1e3a8a;
    }

    .flow-step.current .flow-dot {
      background: #4f63e8;
      color: #fff;
    }

    .flow-unit {
      color: #64748b;
      font-size: 11px;
      white-space: nowrap;
    }

    .action-area {
      margin-top: 12px;
      display: grid;
      grid-template-columns: 1fr;
      gap: 9px;
    }

    .action-btn {
      min-height: 48px;
      border: 0;
      border-radius: 15px;
      background: #4f63e8;
      color: #fff;
      font-size: 16px;
      font-weight: 1000;
      box-shadow: 0 8px 20px rgba(15,23,42,.12);
    }

    .action-btn.green { background:#16a34a; }
    .action-btn.orange { background:#f97316; }
    .action-btn.red { background:#cf3b2f; }
    .action-btn.yellow { background:#eab308; }

    .stage-form {
      margin-top: 12px;
      padding: 12px;
      border-radius: 18px;
      background: #fff;
      border: 1px solid #d7e1ef;
      box-shadow: 0 10px 26px rgba(15,23,42,.08);
    }

    .form-title {
      color: #102348;
      font-size: 17px;
      font-weight: 1000;
      margin-bottom: 8px;
    }

    .form-list {
      display: grid;
      grid-template-columns: 1fr;
      gap: 7px;
    }

    .form-item {
      padding: 9px 10px;
      border-radius: 12px;
      background: #f8fafc;
      color: #334155;
      font-size: 13px;
      font-weight: 900;
      line-height: 1.45;
    }

    .modal-mask {
      position: fixed;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 18px;
      background: rgba(15,23,42,.45);
      z-index: 80;
    }

    .modal {
      width: 100%;
      max-width: 360px;
      border-radius: 24px;
      background: #fff;
      border: 1px solid #d7e1ef;
      box-shadow: 0 24px 70px rgba(15,23,42,.28);
      padding: 18px;
    }

    .modal-title {
      color: #102348;
      font-size: 20px;
      font-weight: 1000;
      line-height: 1.3;
      margin-bottom: 12px;
    }

    .modal-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
    }

    .modal-grid button,
    .modal-cancel {
      height: 52px;
      border: 0;
      border-radius: 16px;
      background: #4f63e8;
      color: #fff;
      font-size: 18px;
      font-weight: 1000;
      box-shadow: 0 8px 20px rgba(15,23,42,.12);
    }

    .modal-cancel {
      margin-top: 12px;
      width: 100%;
      background: #f1f5f9;
      color: #334155;
      font-size: 16px;
    }

    .bottom-nav {
      position: fixed; left: 50%; bottom: 0; transform: translateX(-50%);
      width: 100%; max-width: 430px;
      display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 4px; padding: 8px 8px 12px;
      background: rgba(238,244,251,.96); border-top: 1px solid #d7e1ef;
      backdrop-filter: blur(10px); z-index: 20;
    }
    .bottom-nav button {
      height: 42px; min-width: 0; border: 2px solid #d4af37;
      border-radius: 12px; background: #fff; color: #102348;
      font-size: 12px; font-weight: 900; cursor: pointer;
    }
    .bottom-nav button.gold { background: transparent; border: 2px solid #d4af37; color: #d4af37; }
    .bottom-nav button.primary { background: #4f63e8; border-color: #d4af37; color: #fff; }
    .bottom-nav button.green { background: #16a34a; border-color: #d4af37; color: #fff; }
    .bottom-nav button.orange { background: #f97316; border-color: #d4af37; color: #fff; }
    .bottom-nav button.danger { background: #cf3b2f; border-color: #d4af37; color: #fff; }
  </style>
  <link rel="stylesheet" href="/static/app_header_unified.css?v=20260520_unified">
</head>

<body>
  <div class="app">
    <section class="hero app-standard-hero">
      <div class="hero-main">
        <span class="hero-logo">
          <img class="hero-logo-img" src="/static/shinnan_home_logo.png" alt="Logo">
        </span>
        <h1 class="hero-title">\u8a0a\u5357\u5de5\u7a0b\u7cfb\u7d71</h1>
      </div>
      <div class="hero-sub">__USER_LINE__</div>
    </section>

    <main class="content">
      <section id="home_panel">
        <section class="summary">
          <div class="summary-card">
            <div class="summary-label">進行中</div>
            <div id="summary_active" class="summary-value">-</div>
          </div>
          <div class="summary-card">
            <div class="summary-label">施工中</div>
            <div id="summary_construction" class="summary-value">-</div>
          </div>
          <div class="summary-card">
            <div class="summary-label">待請款</div>
            <div id="summary_billing" class="summary-value">-</div>
          </div>
        </section>

        <div class="section-title">工程案件流程</div>
        <section id="case_list" class="case-list">
          <div class="notice">工程案件讀取中...</div>
        </section>
      </section>

      <section id="detail_panel" class="detail-panel">
        <section id="case_detail" class="detail-card"></section>
        <section id="flow_detail" class="detail-card"></section>
        <section id="stage_form" class="stage-form"></section>
      </section>
    </main>

    <div id="department_modal_mask" class="modal-mask">
      <div class="modal">
        <div id="department_modal_title" class="modal-title">請選擇負責單位</div>
        <div class="modal-grid">
          <button type="button" onclick="confirmDepartmentChoice('業務(公司)')">業務(公司)</button>
          <button type="button" onclick="confirmDepartmentChoice('維修、工程部')">維修、工程部</button>
          <button type="button" onclick="confirmDepartmentChoice('維修、工程、專案部')">維修、工程、專案部</button>
          <button type="button" onclick="confirmDepartmentChoice('外包')">外包</button>
        </div>
        <button type="button" class="modal-cancel" onclick="closeDepartmentModal()">取消</button>
      </div>
    </div>

    <nav class="bottom-nav">
      <button type="button" class="gold" onclick="window.location.href='/app'">🏠 首頁</button>
      <button type="button" class="primary" id="nav_schedule_btn">📅 排班</button>
      <button type="button" class="green" onclick="window.location.href='/app/engineering/schedule'">📋 工程表</button>
      <button type="button" class="danger" onclick="window.location.href='/employee/logout?next=/employee/login'">登出</button>
    </nav>
  </div>

  <script>
    const CASES = __CASES_JSON__;
    const STAGES = __STAGES_JSON__;

    const STAGE_LABELS = {};
    const STAGE_UNITS = {};
    STAGES.forEach(function(stage) {
      STAGE_LABELS[stage.key] = stage.label;
      STAGE_UNITS[stage.key] = stage.unit;
    });

    let currentCase = null;
    let selectedCaseId = null;
    let pendingAction = "";

    const stageOrder = [
      "initial_survey",
      "business_review",
      "detailed_survey",
      "outsourced_survey",
      "quotation",
      "construction",
      "acceptance",
      "billing",
      "closed"
    ];

    const stageForms = {
      initial_survey: ["初步了解社區需求", "初步了解工程範圍", "粗估所需設備", "樓層限制", "備註與照片"],
      business_review: ["評估投資性", "合作條件", "是否繼續", "業務備註"],
      detailed_survey: ["勘驗場地", "規劃線路", "規劃機器數量", "訂定開工時間", "訂定完工時間"],
      outsourced_survey: ["評估施工可能性", "產出線路圖", "施工建議", "外包廠商", "備註"],
      quotation: ["報價單", "施工公告", "完工公告", "材料估算", "備註"],
      construction: ["施工日期", "施工人員", "材料領用", "施工照片", "施工日報", "異常事項"],
      acceptance: ["當區工程師驗收", "社區共同驗收", "驗收照片", "驗收結果", "缺失紀錄"],
      billing: ["確認請款是否入帳", "合作條件是否實施", "請款金額", "請款日期", "備註"],
      closed: ["案件已完成", "資料歸檔", "結案紀錄"],
      ended: ["案件已終止", "終止原因", "備註"]
    };

    function setText(id, value) {
      const el = document.getElementById(id);
      if (el) el.textContent = String(value);
    }

    function createEl(tag, className, text) {
      const el = document.createElement(tag);
      if (className) el.className = className;
      if (text !== undefined && text !== null) el.textContent = String(text);
      return el;
    }

    function clearEl(el) {
      while (el && el.firstChild) el.removeChild(el.firstChild);
    }

    function getCaseById(id) {
      return CASES.find(function(item) { return item.id === id; }) || null;
    }

    function getCurrentTarget() {
      if (selectedCaseId) {
        const selected = getCaseById(selectedCaseId);
        if (selected) return selected;
      }
      if (currentCase) return currentCase;
      return null;
    }

    function getStageIndex(stage) {
      const idx = stageOrder.indexOf(stage);
      return idx < 0 ? 0 : idx;
    }

    function stageLabel(stage) {
      return STAGE_LABELS[stage] || stage || "-";
    }

    function renderHome() {
      const list = document.getElementById("case_list");
      if (!list) return;

      setText("summary_active", CASES.filter(function(x) {
        return x.stage !== "closed" && x.stage !== "ended";
      }).length);
      setText("summary_construction", CASES.filter(function(x) {
        return x.stage === "construction";
      }).length);
      setText("summary_billing", CASES.filter(function(x) {
        return x.stage === "billing";
      }).length);

      clearEl(list);

      CASES.forEach(function(item) {
        list.appendChild(createCaseCard(item));
      });
    }

    function createCaseCard(item) {
      const card = createEl("button", "case-card");
      card.type = "button";
      card.onclick = function() {
        openCase(item.id);
      };

      const head = createEl("div", "case-head");
      const left = createEl("div");

      left.appendChild(createEl("div", "case-title", item.building + " / " + item.project));
      left.appendChild(createEl("div", "case-id", item.id));

      const badge = createEl("div", "stage-badge " + item.stage, stageLabel(item.stage));
      if (selectedCaseId === item.id) {
        badge.className += " selected-action";
      }
      badge.onclick = function(event) {
        event.preventDefault();
        event.stopPropagation();
        selectedCaseId = item.id;
        currentCase = item;
        renderHome();
      };

      head.appendChild(left);
      head.appendChild(badge);

      const meta = createEl("div", "case-meta");
      [
        ["責任單位", item.owner_unit || "-"],
        ["負責", item.owner_name || "-"],
        ["預計日期", item.planned_date || "-"],
        ["目前階段", stageLabel(item.stage)]
      ].forEach(function(pair) {
        const box = createEl("div", "meta-box", pair[0]);
        box.appendChild(createEl("strong", "", pair[1]));
        meta.appendChild(box);
      });

      const note = createEl("div", "case-note", item.note || "");

      card.appendChild(head);
      card.appendChild(meta);
      card.appendChild(note);

      return card;
    }

    function openCase(id) {
      const item = getCaseById(id);
      if (!item) {
        alert("找不到工程案件：" + id);
        return;
      }

      currentCase = item;
      selectedCaseId = null;

      const home = document.getElementById("home_panel");
      const detail = document.getElementById("detail_panel");

      if (home) home.style.display = "none";
      if (detail) detail.style.display = "block";

      renderCaseDetail();
      window.scrollTo({top: 0, behavior: "smooth"});
    }

    function showHome() {
      const home = document.getElementById("home_panel");
      const detail = document.getElementById("detail_panel");

      if (detail) detail.style.display = "none";
      if (home) home.style.display = "block";

      currentCase = null;
      selectedCaseId = null;
      renderHome();
      window.scrollTo({top: 0, behavior: "smooth"});
    }

    function renderCaseDetail() {
      if (!currentCase) return;

      const box = document.getElementById("case_detail");
      const flow = document.getElementById("flow_detail");
      const form = document.getElementById("stage_form");

      clearEl(box);
      clearEl(flow);
      clearEl(form);

      box.appendChild(createEl("div", "detail-title", currentCase.building + " / " + currentCase.project));
      box.appendChild(createEl("div", "detail-sub", currentCase.id + " / " + stageLabel(currentCase.stage)));

      const detailGrid = createEl("div", "detail-box-grid");

      const stageBox = createEl("div", "detail-box", "目前階段");
      stageBox.appendChild(createEl("strong", "", stageLabel(currentCase.stage)));

      const unitBox = createEl("div", "detail-box clickable-unit", "責任單位");
      unitBox.title = "點擊可變更負責單位";
      unitBox.appendChild(createEl("strong", "", currentCase.owner_unit || "-"));
      unitBox.onclick = function() {
        openDepartmentModal("change_unit");
      };

      const ownerBox = createEl("div", "detail-box", "負責");
      ownerBox.appendChild(createEl("strong", "", currentCase.owner_name || "-"));

      const dateBox = createEl("div", "detail-box", "預計日期");
      dateBox.appendChild(createEl("strong", "", currentCase.planned_date || "-"));

      detailGrid.appendChild(stageBox);
      detailGrid.appendChild(unitBox);
      detailGrid.appendChild(ownerBox);
      detailGrid.appendChild(dateBox);
      box.appendChild(detailGrid);

      const note = createEl("div", "case-note", currentCase.note || "");
      box.appendChild(note);

      renderFlowSteps(flow);
      renderStageForm(form);
    }

    function renderFlowSteps(container) {
      container.appendChild(createEl("div", "detail-title", "流程進度"));

      const line = createEl("div", "flow-line");
      const currentIndex = getStageIndex(currentCase.stage);

      STAGES.filter(function(s) {
        return s.key !== "ended";
      }).forEach(function(stage, idx) {
        const row = createEl("div", "flow-step");
        if (stage.key === currentCase.stage) row.className += " current";
        if (idx < currentIndex || currentCase.stage === "closed") row.className += " done";

        row.appendChild(createEl("div", "flow-dot", idx < currentIndex || currentCase.stage === "closed" ? "✓" : String(idx + 1)));
        row.appendChild(createEl("div", "", stage.label));
        row.appendChild(createEl("div", "flow-unit", stage.unit));

        line.appendChild(row);
      });

      container.appendChild(line);

      const actions = createEl("div", "action-area");
      getCurrentStageActions().forEach(function(action) {
        const btn = createEl("button", "action-btn " + (action.color || ""), action.label);
        btn.type = "button";
        btn.onclick = action.handler;
        actions.appendChild(btn);
      });

      container.appendChild(actions);
    }

    function renderStageForm(container) {
      container.appendChild(createEl("div", "form-title", stageLabel(currentCase.stage) + "作業項目與產出文件"));

      const list = createEl("div", "form-list");
      (stageForms[currentCase.stage] || ["備註"]).forEach(function(item) {
        list.appendChild(createEl("div", "form-item", item));
      });

      container.appendChild(list);
    }

    function getCurrentStageActions() {
      const stage = currentCase.stage;

      if (stage === "initial_survey") {
        return [
          {label:"初勘完成，送業務評估", color:"green", handler:function(){ setStage("business_review"); }},
          {label:"終止案件", color:"red", handler:function(){ setStage("ended"); }}
        ];
      }

      if (stage === "business_review") {
        return [
          {label:"可合作，進入細勘", color:"green", handler:function(){ setStage("detailed_survey"); }},
          {label:"不合作，結案 / END", color:"red", handler:function(){ setStage("ended"); }}
        ];
      }

      if (stage === "detailed_survey") {
        return [
          {label:"細勘完成，進入報價", color:"green", handler:function(){ setStage("quotation"); }},
          {label:"轉外包細勘", color:"orange", handler:function(){ setStage("outsourced_survey"); }},
          {label:"無法施作，結案 / END", color:"red", handler:function(){ setStage("ended"); }}
        ];
      }

      if (stage === "outsourced_survey") {
        return [
          {label:"可施工，進入報價", color:"green", handler:function(){ setStage("quotation"); }},
          {label:"不可施工，結案 / END", color:"red", handler:function(){ setStage("ended"); }}
        ];
      }

      if (stage === "quotation") {
        return [
          {label:"報價完成，進入施工", color:"green", handler:function(){ setStage("construction"); }}
        ];
      }

      if (stage === "construction") {
        return [
          {label:"施工完成，送完工驗收", color:"green", handler:function(){ setStage("acceptance"); }}
        ];
      }

      if (stage === "acceptance") {
        return [
          {label:"驗收通過，進入請款", color:"green", handler:function(){ setStage("billing"); }},
          {label:"驗收未過，退回施工", color:"orange", handler:function(){ setStage("construction"); }}
        ];
      }

      if (stage === "billing") {
        return [
          {label:"請款完成，結案 / END", color:"green", handler:function(){ setStage("closed"); }}
        ];
      }

      if (stage === "closed") {
        return [
          {label:"案件已結案", color:"", handler:function(){ alert("此案件已結案。"); }}
        ];
      }

      if (stage === "ended") {
        return [
          {label:"案件已終止", color:"", handler:function(){ alert("此案件已終止。"); }}
        ];
      }

      return [];
    }

    function setStage(stage) {
      if (!currentCase) return;

      currentCase.stage = stage;
      currentCase.owner_unit = STAGE_UNITS[stage] || currentCase.owner_unit;
      currentCase.owner_name = STAGE_UNITS[stage] || currentCase.owner_name;

      renderCaseDetail();
    }

    function openCurrentFlow() {
      const target = getCurrentTarget();
      if (!target) {
        alert("請先選擇或開啟一件工程案件。");
        return;
      }

      openCase(target.id);
    }

    function quickNextFromSelected() {
      const target = getCurrentTarget();
      if (!target) {
        alert("請先點擊案件右上角流程階段，再執行下一步。");
        return;
      }

      currentCase = target;

      const actions = getCurrentStageActions();
      if (!actions.length) {
        alert("此階段沒有可執行的下一步。");
        return;
      }

      actions[0].handler();
      selectedCaseId = null;
      renderHome();
    }

    function openDepartmentModal(actionName) {
      pendingAction = actionName;

      const mask = document.getElementById("department_modal_mask");
      const title = document.getElementById("department_modal_title");

      if (title) title.textContent = "請選擇負責單位";
      if (mask) mask.style.display = "flex";
    }

    function closeDepartmentModal() {
      const mask = document.getElementById("department_modal_mask");
      if (mask) mask.style.display = "none";
      pendingAction = "";
    }

    function confirmDepartmentChoice(unit) {
      if (!currentCase) {
        closeDepartmentModal();
        alert("請先開啟案件。");
        return;
      }

      currentCase.owner_unit = unit;
      currentCase.owner_name = unit;
      closeDepartmentModal();
      renderCaseDetail();
    }

    renderHome();
  </script>
</body>
</html>
"""

    return (
        html
        .replace("__USER_LINE__", _eng_escape(_current_user_line(user)))
        .replace("__CASES_JSON__", cases_json)
        .replace("__STAGES_JSON__", stages_json)
    )


@router.get("/app/engineering/schedule", response_class=HTMLResponse)
def engineering_schedule_landscape_page(request: _EmpRequest):
    user = _employee_current_user_from_request(request)

    if not user:
        return _EmpRedirectResponse("/employee/login?next=/app/engineering/schedule", status_code=303)

    cases_json = json.dumps(_load_engineering_cases(), ensure_ascii=False)

    html = """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

  <title>訊南工程系統｜工程排程</title>

  <style>
    * { box-sizing: border-box; }

    html, body {
      margin: 0;
      min-height: 100%;
      background: #edf2f7;
      color: #102348;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft JhengHei", sans-serif;
    }

    .portrait-warning {
      display: none;
      min-height: 100vh;
      padding: 28px 20px;
      align-items: center;
      justify-content: center;
      text-align: center;
      background: #eef4fb;
    }

    .portrait-card {
      width: 100%;
      max-width: 420px;
      padding: 28px 22px;
      border-radius: 24px;
      background: #fff;
      border: 1px solid #d7e1ef;
      box-shadow: 0 14px 32px rgba(15,23,42,.1);
    }

    .portrait-title {
      color: #102348;
      font-size: 26px;
      font-weight: 1000;
      line-height: 1.25;
    }

    .portrait-text {
      margin-top: 12px;
      color: #64748b;
      font-size: 16px;
      font-weight: 900;
      line-height: 1.55;
    }

    .landscape-page {
      min-height: 100vh;
      padding: 12px;
      background: #eef4fb;
    }

    .topbar {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      min-height: 62px;
      padding: 10px 14px;
      border-radius: 18px;
      background: linear-gradient(135deg, #2f7d7d, #365ee8 55%, #6d35e8);
      color: #fff;
      box-shadow: 0 10px 24px rgba(15,23,42,.12);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }

    .brand img {
      width: 42px;
      height: 42px;
      object-fit: contain;
      flex: 0 0 42px;
    }

    .brand-title {
      font-size: 22px;
      font-weight: 1000;
      line-height: 1.1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .brand-subtitle {
      margin-top: 3px;
      color: #fbbf24;
      font-size: 13px;
      font-weight: 1000;
      line-height: 1.1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .topbar button {
      height: 38px;
      border: 0;
      border-radius: 12px;
      padding: 0 14px;
      background: #fff;
      color: #102348;
      font-size: 13px;
      font-weight: 1000;
      box-shadow: 0 8px 18px rgba(15,23,42,.12);
      cursor: pointer;
      white-space: nowrap;
    }

    .schedule-wrap {
      margin-top: 12px;
      overflow: auto;
      border-radius: 18px;
      background: #fff;
      border: 1px solid #d7e1ef;
      box-shadow: 0 8px 22px rgba(15,23,42,.07);
      max-height: calc(100vh - 98px);
    }

    .schedule-table {
      width: 100%;
      min-width: 840px;
      border-collapse: collapse;
      table-layout: fixed;
    }

    .schedule-table th {
      position: sticky;
      top: 0;
      z-index: 5;
      padding: 6px 4px;
      background: #eff6ff;
      color: #1e3a8a;
      border: 1px solid #dbeafe;
      font-size: 11px;
      font-weight: 1000;
      white-space: nowrap;
      text-align: center;
    }

    .schedule-table th:first-child {
      left: 0;
      z-index: 8;
      background: #f8fafc;
      color: #102348;
      text-align: left;
      width: 118px;
    }

    .schedule-table td {
      height: 38px;
      padding: 0;
      border: 1px solid #e2e8f0;
      background: #fff;
      color: #102348;
      font-size: 11px;
      font-weight: 900;
      vertical-align: middle;
      text-align: center;
      position: relative;
      overflow: visible;
    }

    .schedule-table td:first-child {
      position: sticky;
      left: 0;
      z-index: 4;
      background: #fff;
      text-align: left;
      width: 118px;
      overflow: hidden;
    }

    .building-name {
      color: #102348;
      font-size: 12px;
      font-weight: 1000;
      line-height: 1.2;
    }

    .building-sub {
      margin-top: 2px;
      color: #64748b;
      font-size: 9px;
      font-weight: 900;
      line-height: 1.2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .week-cell {
      position: relative;
      height: 38px;
      display: block;
      background:
        linear-gradient(to right, transparent 0, transparent calc(100% / 63 - 1px), #eef2f7 calc(100% / 63 - 1px), #eef2f7 calc(100% / 63));
      background-size: calc(100% / 63) 100%;
      overflow: hidden;
    }

    .bar {
      position: absolute;
      top: 9px;
      height: 20px;
      border-radius: 0;
      padding: 0;
      font-size: 0;
      line-height: 0;
      overflow: hidden;
      box-shadow: inset 0 0 0 1px rgba(15,23,42,.10);
      z-index: 3;
    }

    .bar.initial,
    .bar.detailed,
    .bar.outsourced {
      background: #fde047;
      border: 1px solid #eab308;
    }

    .bar.construction {
      background: #bbf7d0;
      border: 1px solid #22c55e;
    }

    .bar.acceptance {
      background: #fdba74;
      border: 1px solid #f97316;
    }

    .bar.billing {
      background: #99f6e4;
      border: 1px solid #14b8a6;
    }

    .timeline-legend {
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
      padding: 8px 10px;
      border-top: 1px solid #e2e8f0;
      background: #fff;
      color: #334155;
      font-size: 11px;
      font-weight: 1000;
    }

    .timeline-legend-item {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      white-space: nowrap;
    }

    .legend-color {
      width: 18px;
      height: 10px;
      display: inline-block;
      border-radius: 0;
      border: 1px solid rgba(15,23,42,.16);
    }

    .legend-color.survey { background:#fde047; border-color:#eab308; }
    .legend-color.construction { background:#bbf7d0; border-color:#22c55e; }
    .legend-color.acceptance { background:#fdba74; border-color:#f97316; }
    .legend-color.billing { background:#99f6e4; border-color:#14b8a6; }

    @media screen and (orientation: portrait) and (max-width: 900px) {
      .landscape-page { display: none; }
      .portrait-warning { display: flex; }
    }

    @media screen and (orientation: landscape), screen and (min-width: 901px) {
      .portrait-warning { display: none; }
      .landscape-page { display: block; }
    }
  </style>
</head>

<body>
  <section class="portrait-warning">
    <div class="portrait-card">
      <div class="portrait-title">請將手機轉為橫向</div>
      <div class="portrait-text">
        工程排程表需要較寬畫面顯示。<br>
        請旋轉手機後再查看所有排程。
      </div>
    </div>
  </section>

  <main class="landscape-page">
    <header class="topbar">
      <div class="brand">
        <img src="/static/shinnan_home_logo.png" alt="訊南 Logo">
        <div>
          <div class="brand-title">訊南工程系統</div>
          <div class="brand-subtitle">工程排程</div>
        </div>
      </div>
      <button type="button" onclick="goBackToEngineeringApp()">返回上一頁</button>
    </header>

    <section id="schedule_wrap" class="schedule-wrap">
      <div style="padding:20px;font-weight:1000;color:#64748b;">排程讀取中...</div>
    </section>
  </main>

  <script>
    const CASES = __CASES_JSON__;

    function goBackToEngineeringApp() {
      if (window.history.length > 1) {
        window.history.back();
        return;
      }
      location.href = "/app/engineering";
    }

    function parseDateOnly(value) {
      const raw = String(value || "").trim();
      const parts = raw.split("-");
      if (parts.length !== 3) return null;
      return new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    }

    function formatMonthDay(date) {
      const mm = String(date.getMonth() + 1).padStart(2, "0");
      const dd = String(date.getDate()).padStart(2, "0");
      return mm + "/" + dd;
    }

    function addDays(date, days) {
      const d = new Date(date.getTime());
      d.setDate(d.getDate() + days);
      return d;
    }

    function daysBetween(a, b) {
      return Math.round((b - a) / (1000 * 60 * 60 * 24));
    }

    function escapeHtml(value) {
      return String(value == null ? "" : value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function getScheduleWeeks() {
      const now = new Date();
      const rangeStart = new Date(now.getFullYear(), now.getMonth(), 1);
      const rangeEnd = new Date(now.getFullYear(), now.getMonth() + 2, 0);

      const weeks = [];
      let cursor = new Date(rangeStart.getTime());
      const monthWeekCounter = {};

      while (cursor <= rangeEnd) {
        const weekStart = new Date(cursor.getTime());
        let weekEnd = addDays(weekStart, 6);

        if (weekEnd > rangeEnd) weekEnd = new Date(rangeEnd.getTime());

        const monthNumber = weekStart.getMonth() + 1;
        monthWeekCounter[monthNumber] = (monthWeekCounter[monthNumber] || 0) + 1;

        weeks.push({
          label: monthNumber + "月第" + monthWeekCounter[monthNumber] + "周",
          rangeLabel: formatMonthDay(weekStart) + "-" + formatMonthDay(weekEnd),
          start: weekStart,
          end: weekEnd
        });

        cursor = addDays(weekEnd, 1);
      }

      return {
        weeks: weeks,
        rangeStart: rangeStart,
        rangeEnd: rangeEnd
      };
    }

    function clampDate(date, minDate, maxDate) {
      if (date < minDate) return minDate;
      if (date > maxDate) return maxDate;
      return date;
    }

    function overlaps(start, end, rangeStart, rangeEnd) {
      if (!start || !end) return false;
      return start <= rangeEnd && end >= rangeStart;
    }

    function buildBar(stage, rangeStart, rangeEnd, totalDays) {
      if (!overlaps(stage.start, stage.end, rangeStart, rangeEnd)) return "";

      const barStart = clampDate(stage.start, rangeStart, rangeEnd);
      const barEnd = clampDate(stage.end, rangeStart, rangeEnd);

      const left = (daysBetween(rangeStart, barStart) / totalDays) * 100;
      const width = ((daysBetween(barStart, barEnd) + 1) / totalDays) * 100;

      return '<div class="bar ' + escapeHtml(stage.className) + '" style="left:' + left + '%;width:' + width + '%;"></div>';
    }

    function getStages(item) {
      const stages = [];

      const surveyDate = parseDateOnly(item.planned_date);
      const constructionStart = parseDateOnly(item.startDate);
      const constructionEnd = parseDateOnly(item.endDate);
      const acceptanceDate = constructionEnd ? addDays(constructionEnd, 7) : null;
      const billingDate = acceptanceDate ? addDays(acceptanceDate, 7) : null;

      if (surveyDate) {
        stages.push({className:"initial", start:surveyDate, end:surveyDate});
      }

      if (constructionStart && constructionEnd) {
        stages.push({className:"construction", start:constructionStart, end:constructionEnd});
      }

      if (acceptanceDate) {
        stages.push({className:"acceptance", start:acceptanceDate, end:acceptanceDate});
      }

      if (billingDate) {
        stages.push({className:"billing", start:billingDate, end:billingDate});
      }

      return stages;
    }

    function renderScheduleTable() {
      const wrap = document.getElementById("schedule_wrap");
      if (!wrap) return;

      const timeline = getScheduleWeeks();
      const weeks = timeline.weeks;
      const rangeStart = timeline.rangeStart;
      const rangeEnd = timeline.rangeEnd;
      const totalDays = daysBetween(rangeStart, rangeEnd) + 1;

      const head = weeks.map(function(week) {
        return '<th>' + escapeHtml(week.label) + '<br><span style="font-size:8px;color:#64748b;">' + escapeHtml(week.rangeLabel) + '</span></th>';
      }).join("");

      const rows = CASES.map(function(item) {
        const bars = getStages(item).map(function(stage) {
          return buildBar(stage, rangeStart, rangeEnd, totalDays);
        }).join("");

        return '<tr>' +
          '<td><div class="building-name">' + escapeHtml(item.building) + '</div><div class="building-sub">' + escapeHtml(item.project) + '</div></td>' +
          '<td colspan="' + weeks.length + '"><div class="week-cell">' + bars + '</div></td>' +
          '</tr>';
      }).join("");

      wrap.innerHTML =
        '<table class="schedule-table">' +
          '<thead><tr><th>大樓 / 工程</th>' + head + '</tr></thead>' +
          '<tbody>' + rows + '</tbody>' +
        '</table>' +
        '<div class="timeline-legend">' +
          '<span class="timeline-legend-item"><span class="legend-color survey"></span>勘場 / 細勘</span>' +
          '<span class="timeline-legend-item"><span class="legend-color construction"></span>施工</span>' +
          '<span class="timeline-legend-item"><span class="legend-color acceptance"></span>驗收</span>' +
          '<span class="timeline-legend-item"><span class="legend-color billing"></span>請款</span>' +
        '</div>';
    }

    renderScheduleTable();
  </script>
</body>
</html>
"""

    return (
        html
        .replace("__CASES_JSON__", cases_json)
    )

