from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base


class PayoutStatus(str, enum.Enum):
    """Payout status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    FAILED = "failed"


class Payout(Base):
    """Payout model tracking distributions to members."""
    
    __tablename__ = "payouts"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payout_date = Column(DateTime, nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(Enum(PayoutStatus), default=PayoutStatus.PENDING)
    transaction_id = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    group = relationship("Group", back_populates="payouts")
    recipient = relationship("User", back_populates="received_payouts")

