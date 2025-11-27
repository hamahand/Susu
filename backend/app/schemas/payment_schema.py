from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..models.payment import PaymentStatus, PaymentType


class PaymentBase(BaseModel):
    """Base payment schema."""
    amount: float = Field(..., gt=0)
    group_id: int


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""
    user_id: int
    round_number: int


class PaymentTrigger(BaseModel):
    """Schema for manually triggering a payment."""
    group_id: int


class PaymentResponse(PaymentBase):
    """Schema for payment response."""
    id: int
    transaction_id: Optional[str]
    user_id: int
    round_number: int
    payment_date: Optional[datetime]
    status: PaymentStatus
    payment_type: PaymentType
    marked_paid_by: Optional[int]
    retry_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentHistory(BaseModel):
    """Schema for payment history."""
    payments: list[PaymentResponse]
    total_paid: float
    total_pending: float


class MarkPaidRequest(BaseModel):
    """Schema for marking payment as cash paid."""
    note: Optional[str] = None


class UnpaidPaymentResponse(BaseModel):
    """Schema for unpaid payment with group context."""
    payment_id: Optional[int]
    group_id: int
    group_name: str
    round_number: int
    amount: float
    is_paid: bool
    is_cash_only: bool
    
    class Config:
        from_attributes = True


class AdminPaymentRequest(BaseModel):
    """Schema for admin requesting payment from a member."""
    group_id: int
    user_id: int
    round_number: int


class PaymentStatusResponse(BaseModel):
    """Schema for payment status response."""
    payment_id: int
    status: PaymentStatus
    mtn_status: Optional[str] = None
    amount: float
    transaction_id: Optional[str] = None
    financial_transaction_id: Optional[str] = None

