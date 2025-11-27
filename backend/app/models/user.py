from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base


class UserType(str, enum.Enum):
    """User type enumeration."""
    APP = "app"
    USSD = "ussd"


class AdminRole(str, enum.Enum):
    """Admin role enumeration for system-level administrators."""
    SUPER_ADMIN = "super_admin"
    FINANCE_ADMIN = "finance_admin"
    SUPPORT_ADMIN = "support_admin"


class User(Base):
    """User model representing both mobile app and USSD users."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, nullable=False, index=True)  # Encrypted
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    user_type = Column(Enum(UserType), nullable=False, default=UserType.USSD)
    momo_account_id = Column(String, nullable=True)  # Encrypted, same as phone usually
    password_hash = Column(String, nullable=True)  # Only for app users
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # KYC fields for Ghana compliance
    kyc_verified = Column(Boolean, default=False, nullable=False)
    kyc_verified_at = Column(DateTime, nullable=True)
    kyc_provider = Column(String, nullable=True)  # "MTN", "manual", etc.
    
    # System Admin fields
    is_system_admin = Column(Boolean, default=False, nullable=False)
    admin_role = Column(Enum(AdminRole), nullable=True)  # Only set if is_system_admin=True
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    created_groups = relationship("Group", back_populates="creator", foreign_keys="Group.creator_id")
    memberships = relationship("Membership", back_populates="user")
    payments = relationship("Payment", back_populates="user", foreign_keys="Payment.user_id")
    received_payouts = relationship("Payout", back_populates="recipient")
    payment_preference = relationship("PaymentPreference", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")

