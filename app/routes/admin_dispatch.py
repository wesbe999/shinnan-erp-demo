# -*- coding: utf-8 -*-
import json

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy import text

from app.db import engine
from app.routes.employee_auth import _employee_current_user_from_request


router = APIRouter(tags=["admin_dispatch"])


DISPATCH_DEPARTMENTS = (
    "東區", "北區", "北台南", "仁德", "永康", "安平", "南高", "北高",
    "維修部", "工程部", "專案部",
)


def _json_response(data, status_code: int = 200):
    return Response(
        content=json.dumps(data, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
        status_code=status_code,
    )


@router.get("/admin", response_class=HTMLResponse, summary="公司端派工後台")
def admin_page(request: Request):
    current_user = _employee_current_user_from_request(request)
    if not current_user:
        return RedirectResponse("/employee/login?next=/admin", status_code=303)
    return HTMLResponse(CLEAN_ADMIN_HTML)


@router.get("/admin/engineers", summary="工程師名錄已改由人資系統管理")
def admin_engineers_redirect():
    return RedirectResponse("/admin/hr", status_code=303)


@router.get("/api/admin/engineers", summary="從人資資料取得派工可用工程師")
def api_admin_engineers_from_hr():
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT
                staff_code,
                display_name,
                department,
                role,
                position_title,
                employment_status,
                app_access,
                permission_scope,
                note
            FROM employee_profiles
            WHERE COALESCE(employment_status, '') IN ('', '在職')
              AND COALESCE(department, '') IN (
                    '東區', '北區', '北台南', '仁德', '永康', '安平', '南高', '北高',
                    '維修部', '工程部', '專案部'
              )
              AND (
                    COALESCE(app_access, '') LIKE '%dispatch%'
                 OR COALESCE(app_access, '') LIKE '%engineering%'
                 OR COALESCE(role, '') = 'field'
                 OR COALESCE(position_title, '') LIKE '%工程%'
                 OR COALESCE(position_title, '') LIKE '%區域%'
              )
            ORDER BY
                CASE department
                    WHEN '東區' THEN 1
                    WHEN '北區' THEN 2
                    WHEN '北台南' THEN 3
                    WHEN '仁德' THEN 4
                    WHEN '永康' THEN 5
                    WHEN '安平' THEN 6
                    WHEN '南高' THEN 7
                    WHEN '北高' THEN 8
                    WHEN '維修部' THEN 9
                    WHEN '工程部' THEN 10
                    WHEN '專案部' THEN 11
                    ELSE 99
                END,
                staff_code
        """)).mappings().fetchall()

        today = ""
        leave_staff = set()

        try:
            today_row = conn.execute(text("SELECT date('now', 'localtime') AS today")).mappings().first()
            today = str(today_row.get("today") or "") if today_row else ""
        except Exception:
            today = ""

        if today:
            try:
                has_leave_table = conn.execute(text("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table' AND name = 'employee_leave_settings'
                    LIMIT 1
                """)).first()
                if has_leave_table:
                    leave_rows = conn.execute(text("""
                        SELECT DISTINCT staff_code
                        FROM employee_leave_settings
                        WHERE leave_date = :today
                          AND COALESCE(review_status, '') IN ('已核准', '核准', '通過', 'approved', 'Approved')
                    """), {"today": today}).mappings().fetchall()
                    leave_staff.update(str(r.get("staff_code") or "").strip() for r in leave_rows)
            except Exception:
                pass

            try:
                has_rest_table = conn.execute(text("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table' AND name = 'employee_rest_month_settings'
                    LIMIT 1
                """)).first()
                if has_rest_table:
                    rest_rows = conn.execute(text("""
                        SELECT staff_code, selected_dates, review_status
                        FROM employee_rest_month_settings
                        WHERE selected_dates LIKE :today_like
                          AND COALESCE(review_status, '') IN ('已核准', '核准', '通過', 'approved', 'Approved', '待審核')
                    """), {"today_like": "%" + today + "%"}).mappings().fetchall()
                    for r in rest_rows:
                        try:
                            selected_dates = json.loads(r.get("selected_dates") or "[]")
                        except Exception:
                            selected_dates = []
                        if today in selected_dates:
                            leave_staff.add(str(r.get("staff_code") or "").strip())
            except Exception:
                pass

    items = []
    seen = set()

    for row in rows:
        staff_code = str(row.get("staff_code") or "").strip()
        name = str(row.get("display_name") or "").strip()
        department = str(row.get("department") or "").strip()
        if not staff_code or not name or not department or staff_code in seen:
            continue
        if department not in DISPATCH_DEPARTMENTS:
            continue

        seen.add(staff_code)
        employment_status = str(row.get("employment_status") or "").strip() or "在職"
        work_status = "休假中" if staff_code in leave_staff else "在職"
        if employment_status not in ("", "在職"):
            work_status = employment_status

        items.append({
            "employee_no": staff_code,
            "staff_code": staff_code,
            "name": name,
            "display_name": name,
            "department": department,
            "role": str(row.get("role") or "").strip(),
            "position_title": str(row.get("position_title") or "").strip(),
            "employment_status": employment_status,
            "work_status": work_status,
            "leave_status": work_status,
            "app_access": str(row.get("app_access") or "").strip(),
            "permission_scope": str(row.get("permission_scope") or "").strip(),
            "note": str(row.get("note") or "").strip(),
        })

    return _json_response(items)


CLEAN_ADMIN_HTML = r'''
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>訊南科技派工系統｜公司後台</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {
      --blue:#365ee8;
      --green:#43a047;
      --orange:#d95f18;
      --red:#c9332b;
      --purple:#6f39df;
      --teal:#2d766a;
      --bg:#f3f6fb;
      --card:#ffffff;
      --line:#d7e1ef;
      --text:#102348;
      --muted:#64748b;
      --sticky:#ffffff;
    }

    * { box-sizing:border-box; }

    body {
      margin:0;
      background:var(--bg);
      color:var(--text);
      font-family:"Microsoft JhengHei","Segoe UI",Arial,sans-serif;
    }

    .admin-header {
      min-height:104px;
      padding:18px 34px;
      background:linear-gradient(120deg,#3f6471,#365ee8 68%,#7c3aed);
      color:#fff;
      display:flex;
      align-items:center;
      gap:18px;
      box-shadow:0 10px 26px rgba(15,23,42,.16);
      border-bottom-left-radius:24px;
    }

    .admin-logo { width:96px; height:68px; object-fit:contain; flex:0 0 auto; }
    .admin-title { font-size:34px; line-height:1.1; font-weight:1000; letter-spacing:2px; white-space:nowrap; }

    .page { width:min(1760px, calc(100% - 56px)); margin:14px auto 42px; }

    button {
      height:40px;
      border:0;
      border-radius:12px;
      padding:0 18px;
      color:#fff;
      font-size:15px;
      font-weight:1000;
      cursor:pointer;
      white-space:nowrap;
      font-family:inherit;
    }

    .btn-blue { background:var(--blue); }
    .btn-green { background:var(--green); }
    .btn-gray { background:#64748b; }
    .btn-red { background:var(--red); }
    .btn-orange { background:var(--orange); }
    .btn-purple { background:var(--purple); }

    .notice-panel {
      border:1px solid #fdba74;
      background:#fff7ed;
      border-radius:12px;
      padding:7px 10px;
      margin:8px 0 12px;
    }

    .notice-head { display:flex; align-items:center; gap:20px; margin-bottom:5px; color:#9a3412; line-height:1; white-space:nowrap; }
    .notice-title { font-size:14px; font-weight:1000; color:#c2410c; }
    .notice-subtitle { font-size:13px; font-weight:800; overflow:hidden; text-overflow:ellipsis; }

    .notice-input-row {
      display:grid;
      grid-template-columns:minmax(0,1fr) auto;
      gap:7px;
      align-items:center;
      height:28px;
      border:1px solid #fdba74;
      border-radius:8px;
      background:#fff;
      padding:2px 4px 2px 8px;
    }

    #notice_input { width:100%; height:22px; border:0; outline:0; background:transparent; color:var(--text); font-size:12px; font-weight:900; font-family:inherit; }
    .notice-actions { display:flex; gap:5px; align-items:center; }
    .notice-actions button { height:22px; min-width:48px; padding:0 8px; border-radius:6px; font-size:11px; }

    .notice-list { margin-top:5px; border:1px dashed #fb923c; border-radius:8px; background:#fff; overflow:hidden; }
    .notice-row { display:grid; grid-template-columns:minmax(0,1fr) 44px; align-items:center; gap:6px; height:24px; padding:0 6px; border-bottom:1px dashed #fdba74; }
    .notice-row:last-child { border-bottom:0; }
    .notice-text { overflow:hidden; white-space:nowrap; text-overflow:ellipsis; color:#102348; font-size:12px; font-weight:900; }
    .notice-row button { height:18px; padding:0; border-radius:5px; font-size:10px; background:var(--red); }

    .toolbar { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:12px; }
    .top-filter { display:flex; align-items:center; gap:8px; height:42px; padding:5px 10px; background:#fff; border:1px solid var(--line); border-radius:12px; box-shadow:0 4px 12px rgba(15,23,42,.04); }
    .top-filter label { color:#334155; font-size:14px; font-weight:1000; white-space:nowrap; }
    .top-filter select { width:150px; height:30px; border:1px solid #cbd5e1; border-radius:8px; padding:0 8px; color:var(--text); background:#f8fafc; font-size:14px; font-weight:900; }
    #top_filter_engineer { width:190px; }
    .sync-status { margin-left:auto; color:#64748b; font-size:13px; font-weight:900; white-space:nowrap; }

    .stats-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:14px; margin-bottom:18px; }
    .stat-card { background:#fff; border:1px solid var(--line); border-radius:18px; padding:18px 20px; box-shadow:0 8px 22px rgba(15,23,42,.06); cursor:pointer; min-height:116px; }
    .stat-card.active { border-color:var(--blue); background:#eff6ff; box-shadow:0 0 0 3px rgba(54,94,232,.14),0 8px 22px rgba(15,23,42,.08); }
    .stat-label { color:var(--muted); font-size:15px; font-weight:900; }
    .stat-number { margin-top:8px; font-size:42px; line-height:1; font-weight:1000; color:var(--text); }

    .panel {
      background:#fff;
      border:1px solid var(--line);
      border-radius:20px;
      box-shadow:0 8px 22px rgba(15,23,42,.06);
      padding:20px;
    }

    .case-top-grid {
      display:grid;
      grid-template-columns:1fr 1fr;
      gap:16px;
      align-items:stretch;
      margin-bottom:14px;
    }

    .case-head-box,
    .engineer-board {
      min-height:142px;
      max-height:142px;
      border:1px solid var(--line);
      border-radius:16px;
      background:#fff;
      padding:16px 18px;
      overflow:hidden;
    }

    .panel-title,
    .engineer-board-title {
      margin:0 0 12px;
      color:var(--teal);
      font-size:24px;
      line-height:1.15;
      font-weight:1000;
    }

    .search-box label { display:block; color:var(--muted); font-size:13px; font-weight:900; margin-bottom:6px; }
    .search-box input { width:100%; height:36px; border:1px solid #cbd5e1; border-radius:10px; padding:4px 12px; background:#f8fafc; color:var(--text); font-size:14px; font-weight:900; font-family:inherit; }

    .engineer-board-content {
      height:calc(142px - 56px);
      overflow:auto;
      display:flex;
      flex-wrap:wrap;
      gap:6px;
      align-content:flex-start;
      padding-right:4px;
    }

    .engineer-board-pill {
      display:inline-flex;
      align-items:center;
      gap:5px;
      height:24px;
      min-height:24px;
      max-width:100%;
      padding:0 8px;
      border-radius:999px;
      border:1px solid #cbd5e1;
      background:#fff;
      color:#102348;
      font-size:11px;
      line-height:1;
      font-weight:1000;
      white-space:nowrap;
    }

    .engineer-board-pill-off { background:#f1f5f9; color:#475569; }
    .engineer-board-pill-name,
    .engineer-board-pill-meta { font-size:11px; line-height:1; }

    .table-wrap {
      width:100%;
      max-height:540px;
      overflow:auto;
      border:1px solid var(--line);
      border-radius:14px;
    }

    table {
      width:92%;
      max-width:92%;
      min-width:0;
      border-collapse:separate;
      border-spacing:0;
      table-layout:fixed;
      background:#fff;
      font-size:12px;
    }

    th, td {
      overflow:hidden;
      text-overflow:ellipsis;
      word-break:break-word;
      font-size:12px;
      line-height:1.25;
    }

    th {
      position:sticky;
      top:0;
      z-index:5;
      background:#f8fafc;
      color:#475569;
      font-weight:1000;
      text-align:left;
      padding:6px;
      border-bottom:1px solid #cbd5e1;
      white-space:nowrap;
    }

    thead tr.filter-row th { top:31px; background:#eef3f9; padding:4px 5px; z-index:5; }
    thead select { width:100%; height:24px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; color:#102348; font-size:11px; font-weight:900; }

    td {
      height:40px;
      padding:6px;
      border-bottom:1px solid #e5e7eb;
      background:#fff;
      vertical-align:middle;
      color:#102348;
      font-weight:800;
    }

    tbody tr:hover td { background:#f8fafc; }

    th:nth-child(1), td:nth-child(1) { width:5%; }
    th:nth-child(2), td:nth-child(2) { width:6%; }
    th:nth-child(3), td:nth-child(3) { width:7%; }
    th:nth-child(4), td:nth-child(4) { width:22%; }
    th:nth-child(5), td:nth-child(5) { width:10%; }
    th:nth-child(6), td:nth-child(6) { width:10%; }
    th:nth-child(7), td:nth-child(7) { width:7%; }
    th:nth-child(8), td:nth-child(8) { width:6%; }
    th:nth-child(9), td:nth-child(9) { width:14%; }
    th:nth-child(10), td:nth-child(10) { width:13%; }

    th:nth-child(1), td:nth-child(1) { position:sticky; left:0; z-index:6; background:var(--sticky); box-shadow:1px 0 0 #e5e7eb; }
    th:nth-child(2), td:nth-child(2) { position:sticky; left:5%; z-index:6; background:var(--sticky); box-shadow:1px 0 0 #e5e7eb; }
    th:nth-child(3), td:nth-child(3) { position:sticky; left:11%; z-index:6; background:var(--sticky); box-shadow:1px 0 0 #e5e7eb; }
    thead th:nth-child(1), thead th:nth-child(2), thead th:nth-child(3) { z-index:12; background:#f8fafc; }
    thead tr.filter-row th:nth-child(1), thead tr.filter-row th:nth-child(2), thead tr.filter-row th:nth-child(3) { z-index:12; background:#eef3f9; }

    .address-cell { white-space:normal; line-height:1.35; word-break:break-word; overflow-wrap:anywhere; }
    .pill { display:inline-flex; align-items:center; justify-content:center; min-height:21px; padding:0 7px; border-radius:999px; font-size:11px; font-weight:1000; white-space:nowrap; }
    .pill-wait { background:#fef3c7; color:#92400e; }
    .pill-claim { background:#ffe4e6; color:#be123c; }
    .pill-done { background:#dcfce7; color:#166534; }
    .pill-default { background:#f1f5f9; color:#334155; }
    .delete-button { width:44px; min-width:44px; height:24px; padding:0 4px; border-radius:7px; font-size:11px; background:var(--red); }

    .modal-mask { position:fixed; inset:0; z-index:9000; display:none; align-items:center; justify-content:center; padding:24px; background:rgba(15,23,42,.58); }
    .modal-mask.active { display:flex; }
    .modal { width:min(880px,96vw); max-height:90vh; overflow:auto; background:#fff; border:1px solid var(--line); border-radius:22px; box-shadow:0 28px 90px rgba(15,23,42,.32); padding:20px; }
    .modal-head { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:14px; padding-bottom:12px; border-bottom:1px solid var(--line); }
    .modal-title { font-size:26px; font-weight:1000; color:var(--text); }
    .modal-subtitle { margin-top:5px; color:var(--muted); font-size:13px; font-weight:800; }
    .modal-close { height:34px; min-width:68px; background:#64748b; }
    .detail-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:14px; }
    .detail-card { border:1px solid var(--line); border-radius:14px; background:#f8fbff; padding:10px 12px; }
    .detail-card.full { grid-column:1 / -1; }
    .detail-label { color:var(--muted); font-size:12px; font-weight:900; margin-bottom:4px; }
    .detail-value { color:var(--text); font-size:15px; font-weight:1000; line-height:1.45; white-space:pre-wrap; }
    .modal-actions { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:8px; padding-top:12px; border-top:1px solid var(--line); }
    .create-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px 12px; }
    .field label { display:block; color:var(--muted); font-size:13px; font-weight:900; margin-bottom:5px; }
    .field input, .field select, .field textarea { width:100%; height:38px; border:1px solid #cbd5e1; border-radius:10px; background:#f8fafc; padding:4px 10px; color:var(--text); font-size:14px; font-weight:900; font-family:inherit; }
    .field textarea { height:78px; resize:vertical; }
    .field.full { grid-column:1 / -1; }

    @media (max-width:1320px) {
      .table-wrap { overflow-x:auto; }
      table { min-width:1180px; }
    }

    @media (max-width:1100px) {
      .stats-grid { grid-template-columns:repeat(2,1fr); }
      .case-top-grid { grid-template-columns:1fr; }
      .engineer-board { max-height:180px; }
      .engineer-board-content { height:120px; }
      .sync-status { margin-left:0; }
    }

    @media (max-width:760px) {
      .page { width:calc(100% - 24px); }
      .admin-header { padding:16px 18px; }
      .admin-title { font-size:26px; }
      .stats-grid { grid-template-columns:1fr; }
      .create-grid, .detail-grid { grid-template-columns:1fr; }
    }

    .panel-case-board th:nth-child(1),
    .panel-case-board td:nth-child(1) {
      left: 0 !important;
    }

    .panel-case-board th:nth-child(2),
    .panel-case-board td:nth-child(2) {
      left: 5% !important;
    }

    .panel-case-board th:nth-child(3),
    .panel-case-board td:nth-child(3) {
      left: 11% !important;
    }

    .panel-case-board td:nth-child(4) {
      white-space: normal !important;
      word-break: break-word !important;
      overflow-wrap: anywhere !important;
    }

    .panel-case-board td:nth-child(5),
    .panel-case-board td:nth-child(6),
    .panel-case-board td:nth-child(7),
    .panel-case-board td:nth-child(8),
    .panel-case-board td:nth-child(10) {
      white-space: nowrap !important;
    }

    .panel-case-board td:nth-child(9) {
      white-space: normal !important;
      word-break: break-word !important;
      overflow-wrap: anywhere !important;
    }
    .panel-case-board th:nth-child(1),
    .panel-case-board td:nth-child(1) {
      position: sticky !important;
      left: 0 !important;
      z-index: 6 !important;
      background: var(--sticky) !important;
      box-shadow: 1px 0 0 #e5e7eb !important;
    }

    .panel-case-board th:nth-child(2),
    .panel-case-board td:nth-child(2) {
      position: sticky !important;
      left: 5% !important;
      z-index: 6 !important;
      background: var(--sticky) !important;
      box-shadow: 1px 0 0 #e5e7eb !important;
    }

    .panel-case-board th:nth-child(3),
    .panel-case-board td:nth-child(3) {
      position: sticky !important;
      left: 11% !important;
      z-index: 6 !important;
      background: var(--sticky) !important;
      box-shadow: 1px 0 0 #e5e7eb !important;
    }

    .panel-case-board thead th:nth-child(1),
    .panel-case-board thead th:nth-child(2),
    .panel-case-board thead th:nth-child(3) {
      z-index: 12 !important;
      background: #f8fafc !important;
    }

    .panel-case-board thead tr.filter-row th:nth-child(1),
    .panel-case-board thead tr.filter-row th:nth-child(2),
    .panel-case-board thead tr.filter-row th:nth-child(3) {
      z-index: 12 !important;
      background: #eef3f9 !important;
    }

    .panel-case-board .delete-button {
      width: 54px !important;
      min-width: 54px !important;
      height: 24px !important;
      padding: 0 5px !important;
      font-size: 11px !important;
    }


    /* CLEAN_TABLE_COLGROUP_WIDTH_FINAL_V3 */
    .panel-case-board .table-wrap {
      width: 100% !important;
      overflow-x: hidden !important;
      overflow-y: auto !important;
    }

    .panel-case-board table {
      width: 100% !important;
      min-width: 0 !important;
      table-layout: fixed !important;
    }

    .panel-case-board th,
    .panel-case-board td {
      font-size: 12px !important;
      padding: 6px 5px !important;
      line-height: 1.22 !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
    }

    .panel-case-board th:nth-child(1),
    .panel-case-board td:nth-child(1) {
      position: sticky !important;
      left: 0 !important;
      z-index: 6 !important;
      background: var(--sticky) !important;
      box-shadow: 1px 0 0 #e5e7eb !important;
    }

    .panel-case-board th:nth-child(2),
    .panel-case-board td:nth-child(2) {
      position: sticky !important;
      left: 5% !important;
      z-index: 6 !important;
      background: var(--sticky) !important;
      box-shadow: 1px 0 0 #e5e7eb !important;
    }

    .panel-case-board th:nth-child(3),
    .panel-case-board td:nth-child(3) {
      position: sticky !important;
      left: 11% !important;
      z-index: 6 !important;
      background: var(--sticky) !important;
      box-shadow: 1px 0 0 #e5e7eb !important;
    }

    .panel-case-board thead th:nth-child(1),
    .panel-case-board thead th:nth-child(2),
    .panel-case-board thead th:nth-child(3) {
      z-index: 12 !important;
      background: #f8fafc !important;
    }

    .panel-case-board thead tr.filter-row th:nth-child(1),
    .panel-case-board thead tr.filter-row th:nth-child(2),
    .panel-case-board thead tr.filter-row th:nth-child(3) {
      z-index: 12 !important;
      background: #eef3f9 !important;
    }

    .panel-case-board td:nth-child(4),
    .panel-case-board td:nth-child(9) {
      white-space: normal !important;
      word-break: break-word !important;
      overflow-wrap: anywhere !important;
    }

    .panel-case-board td:nth-child(5),
    .panel-case-board td:nth-child(6),
    .panel-case-board td:nth-child(7),
    .panel-case-board td:nth-child(8),
    .panel-case-board td:nth-child(10) {
      white-space: nowrap !important;
    }

    .panel-case-board .delete-button {
      width: 54px !important;
      min-width: 54px !important;
      height: 24px !important;
      padding: 0 5px !important;
      font-size: 11px !important;
    }


    /* CLEAN_REMOVE_LEFT_STICKY_FINAL_V1 */

    .panel-case-board th:nth-child(1),
    .panel-case-board td:nth-child(1),
    .panel-case-board th:nth-child(2),
    .panel-case-board td:nth-child(2),
    .panel-case-board th:nth-child(3),
    .panel-case-board td:nth-child(3),
    th:nth-child(1),
    td:nth-child(1),
    th:nth-child(2),
    td:nth-child(2),
    th:nth-child(3),
    td:nth-child(3) {
      position: static !important;
      left: auto !important;
      z-index: auto !important;
      box-shadow: none !important;
    }

    .panel-case-board thead th,
    thead th {
      position: sticky !important;
      top: 0 !important;
      z-index: 10 !important;
      background: #f8fafc !important;
    }

    .panel-case-board thead tr.filter-row th,
    thead tr.filter-row th {
      position: sticky !important;
      top: 31px !important;
      z-index: 9 !important;
      background: #eef3f9 !important;
    }

    .panel-case-board table,
    table {
      width: 100% !important;
      max-width: 100% !important;
      table-layout: fixed !important;
    }

    .panel-case-board .table-wrap,
    .table-wrap {
      overflow-x: hidden !important;
      overflow-y: auto !important;
    }


    /* CLEAN_HEADER_STICKY_WIDTH_TUNE_FINAL_V1 */
    .panel-case-board table,
    table {
      width: 100% !important;
      max-width: 100% !important;
      min-width: 0 !important;
      table-layout: fixed !important;
    }
    .panel-case-board tbody td:nth-child(1),
    .panel-case-board tbody td:nth-child(2),
    .panel-case-board tbody td:nth-child(3),
    tbody td:nth-child(1),
    tbody td:nth-child(2),
    tbody td:nth-child(3) {
      position: static !important;
      left: auto !important;
      z-index: auto !important;
      box-shadow: none !important;
    }
    .panel-case-board .table-wrap table thead tr:first-child th,
    .table-wrap table thead tr:first-child th {
      position: sticky !important;
      top: 0 !important;
      z-index: 30 !important;
      background: #f8fafc !important;
      box-shadow: 0 1px 0 #cbd5e1 !important;
    }
    .panel-case-board .table-wrap table thead tr.filter-row th,
    .table-wrap table thead tr.filter-row th {
      position: sticky !important;
      top: 31px !important;
      z-index: 29 !important;
      background: #eef3f9 !important;
      box-shadow: 0 1px 0 #cbd5e1 !important;
    }
    .panel-case-board th,
    .panel-case-board td,
    th,
    td {
      font-size: 12px !important;
      padding: 6px 6px !important;
      line-height: 1.25 !important;
    }
    .panel-case-board td:nth-child(4),
    .panel-case-board td:nth-child(9),
    td:nth-child(4),
    td:nth-child(9) {
      white-space: normal !important;
      word-break: break-word !important;
      overflow-wrap: anywhere !important;
    }

    .panel-case-board td:nth-child(1),
    .panel-case-board td:nth-child(2),
    .panel-case-board td:nth-child(3),
    .panel-case-board td:nth-child(5),
    .panel-case-board td:nth-child(6),
    .panel-case-board td:nth-child(7),
    .panel-case-board td:nth-child(8),
    .panel-case-board td:nth-child(10),
    td:nth-child(1),
    td:nth-child(2),
    td:nth-child(3),
    td:nth-child(5),
    td:nth-child(6),
    td:nth-child(7),
    td:nth-child(8),
    td:nth-child(10) {
      white-space: nowrap !important;
    }
    .panel-case-board td:nth-child(6),
    td:nth-child(6) {
      text-overflow: clip !important;
    }
    .panel-case-board .delete-button,
    .delete-button {
      width: 54px !important;
      min-width: 54px !important;
      height: 26px !important;
      padding: 0 5px !important;
      font-size: 11px !important;
      border-radius: 7px !important;
    }


    /* CLEAN_DETAIL_MODAL_AMOUNT_NOTE_FINAL_V1 */
    .detail-value {
      white-space: pre-wrap !important;
    }

    .detail-card.full .detail-value {
      line-height: 1.5 !important;
    }


    /* CLEAN_DETAIL_AMOUNT_BOX_FINAL_V1 */

    .detail-card-amount {
      background: #f8fbff !important;
    }

    .detail-card-amount .detail-value {
      white-space: normal !important;
    }

    .detail-amount-board {
      border: 1px solid #dbe3ef;
      border-radius: 16px;
      background: #f8fbff;
      padding: 12px 14px;
      color: #102348;
    }

    .detail-amount-title {
      font-size: 20px;
      line-height: 1.2;
      font-weight: 1000;
      color: #102348;
      margin-bottom: 12px;
    }

    .detail-amount-row,
    .detail-amount-formula {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-end;
      gap: 10px;
      margin-bottom: 10px;
    }

    .detail-amount-field {
      min-width: 110px;
    }

    .detail-amount-field-small {
      min-width: 92px;
    }

    .detail-amount-label {
      font-size: 13px;
      line-height: 1.2;
      color: #64748b;
      font-weight: 900;
      margin-bottom: 5px;
    }

    .detail-amount-input,
    .detail-amount-total-value {
      min-height: 36px;
      min-width: 110px;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      background: #ffffff;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      padding: 0 12px;
      font-size: 16px;
      font-weight: 900;
      color: #102348;
    }

    .detail-amount-total-value {
      min-width: 150px;
      border-color: #fdba74;
      background: #fff7ed;
      color: #9a3412;
      font-size: 18px;
      font-weight: 1000;
    }

    .detail-amount-symbol {
      font-size: 24px;
      line-height: 36px;
      font-weight: 1000;
      color: #102348;
      padding-bottom: 2px;
    }

    .detail-amount-note,
    .detail-amount-empty {
      margin-top: 8px;
      color: #64748b;
      font-size: 13px;
      line-height: 1.5;
      font-weight: 800;
    }


    /* CLEAN_CREATE_MODAL_PRICE_FIELDS_CLEAN_V4 */
    .create-price-panel {
      border: 1px solid #dbe3ef;
      border-radius: 16px;
      background: #f8fbff;
      padding: 14px 16px;
      margin-top: 4px;
    }

    .create-price-title {
      font-size: 20px;
      font-weight: 1000;
      color: #102348;
      margin-bottom: 12px;
    }

    .create-price-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px 14px;
    }

    .create-price-note {
      margin-top: 10px;
      color: #64748b;
      font-size: 13px;
      line-height: 1.5;
      font-weight: 800;
    }

    @media (max-width: 900px) {
      .create-price-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }


    /* ADDRESS_HELPER_SELECT_V1 */
    .address-helper-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 180px;
      gap: 10px;
      align-items: center;
    }

    .address-helper-input {
      width: 100%;
      min-width: 0;
    }

    .address-helper-select {
      width: 180px;
      min-width: 180px;
      cursor: pointer;
    }

    @media (max-width: 700px) {
      .address-helper-row {
        grid-template-columns: 1fr;
      }

      .address-helper-select {
        width: 100%;
        min-width: 0;
      }
    }

</style>
</head>

<body>
  <header class="admin-header">
    <img class="admin-logo" src="/erp-static/shinnan_home_logo.png" alt="ShinNan Logo" onerror="this.style.display='none'">
    <div><div class="admin-title">訊南科技派工系統</div></div>
  </header>

  <main class="page">
    <section class="notice-panel">
      <div class="notice-head">
        <div class="notice-title">公司緊急通知</div>
        <div class="notice-subtitle">可連續送出多條通知；每條通知可個別刪除，手機板跑馬燈會依序連播。</div>
      </div>
      <div class="notice-input-row">
        <input id="notice_input" placeholder="輸入新的緊急通知，按送出後會加入通知清單。">
        <div class="notice-actions">
          <button class="btn-green" type="button" onclick="sendNotice()">送出</button>
          <button class="btn-gray" type="button" onclick="clearNoticeInput()">清除</button>
        </div>
      </div>
      <div id="notice_list" class="notice-list"></div>
    </section>

    <section class="toolbar">
      <div class="top-filter"><label for="top_filter_area">區域選擇</label><select id="top_filter_area"></select></div>
      <div class="top-filter"><label for="top_filter_engineer">工程師狀態</label><select id="top_filter_engineer"></select></div>
      <button class="btn-blue" type="button" onclick="location.href='/'">返回上一頁</button>
      <button class="btn-blue" type="button" onclick="loadAll()">重新整理</button>
      <button class="btn-green" type="button" onclick="openCreateModal()">新增案件</button>
      <button class="btn-gray" type="button" onclick="clearFilters()">清除篩選</button>
      <button class="btn-red" type="button" onclick="logout()">登出</button>
      <span id="sync_status" class="sync-status">尚未同步</span>
    </section>

    <section class="stats-grid">
      <div class="stat-card" data-stat-filter="today"><div class="stat-label">今日新增</div><div id="stat_today" class="stat-number">0</div></div>
      <div class="stat-card" data-stat-filter="unclaimed"><div class="stat-label">未領取</div><div id="stat_unclaimed" class="stat-number">0</div></div>
      <div class="stat-card" data-stat-filter="claimed"><div class="stat-label">已領取</div><div id="stat_claimed" class="stat-number">0</div></div>
      <div class="stat-card" data-stat-filter="done"><div class="stat-label">已完工</div><div id="stat_done" class="stat-number">0</div></div>
      <div class="stat-card" onclick="loadBuildingStatus(true)"><div class="stat-label">大樓狀態</div><div id="stat_building" class="stat-number">檢查中</div></div>
    </section>

    <section class="panel panel-case-board">
      <div class="case-top-grid">
        <div class="case-head-box">
          <h2 class="panel-title">案件總覽</h2>
          <div class="search-box"><label for="keyword_filter">關鍵字搜尋</label><input id="keyword_filter" placeholder="客戶 / 住址 / 電話"></div>
        </div>
        <section class="engineer-board">
          <div class="engineer-board-title">工程師狀態</div>
          <div id="engineer_board_content" class="engineer-board-content"><span class="engineer-board-pill">資料載入中</span></div>
        </section>
      </div>
      <div class="table-wrap">
        <table>

          <colgroup id="ticket_table_colgroup">
            <col style="width:5%">
            <col style="width:6%">
            <col style="width:7%">
            <col style="width:22%">
            <col style="width:10%">
            <col style="width:11%">
            <col style="width:7%">
            <col style="width:7%">
            <col style="width:16%">
            <col style="width:9%">
          </colgroup>
          <thead>
            <tr><th>區域</th><th>類型</th><th>客戶</th><th>住址</th><th>電話</th><th>約工時間</th><th>工程師</th><th>狀態</th><th>金額摘要</th><th>操作</th></tr>
            <tr class="filter-row"><th><select id="excel_filter_area"></select></th><th><select id="excel_filter_type"></select></th><th><select id="excel_filter_customer"></select></th><th><select id="excel_filter_address"></select></th><th><select id="excel_filter_phone"></select></th><th><select id="excel_filter_time"></select></th><th><select id="excel_filter_engineer"></select></th><th><select id="excel_filter_status"></select></th><th></th><th></th></tr>
          </thead>
          <tbody id="ticket_rows"><tr><td colspan="10">資料載入中...</td></tr></tbody>
        </table>
      </div>
    </section>
  </main>

  <div id="detail_modal" class="modal-mask"><div class="modal"><div class="modal-head"><div><div id="detail_title" class="modal-title">案件詳情</div><div id="detail_subtitle" class="modal-subtitle"></div></div><button class="modal-close" type="button" onclick="closeDetailModal()">關閉</button></div><div id="detail_body" class="detail-grid"></div><div class="modal-actions"><button class="btn-blue" type="button" onclick="assignSelectedTicket()">指派</button><button class="btn-orange" type="button" onclick="claimSelectedTicket()">領取</button><button class="btn-green" type="button" onclick="completeSelectedTicket()">完工</button><button class="btn-purple" type="button" onclick="alert('轉派功能下一階段接工程系統')">轉派</button><button class="btn-gray" type="button" onclick="alert('退件功能下一階段接退件流程')">退件</button><button class="btn-red" type="button" onclick="deleteSelectedTicket()">刪除</button></div></div></div>


  
<div id="create_modal" class="modal-mask">
  <div class="modal">
    <div class="modal-head">
      <div>
        <div class="modal-title">&#x65B0;&#x589E;&#x6848;&#x4EF6;</div>
        <div class="modal-subtitle">&#x5EFA;&#x7ACB;&#x6D3E;&#x5DE5;&#x6848;&#x4EF6;&#xFF0C;&#x91D1;&#x984D;&#x6B04;&#x4F4D;&#x6703;&#x4F9D;&#x6848;&#x4EF6;&#x985E;&#x578B;&#x5BEB;&#x5165;&#x660E;&#x7D30;&#x3002;</div>
      </div>
      <button class="modal-close" type="button" onclick="closeCreateModal()">&#x95DC;&#x9589;</button>
    </div>

    <div class="create-grid">
      <div class="field"><label>&#x5340;&#x57DF;</label><select id="new_area"></select></div>

      <div class="field">
        <label>&#x985E;&#x578B;</label>
        <select id="new_type">
          <option value="&#x88DD;&#x6A5F;">&#x88DD;&#x6A5F;</option>
          <option value="&#x7DAD;&#x4FEE;">&#x7DAD;&#x4FEE;</option>
          <option value="&#x9000;&#x6A5F;">&#x9000;&#x6A5F;</option>
          <option value="&#x5DE1;&#x6AA2;">&#x5DE1;&#x6AA2;</option>
          <option value="&#x5DE5;&#x7A0B;&#x65BD;&#x5DE5;">&#x5DE5;&#x7A0B;&#x65BD;&#x5DE5;</option>
        </select>
      </div>

      <div class="field"><label>&#x5DE5;&#x7A0B;&#x5E2B;</label><select id="new_engineer"></select></div>
      <div class="field"><label>&#x5BA2;&#x6236;&#x59D3;&#x540D;</label><input id="new_customer_name"></div>
      <div class="field"><label>&#x96FB;&#x8A71;</label><input id="new_phone"></div>
      <div class="field">
  <label>&#x5927;&#x6A13;&#x540D;&#x55AE;</label>
  <select id="new_building_no">
    <option value="">&#x8ACB;&#x5148;&#x9078;&#x64C7;&#x5340;&#x57DF;</option>
  </select>
</div>
      <div class="field full" id="create_address_field">
  <label>&#x4F4F;&#x5740;</label>
  <div class="address-helper-row">
    <input id="new_address" class="address-helper-input" placeholder="&#x53EF;&#x624B;&#x52D5;&#x8F38;&#x5165;&#x4F4F;&#x5740;">
    <select id="new_existing_customer_address" class="address-helper-select" onchange="applyCreateExistingCustomerAddress()">
      <option value="">&#x8ACB;&#x9078;&#x64C7;&#x5BA2;&#x6236;</option>
    </select>
  </div>
</div>
      <div class="field"><label>&#x7D04;&#x5DE5;&#x65E5;&#x671F;</label><input id="new_date" type="date"></div>
      <div class="field"><label>&#x7D04;&#x5DE5;&#x6642;&#x9593;</label><input id="new_time" type="time"></div>

      <div id="create_install_price_fields" class="field full create-price-panel">
        <div class="create-price-title">&#x88DD;&#x6A5F;&#x8CBB;&#x7528;&#x8A08;&#x7B97;</div>
        <div class="create-price-grid">
          <div class="field"><label>&#x5B89;&#x88DD;&#x8CBB;</label><input id="new_construction" value="1000"></div>
          <div class="field"><label>&#x62BC;&#x91D1;</label><input id="new_deposit" value="1000"></div>
          <div class="field"><label>&#x5176;&#x4ED6;&#x8CBB;&#x7528;1</label><input id="new_other_1" value="0"></div>
          <div class="field"><label>&#x5176;&#x4ED6;&#x8CBB;&#x7528;2</label><input id="new_other_2" value="0"></div>
          <div class="field"><label>&#x6708;&#x79DF;&#x8CBB;1</label><input id="new_monthly_1" value="350"></div>
          <div class="field"><label>&#x6708;&#x79DF;&#x8CBB;2</label><input id="new_monthly_2" value="0"></div>
          <div class="field"><label>&#x6708;&#x79DF;&#x8CBB;3</label><input id="new_monthly_3" value="0"></div>
          <div class="field"><label>&#x7E73;&#x8CBB;&#x6708;&#x6578;</label><input id="new_month_count" value="1"></div>
        </div>
        <div class="create-price-note">&#x7E3D;&#x91D1;&#x984D; = &#x5B89;&#x88DD;&#x8CBB; + &#x62BC;&#x91D1; + &#x5176;&#x4ED6;&#x8CBB;&#x7528;1 + &#x5176;&#x4ED6;&#x8CBB;&#x7528;2 +&#xFF08;&#x6708;&#x79DF;&#x8CBB;1 + &#x6708;&#x79DF;&#x8CBB;2 + &#x6708;&#x79DF;&#x8CBB;3&#xFF09;&#x00D7; &#x7E73;&#x8CBB;&#x6708;&#x6578;&#x3002;</div>
      </div>

      <div id="create_return_price_fields" class="field full create-price-panel" style="display:none">
        <div class="create-price-title">&#x9000;&#x6A5F;&#x8CBB;&#x7528;&#x8A08;&#x7B97;</div>
        <div class="create-price-grid">
          <div class="field"><label>&#x62BC;&#x91D1;</label><input id="new_return_deposit" value="1000"></div>
          <div class="field"><label>&#x9000;&#x9084;&#x91D1;&#x984D;</label><input id="new_refund_amount" value="0"></div>
          <div class="field"><label>&#x6263;&#x6B3E;&#x91D1;&#x984D;</label><input id="new_deduction_amount" value="0"></div>
          <div class="field"><label>&#x8A2D;&#x5099;&#x8CBB;</label><input id="new_device_fee" value="0"></div>
          <div class="field"><label>&#x6E05;&#x6F54;&#x8CBB;</label><input id="new_cleaning_fee" value="0"></div>
          <div class="field"><label>&#x5176;&#x4ED6;&#x8CBB;&#x7528;</label><input id="new_return_other" value="0"></div>
        </div>
        <div class="create-price-note">&#x9000;&#x6A5F;&#x7D50;&#x7B97;&#x91D1;&#x984D; = &#x62BC;&#x91D1; + &#x9000;&#x9084;&#x91D1;&#x984D; - &#x6263;&#x6B3E;&#x91D1;&#x984D; - &#x8A2D;&#x5099;&#x8CBB; - &#x6E05;&#x6F54;&#x8CBB; - &#x5176;&#x4ED6;&#x8CBB;&#x7528;&#x3002;</div>
      </div>

      <div class="field full"><label>&#x6848;&#x4EF6;&#x8AAA;&#x660E;</label><textarea id="new_description"></textarea></div>
    </div>

    <div class="modal-actions">
      <button class="btn-gray" type="button" onclick="closeCreateModal()">&#x53D6;&#x6D88;</button>
      <button class="btn-green" type="button" onclick="createTicket()">&#x5EFA;&#x7ACB;&#x6848;&#x4EF6;</button>
    </div>
  </div>
</div>

<script>
  const AREAS = ["全部","東區","北區","北台南","仁德","永康","安平","南高","北高"];
  const ENGINEER_DEPARTMENTS = ["東區","北區","北台南","仁德","永康","安平","南高","北高","維修部","工程部","專案部"];
  let allTickets = [];
  let buildingDirectory = [];
  let engineerDirectory = [];
  let statFilter = "";
  let selectedTicketId = null;
  let selectedTicket = null;

  
function zh(hexText) {
    return String(hexText || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .map(function (x) { return String.fromCharCode(parseInt(x, 16)); })
      .join("");
  }


  function byId(id) { return document.getElementById(id); }
  function escapeHtml(value) { return String(value ?? "").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;"); }
  function money(value) { const n = Number(value || 0); return "NT$ " + n.toLocaleString("zh-TW"); }
  function val(id) { const el = byId(id); return el ? String(el.value || "") : ""; }

  function setSelectOptions(id, values, firstText) {
    const el = byId(id);
    if (!el) return;
    const current = el.value || "";
    const list = Array.from(new Set(values.filter(v => String(v || "").trim() !== "")));
    el.innerHTML = "";
    const first = document.createElement("option");
    first.value = "";
    first.textContent = firstText || "全部";
    el.appendChild(first);
    list.forEach(function (value) { const opt = document.createElement("option"); opt.value = value; opt.textContent = value; el.appendChild(opt); });
    if (list.includes(current)) el.value = current;
  }

  function initStaticSelects() {
    [byId("top_filter_area"), byId("new_area")].forEach(function (el) {
      if (!el) return;
      el.innerHTML = "";
      AREAS.forEach(function (area) { if (el.id === "new_area" && area === "全部") return; const opt = document.createElement("option"); opt.value = area; opt.textContent = area; el.appendChild(opt); });
    });
    if (byId("top_filter_engineer")) byId("top_filter_engineer").innerHTML = "<option value='全部'>全部</option><option value='已派工'>已派工</option><option value='未派工'>未派工</option>";
    if (byId("new_engineer")) byId("new_engineer").innerHTML = "<option value=''>未指派</option>";
  }

  function buildingNameText(item) {
    const no = String(item.building_no || "").trim();
    if (!no) return "";
    if (no.indexOf("HOUSE") === 0 || String(item.site_type || "") === "house") return "透天";
    const found = buildingDirectory.find(b => String(b.building_no || "").trim() === no);
    return found ? String(found.name || no) : no;
  }

  function mergedAddressText(item) {
    const building = buildingNameText(item);
    const address = String(item.service_address || item.address || "").trim();
    if (!building) return address || "-";
    if (!address) return building;
    if (address.indexOf(building) === 0) return address;
    if (building === "透天") return building + "｜" + address;
    return building + address;
  }

  function appointmentText(item) { const d = item.appointment_date || ""; const t = item.appointment_time || ""; if (!d && !t) return "-"; return [d, t].filter(Boolean).join(" "); }
  function engineerText(item) { return item.assigned_engineer || "未指派"; }
  function statusClass(status) { if (status === "待派工" || status === "未派工") return "pill pill-wait"; if (status === "已領取") return "pill pill-claim"; if (status === "已完工") return "pill pill-done"; return "pill pill-default"; }
function amountText(item) {
    if (item.install_detail && Number(item.install_detail.total_amount || 0) > 0) {
      return "\u88dd\u6a5f " + money(item.install_detail.total_amount);
    }

    if (item.return_detail) {
      const ret = item.return_detail;
      const total =
        Number(ret.deposit_amount || 0) +
        Number(ret.refund_amount || 0) -
        Number(ret.deduction_amount || 0) -
        Number(ret.device_fee || 0) -
        Number(ret.cleaning_fee || 0) -
        Number(ret.other_fee || 0);

      return "\u9000\u6a5f " + money(total);
    }

    return "-";
  }

  function todayKey() { const d = new Date(); return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }

  function baseFilteredTickets() {
    const area = val("top_filter_area") || "全部";
    const engineerState = val("top_filter_engineer") || "全部";
    const keyword = val("keyword_filter").trim().toLowerCase();
    return allTickets.filter(function (item) {
      if (area !== "全部" && String(item.dispatch_area || "") !== area) return false;
      if (statFilter === "today") { const created = String(item.created_at || "").slice(0, 10); const appt = String(item.appointment_date || "").slice(0, 10); if (created !== todayKey() && appt !== todayKey()) return false; }
      if (statFilter === "unclaimed" && !(item.status === "待派工" || item.status === "未派工")) return false;
      if (statFilter === "claimed" && item.status !== "已領取") return false;
      if (statFilter === "done" && item.status !== "已完工") return false;
      if (engineerState === "未派工") { if (item.assigned_engineer) return false; } else if (engineerState === "已派工") { if (!item.assigned_engineer) return false; } else if (engineerState !== "全部") { if (String(item.assigned_engineer || "") !== engineerState) return false; }
      if (keyword) { const hay = [item.customer_name,item.contact_name,item.contact_phone,item.customer_phone,item.service_address,mergedAddressText(item),item.ticket_no].join(" ").toLowerCase(); if (!hay.includes(keyword)) return false; }
      return true;
    });
  }

  function excelCellValue(item, key) { if (key === "area") return item.dispatch_area || ""; if (key === "type") return item.case_type || ""; if (key === "customer") return item.customer_name || ""; if (key === "address") return mergedAddressText(item); if (key === "phone") return item.contact_phone || item.customer_phone || ""; if (key === "time") return appointmentText(item); if (key === "engineer") return engineerText(item); if (key === "status") return item.status || ""; return ""; }
  function refreshExcelOptions(data) { ["area","type","customer","address","phone","time","engineer","status"].forEach(function (key) { setSelectOptions("excel_filter_" + key, data.map(item => excelCellValue(item, key)), "全部"); }); }
  function applyExcelFilters(data) { return data.filter(function (item) { return ["area","type","customer","address","phone","time","engineer","status"].every(function (key) { const wanted = val("excel_filter_" + key); if (!wanted) return true; return excelCellValue(item, key) === wanted; }); }); }

  function updateStats() {
    const area = val("top_filter_area") || "全部";
    const scoped = allTickets.filter(item => area === "全部" || String(item.dispatch_area || "") === area);
    byId("stat_today").textContent = scoped.filter(function (item) { const created = String(item.created_at || "").slice(0, 10); const appt = String(item.appointment_date || "").slice(0, 10); return created === todayKey() || appt === todayKey(); }).length;
    byId("stat_unclaimed").textContent = scoped.filter(item => item.status === "待派工" || item.status === "未派工").length;
    byId("stat_claimed").textContent = scoped.filter(item => item.status === "已領取").length;
    byId("stat_done").textContent = scoped.filter(item => item.status === "已完工").length;
  }

  function updateEngineerBoard() {
    const box = byId("engineer_board_content");
    if (!box) return;
    const area = val("top_filter_area") || "全部";
    const selected = val("top_filter_engineer") || "全部";
    const scopedTickets = allTickets.filter(item => area === "全部" || String(item.dispatch_area || "") === area);
    let engineers = engineerDirectory.filter(function (e) {
      if (!e.name) return false;
      if (!ENGINEER_DEPARTMENTS.includes(e.department)) return false;
      if (area === "全部") return true;
      return e.department === area;
    });
    function activeCount(name) {
      return scopedTickets.filter(function (item) {
        if (String(item.assigned_engineer || "") !== name) return false;
        if (item.status === "已完工" || item.status === "待派工" || item.status === "未派工") return false;
        return true;
      }).length;
    }
    let stats = engineers.map(function (e) {
      const workStatus = e.work_status || e.leave_status || e.employment_status || "在職";
      return { name:e.name, department:e.department || "", active:activeCount(e.name), work_status:workStatus };
    });
    if (selected === "已派工") stats = stats.filter(x => x.active > 0);
    else if (selected === "未派工") stats = stats.filter(x => x.active === 0);
    else if (selected !== "全部") stats = stats.filter(x => x.name === selected);
    if (!stats.length) { box.innerHTML = "<span class='engineer-board-pill'><span class='engineer-board-pill-name'>沒有符合條件</span><span class='engineer-board-pill-meta'>0 件</span></span>"; return; }
    box.innerHTML = stats.map(function (x) {
      const isOff = x.work_status && x.work_status !== "在職";
      const countText = isOff && x.active === 0 ? x.work_status : (x.active + " 件");
      const cls = isOff ? "engineer-board-pill engineer-board-pill-off" : "engineer-board-pill";
      const nameText = x.name + (x.department ? "｜" + x.department : "");
      return "<span class='" + cls + "'><span class='engineer-board-pill-name'>" + escapeHtml(nameText) + "</span><span class='engineer-board-pill-meta'>" + escapeHtml(countText) + "</span></span>";
    }).join("");
  }

  function renderTable() {
    const tbody = byId("ticket_rows");
    if (!tbody) return;
    const base = baseFilteredTickets();
    refreshExcelOptions(base);
    const data = applyExcelFilters(base);
    if (!data.length) { tbody.innerHTML = "<tr><td colspan='10'>目前沒有符合條件的案件。</td></tr>"; return; }
    tbody.innerHTML = data.map(function (item) { return `<tr onclick="openDetailModal(${Number(item.id || 0)})"><td>${escapeHtml(excelCellValue(item, "area"))}</td><td>${escapeHtml(excelCellValue(item, "type"))}</td><td>${escapeHtml(excelCellValue(item, "customer"))}</td><td class="address-cell">${escapeHtml(excelCellValue(item, "address"))}</td><td>${escapeHtml(excelCellValue(item, "phone"))}</td><td>${escapeHtml(excelCellValue(item, "time"))}</td><td>${escapeHtml(excelCellValue(item, "engineer"))}</td><td><span class="${statusClass(item.status)}">${escapeHtml(excelCellValue(item, "status"))}</span></td><td>${escapeHtml(amountText(item))}</td><td><button class="delete-button" type="button" onclick="event.stopPropagation(); deleteTicket(${Number(item.id || 0)})">刪除</button></td></tr>`; }).join("");
  }

  function renderAll() { updateStats(); updateEngineerBoard(); renderTable(); }
  async function loadTickets() { const res = await fetch("/api/tickets?ts=" + Date.now(), {cache:"no-store"}); if (!res.ok) throw new Error("tickets api failed"); const data = await res.json(); allTickets = Array.isArray(data) ? data : []; }
async function loadBuildings() {
    try {
      const res = await fetch("/api/admin/buildings?ts=" + Date.now(), {cache:"no-store"});
      if (!res.ok) return;

      const data = await res.json();
      buildingDirectory = Array.isArray(data) ? data : [];

      updateCreateBuildingOptions(false);
    } catch (err) {
      buildingDirectory = [];
      updateCreateBuildingOptions(true);
    }
  }

  async function loadEngineers() { try { const res = await fetch("/api/admin/engineers?ts=" + Date.now(), {cache:"no-store"}); if (!res.ok) return; const data = await res.json(); engineerDirectory = Array.isArray(data) ? data.map(e => ({employee_no:e.employee_no || e.staff_code || "", staff_code:e.staff_code || e.employee_no || "", name:e.name || e.display_name || "", department:e.department || "", position_title:e.position_title || "", employment_status:e.employment_status || "", work_status:e.work_status || e.leave_status || e.employment_status || "在職", leave_status:e.leave_status || ""})).filter(e => ENGINEER_DEPARTMENTS.includes(e.department)) : []; const top = byId("top_filter_engineer"); const create = byId("new_engineer"); if (top) { const current = top.value || "全部"; top.innerHTML = "<option value='全部'>全部</option><option value='已派工'>已派工</option><option value='未派工'>未派工</option>" + engineerDirectory.map(e => "<option value='" + escapeHtml(e.name) + "'>" + escapeHtml(e.name + (e.department ? "｜" + e.department : "")) + "</option>").join(""); top.value = current; } if (create) create.innerHTML = "<option value=''>未指派</option>" + engineerDirectory.map(e => "<option value='" + escapeHtml(e.name) + "'>" + escapeHtml(e.name + (e.department ? "｜" + e.department : "")) + "</option>").join(""); } catch (err) { engineerDirectory = []; } }


  function normalizeNoticeItems(data) {
    if (Array.isArray(data)) return data;

    if (data && Array.isArray(data.notices)) return data.notices;
    if (data && Array.isArray(data.items)) return data.items;
    if (data && Array.isArray(data.messages)) return data.messages;

    return [];
  }

  function noticeTextFromItem(item) {
    if (typeof item === "string") return item;
    if (!item) return "";
    return item.message || item.text || item.content || "";
  }

function renderNoticeListFromItems(items) {
    const box = byId("notice_list");
    if (!box) return;

    const list = Array.isArray(items)
      ? items.map(noticeTextFromItem).map(x => String(x || "").trim()).filter(Boolean)
      : [];

    if (!list.length) {
      box.innerHTML = "<div class='notice-row'><div class='notice-text'>\u76ee\u524d\u6c92\u6709\u7dca\u6025\u901a\u77e5\u3002</div><div></div></div>";
      return;
    }

    box.innerHTML = list.map(function (text, index) {
      return `
        <div class="notice-row">
          <div class="notice-text">${escapeHtml((index + 1) + ". " + text)}</div>
          <button type="button" onclick="deleteNotice(${index})">\u522a\u9664</button>
        </div>
      `;
    }).join("");
  }



  const NOTICE_DELETE_TEXT = "刪除";

async function loadNotices() {
    const box = byId("notice_list");
    if (!box) return;

    try {
      const res = await fetch("/api/notices/emergency?ts=" + Date.now(), { cache: "no-store" });

      if (!res.ok) {
        box.innerHTML = "<div class='notice-row'><div class='notice-text'>\u901a\u77e5\u8b80\u53d6\u5931\u6557\uff1a" + res.status + "</div><div></div></div>";
        return;
      }

      const data = await res.json();
      renderNoticeListFromItems(normalizeNoticeItems(data));
    } catch (err) {
      box.innerHTML = "<div class='notice-row'><div class='notice-text'>\u901a\u77e5\u8b80\u53d6\u932f\u8aa4\uff1a" + escapeHtml(String(err && err.message ? err.message : err)) + "</div><div></div></div>";
    }
  }


async function sendNotice() {
    const input = byId("notice_input");
    const message = input ? input.value.trim() : "";

    if (!message) {
      alert("\u8acb\u5148\u8f38\u5165\u901a\u77e5\u5167\u5bb9");
      return;
    }

    try {
      const res = await fetch("/api/notices/emergency", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ message: message })
      });

      if (!res.ok) {
        alert("\u901a\u77e5\u9001\u51fa\u5931\u6557\uff1a" + res.status);
        return;
      }

      const data = await res.json().catch(function () { return null; });

      input.value = "";

      if (data) {
        renderNoticeListFromItems(normalizeNoticeItems(data));
      } else {
        await loadNotices();
      }
    } catch (err) {
      alert("\u901a\u77e5\u9001\u51fa\u932f\u8aa4\uff1a" + String(err && err.message ? err.message : err));
    }
  }

async function deleteNotice(index) {
    try {
      const res = await fetch("/api/notices/emergency", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ delete_index: index })
      });

      if (!res.ok) {
        alert("\u901a\u77e5\u522a\u9664\u5931\u6557\uff1a" + res.status);
        return;
      }

      const data = await res.json().catch(function () { return null; });

      if (data) {
        renderNoticeListFromItems(normalizeNoticeItems(data));
      } else {
        await loadNotices();
      }
    } catch (err) {
      alert("\u901a\u77e5\u522a\u9664\u932f\u8aa4\uff1a" + String(err && err.message ? err.message : err));
    }
  }

  function clearNoticeInput() { const input = byId("notice_input"); if (input) input.value = ""; }
  async function loadBuildingStatus(showAlert) { const card = byId("stat_building"); try { const res = await fetch("/api/admin/buildings/status?ts=" + Date.now(), {cache:"no-store"}); if (!res.ok) { if (card) card.textContent = "讀取失敗"; return; } const data = await res.json(); const bad = data.filter(x => x.status !== "正常"); if (card) card.textContent = bad.length ? bad.length + " 棟異常" : "一切正常"; if (showAlert) alert(!bad.length ? "目前大樓狀態一切正常。" : bad.map(x => x.name + "｜" + x.status).join("\n")); } catch (err) { if (card) card.textContent = "檢查失敗"; } }
  async function loadAll() { try { byId("sync_status").textContent = "同步中..."; await Promise.all([loadBuildings(), loadEngineers(), loadNotices()]); await loadTickets(); renderAll(); await loadBuildingStatus(false); byId("sync_status").textContent = "最後同步：" + new Date().toLocaleTimeString("zh-TW"); } catch (err) { byId("sync_status").textContent = "同步失敗"; console.error(err); } }
  function clearFilters() { statFilter = ""; document.querySelectorAll(".stat-card").forEach(el => el.classList.remove("active")); byId("top_filter_area").value = "全部"; byId("top_filter_engineer").value = "全部"; byId("keyword_filter").value = ""; ["area","type","customer","address","phone","time","engineer","status"].forEach(function (key) { const el = byId("excel_filter_" + key); if (el) el.value = ""; }); renderAll(); }
  function openDetailModal(id) { selectedTicketId = id; selectedTicket = allTickets.find(x => Number(x.id) === Number(id)) || null; if (!selectedTicket) return; byId("detail_title").textContent = selectedTicket.ticket_no || "案件詳情"; byId("detail_subtitle").textContent = (selectedTicket.case_type || "-") + "｜" + (selectedTicket.customer_name || "-") + "｜" + (selectedTicket.status || "-"); byId("detail_body").innerHTML = detailCards(selectedTicket); byId("detail_modal").classList.add("active"); }
  function closeDetailModal() { byId("detail_modal").classList.remove("active"); }

  function displayDescriptionText(item) {
    const raw = String((item && item.description) || "").trim();

    if (!raw) return "";

    if (raw.indexOf("?") >= 0 && raw.indexOf("http") < 0) {
      return raw
        .split("?")
        .map(function (x) { return x.trim(); })
        .filter(Boolean)
        .join("\uFF5C");
    }

    return raw;
  }


function otherNoticeText(item) {
    const values = [
      item && item.attention_note,
      item && item.notice_note,
      item && item.special_note,
      item && item.transfer_note,
      item && item.reject_note,
      item && item.internal_note
    ];

    const cleaned = values
      .map(function (x) { return String(x || "").trim(); })
      .filter(function (x) { return x.length > 0; });

    if (!cleaned.length) return "\u76EE\u524D\u7121\u5176\u4ED6\u6CE8\u610F\u4E8B\u9805\u3002";

    return cleaned.join("\n");
  }


  
function detailCardHtml(label, html, cls) {
    return `<div class="detail-card ${cls || ""}">
      <div class="detail-label">${escapeHtml(label)}</div>
      <div class="detail-value">${html || "-"}</div>
    </div>`;
  }


  function detailCard(label, value, cls) { return `<div class="detail-card ${cls || ""}"><div class="detail-label">${escapeHtml(label)}</div><div class="detail-value">${escapeHtml(value || "-")}</div></div>`; }
  
function amountDetailBoxHtml(item) {
    const install = item && item.install_detail ? item.install_detail : null;
    const ret = item && item.return_detail ? item.return_detail : null;

    function n(value) {
      return Number(value || 0);
    }

    function moneyPlain(value) {
      return n(value).toLocaleString("zh-TW");
    }

    function box(label, value) {
      return `<div class="detail-amount-field">
        <div class="detail-amount-label">${escapeHtml(label)}</div>
        <div class="detail-amount-input">${escapeHtml(moneyPlain(value))}</div>
      </div>`;
    }

    function totalBox(label, value) {
      return `<div class="detail-amount-total">
        <div class="detail-amount-label">${escapeHtml(label)}</div>
        <div class="detail-amount-total-value">${escapeHtml(moneyPlain(value))}</div>
      </div>`;
    }

    if (install) {
      const installFee = n(install.construction_fee || install.install_fee);
      const deposit = n(install.deposit_amount);
      const otherFee1 = n(install.other_fee_1);
      const otherFee2 = n(install.other_fee_2);

      const monthly1 = n(install.monthly_fee_1 || install.monthly_fee || install.monthly_amount_1);
      const monthly2 = n(install.monthly_fee_2 || install.monthly_amount_2);
      const monthly3 = n(install.monthly_fee_3 || install.monthly_amount_3);
      const months = Math.max(1, Number(install.month_count || install.pay_month_count || 1));

      const monthlyTotal = (monthly1 + monthly2 + monthly3) * months;
      const total = installFee + deposit + otherFee1 + otherFee2 + monthlyTotal;

      return `<div class="detail-amount-board">
        <div class="detail-amount-title">${zh("8CBB 7528 8A08 7B97")}</div>

        <div class="detail-amount-row detail-amount-top">
          ${box(zh("5B89 88DD 8CBB"), installFee)}
          <span class="detail-amount-symbol">+</span>
          ${box(zh("62BC 91D1"), deposit)}
          <span class="detail-amount-symbol">+</span>
          ${box(zh("5176 4ED6 8CBB 7528 0031"), otherFee1)}
          <span class="detail-amount-symbol">+</span>
          ${box(zh("5176 4ED6 8CBB 7528 0032"), otherFee2)}
        </div>

        <div class="detail-amount-formula">
          <span class="detail-amount-symbol">+</span>
          <span class="detail-amount-symbol">(</span>
          ${box(zh("6708 79DF 8CBB 0031"), monthly1)}
          <span class="detail-amount-symbol">+</span>
          ${box(zh("6708 79DF 8CBB 0032"), monthly2)}
          <span class="detail-amount-symbol">+</span>
          ${box(zh("6708 79DF 8CBB 0033"), monthly3)}
          <span class="detail-amount-symbol">)</span>
          <span class="detail-amount-symbol">&times;</span>
          ${box(zh("7E73 8CBB 6708 6578"), months)}
          <span class="detail-amount-symbol">=</span>
          ${totalBox(zh("7E3D 91D1 984D 0020 002F 0020 5E33 55AE 91D1 984D"), total)}
        </div>

        <div class="detail-amount-note">${zh("7E3D 91D1 984D 003D 5B89 88DD 8CBB 002B 62BC 91D1 002B 5176 4ED6 8CBB 7528 0031 002B 5176 4ED6 8CBB 7528 0032 002B FF08 6708 79DF 8CBB 0031 002B 6708 79DF 8CBB 0032 002B 6708 79DF 8CBB 0033 FF09 00D7 7E73 8CBB 6708 6578 3002")}</div>
      </div>`;
    }

    if (ret) {
      const deposit = n(ret.deposit_amount);
      const refund = n(ret.refund_amount);
      const deduction = n(ret.deduction_amount);
      const device = n(ret.device_fee);
      const cleaning = n(ret.cleaning_fee);
      const other = n(ret.other_fee);

      const total = deposit + refund - deduction - device - cleaning - other;

      return `<div class="detail-amount-board">
        <div class="detail-amount-title">${zh("9000 6A5F 8CBB 7528 8A08 7B97")}</div>

        <div class="detail-amount-row detail-amount-top">
          ${box(zh("62BC 91D1"), deposit)}
          <span class="detail-amount-symbol">+</span>
          ${box(zh("9000 9084 91D1 984D"), refund)}
          <span class="detail-amount-symbol">-</span>
          ${box(zh("6263 6B3E 91D1 984D"), deduction)}
        </div>

        <div class="detail-amount-formula">
          <span class="detail-amount-symbol">-</span>
          ${box(zh("8A2D 5099 8CBB"), device)}
          <span class="detail-amount-symbol">-</span>
          ${box(zh("6E05 6F54 8CBB"), cleaning)}
          <span class="detail-amount-symbol">-</span>
          ${box(zh("5176 4ED6 8CBB 7528"), other)}
          <span class="detail-amount-symbol">=</span>
          ${totalBox(zh("9000 6A5F 7D50 7B97 91D1 984D"), total)}
        </div>

        <div class="detail-amount-note">${zh("9000 6A5F 7D50 7B97 91D1 984D 003D 62BC 91D1 002B 9000 9084 91D1 984D 002D 6263 6B3E 91D1 984D 002D 8A2D 5099 8CBB 002D 6E05 6F54 8CBB 002D 5176 4ED6 8CBB 7528 3002")}</div>
      </div>`;
    }

    return `<div class="detail-amount-board">
      <div class="detail-amount-title">${zh("8CBB 7528 8A08 7B97")}</div>
      <div class="detail-amount-empty">${zh("76EE 524D 6C92 6709 91D1 984D 8CC7 6599 3002")}</div>
    </div>`;
  }


  function detailCards(item) {
    return [
      detailCard(zh("5340 57DF"), item.dispatch_area),
      detailCard(zh("985E 578B"), item.case_type),
      detailCard(zh("72C0 614B"), item.status),
      detailCard(zh("5BA2 6236"), item.customer_name),
      detailCard(zh("96FB 8A71"), item.contact_phone || item.customer_phone),
      detailCard(zh("5DE5 7A0B 5E2B"), engineerText(item)),
      detailCard(zh("4F4F 5740"), mergedAddressText(item), "full"),
      detailCard(zh("7D04 5DE5 6642 9593"), appointmentText(item)),
      detailCardHtml(zh("91D1 984D 660E 7D30"), amountDetailBoxHtml(item), "full detail-card-amount"),
      detailCard(zh("6848 4EF6 8AAA 660E"), displayDescriptionText(item), "full"),
      detailCard(zh("5176 4ED6 6CE8 610F 4E8B 9805"), otherNoticeText(item), "full")
    ].join("");
  }
  async function assignTicket(id, engineerName) { if (!id || !engineerName) return; const res = await fetch("/api/tickets/" + id + "/claim", {method:"PATCH", headers:{"Content-Type":"application/json"}, body:JSON.stringify({assigned_engineer:engineerName})}); if (!res.ok) { alert("指派失敗"); return; } await loadAll(); if (byId("detail_modal").classList.contains("active")) openDetailModal(id); }
  async function updateTicketStatus(id, status) { if (!id) return; const res = await fetch("/api/tickets/" + id + "/status", {method:"PATCH", headers:{"Content-Type":"application/json"}, body:JSON.stringify({status:status})}); if (!res.ok) { alert("狀態更新失敗"); return; } await loadAll(); if (byId("detail_modal").classList.contains("active")) openDetailModal(id); }
  function assignSelectedTicket() { if (!selectedTicketId) return; const names = engineerDirectory.map(e => e.name).filter(Boolean); const current = selectedTicket ? (selectedTicket.assigned_engineer || "") : ""; const name = prompt("請輸入工程師姓名：\n" + names.join("、"), current); if (!name) return; assignTicket(selectedTicketId, name.trim()); }
  function claimSelectedTicket() { if (!selectedTicketId) return; const current = selectedTicket ? selectedTicket.assigned_engineer : ""; if (current) { updateTicketStatus(selectedTicketId, "已領取"); return; } assignSelectedTicket(); }
  function completeSelectedTicket() { if (!selectedTicketId) return; updateTicketStatus(selectedTicketId, "已完工"); }
  async function deleteTicket(id) { if (!id) return; if (!confirm("確認刪除此案件？")) return; const res = await fetch("/api/tickets/" + id, {method:"DELETE"}); if (!res.ok) { alert("刪除失敗"); return; } closeDetailModal(); await loadAll(); }
  function deleteSelectedTicket() { if (!selectedTicketId) return; deleteTicket(selectedTicketId); }
  
function syncCreatePriceFields() {
    const caseType = val("new_type");
    const installPanel = byId("create_install_price_fields");
    const returnPanel = byId("create_return_price_fields");

    if (installPanel) installPanel.style.display = caseType === "\u88dd\u6a5f" ? "" : "none";
    if (returnPanel) returnPanel.style.display = caseType === "\u9000\u6a5f" ? "" : "none";

    updateCreateCustomerAddressOptions(false);
  }




function updateCreateBuildingOptions(clearCurrent) {
    const area = val("new_area");
    const select = byId("new_building_no");
    if (!select) return;

    const current = clearCurrent ? "" : String(select.value || "");

    const items = Array.isArray(buildingDirectory)
      ? buildingDirectory.filter(function (b) {
          const bArea = String(b.area || b.dispatch_area || "").trim();
          return !area || bArea === area;
        })
      : [];

    select.innerHTML = "";

    const empty = document.createElement("option");
    empty.value = "";
    empty.textContent = area ? "\u8acb\u9078\u64c7\u5927\u6a13" : "\u8acb\u5148\u9078\u64c7\u5340\u57df";
    select.appendChild(empty);

    const house = document.createElement("option");
    house.value = "HOUSE";
    house.textContent = "\u900f\u5929";
    select.appendChild(house);

    items.forEach(function (b) {
      const no = String(b.building_no || b.id || "").trim();
      const name = String(b.name || b.building_name || no || "").trim();
      const addr = String(b.display_address || b.address || b.raw_address || "").trim();

      if (!no && !name) return;

      const opt = document.createElement("option");
      opt.value = no || name;
      opt.textContent = name || no;
      select.appendChild(opt);
    });

    if (current && Array.from(select.options).some(opt => opt.value === current)) {
      select.value = current;
    } else {
      select.value = "";
    }
  }

function updateCreateAddressDatalist() {
    const addressInput = byId("new_address");
    const list = byId("new_existing_address_list");
    if (!addressInput || !list) return;

    const buildingValue = String(val("new_building_no") || "").trim();
    const buildingName = typeof selectedCreateBuildingName === "function"
      ? selectedCreateBuildingName()
      : "";

    addressInput.setAttribute("list", "new_existing_address_list");
    addressInput.placeholder = "\u53ef\u624b\u52d5\u8f38\u5165\uff0c\u4e5f\u53ef\u4e0b\u62c9\u9078\u64c7\u65e2\u6709\u4f4f\u5740";

    list.innerHTML = "";

    const seen = new Set();

    (Array.isArray(allTickets) ? allTickets : []).forEach(function (item) {
      const itemBuildingNo = String(item.building_no || "").trim();
      const serviceAddress = String(item.service_address || "").trim();
      const internalNote = String(item.internal_note || "").trim();

      if (!serviceAddress) return;

      let matched = true;

      if (buildingValue) {
        matched =
          itemBuildingNo === buildingValue ||
          itemBuildingNo === buildingName ||
          (buildingName && serviceAddress.indexOf(buildingName) !== -1) ||
          (buildingValue && serviceAddress.indexOf(buildingValue) !== -1) ||
          (buildingName && internalNote.indexOf(buildingName) !== -1) ||
          (buildingValue && internalNote.indexOf(buildingValue) !== -1);
      }

      if (!matched) return;

      const customer = String(item.customer_name || item.contact_name || "").trim();
      const phone = String(item.contact_phone || "").trim();

      const key = customer + "|" + phone + "|" + serviceAddress;
      if (seen.has(key)) return;
      seen.add(key);

      const opt = document.createElement("option");
      opt.value = serviceAddress;

      const labelParts = [];
      if (customer) labelParts.push(customer);
      if (phone) labelParts.push(phone);
      labelParts.push(serviceAddress);

      opt.label = labelParts.join("\uff5c");
      opt.dataset.customerName = customer;
      opt.dataset.phone = phone;

      list.appendChild(opt);
    });
  }

function applyCreateAddressDatalistSelection() {
    const addressInput = byId("new_address");
    const list = byId("new_existing_address_list");
    if (!addressInput || !list) return;

    const value = String(addressInput.value || "").trim();
    if (!value) return;

    const opt = Array.from(list.options).find(function (o) {
      return String(o.value || "").trim() === value;
    });

    if (!opt) return;

    const customer = String(opt.dataset.customerName || "").trim();
    const phone = String(opt.dataset.phone || "").trim();

    if (customer && byId("new_customer_name")) byId("new_customer_name").value = customer;
    if (phone && byId("new_phone")) byId("new_phone").value = phone;
  }

function applyCreateBuildingAddress() {
    // ???????????????????????????
    updateCreateCustomerAddressOptions(true);
  }



function selectedCreateBuildingName() {
    const select = byId("new_building_no");
    if (!select || !select.selectedOptions || !select.selectedOptions.length) return "";

    const opt = select.selectedOptions[0];
    return String(opt.dataset.buildingName || opt.textContent || opt.value || "").split("\uff5c")[0].split("|")[0].trim();
  }


function updateCreateCustomerAddressOptions(clearCurrent) {
    const select = byId("new_existing_customer_address");
    if (!select) return;

    const buildingValue = String(val("new_building_no") || "").trim();
    const buildingName = typeof selectedCreateBuildingName === "function" ? selectedCreateBuildingName() : "";

    select.innerHTML = "";

    const empty = document.createElement("option");
    empty.value = "";
    empty.textContent = "\u8acb\u9078\u64c7\u5ba2\u6236";
    select.appendChild(empty);

    const seen = new Set();

    (Array.isArray(allTickets) ? allTickets : []).forEach(function (item) {
      const itemBuildingNo = String(item.building_no || "").trim();
      const serviceAddress = String(item.service_address || "").trim();
      const internalNote = String(item.internal_note || "").trim();

      if (!serviceAddress) return;

      let matched = true;

      if (buildingValue) {
        matched =
          itemBuildingNo === buildingValue ||
          itemBuildingNo === buildingName ||
          (buildingName && serviceAddress.indexOf(buildingName) !== -1) ||
          (buildingValue && serviceAddress.indexOf(buildingValue) !== -1) ||
          (buildingName && internalNote.indexOf(buildingName) !== -1) ||
          (buildingValue && internalNote.indexOf(buildingValue) !== -1);
      }

      if (!matched) return;

      const customer = String(item.customer_name || item.contact_name || "").trim();
      const phone = String(item.contact_phone || "").trim();

      const key = customer + "|" + phone + "|" + serviceAddress;
      if (seen.has(key)) return;
      seen.add(key);

      const opt = document.createElement("option");
      opt.value = serviceAddress;
      opt.dataset.customerName = customer;
      opt.dataset.phone = phone;

      const labelParts = [];
      if (customer) labelParts.push(customer);
      if (phone) labelParts.push(phone);
      labelParts.push(serviceAddress);

      opt.textContent = labelParts.join("\uff5c");
      select.appendChild(opt);
    });

    select.value = "";
  }


function applyCreateExistingCustomerAddress() {
    const select = byId("new_existing_customer_address");
    const addressInput = byId("new_address");

    if (!select || !addressInput) return;

    const opt = select.selectedOptions && select.selectedOptions.length
      ? select.selectedOptions[0]
      : null;

    if (!opt || !opt.value) return;

    addressInput.value = opt.value;

    const customer = String(opt.dataset.customerName || "").trim();
    const phone = String(opt.dataset.phone || "").trim();

    if (customer && byId("new_customer_name")) byId("new_customer_name").value = customer;
    if (phone && byId("new_phone")) byId("new_phone").value = phone;

    // ?????????????
    select.value = "";
  }


function openCreateModal() {
    updateCreateBuildingOptions(false);
    syncCreatePriceFields();
    updateCreateCustomerAddressOptions(false);
    byId("create_modal").classList.add("active");
  }



  function closeCreateModal() { byId("create_modal").classList.remove("active"); }
  function numeric(id) { return Number(String(val(id) || "0").replace(/[^\d.-]/g, "")) || 0; }
async function createTicket() {
    const caseType = val("new_type");
    const isInstall = caseType === "\u88dd\u6a5f";

    if (!isInstall) {
      applyCreateExistingCustomerAddress();
    }

    const customerName = val("new_customer_name").trim();
    const phone = val("new_phone").trim();
    const address = isInstall
      ? val("new_address").trim()
      : (val("new_existing_customer_address") || val("new_address")).trim();

    if (!customerName || !phone || !address) {
      alert("\u8acb\u586b\u5beb\u5ba2\u6236\u59d3\u540d\u3001\u96fb\u8a71\u8207\u4f4f\u5740\u3002");
      return;
    }

    const payload = {
      dispatch_area: val("new_area"),
      case_type: caseType,
      customer_name: customerName,
      contact_name: customerName,
      contact_phone: phone,
      service_address: address,
      appointment_date: val("new_date") || null,
      appointment_time: val("new_time") || null,
      assigned_engineer: val("new_engineer") || null,
      building_no: val("new_building_no") || "",
      description: val("new_description"),
      internal_note: val("new_building_no") ? ("\u5927\u6a13\u7de8\u865f\uff1a" + val("new_building_no")) : ""
    };

    if (caseType === "\u88dd\u6a5f") {
      payload.install_detail = {
        construction_fee: numeric("new_construction"),
        deposit_amount: numeric("new_deposit"),
        other_fee_1: numeric("new_other_1"),
        other_fee_2: numeric("new_other_2"),
        monthly_fee: numeric("new_monthly_1"),
        monthly_fee_1: numeric("new_monthly_1"),
        monthly_fee_2: numeric("new_monthly_2"),
        monthly_fee_3: numeric("new_monthly_3"),
        month_count: Math.max(1, Number(val("new_month_count") || 1)),
        other_fee: 0
      };
    }

    if (caseType === "\u9000\u6a5f") {
      payload.return_detail = {
        deposit_amount: numeric("new_return_deposit"),
        refund_amount: numeric("new_refund_amount"),
        deduction_amount: numeric("new_deduction_amount"),
        device_fee: numeric("new_device_fee"),
        cleaning_fee: numeric("new_cleaning_fee"),
        other_fee: numeric("new_return_other")
      };
    }

    const res = await fetch("/api/tickets", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const text = await res.text();
      alert("\u65b0\u589e\u5931\u6557\uff1a" + text.slice(0, 300));
      return;
    }

    resetCreateForm();
    closeCreateModal();
    await loadAll();
  }


  function logout() { sessionStorage.removeItem("xunnan_admin_token"); localStorage.removeItem("xunnan_admin_token"); localStorage.removeItem("xunnan_auth_token"); window.location.href = "/employee/logout?next=/"; }

  function bindEvents() {
    if (byId("new_type")) byId("new_type").addEventListener("change", syncCreatePriceFields);
    if (byId("new_building_no")) byId("new_building_no").addEventListener("change", function () {
      applyCreateBuildingAddress();
      updateCreateCustomerAddressOptions(true);
    });
    if (byId("new_existing_customer_address")) byId("new_existing_customer_address").addEventListener("change", applyCreateExistingCustomerAddress);
    if (byId("new_area")) byId("new_area").addEventListener("change", function () {
      updateCreateBuildingOptions(true);
      applyCreateBuildingAddress();
    });
    ["top_filter_area","top_filter_engineer","keyword_filter"].forEach(function (id) { const el = byId(id); if (el) el.addEventListener(id === "keyword_filter" ? "input" : "change", renderAll); });
    ["area","type","customer","address","phone","time","engineer","status"].forEach(function (key) { const el = byId("excel_filter_" + key); if (el) el.addEventListener("change", renderTable); });
    document.querySelectorAll(".stat-card[data-stat-filter]").forEach(function (card) { card.addEventListener("click", function () { const f = card.dataset.statFilter || ""; statFilter = statFilter === f ? "" : f; document.querySelectorAll(".stat-card").forEach(el => el.classList.remove("active")); if (statFilter) card.classList.add("active"); renderAll(); }); });
    [byId("detail_modal"), byId("create_modal")].forEach(function (mask) { if (!mask) return; mask.addEventListener("click", function (event) { if (event.target === mask) mask.classList.remove("active"); }); });
  }

  document.addEventListener("DOMContentLoaded", function () { initStaticSelects(); bindEvents(); loadAll(); setInterval(loadAll, 30000); setInterval(loadNotices, 10000); });

  /* ADDRESS_HELPER_SELECT_EVENT_V1 */
  document.addEventListener("change", function (event) {
    if (!event || !event.target) return;

    if (event.target.id === "new_building_no") {
      updateCreateCustomerAddressOptions(true);
    }
  });

</script>
</body>
</html>
'''
