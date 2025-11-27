from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class PaymentType(str, enum.Enum):
    """Payment type enumeration - how payment was actually made."""
    MOMO = "momo"
    CASH = "cash"


class Payment(Base):
    """Payment model tracking member contributions."""
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_type = Column(Enum(PaymentType), default=PaymentType.MOMO)
    marked_paid_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # For cash payments
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="payments", foreign_keys=[user_id])
    group = relationship("Group", back_populates="payments")
    marked_by = relationship("User", foreign_keys=[marked_paid_by])

