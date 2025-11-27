from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..database import Base


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True, nullable=False)  # Store encrypted for consistency
    code_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts_left = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)


