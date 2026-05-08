from __future__ import annotations

import calendar
import json
import secrets
from datetime import date, timedelta
from html import escape

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import text

from app.db import engine
from app.routes.employee_auth import _employee_current_user_from_request


router = APIRouter(tags=["人事系統附屬管理"])


APP_OPTIONS = [
    ("dispatch", "派工 APP"),
    ("billing", "帳務 APP"),
    ("engineering", "工程 APP"),
    ("sales", "業務 APP"),
    ("hr", "人事系統"),
    ("admin", "管理後台"),
]

FRONTLINE_DEPARTMENTS = ["工程部", "維修部", "專案部"]

HOLIDAYS_2026_05_06 = {
    "2026-05-01": "勞動節",
    "2026-06-19": "端午節",
}

DEPARTMENT_ROWS = [
    {"department": "工程部", "roles": "工程師、資深工程師、工程主管", "frontline": "是", "apps": "派工 APP、工程 APP"},
    {"department": "維修部", "roles": "維修專員、維修工程師、維修主管", "frontline": "是", "apps": "派工 APP、工程 APP"},
    {"department": "專案部", "roles": "專案專員、專案主管", "frontline": "是", "apps": "工程 APP、人事系統"},
    {"department": "帳務部", "roles": "帳務專員、帳務主管", "frontline": "否", "apps": "帳務 APP"},
    {"department": "業務部", "roles": "業務專員、業務主管", "frontline": "否", "apps": "業務 APP、工程流程"},
    {"department": "管理部", "roles": "行政、人事、系統管理員", "frontline": "否", "apps": "人事系統、管理後台"},
]


def _safe_user_or_redirect(request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return None
    return user


def _json_loads_list(value):
    if isinstance(value, list):
        return value
    raw = str(value or "").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(x) for x in data]
    except Exception:
        pass
    return [x.strip() for x in raw.split(",") if x.strip()]


def _load_employees():
    with engine.begin() as conn:
        try:
            rows = conn.execute(text("""
                SELECT
                    p.staff_code,
                    p.display_name,
                    p.department,
                    p.role,
                    p.position_title,
                    p.phone,
                    p.email,
                    p.employment_status,
                    p.permission_scope,
                    p.app_access,
                    COALESCE(a.enabled, 0) AS account_enabled
                FROM employee_profiles p
                LEFT JOIN employee_accounts a ON a.staff_code = p.staff_code
                ORDER BY p.department, p.staff_code
            """)).mappings().fetchall()
        except Exception:
            rows = []

    employees = []
    for row in rows:
        item = dict(row)
        item["app_access"] = _json_loads_list(item.get("app_access"))
        employees.append(item)

    if employees:
        return employees

    # 保底虛擬資料，避免頁面空白
    return [
        {"staff_code": "ENG001", "display_name": "王建成", "department": "工程部", "role": "employee", "position_title": "工程師", "phone": "0912000001", "email": "eng001@demo", "employment_status": "在職", "permission_scope": "北區", "app_access": ["dispatch", "engineering"], "account_enabled": 1},
        {"staff_code": "ENG002", "display_name": "林志強", "department": "工程部", "role": "employee", "position_title": "資深工程師", "phone": "0912000002", "email": "eng002@demo", "employment_status": "在職", "permission_scope": "南區", "app_access": ["dispatch", "engineering"], "account_enabled": 1},
        {"staff_code": "MT001", "display_name": "陳雅婷", "department": "維修部", "role": "employee", "position_title": "維修專員", "phone": "0912000003", "email": "mt001@demo", "employment_status": "在職", "permission_scope": "全區", "app_access": ["dispatch", "engineering"], "account_enabled": 1},
        {"staff_code": "PM001", "display_name": "張家豪", "department": "專案部", "role": "manager", "position_title": "專案主管", "phone": "0912000004", "email": "pm001@demo", "employment_status": "在職", "permission_scope": "工程專案", "app_access": ["engineering", "hr"], "account_enabled": 1},
        {"staff_code": "BIL001", "display_name": "李佩君", "department": "帳務部", "role": "employee", "position_title": "帳務專員", "phone": "0912000005", "email": "bil001@demo", "employment_status": "在職", "permission_scope": "帳務", "app_access": ["billing"], "account_enabled": 1},
        {"staff_code": "SAL001", "display_name": "郭明達", "department": "業務部", "role": "sales", "position_title": "業務專員", "phone": "0912000006", "email": "sal001@demo", "employment_status": "在職", "permission_scope": "業務", "app_access": ["sales"], "account_enabled": 1},
        {"staff_code": "HR001", "display_name": "黃怡君", "department": "管理部", "role": "manager", "position_title": "人事行政", "phone": "0912000007", "email": "hr001@demo", "employment_status": "在職", "permission_scope": "人事", "app_access": ["hr", "admin"], "account_enabled": 1},
    ]


def _nav(active: str) -> str:
    items = [
        ("員工名冊", "/admin/hr", "employees"),
        ("權限管理", "/admin/hr/permissions", "permissions"),
        ("密碼管理", "/admin/hr/passwords", "passwords"),
        ("請假審核", "/admin/hr/leave-requests", "leave_requests"),
        ("休假管理", "/admin/hr/leave-management", "leave"),
        ("代理人管理", "/admin/hr/proxy-management", "proxy"),
        ("部門職務", "/admin/hr/departments", "departments"),
    ]
    html = []
    for label, href, key in items:
        cls = "active" if key == active else ""
        html.append(f'<a class="{cls}" href="{href}">{escape(label)}</a>')
    html.append('<a href="/">返回首頁</a>')
    return "\n".join(html)


def _layout(title: str, active: str, user_line: str, body: str) -> str:
    return f"""
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}｜訊南人事系統</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #edf2f7;
      color: #102348;
      font-family: "Microsoft JhengHei", "Segoe UI", Arial, sans-serif;
    }}
    .layout {{
      min-height: 100vh;
      display: grid;
      grid-template-columns: 250px minmax(0, 1fr);
    }}
    .sidebar {{
      background: linear-gradient(180deg, #3f6471, #2f455f 55%, #263a55);
      color: #fff;
      padding: 22px 18px;
      border-right: 1px solid rgba(255,255,255,.16);
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 26px;
    }}
    .brand img {{
      width: 76px;
      height: 58px;
      object-fit: contain;
      filter: drop-shadow(0 4px 8px rgba(0,0,0,.16));
    }}
    .brand-title {{
      font-size: 23px;
      font-weight: 1000;
      line-height: 1.15;
    }}
    .brand-sub {{
      margin-top: 4px;
      color: #fbbf24;
      font-size: 13px;
      font-weight: 900;
    }}
    .nav {{
      display: grid;
      gap: 9px;
    }}
    .nav a {{
      width: 100%;
      min-height: 42px;
      border: 0;
      border-radius: 12px;
      padding: 0 13px;
      background: rgba(255,255,255,.14);
      color: #eef6ff;
      font-size: 15px;
      font-weight: 900;
      text-align: left;
      text-decoration: none;
      display: flex;
      align-items: center;
    }}
    .nav a:hover {{ background: rgba(255,255,255,.22); }}
    .nav .active {{
      background: #365ee8;
      color: #fff;
    }}
    .main {{
      min-width: 0;
      padding: 22px 26px 34px;
    }}
    .topbar {{
      display: grid;
      grid-template-columns: minmax(0,1fr) auto;
      gap: 14px;
      align-items: center;
      margin-bottom: 18px;
    }}
    .page-title {{
      font-size: 32px;
      font-weight: 1000;
      line-height: 1.2;
    }}
    .page-sub {{
      margin-top: 5px;
      color: #64748b;
      font-size: 15px;
      font-weight: 900;
    }}
    .btn {{
      height: 40px;
      border: 0;
      border-radius: 12px;
      padding: 0 16px;
      background: #fff;
      color: #102348;
      font-size: 14px;
      font-weight: 1000;
      box-shadow: 0 8px 18px rgba(15,23,42,.08);
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
    }}
    .btn.primary {{ background: #365ee8; color: #fff; }}
    .btn.green {{ background: #16a34a; color: #fff; }}
    .btn.red {{ background: #cf3b2f; color: #fff; }}
    .panel {{
      background: #fff;
      border: 1px solid #d7e1ef;
      border-radius: 20px;
      box-shadow: 0 10px 26px rgba(15,23,42,.06);
      overflow: hidden;
      margin-bottom: 16px;
    }}
    .panel-head {{
      padding: 16px 18px;
      border-bottom: 1px solid #e2e8f0;
      background: #f8fafc;
      font-size: 20px;
      font-weight: 1000;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }}
    .panel-body {{ padding: 16px 18px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 980px;
    }}
    .table-wrap {{
      overflow: auto;
      max-height: calc(100vh - 235px);
    }}
    th {{
      position: sticky;
      top: 0;
      background: #eff6ff;
      color: #1e3a8a;
      padding: 10px;
      border-bottom: 1px solid #dbeafe;
      text-align: left;
      font-size: 13px;
      font-weight: 1000;
      white-space: nowrap;
    }}
    td {{
      padding: 10px;
      border-bottom: 1px solid #e2e8f0;
      font-size: 14px;
      font-weight: 850;
      white-space: nowrap;
      vertical-align: middle;
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 0 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 1000;
      background: #e2e8f0;
      color: #334155;
      margin: 2px;
    }}
    .pill.green {{ background: #dcfce7; color: #166534; }}
    .pill.blue {{ background: #dbeafe; color: #1d4ed8; }}
    .pill.red {{ background: #fee2e2; color: #991b1b; }}
    .pill.yellow {{ background: #fef3c7; color: #92400e; }}
    .pill.orange {{ background: #ffedd5; color: #c2410c; }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }}
    .summary-card {{
      background: #fff;
      border: 1px solid #d7e1ef;
      border-radius: 18px;
      padding: 14px 16px;
      box-shadow: 0 10px 26px rgba(15,23,42,.06);
    }}
    .summary-label {{
      color: #64748b;
      font-size: 14px;
      font-weight: 1000;
    }}
    .summary-value {{
      margin-top: 8px;
      color: #102348;
      font-size: 32px;
      line-height: 1;
      font-weight: 1000;
    }}
    .note {{
      border-radius: 16px;
      background: #fff7ed;
      border: 1px solid #fdba74;
      color: #7c2d12;
      padding: 12px 14px;
      font-size: 15px;
      font-weight: 900;
      line-height: 1.55;
      margin-bottom: 16px;
    }}
    @media(max-width: 980px) {{
      .layout {{ grid-template-columns: 1fr; }}
      .sidebar {{ display: none; }}
      .summary {{ grid-template-columns: repeat(2, 1fr); }}
    }}
  </style>
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">
        <img src="/static/shinnan_home_logo.png" alt="訊南 Logo">
        <div>
          <div class="brand-title">訊南人事系統</div>
          <div class="brand-sub">HR ADMIN</div>
        </div>
      </div>
      <nav class="nav">
        {_nav(active)}
      </nav>
    </aside>
    <main class="main">
      <header class="topbar">
        <div>
          <div class="page-title">{escape(title)}</div>
          <div class="page-sub">{escape(user_line)}｜電腦版人事後台</div>
        </div>
        <a class="btn" href="/admin/hr">回人事首頁</a>
      </header>
      {body}
    </main>
  </div>
</body>
</html>
"""


def _user_line(user) -> str:
    return (str(user.get("display_name") or "") + "｜" + str(user.get("role") or "")).strip("｜")


def _require_page_user(request: Request):
    user = _safe_user_or_redirect(request)
    if not user:
        return None
    return user


def _date_range(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def _virtual_leave_requests(employees):
    by_dept = {d: [e for e in employees if e.get("department") == d and e.get("employment_status") == "在職"] for d in FRONTLINE_DEPARTMENTS}

    def pick(dept, index):
        arr = by_dept.get(dept) or []
        if not arr:
            return {"staff_code": dept + "000", "display_name": dept + "人員", "department": dept}
        return arr[index % len(arr)]

    rows = []
    seed = [
        ("2026-05-01", "工程部", 0, "排休", "國定假日輪休"),
        ("2026-05-04", "維修部", 0, "特休", "家庭因素"),
        ("2026-05-08", "專案部", 0, "事假", "個人事務"),
        ("2026-05-15", "工程部", 1, "病假", "門診"),
        ("2026-05-22", "維修部", 1, "排休", "排休"),
        ("2026-05-29", "專案部", 0, "特休", "家庭旅遊"),
        ("2026-06-05", "工程部", 0, "公假", "教育訓練"),
        ("2026-06-12", "維修部", 0, "事假", "個人事務"),
        ("2026-06-19", "專案部", 0, "排休", "端午輪休"),
        ("2026-06-22", "工程部", 1, "特休", "特休"),
        ("2026-06-26", "維修部", 1, "病假", "回診"),
    ]
    for i, (day, dept, idx, leave_type, reason) in enumerate(seed, start=1):
        emp = pick(dept, idx)
        rows.append({
            "id": f"LV-20260506-{i:03d}",
            "date": day,
            "staff_code": emp.get("staff_code", ""),
            "display_name": emp.get("display_name", ""),
            "department": dept,
            "leave_type": leave_type,
            "reason": reason,
            "status": "已核准" if i % 3 else "待審核",
        })
    return rows


@router.get("/admin/hr/leave-management", response_class=HTMLResponse)
def hr_leave_management_page(request: Request):
    user = _require_page_user(request)
    if not user:
        return RedirectResponse("/employee/login?next=/admin/hr/leave-management", status_code=303)

    employees = _load_employees()
    leave_rows = _virtual_leave_requests(employees)

    active_by_dept = {
        dept: [
            e for e in employees
            if e.get("department") == dept and e.get("employment_status") == "在職"
        ]
        for dept in FRONTLINE_DEPARTMENTS
    }

    leave_by_date_dept = {}
    for row in leave_rows:
        leave_by_date_dept.setdefault((row["date"], row["department"]), []).append(row)

    total_days = 0
    risk_days = 0
    holiday_count = 0
    table_rows = []

    weekday_names = ["一", "二", "三", "四", "五", "六", "日"]

    for d in _date_range(date(2026, 5, 1), date(2026, 6, 30)):
        key = d.isoformat()
        total_days += 1
        holiday = HOLIDAYS_2026_05_06.get(key, "")
        if holiday:
            holiday_count += 1

        dept_cells = []
        day_has_risk = False
        leave_names_all = []

        for dept in FRONTLINE_DEPARTMENTS:
            total_staff = len(active_by_dept.get(dept) or [])
            dept_leaves = leave_by_date_dept.get((key, dept), [])
            leave_count = len(dept_leaves)
            on_duty = max(0, total_staff - leave_count)

            leave_names = "、".join([x["display_name"] for x in dept_leaves]) or "-"
            if leave_names != "-":
                leave_names_all.append(f"{dept}:{leave_names}")

            if total_staff == 0 or on_duty < 1:
                day_has_risk = True
                dept_cells.append(f"<td><span class='pill red'>{dept} 缺人</span><br>值班 {on_duty}/{total_staff}<br>休：{escape(leave_names)}</td>")
            else:
                dept_cells.append(f"<td><span class='pill green'>{dept} OK</span><br>值班 {on_duty}/{total_staff}<br>休：{escape(leave_names)}</td>")

        if day_has_risk:
            risk_days += 1

        holiday_html = f"<span class='pill yellow'>{escape(holiday)}</span>" if holiday else ""
        status_html = "<span class='pill red'>需補人</span>" if day_has_risk else "<span class='pill green'>一線有人值班</span>"

        table_rows.append(f"""
          <tr>
            <td>{key}</td>
            <td>星期{weekday_names[d.weekday()]}</td>
            <td>{holiday_html}</td>
            {''.join(dept_cells)}
            <td>{escape('；'.join(leave_names_all) or '-')}</td>
            <td>{status_html}</td>
          </tr>
        """)

    request_rows = []
    for row in leave_rows:
        request_rows.append(f"""
          <tr>
            <td>{escape(row["id"])}</td>
            <td>{escape(row["date"])}</td>
            <td>{escape(row["display_name"])}</td>
            <td>{escape(row["department"])}</td>
            <td>{escape(row["leave_type"])}</td>
            <td>{escape(row["reason"])}</td>
            <td><span class='pill {"green" if row["status"] == "已核准" else "yellow"}'>{escape(row["status"])}</span></td>
          </tr>
        """)

    body = f"""
      <div class="note">
        本頁先用 2026 年 5、6 月虛擬休假資料測試管理邏輯。國定假日目前列入：2026-05-01 勞動節、2026-06-19 端午節。<br>
        一線單位規則：工程部、維修部、專案部每天至少要有 1 人值班；若某部門全員請假或無在職人員，該日標示需補人。
      </div>

      <section class="summary">
        <div class="summary-card"><div class="summary-label">檢查天數</div><div class="summary-value">{total_days}</div></div>
        <div class="summary-card"><div class="summary-label">國定假日</div><div class="summary-value">{holiday_count}</div></div>
        <div class="summary-card"><div class="summary-label">虛擬假單</div><div class="summary-value">{len(leave_rows)}</div></div>
        <div class="summary-card"><div class="summary-label">缺人天數</div><div class="summary-value">{risk_days}</div></div>
      </section>

      <section class="panel">
        <div class="panel-head">
          <span>5、6 月一線值班檢查表</span>
          <a class="btn primary" href="/admin/hr/leave-requests">查看虛擬假單</a>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>日期</th>
                <th>星期</th>
                <th>國定假日</th>
                <th>工程部</th>
                <th>維修部</th>
                <th>專案部</th>
                <th>請假摘要</th>
                <th>檢查結果</th>
              </tr>
            </thead>
            <tbody>{''.join(table_rows)}</tbody>
          </table>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head">虛擬假單列表</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>單號</th><th>日期</th><th>員工</th><th>部門</th><th>假別</th><th>原因</th><th>狀態</th></tr>
            </thead>
            <tbody>{''.join(request_rows)}</tbody>
          </table>
        </div>
      </section>
    """
    return _layout("休假管理", "leave", _user_line(user), body)


@router.get("/admin/hr/leave-requests", response_class=HTMLResponse)
def hr_leave_requests_page(request: Request):
    user = _require_page_user(request)
    if not user:
        return RedirectResponse("/employee/login?next=/admin/hr/leave-requests", status_code=303)

    employees = _load_employees()
    leave_rows = _virtual_leave_requests(employees)

    rows = []
    for row in leave_rows:
        rows.append(f"""
          <tr>
            <td>{escape(row["id"])}</td>
            <td>{escape(row["date"])}</td>
            <td>{escape(row["staff_code"])}</td>
            <td>{escape(row["display_name"])}</td>
            <td>{escape(row["department"])}</td>
            <td>{escape(row["leave_type"])}</td>
            <td>{escape(row["reason"])}</td>
            <td><span class='pill {"green" if row["status"] == "已核准" else "yellow"}'>{escape(row["status"])}</span></td>
            <td>
              <button class="btn green" onclick="alert('虛擬功能：核准假單')">核准</button>
              <button class="btn red" onclick="alert('虛擬功能：退回假單')">退回</button>
            </td>
          </tr>
        """)

    body = f"""
      <div class="note">此頁先開放虛擬假單審核流程；下一階段會接正式 employee_leave_settings 表與審核紀錄。</div>
      <section class="panel">
        <div class="panel-head">請假審核 / 虛擬假單</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>單號</th><th>日期</th><th>員編</th><th>姓名</th><th>部門</th><th>假別</th><th>原因</th><th>狀態</th><th>操作</th></tr>
            </thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
      </section>
    """
    return _layout("請假審核", "leave_requests", _user_line(user), body)


@router.get("/admin/hr/permissions", response_class=HTMLResponse)
def hr_permissions_page(request: Request):
    user = _require_page_user(request)
    if not user:
        return RedirectResponse("/employee/login?next=/admin/hr/permissions", status_code=303)

    employees = _load_employees()
    rows = []

    for emp in employees:
        apps = emp.get("app_access") or []
        app_cells = []
        for key, label in APP_OPTIONS:
            checked = "checked" if key in apps else ""
            app_cells.append(f"<td><input type='checkbox' {checked} onclick=\"alert('虛擬功能：切換 {escape(label)} 權限')\"></td>")

        rows.append(f"""
          <tr>
            <td>{escape(emp.get("staff_code", ""))}</td>
            <td>{escape(emp.get("display_name", ""))}</td>
            <td>{escape(emp.get("department", ""))}</td>
            <td>{escape(emp.get("role", ""))}</td>
            {''.join(app_cells)}
          </tr>
        """)

    app_headers = "".join([f"<th>{escape(label)}</th>" for _, label in APP_OPTIONS])

    body = f"""
      <div class="note">權限管理先以矩陣方式開放；目前是可視化與虛擬切換，正式儲存會在下一階段接 employee_profiles.app_access。</div>
      <section class="panel">
        <div class="panel-head">APP 權限矩陣</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>員工編號</th><th>姓名</th><th>部門</th><th>角色</th>{app_headers}</tr>
            </thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
      </section>
    """
    return _layout("權限管理", "permissions", _user_line(user), body)


@router.get("/admin/hr/passwords", response_class=HTMLResponse)
def hr_passwords_page(request: Request):
    user = _require_page_user(request)
    if not user:
        return RedirectResponse("/employee/login?next=/admin/hr/passwords", status_code=303)

    employees = _load_employees()
    rows = []

    for i, emp in enumerate(employees, start=1):
        temp_pin = "TMP" + secrets.token_hex(2).upper()
        rows.append(f"""
          <tr>
            <td>{escape(emp.get("staff_code", ""))}</td>
            <td>{escape(emp.get("display_name", ""))}</td>
            <td>{escape(emp.get("department", ""))}</td>
            <td><span class='pill {"green" if int(emp.get("account_enabled") or 0) else "red"}'>{"啟用" if int(emp.get("account_enabled") or 0) else "停用"}</span></td>
            <td>{escape(temp_pin)}</td>
            <td><span class="pill yellow">虛擬重設碼</span></td>
            <td>
              <button class="btn primary" onclick="alert('虛擬功能：重設此員工密碼')">重設密碼</button>
              <button class="btn" onclick="alert('虛擬功能：停用或啟用帳號')">啟用/停用</button>
            </td>
          </tr>
        """)

    body = f"""
      <div class="note">
        密碼管理不顯示真實密碼，也不保存明文密碼。本頁只顯示「虛擬臨時重設碼」與帳號狀態，用來設計正式流程。
      </div>
      <section class="panel">
        <div class="panel-head">虛擬密碼表 / 帳號重設</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>員工編號</th><th>姓名</th><th>部門</th><th>帳號狀態</th><th>臨時碼</th><th>說明</th><th>操作</th></tr>
            </thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
      </section>
    """
    return _layout("密碼管理", "passwords", _user_line(user), body)


@router.get("/admin/hr/proxy-management", response_class=HTMLResponse)
def hr_proxy_management_page(request: Request):
    user = _require_page_user(request)
    if not user:
        return RedirectResponse("/employee/login?next=/admin/hr/proxy-management", status_code=303)

    employees = _load_employees()
    active = [e for e in employees if e.get("employment_status") == "在職"]
    rows = []

    for i, emp in enumerate(active):
        proxy1 = active[(i + 1) % len(active)] if active else {}
        proxy2 = active[(i + 2) % len(active)] if active else {}
        rows.append(f"""
          <tr>
            <td>{escape(emp.get("staff_code", ""))}</td>
            <td>{escape(emp.get("display_name", ""))}</td>
            <td>{escape(emp.get("department", ""))}</td>
            <td>{escape(proxy1.get("display_name", "-"))}</td>
            <td>{escape(proxy2.get("display_name", "-"))}</td>
            <td><span class="pill blue">派工 / 帳務 / 工程依權限代理</span></td>
            <td><span class="pill green">啟用</span></td>
            <td><button class="btn primary" onclick="alert('虛擬功能：編輯代理人')">編輯</button></td>
          </tr>
        """)

    body = f"""
      <div class="note">代理人管理先以虛擬資料開放；下一階段會接 employee_proxy_settings，並依 APP 權限限制代理範圍。</div>
      <section class="panel">
        <div class="panel-head">代理人管理</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>員編</th><th>員工</th><th>部門</th><th>代理人一</th><th>代理人二</th><th>代理範圍</th><th>狀態</th><th>操作</th></tr>
            </thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
      </section>
    """
    return _layout("代理人管理", "proxy", _user_line(user), body)


@router.get("/admin/hr/departments", response_class=HTMLResponse)
def hr_departments_page(request: Request):
    user = _require_page_user(request)
    if not user:
        return RedirectResponse("/employee/login?next=/admin/hr/departments", status_code=303)

    employees = _load_employees()
    count_by_dept = {}
    for emp in employees:
        dept = emp.get("department") or "未設定"
        count_by_dept[dept] = count_by_dept.get(dept, 0) + 1

    rows = []
    for item in DEPARTMENT_ROWS:
        dept = item["department"]
        rows.append(f"""
          <tr>
            <td>{escape(dept)}</td>
            <td>{escape(item["roles"])}</td>
            <td>{count_by_dept.get(dept, 0)}</td>
            <td><span class='pill {"green" if item["frontline"] == "是" else "blue"}'>{escape(item["frontline"])}</span></td>
            <td>{escape(item["apps"])}</td>
            <td><button class="btn primary" onclick="alert('虛擬功能：編輯部門職務')">編輯</button></td>
          </tr>
        """)

    body = f"""
      <div class="note">部門職務先以公司目前流程所需部門建立虛擬管理表，之後可正式接部門、職稱、職級資料表。</div>
      <section class="panel">
        <div class="panel-head">部門職務</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>部門</th><th>職務 / 職稱</th><th>人數</th><th>一線單位</th><th>常用系統</th><th>操作</th></tr>
            </thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
      </section>
    """
    return _layout("部門職務", "departments", _user_line(user), body)
