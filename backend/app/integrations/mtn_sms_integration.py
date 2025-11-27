"""
MTN SMS Integration Module

This module handles integration with MTN's SMS API for Ghana.
Supports sending SMS messages to MTN subscribers.
"""

import requests
import base64
import logging
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..config import settings

logger = logging.getLogger(__name__)


class MTNSMSIntegration:
    """
    Integration with MTN SMS API.
    
    MTN SMS API allows applications to send SMS messages to mobile subscribers.
    """
    
    def __init__(self):
        self.consumer_key = settings.MTN_CONSUMER_KEY
        self.consumer_secret = settings.MTN_CONSUMER_SECRET
        self.base_url = settings.MTN_BASE_URL
        self.environment = settings.MTN_ENVIRONMENT
        self.enabled = settings.ENABLE_MTN_SMS and settings.USE_MTN_SERVICES
        
        # Token caching
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
        logger.info(f"MTN SMS Integration initialized - Environment: {self.environment}")
    
    def _get_access_token(self) -> str:
        """
        Get OAuth access token for MTN API authentication.
        Tokens are cached and refreshed when expired.
        
        Returns:
            Access token string
            
        Raises:
            Exception: If token request fails
        """
        # Return cached token if still valid
        if self._access_token and self._token_expires_at:
            if datetime.utcnow() < self._token_expires_at:
                return self._access_token
        
        # Request new token
        url = f"{self.base_url}/oauth/token"
        
        # Create Basic Auth header
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data.get("access_token")
            
            # Set expiration (usually 3600 seconds, we set it to 50 minutes to be safe)
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 600)
            
            logger.info("Successfully obtained MTN SMS access token")
            return self._access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to obtain MTN access token: {e}")
            raise Exception(f"MTN authentication failed: {e}")
    
    def send_sms(
        self,
        phone_numbers: List[str],
        message: str,
        sender_id: str = "SusuSave"
    ) -> Dict:
        """
        Send SMS message to one or more recipients.
        
        Args:
            phone_numbers: List of recipient phone numbers (with country code, e.g., +233...)
            message: SMS message content (max 160 chars for single SMS)
            sender_id: Sender ID to display (default: "SusuSave")
            
        Returns:
            Response from MTN API with delivery status
            
        Raises:
            Exception: If API request fails
        """
        if not self.enabled:
            logger.warning("MTN SMS is disabled")
            return {
                "status": "disabled",
                "message": "MTN SMS is not enabled",
                "sent": False
            }
        
        # Validate phone numbers
        validated_numbers = []
        for number in phone_numbers:
            if not number.startswith('+'):
                logger.warning(f"Phone number missing country code: {number}")
                # Assume Ghana if no country code
                number = f"+233{number.lstrip('0')}"
            validated_numbers.append(number)
        
        access_token = self._get_access_token()
        
        url = f"{self.base_url}/sms/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Generate unique message ID
        message_id = str(uuid.uuid4())
        
        payload = {
            "senderAddress": sender_id,
            "receiverAddress": validated_numbers,
            "message": message,
            "clientCorrelator": message_id,
            "senderName": sender_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"SMS sent successfully to {len(validated_numbers)} recipient(s)")
            
            return {
                "status": "success",
                "message_id": message_id,
                "recipients": validated_numbers,
                "sent": True,
                "response": result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send SMS: {e}")
            
            return {
                "status": "error",
                "message": str(e),
                "recipients": validated_numbers,
                "sent": False
            }
    
    def send_single_sms(
        self,
        phone_number: str,
        message: str,
        sender_id: str = "SusuSave"
    ) -> Dict:
        """
        Send SMS to a single recipient.
        
        Args:
            phone_number: Recipient phone number
            message: SMS message content
            sender_id: Sender ID to display
            
        Returns:
            Response from MTN API
        """
        return self.send_sms([phone_number], message, sender_id)
    
    def send_bulk_sms(
        self,
        recipients: List[Dict[str, str]],
        sender_id: str = "SusuSave"
    ) -> List[Dict]:
        """
        Send personalized SMS to multiple recipients.
        
        Args:
            recipients: List of dicts with 'phone_number' and 'message' keys
            sender_id: Sender ID to display
            
        Returns:
            List of responses for each SMS sent
        """
        results = []
        
        for recipient in recipients:
            phone_number = recipient.get("phone_number")
            message = recipient.get("message")
            
            if not phone_number or not message:
                logger.warning(f"Invalid recipient data: {recipient}")
                results.append({
                    "status": "error",
                    "message": "Missing phone_number or message",
                    "sent": False
                })
                continue
            
            result = self.send_single_sms(phone_number, message, sender_id)
            results.append(result)
        
        return results
    
    def get_delivery_status(self, message_id: str) -> Optional[Dict]:
        """
        Get delivery status of a sent SMS.
        
        Args:
            message_id: Message ID returned from send_sms
            
        Returns:
            Delivery status information or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            access_token = self._get_access_token()
            
            url = f"{self.base_url}/sms/messages/{message_id}/deliveryStatus"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get delivery status: {e}")
            return None
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format for Ghana.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if valid
        """
        # Remove spaces and hyphens
        clean_number = phone_number.replace(" ", "").replace("-", "")
        
        # Check Ghana format: +233XXXXXXXXX (country code + 9 digits)
        if clean_number.startswith("+233"):
            return len(clean_number) == 13
        
        # Check local format: 0XXXXXXXXX (10 digits)
        if clean_number.startswith("0"):
            return len(clean_number) == 10
        
        return False


# Singleton instance
mtn_sms_service = MTNSMSIntegration()


# Helper functions for common SMS types (compatible with existing code)
def send_payment_confirmation(
    phone_number: str,
    amount: float,
    group_name: str,
    round_number: int
) -> bool:
    """Send payment confirmation SMS via MTN."""
    message = (
        f"Payment confirmed! You paid GHS {amount:.2f} to {group_name}, "
        f"Round {round_number}. Thank you!"
    )
    result = mtn_sms_service.send_single_sms(phone_number, message)
    return result.get("sent", False)


def send_group_welcome(
    phone_number: str,
    group_name: str,
    group_code: str,
    position: int,
    contribution_amount: float
) -> bool:
    """Send welcome SMS when user joins a group."""
    message = (
        f"Welcome to {group_name}! "
        f"Position: {position}. "
        f"Contribution: GHS {contribution_amount}/month. "
        f"Code: {group_code}"
    )
    result = mtn_sms_service.send_single_sms(phone_number, message)
    return result.get("sent", False)


def send_payout_notification(
    phone_number: str,
    amount: float,
    group_name: str,
    round_number: int
) -> bool:
    """Send payout notification SMS."""
    message = (
        f"Congratulations! You received GHS {amount:.2f} from {group_name}, "
        f"Round {round_number}. Check your MoMo account."
    )
    result = mtn_sms_service.send_single_sms(phone_number, message)
    return result.get("sent", False)


def send_payment_reminder(
    phone_number: str,
    group_name: str,
    amount: float,
    round_number: int
) -> bool:
    """Send payment reminder SMS."""
    message = (
        f"Reminder: Please pay GHS {amount:.2f} for {group_name}, "
        f"Round {round_number}. Dial {settings.MTN_USSD_SERVICE_CODE} to pay."
    )
    result = mtn_sms_service.send_single_sms(phone_number, message)
    return result.get("sent", False)

