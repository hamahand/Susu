"""
Payment preference model for users.

Allows users to choose between automated and manual payment methods.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration."""
    AUTO = "auto"  # Automated monthly deductions (API User auth)
    MANUAL = "manual"  # Manual approval per transaction (bc-authorize/OAuth)
    USSD = "ussd"  # Pay via USSD menu


class PaymentPreference(Base):
    """
    User payment preferences.
    
    Stores how a user prefers to make payments for their susu contributions.
    """
    
    __tablename__ = "payment_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Payment method preference
    payment_method = Column(
        Enum(PaymentMethod), 
        nullable=False, 
        default=PaymentMethod.MANUAL
    )
    
    # Auto-payment settings
    auto_pay_enabled = Column(Boolean, default=False)
    auto_pay_day = Column(Integer, nullable=True)  # Day of month (1-31)
    
    # OAuth/Manual payment settings
    send_payment_reminders = Column(Boolean, default=True)
    reminder_days_before = Column(Integer, default=3)  # Days before due date
    
    # MoMo specific
    momo_consent_given = Column(Boolean, default=False)  # User gave consent for auto-debit
    momo_consent_date = Column(DateTime, nullable=True)
    oauth_auth_req_id = Column(String, nullable=True)  # For bc-authorize flow
    oauth_expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="payment_preference")

