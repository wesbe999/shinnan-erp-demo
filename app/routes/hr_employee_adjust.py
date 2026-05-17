from __future__ import annotations

import json
from html import escape

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from sqlalchemy import text

from app.db import engine
from app.routes.employee_auth import _employee_current_user_from_request


router = APIRouter(tags=["人事系統職務薪資調整"])


DEPARTMENTS = ["工程部", "維修部", "帳務部", "業務部", "專案部", "管理部", "外包"]

ROLE_OPTIONS = ["employee", "sales", "manager", "admin"]

POSITION_OPTIONS = [
    "工程師",
    "資深工程師",
    "維修專員",
    "維修工程師",
    "帳務專員",
    "帳務主管",
    "業務專員",
    "業務主管",
    "專案專員",
    "專案主管",
    "人事行政",
    "系統管理員",
    "外包人員",
]

SALARY_DEFAULTS = {
    "工程師": 42000,
    "資深工程師": 52000,
    "維修專員": 38000,
    "維修工程師": 42000,
    "帳務專員": 35000,
    "帳務主管": 45000,
    "業務專員": 38000,
    "業務主管": 50000,
    "專案專員": 45000,
    "專案主管": 60000,
    "人事行政": 38000,
    "系統管理員": 58000,
    "外包人員": 0,
}


def _dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def _safe_int(value, default=0) -> int:
    try:
        return int(float(str(value or "").replace(",", "").strip()))
    except Exception:
        return int(default or 0)


def _require_user(request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return None
    return user


def _db_init():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS hr_salary_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT UNIQUE NOT NULL,
                salary_type TEXT DEFAULT '月薪',
                base_salary INTEGER DEFAULT 0,
                duty_allowance INTEGER DEFAULT 0,
                technical_allowance INTEGER DEFAULT 0,
                supervisor_allowance INTEGER DEFAULT 0,
                transport_allowance INTEGER DEFAULT 0,
                phone_allowance INTEGER DEFAULT 0,
                meal_allowance INTEGER DEFAULT 0,
                full_attendance_bonus INTEGER DEFAULT 0,
                performance_bonus INTEGER DEFAULT 0,
                engineering_bonus INTEGER DEFAULT 0,
                referral_bonus INTEGER DEFAULT 0,
                rebate_bonus INTEGER DEFAULT 0,
                overtime_pay INTEGER DEFAULT 0,
                other_add INTEGER DEFAULT 0,
                personal_leave_deduct INTEGER DEFAULT 0,
                sick_leave_deduct INTEGER DEFAULT 0,
                late_deduct INTEGER DEFAULT 0,
                absence_deduct INTEGER DEFAULT 0,
                tax_withholding INTEGER DEFAULT 0,
                welfare_fee INTEGER DEFAULT 0,
                other_deduct INTEGER DEFAULT 0,
                employee_pension_self_rate REAL DEFAULT 0,
                note TEXT DEFAULT '',
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
            "ALTER TABLE employee_profiles ADD COLUMN hire_date TEXT DEFAULT ''",
            "ALTER TABLE employee_profiles ADD COLUMN employment_status TEXT DEFAULT '在職'",
            "ALTER TABLE employee_profiles ADD COLUMN permission_scope TEXT DEFAULT ''",
        ]:
            try:
                conn.execute(text(sql))
            except Exception:
                pass


def _default_salary_for_employee(emp: dict) -> dict:
    department = str(emp.get("department") or "")
    role = str(emp.get("role") or "")
    position = str(emp.get("position_title") or "")

    base = SALARY_DEFAULTS.get(position, 36000)
    if department == "外包":
        base = 0

    return {
        "salary_type": "月薪" if department != "外包" else "外包",
        "base_salary": base,
        "duty_allowance": 3000 if "主管" in position else 0,
        "technical_allowance": 3000 if department in ["工程部", "維修部", "專案部"] else 0,
        "supervisor_allowance": 6000 if role in ["manager", "admin"] else 0,
        "transport_allowance": 2000 if department in ["工程部", "維修部", "業務部", "專案部"] else 1000,
        "phone_allowance": 1000 if department in ["工程部", "維修部", "業務部", "專案部"] else 500,
        "meal_allowance": 2400,
        "full_attendance_bonus": 2000,
        "performance_bonus": 3000 if department in ["業務部", "專案部"] else 1500,
        "engineering_bonus": 4000 if department in ["工程部", "維修部", "專案部"] else 0,
        "referral_bonus": 1000 if department == "業務部" else 0,
        "rebate_bonus": 800 if department == "業務部" else 0,
        "overtime_pay": 2500 if department in ["工程部", "維修部"] else 800,
        "other_add": 0,
        "personal_leave_deduct": 0,
        "sick_leave_deduct": 0,
        "late_deduct": 0,
        "absence_deduct": 0,
        "tax_withholding": 0,
        "welfare_fee": 0,
        "other_deduct": 0,
        "employee_pension_self_rate": 0,
        "note": "",
    }


def _load_adjust_employees():
    _db_init()

    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT
                p.staff_code,
                p.display_name,
                p.department,
                p.role,
                p.position_title,
                p.hire_date,
                p.employment_status,
                p.permission_scope,
                COALESCE(s.salary_type, '') AS salary_type,
                COALESCE(s.base_salary, NULL) AS base_salary,
                COALESCE(s.duty_allowance, NULL) AS duty_allowance,
                COALESCE(s.technical_allowance, NULL) AS technical_allowance,
                COALESCE(s.supervisor_allowance, NULL) AS supervisor_allowance,
                COALESCE(s.transport_allowance, NULL) AS transport_allowance,
                COALESCE(s.phone_allowance, NULL) AS phone_allowance,
                COALESCE(s.meal_allowance, NULL) AS meal_allowance,
                COALESCE(s.full_attendance_bonus, NULL) AS full_attendance_bonus,
                COALESCE(s.performance_bonus, NULL) AS performance_bonus,
                COALESCE(s.engineering_bonus, NULL) AS engineering_bonus,
                COALESCE(s.referral_bonus, NULL) AS referral_bonus,
                COALESCE(s.rebate_bonus, NULL) AS rebate_bonus,
                COALESCE(s.overtime_pay, NULL) AS overtime_pay,
                COALESCE(s.other_add, NULL) AS other_add,
                COALESCE(s.personal_leave_deduct, NULL) AS personal_leave_deduct,
                COALESCE(s.sick_leave_deduct, NULL) AS sick_leave_deduct,
                COALESCE(s.late_deduct, NULL) AS late_deduct,
                COALESCE(s.absence_deduct, NULL) AS absence_deduct,
                COALESCE(s.tax_withholding, NULL) AS tax_withholding,
                COALESCE(s.welfare_fee, NULL) AS welfare_fee,
                COALESCE(s.other_deduct, NULL) AS other_deduct,
                COALESCE(s.employee_pension_self_rate, NULL) AS employee_pension_self_rate,
                COALESCE(s.note, '') AS salary_note
            FROM employee_profiles p
            LEFT JOIN hr_salary_profiles s ON s.staff_code = p.staff_code
            ORDER BY
                CASE WHEN p.staff_code = 'admin' THEN 0 ELSE 1 END,
                p.staff_code
        """)).mappings().fetchall()

    items = []

    for row in rows:
        item = dict(row)
        defaults = _default_salary_for_employee(item)

        for key, value in defaults.items():
            if item.get(key) is None or item.get(key) == "":
                item[key] = value

        gross = sum([
            _safe_int(item.get("base_salary")),
            _safe_int(item.get("duty_allowance")),
            _safe_int(item.get("technical_allowance")),
            _safe_int(item.get("supervisor_allowance")),
            _safe_int(item.get("transport_allowance")),
            _safe_int(item.get("phone_allowance")),
            _safe_int(item.get("meal_allowance")),
            _safe_int(item.get("full_attendance_bonus")),
            _safe_int(item.get("performance_bonus")),
            _safe_int(item.get("engineering_bonus")),
            _safe_int(item.get("referral_bonus")),
            _safe_int(item.get("rebate_bonus")),
            _safe_int(item.get("overtime_pay")),
            _safe_int(item.get("other_add")),
        ])

        item["gross_salary"] = gross
        items.append(item)

    return items


@router.post("/api/admin/hr/employee-adjust/save")
async def api_hr_employee_adjust_save(request: Request):
    user = _require_user(request)

    if not user:
        return Response(
            _dumps({"ok": False, "error": "login required"}),
            status_code=401,
            media_type="application/json; charset=utf-8",
        )

    _db_init()

    raw = await request.body()
    try:
        data = json.loads(raw.decode("utf-8") or "{}")
    except Exception:
        data = {}

    staff_code = str(data.get("staff_code") or "").strip()

    if not staff_code:
        return Response(
            _dumps({"ok": False, "error": "缺少員工編號"}),
            status_code=400,
            media_type="application/json; charset=utf-8",
        )

    display_name = str(data.get("display_name") or "").strip()
    department = str(data.get("department") or "").strip()
    role = str(data.get("role") or "").strip()
    position_title = str(data.get("position_title") or "").strip()
    hire_date = str(data.get("hire_date") or "").strip()
    employment_status = str(data.get("employment_status") or "在職").strip()
    permission_scope = str(data.get("permission_scope") or "").strip()

    before_text = ""

    with engine.begin() as conn:
        before = conn.execute(text("""
            SELECT *
            FROM employee_profiles
            WHERE staff_code = :staff_code
            LIMIT 1
        """), {"staff_code": staff_code}).mappings().first()

        before_salary = conn.execute(text("""
            SELECT *
            FROM hr_salary_profiles
            WHERE staff_code = :staff_code
            LIMIT 1
        """), {"staff_code": staff_code}).mappings().first()

        before_text = _dumps({
            "profile": dict(before) if before else {},
            "salary": dict(before_salary) if before_salary else {},
        })

        conn.execute(text("""
            UPDATE employee_profiles
            SET display_name = :display_name,
                department = :department,
                role = :role,
                position_title = :position_title,
                hire_date = :hire_date,
                employment_status = :employment_status,
                permission_scope = :permission_scope,
                updated_at = datetime('now')
            WHERE staff_code = :staff_code
        """), {
            "staff_code": staff_code,
            "display_name": display_name,
            "department": department,
            "role": role,
            "position_title": position_title,
            "hire_date": hire_date,
            "employment_status": employment_status,
            "permission_scope": permission_scope,
        })

        conn.execute(text("""
            UPDATE employee_accounts
            SET display_name = :display_name,
                department = :department,
                role = :role,
                updated_at = datetime('now')
            WHERE staff_code = :staff_code
        """), {
            "staff_code": staff_code,
            "display_name": display_name,
            "department": department,
            "role": role,
        })

        conn.execute(text("""
            INSERT INTO hr_salary_profiles (
                staff_code,
                salary_type,
                base_salary,
                duty_allowance,
                technical_allowance,
                supervisor_allowance,
                transport_allowance,
                phone_allowance,
                meal_allowance,
                full_attendance_bonus,
                performance_bonus,
                engineering_bonus,
                referral_bonus,
                rebate_bonus,
                overtime_pay,
                other_add,
                personal_leave_deduct,
                sick_leave_deduct,
                late_deduct,
                absence_deduct,
                tax_withholding,
                welfare_fee,
                other_deduct,
                employee_pension_self_rate,
                note,
                updated_at
            )
            VALUES (
                :staff_code,
                :salary_type,
                :base_salary,
                :duty_allowance,
                :technical_allowance,
                :supervisor_allowance,
                :transport_allowance,
                :phone_allowance,
                :meal_allowance,
                :full_attendance_bonus,
                :performance_bonus,
                :engineering_bonus,
                :referral_bonus,
                :rebate_bonus,
                :overtime_pay,
                :other_add,
                :personal_leave_deduct,
                :sick_leave_deduct,
                :late_deduct,
                :absence_deduct,
                :tax_withholding,
                :welfare_fee,
                :other_deduct,
                :employee_pension_self_rate,
                :note,
                datetime('now')
            )
            ON CONFLICT(staff_code)
            DO UPDATE SET
                salary_type = excluded.salary_type,
                base_salary = excluded.base_salary,
                duty_allowance = excluded.duty_allowance,
                technical_allowance = excluded.technical_allowance,
                supervisor_allowance = excluded.supervisor_allowance,
                transport_allowance = excluded.transport_allowance,
                phone_allowance = excluded.phone_allowance,
                meal_allowance = excluded.meal_allowance,
                full_attendance_bonus = excluded.full_attendance_bonus,
                performance_bonus = excluded.performance_bonus,
                engineering_bonus = excluded.engineering_bonus,
                referral_bonus = excluded.referral_bonus,
                rebate_bonus = excluded.rebate_bonus,
                overtime_pay = excluded.overtime_pay,
                other_add = excluded.other_add,
                personal_leave_deduct = excluded.personal_leave_deduct,
                sick_leave_deduct = excluded.sick_leave_deduct,
                late_deduct = excluded.late_deduct,
                absence_deduct = excluded.absence_deduct,
                tax_withholding = excluded.tax_withholding,
                welfare_fee = excluded.welfare_fee,
                other_deduct = excluded.other_deduct,
                employee_pension_self_rate = excluded.employee_pension_self_rate,
                note = excluded.note,
                updated_at = datetime('now')
        """), {
            "staff_code": staff_code,
            "salary_type": str(data.get("salary_type") or "月薪"),
            "base_salary": _safe_int(data.get("base_salary")),
            "duty_allowance": _safe_int(data.get("duty_allowance")),
            "technical_allowance": _safe_int(data.get("technical_allowance")),
            "supervisor_allowance": _safe_int(data.get("supervisor_allowance")),
            "transport_allowance": _safe_int(data.get("transport_allowance")),
            "phone_allowance": _safe_int(data.get("phone_allowance")),
            "meal_allowance": _safe_int(data.get("meal_allowance")),
            "full_attendance_bonus": _safe_int(data.get("full_attendance_bonus")),
            "performance_bonus": _safe_int(data.get("performance_bonus")),
            "engineering_bonus": _safe_int(data.get("engineering_bonus")),
            "referral_bonus": _safe_int(data.get("referral_bonus")),
            "rebate_bonus": _safe_int(data.get("rebate_bonus")),
            "overtime_pay": _safe_int(data.get("overtime_pay")),
            "other_add": _safe_int(data.get("other_add")),
            "personal_leave_deduct": _safe_int(data.get("personal_leave_deduct")),
            "sick_leave_deduct": _safe_int(data.get("sick_leave_deduct")),
            "late_deduct": _safe_int(data.get("late_deduct")),
            "absence_deduct": _safe_int(data.get("absence_deduct")),
            "tax_withholding": _safe_int(data.get("tax_withholding")),
            "welfare_fee": _safe_int(data.get("welfare_fee")),
            "other_deduct": _safe_int(data.get("other_deduct")),
            "employee_pension_self_rate": float(data.get("employee_pension_self_rate") or 0),
            "note": str(data.get("note") or ""),
        })

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
                'employee_work_salary_update',
                :target_staff_code,
                :before_text,
                :after_text,
                '職務與薪資調整',
                datetime('now')
            )
        """), {
            "operator_staff_code": str(user.get("staff_code") or ""),
            "target_staff_code": staff_code,
            "before_text": before_text,
            "after_text": _dumps(data),
        })

    return Response(
        _dumps({"ok": True}),
        media_type="application/json; charset=utf-8",
    )


@router.get("/admin/hr/employee-adjust", response_class=HTMLResponse)
def hr_employee_adjust_page(request: Request):
    user = _require_user(request)

    if not user:
        return RedirectResponse("/employee/login?next=/admin/hr/employee-adjust", status_code=303)

    items = _load_adjust_employees()
    items_json = _dumps(items)
    departments_json = _dumps(DEPARTMENTS)
    roles_json = _dumps(ROLE_OPTIONS)
    positions_json = _dumps(POSITION_OPTIONS)

    user_line = (str(user.get("display_name") or "") + "｜" + str(user.get("role") or "")).strip("｜")

    html = """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>職務薪資調整｜訊南人事系統</title>
  <style>
    * { box-sizing: border-box; }
    body { margin:0; background:#edf2f7; color:#102348; font-family:"Microsoft JhengHei","Segoe UI",Arial,sans-serif; }
    .layout { min-height:100vh; display:grid; grid-template-columns:260px minmax(0,1fr); }
    .sidebar { background:linear-gradient(180deg,#3f6471,#2f455f 55%,#263a55); color:#fff; padding:22px 18px; }
    .brand { display:flex; align-items:center; gap:12px; margin-bottom:24px; }
    .brand img { width:76px; height:58px; object-fit:contain; filter:drop-shadow(0 4px 8px rgba(0,0,0,.16)); }
    .brand-title { font-size:23px; font-weight:1000; }
    .brand-sub { margin-top:4px; color:#fbbf24; font-size:13px; font-weight:900; }
    .nav { display:grid; gap:8px; }
    .nav a { min-height:38px; border-radius:12px; padding:0 13px; background:rgba(255,255,255,.14); color:#eef6ff; font-size:15px; font-weight:900; text-decoration:none; display:flex; align-items:center; }
    .nav .active { background:#365ee8; color:#fff; }
    .main { min-width:0; padding:22px 26px 34px; }
    .topbar { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:14px; align-items:center; margin-bottom:18px; }
    .page-title { font-size:32px; font-weight:1000; }
    .page-sub { margin-top:5px; color:#64748b; font-size:15px; font-weight:900; }
    .btn { height:38px; border:0; border-radius:12px; padding:0 14px; background:#fff; color:#102348; font-size:14px; font-weight:1000; box-shadow:0 8px 18px rgba(15,23,42,.08); cursor:pointer; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; white-space:nowrap; }
    .btn.primary { background:#365ee8; color:#fff; }
    .btn.green { background:#16a34a; color:#fff; }
    .panel { background:#fff; border:1px solid #d7e1ef; border-radius:20px; box-shadow:0 10px 26px rgba(15,23,42,.06); overflow:hidden; }
    .panel-head { padding:16px 18px; border-bottom:1px solid #e2e8f0; background:#f8fafc; font-size:20px; font-weight:1000; display:flex; justify-content:space-between; align-items:center; gap:12px; }
    .table-wrap { overflow:auto; max-height:calc(100vh - 170px); }
    table { width:100%; min-width:1280px; border-collapse:collapse; }
    th { position:sticky; top:0; z-index:2; background:#eff6ff; color:#1e3a8a; padding:10px; border-bottom:1px solid #dbeafe; text-align:left; font-size:13px; font-weight:1000; white-space:nowrap; }
    td { padding:10px; border-bottom:1px solid #e2e8f0; font-size:14px; font-weight:850; white-space:nowrap; vertical-align:middle; }
    .pill { display:inline-flex; align-items:center; min-height:28px; padding:0 10px; border-radius:999px; font-size:12px; font-weight:1000; background:#e2e8f0; color:#334155; margin:2px; }
    .pill.green { background:#dcfce7; color:#166534; }
    .pill.blue { background:#dbeafe; color:#1d4ed8; }
    .note { border-radius:16px; background:#fff7ed; border:1px solid #fdba74; color:#7c2d12; padding:12px 14px; font-size:15px; font-weight:900; line-height:1.55; margin-bottom:16px; }
    .modal-mask { position:fixed; inset:0; display:none; align-items:center; justify-content:center; background:rgba(15,23,42,.55); padding:24px; z-index:50; }
    .modal-mask.active { display:flex; }
    .modal { width:min(1080px,100%); max-height:92vh; overflow:auto; background:#fff; border-radius:24px; border:1px solid #d7e1ef; box-shadow:0 30px 90px rgba(15,23,42,.28); }
    .modal-head { position:sticky; top:0; z-index:2; display:grid; grid-template-columns:minmax(0,1fr) auto; gap:12px; align-items:center; padding:18px 20px; background:#fff; border-bottom:1px solid #e2e8f0; }
    .modal-title { font-size:24px; font-weight:1000; }
    .modal-body { padding:18px 20px 22px; }
    .form-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }
    .field label { display:block; color:#64748b; font-size:13px; font-weight:1000; margin-bottom:6px; }
    input, select, textarea { width:100%; height:40px; border:1px solid #cbd5e1; border-radius:12px; padding:0 12px; color:#102348; font-size:14px; font-weight:900; background:#fff; outline:none; }
    textarea { height:78px; padding:10px 12px; resize:vertical; }
    .section-label { grid-column:1/-1; margin-top:8px; padding-top:12px; border-top:1px solid #e2e8f0; font-size:18px; font-weight:1000; color:#102348; }
    .modal-actions { display:flex; justify-content:flex-end; gap:10px; margin-top:18px; }
  
    /* HR_EMPLOYEE_ADJUST_COMPACT_FIX_START */
    .panel table th,
    .panel table td,
    .table-wrap table th,
    .table-wrap table td {
      font-size: 14px !important;
      line-height: 1.35 !important;
      padding: 8px 10px !important;
    }

    .panel table td b,
    .table-wrap table td b {
      font-size: 14px !important;
      line-height: 1.35 !important;
    }

    .mini-btn {
      height: 30px !important;
      min-width: 58px !important;
      padding: 0 10px !important;
      border-radius: 10px !important;
      font-size: 13px !important;
    }

    .pill {
      font-size: 12px !important;
      min-height: 24px !important;
      padding: 0 8px !important;
    }

    .table-wrap {
      max-height: calc(100vh - 120px) !important;
      min-height: calc(100vh - 210px) !important;
    }
    /* HR_EMPLOYEE_ADJUST_COMPACT_FIX_END */

  </style>
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand"><img src="/static/shinnan_home_logo.png"><div><div class="brand-title">訊南人事系統</div><div class="brand-sub">HR ADMIN</div></div></div>
      <nav class="nav">
        <a href="/admin/hr">員工名冊</a>
        <a class="active" href="/admin/hr/employee-adjust">職務薪資調整</a>
        <a href="/admin/hr/permissions">權限管理</a>
        <a href="/admin/hr/passwords">密碼管理</a>
        <a href="/admin/hr/leave-requests">請假審核</a>
        <a href="/admin/hr/leave-management">休假管理</a>
        <a href="/admin/hr/proxy-management">代理人管理</a>
        <a href="/admin/hr/departments">部門職務</a>
        <a href="/admin/hr/salary">薪資結構</a>
        <a href="/admin/hr/insurance">勞健保勞退</a>
        <a href="/admin/hr/payroll">薪資試算</a>
        <a href="/admin/hr/change-logs">異動紀錄</a>
        <a href="/">返回首頁</a>
      </nav>
    </aside>

    <main class="main">
      <header class="topbar">
        <div>
          <div class="page-title">職務 / 薪資調整</div>
          <div class="page-sub">__USER_LINE__｜調整員工職務、部門與薪資主檔</div>
        </div>
        <a class="btn" href="/admin/hr">回人事首頁</a>
      </header>

      <div class="note">本頁是正式調整入口。儲存後會更新 employee_profiles 與 hr_salary_profiles，並寫入異動紀錄。</div>

      <section class="panel">
        <div class="panel-head">
          <span>員工職務與薪資主檔</span>
          <button class="btn" onclick="location.reload()">重新整理</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>操作</th>
                <th>員編</th>
                <th>姓名</th>
                <th>部門</th>
                <th>職稱</th>
                <th>職務類型</th>
                <th>到職日</th>
                <th>狀態</th>
                <th>本薪</th>
                <th>應發薪資</th>
              </tr>
            </thead>
            <tbody id="tbody"></tbody>
          </table>
        </div>
      </section>
    </main>
  </div>

  <div id="editor_mask" class="modal-mask">
    <section class="modal">
      <div class="modal-head">
        <div id="editor_title" class="modal-title">編輯</div>
        <button class="btn" onclick="closeEditor()">關閉</button>
      </div>
      <div class="modal-body">
        <div class="form-grid">
          <div class="section-label">職務資料</div>

          <div class="field"><label>員工編號</label><input id="staff_code" disabled></div>
          <div class="field"><label>姓名</label><input id="display_name"></div>
          <div class="field"><label>部門</label><select id="department"></select></div>
          <div class="field"><label>職稱</label><select id="position_title"></select></div>
          <div class="field"><label>角色</label><select id="role"></select></div>
          <div class="field"><label>到職日</label><input id="hire_date" type="date"></div>
          <div class="field"><label>在職狀態</label><select id="employment_status"><option>在職</option><option>留職停薪</option><option>離職</option></select></div>
          <div class="field"><label>權限範圍 / 區域</label><input id="permission_scope"></div>

          <div class="section-label">應發項目</div>

          <div class="field"><label>薪資類型</label><select id="salary_type"><option>月薪</option><option>日薪</option><option>時薪</option><option>外包</option></select></div>
          <div class="field"><label>本薪</label><input id="base_salary" type="number"></div>
          <div class="field"><label>職務加給</label><input id="duty_allowance" type="number"></div>
          <div class="field"><label>技術加給</label><input id="technical_allowance" type="number"></div>
          <div class="field"><label>主管加給</label><input id="supervisor_allowance" type="number"></div>
          <div class="field"><label>交通津貼</label><input id="transport_allowance" type="number"></div>
          <div class="field"><label>通訊津貼</label><input id="phone_allowance" type="number"></div>
          <div class="field"><label>伙食津貼</label><input id="meal_allowance" type="number"></div>
          <div class="field"><label>全勤獎金</label><input id="full_attendance_bonus" type="number"></div>
          <div class="field"><label>績效獎金</label><input id="performance_bonus" type="number"></div>
          <div class="field"><label>工程獎金</label><input id="engineering_bonus" type="number"></div>
          <div class="field"><label>介紹費</label><input id="referral_bonus" type="number"></div>
          <div class="field"><label>回饋金</label><input id="rebate_bonus" type="number"></div>
          <div class="field"><label>加班費</label><input id="overtime_pay" type="number"></div>
          <div class="field"><label>其他加項</label><input id="other_add" type="number"></div>

          <div class="section-label">扣款項目</div>

          <div class="field"><label>事假扣款</label><input id="personal_leave_deduct" type="number"></div>
          <div class="field"><label>病假扣款</label><input id="sick_leave_deduct" type="number"></div>
          <div class="field"><label>遲到早退扣款</label><input id="late_deduct" type="number"></div>
          <div class="field"><label>缺勤扣款</label><input id="absence_deduct" type="number"></div>
          <div class="field"><label>所得稅預扣</label><input id="tax_withholding" type="number"></div>
          <div class="field"><label>福利金</label><input id="welfare_fee" type="number"></div>
          <div class="field"><label>其他扣款</label><input id="other_deduct" type="number"></div>
          <div class="field"><label>勞退自提率 %</label><input id="employee_pension_self_rate" type="number" step="0.1"></div>

          <div class="section-label">備註</div>
          <div class="field" style="grid-column:1/-1;"><label>薪資備註</label><textarea id="note"></textarea></div>
        </div>

        <div class="modal-actions">
          <button class="btn" onclick="closeEditor()">取消</button>
          <button class="btn green" onclick="saveEditor()">儲存</button>
        </div>
      </div>
    </section>
  </div>

  <script>
    const EMPLOYEES = __ITEMS_JSON__;
    const DEPARTMENTS = __DEPARTMENTS_JSON__;
    const ROLES = __ROLES_JSON__;
    const POSITIONS = __POSITIONS_JSON__;

    const FIELDS = [
      "staff_code","display_name","department","position_title","role","hire_date","employment_status","permission_scope",
      "salary_type","base_salary","duty_allowance","technical_allowance","supervisor_allowance","transport_allowance",
      "phone_allowance","meal_allowance","full_attendance_bonus","performance_bonus","engineering_bonus","referral_bonus",
      "rebate_bonus","overtime_pay","other_add","personal_leave_deduct","sick_leave_deduct","late_deduct","absence_deduct",
      "tax_withholding","welfare_fee","other_deduct","employee_pension_self_rate","note"
    ];


    function roleLabel(value) {
      const raw = String(value || "").trim();

      const map = {
        "admin": "系統管理員",
        "manager": "主管",
        "maintenance": "維修人員",
        "employee": "一般員工",
        "sales": "業務人員",
        "billing": "帳務人員",
        "engineering": "工程人員",
        "hr": "人事人員",
        "field": "外勤人員",
        "product": "專案人員"
      };

      return map[raw] || raw || "-";
    }

    function money(v) {
      const n = Number(v || 0);
      return n.toLocaleString("zh-TW");
    }

    function esc(v) {
      return String(v ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function fillSelect(id, items) {
      const el = document.getElementById(id);
      el.innerHTML = items.map(function(x) {
        return "<option value='" + esc(x) + "'>" + esc(x) + "</option>";
      }).join("");
    }

    function render() {
      const tbody = document.getElementById("tbody");
      tbody.innerHTML = EMPLOYEES.map(function(item) {
        return `
          <tr>
            <td><button class="btn primary mini-btn" onclick="openEditor('${esc(item.staff_code)}')">調整</button></td>
            <td>${esc(item.staff_code)}</td>
            <td>${esc(item.display_name)}</td>
            <td>${esc(item.department)}</td>
            <td>${esc(item.position_title)}</td>
            <td>${esc(roleLabel(item.role))}</td>
            <td>${esc(item.hire_date || "-")}</td>
            <td><span class="pill green">${esc(item.employment_status || "-")}</span></td>
            <td>${money(item.base_salary)}</td>
            <td><b>${money(item.gross_salary)}</b></td>
          </tr>
        `;
      }).join("");
    }

    function openEditor(staffCode) {
      const item = EMPLOYEES.find(function(x) { return x.staff_code === staffCode; });
      if (!item) {
        alert("找不到員工：" + staffCode);
        return;
      }

      document.getElementById("editor_title").textContent = item.staff_code + "｜" + item.display_name;

      FIELDS.forEach(function(id) {
        const el = document.getElementById(id);
        if (el) el.value = item[id] ?? "";
      });

      document.getElementById("editor_mask").classList.add("active");
    }

    function closeEditor() {
      document.getElementById("editor_mask").classList.remove("active");
    }

    async function saveEditor() {
      const payload = {};

      FIELDS.forEach(function(id) {
        const el = document.getElementById(id);
        if (el) payload[id] = el.value;
      });

      const res = await fetch("/api/admin/hr/employee-adjust/save", {
        method: "POST",
        headers: {"Content-Type": "application/json; charset=utf-8"},
        credentials: "same-origin",
        body: JSON.stringify(payload)
      });

      let data = {};
      try { data = await res.json(); } catch (err) {}

      if (!res.ok || !data.ok) {
        alert(data.error || "儲存失敗");
        return;
      }

      alert("已儲存。");
      location.reload();
    }

    fillSelect("department", DEPARTMENTS);
    fillSelect("role", ROLES);
    fillSelect("position_title", POSITIONS);
    render();
  </script>

  <script src="/static/app_header_actions.js?v=cl17p5"></script>
</body>
</html>
"""

    return (
        html
        .replace("__USER_LINE__", escape(user_line))
        .replace("__ITEMS_JSON__", items_json)
        .replace("__DEPARTMENTS_JSON__", departments_json)
        .replace("__ROLES_JSON__", roles_json)
        .replace("__POSITIONS_JSON__", positions_json)
    )
