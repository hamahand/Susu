from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime
from ..database import Base


class AuditLog(Base):
    """Immutable audit log for all financial state changes."""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False, index=True)  # e.g., "payment", "payout"
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String, nullable=False)  # e.g., "create", "update", "approve"
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    performed_by = Column(Integer, nullable=True)  # user_id
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(Text, nullable=True)  # Additional context

