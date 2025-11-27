from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..models.payout import PayoutStatus


class PayoutBase(BaseModel):
    """Base payout schema."""
    group_id: int
    round_number: int
    amount: float


class PayoutCreate(PayoutBase):
    """Schema for creating a payout."""
    recipient_id: int


class PayoutApprove(BaseModel):
    """Schema for approving a payout."""
    payout_id: int


class PayoutResponse(PayoutBase):
    """Schema for payout response."""
    id: int
    recipient_id: int
    payout_date: Optional[datetime]
    status: PayoutStatus
    transaction_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PayoutCurrent(PayoutResponse):
    """Schema for current round payout with recipient details."""
    recipient_name: str
    recipient_phone: str

