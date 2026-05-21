from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class InstallDetailCreate(BaseModel):
    deposit_amount: float = 0
    construction_fee: float = 0
    monthly_fee: float = 0
    monthly_fee_1: float = 0
    monthly_fee_2: float = 0
    monthly_fee_3: float = 0
    month_count: int = 1
    other_fee: float = 0
    other_fee_1: float = 0
    other_fee_2: float = 0
    other_fee_note: Optional[str] = None
    material_name: Optional[str] = None
    material_quantity: int = 0
    usage_start_date: Optional[str] = None
    usage_end_date: Optional[str] = None
    usage_month_count: int = 0


class ReturnDetailCreate(BaseModel):
    payment_record: Optional[str] = None
    deposit_amount: float = 0
    refund_amount: float = 0
    deduction_amount: float = 0
    device_fee: float = 0
    cleaning_fee: float = 0
    other_fee: float = 0
    other_fee_note: Optional[str] = None
    returned_device_status: Optional[str] = None
    return_note: Optional[str] = None
    settlement_note: Optional[str] = None

class TicketCreate(BaseModel):
    dispatch_area: Optional[str] = "未指定"
    case_type: str = Field(..., examples=["裝機", "退機", "維修"])
    customer_name: str
    contact_name: str
    contact_phone: str
    service_address: str
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    assigned_engineer: Optional[str] = None
    description: Optional[str] = None
    internal_note: Optional[str] = None
    customer_no: Optional[str] = None
    building_no: Optional[str] = None
    building_name: Optional[str] = None
    extra_fees_data: Optional[str] = None
    install_detail: Optional[InstallDetailCreate] = None
    return_detail: Optional[ReturnDetailCreate] = None


class TicketStatusUpdate(BaseModel):
    status: str
    completion_note: Optional[str] = None


class TicketClaimUpdate(BaseModel):
    assigned_engineer: str


class InstallDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    deposit_amount: float
    construction_fee: float
    monthly_fee: float
    monthly_fee_1: float = 0
    monthly_fee_2: float = 0
    monthly_fee_3: float = 0
    month_count: int
    rent_subtotal: float
    other_fee: float
    other_fee_1: float = 0
    other_fee_2: float = 0
    other_fee_note: Optional[str]
    material_name: Optional[str]
    material_quantity: int
    usage_start_date: Optional[str]
    usage_end_date: Optional[str]
    usage_month_count: int
    total_amount: float

class ReturnDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_record: Optional[str]
    deposit_amount: float
    refund_amount: float = 0
    deduction_amount: float = 0
    device_fee: float = 0
    cleaning_fee: float = 0
    other_fee: float
    other_fee_note: Optional[str]
    returned_device_status: Optional[str]
    return_note: Optional[str]
    settlement_note: Optional[str]
    total_amount: float = 0

class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_no: str
    dispatch_area: Optional[str]
    case_type: str
    status: str
    customer_name: str
    contact_name: str
    contact_phone: str
    service_address: str
    appointment_date: Optional[str]
    appointment_time: Optional[str]
    assigned_engineer: Optional[str]
    assigned_engineer_staff_code: Optional[str] = None
    customer_no: Optional[str] = None
    building_no: Optional[str] = None
    building_name: Optional[str] = None
    description: Optional[str]
    internal_note: Optional[str]
    completion_note: Optional[str]
    finance_sync_status: str
    external_finance_id: Optional[str]
    finance_note: Optional[str]
    extra_fees_data: Optional[str]
    customer_signature_data: Optional[str]
    customer_signature_signed_at: Optional[datetime]
    created_at: datetime
    install_detail: Optional[InstallDetailOut]
    return_detail: Optional[ReturnDetailOut]





