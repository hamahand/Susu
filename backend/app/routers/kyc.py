"""
KYC Router

Endpoints for managing KYC verification status.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ..database import get_db
from ..models import User
from ..utils import get_current_user
from ..services.kyc_service import kyc_service
from ..config import settings

router = APIRouter(prefix="/kyc", tags=["KYC Verification"])


class KYCStatusResponse(BaseModel):
    """Response schema for KYC status."""
    verified: bool
    verified_at: Optional[str]
    provider: Optional[str]
    required_for_payments: bool
    message: str


class KYCVerifyResponse(BaseModel):
    """Response schema for KYC verification."""
    success: bool
    verified: bool
    message: str
    provider: Optional[str]


class KYCRequirementsResponse(BaseModel):
    """Response schema for KYC requirements."""
    required: bool
    provider: str
    country: str
    compliance: str
    help_url: str


@router.get("/status", response_model=KYCStatusResponse)
def get_kyc_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's KYC verification status.
    
    Returns:
        KYC status information
    """
    status_info = kyc_service.check_verification_status(current_user)
    
    message = "Verified" if status_info["verified"] else "Not verified"
    if not settings.REQUIRE_KYC_FOR_PAYMENTS:
        message += " (KYC not required)"
    
    return KYCStatusResponse(
        verified=status_info["verified"],
        verified_at=status_info["verified_at"],
        provider=status_info["provider"],
        required_for_payments=status_info["required_for_payments"],
        message=message
    )


@router.post("/verify", response_model=KYCVerifyResponse)
def verify_kyc(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger KYC verification for current user.
    
    Returns:
        Verification result
    """
    # Check if already verified
    if current_user.kyc_verified:
        return KYCVerifyResponse(
            success=True,
            verified=True,
            message="User is already verified",
            provider=current_user.kyc_provider
        )
    
    # Trigger verification
    result = kyc_service.retry_verification(db, current_user.id)
    
    return KYCVerifyResponse(
        success=result.get("success", False),
        verified=result.get("verified", False),
        message=result.get("message", "Verification failed"),
        provider=result.get("provider")
    )


@router.get("/requirements", response_model=KYCRequirementsResponse)
def get_kyc_requirements():
    """
    Get information about KYC requirements.
    
    Returns:
        KYC requirements information
    """
    requirements = kyc_service.get_kyc_requirements()
    
    return KYCRequirementsResponse(
        required=requirements["required"],
        provider=requirements["provider"],
        country=requirements["country"],
        compliance=requirements["compliance"],
        help_url=requirements["help_url"]
    )


@router.post("/admin/bulk-verify")
def bulk_verify_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk verify all unverified users (admin only).
    
    Note: This endpoint should be restricted to admin users in production.
    
    Returns:
        Bulk verification results
    """
    # In production, add admin check here
    # For now, any authenticated user can run this
    
    results = kyc_service.bulk_verify_users(db)
    
    return {
        "message": "Bulk verification complete",
        "total_processed": results["total"],
        "verified": results["verified"],
        "failed": results["failed"],
        "errors": results["errors"][:10]  # Return first 10 errors only
    }

