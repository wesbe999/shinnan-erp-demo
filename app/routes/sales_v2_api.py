# SHINNAN_SALES_V2_API
"""
訊南業務系統 v2 API
涵蓋：活動歷史、拜訪備忘、提醒、設備、目標、行程事件
"""
from __future__ import annotations
import json as _json
from datetime import datetime, date, timedelta

from fastapi import APIRouter, Request, Body
from fastapi.responses import JSONResponse, RedirectResponse

from sqlalchemy import text as _sql
from app.db import engine as _db
from app.routes.employee_auth import _employee_current_user_from_request

router = APIRouter(tags=["業務系統 v2 API"])

# ─── 工具函數 ───────────────────────────────────────────────
def _ok(data=None, **kw):
    return JSONResponse({"ok": True, **({"data": data} if data is not None else {}), **kw},
                        media_type="application/json; charset=utf-8")

def _err(msg, status=400):
    return JSONResponse({"ok": False, "error": msg}, status_code=status,
                        media_type="application/json; charset=utf-8")

def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _today():
    return date.today().isoformat()

def _require_login(request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return None, JSONResponse({"ok": False, "error": "login required"}, status_code=401)
    return user, None

# ═══════════════════════════════════════════════════════
# 1. 活動歷史 API  /api/v2/sales/activities
# ═══════════════════════════════════════════════════════

@router.get("/api/v2/sales/activities")
def list_activities(request: Request, building_no: str = "", owner: str = "",
                    category: str = "", year: int = 0, month: int = 0,
                    limit: int = 50, offset: int = 0):
    user, err = _require_login(request)
    if err: return err

    where, params = ["1=1"], {}
    if building_no:
        where.append("a.building_no = :building_no")
        params["building_no"] = building_no
    if owner:
        where.append("a.owner = :owner")
        params["owner"] = owner
    if category:
        where.append("a.activity_category = :category")
        params["category"] = category
    if year:
        where.append("substr(a.activity_date,1,4) = :year")
        params["year"] = str(year)
    if month:
        where.append("substr(a.activity_date,6,2) = :month")
        params["month"] = str(month).zfill(2)

    params["limit"] = limit
    params["offset"] = offset

    with _db.begin() as conn:
        rows = conn.execute(_sql(f"""
            SELECT a.*, b.name AS building_name, b.area
            FROM sales_activities a
            LEFT JOIN buildings b ON b.building_no = a.building_no
            WHERE {' AND '.join(where)}
            ORDER BY a.activity_date DESC, a.id DESC
            LIMIT :limit OFFSET :offset
        """), params).mappings().fetchall()
        total = conn.execute(_sql(f"""
            SELECT COUNT(*) FROM sales_activities a
            WHERE {' AND '.join(where)}
        """), {k: v for k, v in params.items() if k not in ('limit','offset')}).scalar()

    return _ok([dict(r) for r in rows], total=total)


@router.post("/api/v2/sales/activities")
async def create_activity(request: Request):
    user, err = _require_login(request)
    if err: return err

    body = await request.json()
    required = ["building_no", "activity_category", "activity_type", "activity_date"]
    for f in required:
        if not body.get(f):
            return _err(f"缺少必填欄位：{f}")

    now = _now()
    with _db.begin() as conn:
        conn.execute(_sql("""
            INSERT INTO sales_activities
            (building_no, activity_category, activity_type, activity_date,
             owner, result, cost, participants, new_users,
             device_type, device_count, device_serial, device_status,
             file_url, photo_data, note, linked_ticket_id, created_by, created_at, updated_at)
            VALUES
            (:building_no, :activity_category, :activity_type, :activity_date,
             :owner, :result, :cost, :participants, :new_users,
             :device_type, :device_count, :device_serial, :device_status,
             :file_url, :photo_data, :note, :linked_ticket_id, :created_by, :now, :now)
        """), {
            "building_no":       body.get("building_no",""),
            "activity_category": body.get("activity_category",""),
            "activity_type":     body.get("activity_type",""),
            "activity_date":     body.get("activity_date",""),
            "owner":             body.get("owner", user.get("display_name","")),
            "result":            body.get("result",""),
            "cost":              body.get("cost", 0),
            "participants":      body.get("participants", 0),
            "new_users":         body.get("new_users", 0),
            "device_type":       body.get("device_type",""),
            "device_count":      body.get("device_count", 0),
            "device_serial":     body.get("device_serial",""),
            "device_status":     body.get("device_status",""),
            "file_url":          body.get("file_url",""),
            "photo_data":        body.get("photo_data",""),
            "note":              body.get("note",""),
            "linked_ticket_id":  body.get("linked_ticket_id", 0),
            "created_by":        user.get("display_name",""),
            "now":               now,
        })
        # 更新大樓最後活動日
        conn.execute(_sql("""
            UPDATE buildings SET last_activity_date = :date, updated_at = :now
            WHERE building_no = :building_no
        """), {"date": body["activity_date"], "now": now, "building_no": body["building_no"]})

    return _ok(message="活動已新增")


@router.put("/api/v2/sales/activities/{activity_id}")
async def update_activity(activity_id: int, request: Request):
    user, err = _require_login(request)
    if err: return err

    body = await request.json()
    now = _now()
    fields = ["activity_category","activity_type","activity_date","owner","result",
              "cost","participants","new_users","device_type","device_count",
              "device_serial","device_status","file_url","photo_data","note"]
    sets = ", ".join(f"{f} = :{f}" for f in fields if f in body)
    if not sets:
        return _err("沒有可更新的欄位")

    with _db.begin() as conn:
        conn.execute(_sql(f"UPDATE sales_activities SET {sets}, updated_at = :now WHERE id = :id"),
                     {**{f: body[f] for f in fields if f in body}, "now": now, "id": activity_id})

    return _ok(message="活動已更新")


@router.delete("/api/v2/sales/activities/{activity_id}")
def delete_activity(activity_id: int, request: Request):
    user, err = _require_login(request)
    if err: return err

    with _db.begin() as conn:
        conn.execute(_sql("DELETE FROM sales_activities WHERE id = :id"), {"id": activity_id})

    return _ok(message="活動已刪除")

# ═══════════════════════════════════════════════════════
# 2. 拜訪備忘 API  /api/v2/sales/memos
# ═══════════════════════════════════════════════════════

@router.get("/api/v2/sales/memos")
def list_memos(request: Request, building_no: str = "", owner: str = "",
               limit: int = 30, offset: int = 0):
    user, err = _require_login(request)
    if err: return err

    where, params = ["1=1"], {}
    if building_no:
        where.append("m.building_no = :building_no")
        params["building_no"] = building_no
    if owner:
        where.append("m.owner = :owner")
        params["owner"] = owner

    params["limit"] = limit
    params["offset"] = offset

    with _db.begin() as conn:
        rows = conn.execute(_sql(f"""
            SELECT m.*, b.name AS building_name, b.area
            FROM sales_memos m
            LEFT JOIN buildings b ON b.building_no = m.building_no
            WHERE {' AND '.join(where)}
            ORDER BY m.visit_date DESC, m.id DESC
            LIMIT :limit OFFSET :offset
        """), params).mappings().fetchall()

    return _ok([dict(r) for r in rows])


@router.post("/api/v2/sales/memos")
async def create_memo(request: Request):
    user, err = _require_login(request)
    if err: return err

    body = await request.json()
    if not body.get("building_no"):
        return _err("缺少 building_no")

    now = _now()
    visit_date = body.get("visit_date") or _today()

    with _db.begin() as conn:
        conn.execute(_sql("""
            INSERT INTO sales_memos
            (building_no, sales_record_id, visit_date, owner,
             visit_result, content, next_action, next_visit_date, important, created_at, updated_at)
            VALUES
            (:building_no, :sales_record_id, :visit_date, :owner,
             :visit_result, :content, :next_action, :next_visit_date, :important, :now, :now)
        """), {
            "building_no":     body.get("building_no",""),
            "sales_record_id": body.get("sales_record_id", 0),
            "visit_date":      visit_date,
            "owner":           body.get("owner", user.get("display_name","")),
            "visit_result":    body.get("visit_result",""),
            "content":         body.get("content",""),
            "next_action":     body.get("next_action",""),
            "next_visit_date": body.get("next_visit_date",""),
            "important":       1 if body.get("important") else 0,
            "now":             now,
        })
        # 更新大樓最後拜訪日
        conn.execute(_sql("""
            UPDATE buildings SET last_visit_date = :date, updated_at = :now
            WHERE building_no = :building_no
        """), {"date": visit_date, "now": now, "building_no": body["building_no"]})

        # 更新業務記錄拜訪次數與最後拜訪日
        if body.get("sales_record_id"):
            conn.execute(_sql("""
                UPDATE sales_business_records
                SET visit_count = COALESCE(visit_count,0) + 1,
                    last_visit_date = :date,
                    updated_at = :now
                WHERE id = :id
            """), {"date": visit_date, "now": now, "id": body["sales_record_id"]})

    return _ok(message="備忘已儲存")


@router.delete("/api/v2/sales/memos/{memo_id}")
def delete_memo(memo_id: int, request: Request):
    user, err = _require_login(request)
    if err: return err

    with _db.begin() as conn:
        conn.execute(_sql("DELETE FROM sales_memos WHERE id = :id"), {"id": memo_id})

    return _ok(message="備忘已刪除")


# ═══════════════════════════════════════════════════════
# 3. 提醒 API  /api/v2/sales/reminders
# ═══════════════════════════════════════════════════════

@router.get("/api/v2/sales/reminders")
def list_reminders(request: Request, building_no: str = "", status: str = "",
                   days: int = 30):
    user, err = _require_login(request)
    if err: return err

    # 只撈出 days 天內到期的提醒
    cutoff = (date.today() + timedelta(days=days)).isoformat()
    where = ["r.remind_date <= :cutoff"]
    params: dict = {"cutoff": cutoff}

    if building_no:
        where.append("r.building_no = :building_no")
        params["building_no"] = building_no
    if status:
        where.append("r.status = :status")
        params["status"] = status
    else:
        where.append("r.status != 'done'")

    with _db.begin() as conn:
        rows = conn.execute(_sql(f"""
            SELECT r.*, b.name AS building_name, b.area
            FROM sales_reminders r
            LEFT JOIN buildings b ON b.building_no = r.building_no
            WHERE {' AND '.join(where)}
            ORDER BY r.remind_date ASC
        """), params).mappings().fetchall()

    return _ok([dict(r) for r in rows])


@router.post("/api/v2/sales/reminders")
async def create_reminder(request: Request):
    user, err = _require_login(request)
    if err: return err

    body = await request.json()
    if not body.get("building_no") or not body.get("reminder_type") or not body.get("remind_date"):
        return _err("缺少必填欄位")

    now = _now()
    with _db.begin() as conn:
        conn.execute(_sql("""
            INSERT INTO sales_reminders
            (building_no, reminder_type, remind_date, days_before,
             status, auto_generated, source_field, note, created_by, created_at, updated_at)
            VALUES
            (:building_no, :reminder_type, :remind_date, :days_before,
             'pending', :auto_generated, :source_field, :note, :created_by, :now, :now)
        """), {
            "building_no":    body.get("building_no",""),
            "reminder_type":  body.get("reminder_type",""),
            "remind_date":    body.get("remind_date",""),
            "days_before":    body.get("days_before", 7),
            "auto_generated": 1 if body.get("auto_generated") else 0,
            "source_field":   body.get("source_field",""),
            "note":           body.get("note",""),
            "created_by":     user.get("display_name",""),
            "now":            now,
        })

    return _ok(message="提醒已建立")


@router.post("/api/v2/sales/reminders/{reminder_id}/done")
def mark_reminder_done(reminder_id: int, request: Request):
    user, err = _require_login(request)
    if err: return err

    with _db.begin() as conn:
        conn.execute(_sql("""
            UPDATE sales_reminders SET status = 'done', updated_at = :now WHERE id = :id
        """), {"now": _now(), "id": reminder_id})

    return _ok(message="已標記完成")

# ═══════════════════════════════════════════════════════
# 4. 行程事件 API  /api/v2/sales/events
# ═══════════════════════════════════════════════════════

@router.get("/api/v2/sales/events")
def list_events(request: Request, building_no: str = "", owner: str = "",
                status: str = "", year: int = 0, month: int = 0):
    user, err = _require_login(request)
    if err: return err

    where, params = ["1=1"], {}
    if building_no:
        where.append("e.building_no = :building_no")
        params["building_no"] = building_no
    if owner:
        where.append("e.owner = :owner")
        params["owner"] = owner
    if status:
        where.append("e.status = :status")
        params["status"] = status
    if year:
        where.append("substr(e.event_date,1,4) = :year")
        params["year"] = str(year)
    if month:
        where.append("substr(e.event_date,6,2) = :month")
        params["month"] = str(month).zfill(2)

    with _db.begin() as conn:
        rows = conn.execute(_sql(f"""
            SELECT e.*, b.name AS building_name, b.area,
                   b.manager_name, b.manager_phone, b.management_phone
            FROM sales_events e
            LEFT JOIN buildings b ON b.building_no = e.building_no
            WHERE {' AND '.join(where)}
            ORDER BY e.event_date ASC, e.event_time ASC
        """), params).mappings().fetchall()

    return _ok([dict(r) for r in rows])


@router.post("/api/v2/sales/events")
async def create_event(request: Request):
    user, err = _require_login(request)
    if err: return err

    body = await request.json()
    if not body.get("building_no") or not body.get("event_type") or not body.get("event_date"):
        return _err("缺少必填欄位")

    now = _now()
    with _db.begin() as conn:
        conn.execute(_sql("""
            INSERT INTO sales_events
            (building_no, event_type, event_date, event_time, location,
             owner, status, attendees, result, remind_days_before, note, created_by, created_at, updated_at)
            VALUES
            (:building_no, :event_type, :event_date, :event_time, :location,
             :owner, :status, :attendees, :result, :remind_days_before, :note, :created_by, :now, :now)
        """), {
            "building_no":        body.get("building_no",""),
            "event_type":         body.get("event_type",""),
            "event_date":         body.get("event_date",""),
            "event_time":         body.get("event_time",""),
            "location":           body.get("location",""),
            "owner":              body.get("owner", user.get("display_name","")),
            "status":             body.get("status","scheduled"),
            "attendees":          body.get("attendees", 0),
            "result":             body.get("result",""),
            "remind_days_before": body.get("remind_days_before", 3),
            "note":               body.get("note",""),
            "created_by":         user.get("display_name",""),
            "now":                now,
        })

        # 自動建立提醒
        remind_days = body.get("remind_days_before", 3)
        event_dt = date.fromisoformat(body["event_date"])
        remind_dt = event_dt - timedelta(days=remind_days)
        conn.execute(_sql("""
            INSERT INTO sales_reminders
            (building_no, reminder_type, remind_date, days_before,
             status, auto_generated, source_field, note, created_by, created_at, updated_at)
            VALUES
            (:building_no, :type, :remind_date, :days,
             'pending', 1, 'sales_events', :note, :by, :now, :now)
        """), {
            "building_no": body["building_no"],
            "type":        f"{body['event_type']}提醒",
            "remind_date": remind_dt.isoformat(),
            "days":        remind_days,
            "note":        f"{body['event_date']} {body.get('event_time','')} {body.get('location','')}",
            "by":          user.get("display_name",""),
            "now":         now,
        })

    return _ok(message="活動已建立，提醒已自動設定")


@router.put("/api/v2/sales/events/{event_id}")
async def update_event(event_id: int, request: Request):
    user, err = _require_login(request)
    if err: return err

    body = await request.json()
    now = _now()
    fields = ["event_type","event_date","event_time","location","owner",
              "status","attendees","result","remind_days_before","note"]
    sets = ", ".join(f"{f} = :{f}" for f in fields if f in body)
    if not sets:
        return _err("沒有可更新的欄位")

    with _db.begin() as conn:
        conn.execute(_sql(f"UPDATE sales_events SET {sets}, updated_at = :now WHERE id = :id"),
                     {**{f: body[f] for f in fields if f in body}, "now": now, "id": event_id})

    return _ok(message="活動已更新")


@router.post("/api/v2/sales/events/{event_id}/complete")
async def complete_event(event_id: int, request: Request):
    user, err = _require_login(request)
    if err: return err

    body = await request.json()
    now = _now()
    with _db.begin() as conn:
        conn.execute(_sql("""
            UPDATE sales_events
            SET status = 'completed', result = :result,
                attendees = :attendees, updated_at = :now
            WHERE id = :id
        """), {
            "result":    body.get("result",""),
            "attendees": body.get("attendees", 0),
            "now":       now,
            "id":        event_id,
        })

    return _ok(message="活動已標記完成")

# ═══════════════════════════════════════════════════════
# 5. 設備管理 API  /api/v2/sales/devices
# ═══════════════════════════════════════════════════════

@router.get("/api/v2/sales/devices")
def list_devices(request: Request, building_no: str = "", status: str = ""):
    user, err = _require_login(request)
    if err: return err

    where, params = ["1=1"], {}
    if building_no:
        where.append("d.building_no = :building_no")
        params["building_no"] = building_no
    if status:
        where.append("d.status = :status")
        params["status"] = status

    with _db.begin() as conn:
        rows = conn.execute(_sql(f"""
            SELECT d.*, b.name AS building_name
            FROM sales_devices d
            LEFT JOIN buildings b ON b.building_no = d.building_no
            WHERE {' AND '.join(where)}
            ORDER BY d.updated_at DESC
        """), params).mappings().fetchall()

    return _ok([dict(r) for r in rows])


@router.post("/api/v2/sales/devices")
async def create_device(request: Request):
    user, err = _require_login(request)
    if err: return err

    body = await request.json()
    if not body.get("device_type"):
        return _err("缺少 device_type")

    now = _now()
    with _db.begin() as conn:
        conn.execute(_sql("""
            INSERT INTO sales_devices
            (device_no, device_type, model, serial, status,
             building_no, customer_no, owner, lend_date, return_date,
             activity_id, note, created_at, updated_at)
            VALUES
            (:device_no, :device_type, :model, :serial, :status,
             :building_no, :customer_no, :owner, :lend_date, :return_date,
             :activity_id, :note, :now, :now)
        """), {
            "device_no":    body.get("device_no",""),
            "device_type":  body.get("device_type",""),
            "model":        body.get("model",""),
            "serial":       body.get("serial",""),
            "status":       body.get("status","available"),
            "building_no":  body.get("building_no",""),
            "customer_no":  body.get("customer_no",""),
            "owner":        body.get("owner", user.get("display_name","")),
            "lend_date":    body.get("lend_date",""),
            "return_date":  body.get("return_date",""),
            "activity_id":  body.get("activity_id", 0),
            "note":         body.get("note",""),
            "now":          now,
        })

    return _ok(message="設備已登錄")


@router.put("/api/v2/sales/devices/{device_id}/return")
async def return_device(device_id: int, request: Request):
    user, err = _require_login(request)
    if err: return err

    body = await request.json()
    now = _now()
    with _db.begin() as conn:
        conn.execute(_sql("""
            UPDATE sales_devices
            SET status = 'returned', return_date = :date,
                building_no = '', customer_no = '', updated_at = :now
            WHERE id = :id
        """), {"date": body.get("return_date", _today()), "now": now, "id": device_id})

    return _ok(message="設備已歸還")


# ═══════════════════════════════════════════════════════
# 6. 業務目標 API  /api/v2/sales/targets
# ═══════════════════════════════════════════════════════

@router.get("/api/v2/sales/targets")
def list_targets(request: Request, owner: str = "", year: int = 0, month: int = 0):
    user, err = _require_login(request)
    if err: return err

    where, params = ["1=1"], {}
    if owner:
        where.append("owner = :owner")
        params["owner"] = owner
    if year:
        where.append("year = :year")
        params["year"] = year
    if month:
        where.append("month = :month")
        params["month"] = month

    with _db.begin() as conn:
        rows = conn.execute(_sql(f"""
            SELECT * FROM sales_targets WHERE {' AND '.join(where)}
            ORDER BY year DESC, month DESC
        """), params).mappings().fetchall()

    return _ok([dict(r) for r in rows])


@router.post("/api/v2/sales/targets")
async def upsert_target(request: Request):
    user, err = _require_login(request)
    if err: return err

    body = await request.json()
    if not body.get("owner") or not body.get("year") or not body.get("month"):
        return _err("缺少必填欄位")

    now = _now()
    with _db.begin() as conn:
        existing = conn.execute(_sql("""
            SELECT id FROM sales_targets WHERE owner=:owner AND year=:year AND month=:month
        """), {"owner": body["owner"], "year": body["year"], "month": body["month"]}).first()

        if existing:
            fields = ["area","target_new_users","target_contracts","target_revenue",
                      "target_visits","target_activities","actual_new_users",
                      "actual_contracts","actual_revenue","actual_visits","actual_activities","note"]
            sets = ", ".join(f"{f} = :{f}" for f in fields if f in body)
            if sets:
                conn.execute(_sql(f"UPDATE sales_targets SET {sets}, updated_at = :now WHERE id = :id"),
                             {**{f: body[f] for f in fields if f in body}, "now": now, "id": existing[0]})
        else:
            conn.execute(_sql("""
                INSERT INTO sales_targets
                (owner, year, month, area, target_new_users, target_contracts,
                 target_revenue, target_visits, target_activities, note, created_at, updated_at)
                VALUES
                (:owner, :year, :month, :area, :target_new_users, :target_contracts,
                 :target_revenue, :target_visits, :target_activities, :note, :now, :now)
            """), {
                "owner":              body.get("owner",""),
                "year":               body.get("year", 0),
                "month":              body.get("month", 0),
                "area":               body.get("area",""),
                "target_new_users":   body.get("target_new_users", 0),
                "target_contracts":   body.get("target_contracts", 0),
                "target_revenue":     body.get("target_revenue", 0),
                "target_visits":      body.get("target_visits", 0),
                "target_activities":  body.get("target_activities", 0),
                "note":               body.get("note",""),
                "now":                now,
            })

    return _ok(message="目標已儲存")

# ═══════════════════════════════════════════════════════
# 7. 大樓完整資料 API  /api/v2/sales/buildings/{building_no}
# ═══════════════════════════════════════════════════════

@router.get("/api/v2/sales/buildings/{building_no}")
def get_building_full(building_no: str, request: Request):
    user, err = _require_login(request)
    if err: return err

    with _db.begin() as conn:
        # 大樓基本資料
        building = conn.execute(_sql("""
            SELECT b.*, s.id AS sales_id, s.status, s.contract_status,
                   s.contract_end_date, s.next_visit, s.owner, s.business_note,
                   s.business_type, s.event_type, s.event_status,
                   s.event_schedule_date, s.important_schedule,
                   s.last_visit_date, s.visit_count, s.competitor, s.competitor_price,
                   s.feedback_type, s.feedback_status, s.demo_type
            FROM buildings b
            LEFT JOIN sales_business_records s ON s.building_no = b.building_no
            WHERE b.building_no = :no
            ORDER BY s.id DESC LIMIT 1
        """), {"no": building_no}).mappings().first()

        if not building:
            return _err("找不到大樓", 404)

        # 最近 20 筆活動
        activities = conn.execute(_sql("""
            SELECT * FROM sales_activities
            WHERE building_no = :no
            ORDER BY activity_date DESC, id DESC LIMIT 20
        """), {"no": building_no}).mappings().fetchall()

        # 最近 20 筆備忘
        memos = conn.execute(_sql("""
            SELECT * FROM sales_memos
            WHERE building_no = :no
            ORDER BY visit_date DESC, id DESC LIMIT 20
        """), {"no": building_no}).mappings().fetchall()

        # 未來 60 天的行程事件
        future = (date.today() + timedelta(days=60)).isoformat()
        events = conn.execute(_sql("""
            SELECT * FROM sales_events
            WHERE building_no = :no AND status != 'completed'
              AND event_date >= :today
            ORDER BY event_date ASC LIMIT 10
        """), {"no": building_no, "today": _today()}).mappings().fetchall()

        # 未完成提醒
        reminders = conn.execute(_sql("""
            SELECT * FROM sales_reminders
            WHERE building_no = :no AND status != 'done'
            ORDER BY remind_date ASC LIMIT 10
        """), {"no": building_no}).mappings().fetchall()

        # 設備
        devices = conn.execute(_sql("""
            SELECT * FROM sales_devices
            WHERE building_no = :no AND status != 'returned'
        """), {"no": building_no}).mappings().fetchall()

        # 用戶帳務統計
        billing_stats = conn.execute(_sql("""
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN is_overdue = 1 THEN 1 ELSE 0 END) AS overdue,
                   SUM(monthly_fee) AS monthly_revenue
            FROM customer_accounts WHERE building_no = :no AND service_status != '停用'
        """), {"no": building_no}).mappings().first()

    data = dict(building)
    data["activities"]    = [dict(r) for r in activities]
    data["memos"]         = [dict(r) for r in memos]
    data["events"]        = [dict(r) for r in events]
    data["reminders"]     = [dict(r) for r in reminders]
    data["devices"]       = [dict(r) for r in devices]
    data["billing_stats"] = dict(billing_stats) if billing_stats else {}

    # 計算滲透率
    total_hh = data.get("total_households") or 0
    active    = data.get("active_users") or 0
    data["penetration_rate"] = round(active / total_hh * 100, 1) if total_hh > 0 else 0

    return _ok(data)


# ═══════════════════════════════════════════════════════
# 8. 主管儀表板 API  /api/v2/sales/dashboard
# ═══════════════════════════════════════════════════════

@router.get("/api/v2/sales/dashboard")
def get_dashboard(request: Request, area: str = "", owner: str = "",
                  year: int = 0, month: int = 0):
    user, err = _require_login(request)
    if err: return err

    y = year or date.today().year
    m = month or date.today().month
    ym = f"{y}-{str(m).zfill(2)}"
    prev_m = m - 1 if m > 1 else 12
    prev_y = y if m > 1 else y - 1
    prev_ym = f"{prev_y}-{str(prev_m).zfill(2)}"

    where_area = "AND b.area = :area" if area else ""
    where_owner = "AND s.owner = :owner" if owner else ""
    params = {"ym": ym, "prev_ym": prev_ym}
    if area: params["area"] = area
    if owner: params["owner"] = owner

    with _db.begin() as conn:
        # 合約統計
        contract_stats = conn.execute(_sql(f"""
            SELECT s.contract_status, COUNT(*) AS cnt
            FROM sales_business_records s
            LEFT JOIN buildings b ON b.building_no = s.building_no
            WHERE 1=1 {where_area} {where_owner}
            GROUP BY s.contract_status
        """), params).mappings().fetchall()

        # 本月活動統計
        activity_stats = conn.execute(_sql(f"""
            SELECT a.activity_category, COUNT(*) AS cnt, SUM(a.new_users) AS new_users
            FROM sales_activities a
            LEFT JOIN buildings b ON b.building_no = a.building_no
            WHERE substr(a.activity_date,1,7) = :ym {where_area} {where_owner}
            GROUP BY a.activity_category
        """), params).mappings().fetchall()

        # 業務員排行
        owner_stats = conn.execute(_sql(f"""
            SELECT a.owner,
                   COUNT(*) AS activity_count,
                   SUM(a.new_users) AS new_users,
                   COUNT(DISTINCT a.building_no) AS building_count
            FROM sales_activities a
            WHERE substr(a.activity_date,1,7) = :ym
            GROUP BY a.owner
            ORDER BY new_users DESC
        """), params).mappings().fetchall()

        # 即將到期合約（60天內）
        expiring = conn.execute(_sql(f"""
            SELECT s.contract_end_date, b.name, b.area, s.owner, s.contract_status
            FROM sales_business_records s
            LEFT JOIN buildings b ON b.building_no = s.building_no
            WHERE s.contract_end_date != ''
              AND s.contract_end_date BETWEEN :today AND :future
              {where_area} {where_owner}
            ORDER BY s.contract_end_date ASC
            LIMIT 20
        """), {**params, "today": _today(),
               "future": (date.today() + timedelta(days=60)).isoformat()}).mappings().fetchall()

        # 逾期拜訪
        overdue_visits = conn.execute(_sql(f"""
            SELECT s.next_visit, b.name, b.area, s.owner, s.important_schedule
            FROM sales_business_records s
            LEFT JOIN buildings b ON b.building_no = s.building_no
            WHERE s.next_visit != '' AND s.next_visit < :today
              AND s.status != '已完成' {where_area} {where_owner}
            ORDER BY s.next_visit ASC LIMIT 20
        """), {**params, "today": _today()}).mappings().fetchall()

        # 用戶成長（本月 vs 上月）
        growth = conn.execute(_sql(f"""
            SELECT
                SUM(CASE WHEN b.area = b.area THEN b.active_users ELSE 0 END) AS current_users,
                SUM(b.total_households) AS total_households,
                SUM(b.monthly_revenue) AS monthly_revenue
            FROM buildings b
            LEFT JOIN sales_business_records s ON s.building_no = b.building_no
            WHERE 1=1 {where_area}
        """), params).mappings().first()

    return _ok({
        "period":          ym,
        "contract_stats":  [dict(r) for r in contract_stats],
        "activity_stats":  [dict(r) for r in activity_stats],
        "owner_stats":     [dict(r) for r in owner_stats],
        "expiring":        [dict(r) for r in expiring],
        "overdue_visits":  [dict(r) for r in overdue_visits],
        "growth":          dict(growth) if growth else {},
    })


# ═══════════════════════════════════════════════════════
# 9. 自動生成提醒（從合約到期/事件日期）
# ═══════════════════════════════════════════════════════

@router.post("/api/v2/sales/reminders/auto-generate")
def auto_generate_reminders(request: Request):
    """根據合約到期日、管委會時間、住戶大會自動生成提醒"""
    user, err = _require_login(request)
    if err: return err

    now = _now()
    today = _today()
    future_90 = (date.today() + timedelta(days=90)).isoformat()
    created = 0

    with _db.begin() as conn:
        # 合約到期提醒
        records = conn.execute(_sql("""
            SELECT s.building_no, s.contract_end_date, b.name
            FROM sales_business_records s
            LEFT JOIN buildings b ON b.building_no = s.building_no
            WHERE s.contract_end_date BETWEEN :today AND :future
              AND s.contract_end_date != ''
        """), {"today": today, "future": future_90}).mappings().fetchall()

        for r in records:
            remind_dt = (date.fromisoformat(r["contract_end_date"]) - timedelta(days=14)).isoformat()
            exists = conn.execute(_sql("""
                SELECT id FROM sales_reminders
                WHERE building_no=:no AND reminder_type='合約到期' AND remind_date=:dt
            """), {"no": r["building_no"], "dt": remind_dt}).first()
            if not exists:
                conn.execute(_sql("""
                    INSERT INTO sales_reminders
                    (building_no, reminder_type, remind_date, days_before,
                     status, auto_generated, source_field, note, created_by, created_at, updated_at)
                    VALUES (:no, '合約到期', :dt, 14, 'pending', 1, 'contract_end_date',
                            :note, 'system', :now, :now)
                """), {"no": r["building_no"], "dt": remind_dt,
                       "note": f"{r['name']} 合約到期：{r['contract_end_date']}",
                       "now": now})
                created += 1

    return _ok(message=f"自動生成 {created} 筆提醒")
