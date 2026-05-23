import json as _ticket_link_json
from urllib.parse import parse_qs as _ticket_link_parse_qs

from fastapi import APIRouter
from fastapi import Request as _TicketLinkRequest
from fastapi.responses import HTMLResponse as _TicketLinkHTMLResponse
from fastapi.responses import Response as _TicketLinkResponse
from sqlalchemy import text as _ticket_link_sql_text

from app.db import engine as _ticket_link_engine
from app.routes.buildings_admin import _buildings_db_init
from app.routes.customers_admin import _customer_accounts_db_init

router = APIRouter(tags=["ticket-customer-link-admin"])


# SHINNAN_TICKET_CUSTOMER_LINK_START
def _ticket_customer_link_db_init():
    with _ticket_link_engine.begin() as conn:
        rows = conn.execute(_ticket_link_sql_text("PRAGMA table_info(tickets)")).fetchall()
        cols = [row[1] for row in rows]

        if "customer_no" not in cols:
            conn.execute(_ticket_link_sql_text("ALTER TABLE tickets ADD COLUMN customer_no TEXT DEFAULT ''"))

        if "building_no" not in cols:
            conn.execute(_ticket_link_sql_text("ALTER TABLE tickets ADD COLUMN building_no TEXT DEFAULT ''"))

        conn.execute(_ticket_link_sql_text("""
            CREATE TABLE IF NOT EXISTS ticket_customer_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                ticket_no TEXT DEFAULT '',
                customer_name TEXT DEFAULT '',
                contact_phone TEXT DEFAULT '',
                service_address TEXT DEFAULT '',
                candidate_customer_no TEXT DEFAULT '',
                candidate_building_no TEXT DEFAULT '',
                match_type TEXT DEFAULT '',
                match_score INTEGER DEFAULT 0,
                review_status TEXT DEFAULT '待人工確認',
                review_note TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))


@router.get("/api/admin/ticket-customer-candidates", summary="讀取派工客戶關聯候選")
def api_admin_ticket_customer_candidates(status: str = "待人工確認", q: str = "", limit: int = 200):
    _ticket_customer_link_db_init()

    limit = max(1, min(int(limit or 200), 500))

    where = []
    params = {"limit": limit}

    if status and status != "全部":
        where.append("c.review_status = :status")
        params["status"] = status

    if q:
        where.append("""
            (
                c.ticket_no LIKE :q OR
                c.customer_name LIKE :q OR
                c.contact_phone LIKE :q OR
                c.service_address LIKE :q
            )
        """)
        params["q"] = "%" + q + "%"

    where_sql = ""
    if where:
        where_sql = "WHERE " + " AND ".join(where)

    with _ticket_link_engine.begin() as conn:
        rows = conn.execute(
            _ticket_link_sql_text(f"""
                SELECT
                    c.id AS candidate_id,
                    c.ticket_id,
                    c.ticket_no,
                    c.customer_name,
                    c.contact_phone,
                    c.service_address,
                    c.candidate_customer_no,
                    c.candidate_building_no,
                    c.match_type,
                    c.match_score,
                    c.review_status,
                    c.review_note,
                    t.case_type,
                    t.status AS ticket_status,
                    t.appointment_date,
                    t.appointment_time,
                    t.assigned_engineer,
                    t.customer_no AS linked_customer_no,
                    t.building_no AS linked_building_no
                FROM ticket_customer_candidates c
                LEFT JOIN tickets t ON t.id = c.ticket_id
                {where_sql}
                ORDER BY
                    CASE c.review_status
                        WHEN '待人工確認' THEN 0
                        WHEN '已確認' THEN 1
                        ELSE 2
                    END,
                    c.ticket_id ASC
                LIMIT :limit
            """),
            params,
        ).mappings().fetchall()

    return _TicketLinkResponse(
        content=_ticket_link_json.dumps([dict(row) for row in rows], ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.get("/api/admin/ticket-customer-candidates/search-customers", summary="搜尋客戶供派工關聯")
def api_admin_ticket_customer_search_customers(q: str = "", limit: int = 30):
    _ticket_customer_link_db_init()
    _customer_accounts_db_init()
    _buildings_db_init()

    q = (q or "").strip()
    limit = max(1, min(int(limit or 30), 80))

    where_sql = ""
    params = {"limit": limit}

    if q:
        where_sql = """
            WHERE
                c.customer_no LIKE :q OR
                c.customer_name LIKE :q OR
                c.customer_phone LIKE :q OR
                c.service_address LIKE :q OR
                b.name LIKE :q
        """
        params["q"] = "%" + q + "%"

    with _ticket_link_engine.begin() as conn:
        rows = conn.execute(
            _ticket_link_sql_text(f"""
                SELECT
                    c.customer_no,
                    c.customer_name,
                    c.customer_phone,
                    c.customer_type,
                    c.building_no,
                    COALESCE(b.name, CASE WHEN c.building_no = 'HOUSE' THEN '透天' ELSE '' END) AS building_name,
                    COALESCE(b.area, CASE WHEN c.building_no = 'HOUSE' THEN '透天' ELSE '' END) AS area,
                    c.service_address,
                    c.account_status,
                    c.payment_method,
                    c.arrears_status
                FROM customer_accounts c
                LEFT JOIN buildings b ON b.building_no = c.building_no
                {where_sql}
                ORDER BY c.customer_no
                LIMIT :limit
            """),
            params,
        ).mappings().fetchall()

    return _TicketLinkResponse(
        content=_ticket_link_json.dumps([dict(row) for row in rows], ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.post("/api/admin/ticket-customer-candidates/confirm", summary="確認派工案件關聯客戶")
async def api_admin_ticket_customer_candidates_confirm(request: _TicketLinkRequest):
    _ticket_customer_link_db_init()

    raw = (await request.body()).decode("utf-8")
    form = _ticket_link_parse_qs(raw)

    def val(name, default=""):
        return (form.get(name, [default])[0] or default).strip()

    candidate_id = val("candidate_id")
    customer_no = val("customer_no")
    review_note = val("review_note")

    if not candidate_id or not customer_no:
        return _TicketLinkResponse(
            content=_ticket_link_json.dumps({"ok": False, "error": "缺少 candidate_id 或 customer_no"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    with _ticket_link_engine.begin() as conn:
        candidate = conn.execute(
            _ticket_link_sql_text("""
                SELECT id, ticket_id, ticket_no
                FROM ticket_customer_candidates
                WHERE id = :id
                LIMIT 1
            """),
            {"id": candidate_id},
        ).mappings().first()

        if not candidate:
            return _TicketLinkResponse(
                content=_ticket_link_json.dumps({"ok": False, "error": "找不到候選資料"}, ensure_ascii=False),
                media_type="application/json; charset=utf-8",
                status_code=404,
            )

        customer = conn.execute(
            _ticket_link_sql_text("""
                SELECT
                    c.customer_no,
                    COALESCE(NULLIF(c.building_name, ''), NULLIF(b.name, ''), CASE WHEN c.building_no = 'HOUSE' THEN '透天' ELSE c.building_no END, '') AS building_name
                FROM customer_accounts c
                LEFT JOIN buildings b ON b.building_no = c.building_no
                WHERE c.customer_no = :customer_no
                LIMIT 1
            """),
            {"customer_no": customer_no},
        ).mappings().first()

        if not customer:
            return _TicketLinkResponse(
                content=_ticket_link_json.dumps({"ok": False, "error": "找不到客戶資料"}, ensure_ascii=False),
                media_type="application/json; charset=utf-8",
                status_code=404,
            )

        conn.execute(
            _ticket_link_sql_text("""
                UPDATE tickets
                SET customer_no = :customer_no,
                    building_no = :building_name
                WHERE id = :ticket_id
            """),
            {
                "customer_no": customer["customer_no"],
                "building_name": customer["building_name"],
                "ticket_id": candidate["ticket_id"],
            },
        )

        conn.execute(
            _ticket_link_sql_text("""
                UPDATE ticket_customer_candidates
                SET candidate_customer_no = :customer_no,
                    candidate_building_no = :building_name,
                    match_type = 'manual_confirmed',
                    match_score = 100,
                    review_status = '已確認',
                    review_note = :review_note,
                    updated_at = datetime('now')
                WHERE id = :candidate_id
            """),
            {
                "customer_no": customer["customer_no"],
                "building_name": customer["building_name"],
                "review_note": review_note or "人工確認關聯",
                "candidate_id": candidate_id,
            },
        )

    return _TicketLinkResponse(
        content=_ticket_link_json.dumps({"ok": True}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )



@router.post("/api/admin/ticket-customer-candidates/create-customer-and-confirm", summary="由派工資料建立新客戶並綁定")
async def api_admin_ticket_customer_create_customer_and_confirm(request: _TicketLinkRequest):
    _ticket_customer_link_db_init()

    raw = (await request.body()).decode("utf-8")
    form = _ticket_link_parse_qs(raw)

    def val(name, default=""):
        return (form.get(name, [default])[0] or default).strip()

    candidate_id = val("candidate_id")
    review_note = val("review_note", "由派工資料建立新客戶並綁定")

    if not candidate_id:
        return _TicketLinkResponse(
            content=_ticket_link_json.dumps({"ok": False, "error": "缺少 candidate_id"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    with _ticket_link_engine.begin() as conn:
        candidate = conn.execute(
            _ticket_link_sql_text("""
                SELECT
                    id,
                    ticket_id,
                    ticket_no,
                    customer_name,
                    contact_phone,
                    service_address
                FROM ticket_customer_candidates
                WHERE id = :id
                LIMIT 1
            """),
            {"id": candidate_id},
        ).mappings().first()

        if not candidate:
            return _TicketLinkResponse(
                content=_ticket_link_json.dumps({"ok": False, "error": "找不到候選資料"}, ensure_ascii=False),
                media_type="application/json; charset=utf-8",
                status_code=404,
            )

        # 產生下一個 customer_no
        last_no = conn.execute(
            _ticket_link_sql_text("""
                SELECT customer_no
                FROM customer_accounts
                WHERE customer_no LIKE 'C%'
                ORDER BY customer_no DESC
                LIMIT 1
            """)
        ).scalar()

        try:
            next_number = int(str(last_no or "C000000")[1:]) + 1
        except Exception:
            next_number = 1

        customer_no = "C" + str(next_number).zfill(6)

        service_address = candidate["service_address"] or ""
        if service_address and not service_address.startswith("透天"):
            service_address = "透天 " + service_address

        conn.execute(
            _ticket_link_sql_text("""
                INSERT INTO customer_accounts (
                    customer_no,
                    customer_name,
                    customer_phone,
                    customer_type,
                    building_no,
                    floor_text,
                    room_no,
                    service_address,
                    service_type,
                    package_name,
                    monthly_fee,
                    install_date,
                    contract_status,
                    account_status,
                    payment_method,
                    billing_day,
                    arrears_status,
                    equipment_no,
                    cm_mac,
                    ip_address,
                    signal_note,
                    billing_note,
                    service_note,
                    created_at,
                    updated_at
                )
                VALUES (
                    :customer_no,
                    :customer_name,
                    :customer_phone,
                    '派工建立',
                    'HOUSE',
                    '',
                    '',
                    :service_address,
                    '',
                    '',
                    0,
                    '',
                    '待確認',
                    '待確認',
                    '',
                    0,
                    '待確認',
                    '',
                    '',
                    '',
                    '',
                    '由派工案件建立，尚未設定帳務服務。',
                    '由派工案件 ' || :ticket_no || ' 建立。',
                    datetime('now'),
                    datetime('now')
                )
            """),
            {
                "customer_no": customer_no,
                "customer_name": candidate["customer_name"] or "未命名客戶",
                "customer_phone": candidate["contact_phone"] or "",
                "service_address": service_address,
                "ticket_no": candidate["ticket_no"] or "",
            },
        )

        conn.execute(
            _ticket_link_sql_text("""
                UPDATE tickets
                SET customer_no = :customer_no,
                    building_no = '透天'
                WHERE id = :ticket_id
            """),
            {
                "customer_no": customer_no,
                "ticket_id": candidate["ticket_id"],
            },
        )

        conn.execute(
            _ticket_link_sql_text("""
                UPDATE ticket_customer_candidates
                SET candidate_customer_no = :customer_no,
                    candidate_building_no = '透天',
                    match_type = 'manual_created_customer',
                    match_score = 100,
                    review_status = '已確認',
                    review_note = :review_note,
                    updated_at = datetime('now')
                WHERE id = :candidate_id
            """),
            {
                "customer_no": customer_no,
                "review_note": review_note,
                "candidate_id": candidate_id,
            },
        )

    return _TicketLinkResponse(
        content=_ticket_link_json.dumps(
            {
                "ok": True,
                "customer_no": customer_no,
                "building_no": "HOUSE",
            },
            ensure_ascii=False,
        ),
        media_type="application/json; charset=utf-8",
    )



@router.get("/admin/ticket-customer-link", response_class=_TicketLinkHTMLResponse)
def admin_ticket_customer_link_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>派工客戶關聯確認｜訊南 ERP</title>
  <style>
    body {
      margin: 0;
      background: #eef3f9;
      color: #102348;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .wrap {
      max-width: 1680px;
      margin: 0 auto;
      padding: 18px;
    }

    .hero {
      border-radius: 22px;
      padding: 22px;
      color: #fff;
      background: linear-gradient(135deg, #0f766e, #2563eb, #7c3aed);
      margin-bottom: 12px;
      box-shadow: 0 16px 44px rgba(15,23,42,.18);
    }

    h1 {
      margin: 0 0 6px;
      font-size: 36px;
      font-weight: 1000;
    }

    .sub {
      font-size: 15px;
      font-weight: 900;
      opacity: .92;
    }

    .toolbar {
      display: grid;
      grid-template-columns: auto auto 160px 1fr auto;
      gap: 8px;
      margin: 12px 0;
      align-items: center;
    }

    button,
    select,
    input {
      height: 34px;
      border-radius: 10px;
      border: 1px solid #cbd5e1;
      padding: 0 10px;
      font-size: 13px;
      font-weight: 900;
      box-sizing: border-box;
    }

    button {
      border: 0;
      background: #365ee8;
      color: #fff;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
    }

    button.gray {
      background: #64748b;
    }

    button.green {
      background: #16a34a;
    }

    .summary {
      color: #475569;
      font-size: 13px;
      font-weight: 900;
      margin: 4px 0 10px;
    }

    .list {
      display: grid;
      gap: 10px;
    }

    .card {
      background: #fff;
      border: 1px solid #d7e1ef;
      border-radius: 18px;
      padding: 12px;
      box-shadow: 0 8px 24px rgba(15,23,42,.06);
    }

    .card.done {
      opacity: .72;
      background: #f8fafc;
    }

    .card-head {
      display: grid;
      grid-template-columns: 180px 1fr 160px;
      gap: 10px;
      align-items: start;
    }

    .ticket-no {
      font-size: 16px;
      font-weight: 1000;
      color: #1d4ed8;
    }

    .main-title {
      font-size: 18px;
      font-weight: 1000;
      color: #102348;
    }

    .muted {
      margin-top: 2px;
      color: #64748b;
      font-size: 12px;
      font-weight: 850;
      line-height: 1.45;
    }

    .pill {
      display: inline-flex;
      justify-content: center;
      align-items: center;
      min-height: 24px;
      padding: 2px 10px;
      border-radius: 999px;
      background: #ffedd5;
      color: #9a3412;
      font-size: 12px;
      font-weight: 1000;
    }

    .pill.done {
      background: #dcfce7;
      color: #166534;
    }

    .link-area {
      margin-top: 10px;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 8px;
    }

    .results {
      margin-top: 8px;
      display: grid;
      gap: 6px;
    }

    .customer-row {
      border: 1px solid #dbe7f5;
      border-radius: 12px;
      padding: 8px;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 8px;
      align-items: center;
      background: #f8fafc;
    }

    .customer-name {
      font-size: 14px;
      font-weight: 1000;
      color: #102348;
    }

    .empty {
      padding: 18px;
      background: #fff;
      border: 1px dashed #cbd5e1;
      border-radius: 16px;
      color: #64748b;
      font-size: 15px;
      font-weight: 1000;
      text-align: center;
    }

    @media (max-width: 760px) {
      .wrap {
        padding: 10px;
      }

      .hero {
        padding: 16px;
      }

      h1 {
        font-size: 28px;
      }

      .toolbar {
        grid-template-columns: 1fr 1fr;
      }

      .toolbar input {
        grid-column: 1 / -1;
      }

      .card-head {
        grid-template-columns: 1fr;
      }

      .link-area {
        grid-template-columns: 1fr;
      }

      .customer-row {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>

<body>
  <div class="wrap">
    <section class="hero">
      <h1>派工客戶關聯確認</h1>
      <div class="sub">只做人工確認，不自動亂接客戶。確認後才寫回 tickets.customer_no / building_no。</div>
    </section>

    <div class="toolbar">
      <button type="button" onclick="history.back()">返回上一頁</button>
      <button type="button" class="gray" onclick="location.href='/?ts=' + Date.now()">回入口</button>

      <select id="status_filter">
        <option value="全部" selected>全部</option>
        <option value="待建立客戶">待建立客戶</option>
        <option value="待人工確認">待人工確認</option>
        <option value="已確認">已確認</option>
      </select>

      <input id="keyword" placeholder="搜尋派工單號 / 客戶名 / 電話 / 地址">

      <button type="button" onclick="loadCandidates()">搜尋</button>
    </div>

    <div id="summary" class="summary">資料載入中...</div>

    <main id="list" class="list"></main>
  </div>

  <script>
    let candidates = [];

    function esc(v) {
      return String(v ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    async function loadCandidates() {
      const params = new URLSearchParams();
      params.set("status", document.getElementById("status_filter").value);
      params.set("q", document.getElementById("keyword").value.trim());
      params.set("ts", Date.now());

      const res = await fetch("/api/admin/ticket-customer-candidates?" + params.toString(), {cache: "no-store"});

      if (!res.ok) {
        document.getElementById("list").innerHTML = '<div class="empty">API 讀取失敗：' + res.status + '</div>';
        return;
      }

      candidates = await res.json();
      renderCandidates();
    }

    function renderCandidates() {
      document.getElementById("summary").textContent = "目前顯示 " + candidates.length + " 筆";

      const box = document.getElementById("list");

      if (!candidates.length) {
        box.innerHTML = '<div class="empty">沒有符合條件的派工案件。</div>';
        return;
      }

      box.innerHTML = candidates.map(function (item) {
        const done = item.review_status === "已確認";

        return `
          <section class="card ${done ? "done" : ""}">
            <div class="card-head">
              <div>
                <div class="ticket-no">${esc(item.ticket_no)}</div>
                <div class="muted">${esc(item.case_type || "-")}｜${esc(item.ticket_status || "-")}</div>
              </div>

              <div>
                <div class="main-title">${esc(item.customer_name || "-")}｜${esc(item.contact_phone || "-")}</div>
                <div class="muted">地址：${esc(item.service_address || "-")}</div>
                <div class="muted">工程師：${esc(item.assigned_engineer || "-")}｜預約：${esc(item.appointment_date || "-")} ${esc(item.appointment_time || "")}</div>
              </div>

              <div>
                <span class="pill ${done ? "done" : ""}">${esc(item.review_status || "-")}</span>
                <div class="muted">目前關聯：${esc(item.linked_customer_no || "未關聯")}</div>
              </div>
            </div>

            ${done ? "" : `
              <div class="link-area">
                <input id="q_${item.candidate_id}" value="${esc(item.customer_name || item.contact_phone || "")}" placeholder="搜尋客戶姓名 / 電話 / 客戶編號 / 地址">
                <button type="button" onclick="searchCustomers(${item.candidate_id})">搜尋客戶</button>
              </div>

              <div id="results_${item.candidate_id}" class="results"></div>
            `}
          </section>
        `;
      }).join("");
    }

    async function searchCustomers(candidateId) {
      const input = document.getElementById("q_" + candidateId);
      const q = input ? input.value.trim() : "";

      const box = document.getElementById("results_" + candidateId);
      box.innerHTML = '<div class="muted">搜尋中...</div>';

      const params = new URLSearchParams();
      params.set("q", q);
      params.set("limit", "20");
      params.set("ts", Date.now());

      const res = await fetch("/api/admin/ticket-customer-candidates/search-customers?" + params.toString(), {cache: "no-store"});

      if (!res.ok) {
        box.innerHTML = '<div class="muted">搜尋失敗：' + res.status + '</div>';
        return;
      }

      const rows = await res.json();

      if (!rows.length) {
        box.innerHTML = `
          <div class="customer-row">
            <div>
              <div class="customer-name">找不到既有客戶</div>
              <div class="muted">可由此派工資料建立一筆新客戶，並直接綁定此派工單。</div>
            </div>
            <button type="button" class="green" onclick="createCustomerAndBind(${candidateId})">建立新客戶並綁定</button>
          </div>
        `;
        return;
      }

      box.innerHTML = rows.map(function (c) {
        return `
          <div class="customer-row">
            <div>
              <div class="customer-name">${esc(c.customer_no)}｜${esc(c.customer_name)}｜${esc(c.customer_phone)}</div>
              <div class="muted">${esc(c.area || "-")}｜${esc(c.building_name || "-")}｜${esc(c.service_address || "-")}</div>
              <div class="muted">狀態：${esc(c.account_status || "-")}｜欠費：${esc(c.arrears_status || "-")}</div>
            </div>

            <button type="button" class="green" onclick="confirmCustomer(${candidateId}, '${esc(c.customer_no)}')">確認綁定</button>
          </div>
        `;
      }).join("");
    }

    async function createCustomerAndBind(candidateId) {
      if (!confirm("確定要由此派工資料建立新客戶，並綁定此派工案件？")) return;

      const body = new URLSearchParams();
      body.set("candidate_id", candidateId);
      body.set("review_note", "由派工資料建立新客戶並綁定");

      const res = await fetch("/api/admin/ticket-customer-candidates/create-customer-and-confirm", {
        method: "POST",
        body: body
      });

      const data = await res.json();

      if (!res.ok || !data.ok) {
        alert(data.error || "建立新客戶失敗");
        return;
      }

      alert("已建立新客戶：" + data.customer_no + "，並完成派工綁定。");
      loadCandidates();
    }


    async function confirmCustomer(candidateId, customerNo) {
      if (!confirm("確定要將此派工案件綁定到客戶 " + customerNo + "？")) return;

      const body = new URLSearchParams();
      body.set("candidate_id", candidateId);
      body.set("customer_no", customerNo);
      body.set("review_note", "人工確認綁定");

      const res = await fetch("/api/admin/ticket-customer-candidates/confirm", {
        method: "POST",
        body: body
      });

      const data = await res.json();

      if (!res.ok || !data.ok) {
        alert(data.error || "確認失敗");
        return;
      }

      alert("已完成綁定");
      loadCandidates();
    }

    document.getElementById("keyword").addEventListener("keydown", function (event) {
      if (event.key === "Enter") loadCandidates();
    });

    document.getElementById("status_filter").addEventListener("change", loadCandidates);

    loadCandidates();
  </script>

  <script src="/static/app_header_actions.js?v=cl17p6"></script>
<script src='/static/xn_theme.js?v=1'></script>
</body>
</html>
"""
# SHINNAN_TICKET_CUSTOMER_LINK_END
