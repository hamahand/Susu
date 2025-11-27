"""
MTN Mobile Money (MoMo) Integration Module

This module handles integration with MTN's MoMo API for Ghana.
Supports Collections (receiving payments) and Disbursements (sending payouts).

MTN MoMo API Documentation: https://momodeveloper.mtn.com/
"""

import requests
import uuid
import logging
from typing import Dict, Optional
from datetime import datetime
from ..config import settings

logger = logging.getLogger(__name__)


class MTNMoMoIntegration:
    """
    Integration with MTN Mobile Money API.
    
    Handles:
    - Collections: Request payments from users
    - Disbursements: Send money to users
    - Transaction status queries
    """
    
    def __init__(self):
        self.base_url = settings.MTN_MOMO_BASE_URL
        self.subscription_key = settings.MTN_MOMO_SUBSCRIPTION_KEY
        self.api_user = settings.MTN_MOMO_API_USER
        self.api_key = settings.MTN_MOMO_API_KEY
        self.target_environment = settings.MTN_MOMO_TARGET_ENVIRONMENT
        self.currency = settings.MTN_MOMO_CURRENCY
        self.enabled = settings.ENABLE_MTN_MOMO and settings.USE_MTN_SERVICES
        
        logger.info(f"MTN MoMo Integration initialized - Environment: {self.target_environment}")
    
    def _get_auth_token(self) -> str:
        """
        Get Bearer token for MoMo API authentication.
        
        Returns:
            Bearer token string
            
        Raises:
            Exception: If token request fails
        """
        if not self.api_user or not self.api_key:
            raise Exception("MTN MoMo API credentials not configured")
        
        url = f"{self.base_url}/collection/token/"
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        }
        
        # Use basic auth with API user and API key
        auth = (self.api_user, self.api_key)
        
        try:
            response = requests.post(url, headers=headers, auth=auth, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            logger.info("Successfully obtained MTN MoMo access token")
            return access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to obtain MTN MoMo token: {e}")
            raise Exception(f"MTN MoMo authentication failed: {e}")
    
    def create_api_user(self) -> Dict:
        """
        Create API user for sandbox environment.
        This is typically done once during setup.
        
        Returns:
            API user information
        """
        url = f"{self.base_url}/v1_0/apiuser"
        
        api_user_id = str(uuid.uuid4())
        
        headers = {
            "X-Reference-Id": api_user_id,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "providerCallbackHost": settings.MTN_CALLBACK_URL.replace("https://", "").replace("http://", "")
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Created API user: {api_user_id}")
            
            return {
                "api_user": api_user_id,
                "status": "created"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create API user: {e}")
            raise Exception(f"Failed to create API user: {e}")
    
    def create_api_key(self, api_user: str) -> str:
        """
        Create API key for an API user (sandbox only).
        
        Args:
            api_user: API user ID
            
        Returns:
            API key
        """
        url = f"{self.base_url}/v1_0/apiuser/{api_user}/apikey"
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            api_key = data.get("apiKey")
            
            logger.info("Created API key successfully")
            return api_key
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create API key: {e}")
            raise Exception(f"Failed to create API key: {e}")
    
    def request_to_pay(
        self,
        phone_number: str,
        amount: float,
        reference: str,
        payer_message: str = "Payment for SusuSave",
        payee_note: str = "Thank you!"
    ) -> Dict:
        """
        Request payment from a user (Collection).
        
        The user will receive a prompt on their phone to approve the payment.
        
        Args:
            phone_number: User's phone number (format: 233XXXXXXXXX, no +)
            amount: Amount to collect
            reference: Your internal reference/transaction ID
            payer_message: Message shown to payer
            payee_note: Note for payee
            
        Returns:
            Dict with transaction details
            
        Raises:
            Exception: If request fails
        """
        if not self.enabled:
            logger.warning("MTN MoMo is disabled")
            return {
                "status": "disabled",
                "message": "MTN MoMo is not enabled"
            }
        
        # Clean phone number (remove + and spaces)
        clean_phone = phone_number.replace("+", "").replace(" ", "").replace("-", "")
        
        # Ensure it starts with country code (233 for Ghana)
        if not clean_phone.startswith("233"):
            if clean_phone.startswith("0"):
                clean_phone = f"233{clean_phone[1:]}"
            else:
                clean_phone = f"233{clean_phone}"
        
        # Generate unique reference ID
        reference_id = str(uuid.uuid4())
        
        access_token = self._get_auth_token()
        
        url = f"{self.base_url}/collection/v1_0/requesttopay"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "amount": str(amount),
            "currency": self.currency,
            "externalId": reference,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": clean_phone
            },
            "payerMessage": payer_message,
            "payeeNote": payee_note
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            
            logger.info(f"Payment request sent: {reference_id}")
            
            return {
                "status": "pending",
                "reference_id": reference_id,
                "external_id": reference,
                "amount": amount,
                "currency": self.currency,
                "phone_number": clean_phone,
                "message": "Payment request sent. User will receive prompt to approve."
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to request payment: {e}")
            
            return {
                "status": "error",
                "message": str(e),
                "reference_id": reference_id,
                "amount": amount
            }
    
    def get_transaction_status(self, reference_id: str) -> Dict:
        """
        Get status of a payment request.
        
        Args:
            reference_id: Reference ID returned from request_to_pay
            
        Returns:
            Transaction status information
        """
        if not self.enabled:
            return {"status": "disabled"}
        
        access_token = self._get_auth_token()
        
        url = f"{self.base_url}/collection/v1_0/requesttopay/{reference_id}"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "status": data.get("status", "unknown").lower(),
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "financial_transaction_id": data.get("financialTransactionId"),
                "external_id": data.get("externalId"),
                "payer": data.get("payer"),
                "reason": data.get("reason")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get transaction status: {e}")
            
            return {
                "status": "error",
                "message": str(e)
            }
    
    def transfer(
        self,
        phone_number: str,
        amount: float,
        reference: str,
        payee_message: str = "Payout from SusuSave",
        payer_note: str = "Congratulations!"
    ) -> Dict:
        """
        Send money to a user (Disbursement).
        
        Args:
            phone_number: Recipient's phone number
            amount: Amount to send
            reference: Your internal reference
            payee_message: Message for recipient
            payer_note: Note from payer
            
        Returns:
            Dict with transfer details
        """
        if not self.enabled:
            logger.warning("MTN MoMo is disabled")
            return {
                "status": "disabled",
                "message": "MTN MoMo is not enabled"
            }
        
        # Clean phone number
        clean_phone = phone_number.replace("+", "").replace(" ", "").replace("-", "")
        
        if not clean_phone.startswith("233"):
            if clean_phone.startswith("0"):
                clean_phone = f"233{clean_phone[1:]}"
            else:
                clean_phone = f"233{clean_phone}"
        
        reference_id = str(uuid.uuid4())
        
        access_token = self._get_auth_token()
        
        url = f"{self.base_url}/disbursement/v1_0/transfer"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "amount": str(amount),
            "currency": self.currency,
            "externalId": reference,
            "payee": {
                "partyIdType": "MSISDN",
                "partyId": clean_phone
            },
            "payerMessage": payer_note,
            "payeeNote": payee_message
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            
            logger.info(f"Transfer initiated: {reference_id}")
            
            return {
                "status": "pending",
                "reference_id": reference_id,
                "external_id": reference,
                "amount": amount,
                "currency": self.currency,
                "phone_number": clean_phone,
                "message": "Transfer initiated successfully."
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to initiate transfer: {e}")
            
            return {
                "status": "error",
                "message": str(e),
                "reference_id": reference_id
            }
    
    def get_account_balance(self) -> Optional[Dict]:
        """
        Get account balance (for collection account).
        
        Returns:
            Balance information
        """
        if not self.enabled:
            return None
        
        try:
            access_token = self._get_auth_token()
            
            url = f"{self.base_url}/collection/v1_0/account/balance"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Target-Environment": self.target_environment,
                "Ocp-Apim-Subscription-Key": self.subscription_key,
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "available_balance": data.get("availableBalance"),
                "currency": data.get("currency")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get account balance: {e}")
            return None
    
    def validate_account(self, phone_number: str) -> Dict:
        """
        Validate if a phone number has an active MoMo account.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            Account validation result
        """
        if not self.enabled:
            return {"valid": False, "message": "MTN MoMo is disabled"}
        
        # Clean phone number
        clean_phone = phone_number.replace("+", "").replace(" ", "").replace("-", "")
        
        if not clean_phone.startswith("233"):
            if clean_phone.startswith("0"):
                clean_phone = f"233{clean_phone[1:]}"
        
        try:
            access_token = self._get_auth_token()
            
            url = f"{self.base_url}/collection/v1_0/accountholder/msisdn/{clean_phone}/active"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Target-Environment": self.target_environment,
                "Ocp-Apim-Subscription-Key": self.subscription_key,
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "valid": data.get("result", False),
                    "phone_number": clean_phone
                }
            else:
                return {
                    "valid": False,
                    "message": "Account not found or inactive"
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to validate account: {e}")
            return {
                "valid": False,
                "message": str(e)
            }


# Singleton instance
mtn_momo_service = MTNMoMoIntegration()


# Helper functions compatible with existing code
class InsufficientFundsError(Exception):
    """Exception raised when wallet has insufficient funds."""
    pass


class InvalidAccountError(Exception):
    """Exception raised when account is invalid."""
    pass


def validate_account(phone_number: str) -> Dict:
    """Validate MoMo account."""
    result = mtn_momo_service.validate_account(phone_number)
    if not result.get("valid"):
        raise InvalidAccountError(f"Invalid MoMo account: {phone_number}")
    return result


def debit_wallet(phone_number: str, amount: float, reference: str = "") -> str:
    """Request payment from user (debit their wallet)."""
    result = mtn_momo_service.request_to_pay(
        phone_number=phone_number,
        amount=amount,
        reference=reference,
        payer_message=f"Payment for {reference}"
    )
    
    if result.get("status") == "error":
        raise InsufficientFundsError(result.get("message", "Payment failed"))
    
    return result.get("reference_id", "")


def credit_wallet(phone_number: str, amount: float, reference: str = "") -> str:
    """Send money to user (credit their wallet)."""
    result = mtn_momo_service.transfer(
        phone_number=phone_number,
        amount=amount,
        reference=reference,
        payee_message=f"Payout: {reference}"
    )
    
    if result.get("status") == "error":
        raise Exception(result.get("message", "Transfer failed"))
    
    return result.get("reference_id", "")


def get_transaction(transaction_id: str) -> Optional[Dict]:
    """Get transaction details."""
    return mtn_momo_service.get_transaction_status(transaction_id)

