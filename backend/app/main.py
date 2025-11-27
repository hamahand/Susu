from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, Base
from .routers import auth, groups, payments, payouts, ussd, kyc, admin, notifications
from .cron.scheduler import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print("🚀 Starting SusuSave Backend...")
    
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

