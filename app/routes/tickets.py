from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import Ticket, TicketInstallDetail, TicketReturnDetail
from app.schemas import TicketCreate, TicketOut, TicketStatusUpdate, TicketClaimUpdate


router = APIRouter(prefix="/api/tickets", tags=["案件管理"])


CASE_TYPE_INSTALL = "\u88dd\u6a5f"
CASE_TYPE_REPAIR = "\u7dad\u4fee"
CASE_TYPE_RETURN = "\u9000\u6a5f"
CASE_TYPE_INSPECTION = "\u5de1\u6aa2"
CASE_TYPE_OTHER = "\u5176\u4ed6"
STATUS_UNASSIGNED = "\u5f85\u6d3e\u5de5"
STATUS_CLAIMED = "\u5df2\u9818\u53d6"
STATUS_ARRIVED = "\u5df2\u5230\u5834"
STATUS_DONE = "\u5df2\u5b8c\u6210"


def resolve_staff_code_by_name(db: Session, display_name: str | None) -> str:
    name = str(display_name or "").strip()
    if not name:
        return ""

    row = db.execute(
        text("""
        SELECT staff_code
        FROM employee_accounts
        WHERE display_name = :display_name
        LIMIT 1
        """),
        {"display_name": name},
    ).mappings().first()

    if row:
        return str(row.get("staff_code") or "").strip()

    row = db.execute(
        text("""
        SELECT staff_code
        FROM employee_profiles
        WHERE display_name = :display_name
        LIMIT 1
        """),
        {"display_name": name},
    ).mappings().first()

    return str(row.get("staff_code") or "").strip() if row else ""


def normalize_ticket_datetime_columns(db: Session) -> None:
    db.execute(text("""
        UPDATE tickets
        SET
            arrived_at = NULLIF(arrived_at, ''),
            completed_at = NULLIF(completed_at, ''),
            customer_signature_signed_at = NULLIF(customer_signature_signed_at, '')
        WHERE arrived_at = ''
           OR completed_at = ''
           OR customer_signature_signed_at = ''
    """))
    db.commit()


def generate_ticket_no(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"XN-{today}-"

    existing_numbers = (
        db.query(Ticket.ticket_no)
        .filter(Ticket.ticket_no.like(f"{prefix}%"))
        .all()
    )

    max_seq = 0

    for row in existing_numbers:
        ticket_no = row[0] if isinstance(row, tuple) else row.ticket_no
        try:
            seq = int(str(ticket_no).replace(prefix, ""))
            if seq > max_seq:
                max_seq = seq
        except ValueError:
            continue

    return f"{prefix}{max_seq + 1:04d}"


def normalize_extra_fees(value):
    if value is None:
        return []

    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            return []

    if not isinstance(value, list):
        return []

    result = []

    for item in value:
        if not isinstance(item, dict):
            continue

        name = str(item.get("name") or "").strip()

        try:
            amount = float(item.get("amount") or 0)
        except Exception:
            amount = 0

        if name or amount:
            result.append({
                "name": name,
                "amount": amount,
            })

    return result


def extra_fees_total(value) -> float:
    return sum(float(item.get("amount") or 0) for item in normalize_extra_fees(value))


def _number(value, default=0):
    if value is None:
        return default
    try:
        return float(value)
    except Exception:
        return default


def _int(value, default=1):
    if value is None:
        return default
    try:
        v = int(float(value))
        return v if v > 0 else default
    except Exception:
        return default


def calculate_return_settlement(deposit_amount: float, extra_total: float) -> dict:
    balance = float(deposit_amount or 0) - float(extra_total or 0)

    if balance > 0:
        return {
            "mode": "refund",
            "label": f"退 ${balance:,.0f}",
            "amount": balance,
        }

    if balance < 0:
        return {
            "mode": "collect",
            "label": f"補收 ${abs(balance):,.0f}",
            "amount": abs(balance),
        }

    return {
        "mode": "even",
        "label": "不退不收",
        "amount": 0,
    }


def calculate_install_total(detail: TicketInstallDetail) -> None:
    monthly_fee_1 = _number(getattr(detail, "monthly_fee_1", 0) or getattr(detail, "monthly_fee", 0))
    monthly_fee_2 = _number(getattr(detail, "monthly_fee_2", 0))
    monthly_fee_3 = _number(getattr(detail, "monthly_fee_3", 0))
    month_count = _int(getattr(detail, "month_count", 1), 1)

    rent_subtotal = (monthly_fee_1 + monthly_fee_2 + monthly_fee_3) * month_count

    detail.rent_subtotal = rent_subtotal
    detail.total_amount = (
        _number(getattr(detail, "construction_fee", 0))
        + _number(getattr(detail, "deposit_amount", 0))
        + _number(getattr(detail, "other_fee_1", 0))
        + _number(getattr(detail, "other_fee_2", 0))
        + _number(getattr(detail, "other_fee", 0))
        + rent_subtotal
    )


def calculate_return_total(detail: TicketReturnDetail) -> None:
    detail.total_amount = (
        _number(getattr(detail, "deposit_amount", 0))
        + _number(getattr(detail, "refund_amount", 0))
        - _number(getattr(detail, "deduction_amount", 0))
        - _number(getattr(detail, "device_fee", 0))
        - _number(getattr(detail, "cleaning_fee", 0))
        - _number(getattr(detail, "other_fee", 0))
    )


@router.get(
    "/finance/pending",
    response_model=list[TicketOut],
    tags=["財務串接"],
    summary="查詢待同步財務案件",
)
def list_finance_pending_tickets(db: Session = Depends(get_db)):
    return (
        db.query(Ticket)
        .options(joinedload(Ticket.install_detail), joinedload(Ticket.return_detail))
        .filter(Ticket.finance_sync_status == "pending")
        .order_by(Ticket.id.asc())
        .all()
    )


@router.delete(
    "/test/clear",
    summary="清除測試案件",
    description="開發測試用：清除目前所有案件、裝機明細與退機明細。",
)
def clear_test_tickets(db: Session = Depends(get_db)):
    db.query(TicketInstallDetail).delete()
    db.query(TicketReturnDetail).delete()
    db.query(Ticket).delete()
    db.commit()
    return {
        "status": "ok",
        "message": "測試案件已清除",
    }


@router.post("", response_model=TicketOut, summary="建立派工案件")
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    allowed_case_types = [
        CASE_TYPE_INSTALL,
        CASE_TYPE_RETURN,
        CASE_TYPE_REPAIR,
        CASE_TYPE_INSPECTION,
        CASE_TYPE_OTHER,
    ]

    original_case_type = payload.case_type
    case_type = original_case_type

    if case_type not in allowed_case_types:
        case_type = CASE_TYPE_OTHER

    if original_case_type == CASE_TYPE_INSTALL and payload.install_detail is None:
        raise HTTPException(status_code=400, detail="裝機案件必須提供 install_detail")

    if original_case_type == CASE_TYPE_RETURN and payload.return_detail is None:
        raise HTTPException(status_code=400, detail="退機案件必須提供 return_detail")

    assigned_engineer = (payload.assigned_engineer or "").strip() or None
    assigned_engineer_staff_code = resolve_staff_code_by_name(db, assigned_engineer)

    ticket = Ticket(
        ticket_no=generate_ticket_no(db),
        dispatch_area=payload.dispatch_area or "未指定",
        case_type=case_type,
        customer_name=payload.customer_name,
        contact_name=payload.contact_name,
        contact_phone=payload.contact_phone,
        service_address=payload.service_address,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        assigned_engineer=assigned_engineer,
        assigned_engineer_staff_code=assigned_engineer_staff_code,
        description=payload.description,
        internal_note=payload.internal_note,
        customer_no=payload.customer_no or "",
        building_no=payload.building_no or "",
        extra_fees_data=payload.extra_fees_data,
    )

    db.add(ticket)
    db.flush()

    if original_case_type == CASE_TYPE_INSTALL and payload.install_detail:
        detail = TicketInstallDetail(
            ticket_id=ticket.id,
            **payload.install_detail.model_dump(),
        )
        calculate_install_total(detail)
        db.add(detail)

    if original_case_type == CASE_TYPE_RETURN and payload.return_detail:
        detail = TicketReturnDetail(
            ticket_id=ticket.id,
            **payload.return_detail.model_dump(),
        )
        calculate_return_total(detail)
        db.add(detail)

    db.commit()

    return (
        db.query(Ticket)
        .options(joinedload(Ticket.install_detail), joinedload(Ticket.return_detail))
        .filter(Ticket.id == ticket.id)
        .first()
    )


@router.get("", summary="查詢案件列表")
def list_tickets(db: Session = Depends(get_db)):
    normalize_ticket_datetime_columns(db)

    tickets = (
        db.query(Ticket)
        .options(joinedload(Ticket.install_detail), joinedload(Ticket.return_detail))
        .order_by(Ticket.id.desc())
        .all()
    )

    def safe_date(value):
        return str(value) if value is not None else None

    def safe_number(value):
        if value is None:
            return 0
        try:
            return float(value)
        except Exception:
            return value

    def install_to_dict(detail):
        if detail is None:
            return None

        monthly_fee = safe_number(getattr(detail, "monthly_fee", 0))
        monthly_fee_1 = safe_number(getattr(detail, "monthly_fee_1", 0) or monthly_fee)
        monthly_fee_2 = safe_number(getattr(detail, "monthly_fee_2", 0))
        monthly_fee_3 = safe_number(getattr(detail, "monthly_fee_3", 0))

        return {
            "deposit_amount": safe_number(getattr(detail, "deposit_amount", 0)),
            "construction_fee": safe_number(getattr(detail, "construction_fee", 0)),
            "install_fee": safe_number(getattr(detail, "construction_fee", 0)),

            "monthly_fee": monthly_fee,
            "monthly_fee_1": monthly_fee_1,
            "monthly_fee_2": monthly_fee_2,
            "monthly_fee_3": monthly_fee_3,
            "month_count": safe_number(getattr(detail, "month_count", 1)),

            "rent_subtotal": safe_number(getattr(detail, "rent_subtotal", 0)),
            "other_fee": safe_number(getattr(detail, "other_fee", 0)),
            "other_fee_1": safe_number(getattr(detail, "other_fee_1", 0)),
            "other_fee_2": safe_number(getattr(detail, "other_fee_2", 0)),
            "other_fee_note": getattr(detail, "other_fee_note", "") or "",

            "material_name": getattr(detail, "material_name", "") or "",
            "material_quantity": safe_number(getattr(detail, "material_quantity", 0)),
            "usage_start_date": safe_date(getattr(detail, "usage_start_date", None)),
            "usage_end_date": safe_date(getattr(detail, "usage_end_date", None)),
            "usage_month_count": safe_number(getattr(detail, "usage_month_count", 0)),
            "total_amount": safe_number(getattr(detail, "total_amount", 0)),
        }

    def return_to_dict(detail):
        if detail is None:
            return None

        return {
            "payment_record": getattr(detail, "payment_record", "") or "",
            "deposit_amount": safe_number(getattr(detail, "deposit_amount", 0)),
            "refund_amount": safe_number(getattr(detail, "refund_amount", 0)),
            "deduction_amount": safe_number(getattr(detail, "deduction_amount", 0)),
            "device_fee": safe_number(getattr(detail, "device_fee", 0)),
            "cleaning_fee": safe_number(getattr(detail, "cleaning_fee", 0)),
            "other_fee": safe_number(getattr(detail, "other_fee", 0)),
            "other_fee_note": getattr(detail, "other_fee_note", "") or "",
            "returned_device_status": getattr(detail, "returned_device_status", "") or "",
            "return_note": getattr(detail, "return_note", "") or "",
            "settlement_note": getattr(detail, "settlement_note", "") or "",
            "total_amount": safe_number(getattr(detail, "total_amount", 0)),
        }

    items = []

    for ticket in tickets:
        items.append({
            "id": ticket.id,
            "ticket_no": ticket.ticket_no or "",
            "dispatch_area": ticket.dispatch_area or "",
            "case_type": ticket.case_type or "",
            "status": ticket.status or "",
            "customer_name": ticket.customer_name or "",
            "contact_name": ticket.contact_name or "",
            "contact_phone": ticket.contact_phone or "",
            "service_address": ticket.service_address or "",
            "appointment_date": safe_date(ticket.appointment_date),
            "appointment_time": safe_date(ticket.appointment_time),
            "assigned_engineer": ticket.assigned_engineer or "",
            "assigned_engineer_staff_code": getattr(ticket, "assigned_engineer_staff_code", "") or "",
            "customer_no": getattr(ticket, "customer_no", "") or "",
            "building_no": getattr(ticket, "building_no", "") or "",
            "description": ticket.description or "",
            "internal_note": ticket.internal_note or "",
            "completion_note": ticket.completion_note or "",
            "finance_sync_status": ticket.finance_sync_status or "",
            "external_finance_id": ticket.external_finance_id or "",
            "finance_note": ticket.finance_note or "",
            "extra_fees_data": ticket.extra_fees_data or "",
            "customer_signature_data": ticket.customer_signature_data or "",
            "customer_signature_signed_at": safe_date(ticket.customer_signature_signed_at),
            "created_at": safe_date(ticket.created_at),
            "install_detail": install_to_dict(ticket.install_detail),
            "return_detail": return_to_dict(ticket.return_detail),
        })

    return items


@router.get("/", include_in_schema=False)
def list_tickets_with_trailing_slash(db: Session = Depends(get_db)):
    return list_tickets(db)


@router.patch("/{ticket_id}/claim", response_model=TicketOut, summary="工程師領取案件")
def claim_ticket(
    ticket_id: int,
    payload: TicketClaimUpdate,
    db: Session = Depends(get_db),
):
    normalize_ticket_datetime_columns(db)

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="找不到案件")

    if not payload.assigned_engineer or not payload.assigned_engineer.strip():
        raise HTTPException(status_code=400, detail="領取工程師不可空白")

    assigned_engineer = payload.assigned_engineer.strip()
    ticket.assigned_engineer = assigned_engineer
    ticket.assigned_engineer_staff_code = resolve_staff_code_by_name(db, assigned_engineer)
    ticket.status = "已領取"

    db.commit()

    return (
        db.query(Ticket)
        .options(joinedload(Ticket.install_detail), joinedload(Ticket.return_detail))
        .filter(Ticket.id == ticket_id)
        .first()
    )


@router.patch("/{ticket_id}/mobile-update", response_model=TicketOut, summary="手機版更新案件資料")
def mobile_update_ticket(
    ticket_id: int,
    payload: dict,
    db: Session = Depends(get_db),
):
    normalize_ticket_datetime_columns(db)

    ticket = (
        db.query(Ticket)
        .options(joinedload(Ticket.install_detail), joinedload(Ticket.return_detail))
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if ticket is None:
        raise HTTPException(status_code=404, detail="找不到案件")

    if "appointment_date" in payload:
        ticket.appointment_date = payload.get("appointment_date")

    if "appointment_time" in payload:
        ticket.appointment_time = payload.get("appointment_time")

    if "description" in payload:
        ticket.description = payload.get("description")

    if "extra_fees_data" in payload:
        extra_fees = normalize_extra_fees(payload.get("extra_fees_data"))
        ticket.extra_fees_data = json.dumps(extra_fees, ensure_ascii=False)

        if ticket.return_detail:
            ticket.return_detail.other_fee = extra_fees_total(extra_fees)
            if not ticket.return_detail.deposit_amount:
                ticket.return_detail.deposit_amount = 2000
            calculate_return_total(ticket.return_detail)

    if "customer_signature_data" in payload:
        ticket.customer_signature_data = payload.get("customer_signature_data")
        if payload.get("customer_signature_data"):
            ticket.customer_signature_signed_at = datetime.utcnow()

    install_payload = payload.get("install_detail")
    if install_payload and ticket.install_detail:
        detail = ticket.install_detail

        for field in [
            "deposit_amount",
            "construction_fee",
            "monthly_fee",
            "monthly_fee_1",
            "monthly_fee_2",
            "monthly_fee_3",
            "month_count",
            "other_fee",
            "other_fee_1",
            "other_fee_2",
            "material_quantity",
            "usage_month_count",
        ]:
            if field in install_payload:
                setattr(detail, field, install_payload.get(field) or 0)

        for field in [
            "other_fee_note",
            "material_name",
            "usage_start_date",
            "usage_end_date",
        ]:
            if field in install_payload:
                setattr(detail, field, install_payload.get(field))

        calculate_install_total(detail)

    return_payload = payload.get("return_detail")
    if return_payload and ticket.return_detail:
        detail = ticket.return_detail

        if not detail.deposit_amount:
            detail.deposit_amount = 2000

        for field in [
            "deposit_amount",
            "refund_amount",
            "deduction_amount",
            "device_fee",
            "cleaning_fee",
            "other_fee",
        ]:
            if field in return_payload:
                setattr(detail, field, return_payload.get(field) or 0)

        for field in [
            "payment_record",
            "other_fee_note",
            "returned_device_status",
            "return_note",
            "settlement_note",
        ]:
            if field in return_payload:
                setattr(detail, field, return_payload.get(field))

        calculate_return_total(detail)

    db.commit()

    return (
        db.query(Ticket)
        .options(joinedload(Ticket.install_detail), joinedload(Ticket.return_detail))
        .filter(Ticket.id == ticket_id)
        .first()
    )


@router.get("/{ticket_id}", response_model=TicketOut, summary="查詢單一案件詳情")
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    normalize_ticket_datetime_columns(db)

    ticket = (
        db.query(Ticket)
        .options(joinedload(Ticket.install_detail), joinedload(Ticket.return_detail))
        .filter(Ticket.id == ticket_id)
        .first()
    )
    if ticket is None:
        raise HTTPException(status_code=404, detail="找不到案件")
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketOut, summary="更新案件狀態")
def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    db: Session = Depends(get_db),
):
    normalize_ticket_datetime_columns(db)

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="找不到案件")

    ticket.status = payload.status

    if payload.completion_note is not None:
        ticket.completion_note = payload.completion_note

    if payload.status == "已到場":
        ticket.arrived_at = datetime.utcnow()

    if payload.status == "已完工":
        ticket.completed_at = datetime.utcnow()
        ticket.finance_sync_status = "pending"

    db.commit()

    return (
        db.query(Ticket)
        .options(joinedload(Ticket.install_detail), joinedload(Ticket.return_detail))
        .filter(Ticket.id == ticket_id)
        .first()
    )


@router.delete("/{ticket_id}", summary="刪除派工案件")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    normalize_ticket_datetime_columns(db)

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="找不到案件")

    db.delete(ticket)
    db.commit()

    return {
        "status": "ok",
        "message": "案件已刪除",
        "ticket_id": ticket_id,
    }
