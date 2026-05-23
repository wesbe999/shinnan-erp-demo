from fastapi.responses import RedirectResponse
from app.routes.employee_auth import _employee_current_user_from_request

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import text
from app.db import engine

router = APIRouter(tags=["Shinnan Stats Admin"])


def _one(conn, sql, params=None, default=0):
    try:
        value = conn.execute(text(sql), params or {}).scalar()
        return default if value is None else value
    except Exception:
        return default


def _rows(conn, sql, params=None):
    try:
        return [dict(row) for row in conn.execute(text(sql), params or {}).mappings().all()]
    except Exception:
        return []


def _exists(conn, table_name):
    return bool(_one(
        conn,
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=:name",
        {"name": table_name},
        0,
    ))


def _i(value):
    try:
        return int(value or 0)
    except Exception:
        return 0


def _f(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def _rate(numerator, denominator):
    denominator = _f(denominator)
    if denominator <= 0:
        return 0.0
    return round((_f(numerator) / denominator) * 100.0, 2)



def _normalize_repair_mix(rows):
    customer_problem = "\u5ba2\u6236\u81ea\u8eab\u554f\u984c"
    equipment = "\u8a2d\u5099"
    line = "\u7dda\u8def"
    staff = "\u4eba\u54e1"
    other = "\u5176\u4ed6"
    billing = "\u5e33\u52d9"

    mapping = {
        "\u7db2\u8def": customer_problem,
        "\u5ba2\u6236": customer_problem,
        customer_problem: customer_problem,
        "TV": equipment,
        equipment: equipment,
        line: line,
        staff: staff,
        other: other,
        "\u672a\u5206\u985e": other,
        "": other,
    }

    totals = {}
    for row in rows or []:
        raw_label = str(row.get("label") or "")
        if raw_label == billing:
            continue
        label = mapping.get(raw_label, other)
        totals[label] = totals.get(label, 0) + int(row.get("value") or 0)

    order = [customer_problem, equipment, line, staff, other]
    return [{"label": label, "value": totals[label]} for label in order if totals.get(label, 0) > 0]


def _month_shift(month_key, delta):
    if not month_key or len(month_key) < 7:
        return ""
    year = int(month_key[:4])
    month = int(month_key[5:7]) + int(delta)
    while month <= 0:
        year -= 1
        month += 12
    while month > 12:
        year += 1
        month -= 12
    return f"{year:04d}-{month:02d}"


def _month_range(latest_month, count=12):
    months = []
    for offset in range(count - 1, -1, -1):
        months.append(_month_shift(latest_month, -offset))
    return [m for m in months if m]


def _actual_report_months(conn, latest_month, count=12):
    rows = _rows(conn, """
        SELECT month_key
        FROM (
            SELECT DISTINCT substr(created_at,1,7) AS month_key
            FROM tickets
            WHERE COALESCE(created_at,'') <> ''
              AND substr(created_at,1,7) <= :latest_month
        )
        WHERE COALESCE(month_key,'') <> ''
        ORDER BY month_key DESC
        LIMIT :limit_count
    """, {"latest_month": latest_month, "limit_count": count})

    months = [str(row.get("month_key") or "") for row in rows if row.get("month_key")]
    months = list(reversed(months))

    if months:
        return months

    return _month_range(latest_month, count)


def _ticket_case_condition(kind):
    if kind == "install":
        return "COALESCE(case_type,'') LIKE '%\u88dd\u6a5f%'"
    if kind == "disconnect":
        return "(COALESCE(case_type,'') LIKE '%\u9000\u6a5f%' OR COALESCE(case_type,'') LIKE '%\u62c6\u7dda%')"
    if kind == "repair":
        return "(COALESCE(case_type,'') LIKE '%\u7dad\u4fee%' AND COALESCE(repair_category,'') <> '\u5e33\u52d9')"
    return "1=1"


def _month_ticket_count(conn, month_key, condition="1=1"):
    return _i(_one(
        conn,
        "SELECT COUNT(*) FROM tickets WHERE substr(created_at,1,7)=:m AND " + condition,
        {"m": month_key},
    ))


def _month_completed_count(conn, month_key):
    return _i(_one(conn, """
        SELECT COUNT(*)
        FROM tickets
        WHERE substr(created_at,1,7)=:m
          AND COALESCE(status,'') IN ('\u5df2\u5b8c\u6210','\u5b8c\u6210','\u5df2\u5b8c\u5de5')
    """, {"m": month_key}))


def _month_open_backlog(conn, month_key):
    return _i(_one(conn, """
        SELECT COUNT(*)
        FROM tickets
        WHERE substr(created_at,1,7) <= :m
          AND COALESCE(status,'') IN ('\u672a\u9818\u53d6','\u5df2\u9818\u53d6','\u5f85\u8655\u7406','\u8655\u7406\u4e2d','\u65bd\u5de5\u4e2d','\u5f85\u8001\u95c6\u5224\u65b7')
    """, {"m": month_key}))


def _month_avg_completion_hours(conn, month_key):
    return _f(_one(conn, """
        SELECT AVG((julianday(COALESCE(NULLIF(completed_at,''), NULLIF(finished_at,''))) - julianday(created_at)) * 24.0)
        FROM tickets
        WHERE substr(created_at,1,7)=:m
          AND COALESCE(status,'') IN ('\u5df2\u5b8c\u6210','\u5b8c\u6210','\u5df2\u5b8c\u5de5')
          AND COALESCE(NULLIF(completed_at,''), NULLIF(finished_at,''), '') <> ''
          AND COALESCE(created_at,'') <> ''
    """, {"m": month_key}, 0.0))


def _customer_snapshot_for_month(conn, month_key):
    # Demo DB currently has current-state customer rows. Historical active users are estimated:
    # active at month end = customers installed by month end and not currently marked as terminated.
    active = _i(_one(conn, """
        SELECT COUNT(*)
        FROM customer_accounts
        WHERE substr(COALESCE(NULLIF(install_date,''), created_at),1,7) <= :m
          AND COALESCE(service_status,'') IN ('\u6b63\u5e38','\u5f85\u5fa9\u6a5f')
    """, {"m": month_key}))

    mrr = _f(_one(conn, """
        SELECT COALESCE(SUM(monthly_fee),0)
        FROM customer_accounts
        WHERE substr(COALESCE(NULLIF(install_date,''), created_at),1,7) <= :m
          AND COALESCE(service_status,'') IN ('\u6b63\u5e38','\u5f85\u5fa9\u6a5f')
    """, {"m": month_key}))

    overdue_customers = _i(_one(conn, """
        SELECT COUNT(*)
        FROM customer_accounts
        WHERE substr(COALESCE(NULLIF(install_date,''), created_at),1,7) <= :m
          AND (
             COALESCE(is_overdue,0)=1
          OR COALESCE(payment_status,'') IN ('\u5f85\u7e73','\u6b20\u8cbb')
          OR COALESCE(service_status,'')='\u6b20\u8cbb'
          )
    """, {"m": month_key}))

    overdue_mrr = _f(_one(conn, """
        SELECT COALESCE(SUM(monthly_fee),0)
        FROM customer_accounts
        WHERE substr(COALESCE(NULLIF(install_date,''), created_at),1,7) <= :m
          AND (
             COALESCE(is_overdue,0)=1
          OR COALESCE(payment_status,'') IN ('\u5f85\u7e73','\u6b20\u8cbb')
          OR COALESCE(service_status,'')='\u6b20\u8cbb'
          )
    """, {"m": month_key}))

    ip_limited = _i(_one(conn, """
        SELECT COUNT(*)
        FROM customer_accounts
        WHERE substr(COALESCE(NULLIF(install_date,''), created_at),1,7) <= :m
          AND (
             COALESCE(ip_limited,0)=1
          OR COALESCE(service_status,'')='\u9396 IP'
          )
    """, {"m": month_key}))

    return {
        "active_customers": active,
        "mrr": round(mrr, 0),
        "arpu": round(mrr / active, 2) if active else 0.0,
        "overdue_customers": overdue_customers,
        "overdue_mrr": round(overdue_mrr, 0),
        "overdue_rate": _rate(overdue_customers, active),
        "overdue_mrr_rate": _rate(overdue_mrr, mrr),
        "ip_limited_customers": ip_limited,
        "ip_limited_rate": _rate(ip_limited, active),
    }


def _monthly_series(conn, latest_month, count=12):
    months = _actual_report_months(conn, latest_month, count)
    series = []
    prev_active = 0

    for month_key in months:
        snap = _customer_snapshot_for_month(conn, month_key)
        active_customers = snap["active_customers"]

        installs = _month_ticket_count(conn, month_key, _ticket_case_condition("install"))
        disconnects = _month_ticket_count(conn, month_key, _ticket_case_condition("disconnect"))
        net_adds = installs - disconnects

        if prev_active <= 0:
            estimated_previous_active = max(active_customers - net_adds, 0)
        else:
            estimated_previous_active = prev_active

        growth_rate = _rate(net_adds, estimated_previous_active)
        churn_rate = _rate(disconnects, estimated_previous_active)

        ticket_count = _month_ticket_count(conn, month_key)
        completed_count = _month_completed_count(conn, month_key)
        repair_count = _month_ticket_count(conn, month_key, _ticket_case_condition("repair"))

        item = {
            "month": month_key,
            "active_customers": active_customers,
            "installs": installs,
            "disconnects": disconnects,
            "net_adds": net_adds,
            "estimated_previous_active_customers": estimated_previous_active,
            "growth_rate": growth_rate,
            "churn_rate": churn_rate,
            "mrr": snap["mrr"],
            "arpu": snap["arpu"],
            "overdue_customers": snap["overdue_customers"],
            "overdue_rate": snap["overdue_rate"],
            "overdue_mrr": snap["overdue_mrr"],
            "overdue_mrr_rate": snap["overdue_mrr_rate"],
            "ip_limited_customers": snap["ip_limited_customers"],
            "ip_limited_rate": snap["ip_limited_rate"],
            "ticket_count": ticket_count,
            "completed_count": completed_count,
            "completion_rate": _rate(completed_count, ticket_count),
            "open_backlog": _month_open_backlog(conn, month_key),
            "avg_completion_hours": round(_month_avg_completion_hours(conn, month_key), 2),
            "repair_count": repair_count,
            "repair_rate": _rate(repair_count, active_customers),
        }

        series.append(item)
        if active_customers > 0:
            prev_active = active_customers

    return series


def _build_report():
    with engine.connect() as conn:
        latest_date = str(_one(conn, "SELECT MAX(substr(created_at,1,10)) FROM tickets", default="") or "")
        if not latest_date:
            latest_date = str(_one(conn, "SELECT DATE('now')", default="") or "")
        latest_month = latest_date[:7]

        monthly_series = _monthly_series(conn, latest_month, 12)
        current = monthly_series[-1] if monthly_series else {}
        previous = monthly_series[-2] if len(monthly_series) >= 2 else {}

        repair_mix = _rows(conn, """
            SELECT
              COALESCE(NULLIF(repair_category,''), '\u672a\u5206\u985e') AS label,
              COUNT(*) AS value
            FROM tickets
            WHERE substr(created_at,1,7)=:m
              AND """ + _ticket_case_condition("repair") + """
            GROUP BY COALESCE(NULLIF(repair_category,''), '\u672a\u5206\u985e')
            ORDER BY value DESC
            LIMIT 12
        """, {"m": latest_month})

        repair_mix = _normalize_repair_mix(repair_mix)

        ticket_mix = _rows(conn, """
            SELECT
              COALESCE(case_type,'\u672a\u5206\u985e') AS label,
              COUNT(*) AS value
            FROM tickets
            WHERE substr(created_at,1,7)=:m
            GROUP BY COALESCE(case_type,'\u672a\u5206\u985e')
            ORDER BY value DESC
            LIMIT 12
        """, {"m": latest_month})

        area_monthly_growth = _rows(conn, """
            SELECT
              area AS label,
              SUM(installs) AS installs,
              SUM(disconnects) AS disconnects,
              SUM(installs) - SUM(disconnects) AS net_adds
            FROM (
              SELECT
                COALESCE(dispatch_area,'\u672a\u5206\u5340') AS area,
                CASE WHEN """ + _ticket_case_condition("install") + """ THEN 1 ELSE 0 END AS installs,
                CASE WHEN """ + _ticket_case_condition("disconnect") + """ THEN 1 ELSE 0 END AS disconnects
              FROM tickets
              WHERE substr(created_at,1,7)=:m
            )
            GROUP BY area
            ORDER BY net_adds DESC
            LIMIT 20
        """, {"m": latest_month})

        area_overdue_risk = _rows(conn, """
            SELECT
              COALESCE(area,'\u672a\u5206\u5340') AS label,
              COUNT(*) AS overdue_customers,
              ROUND(COALESCE(SUM(monthly_fee),0),0) AS overdue_mrr
            FROM customer_accounts
            WHERE COALESCE(is_overdue,0)=1
               OR COALESCE(payment_status,'') IN ('\u5f85\u7e73','\u6b20\u8cbb')
               OR COALESCE(service_status,'')='\u6b20\u8cbb'
            GROUP BY COALESCE(area,'\u672a\u5206\u5340')
            ORDER BY overdue_mrr DESC
            LIMIT 20
        """)

        engineer_load = _rows(conn, """
            SELECT
              COALESCE(assigned_engineer, finished_by_name, '\u672a\u6307\u6d3e') AS label,
              COUNT(*) AS ticket_count,
              SUM(CASE WHEN COALESCE(status,'') IN ('\u5df2\u5b8c\u6210','\u5b8c\u6210','\u5df2\u5b8c\u5de5') THEN 1 ELSE 0 END) AS completed_count,
              SUM(CASE WHEN COALESCE(status,'') IN ('\u672a\u9818\u53d6','\u5df2\u9818\u53d6','\u5f85\u8655\u7406','\u8655\u7406\u4e2d','\u65bd\u5de5\u4e2d','\u5f85\u8001\u95c6\u5224\u65b7') THEN 1 ELSE 0 END) AS open_count
            FROM tickets
            WHERE substr(created_at,1,7)=:m
            GROUP BY COALESCE(assigned_engineer, finished_by_name, '\u672a\u6307\u6d3e')
            ORDER BY ticket_count DESC
            LIMIT 20
        """, {"m": latest_month})

        repair_building_risk = []
        if _exists(conn, "dispatch_repair_analysis"):
            repair_building_risk = _rows(conn, """
                SELECT
                  COALESCE(b.name, a.building_no, '\u672a\u6307\u5b9a') AS label,
                  COUNT(*) AS repair_count
                FROM dispatch_repair_analysis a
                LEFT JOIN buildings b
                  ON b.building_no = a.building_no
                GROUP BY a.building_no
                ORDER BY repair_count DESC
                LIMIT 20
            """)

        building_penetration = _rows(conn, """
            SELECT
              b.building_no,
              b.area,
              COALESCE(b.name, b.building_no, '\u672a\u547d\u540d') AS label,
              COALESCE(b.total_households,0) AS total_households,
              COUNT(c.id) AS active_customers,
              ROUND(CASE WHEN COALESCE(b.total_households,0) > 0 THEN COUNT(c.id) * 100.0 / b.total_households ELSE 0 END, 2) AS penetration_rate
            FROM buildings b
            LEFT JOIN customer_accounts c
              ON c.building_no = b.building_no
             AND c.area = b.area
             AND COALESCE(c.service_status,'') IN ('\u6b63\u5e38','\u5f85\u5fa9\u6a5f')
            WHERE COALESCE(b.total_households,0) > 0
            GROUP BY b.building_no, b.area, b.name, b.total_households
            ORDER BY penetration_rate DESC
            LIMIT 20
        """)

        building_opportunity = _rows(conn, """
            SELECT
              b.building_no,
              b.area,
              COALESCE(b.name, b.building_no, '\u672a\u547d\u540d') AS label,
              COALESCE(b.total_households,0) AS total_households,
              COUNT(c.id) AS active_customers,
              MAX(COALESCE(b.total_households,0) - COUNT(c.id),0) AS remaining_households,
              ROUND(CASE WHEN COALESCE(b.total_households,0) > 0 THEN COUNT(c.id) * 100.0 / b.total_households ELSE 0 END, 2) AS penetration_rate
            FROM buildings b
            LEFT JOIN customer_accounts c
              ON c.building_no = b.building_no
             AND c.area = b.area
             AND COALESCE(c.service_status,'') IN ('\u6b63\u5e38','\u5f85\u5fa9\u6a5f')
            WHERE COALESCE(b.total_households,0) > 0
            GROUP BY b.building_no, b.area, b.name, b.total_households
            ORDER BY remaining_households DESC
            LIMIT 20
        """)


        building_monthly_growth = _rows(conn, """
            SELECT
              COALESCE(b.name, t.building_no, '\u672a\u6307\u5b9a') AS label,
              COALESCE(t.dispatch_area, '\u672a\u5206\u5340') AS area,
              SUM(CASE WHEN """ + _ticket_case_condition("install") + """ THEN 1 ELSE 0 END) AS installs,
              SUM(CASE WHEN """ + _ticket_case_condition("disconnect") + """ THEN 1 ELSE 0 END) AS disconnects,
              SUM(CASE WHEN """ + _ticket_case_condition("install") + """ THEN 1 ELSE 0 END)
              - SUM(CASE WHEN """ + _ticket_case_condition("disconnect") + """ THEN 1 ELSE 0 END) AS net_adds
            FROM tickets t
            LEFT JOIN buildings b
              ON b.building_no = t.building_no
             AND b.area = t.dispatch_area
            WHERE substr(t.created_at,1,7)=:m
              AND (""" + _ticket_case_condition("install") + """ OR """ + _ticket_case_condition("disconnect") + """)
            GROUP BY COALESCE(b.name, t.building_no, '\u672a\u6307\u5b9a'), COALESCE(t.dispatch_area, '\u672a\u5206\u5340')
            HAVING net_adds > 0
            ORDER BY net_adds DESC, installs DESC
            LIMIT 5
        """, {"m": latest_month})

        building_monthly_decline = _rows(conn, """
            SELECT
              COALESCE(b.name, t.building_no, '\u672a\u6307\u5b9a') AS label,
              COALESCE(t.dispatch_area, '\u672a\u5206\u5340') AS area,
              SUM(CASE WHEN """ + _ticket_case_condition("install") + """ THEN 1 ELSE 0 END) AS installs,
              SUM(CASE WHEN """ + _ticket_case_condition("disconnect") + """ THEN 1 ELSE 0 END) AS disconnects,
              SUM(CASE WHEN """ + _ticket_case_condition("install") + """ THEN 1 ELSE 0 END)
              - SUM(CASE WHEN """ + _ticket_case_condition("disconnect") + """ THEN 1 ELSE 0 END) AS net_adds
            FROM tickets t
            LEFT JOIN buildings b
              ON b.building_no = t.building_no
             AND b.area = t.dispatch_area
            WHERE substr(t.created_at,1,7)=:m
              AND (""" + _ticket_case_condition("install") + """ OR """ + _ticket_case_condition("disconnect") + """)
            GROUP BY COALESCE(b.name, t.building_no, '\u672a\u6307\u5b9a'), COALESCE(t.dispatch_area, '\u672a\u5206\u5340')
            HAVING net_adds < 0
            ORDER BY net_adds ASC, disconnects DESC
            LIMIT 5
        """, {"m": latest_month})


        building_development_potential = _rows(conn, """
            WITH raw AS (
              SELECT
                b.building_no AS building_no,
                b.area AS area,
                COALESCE(b.name, b.building_no, '\u672a\u547d\u540d') AS label,
                COALESCE(b.total_households,0) AS total_households,

                (
                  SELECT COUNT(*)
                  FROM customer_accounts c
                  WHERE c.building_no = b.building_no
                    AND c.area = b.area
                    AND COALESCE(c.service_status,'') IN ('\u6b63\u5e38','\u5f85\u5fa9\u6a5f')
                ) AS active_customers,

                (
                  SELECT COUNT(*)
                  FROM customer_accounts c
                  WHERE c.building_no = b.building_no
                    AND c.area = b.area
                    AND (
                         COALESCE(c.is_overdue,0)=1
                      OR COALESCE(c.payment_status,'') IN ('\u5f85\u7e73','\u6b20\u8cbb')
                      OR COALESCE(c.service_status,'')='\u6b20\u8cbb'
                    )
                ) AS overdue_customers,

                (
                  SELECT COUNT(*)
                  FROM tickets t
                  WHERE t.building_no = b.building_no
                    AND t.dispatch_area = b.area
                    AND substr(t.created_at,1,7) IN (:m0,:m1,:m2)
                    AND """ + _ticket_case_condition("install") + """
                ) AS installs_3m,

                (
                  SELECT COUNT(*)
                  FROM tickets t
                  WHERE t.building_no = b.building_no
                    AND t.dispatch_area = b.area
                    AND substr(t.created_at,1,7) IN (:m0,:m1,:m2)
                    AND """ + _ticket_case_condition("disconnect") + """
                ) AS disconnects_3m,

                (
                  SELECT COUNT(*)
                  FROM tickets t
                  WHERE t.building_no = b.building_no
                    AND t.dispatch_area = b.area
                    AND substr(t.created_at,1,7) IN (:m0,:m1,:m2)
                    AND """ + _ticket_case_condition("repair") + """
                ) AS repairs_3m

              FROM buildings b
              WHERE COALESCE(b.total_households,0) > 0
            ),
            scored AS (
              SELECT
                building_no,
                area,
                label,
                total_households,
                active_customers,
                MAX(total_households - active_customers, 0) AS remaining_households,
                ROUND(CASE WHEN total_households > 0 THEN active_customers * 100.0 / total_households ELSE 0 END, 2) AS penetration_rate,
                overdue_customers,
                installs_3m,
                disconnects_3m,
                repairs_3m,
                ROUND(
                    (MAX(total_households - active_customers, 0) * 1.0)
                  + (installs_3m * 15.0)
                  - (disconnects_3m * 20.0)
                  - (repairs_3m * 1.5)
                  - (overdue_customers * 8.0)
                  - (CASE WHEN total_households > 0 AND active_customers * 100.0 / total_households >= 60 THEN 100.0 ELSE 0.0 END)
                , 2) AS potential_score
              FROM raw
            )
            SELECT *
            FROM scored
            ORDER BY potential_score DESC, remaining_households DESC
            LIMIT 10
        """, {
            "m0": latest_month,
            "m1": _month_shift(latest_month, -1),
            "m2": _month_shift(latest_month, -2),
        })

        payroll_cost = 0.0
        if _exists(conn, "hr_salary_profiles"):
            payroll_cost = _f(_one(conn, """
                SELECT COALESCE(SUM(
                    COALESCE(base_salary,0)
                  + COALESCE(duty_allowance,0)
                  + COALESCE(technical_allowance,0)
                  + COALESCE(supervisor_allowance,0)
                  + COALESCE(transport_allowance,0)
                  + COALESCE(phone_allowance,0)
                  + COALESCE(meal_allowance,0)
                  + COALESCE(full_attendance_bonus,0)
                  + COALESCE(performance_bonus,0)
                  + COALESCE(engineering_bonus,0)
                  + COALESCE(overtime_pay,0)
                ),0)
                FROM hr_salary_profiles
            """))

        current_mrr = _f(current.get("mrr", 0))
        payroll_to_mrr_rate = _rate(payroll_cost, current_mrr)

        return {
            "meta": {
                "report_type": "telecom_monthly_operation_dashboard",
                "version": "cl13a",
                "latest_date": latest_date,
                "latest_month": latest_month,
                "months": [item["month"] for item in monthly_series],
                "method_notes": [
                    "daily_page_should_focus_on_month_over_month_and_trend_not_yearly_report",
                    "growth_and_churn_are_estimated_from_install_disconnect_tickets",
                    "mrr_and_arpu_are_estimated_from_customer_accounts_current_monthly_fee",
                    "building_penetration_is_recalculated_from_customer_accounts_not_buildings_active_users",
                    "material_cost_is_excluded_until_monthly_material_source_is_confirmed",
                    "repair_category_standard_customer_equipment_line_staff_other",
                    "building_development_potential_score_uses_remaining_installs_disconnects_repairs_overdue",
                    "billing_category_is_excluded_from_repair_reason_statistics",
                    "monthly_series_uses_actual_ticket_months_only",
                    "repair_count_uses_repair_case_type_only"
                ],
            },
            "current": current,
            "previous": previous,
            "monthly_series": monthly_series,
            "mix": {
                "repair_mix": repair_mix,
                "ticket_mix": ticket_mix,
            },
            "ranking": {
                "area_monthly_growth": area_monthly_growth,
                "area_overdue_risk": area_overdue_risk,
                "engineer_load": engineer_load,
                "repair_building_risk": repair_building_risk,
                "building_penetration": building_penetration,
                "building_opportunity": building_opportunity,
                "building_development_potential": building_development_potential,
                "building_monthly_growth": building_monthly_growth,
                "building_monthly_decline": building_monthly_decline,
            },
            "cost_and_manpower": {
                "material_report_status": "excluded_no_monthly_source",
                "material_cost": None,
                "payroll_cost": round(payroll_cost, 0),
                "payroll_to_mrr_rate": payroll_to_mrr_rate,
            },
        }


@router.get("/api/admin/stats/summary")
def admin_stats_summary():
    return JSONResponse(_build_report())


@router.get("/api/admin/stats/monthly")
def admin_stats_monthly():
    report = _build_report()
    return JSONResponse({
        "meta": report["meta"],
        "current": report["current"],
        "previous": report["previous"],
        "monthly_series": report["monthly_series"],
    })


@router.get("/admin/stats", response_class=HTMLResponse)
def admin_stats_page(request: Request):
    _user = _employee_current_user_from_request(request)
    if not _user:
        return RedirectResponse(f"/employee/login?next=/admin/stats", status_code=303)
    return HTMLResponse(STATS_HTML)


STATS_HTML = r"""
<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>&#x8cc7;&#x6599;&#x7d71;&#x8a08;&#xff5c;&#x4e2d;&#x592e;&#x63a7;&#x7ba1;&#x7cfb;&#x7d71;</title>
<link rel="stylesheet" href="/static/web_title_unified.css?v=xn_v2">
<link rel="stylesheet" href="/static/xn_buttons.css?v=xn_v1">
<link rel="stylesheet" href="/static/stats_admin.css?v=xn_v1">

</head>
<body>
<section class="web-title web-title-tech" id="xn-page-header">
  <img class="web-title-watermark" src="/static/shinnan_logo_outline_white.png" alt="">
  <div class="web-title-map"></div>
  <div class="web-title-radar"></div>
  <div class="web-title-main">
    <div class="web-title-logo-box">
      <img class="web-title-logo" src="/static/shinnan_logo_gold_transparent.png?v=cl_header_v1" alt="ShinNan Logo">
    </div>
    <div class="web-title-text">
      <h1 class="web-title-system">資料統計</h1>
      <div class="web-title-sub">
        <span class="web-title-sub-dot"></span>中央控管系統<span class="web-title-sub-dot"></span>
      </div>
    </div>
  </div>
  <div class="xn-header-actions">
    <button type="button" style="background:#b45309 !important;border:1.5px solid #d4af37 !important" onclick="loadStats()">重新整理</button>
    <button type="button" style="background:#6b3fa0 !important;border:1.5px solid #d4af37 !important" onclick="window.location.href='/'">🏠 首頁</button>
    <button type="button" class="danger" style="border:1.5px solid #d4af37 !important" onclick="window.location.href='/employee/logout?next=/'">登出</button>
  </div>
</section>

<main class="page">
  <div class="intro">
    <div>
      <h2>&#x96fb;&#x4fe1;&#x71df;&#x904b;&#x6708;&#x5831;&#x5100;&#x8868;&#x677f;</h2>
      <p>&#x4ee5;&#x9010;&#x6708;&#x5c0d;&#x6bd4;&#x70ba;&#x4e3b;&#xff1a;&#x6298;&#x7dda;&#x5716;&#x770b;&#x6210;&#x9577;&#x8207;&#x8870;&#x9000;&#xff0c;&#x5713;&#x9905;&#x5716;&#x770b;&#x4f54;&#x6bd4;&#xff0c;&#x9577;&#x689d;&#x5716;&#x770b;&#x7cbe;&#x78ba;&#x6578;&#x5b57;&#x6392;&#x884c;&#x3002;</p>
      <div id="meta_line" class="note"></div>
    </div>
  </div>

  <section class="kpi-grid" id="kpi_grid"></section>

  <!-- Row 1: 逐月成長率 + MRR/ARPU -->
  <section class="grid-two">
    <div class="panel">
      <h3>&#x9010;&#x6708;&#x7e3d;&#x6210;&#x9577;&#x7387;&#x8207;&#x6d41;&#x5931;&#x7387;</h3>
      <div class="panel-sub">&#x6298;&#x7dda;&#x5716;&#xff1a;&#x6de8;&#x6210;&#x9577;&#x3001;&#x6d41;&#x5931;&#x7387;</div>
      <svg class="svg-chart" id="growth_line"></svg>
      <div class="legend"><span><i class="la"></i>&#x6de8;&#x6210;&#x9577;</span><span><i class="lb"></i>&#x6d41;&#x5931;&#x7387;</span></div>
    </div>
    <div class="panel">
      <h3>MRR / ARPU &#x9010;&#x6708;&#x8da8;&#x52e2;</h3>
      <div class="panel-sub">&#x6298;&#x7dda;&#x5716;&#xff1a;&#x6708;&#x7d93;&#x5e38;&#x6027;&#x6536;&#x5165;&#x8207;&#x6bcf;&#x6236;&#x5e73;&#x5747;&#x6536;&#x5165;</div>
      <svg class="svg-chart" id="revenue_line"></svg>
      <div class="legend"><span><i class="la"></i>MRR</span><span><i class="lb"></i>ARPU</span></div>
    </div>
  </section>

  <!-- Row 2: 本月成長前5 + 本月衰退前5 -->
  <section class="grid-two">
    <div class="panel">
      <h3>&#x672c;&#x6708;&#x6210;&#x9577;&#x524d; 5 &#x540d;&#x5927;&#x6a13;</h3>
      <div class="panel-sub">&#x9577;&#x689d;&#x5716;&#xff1a;&#x88dd;&#x6a5f;&#x6e1b;&#x9000;&#x6a5f;&#x7684;&#x6de8;&#x589e;&#x6236;&#x6578;</div>
      <div class="bar-list" id="building_growth_bar"></div>
    </div>
    <div class="panel">
      <h3>&#x672c;&#x6708;&#x8870;&#x9000;&#x524d; 5 &#x540d;&#x5927;&#x6a13;</h3>
      <div class="panel-sub">&#x9577;&#x689d;&#x5716;&#xff1a;&#x9000;&#x79df;&#x5927;&#x65bc;&#x88dd;&#x6a5f;&#x7684;&#x6de8;&#x6e1b;&#x6236;&#x6578;</div>
      <div class="bar-list" id="building_decline_bar"></div>
    </div>
  </section>

  <!-- Row 3: 帳務風險趨勢 + 各區欠費風險 -->
  <section class="grid-two">
    <div class="panel">
      <h3>&#x5e33;&#x52d9;&#x98a8;&#x96aa;&#x9010;&#x6708;&#x8da8;&#x52e2;</h3>
      <div class="panel-sub">&#x6298;&#x7dda;&#x5716;&#xff1a;&#x6b20;&#x8cbb;&#x7387;&#x3001;&#x9396; IP &#x7387;</div>
      <svg class="svg-chart small" id="risk_line"></svg>
      <div class="legend"><span><i class="la"></i>&#x6b20;&#x8cbb;&#x7387;</span><span><i class="lb"></i>&#x9396; IP &#x7387;</span></div>
    </div>
    <div class="panel">
      <h3>&#x5404;&#x5340;&#x6b20;&#x8cbb;&#x98a8;&#x96aa;</h3>
      <div class="bar-list" id="overdue_area_bar"></div>
    </div>
  </section>

  <!-- Row 4: 各區淨成長 + 高潛力開發大樓 -->
  <section class="grid-two">
    <div class="panel">
      <h3>&#x5404;&#x5340;&#x6de8;&#x6210;&#x9577;</h3>
      <div class="bar-list" id="area_growth_bar"></div>
    </div>
    <div class="panel">
      <h3>&#x9ad8;&#x6f5b;&#x529b;&#x958b;&#x767c;&#x5927;&#x6a13;&#xff08;&#x7d9c;&#x5408;&#x5206;&#x6578;&#xff09;</h3>
      <div class="bar-list" id="building_opportunity_bar"></div>
    </div>
  </section>

  <!-- Row 5: 維修原因圓餅 + 高頻維修大樓 -->
  <section class="grid-two">
    <div class="panel">
      <h3>&#x7dad;&#x4fee;&#x539f;&#x56e0;&#x4f54;&#x6bd4;</h3>
      <div class="panel-sub">&#x5713;&#x9905;&#x5716;&#xff1a;&#x672c;&#x6708;&#x7dad;&#x4fee;&#x985e;&#x5225;&#x7d50;&#x69cb;</div>
      <div class="donut-wrap">
        <div class="donut" id="repair_donut"><div class="donut-center" id="repair_donut_center">0</div></div>
        <div class="pie-list" id="repair_pie_list"></div>
      </div>
    </div>
    <div class="panel">
      <h3>&#x9ad8;&#x983b;&#x7dad;&#x4fee;&#x5927;&#x6a13;</h3>
      <div class="bar-list" id="repair_building_bar"></div>
    </div>
  </section>

  <!-- Row 6: 工程師負載 + 案件類型圓餅 -->
  <section class="grid-two">
    <div class="panel">
      <h3>&#x5de5;&#x7a0b;&#x5e2b;&#x8ca0;&#x8f09;</h3>
      <div class="bar-list" id="engineer_load_bar"></div>
    </div>
    <div class="panel">
      <h3>&#x6848;&#x4ef6;&#x985e;&#x578b;&#x4f54;&#x6bd4;</h3>
      <div class="panel-sub">&#x5713;&#x9905;&#x5716;&#xff1a;&#x672c;&#x6708;&#x6d3e;&#x5de5;&#x985e;&#x578b;&#x7d50;&#x69cb;</div>
      <div class="donut-wrap">
        <div class="donut" id="ticket_donut"><div class="donut-center" id="ticket_donut_center">0</div></div>
        <div class="pie-list" id="ticket_pie_list"></div>
      </div>
    </div>
  </section>

  <!-- Row 7: 派工效率趨勢（單獨一行，佔全寬） -->
  <section class="grid-two">
    <div class="panel">
      <h3>&#x6d3e;&#x5de5;&#x6548;&#x7387;&#x9010;&#x6708;&#x8da8;&#x52e2;</h3>
      <div class="panel-sub">&#x6298;&#x7dda;&#x5716;&#xff1a;&#x5b8c;&#x5de5;&#x7387;&#x3001;&#x7dad;&#x4fee;&#x7387;</div>
      <svg class="svg-chart small" id="dispatch_line"></svg>
      <div class="legend"><span><i class="la"></i>&#x5b8c;&#x5de5;&#x7387;</span><span><i class="lb"></i>&#x7dad;&#x4fee;&#x7387;</span></div>
    </div>
    <div class="panel" style="display:flex;align-items:center;justify-content:center;color:#a0b0a8;font-size:15px;font-weight:900;min-height:200px;">&#x66f4;&#x591a;&#x5831;&#x8868;&#x529f;&#x80fd;&#x958b;&#x767c;&#x4e2d;</div>
  </section>
</main>

<script>
var PIE_COLORS=["#0f6b3b","#d8a63f","#2f80ed","#eb5757","#9b51e0","#27ae60","#f2994a","#56ccf2","#bb6bd9","#6fcf97","#f2c94c","#4f4f4f"];
function num(v){var n=Number(v||0);return Number.isFinite(n)?n:0;}
function fmt(v){return num(v).toLocaleString("zh-TW");}
function pct(v){return num(v).toFixed(2)+"%";}
function money(v){return "$"+Math.round(num(v)).toLocaleString("zh-TW");}
function esc(v){return String(v==null?"":v).replace(/[&<>"']/g,function(c){if(c==="&")return "&amp;";if(c==="<")return "&lt;";if(c===">")return "&gt;";if(c==='"')return "&quot;";return "&#39;";});}
function deltaClass(v){v=num(v);return v>0?"up":(v<0?"down":"flat");}
function deltaText(v,unit){v=num(v);var sign=v>0?"+":"";return sign+fmt(v)+(unit||"");}
function diff(current,previous){return num(current)-num(previous);}
function kpi(label,value,hint,delta,deltaUnit){
  return '<div class="kpi"><div class="label">'+esc(label)+'</div><div class="value">'+value+'</div><div class="hint">'+esc(hint||"")+'</div><div class="delta '+deltaClass(delta)+'">'+deltaText(delta,deltaUnit)+'</div></div>';
}
function renderKpis(cur,pre){
  var html=[
    kpi("\u6709\u6548\u6236\u6578",fmt(cur.active_customers)+"\u6236","\u8207\u4e0a\u6708\u6bd4",diff(cur.active_customers,pre.active_customers),"\u6236"),
    kpi("\u6de8\u6210\u9577",fmt(cur.net_adds)+"\u6236","\u88dd\u6a5f - \u9000\u79df",diff(cur.net_adds,pre.net_adds),"\u6236"),
    kpi("MRR",money(cur.mrr),"\u6708\u7d93\u5e38\u6027\u6536\u5165",diff(cur.mrr,pre.mrr),"\u5143"),
    kpi("ARPU",money(cur.arpu),"\u6bcf\u6236\u5e73\u5747\u6708\u6536\u5165",diff(cur.arpu,pre.arpu),"\u5143"),
    kpi("\u6d41\u5931\u7387",pct(cur.churn_rate),"\u9000\u79df / \u4f30\u7b97\u4e0a\u6708\u6709\u6548\u6236",diff(cur.churn_rate,pre.churn_rate),"%"),
    kpi("\u6b20\u8cbb\u7387",pct(cur.overdue_rate),"\u6b20\u8cbb\u6236 / \u6709\u6548\u6236",diff(cur.overdue_rate,pre.overdue_rate),"%"),
    kpi("\u5b8c\u5de5\u7387",pct(cur.completion_rate),"\u5b8c\u6210 / \u672c\u6708\u6848\u4ef6",diff(cur.completion_rate,pre.completion_rate),"%"),
    kpi("\u7dad\u4fee\u7387",pct(cur.repair_rate),"\u7dad\u4fee\u6848\u4ef6 / \u6709\u6548\u6236",diff(cur.repair_rate,pre.repair_rate),"%")
  ].join("");
  document.getElementById("kpi_grid").innerHTML=html;
}
function svgLine(id,rows,keyA,keyB,labelFormatA,labelFormatB){
  var svg=document.getElementById(id);
  var w=svg.clientWidth||600,h=svg.clientHeight||280,pad=38;
  var vals=[];
  rows.forEach(function(r){vals.push(num(r[keyA]));vals.push(num(r[keyB]));});
  var max=Math.max.apply(null,vals.concat([1])),min=Math.min.apply(null,vals.concat([0]));
  if(max===min){max+=1;min=0;}
  function x(i){return pad+(w-pad*2)*(i/Math.max(rows.length-1,1));}
  function y(v){return h-pad-((num(v)-min)/(max-min))*(h-pad*2);}
  function pathFor(key){return rows.map(function(r,i){return (i?"L":"M")+x(i).toFixed(1)+" "+y(r[key]).toFixed(1);}).join(" ");}
  var html='';
  html+='<line class="axis" x1="'+pad+'" y1="'+(h-pad)+'" x2="'+(w-pad)+'" y2="'+(h-pad)+'"></line>';
  html+='<line class="axis" x1="'+pad+'" y1="'+pad+'" x2="'+pad+'" y2="'+(h-pad)+'"></line>';
  html+='<path class="line-a" d="'+pathFor(keyA)+'"></path>';
  html+='<path class="line-b" d="'+pathFor(keyB)+'"></path>';
  rows.forEach(function(r,i){
    html+='<circle class="point-a" cx="'+x(i)+'" cy="'+y(r[keyA])+'" r="4"><title>'+esc(r.month+" "+labelFormatA(r[keyA]))+'</title></circle>';
    html+='<circle class="point-b" cx="'+x(i)+'" cy="'+y(r[keyB])+'" r="4"><title>'+esc(r.month+" "+labelFormatB(r[keyB]))+'</title></circle>';
    html+='<text class="chart-label" x="'+x(i)+'" y="'+(h-12)+'" text-anchor="middle">'+esc(String(r.month).slice(5))+'</text>';
  });
  html+='<text class="chart-label" x="'+(pad+4)+'" y="'+(pad-10)+'">'+esc(labelFormatA(max))+'</text>';
  svg.setAttribute("viewBox","0 0 "+w+" "+h);
  svg.innerHTML=html;
}
function renderDonut(id,listId,centerId,rows,valueKey){
  rows=(rows||[]).slice(0,8);
  var total=rows.reduce(function(s,r){return s+num(r[valueKey||"value"]);},0);
  var deg=0,parts=[];
  rows.forEach(function(r,i){
    var v=num(r[valueKey||"value"]);
    var next=deg+(total? v/total*360:0);
    parts.push(PIE_COLORS[i%PIE_COLORS.length]+" "+deg.toFixed(2)+"deg "+next.toFixed(2)+"deg");
    deg=next;
  });
  if(!parts.length){parts=["#dfe8e2 0deg 360deg"];}
  document.getElementById(id).style.background="conic-gradient("+parts.join(",")+")";
  document.getElementById(centerId).textContent=fmt(total);
  document.getElementById(listId).innerHTML=rows.map(function(r,i){
    var v=num(r[valueKey||"value"]);
    var p=total? v/total*100:0;
    return '<div class="pie-item"><span class="pie-color" style="background:'+PIE_COLORS[i%PIE_COLORS.length]+'"></span><span>'+esc(r.label)+'</span><strong>'+fmt(v)+' / '+p.toFixed(1)+'%</strong></div>';
  }).join("") || '<div class="note">\u76ee\u524d\u7121\u8cc7\u6599</div>';
}
function renderBars(id,rows,labelKey,valueKey,suffix){
  rows=(rows||[]).slice(0,12);
  var max=Math.max.apply(null,rows.map(function(r){return Math.abs(num(r[valueKey]));}).concat([1]));
  document.getElementById(id).innerHTML=rows.map(function(r){
    var v=num(r[valueKey]);
    var width=Math.max(3,Math.abs(v)/max*100);
    var grad=v<0?"linear-gradient(90deg,#b42318,#eb5757,#f2994a)":"linear-gradient(90deg,#0f5132,#35a46a,#e1b64d)";
    return '<div class="bar-row"><div class="bar-label" title="'+esc(r[labelKey])+'">'+esc(r[labelKey])+'</div><div class="bar-track"><div class="bar-fill" style="width:'+width+'%;background:'+grad+'"></div></div><div class="bar-value">'+fmt(v)+(suffix||"")+'</div></div>';
  }).join("") || '<div class="note">\u76ee\u524d\u7121\u8cc7\u6599</div>';
}
async function loadStats(){
  var res=await fetch("/api/admin/stats/summary?ts="+Date.now(),{cache:"no-store"});
  var data=await res.json();
  var series=data.monthly_series||[],cur=data.current||{},pre=data.previous||{};
  document.getElementById("meta_line").textContent="Report "+(data.meta.latest_month||"-")+" / months "+(data.meta.months||[]).join(", ");
  renderKpis(cur,pre);
  svgLine("growth_line",series,"net_adds","churn_rate",function(v){return fmt(v)+"\u6236";},function(v){return pct(v);});
  svgLine("revenue_line",series,"mrr","arpu",function(v){return money(v);},function(v){return money(v);});
  svgLine("risk_line",series,"overdue_rate","ip_limited_rate",function(v){return pct(v);},function(v){return pct(v);});
  svgLine("dispatch_line",series,"completion_rate","repair_rate",function(v){return pct(v);},function(v){return pct(v);});
  renderDonut("repair_donut","repair_pie_list","repair_donut_center",(data.mix||{}).repair_mix||[],"value");
  renderDonut("ticket_donut","ticket_pie_list","ticket_donut_center",(data.mix||{}).ticket_mix||[],"value");
  var ranking=data.ranking||{};
  renderBars("area_growth_bar",ranking.area_monthly_growth||[],"label","net_adds","\u6236");
  renderBars("building_growth_bar",ranking.building_monthly_growth||[],"label","net_adds","\u6236");
  renderBars("building_decline_bar",ranking.building_monthly_decline||[],"label","net_adds","\u6236");
  renderBars("engineer_load_bar",ranking.engineer_load||[],"label","ticket_count","\u4ef6");
  renderBars("overdue_area_bar",ranking.area_overdue_risk||[],"label","overdue_mrr","\u5143");
  renderBars("repair_building_bar",ranking.repair_building_risk||[],"label","repair_count","\u6b21");
  renderBars("building_opportunity_bar",ranking.building_development_potential||ranking.building_opportunity||[],"label","potential_score","\u5206");
}
window.addEventListener("resize",function(){clearTimeout(window.__statsResizeTimer);window.__statsResizeTimer=setTimeout(loadStats,250);});
loadStats().catch(function(err){alert("stats load failed");console.error(err);});
</script>

<script src='/static/xn_theme.js?v=5'></script>
</body>
</html>
"""
