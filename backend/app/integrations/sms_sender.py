"""
Unified SMS sender that supports MTN, AfricaTalking, and mock integration.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
from ..config import settings

# Try to import AfricaTalking service
try:
    from .africastalking_integration import africastalking_service
    AT_AVAILABLE = True
except ImportError:
    AT_AVAILABLE = False

# Try to import MTN service
try:
    from .mtn_sms_integration import mtn_sms_service
    MTN_AVAILABLE = True
except ImportError:
    MTN_AVAILABLE = False


def send_sms(
    phone_number: str,
    message: str,
    use_africastalking: Optional[bool] = None
) -> bool:
    """
    Send SMS message.
    
    Priority order:
    1. MTN (if USE_MTN_SERVICES is True and configured)
    2. AfricaTalking (if configured and use_africastalking=True)
    3. Mock (logs to file/console)
    
    Args:
        phone_number: Recipient's phone number (with country code)
        message: SMS message content
        use_africastalking: Whether to use AfricaTalking. If None, auto-detects based on config
        
    Returns:
        True if successful
    """
    # Try MTN first if enabled
    if settings.USE_MTN_SERVICES and MTN_AVAILABLE and mtn_sms_service.enabled:
        try:
            result = mtn_sms_service.send_single_sms(phone_number, message)
            if result.get("sent"):
                print(f"✅ SMS sent via MTN to {phone_number}")
                # Log to file for audit trail
                _log_to_file(phone_number, message, "MTN")
                return True
            else:
                print(f"⚠️  MTN SMS failed: {result.get('message')}, falling back...")
        except Exception as e:
            print(f"⚠️  MTN error: {e}, falling back...")
    
    # Auto-detect if not specified
    if use_africastalking is None:
        use_africastalking = settings.ENABLE_REAL_SMS
    
    # Try AfricaTalking if available and enabled
    if use_africastalking and AT_AVAILABLE and africastalking_service.enabled:
        try:
            result = africastalking_service.send_sms([phone_number], message)
            if result.get("SMSMessageData"):
                print(f"✅ SMS sent via AfricaTalking to {phone_number}")
                # Also log to file for audit trail
                _log_to_file(phone_number, message, "AfricaTalking")
                return True
            else:
                print(f"⚠️  AfricaTalking SMS failed, falling back to mock")
        except Exception as e:
            print(f"⚠️  AfricaTalking error: {e}, falling back to mock")
    
    # Fallback to mock
    return _mock_send_sms(phone_number, message)


def _mock_send_sms(phone_number: str, message: str) -> bool:
    """Send mock SMS (logs to file and console)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] To: {phone_number}\nMessage: {message}\n{'-'*50}\n"
    
    # Log to file
    _log_to_file(phone_number, message, "Mock")
    
    # Print to console in development
    print(f"\n📱 SMS Sent (Mock):\n{log_entry}")
    
    return True


def _log_to_file(phone_number: str, message: str, provider: str = "Mock"):
    """Log SMS to file for audit trail."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{provider}] To: {phone_number}\nMessage: {message}\n{'-'*50}\n"
    
    log_path = Path(settings.SMS_LOGS_PATH)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_path, 'a') as f:
        f.write(log_entry)


# Helper functions for common SMS types
def send_payment_confirmation(
    phone_number: str,
    amount: float,
    group_name: str,
    round_number: int
) -> bool:
    """Send payment confirmation SMS."""
    message = (
        f"Payment confirmed! You paid GHS {amount:.2f} to {group_name}, "
        f"Round {round_number}. Thank you!"
    )
    return send_sms(phone_number, message)


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
    return send_sms(phone_number, message)


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
    return send_sms(phone_number, message)


def send_payment_reminder(
    phone_number: str,
    group_name: str,
    amount: float,
    round_number: int
) -> bool:
    """Send payment reminder SMS."""
    ussd_code = settings.MTN_USSD_SERVICE_CODE if settings.USE_MTN_SERVICES else settings.AT_USSD_SERVICE_CODE
    message = (
        f"Reminder: Please pay GHS {amount:.2f} for {group_name}, "
        f"Round {round_number}. Dial {ussd_code} to pay."
    )
    return send_sms(phone_number, message)


def send_group_invitation_existing_user(
    phone_number: str,
    inviter_name: str,
    group_name: str,
    group_code: str
) -> bool:
    """Send invitation SMS to an existing user."""
    ussd_code = settings.MTN_USSD_SERVICE_CODE if settings.USE_MTN_SERVICES else settings.AT_USSD_SERVICE_CODE
    message = (
        f"You've been invited by {inviter_name} to join {group_name}. "
        f"Dial {ussd_code} or use the app with code: {group_code} to accept."
    )
    return send_sms(phone_number, message)


def send_group_invitation_new_user(
    phone_number: str,
    group_name: str,
    group_code: str
) -> bool:
    """Send invitation SMS to a new user who needs to register."""
    ussd_code = settings.MTN_USSD_SERVICE_CODE if settings.USE_MTN_SERVICES else settings.AT_USSD_SERVICE_CODE
    message = (
        f"You've been invited to join {group_name} susu group! "
        f"Register via USSD ({ussd_code}) or download the app, then use code: {group_code} to join."
    )
    return send_sms(phone_number, message)

