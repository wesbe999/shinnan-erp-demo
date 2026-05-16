from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    dispatch_area: Mapped[str | None] = mapped_column(String(50), nullable=True, default="未指定")

    case_type: Mapped[str] = mapped_column(String(30), index=True)
    status: Mapped[str] = mapped_column(String(30), default="待派工", index=True)

    customer_name: Mapped[str] = mapped_column(String(100))
    contact_name: Mapped[str] = mapped_column(String(100))
    contact_phone: Mapped[str] = mapped_column(String(50))
    service_address: Mapped[str] = mapped_column(String(255))

    appointment_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    appointment_time: Mapped[str | None] = mapped_column(String(20), nullable=True)
    assigned_engineer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assigned_engineer_staff_code: Mapped[str | None] = mapped_column(String(50), nullable=True, default="")
    customer_no: Mapped[str | None] = mapped_column(String(50), nullable=True, default="")
    building_no: Mapped[str | None] = mapped_column(String(50), nullable=True, default="")

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    internal_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    completion_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    finance_sync_status: Mapped[str] = mapped_column(String(30), default="not_synced")
    external_finance_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    finance_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    extra_fees_data: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer_signature_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    customer_signature_signed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    arrived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    install_detail = relationship(
        "TicketInstallDetail",
        back_populates="ticket",
        uselist=False,
        cascade="all, delete-orphan",
    )

    return_detail = relationship(
        "TicketReturnDetail",
        back_populates="ticket",
        uselist=False,
        cascade="all, delete-orphan",
    )


class TicketInstallDetail(Base):
    __tablename__ = "ticket_install_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), unique=True)

    deposit_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    construction_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    monthly_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    monthly_fee_1: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    monthly_fee_2: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    monthly_fee_3: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    month_count: Mapped[int] = mapped_column(Integer, default=1)
    other_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    other_fee_1: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    other_fee_2: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    other_fee_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    material_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    material_quantity: Mapped[int] = mapped_column(Integer, default=0)

    usage_start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    usage_end_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    usage_month_count: Mapped[int] = mapped_column(Integer, default=0)

    rent_subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    ticket = relationship("Ticket", back_populates="install_detail")


class TicketReturnDetail(Base):
    __tablename__ = "ticket_return_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), unique=True)

    payment_record: Mapped[str | None] = mapped_column(Text, nullable=True)
    deposit_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    refund_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    deduction_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    device_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    cleaning_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    other_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    other_fee_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    returned_device_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    return_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    settlement_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    ticket = relationship("Ticket", back_populates="return_detail")

