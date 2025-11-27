"""
KYC Service Module

This service layer handles KYC verification orchestration,
combining MTN KYC API calls with database operations.
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import User
from ..integrations.mtn_kyc_integration import mtn_kyc_service
from ..config import settings

logger = logging.getLogger(__name__)


class KYCService:
    """
    Service for managing user KYC verification.
    
    Handles:
    - User verification orchestration
    - Database updates for KYC status
    - Verification status checks
    """
    
    @staticmethod
    def verify_user(db: Session, user_id: int, phone_number: str) -> Dict:
        """
        Verify a user's identity via MTN KYC.
        
        Args:
            db: Database session
            user_id: User ID to verify
            phone_number: User's phone number (unencrypted)
            
        Returns:
            Dict with verification result
        """
        logger.info(f"Starting KYC verification for user {user_id}")
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {
                "success": False,
                "verified": False,
                "message": "User not found"
            }
        
        # If KYC is disabled, mark as verified
        if not settings.ENABLE_MTN_KYC:
            logger.warning("KYC is disabled, auto-verifying user")
            user.kyc_verified = True
            user.kyc_verified_at = datetime.utcnow()
            user.kyc_provider = "disabled"
            db.commit()
            
            return {
                "success": True,
                "verified": True,
                "message": "KYC verification disabled, user auto-verified",
                "provider": "disabled"
            }
        
        # Perform MTN KYC verification
        try:
            verification_result = mtn_kyc_service.perform_kyc_verification(phone_number)
            
            # Update user record
            user.kyc_verified = verification_result.get("verified", False)
            
            if verification_result.get("verified"):
                user.kyc_verified_at = datetime.utcnow()
                user.kyc_provider = verification_result.get("provider", "MTN")
                logger.info(f"User {user_id} verified successfully")
            else:
                user.kyc_verified_at = None
                user.kyc_provider = None
                logger.warning(f"User {user_id} verification failed: {verification_result.get('message')}")
            
            db.commit()
            db.refresh(user)
            
            return {
                "success": True,
                "verified": user.kyc_verified,
                "verified_at": user.kyc_verified_at.isoformat() if user.kyc_verified_at else None,
                "provider": user.kyc_provider,
                "message": verification_result.get("message"),
                "details": verification_result.get("details")
            }
            
        except Exception as e:
            logger.error(f"KYC verification error for user {user_id}: {e}")
            db.rollback()
            
            return {
                "success": False,
                "verified": False,
                "message": f"Verification error: {str(e)}"
            }
    
    @staticmethod
    def check_verification_status(user: User) -> Dict:
        """
        Check if a user is KYC verified.
        
        Args:
            user: User object
            
        Returns:
            Dict with verification status
        """
        return {
            "verified": user.kyc_verified if user else False,
            "verified_at": user.kyc_verified_at.isoformat() if user and user.kyc_verified_at else None,
            "provider": user.kyc_provider if user else None,
            "required_for_payments": settings.REQUIRE_KYC_FOR_PAYMENTS
        }
    
    @staticmethod
    def retry_verification(db: Session, user_id: int) -> Dict:
        """
        Retry KYC verification for a user.
        
        Args:
            db: Database session
            user_id: User ID to re-verify
            
        Returns:
            Dict with verification result
        """
        logger.info(f"Retrying KYC verification for user {user_id}")
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "success": False,
                "verified": False,
                "message": "User not found"
            }
        
        # Get phone number (need to decrypt)
        from ..utils import decrypt_field
        try:
            phone_number = decrypt_field(user.phone_number)
        except Exception as e:
            logger.error(f"Failed to decrypt phone number: {e}")
            return {
                "success": False,
                "verified": False,
                "message": "Failed to decrypt phone number"
            }
        
        # Perform verification
        return KYCService.verify_user(db, user_id, phone_number)
    
    @staticmethod
    def is_user_verified(user: Optional[User]) -> bool:
        """
        Simple check if user is verified.
        
        Args:
            user: User object or None
            
        Returns:
            True if verified, False otherwise
        """
        if not user:
            return False
        
        # If KYC is disabled, all users are considered verified
        if not settings.REQUIRE_KYC_FOR_PAYMENTS:
            return True
        
        return user.kyc_verified
    
    @staticmethod
    def get_kyc_requirements() -> Dict:
        """
        Get KYC requirements information.
        
        Returns:
            Dict with KYC requirements
        """
        return mtn_kyc_service.get_kyc_requirements()
    
    @staticmethod
    def bulk_verify_users(db: Session, user_ids: list = None) -> Dict:
        """
        Verify multiple users in bulk.
        Useful for migrating existing users.
        
        Args:
            db: Database session
            user_ids: List of user IDs to verify (None = all unverified users)
            
        Returns:
            Dict with bulk verification results
        """
        logger.info(f"Starting bulk KYC verification")
        
        # Get users to verify
        query = db.query(User)
        
        if user_ids:
            query = query.filter(User.id.in_(user_ids))
        else:
            # Only verify unverified users
            query = query.filter(User.kyc_verified == False)
        
        users = query.all()
        
        results = {
            "total": len(users),
            "verified": 0,
            "failed": 0,
            "errors": [],
            "details": []
        }
        
        from ..utils import decrypt_field
        
        for user in users:
            try:
                # Decrypt phone number
                phone_number = decrypt_field(user.phone_number)
                
                # Verify user
                result = KYCService.verify_user(db, user.id, phone_number)
                
                if result.get("verified"):
                    results["verified"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "user_id": user.id,
                        "phone": phone_number[-4:],  # Last 4 digits only
                        "message": result.get("message")
                    })
                
                results["details"].append({
                    "user_id": user.id,
                    "verified": result.get("verified"),
                    "message": result.get("message")
                })
                
            except Exception as e:
                logger.error(f"Error verifying user {user.id}: {e}")
                results["failed"] += 1
                results["errors"].append({
                    "user_id": user.id,
                    "message": str(e)
                })
        
        logger.info(f"Bulk verification complete: {results['verified']} verified, {results['failed']} failed")
        return results


# Singleton instance
kyc_service = KYCService()

