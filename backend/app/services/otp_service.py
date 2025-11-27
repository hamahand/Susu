from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict
import hashlib
import random

from sqlalchemy.orm import Session

from ..models import User
from ..models.otp_code import OtpCode
from ..utils import encrypt_field, decrypt_field


class OTPService:
    """Handles OTP generation, storage and verification (DB-backed)."""

    DEFAULT_TTL_MINUTES = 5
    MAX_PER_15_MIN = 5  # simple rate limit per phone

    @staticmethod
    def _hash_code(code: str) -> str:
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_code(num_digits: int = 6) -> str:
        lower = 10 ** (num_digits - 1)
        upper = (10 ** num_digits) - 1
        return str(random.randint(lower, upper))

    @classmethod
    def create_otp(cls, db: Session, phone_number: str, ttl_minutes: int = DEFAULT_TTL_MINUTES) -> Dict:
        # Simple rate limit: count recent requests in last 15 minutes
        threshold = datetime.utcnow() - timedelta(minutes=15)
        enc_phone = encrypt_field(phone_number)
        recent = db.query(OtpCode).filter(OtpCode.phone_number == enc_phone, OtpCode.created_at >= threshold).count()
        if recent >= cls.MAX_PER_15_MIN:
            raise ValueError("Too many OTP requests. Please try again later.")

        code = cls.generate_code()
        code_hash = cls._hash_code(code)
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)

        otp = OtpCode(
            phone_number=enc_phone,
            code_hash=code_hash,
            expires_at=expires_at,
            attempts_left=5,
        )
        db.add(otp)
        db.commit()

        return {"code": code, "expires_at": expires_at}

    @classmethod
    def verify_otp(cls, db: Session, phone_number: str, code: str) -> bool:
        # Since phone_number is encrypted with Fernet (non-deterministic), we must decrypt all
        all_otps = db.query(OtpCode).order_by(OtpCode.created_at.desc()).all()
        otp = None
        for o in all_otps:
            try:
                if decrypt_field(o.phone_number) == phone_number:
                    otp = o
                    break
            except:
                continue
        
        if not otp or otp.expires_at < datetime.utcnow():
            return False
        if otp.attempts_left <= 0:
            return False

        provided = cls._hash_code(code)
        if provided == otp.code_hash:
            # consume OTP
            db.delete(otp)
            db.commit()
            return True

        # decrement attempts
        otp.attempts_left -= 1
        db.add(otp)
        db.commit()
        return False


