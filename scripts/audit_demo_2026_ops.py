#!/usr/bin/env python3
"""Audit the 2026 demo operation data in the SQLite DB.

The source code in this file is intentionally ASCII-only.
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


START_DATE = "2026-01-01"
END_DATE = "2026-05-11"
DONE_STATUSES = ["\u5df2\u5b8c\u6210", "\u5df2\u5b8c\u5de5", "\u5b8c\u6210"]
OPEN_STATUSES = ["\u5f85\u8655\u7406", "\u8655\u7406\u4e2d", "\u5df2\u9818\u53d6", "\u5f85\u8001\u95c6\u5224\u65b7", "\u5f85\u4e3b\u7ba1\u5be9\u6838"]
SEEDED_TABLES = [
    "billing_service_plans",
    "buildings",
    "customer_accounts",
    "customer_service_items",
    "tickets",
    "ticket_install_details",
    "ticket_return_details",
    "dispatch_repair_analysis",
    "dispatch_material_usage",
    "ticket_customer_candidates",
    "manager_approval_requests",
    "sales_business_records",
    "purchase_requests",
    "product_promotion_records",
    "project_records",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="xunnan_dispatch.db")
    parser.add_argument("--report", default="reports/demo_2026_seed_audit.txt")
    return parser.parse_args()


def schema(conn: sqlite3.Connection) -> dict[str, dict]:
    cur = conn.cursor()
    tables = [
        r[0]
        for r in cur.execute(
            "select name from sqlite_master "
            "where type='table' and name not like 'sqlite_%' order by name"
        ).fetchall()
    ]
    out = {}
    for table in tables:
        cols = cur.execute(f'pragma table_info("{table}")').fetchall()
        out[table] = {
            "columns": [
                {
                    "name": c[1],
                    "type": c[2] or "",
                    "notnull": bool(c[3]),
                    "default": c[4],
                    "pk": c[5],
                }
                for c in cols
            ]
        }
    return out


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f'select count(*) from "{table}"').fetchone()[0])


def append_null_checks(lines: list[str], conn: sqlite3.Connection, sc: dict[str, dict]) -> None:
    for table in sorted(sc):
        total = table_count(conn, table)
        if total == 0:
            lines.append(f"null_or_blank_check.{table}: skipped-empty")
            continue
        missing = []
        for col in sc[table]["columns"]:
            name = col["name"]
            typ = col["type"].upper()
            qname = '"' + name.replace('"', '""') + '"'
            sql = f'select count(*) from "{table}" where {qname} is null'
            if "TEXT" in typ or "CHAR" in typ or "VARCHAR" in typ:
                sql += f" or trim(cast({qname} as text))=''"
            count = int(conn.execute(sql).fetchone()[0])
            if count:
                missing.append((name, count, total))
        lines.append(f"null_or_blank_check.{table}:")
        if not missing:
            lines.append("  ok")
        else:
            for name, count, total in missing[:40]:
                lines.append(f"  {name}: {count}/{total}")
            if len(missing) > 40:
                lines.append(f"  ... +{len(missing) - 40} more")


def append_distribution(lines: list[str], conn: sqlite3.Connection, table: str, column: str) -> None:
    try:
        rows = conn.execute(
            f'select "{column}", count(*) from "{table}" group by "{column}" order by count(*) desc'
        ).fetchall()
    except sqlite3.OperationalError:
        return
    lines.append(f"{table}.{column}_distribution:")
    for value, count in rows:
        lines.append(f"  {value}: {count}")


def append_mapping(lines: list[str], sc: dict[str, dict]) -> None:
    lines.append("seeded_table_column_mapping:")
    for table in SEEDED_TABLES:
        if table not in sc:
            continue
        cols = [c["name"] for c in sc[table]["columns"] if not (c["pk"] and "INT" in c["type"].upper())]
        lines.append(f"  {table}: {', '.join(cols)}")


def latest_backup(db_path: Path) -> str:
    pattern = f"{db_path.stem}.before_demo_2026_ops_*{db_path.suffix}"
    found = sorted(db_path.parent.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return str(found[0]) if found else ""


def main() -> None:
    args = parse_args()
    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"db not found: {db_path}")
    conn = sqlite3.connect(db_path)
    try:
        sc = schema(conn)
        lines = []
        lines.append("Demo 2026 operation audit")
        lines.append(f"db: {db_path}")
        backup = latest_backup(db_path)
        if backup:
            lines.append(f"latest_backup: {backup}")
        lines.append(f"period_expected: {START_DATE} to {END_DATE}")
        lines.append("")
        append_mapping(lines, sc)
        lines.append("")
        lines.append("integrity_check:")
        lines.append(f"  {conn.execute('pragma integrity_check').fetchone()[0]}")
        lines.append("")
        lines.append("table_counts:")
        for table in sorted(sc):
            lines.append(f"  {table}: {table_count(conn, table)}")
        lines.append("")
        append_null_checks(lines, conn, sc)
        if "tickets" in sc:
            lines.append("")
            append_distribution(lines, conn, "tickets", "status")
            append_distribution(lines, conn, "tickets", "case_type")
            row = conn.execute(
                "select min(appointment_date), max(appointment_date), min(created_at), max(created_at) from tickets"
            ).fetchone()
            lines.append(f"tickets.date_range: appointment={row[0]}..{row[1]} created={row[2]}..{row[3]}")
            bad_done = conn.execute(
                "select count(*) from tickets where status in (?, ?, ?) and coalesce(completed_at, '')=''",
                tuple(DONE_STATUSES),
            ).fetchone()[0]
            bad_open = conn.execute(
                "select count(*) from tickets where status in (?, ?, ?, ?, ?) and coalesce(completed_at, '')<>''",
                tuple(OPEN_STATUSES),
            ).fetchone()[0]
            lines.append(f"tickets.done_without_completed_at: {bad_done}")
            lines.append(f"tickets.open_with_completed_at: {bad_open}")
            photo_count = conn.execute(
                "select count(*) from tickets where coalesce(speedtest_photo_data,'')<>'' "
                "or coalesce(before_photos_data,'')<>'' or coalesce(after_photos_data,'')<>''"
            ).fetchone()[0]
            lines.append(f"tickets.photo_placeholder_count: {photo_count}")
        if "customer_accounts" in sc:
            lines.append("")
            append_distribution(lines, conn, "customer_accounts", "service_status")
            append_distribution(lines, conn, "customer_accounts", "payment_status")
        if "manager_approval_requests" in sc:
            lines.append("")
            append_distribution(lines, conn, "manager_approval_requests", "status")
            append_distribution(lines, conn, "manager_approval_requests", "boss_status")
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"report={report_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
