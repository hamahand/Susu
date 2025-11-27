from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..models import User, UserType
from ..schemas import UserCreate, UserLogin, UserResponse, Token
from ..utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    encrypt_field,
    get_current_user
)
from ..integrations.sms_sender import send_sms
from ..services.otp_service import OTPService
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user (for mobile app users).
    """
    # Check if user already exists (decrypt all to compare since Fernet is non-deterministic)
    from ..utils import decrypt_field
    all_users = db.query(User).all()
    for u in all_users:
        try:
            decrypted_phone = decrypt_field(u.phone_number)
            if decrypted_phone == user_data.phone_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this phone number already exists"
                )
        except HTTPException:
            # Re-raise HTTP exceptions (this is our duplicate user error)
            raise
        except Exception as e:
            # Log decryption errors but continue checking other users
            logger.debug(f"Could not decrypt phone for user {u.id}: {e}")
            continue
    
    # Create user
    encrypted_phone = encrypt_field(user_data.phone_number)
    user = User(
        phone_number=encrypted_phone,
        name=user_data.name,
        user_type=user_data.user_type,
        momo_account_id=encrypted_phone,  # Same as phone for now
        password_hash=get_password_hash(user_data.password) if user_data.password else None
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Perform KYC verification
    from ..services.kyc_service import kyc_service
    try:
        kyc_result = kyc_service.verify_user(db, user.id, user_data.phone_number)
        logger.info(f"KYC verification for user {user.id}: {kyc_result.get('message')}")
    except Exception as e:
        logger.error(f"KYC verification failed for user {user.id}: {e}")
        # Continue with registration even if KYC fails
    
    # Set payment preference if provided
    if user_data.payment_method:
        from ..services.dual_payment_service import dual_payment_service
        from ..models import PaymentMethod
        
        # Map string to enum
        method_map = {
            'auto': PaymentMethod.AUTO,
            'manual': PaymentMethod.MANUAL,
            'ussd': PaymentMethod.USSD
        }
        
        payment_method = method_map.get(user_data.payment_method, PaymentMethod.MANUAL)
        
        dual_payment_service.set_payment_preference(
            db=db,
            user_id=user.id,
            payment_method=payment_method,
            auto_pay_day=1 if payment_method == PaymentMethod.AUTO else None,
            send_reminders=True
        )
    
    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login and get JWT access token.
    """
    # Find user by decrypting all phone numbers (Fernet encryption is non-deterministic)
    from ..utils import decrypt_field
    all_users = db.query(User).all()
    user = None
    for u in all_users:
        try:
            decrypted_phone = decrypt_field(u.phone_number)
            if decrypted_phone == credentials.phone_number:
                user = u
                break
        except:
            continue
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not user.password_hash or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "phone_number": credentials.phone_number}
    )
    
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile.
    """
    return current_user


# -------------------------
# OTP-based authentication
# -------------------------


class OTPRequest(BaseModel):
    phone_number: str = Field(..., description="MSISDN with country code, e.g., +256700000001")


class OTPVerify(BaseModel):
    phone_number: str
    code: str = Field(..., min_length=4, max_length=8)


@router.post("/request-otp")
def request_otp(data: OTPRequest, db: Session = Depends(get_db)):
    """
    Request an OTP for phone login. Creates the user if not found.
    Sends OTP via AfricaTalking SMS when enabled, else logs to file.
    """
    # Find or create user by phone (decrypt all due to encryption scheme)
    from ..utils import decrypt_field
    all_users = db.query(User).all()
    user = None
    for u in all_users:
        try:
            if decrypt_field(u.phone_number) == data.phone_number:
                user = u
                break
        except:
            continue
    if not user:
        # Create minimal user for USSD/mobile OTP flow
        encrypted_phone = encrypt_field(data.phone_number)
        user = User(
            phone_number=encrypted_phone,
            name=f"User {data.phone_number[-4:]}",
            user_type=UserType.USSD,
            momo_account_id=encrypted_phone
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Perform KYC verification for new USSD user
        from ..services.kyc_service import kyc_service
        try:
            kyc_result = kyc_service.verify_user(db, user.id, data.phone_number)
            logger.info(f"KYC verification for USSD user {user.id}: {kyc_result.get('message')}")
        except Exception as e:
            logger.error(f"KYC verification failed for USSD user {user.id}: {e}")

    # Create OTP
    try:
      otp = OTPService.create_otp(db, data.phone_number)
    except ValueError as e:
      raise HTTPException(status_code=429, detail=str(e))

    # Send via SMS (mask code in logs if needed)
    message = f"Your SusuSave login code is {otp['code']}. Expires in 5 minutes."
    send_sms(data.phone_number, message, use_africastalking=settings.ENABLE_REAL_SMS)

    # Masked response
    masked = data.phone_number[:-4] + "****"
    return {"sent_to": masked, "ttl_minutes": OTPService.DEFAULT_TTL_MINUTES}


@router.post("/verify-otp", response_model=Token)
def verify_otp(data: OTPVerify, db: Session = Depends(get_db)):
    """
    Verify OTP and return JWT.
    """
    ok = OTPService.verify_otp(db, data.phone_number, data.code)
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired code")

    # Load user
    from ..utils import decrypt_field
    user = None
    for u in db.query(User).all():
        try:
            if decrypt_field(u.phone_number) == data.phone_number:
                user = u
                break
        except:
            continue
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    token = create_access_token({"sub": str(user.id), "phone_number": data.phone_number})
    return Token(access_token=token)


class ProfileUpdate(BaseModel):
    username: str | None = None
    email: str | None = None


@router.put("/profile", response_model=UserResponse)
def update_profile(data: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update current user's profile (username as name, optional email stored in name extension if model updated later).
    """
    if data.username:
        current_user.name = data.username
    if data.email is not None and hasattr(current_user, "email"):
        setattr(current_user, "email", data.email)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

