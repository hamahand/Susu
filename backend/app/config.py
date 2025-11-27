from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://sususer:suspass@localhost:5432/sususave"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ENCRYPTION_KEY: Optional[str] = None  # Fernet key for field encryption
    
    # USSD
    USSD_CODE: str = "*920*55#"
    
    # SMS & MoMo (Mock for now)
    ENABLE_REAL_SMS: bool = False
    ENABLE_REAL_MOMO: bool = False
    SMS_LOGS_PATH: str = "sms_logs.txt"
    MOMO_TRANSACTIONS_PATH: str = "momo_transactions.json"
    
    # Africa's Talking (USSD, SMS, Payments)
    AT_USERNAME: Optional[str] = None
    AT_API_KEY: Optional[str] = None
    AT_ENVIRONMENT: str = "sandbox"  # or "production"
    AT_USSD_SERVICE_CODE: str = "*384*15262#"  # Your AfricaTalking USSD code
    
    # MTN API Settings
    MTN_CONSUMER_KEY: str = "J7SH4tF6QqAsa6VYFhtGRwgpvPjYnF9y"
    MTN_CONSUMER_SECRET: str = "1gBhKETCBKLMyILR"
    MTN_ENVIRONMENT: str = "sandbox"  # or "production"
    MTN_BASE_URL: str = "https://api.mtn.com/v1"
    MTN_USSD_SERVICE_CODE: str = "*920*55#"
    MTN_CALLBACK_URL: str = "https://76280680be24.ngrok-free.app/ussd/callback"
    
    # MTN MoMo Settings
    MTN_MOMO_SUBSCRIPTION_KEY: Optional[str] = None
    MTN_MOMO_API_USER: Optional[str] = None
    MTN_MOMO_API_KEY: Optional[str] = None
    MTN_MOMO_TARGET_ENVIRONMENT: str = "sandbox"  # or "production"
    MTN_MOMO_BASE_URL: str = "https://sandbox.momodeveloper.mtn.com"
    MTN_MOMO_CURRENCY: str = "GHS"  # Ghana Cedis
    
    # Enable/Disable MTN Services
    ENABLE_MTN_USSD: bool = True
    ENABLE_MTN_SMS: bool = True
    ENABLE_MTN_MOMO: bool = True
    USE_MTN_SERVICES: bool = True  # Toggle between MTN and AfricasTalking
    
    # MTN KYC Settings
    ENABLE_MTN_KYC: bool = True
    MTN_KYC_BASE_URL: str = "https://api.mtn.com/v1"
    REQUIRE_KYC_FOR_PAYMENTS: bool = True
    
    # Scheduler
    ENABLE_SCHEDULER: bool = True
    PAYMENT_CHECK_HOUR: int = 6  # 6:00 AM
    RETRY_INTERVAL_HOURS: int = 6
    PAYOUT_CHECK_INTERVAL_HOURS: int = 2
    
    # Redis (for USSD session state)
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS: bool = False  # Use in-memory dict for MVP
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Admin panel
        "http://localhost:8081",  # React Native dev
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

