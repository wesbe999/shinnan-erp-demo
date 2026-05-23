from __future__ import annotations

import json
from html import escape
from sqlalchemy import text

from app.db import engine


APP_LABELS = {
    "dispatch": "派工 APP",
    "billing": "帳務 APP",
    "engineering": "工程 APP",
    "sales": "業務 APP",
    "hr": "人事系統",
    "admin": "管理後台",
}


def _parse_app_access(value):
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]

    raw = str(value or "").strip()
    if not raw:
        return []

    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(x).strip() for x in data if str(x).strip()]
    except Exception:
        pass

    return [x.strip() for x in raw.split(",") if x.strip()]


def get_employee_app_access(staff_code: str):
    staff_code = str(staff_code or "").strip()
    if not staff_code:
        return []

    with engine.begin() as conn:
        row = conn.execute(
            text("""
                SELECT app_access
                FROM employee_profiles
                WHERE staff_code = :staff_code
                LIMIT 1
            """),
            {"staff_code": staff_code},
        ).mappings().first()

    if not row:
        return []

    return _parse_app_access(row.get("app_access"))


def employee_has_app_access(user: dict, app_key: str) -> bool:
    if not user:
        return False

    role = str(user.get("role") or "").strip()
    if role == "admin":
        return True

    staff_code = str(user.get("staff_code") or "").strip()
    allowed_apps = get_employee_app_access(staff_code)

    return str(app_key) in allowed_apps


def app_access_denied_html(app_key: str, back_url: str = "/"):
    label = APP_LABELS.get(app_key, app_key)

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>無權限｜訊南 ERP</title>
  <style>
    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #eef3f9;
      color: #102348;
      font-family: "Microsoft JhengHei", "Segoe UI", Arial, sans-serif;
      padding: 24px;
    }}

    .card {{
      width: min(460px, 100%);
      background: #fff;
      border: 1px solid #d7e1ef;
      border-radius: 24px;
      padding: 28px 24px;
      text-align: center;
      box-shadow: 0 16px 42px rgba(15,23,42,.12);
    }}

    .title {{
      color: #991b1b;
      font-size: 30px;
      font-weight: 1000;
      line-height: 1.2;
    }}

    .text {{
      margin-top: 14px;
      color: #475569;
      font-size: 17px;
      font-weight: 900;
      line-height: 1.6;
    }}

    .btn {{
      margin-top: 22px;
      height: 48px;
      border: 0;
      border-radius: 16px;
      padding: 0 22px;
      background: #365ee8;
      color: #fff;
      font-size: 17px;
      font-weight: 1000;
      cursor: pointer;
    }}
  </style>
</head>
<body>
  <section class="card">
    <div class="title">無權限</div>
    <div class="text">
      你的帳號目前沒有「{escape(label)}」使用權限。<br>
      請由人事系統或管理員調整 APP 權限。
    </div>
    <button class="btn" onclick="location.href='{escape(back_url)}'">返回首頁</button>
  </section>

<script src='/static/xn_theme.js?v=1'></script>
</body>
</html>"""
