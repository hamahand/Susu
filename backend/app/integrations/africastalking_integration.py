"""
AfricaTalking Integration Module

Provides integration with AfricaTalking API for:
- SMS messaging
- USSD (callback handled in routers/ussd.py)
- Mobile Money (future)

For development, use the sandbox environment.
For production, switch to your live account.
"""

import africastalking
from typing import List, Optional
from ..config import settings


class AfricaTalkingService:
    """Service class for AfricaTalking API integration."""
    
    def __init__(self):
        """Initialize AfricaTalking SDK."""
        # Initialize SDK
        if settings.AT_USERNAME and settings.AT_API_KEY:
            africastalking.initialize(
                username=settings.AT_USERNAME,
                api_key=settings.AT_API_KEY
            )
            
            # Initialize services
            self.sms = africastalking.SMS
            self.payments = africastalking.Payment
            self.ussd = africastalking.USSD
            self.enabled = True
        else:
            self.enabled = False
            print("Warning: AfricaTalking credentials not configured")
    
    def send_sms(
        self,
        phone_numbers: List[str],
        message: str,
        sender_id: Optional[str] = None
    ) -> dict:
        """
        Send SMS message via AfricaTalking.
        
        Args:
            phone_numbers: List of phone numbers (with country code, e.g., +256...)
            message: SMS message content (max 160 chars for single SMS)
            sender_id: Optional sender ID (alphanumeric, max 11 chars)
            
        Returns:
            Response dict from AfricaTalking API
            
        Example:
            >>> service.send_sms(
            ...     phone_numbers=["+256700000001"],
            ...     message="Welcome to SusuSave! Your group code is SUSU1234"
            ... )
        """
        if not self.enabled:
            # Fallback to mock
            print(f"[MOCK SMS] To: {phone_numbers}, Message: {message}")
            return {
                "SMSMessageData": {
                    "Recipients": [
                        {
                            "number": num,
                            "status": "Success",
                            "messageId": "mock-id",
                            "cost": "KES 0.8000"
                        }
                        for num in phone_numbers
                    ]
                }
            }
        
        try:
            # Send SMS
            response = self.sms.send(
                message=message,
                recipients=phone_numbers,
                sender_id=sender_id
            )
            return response
            
        except Exception as e:
            print(f"SMS Error: {str(e)}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def send_group_welcome_sms(
        self,
        phone_number: str,
        group_name: str,
        group_code: str,
        position: int,
        contribution_amount: float
    ):
        """
        Send welcome SMS when user joins a group.
        
        Args:
            phone_number: User's phone number
            group_name: Name of the group
            group_code: Group code
            position: User's rotation position
            contribution_amount: Monthly contribution amount
        """
        message = (
            f"Welcome to {group_name}! "
            f"Your position: {position}. "
            f"Contribution: GHS {contribution_amount}/month. "
            f"Code: {group_code}"
        )
        return self.send_sms([phone_number], message)
    
    def send_payment_confirmation_sms(
        self,
        phone_number: str,
        group_name: str,
        amount: float,
        round_number: int
    ):
        """
        Send payment confirmation SMS.
        
        Args:
            phone_number: User's phone number
            group_name: Name of the group
            amount: Payment amount
            round_number: Round number
        """
        message = (
            f"Payment confirmed! "
            f"GHS {amount} for {group_name}, Round {round_number}. "
            f"Thank you!"
        )
        return self.send_sms([phone_number], message)
    
    def send_payout_notification_sms(
        self,
        phone_number: str,
        group_name: str,
        amount: float,
        round_number: int
    ):
        """
        Send payout notification SMS.
        
        Args:
            phone_number: User's phone number
            group_name: Name of the group
            amount: Payout amount
            round_number: Round number
        """
        message = (
            f"Congratulations! "
            f"You've received GHS {amount} from {group_name}, Round {round_number}. "
            f"Check your MoMo account."
        )
        return self.send_sms([phone_number], message)
    
    def send_payment_reminder_sms(
        self,
        phone_number: str,
        group_name: str,
        amount: float,
        round_number: int
    ):
        """
        Send payment reminder SMS.
        
        Args:
            phone_number: User's phone number
            group_name: Name of the group
            amount: Payment amount due
            round_number: Round number
        """
        message = (
            f"Reminder: Please pay GHS {amount} "
            f"for {group_name}, Round {round_number}. "
            f"Dial {settings.AT_USSD_SERVICE_CODE} to pay."
        )
        return self.send_sms([phone_number], message)


# Global instance
africastalking_service = AfricaTalkingService()

