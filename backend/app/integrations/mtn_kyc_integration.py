"""
MTN Customer KYC Integration Module

This module handles integration with MTN's KYC API for Ghana.
Supports phone number verification and MoMo account validation for compliance.

MTN KYC API Documentation: https://developers.mtn.com/products/mtn-customer-kyc-api-v1-product
"""

import requests
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from ..config import settings

logger = logging.getLogger(__name__)


class MTNKYCIntegration:
    """
    Integration with MTN Customer KYC API.
    
    Handles:
    - Phone number verification
    - MoMo account validation
    - Customer KYC checks for Ghana compliance
    """
    
    def __init__(self):
        self.base_url = settings.MTN_KYC_BASE_URL
        self.consumer_key = settings.MTN_CONSUMER_KEY
        self.consumer_secret = settings.MTN_CONSUMER_SECRET
        self.environment = settings.MTN_ENVIRONMENT
        self.enabled = settings.ENABLE_MTN_KYC
        
        # Token caching
        self._access_token = None
        self._token_expires_at = None
        
        logger.info(f"MTN KYC Integration initialized - Environment: {self.environment}")
    
    def _get_oauth_token(self) -> str:
        """
        Get OAuth 2.0 Bearer token for MTN API authentication.
        Implements token caching to reduce API calls.
        
        Returns:
            Bearer token string
            
        Raises:
            Exception: If token request fails
        """
        # Return cached token if still valid
        if self._access_token and self._token_expires_at:
            if datetime.utcnow() < self._token_expires_at:
                logger.debug("Using cached OAuth token")
                return self._access_token
        
        if not self.consumer_key or not self.consumer_secret:
            raise Exception("MTN API credentials not configured")
        
        # MTN OAuth 2.0 token endpoint
        url = f"{self.base_url}/oauth/token"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        payload = {
            "grant_type": "client_credentials"
        }
        
        # Use basic auth with consumer key and secret
        auth = (self.consumer_key, self.consumer_secret)
        
        try:
            response = requests.post(url, headers=headers, data=payload, auth=auth, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data.get("access_token")
            
            # Cache token (typically valid for 1 hour, we'll cache for 55 minutes)
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 300)
            
            logger.info("Successfully obtained MTN OAuth token")
            return self._access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to obtain MTN OAuth token: {e}")
            raise Exception(f"MTN authentication failed: {e}")
    
    def verify_phone_number(self, phone_number: str) -> Dict:
        """
        Verify if a phone number is a valid MTN number.
        
        Args:
            phone_number: Phone number to verify (format: 233XXXXXXXXX or +233XXXXXXXXX)
            
        Returns:
            Dict with verification result
        """
        if not self.enabled:
            logger.warning("MTN KYC is disabled")
            return {
                "verified": False,
                "message": "MTN KYC is not enabled",
                "provider": "disabled"
            }
        
        # Clean phone number
        clean_phone = self._clean_phone_number(phone_number)
        
        try:
            access_token = self._get_oauth_token()
            
            # MTN KYC phone verification endpoint
            url = f"{self.base_url}/customer/v1/msisdn/{clean_phone}/verify"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Phone number {clean_phone} verified successfully")
                return {
                    "verified": True,
                    "phone_number": clean_phone,
                    "is_mtn": True,
                    "message": "Phone number verified",
                    "provider": "MTN"
                }
            elif response.status_code == 404:
                logger.warning(f"Phone number {clean_phone} not found in MTN network")
                return {
                    "verified": False,
                    "phone_number": clean_phone,
                    "is_mtn": False,
                    "message": "Phone number not found in MTN network",
                    "provider": "unknown"
                }
            else:
                logger.error(f"Phone verification failed with status {response.status_code}")
                return {
                    "verified": False,
                    "message": f"Verification failed: {response.status_code}",
                    "provider": "error"
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to verify phone number: {e}")
            return {
                "verified": False,
                "message": str(e),
                "provider": "error"
            }
    
    def verify_momo_account(self, phone_number: str) -> Dict:
        """
        Verify if a phone number has an active MoMo account.
        Reuses the MoMo integration's validate_account method.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            Account validation result
        """
        if not self.enabled:
            return {
                "valid": False,
                "has_momo": False,
                "message": "MTN KYC is disabled"
            }
        
        # Import here to avoid circular dependency
        from .mtn_momo_integration import mtn_momo_service
        
        try:
            result = mtn_momo_service.validate_account(phone_number)
            
            return {
                "valid": result.get("valid", False),
                "has_momo": result.get("valid", False),
                "phone_number": result.get("phone_number"),
                "message": result.get("message", "MoMo account validated")
            }
            
        except Exception as e:
            logger.error(f"Failed to verify MoMo account: {e}")
            return {
                "valid": False,
                "has_momo": False,
                "message": str(e)
            }
    
    def perform_kyc_verification(self, phone_number: str) -> Dict:
        """
        Perform complete KYC verification including:
        1. Phone number verification
        2. MoMo account validation
        
        Args:
            phone_number: Phone number to verify
            
        Returns:
            Dict with complete verification status
        """
        if not self.enabled:
            logger.warning("MTN KYC is disabled, verification bypassed")
            return {
                "verified": False,
                "phone_verified": False,
                "momo_verified": False,
                "message": "KYC verification is disabled",
                "provider": "disabled"
            }
        
        logger.info(f"Starting KYC verification for {phone_number}")
        
        # Step 1: Verify phone number
        phone_result = self.verify_phone_number(phone_number)
        phone_verified = phone_result.get("verified", False)
        
        # Step 2: Verify MoMo account
        momo_result = self.verify_momo_account(phone_number)
        momo_verified = momo_result.get("valid", False)
        
        # Overall verification: both checks must pass
        overall_verified = phone_verified and momo_verified
        
        verification_result = {
            "verified": overall_verified,
            "phone_verified": phone_verified,
            "momo_verified": momo_verified,
            "phone_number": self._clean_phone_number(phone_number),
            "provider": "MTN" if overall_verified else phone_result.get("provider", "unknown"),
            "verified_at": datetime.utcnow().isoformat() if overall_verified else None,
            "details": {
                "phone_check": phone_result,
                "momo_check": momo_result
            }
        }
        
        if overall_verified:
            logger.info(f"KYC verification successful for {phone_number}")
            verification_result["message"] = "KYC verification successful"
        else:
            logger.warning(f"KYC verification failed for {phone_number}")
            messages = []
            if not phone_verified:
                messages.append("Phone number verification failed")
            if not momo_verified:
                messages.append("MoMo account validation failed")
            verification_result["message"] = "; ".join(messages)
        
        return verification_result
    
    def _clean_phone_number(self, phone_number: str) -> str:
        """
        Clean and format phone number for MTN API.
        
        Args:
            phone_number: Raw phone number
            
        Returns:
            Cleaned phone number (233XXXXXXXXX format)
        """
        # Remove all non-digit characters
        clean = ''.join(filter(str.isdigit, phone_number))
        
        # Ensure it starts with country code (233 for Ghana)
        if not clean.startswith("233"):
            if clean.startswith("0"):
                clean = f"233{clean[1:]}"
            else:
                clean = f"233{clean}"
        
        return clean
    
    def get_kyc_requirements(self) -> Dict:
        """
        Get information about KYC requirements.
        
        Returns:
            Dict with KYC requirements information
        """
        return {
            "required": settings.REQUIRE_KYC_FOR_PAYMENTS,
            "provider": "MTN",
            "country": "Ghana",
            "checks": [
                {
                    "name": "Phone Verification",
                    "description": "Verify phone number is valid MTN number"
                },
                {
                    "name": "MoMo Account",
                    "description": "Verify active MTN Mobile Money account"
                }
            ],
            "compliance": "Bank of Ghana KYC requirements for financial services",
            "help_url": "https://developers.mtn.com/products/mtn-customer-kyc-api-v1-product"
        }


# Singleton instance
mtn_kyc_service = MTNKYCIntegration()

