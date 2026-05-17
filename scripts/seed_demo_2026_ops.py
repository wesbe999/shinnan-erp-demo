#!/usr/bin/env python3
"""Seed 2026 demo operation data for Shinnan ERP.

The source code in this file is intentionally ASCII-only. Demo text written to
SQLite uses Python Unicode escape literals so PowerShell/CP950 cannot corrupt it.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import shutil
import sqlite3
from pathlib import Path


START_DATE = dt.date(2026, 1, 1)
END_DATE = dt.date(2026, 5, 11)
RANDOM_SEED = 20260511

PRESERVE_TABLES = {
    "_codex_write_probe",
    "company_holidays",
    "employee_accounts",
    "employee_holidays",
    "employee_leave_settings",
    "employee_profiles",
    "employee_proxy_settings",
    "employee_rest_month_settings",
    "employee_rest_months",
    "employee_sessions",
    "hr_change_logs",
    "hr_leave_requests",
    "hr_salary_profiles",
    "manager_department_scopes",
}

OPERATION_TABLE_ORDER = [
    "ticket_install_details",
    "ticket_return_details",
    "ticket_customer_candidates",
    "dispatch_material_usage",
    "dispatch_repair_analysis",
    "tickets",
    "manager_approval_requests",
    "customer_service_items",
    "customer_accounts",
    "billing_service_plans",
    "sales_business_records",
    "purchase_requests",
    "product_promotion_records",
    "project_records",
    "manager_contacts",
    "buildings",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="xunnan_dispatch.db")
    parser.add_argument("--line-sample", default="")
    parser.add_argument("--report", default="reports/demo_2026_seed_audit.txt")
    parser.add_argument("--customers", type=int, default=650)
    parser.add_argument("--tickets", type=int, default=1100)
    parser.add_argument("--area-focus", choices=["all", "east", "north", "anping", "north_tainan", "yongkang"], default="all")
    parser.add_argument("--clear-scope", choices=["all", "focus"], default="all")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def schema(conn: sqlite3.Connection) -> dict[str, dict]:
    cur = conn.cursor()
    table_names = [
        r[0]
        for r in cur.execute(
            "select name from sqlite_master "
            "where type='table' and name not like 'sqlite_%' order by name"
        ).fetchall()
    ]
    out: dict[str, dict] = {}
    for table in table_names:
        cols = cur.execute(f'pragma table_info("{table}")').fetchall()
        out[table] = {
            "columns": [
                {
                    "cid": c[0],
                    "name": c[1],
                    "type": c[2] or "",
                    "notnull": bool(c[3]),
                    "default": c[4],
                    "pk": c[5],
                }
                for c in cols
            ],
            "column_names": [c[1] for c in cols],
        }
    return out


def has_table(sc: dict[str, dict], table: str) -> bool:
    return table in sc


def insert_row(conn: sqlite3.Connection, sc: dict[str, dict], table: str, values: dict) -> int | None:
    if table not in sc:
        return None
    row = {}
    for col in sc[table]["columns"]:
        name = col["name"]
        typ = col["type"].upper()
        if col["pk"] and "INT" in typ:
            continue
        if name in values:
            row[name] = values[name]
        elif col["notnull"] and col["default"] is None:
            if any(token in typ for token in ("INT", "REAL", "NUMERIC", "DECIMAL", "FLOAT")):
                row[name] = 0
            else:
                row[name] = ""
    if not row:
        return None
    cols = list(row)
    placeholders = ",".join(["?"] * len(cols))
    col_sql = ",".join([f'"{c}"' for c in cols])
    conn.execute(f'insert into "{table}" ({col_sql}) values ({placeholders})', [row[c] for c in cols])
    return int(conn.execute("select last_insert_rowid()").fetchone()[0])


def dstr(date_value: dt.date) -> str:
    return date_value.isoformat()


def tstamp(date_value: dt.date, hour: int = 9, minute: int = 0) -> str:
    return f"{date_value.isoformat()} {hour:02d}:{minute:02d}:00"


def add_days(date_value: dt.date, days: int) -> dt.date:
    return min(END_DATE, date_value + dt.timedelta(days=days))


def weighted_choice(rng: random.Random, items: list[tuple[str, int]]) -> str:
    total = sum(weight for _, weight in items)
    pick = rng.randint(1, total)
    acc = 0
    for value, weight in items:
        acc += weight
        if pick <= acc:
            return value
    return items[-1][0]


def random_date(rng: random.Random, index: int, total: int) -> dt.date:
    days = (END_DATE - START_DATE).days
    base = START_DATE + dt.timedelta(days=(index * days) // max(total - 1, 1))
    jitter = rng.randint(-2, 2)
    out = base + dt.timedelta(days=jitter)
    if out < START_DATE:
        return START_DATE
    if out > END_DATE:
        return END_DATE
    return out


def read_line_signal(path_text: str) -> dict[str, int]:
    if not path_text:
        return {}
    path = Path(path_text)
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="ignore")
    terms = {
        "repair": "\u7dad\u4fee",
        "install": "\u88dd\u6a5f",
        "billing": "\u67e5\u5e33",
        "return": "\u9000\u6a5f",
        "photo": "\u7167\u7247",
        "boss": "\u8001\u95c6",
        "reschedule": "\u6539\u7d04",
        "phone": "\u96fb\u806f",
    }
    return {key: text.count(value) for key, value in terms.items()}


def load_staff(conn: sqlite3.Connection) -> list[dict]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "select staff_code, display_name, department from employee_accounts "
        "where coalesce(staff_code, '') <> '' order by id"
    ).fetchall()
    staff = []
    for row in rows:
        staff.append(
            {
                "staff_code": row["staff_code"],
                "name": row["display_name"],
                "department": row["department"] or "",
            }
        )
    return staff


AREAS = [
    "\u5317\u5340",
    "\u6c38\u5eb7",
    "\u6771\u5340",
    "\u4e2d\u897f\u5340",
    "\u5b89\u5357",
    "\u5b89\u5e73",
]

BUILDING_NAMES = [
    "\u6210\u5927\u57ce",
    "\u6771\u6a4b\u771f\u611b",
    "\u9577\u69ae\u65b0\u57ce",
    "\u4eac\u57ce\u9cf3\u51f0",
    "\u6842\u82b1\u9109",
    "\u71b1\u5e36\u5dbc",
    "\u5927\u9053\u4e00\u5340",
    "\u5927\u9053\u4e8c\u5340",
    "\u5927\u9053\u4e09\u5340",
    "\u5927\u9053\u4e94\u5340",
    "\u5927\u9053\u5341\u5340",
    "\u958b\u5143\u5bf6",
    "\u4e16\u7d00\u4e4b\u9580",
    "\u6c38\u9f8d",
    "\u9577\u5104\u57ce",
    "\u65b0\u597d\u570b\u5b85",
    "\u6771\u65b9\u516c\u5712",
    "\u7fe1\u7fe0",
    "\u6676\u91c7",
    "\u5927\u6642\u4ee3",
    "\u6c34\u821e\u7d00",
    "\u5922\u516c\u5712",
    "\u5317\u5e9c\u82d1",
    "\u6625\u798f\u5b78\u5b78",
    "\u7da0\u6d77\u90fd\u5fc3",
    "\u6771\u8208",
    "\u5929\u95d5",
    "\u679c\u8cbf",
]

EAST_BUILDING_NAMES = [
    "\u516c\u5712\u9e97\u7dfb",
    "\u5104\u8f09\u91d1\u57ce",
    "\u5e1d\u5fc3",
    "\u5927\u5b78\u4e16\u754c",
    "\u6d77\u95b1",
    "\u5d07\u660e\u5c45",
    "Yes \u9060\u6771",
    "\u6771\u65b9\u516c\u5712",
    "\u5922\u516c\u5712",
    "\u4e16\u7d00\u4e4b\u9580",
    "\u6c34\u821e\u7d00",
    "\u6676\u91c7",
    "\u5927\u6642\u4ee3",
    "\u7da0\u6d77\u90fd\u5fc3",
    "\u6771\u8208",
    "\u6625\u798f\u5b78\u5b78",
]

ANPING_BUILDING_NAMES = [
    "\u90fd\u6703\u5047\u671f",
    "\u5357\u570b",
    "\u8377\u862d\u9996\u5e9c",
    "\u8377\u862d\u5bb6\u9109",
    "\u6d77\u95b1",
    "\u6c34\u821e\u7d00",
    "\u5922\u516c\u5712",
    "\u5317\u5e9c\u82d1",
    "\u5927\u6642\u4ee3",
    "\u6676\u91c7",
    "\u5e1d\u5bf6",
    "\u5e9c\u5e73\u516c\u5712",
]

NORTH_TAINAN_BUILDING_NAMES = [
    "\u7dad\u51a0\u9f8d\u6bbf",
    "\u6469\u6839 168",
    "\u4e2d\u83ef\u5317\u8def\u793e\u5340",
    "\u9577\u5104\u57ce",
    "\u65b0\u597d\u570b\u5b85",
    "\u958b\u5143\u5bf6",
    "\u9577\u69ae\u65b0\u57ce",
    "\u4eac\u57ce\u9cf3\u51f0",
    "\u5927\u9053\u4e00\u5340",
    "\u5927\u9053\u4e8c\u5340",
    "\u5927\u9053\u4e09\u5340",
    "\u4e16\u7d00\u4e4b\u9580",
]

YONGKANG_BUILDING_NAMES = [
    "\u6469\u6839 168",
    "\u967d\u5149\u83ef\u5ec8",
    "\u767d\u91d1\u6f22\u5bae",
    "\u51e1\u723e\u8cfd",
    "\u6c38\u9f8d",
    "\u6771\u6a4b\u771f\u611b",
    "\u9577\u5104\u57ce",
    "\u6842\u82b1\u9109",
    "\u71b1\u5e36\u5dbc",
    "\u6210\u5927\u57ce",
    "\u6771\u65b9\u516c\u5712",
    "\u6625\u798f\u5b78\u5b78",
]

REAL_BUILDING_ADDRESSES = {
    "\u516c\u5712\u9e97\u7dfb": "\u53f0\u5357\u5e02\u5317\u5340\u516c\u5712\u5317\u8def156\u865f",
    "\u90fd\u6703\u5047\u671f": "\u53f0\u5357\u5e02\u5b89\u5e73\u5340\u5065\u5eb7\u4e09\u8857592\u5df755\u865f",
    "\u5357\u570b": "\u53f0\u5357\u5e02\u5b89\u5e73\u5340\u90e1\u5e73\u8def188\u865f",
    "\u8377\u862d\u9996\u5e9c": "\u53f0\u5357\u5e02\u5b89\u5e73\u5340\u6c38\u83ef\u8def\u4e8c\u6bb5851\u865f",
    "\u6d77\u95b1": "\u53f0\u5357\u5e02\u5b89\u5e73\u5340\u90e1\u5e73\u8def52\u865f",
    "\u7dad\u51a0\u9f8d\u6bbf": "\u53f0\u5357\u5e02\u6c38\u5eb7\u5340\u6c38\u4e8c\u8857411\u865f",
    "\u6469\u6839 168": "\u53f0\u5357\u5e02\u6771\u5340\u4e2d\u83ef\u6771\u8def\u4e8c\u6bb5151\u865f",
    "\u6210\u5927\u57ce": "\u53f0\u5357\u5e02\u5317\u5340\u958b\u5143\u8def501\u865f",
    "\u6771\u6a4b\u771f\u611b": "\u53f0\u5357\u5e02\u6c38\u5eb7\u5340\u6771\u6a4b\u4e03\u8def191\u865f",
    "\u9577\u69ae\u65b0\u57ce": "\u53f0\u5357\u5e02\u5317\u5340\u9577\u69ae\u8def\u4e94\u6bb541\u5df746\u865f",
    "\u4eac\u57ce\u9cf3\u51f0": "\u53f0\u5357\u5e02\u6c38\u5eb7\u5340\u4e2d\u83ef\u8def7\u5df72\u865f",
    "\u6842\u82b1\u9109": "\u53f0\u5357\u5e02\u5317\u5340\u958b\u5143\u8def485\u5df741\u5f046\u865f",
    "\u71b1\u5e36\u5dbc": "\u53f0\u5357\u5e02\u6c38\u5eb7\u5340\u52dd\u5b78\u8def260\u5df72\u865f",
    "\u9577\u5104\u57ce": "\u53f0\u5357\u5e02\u6c38\u5eb7\u5340\u4e2d\u83ef\u8def725\u865f",
    "\u6c34\u821e\u7d00": "\u53f0\u5357\u5e02\u6c38\u5eb7\u5340\u6771\u6a4b\u4e94\u8def91\u865f",
    "\u967d\u5149\u83ef\u5ec8": "\u53f0\u5357\u5e02\u6c38\u5eb7\u5340\u5fa9\u83ef\u4e03\u885732\u5df723\u865f",
    "\u767d\u91d1\u6f22\u5bae": "\u53f0\u5357\u5e02\u6c38\u5eb7\u5340\u5fa9\u83ef\u4e09\u885762\u865f",
    "\u51e1\u723e\u8cfd": "\u53f0\u5357\u5e02\u6c38\u5eb7\u5340\u5fa9\u83ef\u4e09\u885790\u5df712\u865f",
}

CASE_WEIGHTS = [
    ("\u7dad\u4fee", 30),
    ("\u88dd\u6a5f", 22),
    ("\u9000\u6a5f", 10),
    ("\u62c6\u7dda", 5),
    ("TV \u7dad\u4fee", 10),
    ("\u67e5\u5e33", 5),
    ("\u6b20\u8cbb / \u9396 IP", 5),
    ("\u79fb\u6a5f", 2),
    ("\u66ab\u505c", 2),
    ("\u5fa9\u6a5f", 2),
    ("\u516c\u8a2d / \u7ba1\u7406\u5ba4", 5),
    ("\u5ba2\u8a34 / \u8001\u95c6\u5224\u65b7", 2),
]

DONE_STATUSES = ["\u5df2\u5b8c\u6210", "\u5df2\u5b8c\u5de5", "\u5b8c\u6210"]
OPEN_STATUSES = ["\u5f85\u8655\u7406", "\u8655\u7406\u4e2d", "\u5df2\u9818\u53d6", "\u5f85\u8001\u95c6\u5224\u65b7", "\u5f85\u4e3b\u7ba1\u5be9\u6838"]
WAIT_STATUSES = ["\u5f85\u6d3e\u5de5", "\u672a\u6d3e\u5de5", "\u5df2\u5efa\u7acb"]
RESULTS = [
    "\u5b89\u88dd\u5b8c\u6210",
    "\u6e2c\u901f\u6b63\u5e38",
    "\u66f4\u63db\u5c0f\u767d",
    "\u66f4\u63db\u5927\u767d",
    "\u66f4\u63db\u5206\u4eab\u5668",
    "\u7aef\u5b50\u677f\u63db port",
    "\u96fb\u4fe1\u7bb1\u8df3\u7dda\u91cd\u6253",
    "RJ11 \u982d\u4e0d\u826f\u5df2\u66f4\u63db",
    "\u96fb\u6e90\u7dda\u4e0d\u826f\u5df2\u66f4\u63db",
    "TV \u76d2\u91cd\u8a2d",
    "APP \u66f4\u65b0\u5b8c\u6210",
    "\u96fb\u8a71\u672a\u63a5",
    "\u5df2\u7559\u7c21\u8a0a",
    "\u6539\u7d04",
    "\u4f4f\u6236\u53d6\u6d88",
    "\u5df2\u9000\u6a5f",
    "\u5df2\u62c6\u7dda",
    "\u5df2\u6536\u55ae",
    "\u5df2\u5fa9\u6a5f",
    "\u5df2\u89e3\u9396",
    "\u5f85\u8001\u95c6\u5224\u65b7",
    "\u5f85\u5e33\u52d9\u78ba\u8a8d",
    "\u5f85\u4e3b\u7ba1\u5be9\u6838",
]


def make_phone(rng: random.Random, index: int) -> str:
    if index % 11 == 0:
        return f"06{rng.randint(2000000, 3999999)}"
    return "09" + f"{rng.randint(10000000, 99999999)}"


def make_address(building: dict, rng: random.Random) -> tuple[str, str, str]:
    floor = f"{rng.randint(2, 18)}F"
    room = f"{rng.randint(1, 8)}"
    if rng.random() < 0.35:
        room = f"{rng.choice(['A', 'B', 'C', 'D'])}\u68df{floor}-{room}"
    address = f"{building['name']} {floor}-{room}"
    return floor, room, address


def focus_area_name(area_focus: str) -> str:
    if area_focus == "east":
        return "\u6771\u5340"
    if area_focus == "north":
        return "\u5317\u5340"
    if area_focus == "anping":
        return "\u5b89\u5e73"
    if area_focus == "north_tainan":
        return "\u5317\u53f0\u5357"
    if area_focus == "yongkang":
        return "\u6c38\u5eb7"
    return ""


def delete_where(conn: sqlite3.Connection, table: str, where_sql: str, params: list | tuple) -> tuple[int, int]:
    cur = conn.cursor()
    before = cur.execute(f'select count(*) from "{table}"').fetchone()[0]
    cur.execute(f'delete from "{table}" where {where_sql}', params)
    after = cur.execute(f'select count(*) from "{table}"').fetchone()[0]
    return before, after


def clear_focus_tables(conn: sqlite3.Connection, sc: dict[str, dict], area_focus: str) -> dict[str, tuple[int, int]]:
    area = focus_area_name(area_focus)
    if not area:
        return {}
    cur = conn.cursor()
    ticket_ids = [
        str(r[0])
        for r in cur.execute("select id from tickets where dispatch_area=?", (area,)).fetchall()
    ] if "tickets" in sc else []
    ticket_nos = [
        str(r[0])
        for r in cur.execute("select ticket_no from tickets where dispatch_area=?", (area,)).fetchall()
    ] if "tickets" in sc else []
    customer_nos = [
        str(r[0])
        for r in cur.execute("select customer_no from customer_accounts where area=?", (area,)).fetchall()
    ] if "customer_accounts" in sc else []
    building_nos = [
        str(r[0])
        for r in cur.execute("select building_no from buildings where area=?", (area,)).fetchall()
    ] if "buildings" in sc else []
    result: dict[str, tuple[int, int]] = {}

    def placeholders(values: list[str]) -> str:
        return ",".join(["?"] * len(values))

    child_tables = ["ticket_install_details", "ticket_return_details"]
    for table in child_tables:
        if table in sc and ticket_ids:
            result[table] = delete_where(conn, table, f"cast(ticket_id as text) in ({placeholders(ticket_ids)})", ticket_ids)
    for table in ["ticket_customer_candidates", "dispatch_material_usage", "dispatch_repair_analysis"]:
        if table in sc and ticket_ids:
            values = ticket_ids + ticket_nos
            result[table] = delete_where(
                conn,
                table,
                f"cast(ticket_id as text) in ({placeholders(values)})",
                values,
            )
    if "manager_approval_requests" in sc:
        if ticket_ids:
            result["manager_approval_requests"] = delete_where(
                conn,
                "manager_approval_requests",
                f'area=? or (source_table=? and source_id in ({placeholders(ticket_ids)}))',
                [area, "tickets"] + ticket_ids,
            )
        else:
            result["manager_approval_requests"] = delete_where(conn, "manager_approval_requests", "area=?", [area])
    if "tickets" in sc:
        result["tickets"] = delete_where(conn, "tickets", "dispatch_area=?", [area])
    if "customer_service_items" in sc and customer_nos:
        result["customer_service_items"] = delete_where(
            conn,
            "customer_service_items",
            f"customer_no in ({placeholders(customer_nos)})",
            customer_nos,
        )
    if "customer_accounts" in sc:
        result["customer_accounts"] = delete_where(conn, "customer_accounts", "area=?", [area])
    if "sales_business_records" in sc and building_nos:
        result["sales_business_records"] = delete_where(
            conn,
            "sales_business_records",
            f"building_no in ({placeholders(building_nos)})",
            building_nos,
        )
    for table, column in [
        ("product_promotion_records", "target_area"),
        ("manager_contacts", "area"),
    ]:
        if table in sc and column in sc[table]["column_names"]:
            result[table] = delete_where(conn, table, f'"{column}"=?', [area])
    if "buildings" in sc:
        result["buildings"] = delete_where(conn, "buildings", "area=?", [area])
    return result


def clear_operation_tables(conn: sqlite3.Connection, sc: dict[str, dict], area_focus: str, clear_scope: str) -> dict[str, tuple[int, int]]:
    if clear_scope == "focus":
        return clear_focus_tables(conn, sc, area_focus)
    cur = conn.cursor()
    before_after = {}
    existing = [t for t in OPERATION_TABLE_ORDER if t in sc]
    extras = [t for t in sc if t not in PRESERVE_TABLES and t not in existing]
    clear_tables = existing + extras
    cur.execute("pragma foreign_keys=off")
    for table in clear_tables:
        before = cur.execute(f'select count(*) from "{table}"').fetchone()[0]
        cur.execute(f'delete from "{table}"')
        try:
            cur.execute("delete from sqlite_sequence where name=?", (table,))
        except sqlite3.OperationalError:
            pass
        after = cur.execute(f'select count(*) from "{table}"').fetchone()[0]
        before_after[table] = (before, after)
    cur.execute("pragma foreign_keys=on")
    return before_after


def seed_plans(conn: sqlite3.Connection, sc: dict[str, dict]) -> list[dict]:
    plans = [
        ("P100M", "100M/40M", 499, "100M", "40M", "\u4f4f\u5b85\u7db2\u8def"),
        ("P300M", "300M/100M", 699, "300M", "100M", "\u4f4f\u5b85\u7db2\u8def"),
        ("P500M", "500M/250M", 899, "500M", "250M", "\u9ad8\u901f\u7db2\u8def"),
        ("P1G", "1G/600M", 1299, "1G", "600M", "\u9ad8\u901f\u7db2\u8def"),
        ("TVBASIC", "TV \u57fa\u672c\u9910", 299, "TV", "TV", "\u6709\u7dda\u96fb\u8996"),
        ("NETTV", "\u7db2\u8def + TV", 798, "300M", "100M", "\u5957\u9910"),
    ]
    out = []
    for code, name, fee, down, up, cat in plans:
        insert_row(
            conn,
            sc,
            "billing_service_plans",
            {
                "plan_code": code,
                "plan_name": name,
                "monthly_fee": fee,
                "speed_down": down,
                "speed_up": up,
                "enabled": 1,
                "created_at": "2026-01-01 08:00:00",
                "updated_at": "2026-05-11 08:00:00",
                "plan_label": f"{name} / {fee}",
                "billing_category": cat,
            },
        )
        out.append({"code": code, "name": name, "fee": fee})
    return out


def area_for_focus(focus: str, idx: int, rng: random.Random) -> str:
    if focus == "east":
        return "\u6771\u5340"
    if focus == "north":
        return "\u5317\u5340"
    if focus == "anping":
        return "\u5b89\u5e73"
    if focus == "north_tainan":
        return "\u5317\u53f0\u5357"
    if focus == "yongkang":
        return "\u6c38\u5eb7"
    return AREAS[idx % len(AREAS)]


def building_names_for_focus(focus: str) -> list[str]:
    if focus == "east":
        return EAST_BUILDING_NAMES
    if focus == "anping":
        return ANPING_BUILDING_NAMES
    if focus == "north_tainan":
        return NORTH_TAINAN_BUILDING_NAMES
    if focus == "yongkang":
        return YONGKANG_BUILDING_NAMES
    return BUILDING_NAMES


def real_building_address(name: str) -> str:
    return REAL_BUILDING_ADDRESSES.get(name, "")


def seed_buildings(conn: sqlite3.Connection, sc: dict[str, dict], rng: random.Random, area_focus: str) -> list[dict]:
    buildings = []
    for idx, name in enumerate(building_names_for_focus(area_focus), start=1):
        area = area_for_focus(area_focus, idx, rng)
        building_no = f"B{idx:03d}"
        households = rng.randint(80, 520)
        active = int(households * rng.uniform(0.28, 0.76))
        address = real_building_address(name)
        row = {
            "building_no": building_no,
            "name": name,
            "area": area,
            "address": address,
            "raw_address": address,
            "display_address": address,
            "management_company": f"{name}\u7ba1\u7406\u59d4\u54e1\u6703",
            "management_phone": f"06{rng.randint(2000000, 3999999)}",
            "manager_name": rng.choice(["\u9673\u4e3b\u4efb", "\u6797\u7d44\u9577", "\u738b\u7e3d\u5e79\u4e8b", "\u9ec3\u79d8\u66f8"]),
            "manager_phone": make_phone(rng, idx),
            "active_users": active,
            "total_households": households,
            "ip": f"10.{idx}.{rng.randint(1, 254)}.1",
            "host": f"sw-b{idx:03d}",
            "note": rng.choice(["\u7ba1\u7406\u5ba4\u53ef\u4ee3\u6536\u55ae", "\u9700\u5148\u96fb\u806f\u7ba1\u59d4\u6703", "\u5730\u4e0b\u5ba4\u8a2d\u5099\u9593\u9700\u501f\u9470", "\u7dda\u8def\u6574\u7406\u4e2d"]),
            "created_at": tstamp(START_DATE, 8, 0),
            "updated_at": tstamp(END_DATE, 18, 0),
            "contract_status": rng.choice(["\u6709\u6548", "\u7e8c\u7d04\u4e2d", "\u5f85\u8b70\u50f9"]),
            "monthly_revenue": active * rng.choice([499, 699, 798, 899]),
            "building_type": rng.choice(["\u5927\u6a13", "\u793e\u5340", "\u570b\u5b85"]),
            "service_level": rng.choice(["A", "B", "C"]),
            "public_facility_status": rng.choice(["\u6b63\u5e38", "\u5f85\u7dda\u8def\u6574\u7406", "\u7ba1\u7406\u5ba4\u53cd\u61c9\u8a0a\u865f\u5f31"]),
            "manager_age": rng.choice(["30-39", "40-49", "50-59", "60+"]),
            "manager_experience": rng.choice(["1 \u5e74\u4ee5\u5167", "1-3 \u5e74", "3 \u5e74\u4ee5\u4e0a"]),
            "manager_interest": rng.choice(["\u7e8c\u7d04", "\u516c\u8a2d\u7dda\u8def", "TV \u670d\u52d9", "\u7db2\u8def\u5347\u7d1a"]),
            "visit_time": rng.choice(["09:00-12:00", "13:30-17:30", "\u9700\u9810\u7d04"]),
            "committee_time": rng.choice(["\u6bcf\u6708\u7b2c\u4e00\u9031", "\u6bcf\u6708\u7b2c\u4e09\u9031", "\u4e0d\u5b9a\u671f"]),
            "resident_meeting_time": rng.choice(["\u9031\u516d\u665a\u9593", "\u9031\u65e5\u4e0b\u5348", "\u5c1a\u672a\u5b89\u6392"]),
        }
        insert_row(conn, sc, "buildings", row)
        buildings.append({"building_no": building_no, "name": name, "area": area, "address": address})
    return buildings


def seed_customers(
    conn: sqlite3.Connection,
    sc: dict[str, dict],
    rng: random.Random,
    buildings: list[dict],
    plans: list[dict],
    target_count: int,
) -> list[dict]:
    customers = []
    for idx in range(1, target_count + 1):
        building = rng.choice(buildings)
        plan = rng.choice(plans)
        floor, room, service_address = make_address(building, rng)
        customer_no = f"C2026{idx:05d}"
        unknown = idx % 13 == 0
        cname = "" if unknown else rng.choice(["\u9673", "\u6797", "\u9ec3", "\u5f35", "\u738b", "\u674e", "\u5289"]) + rng.choice(["\u5148\u751f", "\u5c0f\u59d0", "\u592a\u592a"])
        service_status = weighted_choice(
            rng,
            [
                ("\u6b63\u5e38", 72),
                ("\u6b20\u8cbb", 9),
                ("\u9396 IP", 5),
                ("\u66ab\u505c", 5),
                ("\u9000\u79df", 4),
                ("\u5f85\u5fa9\u6a5f", 5),
            ],
        )
        overdue = 1 if service_status in {"\u6b20\u8cbb", "\u9396 IP"} else 0
        ip_limited = 1 if service_status == "\u9396 IP" else 0
        created = random_date(rng, idx, target_count)
        last_pay = max(START_DATE, created - dt.timedelta(days=rng.randint(0, 60)))
        row = {
            "customer_no": customer_no,
            "customer_name": cname,
            "building_no": building["building_no"],
            "area": building["area"],
            "address": service_address,
            "phone": make_phone(rng, idx),
            "service_status": service_status,
            "payment_status": "\u6b63\u5e38" if not overdue else "\u5f85\u7e73",
            "monthly_fee": plan["fee"],
            "is_overdue": overdue,
            "ip_limited": ip_limited,
            "created_at": tstamp(created, rng.randint(8, 20), rng.choice([0, 15, 30, 45])),
            "updated_at": tstamp(END_DATE, 18, 0),
            "install_date": dstr(created),
            "last_payment_date": dstr(last_pay),
            "arrears_months": rng.randint(1, 4) if overdue else 0,
            "plan_name": plan["name"],
            "router_model": rng.choice(["HG8245H", "AX1800", "Archer C6", "TV Box S", ""]),
            "customer_type": rng.choice(["\u4f4f\u6236", "\u79df\u5ba2", "\u7ba1\u7406\u5ba4", "\u516c\u8a2d"]),
            "customer_phone": make_phone(rng, idx + 700),
            "floor_text": floor,
            "room_no": room,
            "service_address": service_address,
            "service_type": rng.choice(["\u7db2\u8def", "TV", "\u7db2\u8def+TV"]),
            "package_name": plan["name"],
            "contract_status": "\u6709\u6548" if service_status not in {"\u9000\u79df"} else "\u7d42\u6b62",
            "account_status": service_status,
            "payment_method": rng.choice(["\u532f\u6b3e", "\u73fe\u91d1", "\u4fe1\u7528\u5361", "\u8f49\u5e33"]),
            "billing_day": rng.randint(1, 28),
            "arrears_status": "\u7121\u6b20\u8cbb" if not overdue else f"\u6b20 {rng.randint(1, 4)} \u671f",
            "equipment_no": f"EQ{idx:06d}",
            "cm_mac": "AA:BB:%02X:%02X:%02X:%02X" % (idx % 255, rng.randint(0, 254), rng.randint(0, 254), rng.randint(0, 254)),
            "ip_address": f"100.64.{idx % 240}.{rng.randint(2, 250)}",
            "signal_note": rng.choice(["RX -3.2 / TX 42", "RX -5.8 / TX 45", "\u4fe1\u865f\u6b63\u5e38", "\u9700\u8ffd\u8e64\u8a0a\u865f"]),
            "billing_note": "\u6b20\u8cbb\u5df2\u901a\u77e5" if overdue else "\u5e33\u52d9\u6b63\u5e38",
            "service_note": rng.choice(["\u9700\u5148\u96fb\u806f", "\u53ef\u76f4\u63a5\u5230\u7ba1\u7406\u5ba4", "\u591c\u9593\u4e0d\u4fbf\u65bd\u5de5", "\u6a23\u672c\u8cc7\u6599"]),
        }
        insert_row(conn, sc, "customer_accounts", row)
        customer = row.copy()
        customer["building_name"] = building["name"]
        customers.append(customer)
        for item_idx in range(1, rng.randint(1, 3) + 1):
            insert_row(
                conn,
                sc,
                "customer_service_items",
                {
                    "customer_no": customer_no,
                    "item_type": rng.choice(["Internet", "TV", "Router", "Public"]),
                    "item_status": "\u555f\u7528" if service_status not in {"\u9000\u79df"} else "\u505c\u7528",
                    "description": rng.choice(["\u4e3b\u7dda\u8def", "\u5206\u4eab\u5668", "TV \u76d2", "\u516c\u8a2d\u7dda"]),
                    "created_at": row["created_at"],
                    "plan_code": plan["code"],
                    "enabled": 1 if service_status not in {"\u9000\u79df"} else 0,
                    "updated_at": row["updated_at"],
                },
            )
    return customers


def ticket_status_for_date(rng: random.Random, case_date: dt.date) -> str:
    if case_date >= dt.date(2026, 5, 8):
        return weighted_choice(rng, [("\u8655\u7406\u4e2d", 30), ("\u5df2\u9818\u53d6", 25), ("\u5f85\u8655\u7406", 20), ("\u5f85\u8001\u95c6\u5224\u65b7", 15), ("\u5df2\u5b8c\u6210", 10)])
    if case_date >= dt.date(2026, 5, 1):
        return weighted_choice(rng, [("\u5df2\u5b8c\u6210", 55), ("\u8655\u7406\u4e2d", 18), ("\u5df2\u9818\u53d6", 12), ("\u5f85\u8655\u7406", 10), ("\u5f85\u8001\u95c6\u5224\u65b7", 5)])
    return weighted_choice(rng, [("\u5df2\u5b8c\u6210", 78), ("\u5df2\u5b8c\u5de5", 9), ("\u4f4f\u6236\u53d6\u6d88", 4), ("\u9000\u56de", 3), ("\u8655\u7406\u4e2d", 3), ("\u5f85\u8655\u7406", 3)])


def is_done_status(status: str) -> bool:
    return status in DONE_STATUSES or status in {"\u4f4f\u6236\u53d6\u6d88", "\u9000\u56de"}


def case_description(case_type: str, customer: dict, rng: random.Random) -> str:
    fragments = {
        "\u7dad\u4fee": ["wifi \u8a0a\u865f\u4e0d\u7a69", "\u7db2\u8def\u65b7\u7dda", "\u901f\u5ea6\u504f\u6162", "\u96fb\u8a71\u672a\u63a5\u5df2\u7559\u8a0a"],
        "\u88dd\u6a5f": ["\u65b0\u88dd\u6a5f\u7d04\u65bd\u5de5", "\u9700\u6536\u62bc\u91d1\u8207\u9996\u671f", "\u88dd\u6a5f\u5f8c\u9700\u6e2c\u901f"],
        "\u9000\u6a5f": ["\u9000\u79df\u9000\u6a5f", "\u8a2d\u5099\u7e73\u56de\u8207\u7d50\u7b97", "\u9700\u62c6\u7dda\u6536\u55ae"],
        "\u62c6\u7dda": ["\u6b20\u8cbb\u62c6\u7dda", "\u9000\u6a5f\u5f8c\u62c6\u7dda", "\u7ba1\u7406\u5ba4\u4ee3\u6536\u55ae"],
        "TV \u7dad\u4fee": ["TV \u76d2\u7121\u6cd5\u770b", "APP \u9700\u66f4\u65b0", "\u96fb\u8996\u8a0a\u865f\u4e0d\u826f"],
        "\u67e5\u5e33": ["\u67e5\u5e33\u8207\u5230\u671f\u65e5", "\u5ba2\u6236\u8a62\u554f\u6536\u8cbb", "\u5e33\u52d9\u78ba\u8a8d"],
        "\u6b20\u8cbb / \u9396 IP": ["\u6b20\u8cbb\u901a\u77e5", "\u9396 IP \u5f8c\u5ba2\u6236\u4f86\u96fb", "\u6536\u6b3e\u5f8c\u89e3\u9396"],
        "\u79fb\u6a5f": ["\u540c\u793e\u5340\u79fb\u6a5f", "\u642c\u5bb6\u6539\u88dd", "\u9700\u91cd\u62c9\u7dda"],
        "\u66ab\u505c": ["\u4f4f\u6236\u7533\u8acb\u66ab\u505c", "\u5e33\u52d9\u8a2d\u5b9a\u66ab\u505c", "\u9700\u78ba\u8a8d\u5fa9\u6a5f\u65e5"],
        "\u5fa9\u6a5f": ["\u6536\u6b3e\u5f8c\u5fa9\u6a5f", "\u66ab\u505c\u5fa9\u6a5f", "\u9700\u89e3\u9396 IP"],
        "\u516c\u8a2d / \u7ba1\u7406\u5ba4": ["\u7ba1\u7406\u5ba4\u53cd\u61c9\u516c\u8a2d\u7dda", "\u505c\u8eca\u5834\u8a0a\u865f\u5f31", "\u7cfb\u7d71\u7dda\u8def\u6574\u7406"],
        "\u5ba2\u8a34 / \u8001\u95c6\u5224\u65b7": ["\u5ba2\u8a34\u9700\u8001\u95c6\u5224\u65b7", "\u8cbb\u7528\u722d\u8b70", "\u591a\u6b21\u5831\u4fee\u8ffd\u8e64"],
    }
    base = rng.choice(fragments.get(case_type, ["\u6a23\u672c\u6d3e\u5de5\u4e8b\u4ef6"]))
    return f"{base} / {customer['service_address']} / {customer['phone']}"


def seed_tickets(
    conn: sqlite3.Connection,
    sc: dict[str, dict],
    rng: random.Random,
    customers: list[dict],
    staff: list[dict],
    target_count: int,
) -> list[dict]:
    tickets = []
    engineer_pool = [s for s in staff if any(k in s["department"] for k in ["\u5de5", "\u7dad", "\u5ba2"])] or staff
    for idx in range(1, target_count + 1):
        case_date = random_date(rng, idx, target_count)
        case_type = weighted_choice(rng, CASE_WEIGHTS)
        status = ticket_status_for_date(rng, case_date)
        customer = rng.choice(customers)
        public_case = case_type == "\u516c\u8a2d / \u7ba1\u7406\u5ba4" or customer["customer_type"] in {"\u7ba1\u7406\u5ba4", "\u516c\u8a2d"}
        staff_row = rng.choice(engineer_pool)
        assigned = status not in WAIT_STATUSES and rng.random() > 0.04
        done = is_done_status(status)
        arrive_hour = rng.randint(9, 17)
        completed_at = ""
        finished_at = ""
        completion_note = ""
        if done and status not in {"\u4f4f\u6236\u53d6\u6d88", "\u9000\u56de"}:
            finish_date = add_days(case_date, rng.choice([0, 0, 0, 1, 2]))
            completed_at = tstamp(finish_date, min(arrive_hour + rng.randint(1, 3), 20), rng.choice([0, 15, 30, 45]))
            finished_at = completed_at
            completion_note = rng.choice(RESULTS)
        elif status in {"\u4f4f\u6236\u53d6\u6d88", "\u9000\u56de"}:
            completion_note = status
        has_photo = done and rng.random() < 0.48
        ticket_no = f"T2026{idx:06d}"
        repair_category = rng.choice(["\u7db2\u8def", "TV", "\u5e33\u52d9", "\u7dda\u8def", "\u8a2d\u5099"])
        repair_reason = rng.choice(["\u8a0a\u865f\u4e0d\u7a69", "\u8a2d\u5099\u6545\u969c", "\u5ba2\u6236\u6539\u7d04", "\u5e33\u52d9\u72c0\u614b", "\u516c\u8a2d\u7dda\u8def"])
        material_json = json.dumps(
            [{"name": rng.choice(["RJ11", "F \u982d", "\u7db2\u8def\u7dda", "\u5206\u4eab\u5668", "TV Box"]), "qty": rng.randint(1, 3)}],
            ensure_ascii=False,
        )
        photo_path = f"/demo/attachments/2026/{case_date.strftime('%m')}/{ticket_no}.jpg" if has_photo else ""
        cust_name = customer["customer_name"] or "\u7121\u59d3\u540d\u5ba2\u6236"
        row = {
            "ticket_no": ticket_no,
            "dispatch_area": customer["area"],
            "case_type": case_type,
            "status": status,
            "customer_name": cust_name,
            "contact_name": cust_name if not public_case else "\u7ba1\u7406\u5ba4",
            "contact_phone": customer["phone"],
            "service_address": customer["service_address"],
            "appointment_date": dstr(case_date),
            "appointment_time": rng.choice(["09:00-12:00", "13:30-15:30", "15:30-18:00", "\u5148\u96fb\u806f"]),
            "assigned_engineer": staff_row["name"] if assigned else "",
            "assigned_engineer_staff_code": staff_row["staff_code"] if assigned else "",
            "customer_no": customer["customer_no"],
            "building_no": customer["building_no"],
            "description": case_description(case_type, customer, rng),
            "internal_note": rng.choice(["LINE \u6a23\u672c\u8f49\u55ae", "\u9700\u5148\u96fb\u806f", "\u7ba1\u7406\u5ba4\u53ef\u5354\u52a9", "\u5ba2\u6236\u8981\u6c42\u6539\u7d04"]),
            "completion_note": completion_note,
            "finance_sync_status": "\u5df2\u540c\u6b65" if done else "\u5f85\u540c\u6b65",
            "external_finance_id": f"FIN{idx:06d}" if case_type in {"\u88dd\u6a5f", "\u9000\u6a5f", "\u67e5\u5e33", "\u6b20\u8cbb / \u9396 IP"} else "",
            "finance_note": "\u5f85\u5e33\u52d9\u78ba\u8a8d" if case_type in {"\u67e5\u5e33", "\u6b20\u8cbb / \u9396 IP"} and not done else "\u5e33\u52d9\u6b63\u5e38",
            "extra_fees_data": json.dumps({"other_fee": rng.choice([0, 100, 300, 500]), "source": "demo"}, ensure_ascii=False),
            "customer_signature_data": f"/demo/signatures/{ticket_no}.png" if done and rng.random() < 0.55 else "",
            "customer_signature_signed_at": completed_at if done and rng.random() < 0.55 else "",
            "created_at": tstamp(case_date, rng.randint(8, 18), rng.choice([0, 15, 30, 45])),
            "arrived_at": tstamp(case_date, arrive_hour, rng.choice([0, 15, 30, 45])) if assigned and status not in WAIT_STATUSES else "",
            "completed_at": completed_at,
            "repair_category": repair_category,
            "repair_reason": repair_reason,
            "is_public_facility": 1 if public_case else 0,
            "is_non_general_repair": 1 if case_type in {"\u5ba2\u8a34 / \u8001\u95c6\u5224\u65b7", "\u516c\u8a2d / \u7ba1\u7406\u5ba4"} else 0,
            "material_usage_json": material_json,
            "speedtest_photo_data": photo_path if has_photo and case_type in {"\u88dd\u6a5f", "\u7dad\u4fee"} else "",
            "before_photos_data": photo_path.replace(".jpg", "_before.jpg") if has_photo else "",
            "after_photos_data": photo_path.replace(".jpg", "_after.jpg") if has_photo else "",
            "finished_by_staff_code": staff_row["staff_code"] if done and assigned else "",
            "finished_by_name": staff_row["name"] if done and assigned else "",
            "finished_at": finished_at,
            "source_channel": "LINE",
            "call_attempts": rng.randint(0, 3),
            "voice_message_left": 1 if rng.random() < 0.18 else 0,
            "same_day_confirmed": 1 if rng.random() < 0.72 else 0,
            "customer_valid_checked": 1,
            "billing_checked": 1 if case_type in {"\u67e5\u5e33", "\u6b20\u8cbb / \u9396 IP", "\u88dd\u6a5f", "\u9000\u6a5f"} else rng.randint(0, 1),
            "oral_troubleshooting_done": 1 if case_type in {"\u7dad\u4fee", "TV \u7dad\u4fee"} else 0,
            "boss_review_required": 1 if case_type == "\u5ba2\u8a34 / \u8001\u95c6\u5224\u65b7" or status == "\u5f85\u8001\u95c6\u5224\u65b7" else 0,
        }
        ticket_id = insert_row(conn, sc, "tickets", row)
        ticket = row.copy()
        ticket["id"] = ticket_id
        ticket["staff"] = staff_row
        tickets.append(ticket)
        seed_ticket_children(conn, sc, rng, ticket)
    return tickets


def seed_ticket_children(conn: sqlite3.Connection, sc: dict[str, dict], rng: random.Random, ticket: dict) -> None:
    case_type = ticket["case_type"]
    ticket_id = ticket["id"]
    if ticket_id is None:
        return
    staff = ticket["staff"]
    if case_type in {"\u7dad\u4fee", "TV \u7dad\u4fee", "\u516c\u8a2d / \u7ba1\u7406\u5ba4", "\u5ba2\u8a34 / \u8001\u95c6\u5224\u65b7"}:
        insert_row(
            conn,
            sc,
            "dispatch_repair_analysis",
            {
                "ticket_id": str(ticket_id),
                "staff_code": staff["staff_code"],
                "staff_name": staff["name"],
                "area": ticket["dispatch_area"],
                "building_no": ticket["building_no"],
                "repair_category": ticket["repair_category"],
                "repair_reason": ticket["repair_reason"],
                "is_repeat_repair": 1 if rng.random() < 0.12 else 0,
                "is_public_facility": ticket["is_public_facility"],
                "is_non_general_repair": ticket["is_non_general_repair"],
                "created_at": ticket["created_at"],
            },
        )
    if case_type in {"\u88dd\u6a5f"}:
        monthly = rng.choice([499, 699, 798, 899])
        deposit = rng.choice([1000, 1500, 2000])
        construction = rng.choice([0, 500, 800])
        month_count = rng.choice([1, 3, 6])
        total = deposit + construction + monthly * month_count
        insert_row(
            conn,
            sc,
            "ticket_install_details",
            {
                "ticket_id": ticket_id,
                "deposit_amount": deposit,
                "construction_fee": construction,
                "monthly_fee": monthly,
                "monthly_fee_1": monthly,
                "monthly_fee_2": monthly if month_count >= 2 else 0,
                "monthly_fee_3": monthly if month_count >= 3 else 0,
                "month_count": month_count,
                "other_fee": rng.choice([0, 100, 300]),
                "other_fee_1": 0,
                "other_fee_2": 0,
                "other_fee_note": "\u88dd\u6a5f\u96f6\u4ef6",
                "material_name": rng.choice(["\u5206\u4eab\u5668", "TV Box", "ONU"]),
                "material_quantity": 1,
                "usage_start_date": ticket["appointment_date"],
                "usage_end_date": dstr(add_days(dt.date.fromisoformat(ticket["appointment_date"]), 90)),
                "usage_month_count": month_count,
                "rent_subtotal": monthly * month_count,
                "total_amount": total,
            },
        )
    if case_type in {"\u9000\u6a5f", "\u62c6\u7dda"}:
        deposit = rng.choice([1000, 1500, 2000])
        deduction = rng.choice([0, 100, 300, 500])
        refund = max(0, deposit - deduction)
        insert_row(
            conn,
            sc,
            "ticket_return_details",
            {
                "ticket_id": ticket_id,
                "payment_record": "\u9000\u6a5f\u7d50\u7b97\u6a23\u672c",
                "deposit_amount": deposit,
                "refund_amount": refund,
                "deduction_amount": deduction,
                "device_fee": rng.choice([0, 300, 500]),
                "cleaning_fee": rng.choice([0, 100]),
                "other_fee": rng.choice([0, 100]),
                "other_fee_note": "\u8a2d\u5099\u6aa2\u67e5",
                "total_amount": refund,
                "returned_device_status": rng.choice(["\u6b63\u5e38", "\u7f3a\u96fb\u6e90\u7dda", "\u5916\u89c0\u78e8\u640d"]),
                "return_note": "\u5df2\u6536\u8a2d\u5099" if ticket["completed_at"] else "\u5f85\u6536\u8a2d\u5099",
                "settlement_note": "\u5f85\u5e33\u52d9\u78ba\u8a8d" if not ticket["completed_at"] else "\u5df2\u7d50\u7b97",
            },
        )
    if rng.random() < 0.62:
        insert_row(
            conn,
            sc,
            "dispatch_material_usage",
            {
                "ticket_id": str(ticket_id),
                "staff_code": staff["staff_code"],
                "staff_name": staff["name"],
                "area": ticket["dispatch_area"],
                "building_no": ticket["building_no"],
                "material_name": rng.choice(["RJ11", "F \u982d", "\u7db2\u8def\u7dda", "\u5206\u4eab\u5668", "\u5927\u767d", "\u5c0f\u767d", "TV Box"]),
                "material_qty": rng.choice([1, 1, 1, 2, 3, 5, 10]),
                "material_unit": rng.choice(["pcs", "m", "\u500b"]),
                "material_unit_cost": rng.choice([5, 10, 25, 80, 300, 900]),
                "used_at": ticket["completed_at"] or ticket["created_at"],
            },
        )
    if rng.random() < 0.25:
        insert_row(
            conn,
            sc,
            "ticket_customer_candidates",
            {
                "ticket_id": ticket_id,
                "ticket_no": ticket["ticket_no"],
                "customer_name": ticket["customer_name"],
                "contact_phone": ticket["contact_phone"],
                "service_address": ticket["service_address"],
                "candidate_customer_no": ticket["customer_no"],
                "candidate_building_no": ticket["building_no"],
                "match_type": rng.choice(["phone", "address", "building_room"]),
                "match_score": rng.randint(70, 100),
                "review_status": rng.choice(["\u5f85\u4eba\u5de5\u78ba\u8a8d", "\u5df2\u78ba\u8a8d", "\u9700\u88dc\u8cc7\u6599"]),
                "review_note": "\u6a23\u672c\u5019\u9078\u5ba2\u6236",
                "created_at": ticket["created_at"],
                "updated_at": ticket["created_at"],
            },
        )
    if ticket["boss_review_required"] or rng.random() < 0.13:
        insert_row(
            conn,
            sc,
            "manager_approval_requests",
            {
                "request_type": rng.choice(["dispatch", "billing", "complaint", "return"]),
                "request_group": "demo_ops",
                "source_table": "tickets",
                "source_id": str(ticket_id),
                "requester_staff_code": staff["staff_code"],
                "requester_name": staff["name"],
                "department": staff["department"],
                "area": ticket["dispatch_area"],
                "title": f"{ticket['case_type']} / {ticket['service_address']}",
                "detail": ticket["description"],
                "risk_level": rng.choice(["A", "B", "C"]),
                "status": rng.choice(["pending", "approved", "returned", "completed"]),
                "manager_status": rng.choice(["pending", "approved", "returned"]),
                "boss_status": rng.choice(["pending", "approved", "need_review", ""]),
                "created_at": ticket["created_at"],
                "updated_at": ticket["completed_at"] or ticket["created_at"],
            },
        )


def seed_extra_ops(conn: sqlite3.Connection, sc: dict[str, dict], rng: random.Random, buildings: list[dict], staff: list[dict], area_focus: str) -> None:
    for idx in range(1, 181):
        b = rng.choice(buildings)
        created = random_date(rng, idx, 180)
        owner = rng.choice(staff)
        insert_row(
            conn,
            sc,
            "sales_business_records",
            {
                "building_no": b["building_no"],
                "business_type": rng.choice(["\u7e8c\u7d04", "\u65b0\u793e\u5340", "\u8cbb\u7387\u8abf\u6574", "\u516c\u8a2d\u7dda"]),
                "status": rng.choice(["\u8ffd\u8e64\u4e2d", "\u5df2\u5b8c\u6210", "\u5f85\u56de\u8986"]),
                "contract_status": rng.choice(["\u6709\u6548", "\u5f85\u7e8c\u7d04", "\u8b70\u7d04\u4e2d"]),
                "contract_end_date": dstr(add_days(created, rng.randint(30, 180))),
                "feedback_type": rng.choice(["\u7ba1\u59d4\u6703", "\u4f4f\u6236", "\u7ba1\u7406\u5ba4"]),
                "feedback_status": rng.choice(["\u5f85\u8655\u7406", "\u5df2\u8655\u7406", "\u8ffd\u8e64"]),
                "event_type": rng.choice(["\u62dc\u8a2a", "\u5831\u50f9", "\u8aaa\u660e\u6703"]),
                "event_status": rng.choice(["\u5df2\u5b89\u6392", "\u5df2\u5b8c\u6210", "\u6539\u671f"]),
                "event_schedule_date": dstr(created),
                "important_schedule": 1 if rng.random() < 0.22 else 0,
                "next_visit": dstr(add_days(created, rng.randint(7, 30))),
                "owner": owner["name"],
                "business_note": "\u793e\u5340\u71df\u904b\u6a23\u672c",
                "demo_type": "2026_ops",
                "created_at": tstamp(created, 10, 0),
                "updated_at": tstamp(add_days(created, rng.randint(0, 12)), 16, 0),
            },
        )
    for idx in range(1, 121):
        staff_row = rng.choice(staff)
        created = random_date(rng, idx, 120)
        insert_row(
            conn,
            sc,
            "purchase_requests",
            {
                "request_no": f"PR2026{idx:04d}",
                "requester_staff_code": staff_row["staff_code"],
                "department": staff_row["department"],
                "item_name": rng.choice(["\u7db2\u8def\u7dda", "RJ11", "\u5206\u4eab\u5668", "\u5c0f\u767d", "\u5927\u767d", "TV Box"]),
                "qty": rng.choice([10, 20, 30, 50, 100]),
                "unit": rng.choice(["pcs", "m", "\u500b"]),
                "estimated_amount": rng.choice([500, 1200, 3500, 8000, 16000]),
                "vendor_name": rng.choice(["DemoNet", "CablePro", "Xunnan Supplier"]),
                "status": rng.choice(["\u5f85\u5be9", "\u5df2\u6838\u51c6", "\u5df2\u63a1\u8cfc", "\u9000\u56de"]),
                "boss_status": rng.choice(["pending", "approved", "returned", ""]),
                "created_at": tstamp(created, 11, 0),
            },
        )
    for idx in range(1, 61):
        owner = rng.choice(staff)
        created = random_date(rng, idx, 60)
        insert_row(
            conn,
            sc,
            "product_promotion_records",
            {
                "campaign_no": f"CP2026{idx:04d}",
                "campaign_name": rng.choice(["\u6625\u5b63\u5347\u901f", "TV \u52a0\u8cfc", "\u793e\u5340\u63a8\u5ee3", "\u7e8c\u7d04\u512a\u60e0"]),
                "owner_staff_code": owner["staff_code"],
                "target_area": area_for_focus(area_focus, idx, rng),
                "budget": rng.choice([5000, 10000, 20000, 50000]),
                "leads": rng.randint(5, 120),
                "conversions": rng.randint(0, 45),
                "status": rng.choice(["\u9032\u884c\u4e2d", "\u5df2\u5b8c\u6210", "\u5f85\u555f\u52d5"]),
                "created_at": tstamp(created, 9, 0),
            },
        )
    for idx in range(1, 41):
        owner = rng.choice(staff)
        created = random_date(rng, idx, 40)
        insert_row(
            conn,
            sc,
            "project_records",
            {
                "project_no": f"PJ2026{idx:04d}",
                "project_name": rng.choice(["\u7dda\u8def\u6574\u7406", "\u7cfb\u7d71\u6574\u7406", "\u516c\u8a2d\u6539\u5584", "\u8a2d\u5099\u6c70\u63db"]),
                "project_type": rng.choice(["ops", "network", "billing", "building"]),
                "owner_staff_code": owner["staff_code"],
                "status": rng.choice(["\u9032\u884c\u4e2d", "\u5df2\u5b8c\u6210", "\u5ef6\u671f"]),
                "budget": rng.choice([10000, 30000, 80000, 150000]),
                "progress": rng.randint(10, 100),
                "start_date": dstr(created),
                "due_date": dstr(add_days(created, rng.randint(14, 90))),
                "created_at": tstamp(created, 8, 30),
            },
        )


def audit_lines(conn: sqlite3.Connection, sc: dict[str, dict], clear_result: dict, line_signal: dict) -> list[str]:
    lines = []
    cur = conn.cursor()
    lines.append("Demo 2026 seed sanity report")
    lines.append(f"period: {START_DATE.isoformat()} to {END_DATE.isoformat()}")
    lines.append("")
    lines.append("line_sample_signal:")
    for key in sorted(line_signal):
        lines.append(f"  {key}: {line_signal[key]}")
    lines.append("")
    lines.append("cleared_tables:")
    for table, (before, after) in sorted(clear_result.items()):
        lines.append(f"  {table}: {before} -> {after}")
    lines.append("")
    lines.append("table_counts:")
    for table in sorted(sc):
        count = cur.execute(f'select count(*) from "{table}"').fetchone()[0]
        lines.append(f"  {table}: {count}")
    lines.append("")
    for table in sorted(sc):
        count = cur.execute(f'select count(*) from "{table}"').fetchone()[0]
        if count == 0:
            continue
        missing = []
        for col in sc[table]["columns"]:
            name = col["name"]
            typ = col["type"].upper()
            qname = '"' + name.replace('"', '""') + '"'
            sql = f'select count(*) from "{table}" where {qname} is null'
            if "TEXT" in typ or "CHAR" in typ or "VARCHAR" in typ:
                sql += f" or trim(cast({qname} as text))=''"
            miss = cur.execute(sql).fetchone()[0]
            if miss:
                missing.append((name, miss, count))
        lines.append(f"null_or_blank_check.{table}:")
        if not missing:
            lines.append("  ok")
        else:
            for name, miss, total in missing[:30]:
                lines.append(f"  {name}: {miss}/{total}")
            if len(missing) > 30:
                lines.append(f"  ... +{len(missing)-30} more")
    if "tickets" in sc:
        lines.append("")
        lines.append("tickets.status_distribution:")
        for status, cnt in cur.execute('select status, count(*) from tickets group by status order by count(*) desc').fetchall():
            lines.append(f"  {status}: {cnt}")
        lines.append("tickets.case_type_distribution:")
        for case_type, cnt in cur.execute('select case_type, count(*) from tickets group by case_type order by count(*) desc').fetchall():
            lines.append(f"  {case_type}: {cnt}")
        row = cur.execute("select min(appointment_date), max(appointment_date), min(created_at), max(created_at) from tickets").fetchone()
        lines.append(f"tickets.date_range: appointment={row[0]}..{row[1]} created={row[2]}..{row[3]}")
        bad_done = cur.execute(
            "select count(*) from tickets where status in (?, ?, ?) and coalesce(completed_at, '')=''",
            tuple(DONE_STATUSES),
        ).fetchone()[0]
        bad_open = cur.execute(
            "select count(*) from tickets where status in (?, ?, ?, ?, ?) and coalesce(completed_at, '')<>''",
            tuple(OPEN_STATUSES),
        ).fetchone()[0]
        lines.append(f"tickets.done_without_completed_at: {bad_done}")
        lines.append(f"tickets.open_with_completed_at: {bad_open}")
        photo_count = cur.execute(
            "select count(*) from tickets where coalesce(speedtest_photo_data,'')<>'' "
            "or coalesce(before_photos_data,'')<>'' or coalesce(after_photos_data,'')<>''"
        ).fetchone()[0]
        lines.append(f"tickets.photo_placeholder_count: {photo_count}")
    return lines


def main() -> None:
    args = parse_args()
    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"db not found: {db_path}")
    backup = db_path.with_name(f"{db_path.stem}.before_demo_2026_ops_{now_stamp()}{db_path.suffix}")
    shutil.copy2(db_path, backup)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("pragma foreign_keys=on")
        sc = schema(conn)
        staff = load_staff(conn)
        if not staff:
            raise SystemExit("no staff rows found; aborting to avoid creating fake staff")
        rng = random.Random(RANDOM_SEED)
        line_signal = read_line_signal(args.line_sample)
        clear_result = clear_operation_tables(conn, sc, args.area_focus, args.clear_scope)
        plans = seed_plans(conn, sc)
        buildings = seed_buildings(conn, sc, rng, args.area_focus)
        customers = seed_customers(conn, sc, rng, buildings, plans, args.customers)
        seed_tickets(conn, sc, rng, customers, staff, args.tickets)
        seed_extra_ops(conn, sc, rng, buildings, staff, args.area_focus)
        conn.commit()
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines = audit_lines(conn, sc, clear_result, line_signal)
        lines.insert(1, f"backup: {backup}")
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"backup={backup}")
        print(f"report={report_path}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
