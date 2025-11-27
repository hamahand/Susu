from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Membership(Base):
    """Membership model linking users to groups with rotation position."""
    
    __tablename__ = "memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    rotation_position = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    join_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="memberships")
    group = relationship("Group", back_populates="memberships")

