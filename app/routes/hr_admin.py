from __future__ import annotations

def _role_label_zh(value) -> str:
    raw = str(value or "").strip()

    mapping = {
        "admin": "系統管理員",
        "manager": "主管",
        "maintenance": "維修人員",
        "employee": "一般員工",
        "sales": "業務人員",
        "billing": "帳務人員",
        "engineering": "工程人員",
        "engineer": "工程人員",
        "hr": "人事人員",
        "field": "外勤人員",
        "product": "專案人員",
        "project": "專案人員",
        "warehouse": "倉管人員",
        "customer_service": "客服人員",
    }

    return mapping.get(raw, raw or "-")



import hashlib
import json
import secrets
from datetime import date, timedelta
from html import escape

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from sqlalchemy import text

from app.db import engine
from app.routes.employee_auth import _employee_current_user_from_request

router = APIRouter(tags=["人事系統"])

MIN_WAGE_115 = 29500
LABOR_RATE = 0.115
LABOR_EMPLOYEE_SHARE = 0.20
LABOR_EMPLOYER_SHARE = 0.70
HEALTH_RATE = 0.0517
HEALTH_EMPLOYEE_SHARE = 0.30
HEALTH_EMPLOYER_SHARE = 0.60
PENSION_EMPLOYER_RATE = 0.06
OCCUPATIONAL_RATE = 0.003
ARREARS_RATE = 0.00025

APP_OPTIONS = [
    ("dispatch", "派工 APP"),
    ("billing", "帳務 APP"),
    ("engineering", "工程 APP"),
    ("sales", "業務 APP"),
    ("hr", "人事系統"),
    ("admin", "管理後台"),
]
DEPARTMENTS = ["工程部", "維修部", "帳務部", "業務部", "專案部", "管理部", "外包"]
FRONTLINE_DEPARTMENTS = ["工程部", "維修部", "專案部"]
HOLIDAYS_2026_05_06 = {"2026-05-01": "勞動節", "2026-06-19": "端午節"}

SALARY_MARKET = {
    "工程師": 42000,
    "資深工程師": 52000,
    "維修專員": 38000,
    "維修工程師": 42000,
    "帳務專員": 35000,
    "業務專員": 38000,
    "專案主管": 60000,
    "人事行政": 38000,
    "系統管理員": 58000,
    "外包人員": 0,
}

VIRTUAL_EMPLOYEES = [
    ("S0045", "王建成", "工程部", "employee", "工程師", "男", "0912000001", "eng001@shinnan.local", "2024-03-01", "北區", ["dispatch", "engineering"]),
    ("S0041", "林志強", "工程部", "employee", "資深工程師", "男", "0912000002", "eng002@shinnan.local", "2023-08-15", "南區", ["dispatch", "engineering"]),
    ("S0046", "陳雅婷", "維修部", "employee", "維修專員", "女", "0912000003", "mt001@shinnan.local", "2024-06-10", "全區", ["dispatch", "engineering"]),
    ("S0043", "黃柏翰", "維修部", "employee", "維修工程師", "男", "0912000004", "mt002@shinnan.local", "2023-12-01", "北區", ["dispatch", "engineering"]),
    ("S0042", "李佩君", "帳務部", "employee", "帳務專員", "女", "0912000005", "bil001@shinnan.local", "2023-11-20", "帳務", ["billing"]),
    ("S0044", "郭明達", "業務部", "sales", "業務專員", "男", "0912000006", "sal001@shinnan.local", "2024-01-05", "業務", ["sales", "engineering"]),
    ("S0039", "張家豪", "專案部", "manager", "專案主管", "男", "0912000007", "pm001@shinnan.local", "2022-09-01", "工程專案", ["dispatch", "engineering", "hr"]),
    ("S0040", "黃怡君", "管理部", "manager", "人事行政", "女", "0912000008", "hr001@shinnan.local", "2022-02-11", "人事", ["hr", "admin"]),
    ("admin", "系統管理員", "管理部", "admin", "系統管理員", "", "", "admin@shinnan.local", "2021-01-01", "全系統", ["dispatch", "billing", "engineering", "sales", "hr", "admin"]),
]

LABOR_GRADES = [29500, 30300, 31800, 33300, 34800, 36300, 38200, 40100, 42000, 43900, 45800]
HEALTH_GRADES = [29500, 30300, 31800, 33300, 34800, 36300, 38200, 40100, 42000, 43900, 45800, 48200, 50600, 53000, 55400, 57800, 60800, 63800, 66800, 69800, 72800, 76500, 80200, 83900, 87600, 92100, 96600, 101100, 105600, 110100, 115500, 120900, 126300, 131700, 137100, 142500, 147900, 150000]


def _dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def _loads_list(value):
    if isinstance(value, list):
        return [str(x) for x in value]
    raw = str(value or "").strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
    except Exception:
        pass
    return [x.strip() for x in raw.split(",") if x.strip()]


def _hash_pin(pin: str, salt: str) -> str:
    return hashlib.sha256((str(pin) + ":" + str(salt)).encode("utf-8")).hexdigest()


def _money(value) -> str:
    try:
        return f"{int(round(float(value))):,}"
    except Exception:
        return "0"


def _ceil_grade(amount: float, grades: list[int]) -> int:
    amount = float(amount or 0)
    for grade in grades:
        if amount <= grade:
            return grade
    return grades[-1]


def _hr_db_init():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS employee_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                department TEXT DEFAULT '',
                role TEXT DEFAULT 'employee',
                position_title TEXT DEFAULT '',
                gender TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                employment_status TEXT DEFAULT '在職',
                hire_date TEXT DEFAULT '',
                permission_scope TEXT DEFAULT '',
                app_access TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS employee_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                department TEXT DEFAULT '',
                role TEXT DEFAULT 'employee',
                pin_salt TEXT NOT NULL,
                pin_hash TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS hr_change_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operator_staff_code TEXT DEFAULT '',
                action_type TEXT DEFAULT '',
                target_staff_code TEXT DEFAULT '',
                before_text TEXT DEFAULT '',
                after_text TEXT DEFAULT '',
                note TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))
        for sql in [
            "ALTER TABLE employee_profiles ADD COLUMN position_title TEXT DEFAULT ''",
            "ALTER TABLE employee_profiles ADD COLUMN gender TEXT DEFAULT ''",
            "ALTER TABLE employee_profiles ADD COLUMN phone TEXT DEFAULT ''",
            "ALTER TABLE employee_profiles ADD COLUMN email TEXT DEFAULT ''",
            "ALTER TABLE employee_profiles ADD COLUMN employment_status TEXT DEFAULT '在職'",
            "ALTER TABLE employee_profiles ADD COLUMN hire_date TEXT DEFAULT ''",
            "ALTER TABLE employee_profiles ADD COLUMN permission_scope TEXT DEFAULT ''",
            "ALTER TABLE employee_profiles ADD COLUMN app_access TEXT DEFAULT ''",
        ]:
            try:
                conn.execute(text(sql))
            except Exception:
                pass

        count = conn.execute(text("SELECT COUNT(*) FROM employee_profiles")).scalar() or 0
        if count < 8:
            for staff_code, display_name, department, role, position_title, gender, phone, email, hire_date, scope, apps in VIRTUAL_EMPLOYEES:
                exists = conn.execute(text("SELECT COUNT(*) FROM employee_profiles WHERE staff_code=:staff_code"), {"staff_code": staff_code}).scalar()
                if not exists:
                    conn.execute(text("""
                        INSERT INTO employee_profiles (
                            staff_code, display_name, department, role, position_title, gender, phone, email,
                            employment_status, hire_date, permission_scope, app_access, created_at, updated_at
                        )
                        VALUES (
                            :staff_code, :display_name, :department, :role, :position_title, :gender, :phone, :email,
                            '在職', :hire_date, :permission_scope, :app_access, datetime('now'), datetime('now')
                        )
                    """), {
                        "staff_code": staff_code,
                        "display_name": display_name,
                        "department": department,
                        "role": role,
                        "position_title": position_title,
                        "gender": gender,
                        "phone": phone,
                        "email": email,
                        "hire_date": hire_date,
                        "permission_scope": scope,
                        "app_access": _dumps(apps),
                    })

                account_exists = conn.execute(text("SELECT COUNT(*) FROM employee_accounts WHERE staff_code=:staff_code"), {"staff_code": staff_code}).scalar()
                if not account_exists:
                    salt = secrets.token_hex(8)
                    conn.execute(text("""
                        INSERT INTO employee_accounts (
                            staff_code, display_name, department, role, pin_salt, pin_hash, enabled, created_at, updated_at
                        )
                        VALUES (
                            :staff_code, :display_name, :department, :role, :pin_salt, :pin_hash, 1, datetime('now'), datetime('now')
                        )
                    """), {
                        "staff_code": staff_code,
                        "display_name": display_name,
                        "department": department,
                        "role": role,
                        "pin_salt": salt,
                        "pin_hash": _hash_pin("1111", salt),
                    })


def _load_employees():
    _hr_db_init()
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT
                p.staff_code, p.display_name, p.department, p.role, p.position_title,
                p.gender, p.phone, p.email, p.employment_status, p.hire_date,
                p.permission_scope, p.app_access, COALESCE(a.enabled, 0) AS account_enabled
            FROM employee_profiles p
            LEFT JOIN employee_accounts a ON a.staff_code = p.staff_code
            ORDER BY CASE p.employment_status WHEN '在職' THEN 1 ELSE 9 END, p.department, p.staff_code
        """)).mappings().fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["app_access"] = _loads_list(item.get("app_access"))
        items.append(item)
    return items


def _salary(emp: dict) -> dict:
    position = str(emp.get("position_title") or "")
    dept = str(emp.get("department") or "")
    base = SALARY_MARKET.get(position, 36000)
    if dept == "外包":
        base = 0

    duty = 3000 if "主管" in position else 0
    technical = 3000 if dept in FRONTLINE_DEPARTMENTS else 0
    supervisor = 6000 if emp.get("role") in ["manager", "admin"] else 0
    transport = 2000 if dept in ["工程部", "維修部", "業務部", "專案部"] else 1000
    phone = 1000 if dept in ["工程部", "維修部", "業務部", "專案部"] else 500
    meal = 2400
    full_attendance = 2000
    performance = 3000 if dept in ["業務部", "專案部"] else 1500
    engineering_bonus = 4000 if dept in FRONTLINE_DEPARTMENTS else 0
    referral = 1000 if dept == "業務部" else 0
    rebate = 800 if dept == "業務部" else 0
    overtime = 2500 if dept in ["工程部", "維修部"] else 800
    other_add = 0

    gross = sum([base, duty, technical, supervisor, transport, phone, meal, full_attendance, performance, engineering_bonus, referral, rebate, overtime, other_add])

    labor_grade = min(45800, _ceil_grade(gross, LABOR_GRADES))
    health_grade = _ceil_grade(gross, HEALTH_GRADES)
    pension_wage = max(MIN_WAGE_115, gross)

    labor_employee = round(labor_grade * LABOR_RATE * LABOR_EMPLOYEE_SHARE)
    labor_employer = round(labor_grade * LABOR_RATE * LABOR_EMPLOYER_SHARE)
    health_employee = round(health_grade * HEALTH_RATE * HEALTH_EMPLOYEE_SHARE)
    health_employer = round(health_grade * HEALTH_RATE * HEALTH_EMPLOYER_SHARE)
    occupational = round(labor_grade * OCCUPATIONAL_RATE)
    arrears = round(labor_grade * ARREARS_RATE)
    employer_pension = round(pension_wage * PENSION_EMPLOYER_RATE)

    employee_pension_self = 0
    personal_leave = 0
    sick_leave = 0
    late = 0
    absence = 0
    tax = 0
    welfare = 0
    other_deduct = 0

    deductions = sum([personal_leave, sick_leave, late, absence, labor_employee, health_employee, employee_pension_self, tax, welfare, other_deduct])
    net = gross - deductions
    company_cost = gross + labor_employer + health_employer + occupational + arrears + employer_pension

    return {
        "base": base, "duty": duty, "technical": technical, "supervisor": supervisor,
        "transport": transport, "phone": phone, "meal": meal, "full_attendance": full_attendance,
        "performance": performance, "engineering_bonus": engineering_bonus, "referral": referral,
        "rebate": rebate, "overtime": overtime, "other_add": other_add, "gross": gross,
        "labor_grade": labor_grade, "health_grade": health_grade, "pension_wage": pension_wage,
        "labor_employee": labor_employee, "labor_employer": labor_employer,
        "health_employee": health_employee, "health_employer": health_employer,
        "occupational": occupational, "arrears": arrears, "employer_pension": employer_pension,
        "employee_pension_self": employee_pension_self, "personal_leave": personal_leave,
        "sick_leave": sick_leave, "late": late, "absence": absence, "tax": tax,
        "welfare": welfare, "other_deduct": other_deduct, "deductions": deductions,
        "net": net, "company_cost": company_cost,
    }


def _user_or_redirect(request: Request, next_url: str):
    user = _employee_current_user_from_request(request)
    if not user:
        return RedirectResponse(f"/employee/login?next={next_url}", status_code=303)
    return user


def _user_line(user: dict) -> str:
    return (str(user.get("display_name") or "") + "｜" + str(user.get("role") or "")).strip("｜")


def _nav(active: str) -> str:
    links = [
        ("人事總覽", "/admin/hr", "home"),
        ("員工名冊", "/admin/hr/employees", "employees"),
        ("職務薪資調整", "/admin/hr/employee-adjust", "employee_adjust"),
        ("權限管理", "/admin/hr/permissions", "permissions"),
        ("密碼管理", "/admin/hr/passwords", "passwords"),
        ("請假審核", "/admin/hr/leave-requests", "leave_requests"),
        ("休假管理", "/admin/hr/leave-management", "leave"),
        ("代理人管理", "/admin/hr/proxy-management", "proxy"),
        ("部門職務", "/admin/hr/departments", "departments"),
        ("薪資結構", "/admin/hr/salary", "salary"),
        ("勞健保勞退", "/admin/hr/insurance", "insurance"),
        ("薪資試算", "/admin/hr/payroll", "payroll"),
        ("異動紀錄", "/admin/hr/change-logs", "logs"),
    ]
    out = []
    for label, href, key in links:
        cls = "active" if active == key else ""
        out.append(f'<a class="{cls}" href="{href}">{escape(label)}</a>')
    out.append('<a href="/">返回首頁</a>')
    return "\n".join(out)


def _layout(title: str, active: str, user_line: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}｜訊南人事系統</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin:0; background:#edf2f7; color:#102348; font-family:"Microsoft JhengHei","Segoe UI",Arial,sans-serif; }}
    .layout {{ min-height:100vh; display:grid; grid-template-columns:260px minmax(0,1fr); }}
    .sidebar {{ background:linear-gradient(180deg,#3f6471,#2f455f 55%,#263a55); color:#fff; padding:22px 18px; border-right:1px solid rgba(255,255,255,.16); }}
    .brand {{ display:flex; align-items:center; gap:12px; margin-bottom:24px; }}
    .brand img {{ width:76px; height:58px; object-fit:contain; filter:drop-shadow(0 4px 8px rgba(0,0,0,.16)); }}
    .brand-title {{ font-size:23px; font-weight:1000; line-height:1.15; }}
    .brand-sub {{ margin-top:4px; color:#fbbf24; font-size:13px; font-weight:900; }}
    .nav {{ display:grid; gap:8px; }}
    .nav a {{ min-height:38px; border-radius:12px; padding:0 13px; background:rgba(255,255,255,.14); color:#eef6ff; font-size:15px; font-weight:900; text-decoration:none; display:flex; align-items:center; }}
    .nav a:hover {{ background:rgba(255,255,255,.22); }}
    .nav .active {{ background:#365ee8; color:#fff; }}
    .main {{ min-width:0; padding:22px 26px 34px; }}
    .topbar {{ display:grid; grid-template-columns:minmax(0,1fr) auto; gap:14px; align-items:center; margin-bottom:18px; }}
    .page-title {{ font-size:32px; font-weight:1000; line-height:1.2; }}
    .page-sub {{ margin-top:5px; color:#64748b; font-size:15px; font-weight:900; }}
    .btn {{ height:38px; border:0; border-radius:12px; padding:0 14px; background:#fff; color:#102348; font-size:14px; font-weight:1000; box-shadow:0 8px 18px rgba(15,23,42,.08); cursor:pointer; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; white-space:nowrap; }}
    .btn.primary {{ background:#365ee8; color:#fff; }}
    .btn.green {{ background:#16a34a; color:#fff; }}
    .btn.red {{ background:#cf3b2f; color:#fff; }}
    .summary {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-bottom:16px; }}
    .summary-card {{ background:#fff; border:1px solid #d7e1ef; border-radius:18px; padding:14px 16px; box-shadow:0 10px 26px rgba(15,23,42,.06); }}
    .summary-label {{ color:#64748b; font-size:14px; font-weight:1000; }}
    .summary-value {{ margin-top:8px; color:#102348; font-size:32px; line-height:1; font-weight:1000; }}
    .panel {{ background:#fff; border:1px solid #d7e1ef; border-radius:20px; box-shadow:0 10px 26px rgba(15,23,42,.06); overflow:hidden; margin-bottom:16px; }}
    .panel-head {{ padding:16px 18px; border-bottom:1px solid #e2e8f0; background:#f8fafc; font-size:20px; font-weight:1000; display:flex; justify-content:space-between; align-items:center; gap:12px; }}
    .table-wrap {{ overflow:auto; 
      max-height: calc(100vh - 120px);
      min-height: calc(100vh - 210px);
max-height: calc(100vh - 120px); }}
    table {{ width:100%; min-width:1100px; border-collapse:collapse; }}
    th {{ position:sticky; top:0; z-index:2; background:#eff6ff; color:#1e3a8a; padding:10px; border-bottom:1px solid #dbeafe; text-align:left; font-size:13px; font-weight:1000; white-space:nowrap; }}
    td {{ padding:10px; border-bottom:1px solid #e2e8f0; font-size:14px; font-weight:850; white-space:nowrap; vertical-align:middle; }}
    .pill {{ display:inline-flex; align-items:center; min-height:28px; padding:0 10px; border-radius:999px; font-size:12px; font-weight:1000; background:#e2e8f0; color:#334155; margin:2px; }}
    .pill.green {{ background:#dcfce7; color:#166534; }}
    .pill.blue {{ background:#dbeafe; color:#1d4ed8; }}
    .pill.red {{ background:#fee2e2; color:#991b1b; }}
    .pill.yellow {{ background:#fef3c7; color:#92400e; }}
    .note {{ border-radius:16px; background:#fff7ed; border:1px solid #fdba74; color:#7c2d12; padding:12px 14px; font-size:15px; font-weight:900; line-height:1.55; margin-bottom:16px; }}
    
.dashboard-grid {{ display:flex; flex-direction:column; gap:20px; margin-top:20px; }}
    .dash-row {{ display:grid; gap:16px; }}
    .dash-row.col-3-1 {{ grid-template-columns:3fr 1fr; }}
    .dash-row.col-1-1 {{ grid-template-columns:1fr 1fr; }}
    .dash-row.col-1-1-1 {{ grid-template-columns:1fr 1fr 1fr; }}
    .dash-panel {{ background:#fff; border-radius:12px; padding:14px 16px; box-shadow:0 2px 8px rgba(0,0,0,.07); border:1px solid #e5e7eb; }}
    .dash-panel canvas {{ max-height:160px; }}
    .dash-panel-title {{ font-size:13px; }}
    .dash-panel-title {{ font-size:15px; font-weight:800; color:#1e3a5f; margin-bottom:14px; padding-bottom:10px; border-bottom:2px solid #eef3f9; }}
    .dash-list {{ list-style:none; padding:0; margin:0; }}
    .dash-list li {{ padding:8px 0; border-bottom:1px solid #f1f5f9; font-size:13px; }}
    .dash-list li:last-child {{ border-bottom:none; }}
    .dash-list a {{ color:#1d4ed8; text-decoration:none; }}
    .dash-list a:hover {{ text-decoration:underline; }}
    .dash-table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    .dash-table tr {{ border-bottom:1px solid #f1f5f9; }}
    .dash-table td {{ padding:8px 4px; color:#475569; }}
    .dash-table td.val {{ font-weight:800; color:#1e3a5f; text-align:right; }}
    .dash-shortcuts {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
    .shortcut-btn {{ display:block; text-align:center; padding:12px 8px; background:#eef3f9; border-radius:8px; font-size:13px; font-weight:700; color:#1e3a5f; text-decoration:none; border:1px solid #d7e1ef; }}
    .shortcut-btn:hover {{ background:#1d4ed8; color:#fff; border-color:#1d4ed8; }}
    .cards {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }}
    .big-card {{ background:#fff; border:1px solid #d7e1ef; border-radius:20px; padding:18px; box-shadow:0 10px 26px rgba(15,23,42,.06); text-decoration:none; color:#102348; }}
    .big-card h3 {{ margin:0 0 10px; font-size:22px; }}
    .big-card p {{ margin:0; color:#64748b; font-weight:900; line-height:1.55; }}
    @media(max-width:980px) {{ .layout {{ grid-template-columns:1fr; }} .sidebar {{ display:none; }} .summary {{ grid-template-columns:repeat(2,1fr); }} 
    .cards {{ grid-template-columns:1fr; }} }}
  
    /* HR_TABLE_COMPACT_FIX_START */
    .panel table th,
    .panel table td,
    .table-wrap table th,
    .table-wrap table td {{
      font-size: 14px !important;
      line-height: 1.35 !important;
      padding: 8px 10px !important;
    }}

    .panel table td b,
    .table-wrap table td b {{
      font-size: 14px !important;
      line-height: 1.35 !important;
    }}

    .pill {{
      font-size: 12px !important;
      min-height: 24px !important;
      padding: 0 8px !important;
    }}

    .table-wrap {{
      max-height: calc(100vh - 120px) !important;
      min-height: calc(100vh - 210px) !important;
    }}
    /* HR_TABLE_COMPACT_FIX_END */

  </style>
  <link rel="stylesheet" href="/static/hr_sidebar_gold_glass_v2.css?v=cl15n43b">
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand"><img src="/static/shinnan_logo_gold_transparent.png" alt="訊南 Logo"><div><div class="brand-title">訊南人事系統</div><div class="brand-sub">HR ADMIN</div></div></div>
      <nav class="nav">{_nav(active)}</nav>
    </aside>
    <main class="main">
      <header class="topbar"><div><div class="page-title">{escape(title)}</div><div class="page-sub">{escape(user_line)}｜電腦版人事後台</div></div><a class="btn red" href="/employee/logout" onclick="localStorage.removeItem('xunnan_admin_token');localStorage.removeItem('xunnan_auth_token');localStorage.removeItem('xunnan_admin_role');localStorage.removeItem('xunnan_login_role')">登出</a></header>
      {body}
    </main>
  </div>

  <!-- app_header_actions 已移除 -->
</body>
</html>"""


def _employees_table(employees):
    rows = []
    for item in employees:
        apps = item.get("app_access") or []
        app_html = "".join([f"<span class='pill blue'>{escape(dict(APP_OPTIONS).get(a, a))}</span>" for a in apps]) or "<span class='pill'>未設定</span>"
        status_class = "green" if item.get("employment_status") == "在職" else "red"
        account_class = "green" if int(item.get("account_enabled") or 0) else "red"
        rows.append(f"""
          <tr><td>{escape(item.get("staff_code",""))}</td><td>{escape(item.get("display_name",""))}</td><td>{escape(item.get("department",""))}</td><td>{escape(item.get("position_title",""))}</td><td>{_role_label_zh(item.get('role',''))}</td><td>{escape(item.get("phone",""))}</td><td>{escape(item.get("email",""))}</td><td>{escape(item.get("hire_date",""))}</td><td><span class="pill {status_class}">{escape(item.get("employment_status",""))}</span></td><td><span class="pill {account_class}">{"啟用" if int(item.get("account_enabled") or 0) else "停用"}</span></td><td>{app_html}</td></tr>
        """)
    return "".join(rows)



@router.get("/admin/hr", response_class=HTMLResponse)
def hr_home_page(request: Request):
    user = _user_or_redirect(request, "/admin/hr")
    if not isinstance(user, dict):
        return user

    employees = _load_employees()
    total = len(employees)
    active = len([e for e in employees if e.get("employment_status") == "在職"])
    inactive = total - active
    enabled = len([e for e in employees if int(e.get("account_enabled") or 0)])
    disabled = total - enabled
    departments = len(set([e.get("department") for e in employees if e.get("department")]))

    # 各部門人數
    dept_count = {}
    for e in employees:
        d = e.get("department") or "未分類"
        dept_count[d] = dept_count.get(d, 0) + 1
    dept_sorted = sorted(dept_count.items(), key=lambda x: -x[1])[:10]
    dept_labels = str([d[0] for d in dept_sorted]).replace("'", '"')
    dept_values = str([d[1] for d in dept_sorted])

    # 職務類型分布
    role_count = {}
    for e in employees:
        r = _role_label_zh(e.get("role") or "")
        role_count[r] = role_count.get(r, 0) + 1
    role_labels = str(list(role_count.keys())).replace("'", '"')
    role_values = str(list(role_count.values()))

    # 各部門平均薪資
    dept_salary = {}
    dept_scnt = {}
    for e in employees:
        d = e.get("department") or "未分類"
        sal = int(e.get("base_salary") or e.get("monthly_salary") or 0)
        if sal > 0:
            dept_salary[d] = dept_salary.get(d, 0) + sal
            dept_scnt[d] = dept_scnt.get(d, 0) + 1
    salary_sorted = sorted(
        [(d, dept_salary[d] // dept_scnt[d]) for d in dept_salary if dept_scnt[d] > 0],
        key=lambda x: -x[1]
    )[:8]
    import json as _json
    if salary_sorted:
        salary_data = _json.dumps({"labels": [s[0] for s in salary_sorted], "values": [s[1] for s in salary_sorted]}, ensure_ascii=False)
    else:
        salary_data = '{"labels":["無薪資資料"],"values":[0]}'

    body = f"""
      <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>

      <section class="summary">
        <div class="summary-card"><div class="summary-label">員工總數</div><div class="summary-value">{total}</div></div>
        <div class="summary-card"><div class="summary-label">在職員工</div><div class="summary-value">{active}</div></div>
        <div class="summary-card"><div class="summary-label">帳號啟用</div><div class="summary-value">{enabled}</div></div>
        <div class="summary-card"><div class="summary-label">部門數</div><div class="summary-value">{departments}</div></div>
      </section>

      <section class="dashboard-grid">

        <!-- 第一排：部門長條圖（全寬） -->
        <div class="dash-panel">
          <div class="dash-panel-title">📊 各部門人數分布</div>
          <canvas id="deptChart" height="60"></canvas>
        </div>

        <!-- 第二排：3個圓餅圖 -->
        <div class="dash-row col-1-1-1">
          <div class="dash-panel">
            <div class="dash-panel-title">👤 在職狀況</div>
            <canvas id="statusChart" height="120"></canvas>
          </div>
          <div class="dash-panel">
            <div class="dash-panel-title">🔑 帳號狀態</div>
            <canvas id="accountChart" height="120"></canvas>
          </div>
          <div class="dash-panel">
            <div class="dash-panel-title">💼 職務類型分布</div>
            <canvas id="roleChart" height="120"></canvas>
          </div>
        </div>

        <!-- 第三排：待辦 + 薪資概況 -->
        <div class="dash-row col-1-1">
          <div class="dash-panel">
            <div class="dash-panel-title">📋 待辦事項</div>
            <ul class="dash-list">
              <li><a href="/admin/hr/leave-requests">→ 請假審核 — 查看待審假單</a></li>
              <li><a href="/admin/hr/leave-management">→ 排休管理 — 確認本月值班安排</a></li>
              <li><a href="/admin/hr/passwords">→ 帳號管理 — 檢查停用或異常帳號</a></li>
              <li><a href="/admin/hr/change-logs">→ 異動紀錄 — 查看近期人事異動</a></li>
              <li><a href="/admin/hr/employee-adjust">→ 薪資調整 — 確認待更新薪資</a></li>
            </ul>
          </div>
          <div class="dash-panel">
            <div class="dash-panel-title">💰 各部門平均薪資</div>
            <canvas id="salaryChart" height="120"></canvas>
          </div>
        </div>

      </section>

      <script>
      window.addEventListener('load', function() {{
      new Chart(document.getElementById('deptChart'), {{
        type: 'bar',
        data: {{
          labels: {dept_labels},
          datasets: [{{ label: '人數', data: {dept_values},
            backgroundColor: 'rgba(29,78,216,0.75)', borderRadius: 6 }}]
        }},
        options: {{ plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }}
      }});

      // 在職狀況圓餅
      new Chart(document.getElementById('statusChart'), {{
        type: 'doughnut',
        data: {{
          labels: ['在職', '離職'],
          datasets: [{{ data: [{active}, {inactive}],
            backgroundColor: ['#16a34a','#e5e7eb'], borderWidth: 0 }}]
        }},
        options: {{ plugins: {{ legend: {{ position: 'bottom' }} }}, cutout: '65%' }}
      }});

      // 帳號狀態圓餅
      new Chart(document.getElementById('accountChart'), {{
        type: 'doughnut',
        data: {{
          labels: ['啟用', '停用'],
          datasets: [{{ data: [{enabled}, {disabled}],
            backgroundColor: ['#1d4ed8','#f87171'], borderWidth: 0 }}]
        }},
        options: {{ plugins: {{ legend: {{ position: 'bottom' }} }}, cutout: '65%' }}
      }});

      // 職務類型圓餅
      new Chart(document.getElementById('roleChart'), {{
        type: 'doughnut',
        data: {{
          labels: {role_labels},
          datasets: [{{ data: {role_values},
            backgroundColor: ['#7c3aed','#0891b2','#d97706','#16a34a','#dc2626','#64748b'], borderWidth: 0 }}]
        }},
        options: {{ plugins: {{ legend: {{ position: 'bottom' }} }}, cutout: '65%' }}
      }});

      // 薪資概況長條圖（依部門平均月薪）
      const salaryData = {salary_data};
      new Chart(document.getElementById('salaryChart'), {{
        type: 'bar',
        data: {{
          labels: salaryData.labels,
          datasets: [{{ label: '平均月薪', data: salaryData.values,
            backgroundColor: 'rgba(16,163,74,0.75)', borderRadius: 6 }}]
        }},
        options: {{ plugins: {{ legend: {{ display: false }} }},
          scales: {{ y: {{ beginAtZero: true, ticks: {{ callback: v => '$' + v.toLocaleString() }} }} }} }}
      }});
      }});
      </script>
    """

    return _layout("人事系統總覽", "home", _user_line(user), body)



@router.get("/admin/hr/employees", response_class=HTMLResponse)
def hr_employees_page(request: Request):
    user = _user_or_redirect(request, "/admin/hr/employees")
    if not isinstance(user, dict):
        return user

    employees = _load_employees()

    departments = sorted(set([str(e.get("department") or "") for e in employees if e.get("department")]))
    roles = sorted(set([_role_label_zh(e.get("role", "")) for e in employees if e.get("role")]))

    dept_options = "".join([f"<option value='{escape(d)}'>{escape(d)}</option>" for d in departments])
    role_options = "".join([f"<option value='{escape(r)}'>{escape(r)}</option>" for r in roles])

    rows = []
    for emp in employees:
        staff_code = escape(emp.get("staff_code", ""))
        display_name = escape(emp.get("display_name", ""))
        department = escape(emp.get("department", ""))
        position = escape(emp.get("position_title", ""))
        role_label = _role_label_zh(emp.get("role", ""))
        employment = escape(emp.get("employment_status", ""))
        account_enabled = int(emp.get("account_enabled") or 0)
        account_text = "啟用" if account_enabled else "停用"
        account_class = "green" if account_enabled else "red"

        rows.append(
            f"<tr data-dept='{department}' data-role='{escape(role_label)}' data-account='{account_text}'>"
            f"<td>{staff_code}</td>"
            f"<td>{display_name}</td>"
            f"<td>{department}</td>"
            f"<td>{position}</td>"
            f"<td>{escape(role_label)}</td>"
            f"<td>{escape(emp.get('phone',''))}</td>"
            f"<td>{escape(emp.get('email',''))}</td>"
            f"<td>{escape(emp.get('hire_date',''))}</td>"
            f"<td>{employment}</td>"
            f"<td><span class='pill {account_class}'>{account_text}</span></td>"
            f"</tr>"
        )

    body = f"""
<section class='panel' style='max-width:none;margin:0;'>
  <div class='panel-head'>員工名冊</div>

  <div style='display:flex;gap:10px;align-items:center;padding:12px 14px;border-bottom:1px solid #e2e8f0;background:#fff;flex-wrap:wrap;'>
    <input id='employeeSearch' placeholder='搜尋員工工號 / 姓名' oninput='filterEmployeeRows()' style='height:34px;width:220px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
    <select id='employeeDeptFilter' onchange='filterEmployeeRows()' style='height:34px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
      <option value=''>全部部門</option>
      {dept_options}
    </select>
    <select id='employeeRoleFilter' onchange='filterEmployeeRows()' style='height:34px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
      <option value=''>全部職務</option>
      {role_options}
    </select>
    <select id='employeeAccountFilter' onchange='filterEmployeeRows()' style='height:34px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
      <option value=''>全部帳號</option>
      <option value='啟用'>啟用</option>
      <option value='停用'>停用</option>
    </select>
  </div>

  <div class='table-wrap' style='min-height:auto;max-height:calc(100vh - 280px);'>
    <table style='width:100%;min-width:1000px;margin-left:0;border-collapse:collapse;'>
      <thead>
        <tr>
          <th onclick='sortEmployeeTable(0)' style='cursor:pointer;width:120px;'>員工工號 ▲▼</th>
          <th onclick='sortEmployeeTable(1)' style='cursor:pointer;width:140px;'>姓名 ▲▼</th>
          <th style='width:120px;'>部門</th>
          <th style='width:150px;'>職稱</th>
          <th style='width:130px;'>職務</th>
          <th style='width:130px;'>手機</th>
          <th>Email</th>
          <th style='width:120px;'>到職日</th>
          <th style='width:90px;'>在職</th>
          <th style='width:90px;'>帳號</th>
        </tr>
      </thead>
      <tbody id='employeeRows'>{''.join(rows)}</tbody>
    </table>
  </div>
</section>

<script>
function filterEmployeeRows() {{
  const keyword = (document.getElementById("employeeSearch").value || "").trim().toLowerCase();
  const dept = document.getElementById("employeeDeptFilter").value || "";
  const role = document.getElementById("employeeRoleFilter").value || "";
  const account = document.getElementById("employeeAccountFilter").value || "";

  Array.from(document.querySelectorAll("#employeeRows tr")).forEach(function(row) {{
    const staffCode = (row.children[0]?.innerText || "").toLowerCase();
    const name = (row.children[1]?.innerText || "").toLowerCase();
    const rowDept = row.getAttribute("data-dept") || "";
    const rowRole = row.getAttribute("data-role") || "";
    const rowAccount = row.getAttribute("data-account") || "";

    let show = true;
    if (keyword && !(staffCode.includes(keyword) || name.includes(keyword))) show = false;
    if (dept && rowDept !== dept) show = false;
    if (role && rowRole !== role) show = false;
    if (account && rowAccount !== account) show = false;

    row.style.display = show ? "" : "none";
  }});
}}

function sortEmployeeTable(colIndex) {{
  const tbody = document.getElementById("employeeRows");
  const currentCol = tbody.getAttribute("data-sort-col");
  const currentDir = tbody.getAttribute("data-sort-dir") || "asc";
  const nextDir = (currentCol === String(colIndex) && currentDir === "asc") ? "desc" : "asc";

  const rows = Array.from(tbody.querySelectorAll("tr"));
  rows.sort(function(a, b) {{
    const av = (a.children[colIndex]?.innerText || "").trim();
    const bv = (b.children[colIndex]?.innerText || "").trim();
    const result = av.localeCompare(bv, "zh-Hant", {{numeric:true}});
    return nextDir === "asc" ? result : -result;
  }});

  rows.forEach(function(row) {{ tbody.appendChild(row); }});
  tbody.setAttribute("data-sort-col", String(colIndex));
  tbody.setAttribute("data-sort-dir", nextDir);
}}
</script>
"""

    return _layout("員工名冊", "employees", _user_line(user), body)


@router.get("/api/admin/hr/employees")
def api_hr_employees(request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return Response(_dumps({"ok": False, "error": "login required"}), status_code=401, media_type="application/json; charset=utf-8")
    return Response(_dumps({"ok": True, "items": _load_employees()}), media_type="application/json; charset=utf-8")



@router.post("/api/admin/hr/permissions/save")
async def api_hr_permissions_save(request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return Response(
            _dumps({"ok": False, "error": "login required"}),
            status_code=401,
            media_type="application/json; charset=utf-8",
        )

    _hr_db_init()

    raw = await request.body()
    try:
        data = json.loads(raw.decode("utf-8") or "{}")
    except Exception:
        data = {}

    items = data.get("items") or []
    if not isinstance(items, list):
        return Response(
            _dumps({"ok": False, "error": "資料格式錯誤"}),
            status_code=400,
            media_type="application/json; charset=utf-8",
        )

    valid_apps = {key for key, _label in APP_OPTIONS}
    full_apps = [key for key, _label in APP_OPTIONS]

    updated = 0

    with engine.begin() as conn:
        for item in items:
            if not isinstance(item, dict):
                continue

            staff_code = str(item.get("staff_code") or "").strip()
            apps_raw = item.get("app_access") or []

            if not staff_code:
                continue

            apps = []
            if isinstance(apps_raw, list):
                for app in apps_raw:
                    app_key = str(app or "").strip()
                    if app_key in valid_apps and app_key not in apps:
                        apps.append(app_key)

            row = conn.execute(text("""
                SELECT staff_code, role, app_access
                FROM employee_profiles
                WHERE staff_code = :staff_code
                LIMIT 1
            """), {"staff_code": staff_code}).mappings().first()

            if not row:
                continue

            # 系統管理員 admin 固定保留全權限，避免誤關後進不來。
            if staff_code == "admin" or str(row.get("role") or "") == "admin":
                apps = full_apps

            before_text = str(row.get("app_access") or "")
            after_text = _dumps(apps)

            conn.execute(text("""
                UPDATE employee_profiles
                SET app_access = :app_access,
                    updated_at = datetime('now')
                WHERE staff_code = :staff_code
            """), {
                "staff_code": staff_code,
                "app_access": after_text,
            })

            try:
                conn.execute(text("""
                    INSERT INTO hr_change_logs (
                        operator_staff_code,
                        action_type,
                        target_staff_code,
                        before_text,
                        after_text,
                        note,
                        created_at
                    )
                    VALUES (
                        :operator_staff_code,
                        'app_access_update',
                        :target_staff_code,
                        :before_text,
                        :after_text,
                        '人事系統權限管理儲存',
                        datetime('now')
                    )
                """), {
                    "operator_staff_code": str(user.get("staff_code") or ""),
                    "target_staff_code": staff_code,
                    "before_text": before_text,
                    "after_text": after_text,
                })
            except Exception:
                pass

            updated += 1

    return Response(
        _dumps({"ok": True, "updated": updated}),
        media_type="application/json; charset=utf-8",
    )



@router.get("/admin/hr/permissions", response_class=HTMLResponse)
def hr_permissions_page(request: Request):
    user = _user_or_redirect(request, "/admin/hr/permissions")
    if not isinstance(user, dict):
        return user

    app_label_map = {
        "dispatch": "派工",
        "billing": "帳務",
        "engineering": "工程",
        "sales": "業務",
        "hr": "人事",
        "admin": "後台",
    }

    headers = "".join([
        f"<th class='app-col' style='text-align:center'>{escape(app_label_map.get(key, label.replace(' APP', '')))}</th>"
        for key, label in APP_OPTIONS
    ])

    employees = _load_employees()
    departments = sorted(set([str(e.get("department") or "") for e in employees if e.get("department")]))
    roles = sorted(set([_role_label_zh(e.get("role", "")) for e in employees if e.get("role")]))

    dept_options = "".join([f"<option value='{escape(d)}'>{escape(d)}</option>" for d in departments])
    role_options = "".join([f"<option value='{escape(r)}'>{escape(r)}</option>" for r in roles])

    rows = []

    for emp in employees:
        staff_code = str(emp.get("staff_code", "") or "")
        display_name = str(emp.get("display_name", "") or "")
        department = str(emp.get("department", "") or "")
        role_label = _role_label_zh(emp.get("role", ""))
        apps = emp.get("app_access") or []
        is_admin = staff_code == "admin" or str(emp.get("role") or "") == "admin"

        cells = []
        for key, label in APP_OPTIONS:
            checked = "checked" if key in apps or is_admin else ""
            disabled = "disabled" if is_admin else ""
            title = "系統管理員固定全權限" if is_admin else "可勾選後儲存"
            cells.append(
                "<td class='app-col' style='text-align:center'>"
                f"<input class='permission-check' data-app='{escape(key)}' type='checkbox' {checked} {disabled} title='{escape(title)}'>"
                "</td>"
            )

        admin_note = "<span class='pill yellow'>固定全權限</span>" if is_admin else ""

        rows.append(
            f"<tr data-staff-code='{escape(staff_code)}' data-dept='{escape(department)}' data-role='{escape(role_label)}'>"
            f"<td class='staff-col'>{escape(staff_code)}</td>"
            f"<td class='name-col'>{escape(display_name)} {admin_note}</td>"
            f"<td class='dept-col'>{escape(department)}</td>"
            f"<td class='role-col'>{escape(role_label)}</td>"
            + "".join(cells) +
            "</tr>"
        )

    body = """
      <section class='panel' style='max-width:none;margin:0;'>
        <div class='panel-head'>
          <span>系統權限矩陣</span>
          <span>
            <button class='btn primary' style='padding:3px 8px;font-size:12px;border-radius:5px;' type='button' onclick='savePermissionMatrix()'>儲存權限</button>
            <button class='btn' type='button' onclick='location.reload()'>重新整理</button>
          </span>
        </div>

        <div style='display:flex;gap:10px;align-items:center;padding:12px 14px;border-bottom:1px solid #e2e8f0;background:#fff;flex-wrap:wrap;'>
          <input id='permissionSearch' placeholder='搜尋員工工號 / 姓名' oninput='filterPermissionRows()' style='height:34px;width:220px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
          <select id='permissionDeptFilter' onchange='filterPermissionRows()' style='height:34px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
            <option value=''>全部部門</option>
            __DEPT_OPTIONS__
          </select>
          <select id='permissionRoleFilter' onchange='filterPermissionRows()' style='height:34px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
            <option value=''>全部職務</option>
            __ROLE_OPTIONS__
          </select>
        </div>

        <div class='table-wrap' style='min-height:auto;max-height:calc(100vh - 280px);'>
          <table id='permissionTable' style='width:100%;min-width:0;table-layout:fixed;border-collapse:collapse;'>
            <thead>
              <tr>
                <th onclick='sortPermissionTable(0)' style='cursor:pointer;width:105px;'>員工工號 ▲▼</th>
                <th onclick='sortPermissionTable(1)' style='cursor:pointer;width:130px;'>姓名 ▲▼</th>
                <th style='width:115px;'>部門</th>
                <th style='width:120px;'>職務</th>
                __HEADERS__
              </tr>
            </thead>
            <tbody id='permissionRows'>
              __ROWS__
            </tbody>
          </table>
        </div>
      </section>

      <script>
        function filterPermissionRows() {
          const keyword = (document.getElementById("permissionSearch").value || "").trim().toLowerCase();
          const dept = document.getElementById("permissionDeptFilter").value || "";
          const role = document.getElementById("permissionRoleFilter").value || "";

          Array.from(document.querySelectorAll("#permissionRows tr")).forEach(function(row) {
            const staffCode = (row.children[0]?.innerText || "").toLowerCase();
            const name = (row.children[1]?.innerText || "").toLowerCase();
            const rowDept = row.getAttribute("data-dept") || "";
            const rowRole = row.getAttribute("data-role") || "";

            let show = true;
            if (keyword && !(staffCode.includes(keyword) || name.includes(keyword))) show = false;
            if (dept && rowDept !== dept) show = false;
            if (role && rowRole !== role) show = false;

            row.style.display = show ? "" : "none";
          });
        }

        function sortPermissionTable(colIndex) {
          const tbody = document.getElementById("permissionRows");
          const currentCol = tbody.getAttribute("data-sort-col");
          const currentDir = tbody.getAttribute("data-sort-dir") || "asc";
          const nextDir = (currentCol === String(colIndex) && currentDir === "asc") ? "desc" : "asc";

          const rows = Array.from(tbody.querySelectorAll("tr"));

          rows.sort(function(a, b) {
            const av = (a.children[colIndex]?.innerText || "").trim();
            const bv = (b.children[colIndex]?.innerText || "").trim();
            const result = av.localeCompare(bv, "zh-Hant", {numeric:true});
            return nextDir === "asc" ? result : -result;
          });

          rows.forEach(function(row) { tbody.appendChild(row); });
          tbody.setAttribute("data-sort-col", String(colIndex));
          tbody.setAttribute("data-sort-dir", nextDir);
        }

        async function savePermissionMatrix() {
          const rows = Array.from(document.querySelectorAll("tr[data-staff-code]"));

          const items = rows.map(function(row) {
            const staffCode = row.getAttribute("data-staff-code") || "";
            const apps = Array.from(row.querySelectorAll(".permission-check"))
              .filter(function(box) { return box.checked; })
              .map(function(box) { return box.getAttribute("data-app") || ""; })
              .filter(Boolean);

            return {
              staff_code: staffCode,
              app_access: apps
            };
          });

          const res = await fetch("/api/admin/hr/permissions/save", {
            method: "POST",
            headers: {"Content-Type": "application/json; charset=utf-8"},
            credentials: "same-origin",
            body: JSON.stringify({items: items})
          });

          let data = {};
          try {
            data = await res.json();
          } catch (err) {}

          if (!res.ok || !data.ok) {
            alert(data.error || "權限儲存失敗");
            return;
          }

          alert("權限已儲存，共更新 " + data.updated + " 筆。");
          location.reload();
        }
      </script>
    """

    body = (
        body
        .replace("__HEADERS__", headers)
        .replace("__ROWS__", "".join(rows))
        .replace("__DEPT_OPTIONS__", dept_options)
        .replace("__ROLE_OPTIONS__", role_options)
    )

    return _layout("權限管理", "permissions", _user_line(user), body)


@router.post("/api/admin/hr/account/toggle")
async def api_admin_hr_account_toggle(request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return Response(_dumps({"ok": False, "error": "login required"}), status_code=401, media_type="application/json; charset=utf-8")

    data = await request.json()
    staff_code = str(data.get("staff_code") or "").strip()

    if not staff_code:
        return Response(_dumps({"ok": False, "error": "missing staff_code"}), status_code=400, media_type="application/json; charset=utf-8")

    _hr_db_init()

    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT enabled FROM employee_accounts WHERE staff_code=:staff_code"),
            {"staff_code": staff_code}
        ).first()

        if not row:
            return Response(_dumps({"ok": False, "error": "employee account not found"}), status_code=404, media_type="application/json; charset=utf-8")

        old_enabled = int(row[0] or 0)
        new_enabled = 0 if old_enabled else 1

        conn.execute(text("""
            UPDATE employee_accounts
            SET enabled=:enabled,
                updated_at=datetime('now')
            WHERE staff_code=:staff_code
        """), {
            "enabled": new_enabled,
            "staff_code": staff_code,
        })

        try:
            conn.execute(text("""
                INSERT INTO hr_change_logs (
                    operator_staff_code,
                    action_type,
                    target_staff_code,
                    before_text,
                    after_text,
                    note,
                    created_at
                )
                VALUES (
                    :operator_staff_code,
                    'account_toggle',
                    :target_staff_code,
                    :before_text,
                    :after_text,
                    '密碼管理切換帳號狀態',
                    datetime('now')
                )
            """), {
                "operator_staff_code": str(user.get("staff_code") or ""),
                "target_staff_code": staff_code,
                "before_text": str(old_enabled),
                "after_text": str(new_enabled),
            })
        except Exception:
            pass

    return Response(_dumps({"ok": True, "staff_code": staff_code, "enabled": new_enabled}), media_type="application/json; charset=utf-8")




@router.post("/api/admin/hr/account/set-pin")
async def api_admin_hr_account_set_pin(request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return Response(_dumps({"ok": False, "error": "login required"}), status_code=401, media_type="application/json; charset=utf-8")

    data = await request.json()
    staff_code = str(data.get("staff_code") or "").strip()
    new_pin = str(data.get("new_pin") or "").strip()

    if not staff_code:
        return Response(_dumps({"ok": False, "error": "missing staff_code"}), status_code=400, media_type="application/json; charset=utf-8")

    if not new_pin or len(new_pin) < 4 or len(new_pin) > 12 or not new_pin.isdigit():
        return Response(_dumps({"ok": False, "error": "PIN 必須是 4 到 12 位數字"}), status_code=400, media_type="application/json; charset=utf-8")

    _hr_db_init()
    salt = secrets.token_hex(8)
    pin_hash = _hash_pin(new_pin, salt)

    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT staff_code FROM employee_accounts WHERE staff_code=:staff_code"),
            {"staff_code": staff_code}
        ).first()

        if not row:
            return Response(_dumps({"ok": False, "error": "employee account not found"}), status_code=404, media_type="application/json; charset=utf-8")

        conn.execute(text("""
            UPDATE employee_accounts
            SET pin_salt=:pin_salt,
                pin_hash=:pin_hash,
                updated_at=datetime('now')
            WHERE staff_code=:staff_code
        """), {
            "pin_salt": salt,
            "pin_hash": pin_hash,
            "staff_code": staff_code,
        })

        try:
            conn.execute(text("""
                INSERT INTO hr_change_logs (
                    operator_staff_code,
                    action_type,
                    target_staff_code,
                    before_text,
                    after_text,
                    note,
                    created_at
                )
                VALUES (
                    :operator_staff_code,
                    'pin_update',
                    :target_staff_code,
                    '',
                    'pin_hash_updated',
                    '密碼管理修改 PIN',
                    datetime('now')
                )
            """), {
                "operator_staff_code": str(user.get("staff_code") or ""),
                "target_staff_code": staff_code,
            })
        except Exception:
            pass

    return Response(_dumps({"ok": True, "staff_code": staff_code}), media_type="application/json; charset=utf-8")




@router.get("/admin/hr/passwords", response_class=HTMLResponse)
def hr_passwords_page(request: Request):
    user = _user_or_redirect(request, "/admin/hr/passwords")
    if not isinstance(user, dict):
        return user

    employees = _load_employees()
    departments = sorted(set([str(e.get("department") or "") for e in employees if e.get("department")]))
    dept_options = "".join([f"<option value='{escape(d)}'>{escape(d)}</option>" for d in departments])

    rows = []
    for emp in employees:
        staff_code_raw = str(emp.get("staff_code") or "")
        staff_code = escape(staff_code_raw)
        display_name = escape(emp.get("display_name", ""))
        department = escape(emp.get("department", ""))

        enabled = int(emp.get("account_enabled") or 0)
        status_class = "green" if enabled else "red"
        status_text = "啟用" if enabled else "停用"
        toggle_text = "停用" if enabled else "啟用"

        staff_code_js = json.dumps(staff_code_raw, ensure_ascii=False)
        display_name_js = json.dumps(str(emp.get("display_name") or ""), ensure_ascii=False)
        toggle_text_js = json.dumps(toggle_text, ensure_ascii=False)

        rows.append(
            f"<tr data-dept='{department}' data-status='{status_text}'>"
            f"<td>{staff_code}</td>"
            f"<td>{display_name}</td>"
            f"<td>{department}</td>"
            f"<td><span class='pill {status_class}'>{status_text}</span></td>"
            f"<td>"
            f"<button class='btn primary' style='padding:3px 8px;font-size:12px;border-radius:5px;' onclick='openResetDialog({staff_code_js}, {display_name_js})'>重設</button>"
            f" <button class='btn' style='padding:3px 7px;font-size:12px;margin-left:3px;' onclick='openPinDialog({staff_code_js}, {display_name_js})'>修改</button>"
            f" <button class='btn' style='padding:3px 7px;font-size:12px;margin-left:3px;' onclick='openToggleDialog({staff_code_js}, {display_name_js}, {toggle_text_js})'>{toggle_text}</button>"
            f"</td>"
            f"</tr>"
        )

    body = f"""
<section class='panel' style='max-width:none;margin:0;'>
  <div class='panel-head'>密碼管理 / 帳號 PIN 管理</div>

  <div style='display:flex;gap:10px;align-items:center;padding:12px 14px;border-bottom:1px solid #e2e8f0;background:#fff;flex-wrap:wrap;'>
    <input id='passwordSearch' placeholder='搜尋員工工號 / 姓名' oninput='filterPasswordRows()' style='height:34px;width:220px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
    <select id='passwordDeptFilter' onchange='filterPasswordRows()' style='height:34px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
      <option value=''>全部部門</option>
      {dept_options}
    </select>
    <select id='passwordStatusFilter' onchange='filterPasswordRows()' style='height:34px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
      <option value=''>全部狀態</option>
      <option value='啟用'>啟用</option>
      <option value='停用'>停用</option>
    </select>
  </div>

  <div class='table-wrap' style='min-height:auto;max-height:calc(100vh - 300px);'>
    <table style='width:100%;min-width:900px;margin-left:0;border-collapse:collapse;'>
      <thead>
        <tr>
          <th onclick='sortPasswordTable(0)' style='cursor:pointer;width:120px;'>員工工號 ▲▼</th>
          <th onclick='sortPasswordTable(1)' style='cursor:pointer;width:140px;'>姓名 ▲▼</th>
          <th style='width:130px;'>部門</th>
          <th style='width:120px;'>帳號狀態</th>
          <th style='width:220px;'>操作</th>
        </tr>
      </thead>
      <tbody id='passwordRows'>{''.join(rows)}</tbody>
    </table>
  </div>
</section>

<div id="modalMask" style="display:none;position:fixed;inset:0;background:rgba(15,23,42,.42);z-index:9999;align-items:center;justify-content:center;">
  <div style="width:420px;max-width:calc(100vw - 32px);background:#fff;border-radius:18px;box-shadow:0 24px 70px rgba(15,23,42,.28);overflow:hidden;">
    <div id="modalTitle" style="padding:18px 20px;font-size:20px;font-weight:1000;color:#102348;border-bottom:1px solid #e2e8f0;">確認</div>
    <div id="modalBody" style="padding:18px 20px;color:#334155;font-size:15px;font-weight:800;line-height:1.7;"></div>
    <div id="modalActions" style="padding:14px 20px;display:flex;gap:10px;justify-content:flex-end;background:#f8fafc;border-top:1px solid #e2e8f0;"></div>
  </div>
</div>

<script>
let modalAction = null;

function closeModal() {{
  document.getElementById("modalMask").style.display = "none";
  modalAction = null;
}}

function showModal(title, bodyHtml, confirmText, confirmClass, action) {{
  document.getElementById("modalTitle").innerText = title;
  document.getElementById("modalBody").innerHTML = bodyHtml;
  document.getElementById("modalActions").innerHTML =
    '<button class="btn" type="button" onclick="closeModal()">取消</button>' +
    '<button class="btn ' + confirmClass + '" type="button" onclick="runModalAction()">' + confirmText + '</button>';
  modalAction = action;
  document.getElementById("modalMask").style.display = "flex";
}}

async function runModalAction() {{
  if (typeof modalAction === "function") await modalAction();
}}

function openToggleDialog(staffCode, displayName, actionText) {{
  showModal("確認帳號狀態", "確定要「" + actionText + "」<b>" + displayName + "</b> 的帳號嗎？", actionText, actionText === "停用" ? "red" : "green", async function() {{
    await toggleAccount(staffCode);
  }});
}}

function openPinDialog(staffCode, displayName) {{
  showModal("修改 PIN",
    "<div>員工：<b>" + displayName + "</b></div><div style='margin-top:10px;'>請輸入新 PIN：</div><input id='newPinInput' type='password' inputmode='numeric' style='width:100%;height:38px;margin-top:8px;border:1px solid #cbd5e1;border-radius:10px;padding:0 10px;font-size:16px;'>",
    "儲存", "primary", async function() {{
      const pin = document.getElementById("newPinInput").value.trim();
      await setPin(staffCode, pin);
    }}
  );
}}

function openResetDialog(staffCode, displayName) {{
  const randomPin = String(Math.floor(100000 + Math.random() * 900000));
  showModal("重設 PIN",
    "<div>系統將為 <b>" + displayName + "</b> 產生一次性新 PIN。</div><div style='margin-top:12px;font-size:22px;font-weight:1000;color:#1d4ed8;'>新 PIN：" + randomPin + "</div><div style='margin-top:8px;color:#991b1b;'>此 PIN 只會顯示這一次，請立即記錄。</div>",
    "寫入新 PIN", "primary", async function() {{
      await setPin(staffCode, randomPin);
    }}
  );
}}

async function toggleAccount(staffCode) {{
  const res = await fetch("/api/admin/hr/account/toggle", {{
    method: "POST",
    headers: {{"Content-Type": "application/json; charset=utf-8"}},
    credentials: "same-origin",
    body: JSON.stringify({{staff_code: staffCode}})
  }});
  const data = await res.json();
  if (!res.ok || !data.ok) {{
    alert(data.error || "切換失敗");
    return;
  }}
  closeModal();
  location.reload();
}}

async function setPin(staffCode, newPin) {{
  if (!newPin) {{
    alert("請輸入 PIN");
    return;
  }}
  const res = await fetch("/api/admin/hr/account/set-pin", {{
    method: "POST",
    headers: {{"Content-Type": "application/json; charset=utf-8"}},
    credentials: "same-origin",
    body: JSON.stringify({{staff_code: staffCode, new_pin: newPin}})
  }});
  const data = await res.json();
  if (!res.ok || !data.ok) {{
    alert(data.error || "PIN 修改失敗");
    return;
  }}
  closeModal();
  alert("PIN 已更新");
  location.reload();
}}

function filterPasswordRows() {{
  const keyword = (document.getElementById("passwordSearch").value || "").trim().toLowerCase();
  const dept = document.getElementById("passwordDeptFilter").value || "";
  const status = document.getElementById("passwordStatusFilter").value || "";

  Array.from(document.querySelectorAll("#passwordRows tr")).forEach(function(row) {{
    const staffCode = (row.children[0]?.innerText || "").toLowerCase();
    const name = (row.children[1]?.innerText || "").toLowerCase();
    const rowDept = row.getAttribute("data-dept") || "";
    const rowStatus = row.getAttribute("data-status") || "";
    let show = true;
    if (keyword && !(staffCode.includes(keyword) || name.includes(keyword))) show = false;
    if (dept && rowDept !== dept) show = false;
    if (status && rowStatus !== status) show = false;
    row.style.display = show ? "" : "none";
  }});
}}

function sortPasswordTable(colIndex) {{
  const tbody = document.getElementById("passwordRows");
  const currentCol = tbody.getAttribute("data-sort-col");
  const currentDir = tbody.getAttribute("data-sort-dir") || "asc";
  const nextDir = (currentCol === String(colIndex) && currentDir === "asc") ? "desc" : "asc";
  const rows = Array.from(tbody.querySelectorAll("tr"));
  rows.sort(function(a, b) {{
    const av = (a.children[colIndex]?.innerText || "").trim();
    const bv = (b.children[colIndex]?.innerText || "").trim();
    const result = av.localeCompare(bv, "zh-Hant", {{numeric:true}});
    return nextDir === "asc" ? result : -result;
  }});
  rows.forEach(function(row) {{ tbody.appendChild(row); }});
  tbody.setAttribute("data-sort-col", String(colIndex));
  tbody.setAttribute("data-sort-dir", nextDir);
}}
</script>
"""

    return _layout("密碼管理", "passwords", _user_line(user), body)

def _virtual_leave_requests(employees):
    frontline = [e for e in employees if e.get("department") in FRONTLINE_DEPARTMENTS and e.get("employment_status") == "在職"] or VIRTUAL_EMPLOYEES
    seeds = [("2026-05-01", "排休", "國定假日輪休"), ("2026-05-04", "特休", "家庭因素"), ("2026-05-08", "事假", "個人事務"), ("2026-05-15", "病假", "門診"), ("2026-05-22", "排休", "排休"), ("2026-06-05", "公假", "教育訓練"), ("2026-06-19", "排休", "端午輪休"), ("2026-06-22", "特休", "特休")]
    rows = []
    for i, (day, leave_type, reason) in enumerate(seeds):
        emp = frontline[i % len(frontline)]
        rows.append({"id": f"LV-20260506-{i+1:03d}", "date": day, "staff_code": emp.get("staff_code",""), "display_name": emp.get("display_name",""), "department": emp.get("department",""), "leave_type": leave_type, "reason": reason, "status": "已核准" if i % 3 else "待審核"})
    return rows



def _hr_leave_db_init():
    _hr_db_init()
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS hr_leave_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                leave_no TEXT UNIQUE DEFAULT '',
                staff_code TEXT DEFAULT '',
                display_name TEXT DEFAULT '',
                department TEXT DEFAULT '',
                leave_date TEXT DEFAULT '',
                leave_type TEXT DEFAULT '',
                reason TEXT DEFAULT '',
                status TEXT DEFAULT '待審核',
                review_note TEXT DEFAULT '',
                reviewed_by TEXT DEFAULT '',
                reviewed_at TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))

        count = conn.execute(text("SELECT COUNT(*) FROM hr_leave_requests")).scalar() or 0
        if count == 0:
            employees = _load_employees()
            for row in _virtual_leave_requests(employees):
                conn.execute(text("""
                    INSERT INTO hr_leave_requests (
                        leave_no, staff_code, display_name, department,
                        leave_date, leave_type, reason, status,
                        created_at, updated_at
                    )
                    VALUES (
                        :leave_no, :staff_code, :display_name, :department,
                        :leave_date, :leave_type, :reason, :status,
                        datetime('now'), datetime('now')
                    )
                """), {
                    "leave_no": row.get("id", ""),
                    "staff_code": row.get("staff_code", ""),
                    "display_name": row.get("display_name", ""),
                    "department": row.get("department", ""),
                    "leave_date": row.get("date", ""),
                    "leave_type": row.get("leave_type", ""),
                    "reason": row.get("reason", ""),
                    "status": row.get("status", "待審核"),
                })


@router.post("/api/admin/hr/leave-requests/review")
async def api_hr_leave_request_review(request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return Response(_dumps({"ok": False, "error": "login required"}), status_code=401, media_type="application/json; charset=utf-8")

    data = await request.json()
    leave_id = str(data.get("id") or "").strip()
    action = str(data.get("action") or "").strip()
    note = str(data.get("note") or "").strip()

    if not leave_id:
        return Response(_dumps({"ok": False, "error": "missing id"}), status_code=400, media_type="application/json; charset=utf-8")

    if action not in ["approve", "reject"]:
        return Response(_dumps({"ok": False, "error": "bad action"}), status_code=400, media_type="application/json; charset=utf-8")

    new_status = "已核准" if action == "approve" else "已退回"
    operator = str(user.get("staff_code") or user.get("display_name") or "")

    _hr_leave_db_init()

    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT id, staff_code, status
            FROM hr_leave_requests
            WHERE id = :id
        """), {"id": leave_id}).mappings().first()

        if not row:
            return Response(_dumps({"ok": False, "error": "leave request not found"}), status_code=404, media_type="application/json; charset=utf-8")

        old_status = str(row.get("status") or "")

        conn.execute(text("""
            UPDATE hr_leave_requests
            SET status = :status,
                review_note = :review_note,
                reviewed_by = :reviewed_by,
                reviewed_at = datetime('now'),
                updated_at = datetime('now')
            WHERE id = :id
        """), {
            "id": leave_id,
            "status": new_status,
            "review_note": note,
            "reviewed_by": operator,
        })

        try:
            conn.execute(text("""
                INSERT INTO hr_change_logs (
                    operator_staff_code,
                    action_type,
                    target_staff_code,
                    before_text,
                    after_text,
                    note,
                    created_at
                )
                VALUES (
                    :operator_staff_code,
                    'leave_review',
                    :target_staff_code,
                    :before_text,
                    :after_text,
                    :note,
                    datetime('now')
                )
            """), {
                "operator_staff_code": operator,
                "target_staff_code": str(row.get("staff_code") or ""),
                "before_text": old_status,
                "after_text": new_status,
                "note": "請假審核：" + new_status + ("；" + note if note else ""),
            })
        except Exception:
            pass

    return Response(_dumps({"ok": True, "status": new_status}), media_type="application/json; charset=utf-8")


@router.get("/admin/hr/leave-requests", response_class=HTMLResponse)
def hr_leave_requests_page(request: Request):
    user = _user_or_redirect(request, "/admin/hr/leave-requests")
    if not isinstance(user, dict):
        return user

    _hr_leave_db_init()

    with engine.begin() as conn:
        items = conn.execute(text("""
            SELECT id, leave_no, staff_code, display_name, department,
                   leave_date, leave_type, reason, status,
                   review_note, reviewed_by, reviewed_at, created_at
            FROM hr_leave_requests
            ORDER BY
              CASE status WHEN '待審核' THEN 1 WHEN '已核准' THEN 2 ELSE 3 END,
              leave_date DESC,
              id DESC
        """)).mappings().fetchall()

    departments = sorted(set([str(x.get("department") or "") for x in items if x.get("department")]))
    leave_types = sorted(set([str(x.get("leave_type") or "") for x in items if x.get("leave_type")]))

    dept_options = "".join([f"<option value='{escape(d)}'>{escape(d)}</option>" for d in departments])
    type_options = "".join([f"<option value='{escape(t)}'>{escape(t)}</option>" for t in leave_types])

    rows = []
    for row in items:
        status = str(row.get("status") or "待審核")
        cls = "green" if status == "已核准" else ("red" if status == "已退回" else "yellow")
        disabled = "disabled" if status != "待審核" else ""

        leave_id_js = json.dumps(str(row.get("id") or ""), ensure_ascii=False)
        name_js = json.dumps(str(row.get("display_name") or ""), ensure_ascii=False)

        rows.append(
            f"<tr data-dept='{escape(row.get('department',''))}' data-type='{escape(row.get('leave_type',''))}' data-status='{escape(status)}'>"
            f"<td>{escape(row.get('leave_no',''))}</td>"
            f"<td>{escape(row.get('leave_date',''))}</td>"
            f"<td>{escape(row.get('staff_code',''))}</td>"
            f"<td>{escape(row.get('display_name',''))}</td>"
            f"<td>{escape(row.get('department',''))}</td>"
            f"<td>{escape(row.get('leave_type',''))}</td>"
            f"<td>{escape(row.get('reason',''))}</td>"
            f"<td><span class='pill {cls}'>{escape(status)}</span></td>"
            f"<td>{escape(row.get('reviewed_by','') or '-')}</td>"
            f"<td>"
            f"<button class='btn green' style='padding:3px 8px;font-size:12px;border-radius:5px;' {disabled} onclick='openLeaveReviewDialog({leave_id_js}, {name_js}, \"approve\")'>核准</button>"
            f" <button class='btn red' style='padding:3px 8px;font-size:12px;border-radius:5px;margin-left:3px;' {disabled} onclick='openLeaveReviewDialog({leave_id_js}, {name_js}, \"reject\")'>退回</button>"
            f"</td>"
            f"</tr>"
        )

    body = f"""
<section class='panel' style='max-width:none;margin:0;'>
  <div class='panel-head'>請假審核</div>

  <div style='display:flex;gap:10px;align-items:center;padding:12px 14px;border-bottom:1px solid #e2e8f0;background:#fff;flex-wrap:wrap;'>
    <input id='leaveSearch' placeholder='搜尋單號 / 工號 / 姓名' oninput='filterLeaveRows()' style='height:34px;width:230px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
    <select id='leaveDeptFilter' onchange='filterLeaveRows()' style='height:34px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
      <option value=''>全部部門</option>
      {dept_options}
    </select>
    <select id='leaveTypeFilter' onchange='filterLeaveRows()' style='height:34px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
      <option value=''>全部假別</option>
      {type_options}
    </select>
    <select id='leaveStatusFilter' onchange='filterLeaveRows()' style='height:34px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;font-weight:800;'>
      <option value=''>全部狀態</option>
      <option value='待審核'>待審核</option>
      <option value='已核准'>已核准</option>
      <option value='已退回'>已退回</option>
    </select>
  </div>

  <div class='table-wrap' style='min-height:auto;max-height:calc(100vh - 300px);'>
    <table style='width:100%;min-width:1100px;margin-left:0;border-collapse:collapse;'>
      <thead>
        <tr>
          <th onclick='sortLeaveTable(0)' style='cursor:pointer;width:145px;'>單號 ▲▼</th>
          <th onclick='sortLeaveTable(1)' style='cursor:pointer;width:110px;'>日期 ▲▼</th>
          <th onclick='sortLeaveTable(2)' style='cursor:pointer;width:110px;'>員工工號 ▲▼</th>
          <th onclick='sortLeaveTable(3)' style='cursor:pointer;width:120px;'>姓名 ▲▼</th>
          <th style='width:120px;'>部門</th>
          <th style='width:100px;'>假別</th>
          <th>原因</th>
          <th style='width:100px;'>狀態</th>
          <th style='width:110px;'>審核人</th>
          <th style='width:150px;'>操作</th>
        </tr>
      </thead>
      <tbody id='leaveRows'>{''.join(rows)}</tbody>
    </table>
  </div>
</section>

<div id="leaveModalMask" style="display:none;position:fixed;inset:0;background:rgba(15,23,42,.42);z-index:9999;align-items:center;justify-content:center;">
  <div style="width:420px;max-width:calc(100vw - 32px);background:#fff;border-radius:18px;box-shadow:0 24px 70px rgba(15,23,42,.28);overflow:hidden;">
    <div id="leaveModalTitle" style="padding:18px 20px;font-size:20px;font-weight:1000;color:#102348;border-bottom:1px solid #e2e8f0;">請假審核</div>
    <div id="leaveModalBody" style="padding:18px 20px;color:#334155;font-size:15px;font-weight:800;line-height:1.7;"></div>
    <div id="leaveModalActions" style="padding:14px 20px;display:flex;gap:10px;justify-content:flex-end;background:#f8fafc;border-top:1px solid #e2e8f0;"></div>
  </div>
</div>

<script>
let leaveReviewPayload = null;

function closeLeaveModal() {{
  document.getElementById("leaveModalMask").style.display = "none";
  leaveReviewPayload = null;
}}

function openLeaveReviewDialog(id, name, action) {{
  const isApprove = action === "approve";
  leaveReviewPayload = {{id: id, action: action}};

  document.getElementById("leaveModalTitle").innerText = isApprove ? "核准請假" : "退回請假";
  document.getElementById("leaveModalBody").innerHTML =
    "<div>員工：<b>" + name + "</b></div>" +
    "<div style='margin-top:10px;'>審核備註：</div>" +
    "<textarea id='leaveReviewNote' style='width:100%;height:82px;margin-top:8px;border:1px solid #cbd5e1;border-radius:10px;padding:8px 10px;font-size:15px;'></textarea>";

  document.getElementById("leaveModalActions").innerHTML =
    '<button class="btn" type="button" onclick="closeLeaveModal()">取消</button>' +
    '<button class="btn ' + (isApprove ? "green" : "red") + '" type="button" onclick="submitLeaveReview()">' + (isApprove ? "核准" : "退回") + '</button>';

  document.getElementById("leaveModalMask").style.display = "flex";
}}

async function submitLeaveReview() {{
  if (!leaveReviewPayload) return;

  const note = (document.getElementById("leaveReviewNote").value || "").trim();

  const res = await fetch("/api/admin/hr/leave-requests/review", {{
    method: "POST",
    headers: {{"Content-Type": "application/json; charset=utf-8"}},
    credentials: "same-origin",
    body: JSON.stringify({{
      id: leaveReviewPayload.id,
      action: leaveReviewPayload.action,
      note: note
    }})
  }});

  const data = await res.json();
  if (!res.ok || !data.ok) {{
    alert(data.error || "審核失敗");
    return;
  }}

  closeLeaveModal();
  location.reload();
}}

function filterLeaveRows() {{
  const keyword = (document.getElementById("leaveSearch").value || "").trim().toLowerCase();
  const dept = document.getElementById("leaveDeptFilter").value || "";
  const type = document.getElementById("leaveTypeFilter").value || "";
  const status = document.getElementById("leaveStatusFilter").value || "";

  Array.from(document.querySelectorAll("#leaveRows tr")).forEach(function(row) {{
    const no = (row.children[0]?.innerText || "").toLowerCase();
    const code = (row.children[2]?.innerText || "").toLowerCase();
    const name = (row.children[3]?.innerText || "").toLowerCase();
    const rowDept = row.getAttribute("data-dept") || "";
    const rowType = row.getAttribute("data-type") || "";
    const rowStatus = row.getAttribute("data-status") || "";

    let show = true;
    if (keyword && !(no.includes(keyword) || code.includes(keyword) || name.includes(keyword))) show = false;
    if (dept && rowDept !== dept) show = false;
    if (type && rowType !== type) show = false;
    if (status && rowStatus !== status) show = false;

    row.style.display = show ? "" : "none";
  }});
}}

function sortLeaveTable(colIndex) {{
  const tbody = document.getElementById("leaveRows");
  const currentCol = tbody.getAttribute("data-sort-col");
  const currentDir = tbody.getAttribute("data-sort-dir") || "asc";
  const nextDir = (currentCol === String(colIndex) && currentDir === "asc") ? "desc" : "asc";
  const rows = Array.from(tbody.querySelectorAll("tr"));

  rows.sort(function(a, b) {{
    const av = (a.children[colIndex]?.innerText || "").trim();
    const bv = (b.children[colIndex]?.innerText || "").trim();
    const result = av.localeCompare(bv, "zh-Hant", {{numeric:true}});
    return nextDir === "asc" ? result : -result;
  }});

  rows.forEach(function(row) {{ tbody.appendChild(row); }});
  tbody.setAttribute("data-sort-col", String(colIndex));
  tbody.setAttribute("data-sort-dir", nextDir);
}}
</script>
"""

    return _layout("請假審核", "leave_requests", _user_line(user), body)


@router.get("/admin/hr/leave-management", response_class=HTMLResponse)
def hr_leave_management_page(request: Request):
    user = _user_or_redirect(request, "/admin/hr/leave-management")
    if not isinstance(user, dict): return user
    employees = _load_employees()
    leaves = _virtual_leave_requests(employees)
    active_by_dept = {dept: [e for e in employees if e.get("department") == dept and e.get("employment_status") == "在職"] for dept in FRONTLINE_DEPARTMENTS}
    leave_by_date_dept = {}
    for r in leaves:
        leave_by_date_dept.setdefault((r["date"], r["department"]), []).append(r)
    rows = []
    risk_days = 0
    total_days = 0
    holiday_count = 0
    d = date(2026, 5, 1)
    while d <= date(2026, 6, 30):
        key = d.isoformat()
        total_days += 1
        holiday = HOLIDAYS_2026_05_06.get(key, "")
        holiday_count += 1 if holiday else 0
        cells, risk = [], False
        for dept in FRONTLINE_DEPARTMENTS:
            total = len(active_by_dept.get(dept) or [])
            dept_leaves = leave_by_date_dept.get((key, dept), [])
            on_duty = max(0, total - len(dept_leaves))
            names = "、".join([x["display_name"] for x in dept_leaves]) or "-"
            if total == 0 or on_duty < 1:
                risk = True
                cells.append(f"<td><span class='pill red'>{dept} 缺人</span><br>值班 {on_duty}/{total}<br>休：{escape(names)}</td>")
            else:
                cells.append(f"<td><span class='pill green'>{dept} OK</span><br>值班 {on_duty}/{total}<br>休：{escape(names)}</td>")
        risk_days += 1 if risk else 0
        weekday = ["一", "二", "三", "四", "五", "六", "日"][d.weekday()]
        holiday_html = f"<span class='pill yellow'>{escape(holiday)}</span>" if holiday else ""
        result_html = "<span class='pill red'>需補人</span>" if risk else "<span class='pill green'>一線有人值班</span>"
        rows.append(f"<tr><td>{key}</td><td>星期{weekday}</td><td>{holiday_html}</td>{''.join(cells)}<td>{result_html}</td></tr>")
        d += timedelta(days=1)
    body = f"<div class='note'>以 2026 年 5、6 月做排休管理測試。國定假日：5/1 勞動節、6/19 端午節。規則：工程部、維修部、專案部每天至少 1 人值班。</div><section class='summary'><div class='summary-card'><div class='summary-label'>檢查天數</div><div class='summary-value'>{total_days}</div></div><div class='summary-card'><div class='summary-label'>國定假日</div><div class='summary-value'>{holiday_count}</div></div><div class='summary-card'><div class='summary-label'>虛擬假單</div><div class='summary-value'>{len(leaves)}</div></div><div class='summary-card'><div class='summary-label'>缺人天數</div><div class='summary-value'>{risk_days}</div></div></section><section class='panel' style='max-width:900px;margin:auto;'><div class='panel-head'>5、6 月一線值班檢查表</div><div class='table-wrap'><table style='width:720px;min-width:720px;margin-left:0;border-collapse:collapse;'><thead><tr><th>日期</th><th>星期</th><th>國定假日</th><th>工程部</th><th>維修部</th><th>專案部</th><th>結果</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>"
    return _layout("休假管理", "leave", _user_line(user), body)


@router.get("/admin/hr/proxy-management", response_class=HTMLResponse)
def hr_proxy_page(request: Request):
    user = _user_or_redirect(request, "/admin/hr/proxy-management")
    if not isinstance(user, dict): return user
    employees = [e for e in _load_employees() if e.get("employment_status") == "在職"]
    rows = []
    for i, emp in enumerate(employees):
        p1 = employees[(i + 1) % len(employees)] if employees else {}
        p2 = employees[(i + 2) % len(employees)] if employees else {}
        rows.append(f"<tr><td>{escape(emp.get('staff_code',''))}</td><td>{escape(emp.get('display_name',''))}</td><td>{escape(emp.get('department',''))}</td><td>{escape(p1.get('display_name','-'))}</td><td>{escape(p2.get('display_name','-'))}</td><td><span class='pill blue'>依 APP 權限代理</span></td><td><span class='pill green'>啟用</span></td></tr>")
    body = f"<section class='panel' style='max-width:900px;margin:auto;'><div class='panel-head'>代理人管理</div><div class='table-wrap'><table style='width:720px;min-width:720px;margin-left:0;border-collapse:collapse;'><thead><tr><th>員編</th><th>員工</th><th>部門</th><th>代理人一</th><th>代理人二</th><th>代理範圍</th><th>狀態</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>"
    return _layout("代理人管理", "proxy", _user_line(user), body)


@router.get("/admin/hr/departments", response_class=HTMLResponse)
def hr_departments_page(request: Request):
    user = _user_or_redirect(request, "/admin/hr/departments")
    if not isinstance(user, dict): return user
    employees = _load_employees()
    counts = {}
    for e in employees:
        counts[e.get("department") or "未設定"] = counts.get(e.get("department") or "未設定", 0) + 1
    data = [("工程部","工程師、資深工程師、工程主管","是","派工 APP、工程 APP"),("維修部","維修專員、維修工程師、維修主管","是","派工 APP、工程 APP"),("專案部","專案專員、專案主管","是","工程 APP、人事系統"),("帳務部","帳務專員、帳務主管","否","帳務 APP"),("業務部","業務專員、業務主管","否","業務 APP、工程流程"),("管理部","行政、人事、系統管理員","否","人事系統、管理後台")]
    rows = "".join([f"<tr><td>{d}</td><td>{r}</td><td>{counts.get(d,0)}</td><td><span class='pill {'green' if f=='是' else 'blue'}'>{f}</span></td><td>{apps}</td></tr>" for d, r, f, apps in data])
    body = f"<section class='panel' style='max-width:900px;margin:auto;'><div class='panel-head'>部門職務</div><div class='table-wrap'><table style='width:720px;min-width:720px;margin-left:0;border-collapse:collapse;'><thead><tr><th>部門</th><th>職務 / 職稱</th><th>人數</th><th>一線單位</th><th>常用系統</th></tr></thead><tbody>{rows}</tbody></table></div></section>"
    return _layout("部門職務", "departments", _user_line(user), body)


@router.get("/admin/hr/salary", response_class=HTMLResponse)
def hr_salary_page(request: Request):
    user = _user_or_redirect(request, "/admin/hr/salary")
    if not isinstance(user, dict): return user
    employees = _load_employees()
    rows, total_gross = [], 0
    for emp in employees:
        s = _salary(emp)
        total_gross += s["gross"]
        rows.append(f"<tr><td>{escape(emp.get('staff_code',''))}</td><td>{escape(emp.get('display_name',''))}</td><td>{escape(emp.get('department',''))}</td><td>{escape(emp.get('position_title',''))}</td><td>{_money(s['base'])}</td><td>{_money(s['duty'])}</td><td>{_money(s['technical'])}</td><td>{_money(s['supervisor'])}</td><td>{_money(s['transport'])}</td><td>{_money(s['phone'])}</td><td>{_money(s['meal'])}</td><td>{_money(s['full_attendance'])}</td><td>{_money(s['performance'])}</td><td>{_money(s['engineering_bonus'])}</td><td>{_money(s['overtime'])}</td><td>{_money(s['gross'])}</td></tr>")
    body = f"<div class='note'>薪資結構採正規模式：應發項目包含本薪、職務/技術/主管加給、交通、通訊、伙食、全勤、績效、工程獎金與加班費。虛擬薪資依目前職務市價估算。</div><section class='summary'><div class='summary-card'><div class='summary-label'>員工數</div><div class='summary-value'>{len(employees)}</div></div><div class='summary-card'><div class='summary-label'>應發總額</div><div class='summary-value'>{_money(total_gross)}</div></div><div class='summary-card'><div class='summary-label'>最低月薪基準</div><div class='summary-value'>{_money(MIN_WAGE_115)}</div></div><div class='summary-card'><div class='summary-label'>薪資年度</div><div class='summary-value'>115</div></div></section><section class='panel' style='max-width:900px;margin:auto;'><div class='panel-head'>薪資結構主檔</div><div class='table-wrap'><table style='width:720px;min-width:720px;margin-left:0;border-collapse:collapse;'><thead><tr><th>員編</th><th>姓名</th><th>部門</th><th>職稱</th><th>本薪</th><th>職務加給</th><th>技術加給</th><th>主管加給</th><th>交通</th><th>通訊</th><th>伙食</th><th>全勤</th><th>績效</th><th>工程獎金</th><th>加班</th><th>應發薪資</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>"
    return _layout("薪資結構", "salary", _user_line(user), body)


@router.get("/admin/hr/insurance", response_class=HTMLResponse)
def hr_insurance_page(request: Request):
    user = _user_or_redirect(request, "/admin/hr/insurance")
    if not isinstance(user, dict): return user
    rows = []
    for emp in _load_employees():
        s = _salary(emp)
        rows.append(f"<tr><td>{escape(emp.get('staff_code',''))}</td><td>{escape(emp.get('display_name',''))}</td><td>{_money(s['gross'])}</td><td>{_money(s['labor_grade'])}</td><td>{_money(s['labor_employee'])}</td><td>{_money(s['labor_employer'])}</td><td>{_money(s['health_grade'])}</td><td>{_money(s['health_employee'])}</td><td>{_money(s['health_employer'])}</td><td>{_money(s['occupational'])}</td><td>{_money(s['arrears'])}</td><td>{_money(s['employer_pension'])}</td></tr>")
    body = f"<div class='note'>勞健保勞退為 115 年試算版：勞保級距最高以 45,800 元估算，健保以級距估算，雇主勞退以提繳工資 6% 計算。正式申報仍以政府機關與公司實際投保資料為準。</div><section class='panel' style='max-width:900px;margin:auto;'><div class='panel-head'>勞健保 / 勞退試算</div><div class='table-wrap'><table style='width:720px;min-width:720px;margin-left:0;border-collapse:collapse;'><thead><tr><th>員編</th><th>姓名</th><th>應發</th><th>勞保級距</th><th>勞保自付</th><th>勞保公司</th><th>健保級距</th><th>健保自付</th><th>健保公司</th><th>職災公司</th><th>工資墊償</th><th>雇主勞退6%</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>"
    return _layout("勞健保勞退", "insurance", _user_line(user), body)


@router.get("/admin/hr/payroll", response_class=HTMLResponse)
def hr_payroll_page(request: Request):
    user = _user_or_redirect(request, "/admin/hr/payroll")
    if not isinstance(user, dict): return user
    rows = []
    gross_total = deduction_total = net_total = cost_total = 0
    for emp in _load_employees():
        s = _salary(emp)
        gross_total += s["gross"]; deduction_total += s["deductions"]; net_total += s["net"]; cost_total += s["company_cost"]
        rows.append(f"<tr><td>2026-06</td><td>{escape(emp.get('staff_code',''))}</td><td>{escape(emp.get('display_name',''))}</td><td>{escape(emp.get('department',''))}</td><td>{_money(s['gross'])}</td><td>{_money(s['labor_employee'])}</td><td>{_money(s['health_employee'])}</td><td>{_money(s['employee_pension_self'])}</td><td>{_money(s['deductions'])}</td><td>{_money(s['net'])}</td><td>{_money(s['labor_employer'] + s['health_employer'] + s['occupational'] + s['arrears'])}</td><td>{_money(s['employer_pension'])}</td><td>{_money(s['company_cost'])}</td></tr>")
    body = f"<div class='note'>正規薪資試算：應發薪資 - 應扣總額 = 實發薪資；公司總成本 = 應發薪資 + 公司負擔勞健保 + 職災 + 工資墊償 + 雇主勞退。</div><section class='summary'><div class='summary-card'><div class='summary-label'>應發總額</div><div class='summary-value'>{_money(gross_total)}</div></div><div class='summary-card'><div class='summary-label'>應扣總額</div><div class='summary-value'>{_money(deduction_total)}</div></div><div class='summary-card'><div class='summary-label'>實發總額</div><div class='summary-value'>{_money(net_total)}</div></div><div class='summary-card'><div class='summary-label'>公司總成本</div><div class='summary-value'>{_money(cost_total)}</div></div></section><section class='panel' style='max-width:900px;margin:auto;'><div class='panel-head'>2026-06 薪資試算清冊</div><div class='table-wrap'><table style='width:720px;min-width:720px;margin-left:0;border-collapse:collapse;'><thead><tr><th>年月</th><th>員編</th><th>姓名</th><th>部門</th><th>應發</th><th>勞保自付</th><th>健保自付</th><th>勞退自提</th><th>應扣總額</th><th>實發</th><th>公司保險負擔</th><th>雇主勞退</th><th>公司總成本</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>"
    return _layout("薪資試算", "payroll", _user_line(user), body)


@router.get("/admin/hr/change-logs", response_class=HTMLResponse)
def hr_change_logs_page(request: Request):
    user = _user_or_redirect(request, "/admin/hr/change-logs")
    if not isinstance(user, dict): return user
    _hr_db_init()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id, operator_staff_code, action_type, target_staff_code, note, created_at FROM hr_change_logs ORDER BY id DESC LIMIT 100")).mappings().fetchall()
    if not rows:
        row_html = "<tr><td colspan='6'>目前尚無正式異動紀錄。此頁已預留資料表 hr_change_logs。</td></tr>"
    else:
        row_html = "".join([f"<tr><td>{r['id']}</td><td>{escape(r['operator_staff_code'] or '')}</td><td>{escape(r['action_type'] or '')}</td><td>{escape(r['target_staff_code'] or '')}</td><td>{escape(r['note'] or '')}</td><td>{escape(r['created_at'] or '')}</td></tr>" for r in rows])
    body = f"<section class='panel' style='max-width:900px;margin:auto;'><div class='panel-head'>異動紀錄</div><div class='table-wrap'><table style='width:720px;min-width:720px;margin-left:0;border-collapse:collapse;'><thead><tr><th>ID</th><th>操作人</th><th>異動類型</th><th>目標員工</th><th>備註</th><th>時間</th></tr></thead><tbody>{row_html}</tbody></table></div></section>"
    return _layout("異動紀錄", "logs", _user_line(user), body)













