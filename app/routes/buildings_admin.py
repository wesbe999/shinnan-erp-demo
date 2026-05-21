from fastapi.responses import RedirectResponse
from app.routes.employee_auth import _employee_current_user_from_request
import json as _buildings_json

from fastapi import APIRouter, Request
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
                id,
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
            ORDER BY CAST(substr(building_no, 2) AS INTEGER) ASC
        """)).mappings().fetchall()

    return [dict(row) for row in rows]
# SHINNAN_BUILDINGS_DB_API_HELPER_END


_BUILDING_EDIT_FIELDS = {
    "building_no": "TEXT",
    "name": "TEXT",
    "area": "TEXT",
    "address": "TEXT",
    "raw_address": "TEXT",
    "display_address": "TEXT",
    "management_company": "TEXT",
    "management_phone": "TEXT",
    "manager_name": "TEXT",
    "manager_phone": "TEXT",
    "manager_age": "TEXT",
    "manager_experience": "TEXT",
    "manager_interest": "TEXT",
    "visit_time": "TEXT",
    "committee_time": "TEXT",
    "resident_meeting_time": "TEXT",
    "active_users": "INTEGER",
    "total_households": "INTEGER",
    "ip": "TEXT",
    "host": "TEXT",
    "note": "TEXT",
}


def _clean_building_value(field: str, value):
    if _BUILDING_EDIT_FIELDS.get(field) == "INTEGER":
        try:
            return max(0, int(str(value or "0").replace(",", "").strip() or "0"))
        except ValueError:
            return 0

    return str(value or "").strip()


@router.patch("/api/admin/buildings/{building_id}")
async def api_admin_update_building(building_id: int, request: Request):
    _buildings_db_init()
    payload = await request.json()

    updates = {}
    for field, value in dict(payload or {}).items():
        if field in _BUILDING_EDIT_FIELDS:
            updates[field] = _clean_building_value(field, value)

    if not updates:
        return JSONResponse({"ok": False, "error": "no editable fields"}, status_code=400)

    if "address" in updates:
        updates.setdefault("raw_address", updates["address"])
        updates.setdefault("display_address", updates["address"])
    elif "raw_address" in updates:
        updates.setdefault("address", updates["raw_address"])
        updates.setdefault("display_address", updates["raw_address"])
    elif "display_address" in updates:
        updates.setdefault("address", updates["display_address"])
        updates.setdefault("raw_address", updates["display_address"])

    set_sql = ", ".join(f"{field} = :{field}" for field in updates)
    params = dict(updates)
    params["id"] = building_id

    with _buildings_engine.begin() as conn:
        result = conn.execute(
            _buildings_sql_text(
                f"UPDATE buildings SET {set_sql}, updated_at = datetime('now', 'localtime') WHERE id = :id"
            ),
            params,
        )

        row = conn.execute(
            _buildings_sql_text("SELECT * FROM buildings WHERE id = :id"),
            {"id": building_id},
        ).mappings().first()

    if not row or int(result.rowcount or 0) <= 0:
        return JSONResponse({"ok": False, "error": "building not found"}, status_code=404)

    return _BuildingsResponse(
        content=_buildings_json.dumps({"ok": True, "item": dict(row)}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )




@router.post("/api/admin/buildings")
async def api_admin_create_building(request: Request):
    _buildings_db_init()
    payload = await request.json()

    data = {}
    for field, value in dict(payload or {}).items():
        if field in _BUILDING_EDIT_FIELDS:
            data[field] = _clean_building_value(field, value)

    name = str(data.get("name") or "").strip()
    if not name:
        return JSONResponse({"ok": False, "error": "name_required"}, status_code=400)

    if "address" in data:
        data.setdefault("raw_address", data["address"])
        data.setdefault("display_address", data["address"])
    elif "raw_address" in data:
        data.setdefault("address", data["raw_address"])
        data.setdefault("display_address", data["raw_address"])
    elif "display_address" in data:
        data.setdefault("address", data["display_address"])
        data.setdefault("raw_address", data["display_address"])

    with _buildings_engine.begin() as conn:
        if not str(data.get("building_no") or "").strip():
            rows = conn.execute(_buildings_sql_text("SELECT building_no FROM buildings")).fetchall()
            max_no = 0
            for row in rows:
                value = str(row[0] or "")
                m = __import__("re").search(r"B(\d+)", value)
                if m:
                    max_no = max(max_no, int(m.group(1)))
            data["building_no"] = "B" + str(max_no + 1).zfill(3)

        defaults = {
            "area": "",
            "address": "",
            "raw_address": "",
            "display_address": "",
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
            "note": "",
        }

        for key, value in defaults.items():
            data.setdefault(key, value)

        fields = [
            "building_no",
            "name",
            "area",
            "address",
            "raw_address",
            "display_address",
            "management_company",
            "management_phone",
            "manager_name",
            "manager_phone",
            "manager_age",
            "manager_experience",
            "manager_interest",
            "visit_time",
            "committee_time",
            "resident_meeting_time",
            "active_users",
            "total_households",
            "ip",
            "host",
            "note",
        ]

        use_fields = [f for f in fields if f in data]
        sql = (
            "INSERT INTO buildings (" + ", ".join(use_fields) + ", created_at, updated_at) "
            "VALUES (" + ", ".join(":" + f for f in use_fields) + ", datetime('now','localtime'), datetime('now','localtime'))"
        )

        try:
            result = conn.execute(_buildings_sql_text(sql), data)
        except Exception as exc:
            return JSONResponse({"ok": False, "error": str(exc)[:500]}, status_code=400)

        row = conn.execute(
            _buildings_sql_text("SELECT * FROM buildings WHERE id = :id"),
            {"id": result.lastrowid},
        ).mappings().first()

    return _BuildingsResponse(
        content=_buildings_json.dumps({"ok": True, "item": dict(row)}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.get("/api/admin/buildings")
def api_admin_buildings():
    buildings = _fetch_buildings_from_db()

    return _BuildingsResponse(
        content=_buildings_json.dumps(buildings, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.delete("/api/admin/buildings/{building_no}")
def api_admin_delete_building(building_no: str):
    from sqlalchemy import text as _del_text
    from app.db import engine as _del_engine

    building_no = building_no.strip()
    if not building_no:
        return _BuildingsResponse(
            content=_buildings_json.dumps({"ok": False, "error": "無效編號"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    with _del_engine.begin() as conn:
        result = conn.execute(
            _del_text("DELETE FROM buildings WHERE building_no = :no"),
            {"no": building_no},
        )

    if result.rowcount == 0:
        return _BuildingsResponse(
            content=_buildings_json.dumps({"ok": False, "error": "找不到此大樓"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=404,
        )

    return _BuildingsResponse(
        content=_buildings_json.dumps({"ok": True, "deleted": building_no}, ensure_ascii=False),
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
def admin_buildings_page(request: Request):
    _user = _employee_current_user_from_request(request)
    if not _user:
        return RedirectResponse(f"/employee/login?next=/admin/buildings", status_code=303)
    import html as _buildings_html

    def _cell(value):
        return _buildings_html.escape(str(value or ""), quote=True)

    initial_rows = []
    for b in _fetch_buildings_from_db():
        building_no = _cell(b.get("building_no"))
        name = _cell(b.get("name"))
        area = _cell(b.get("area"))
        address = _cell(b.get("address"))
        company = _cell(b.get("management_company"))
        active_users = _cell(b.get("active_users"))
        total_households = _cell(b.get("total_households"))
        ip = _cell(b.get("ip"))
        initial_rows.append(f"""
          <tr data-building-no="{building_no}">
            <td>{building_no}</td>
            <td contenteditable="true" data-field="name">{name}</td>
            <td contenteditable="true" data-field="area"><span class="pill">{area}</span></td>
            <td contenteditable="true" data-field="address">{address}</td>
            <td contenteditable="true" data-field="management_company">{company}</td>
            <td contenteditable="true" data-field="active_users">{active_users}</td>
            <td contenteditable="true" data-field="total_households">{total_households}</td>
            <td contenteditable="true" data-field="ip">{ip}</td>
            <td><button class="btn-small" type="button" onclick="hostLogin('{ip}')">主機登入</button></td>
            <td><button class="btn-small btn-danger" type="button" onclick="deleteBuilding('{building_no}', '{name}')">刪除</button></td>
          </tr>
        """)

    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>\u5927\u6a13\u540d\u9304\uff5c\u4e2d\u592e\u63a7\u7ba1\u7cfb\u7d71</title>
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

    .ip-input {
      width: 100%;
      height: 36px;
      padding: 0 8px;
      border: 1px solid #d7e1ef;
      border-radius: 6px;
      background: #fff;
      color: #1e40af;
      font-size: 13px;
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      cursor: text;
    }
    .ip-input:focus {
      outline: none;
      border-color: #1e40af;
      box-shadow: 0 0 0 2px rgba(30,64,175,.15);
    }

    .area-select {
      width: 100%;
      height: 36px;
      padding: 0 8px;
      border: 1px solid #d7e1ef;
      border-radius: 6px;
      background: #fff;
      color: #102348;
      font-size: 14px;
      font-family: inherit;
      cursor: pointer;
    }

    .area-select:focus {
      outline: none;
      border-color: #365ee8;
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

    .btn-danger {
      background: #dc2626 !important;
      color: #fff !important;
    }

    .btn-danger:hover {
      background: #b91c1c !important;
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

  <link rel="stylesheet" href="/static/web_title_unified.css?v=20260513_cl9b">
</head>

<body>
  <section class="web-title web-title-tech">
  <img class="web-title-watermark" src="/static/shinnan_logo_outline_white.png" alt="">
  <div class="web-title-map"></div>
  <div class="web-title-radar"></div>
  <div class="web-title-main">
    <div class="web-title-logo-box"><img class="web-title-logo" src="/static/shinnan_logo_gold_transparent.png?v=20260513_cl9h" alt="ShinNan Logo"></div>
    <div class="web-title-text">
      <h1 class="web-title-system">&#x5927;&#x6a13;&#x540d;&#x9304;</h1>
      <div class="web-title-sub"><span class="web-title-sub-dot"></span>&#x4e2d;&#x592e;&#x63a7;&#x7ba1;&#x7cfb;&#x7d71;<span class="web-title-sub-dot"></span></div>
    </div>
  </div>
</section>

  <main class="page">
    <div class="web-title-user" data-web-title-user="1" style="margin-bottom:8px;padding:6px 16px;border:1px solid rgba(247,211,111,.6);border-radius:10px;background:rgba(5,42,24,.15);color:#555;font-size:13px;font-weight:700;display:inline-block;">
      <span class="web-title-user-label">登入者：</span><span class="web-title-user-name" id="web_title_user_name">載入中</span>
    </div>
    <div class="toolbar">
      <button type="button" onclick="goBackFromBuildings(event)">返回上一頁</button>
      <button type="button" id="create_building_button">新增資料</button>

      <select id="area_filter">
        <option value="全部">全部區域</option>
        <option value="東區">東區</option>
        <option value="北區">北區</option>
        <option value="北台南">北台南</option>
        <option value="仁德">仁德</option>
        <option value="永康">永康</option>
        <option value="安平">安平</option>
        <option value="高雄">高雄</option>
        <option value="透天">透天</option>
      </select>

      <input id="keyword" placeholder="搜尋大樓 / 地址 / 管理公司 / IP">
    </div>

    <section class="card">
      <div class="hint">提示：大樓名稱、區域、地址、管理公司、用戶數量、住戶總數、IP 可直接點擊修改。選擇大樓時會帶出「大樓名稱 + 地址」。</div>

      <table>
        <thead>
          <tr>
            <th onclick="sortBy('building_no')" style="cursor:pointer;user-select:none">編號 <span id="sort_building_no"></span></th>
            <th onclick="sortBy('name')" style="cursor:pointer;user-select:none">大樓名稱 <span id="sort_name"></span></th>
            <th onclick="sortBy('area')" style="cursor:pointer;user-select:none">區域 <span id="sort_area"></span></th>
            <th onclick="sortBy('address')" style="cursor:pointer;user-select:none">地址 <span id="sort_address"></span></th>
            <th onclick="sortBy('management_company')" style="cursor:pointer;user-select:none">管理公司 <span id="sort_management_company"></span></th>
            <th onclick="sortBy('active_users')" style="cursor:pointer;user-select:none">用戶數量 <span id="sort_active_users"></span></th>
            <th onclick="sortBy('total_households')" style="cursor:pointer;user-select:none">住戶總數 <span id="sort_total_households"></span></th>
            <th onclick="sortBy('management_phone')" style="cursor:pointer;user-select:none">管理室電話 <span id="sort_management_phone"></span></th>
            <th>IP</th>
            <th>刪除</th>
          </tr>
        </thead>
        <tbody id="rows">__INITIAL_BUILDING_ROWS__</tbody>
      </table>
    </section>
  </main>

  <script>
    let buildings = [];
    let sortField = 'building_no';
    let sortAsc = true;
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

    function loadOverrides() {
      try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      } catch (e) {
        return {};
      }
    }

    async function saveOverride(buildingNo, field, value) {
      // 同步存 localStorage（即時顯示）
      const overrides = loadOverrides();
      if (!overrides[buildingNo]) overrides[buildingNo] = {};
      overrides[buildingNo][field] = value;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(overrides));

      // 同步存後端 DB
      const item = buildings.find(b => b.building_no === buildingNo);
      if (!item || !item.id) return;
      try {
        await fetch(`/api/admin/buildings/${item.id}`, {
          method: 'PATCH',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({[field]: value})
        });
      } catch(e) {
        console.error('Save to DB failed:', e);
      }
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
      const areaEl = document.getElementById("area_filter");
      const area = areaEl.value;
      const isAllArea = !area || areaEl.selectedIndex === 0;
      const keyword = document.getElementById("keyword").value.trim().toLowerCase();

      return buildings.filter(function (b) {
        if (!isAllArea && b.area !== area) return false;
        if (!keyword) return true;

        return [
          b.building_no,
          b.name,
          b.area,
          b.address,
          b.management_company,
          b.management_phone
        ].join(" ").toLowerCase().includes(keyword);
      });
    }

    function sortBy(field) {
      if (sortField === field) {
        sortAsc = !sortAsc;
      } else {
        sortField = field;
        sortAsc = true;
      }
      renderRows();
    }

    function getSorted(data) {
      const numFields = ['active_users', 'total_households'];
      return data.slice().sort(function (a, b) {
        let va = a[sortField] ?? '';
        let vb = b[sortField] ?? '';
        if (sortField === 'building_no') {
          va = parseInt(String(va).replace(/[^0-9]/g, '')) || 0;
          vb = parseInt(String(vb).replace(/[^0-9]/g, '')) || 0;
        } else if (numFields.includes(sortField)) {
          va = parseFloat(va) || 0;
          vb = parseFloat(vb) || 0;
        } else {
          va = String(va).toLowerCase();
          vb = String(vb).toLowerCase();
        }
        if (va < vb) return sortAsc ? -1 : 1;
        if (va > vb) return sortAsc ? 1 : -1;
        return 0;
      });
    }

    function updateSortIcons() {
      const fields = ['building_no','name','area','address','management_company','active_users','total_households','management_phone'];
      fields.forEach(function (f) {
        const el = document.getElementById('sort_' + f);
        if (!el) return;
        if (f === sortField) {
          el.textContent = sortAsc ? ' ▲' : ' ▼';
          el.style.color = '#0f6b3b';
        } else {
          el.textContent = ' ⇅';
          el.style.color = '#bbb';
        }
      });
    }

    function renderRows() {
      const rows = document.getElementById("rows");
      const data = getSorted(getFiltered());
      updateSortIcons();

      rows.innerHTML = data.map(function (b) {
        return `
          <tr data-building-no="${escapeHtml(b.building_no)}">
            <td>${escapeHtml(b.building_no)}</td>
            <td contenteditable="true" data-field="name">${escapeHtml(b.name)}</td>
            <td data-field="area" data-building-no="${escapeHtml(b.building_no)}">
              <select class="area-select" data-building-no="${escapeHtml(b.building_no)}" onchange="saveAreaChange(this)">
                <option value="">－ 未分區</option>
                <option value="東區" ${b.area==='東區'?'selected':''}>東區</option>
                <option value="北區" ${b.area==='北區'?'selected':''}>北區</option>
                <option value="安平" ${b.area==='安平'?'selected':''}>安平</option>
                <option value="永康" ${b.area==='永康'?'selected':''}>永康</option>
                <option value="高雄" ${b.area==='高雄'?'selected':''}>高雄</option>
                <option value="北台南" ${b.area==='北台南'?'selected':''}>北台南</option>
              </select>
            </td>
            <td contenteditable="true" data-field="address">${escapeHtml(b.address)}</td>
            <td contenteditable="true" data-field="management_company">${escapeHtml(b.management_company)}</td>
            <td contenteditable="true" data-field="active_users">${escapeHtml(b.active_users)}</td>
            <td contenteditable="true" data-field="total_households">${escapeHtml(b.total_households)}</td>
            <td>${escapeHtml(b.management_phone || '')}</td>
            <td>
              <input class="ip-input" type="text"
                value="${escapeHtml(b.ip || '')}"
                placeholder="IP:Port"
                data-building-no="${escapeHtml(b.building_no)}"
                onchange="saveIpChange(this)">
            </td>
            <td><button class="btn-small btn-danger" type="button" onclick="deleteBuilding('${escapeHtml(b.building_no)}', '${escapeHtml(b.name)}')">刪除</button></td>
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

    async function saveAreaChange(sel) {
      const buildingNo = sel.dataset.buildingNo;
      const value = sel.value;
      const item = buildings.find(b => b.building_no === buildingNo);
      if (item) item.area = value;
      await saveOverride(buildingNo, 'area', value);
    }

    async function saveIpChange(input) {
      const buildingNo = input.dataset.buildingNo;
      const value = input.value.trim();
      const item = buildings.find(b => b.building_no === buildingNo);
      if (item) item.ip = value;
      await saveOverride(buildingNo, 'ip', value);
    }

    function hostLogin(ip) {
      alert("主機登入：" + ip);
    }

    async function deleteBuilding(buildingNo, name) {
      if (!confirm("確定要刪除「" + name + "」（" + buildingNo + "）？\\n刪除後無法復原。")) return;
      try {
        const res = await fetch("/api/admin/buildings/" + encodeURIComponent(buildingNo), {
          method: "DELETE",
          credentials: "same-origin",
        });
        const data = await res.json().catch(function () { return {}; });
        if (!res.ok || !data.ok) {
          alert("刪除失敗：" + (data.error || res.status));
          return;
        }
        buildings = buildings.filter(function (b) { return b.building_no !== buildingNo; });
        renderRows();
      } catch (e) {
        alert("刪除失敗：" + e.message);
      }
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
            <option value="高雄">高雄</option>
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
      if (event.stopImmediatePropagation) event.stopImmediatePropagation();
    }

    const params = new URLSearchParams(window.location.search);
    const caller = params.get("caller") || "";

    if (caller === "sales") {
      window.location.href = "/admin/sales";
      return;
    }

    if (caller === "dispatch") {
      window.location.href = "/admin";
      return;
    }

    const backReturn = localStorage.getItem("xunnan_building_back_return") || "";
    const pickReturn = localStorage.getItem("xunnan_building_pick_return") || "";

    const candidates = [backReturn, pickReturn];

    for (const raw of candidates) {
      if (!raw) continue;
      try {
        const u = new URL(raw, window.location.origin);
        if (u.pathname === "/admin/sales") {
          window.location.href = "/admin/sales";
          return;
        }
        if (u.pathname === "/admin") {
          window.location.href = "/admin";
          return;
        }
      } catch (err) {}
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


<script>
(function () {
  function text(v) {
    return String(v || "").trim();
  }

  function setName(name) {
    var el = document.getElementById("web_title_user_name");
    if (!el) return;
    el.textContent = text(name) || "-";
  }

  function fallbackName() {
    var keys = [
      "xunnan_employee_display_name",
      "xunnan_display_name",
      "xunnan_employee_name",
      "xunnan_engineer_name",
      "xunnan_admin_name"
    ];
    for (var i = 0; i < keys.length; i += 1) {
      try {
        var v = localStorage.getItem(keys[i]) || sessionStorage.getItem(keys[i]);
        if (text(v)) return v;
      } catch (e) {}
    }
    return "";
  }

  setName(fallbackName() || "\u767b\u5165\u8005");

  fetch("/api/app/employee/profile?ts=" + Date.now(), {
    cache: "no-store",
    credentials: "same-origin"
  })
    .then(function (res) {
      if (!res || !res.ok) return null;
      return res.json();
    })
    .then(function (data) {
      if (!data) return;
      var p = data.profile || data.data || data;
      var name =
        p.display_name ||
        p.acting_display_name ||
        p.login_display_name ||
        p.staff_code ||
        data.display_name ||
        data.staff_code ||
        "";
      setName(name || fallbackName() || "\u767b\u5165\u8005");
    })
    .catch(function () {
      setName(fallbackName() || "\u767b\u5165\u8005");
    });
})();
</script>



<script id="cl15g2_buildings_admin_final_fix_v1">
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  function safeBack(event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
      if (event.stopImmediatePropagation) event.stopImmediatePropagation();
    }

    const params = new URLSearchParams(location.search);
    const caller = params.get("caller") || "";

    if (caller === "sales") {
      location.href = "/admin/sales";
      return;
    }

    if (caller === "dispatch") {
      location.href = "/admin";
      return;
    }

    const backReturn = localStorage.getItem("xunnan_building_back_return") || "";
    const pickReturn = localStorage.getItem("xunnan_building_pick_return") || "";

    for (const raw of [backReturn, pickReturn]) {
      if (!raw) continue;
      try {
        const u = new URL(raw, location.origin);
        if (u.pathname === "/admin/sales") {
          location.href = "/admin/sales";
          return;
        }
        if (u.pathname === "/admin") {
          location.href = "/admin";
          return;
        }
      } catch (err) {}
    }

    location.href = "/admin";
  }

  window.goBackFromBuildings = safeBack;

  function bindBack() {
    Array.from(document.querySelectorAll("button, a")).forEach(function (el) {
      const txt = String(el.textContent || "").trim();
      if (txt !== "\u8fd4\u56de\u4e0a\u4e00\u9801" && txt !== "\u8fd4\u56de\u5f8c\u53f0" && txt !== "\u8fd4\u56de\u9996\u9801") return;

      const clone = el.cloneNode(true);
      clone.textContent = "\u8fd4\u56de\u4e0a\u4e00\u9801";
      clone.onclick = safeBack;
      clone.addEventListener("click", safeBack, true);
      el.parentNode.replaceChild(clone, el);
    });
  }

  function valueOf(id) {
    const el = document.getElementById(id);
    return el ? String(el.value || "").trim() : "";
  }

  async function createBuildingToDb(event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
      if (event.stopImmediatePropagation) event.stopImmediatePropagation();
    }

    const name = valueOf("new_building_name");
    const area = valueOf("new_building_area");
    const address = valueOf("new_building_address");
    const managementCompany = valueOf("new_management_company");
    const activeUsers = Number(valueOf("new_active_users").replace(/[^\\d]/g, "") || 0);
    const totalHouseholds = Number(valueOf("new_total_households").replace(/[^\\d]/g, "") || 0);
    const ip = valueOf("new_building_ip");

    if (!name) {
      alert("\u8acb\u8f38\u5165\u5927\u6a13\u540d\u7a31");
      return false;
    }

    const payload = {
      name: name,
      area: area,
      address: address,
      raw_address: address,
      display_address: address,
      management_company: managementCompany,
      active_users: activeUsers,
      total_households: totalHouseholds,
      ip: ip
    };

    try {
      const res = await fetch("/api/admin/buildings", {
        method: "POST",
        headers: {"Content-Type": "application/json; charset=utf-8"},
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(await res.text());
      }

      const modal = document.getElementById("create_building_modal");
      if (modal) modal.classList.remove("active");

      ["new_building_name", "new_building_address", "new_management_company", "new_building_ip"].forEach(function (id) {
        const el = document.getElementById(id);
        if (el) el.value = "";
      });

      const au = document.getElementById("new_active_users");
      const th = document.getElementById("new_total_households");
      if (au) au.value = "0";
      if (th) th.value = "0";

      if (typeof window.loadBuildings === "function") {
        await window.loadBuildings();
      } else {
        location.reload();
      }

      alert("\u5927\u6a13\u8cc7\u6599\u5df2\u65b0\u589e");
      return false;
    } catch (err) {
      console.error("create building failed", err);
      alert("\u65b0\u589e\u5927\u6a13\u5931\u6557\uff0c\u8acb\u518d\u8a66\u4e00\u6b21\u3002");
      return false;
    }
  }

  function bindCreateSave() {
    const btn = document.getElementById("save_create_building_button");
    if (!btn || btn.dataset.cl15g2Bound === "1") return;

    const clone = btn.cloneNode(true);
    clone.dataset.cl15g2Bound = "1";
    clone.onclick = createBuildingToDb;
    clone.addEventListener("click", createBuildingToDb, true);
    btn.parentNode.replaceChild(clone, btn);
  }

  function bindAll() {
    bindBack();
    bindCreateSave();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindAll);
  } else {
    bindAll();
  }

  setTimeout(bindAll, 300);
  setTimeout(bindAll, 900);
})();
</script>


  <script src="/static/app_header_actions.js?v=cl17p6"></script>
</body>
</html>
""".replace("__INITIAL_BUILDING_ROWS__", "\n".join(initial_rows))
# SHINNAN_BUILDINGS_PAGE_RESTORE_END
