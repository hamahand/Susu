from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, Base
from .routers import auth, groups, payments, payouts, ussd, kyc, admin, notifications
from .cron.scheduler import scheduler


def validate_required_secrets():
    """Validate that required secrets are set and not using default values."""
    errors = []
    
    # Check SECRET_KEY
    if not settings.SECRET_KEY or settings.SECRET_KEY in ["", "your-secret-key-change-in-production"]:
        errors.append("SECRET_KEY is required and must be set via environment variable")
    
    # Check DATABASE_URL
    if not settings.DATABASE_URL or "suspass" in settings.DATABASE_URL:
        errors.append("DATABASE_URL is required and must not use default credentials")
    
    # Check MTN credentials if MTN services are enabled
    if settings.USE_MTN_SERVICES:
        if not settings.MTN_CONSUMER_KEY or not settings.MTN_CONSUMER_SECRET:
            errors.append("MTN_CONSUMER_KEY and MTN_CONSUMER_SECRET are required when USE_MTN_SERVICES=True")
        if settings.ENABLE_MTN_USSD and not settings.MTN_CALLBACK_URL:
            errors.append("MTN_CALLBACK_URL is required when ENABLE_MTN_USSD=True")
    
    if errors:
        error_msg = "\n".join(f"  ❌ {error}" for error in errors)
        raise ValueError(
            f"\n🔒 Security Configuration Error:\n{error_msg}\n\n"
            "Please set required environment variables in your .env file.\n"
            "See backend/env.example for required variables."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print("🚀 Starting SusuSave Backend...")
    
    # Validate required secrets
    validate_required_secrets()
    print("✅ Security configuration validated")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Start scheduler
    scheduler.start()
    
    yield
    
    # Shutdown
    print("🛑 Shutting down SusuSave Backend...")
    scheduler.stop()


# Create FastAPI app
app = FastAPI(
    title="SusuSave API",
    description="Hybrid ROSCA Platform - Mobile App & USSD Interface",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(payments.router)
app.include_router(payouts.router)
app.include_router(ussd.router)
app.include_router(kyc.router)
app.include_router(admin.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to SusuSave API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "SusuSave Backend",
        "scheduler_running": scheduler.scheduler.running if scheduler.scheduler else False
    }

