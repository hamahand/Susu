from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base


class GroupStatus(str, enum.Enum):
    """Group status enumeration."""
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"


class Group(Base):
    """Group model representing a ROSCA group."""
    
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    group_code = Column(String(8), unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    contribution_amount = Column(Float, nullable=False)
    num_cycles = Column(Integer, nullable=False)
    current_round = Column(Integer, default=1)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(GroupStatus), default=GroupStatus.ACTIVE)
    cash_only = Column(Boolean, default=False, nullable=False)  # For freemium/cash-only groups
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Privacy settings for member information visibility
    show_alias_to_members = Column(Boolean, default=True, nullable=False)  # Whether to show aliases to non-admins
    show_real_name_to_members = Column(Boolean, default=False, nullable=False)  # Whether to show real names to non-admins
    show_phone_to_members = Column(Boolean, default=False, nullable=False)  # Whether to show phone numbers to non-admins
    
    # Relationships
    creator = relationship("User", back_populates="created_groups", foreign_keys=[creator_id])
    memberships = relationship("Membership", back_populates="group")
    payments = relationship("Payment", back_populates="group")
    payouts = relationship("Payout", back_populates="group")
    notifications = relationship("Notification", back_populates="group")

