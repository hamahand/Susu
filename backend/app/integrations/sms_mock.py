from datetime import datetime
from pathlib import Path
from typing import Optional


class SMSGateway:
    """Mock SMS gateway for sending notifications."""
    
    def __init__(self, logs_file: str = "sms_logs.txt"):
        self.logs_file = Path(logs_file)
        self.ensure_log_file()
    
    def ensure_log_file(self):
        """Ensure the log file exists."""
        if not self.logs_file.exists():
            self.logs_file.touch()
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send SMS message to a phone number.
        
        Args:
            phone_number: Recipient's phone number
            message: SMS message content
            
        Returns:
            True if sent successfully, False otherwise
        """
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] TO: {phone_number}\nMESSAGE: {message}\n{'-'*80}\n"
        
        # Write to log file
        with open(self.logs_file, 'a') as f:
            f.write(log_entry)
        
        # Also print to console for visibility
        print(f"\n📱 SMS SENT 📱")
        print(f"To: {phone_number}")
        print(f"Message: {message}")
        print(f"Time: {timestamp}\n")
        
        return True
    
    @staticmethod
    def payment_confirmation(phone_number: str, amount: float, group_name: str, transaction_id: str):
        """Send payment confirmation SMS."""
        message = f"Payment confirmed! You paid GHS {amount:.2f} to {group_name}. TxnID: {transaction_id}. Thank you!"
        return sms_gateway.send_sms(phone_number, message)
    
    @staticmethod
    def payment_failure(phone_number: str, amount: float, group_name: str, retry_count: int):
        """Send payment failure notification."""
        message = f"Payment of GHS {amount:.2f} to {group_name} failed. Attempt {retry_count}/3. Please ensure sufficient funds."
        return sms_gateway.send_sms(phone_number, message)
    
    @staticmethod
    def payout_notification(phone_number: str, amount: float, group_name: str, transaction_id: str):
        """Send payout notification SMS."""
        message = f"Congratulations! You received GHS {amount:.2f} from {group_name}. TxnID: {transaction_id}. Funds in your wallet."
        return sms_gateway.send_sms(phone_number, message)
    
    @staticmethod
    def join_confirmation(phone_number: str, group_name: str, first_payment_date: str):
        """Send group join confirmation."""
        message = f"Welcome to {group_name}! Your first payment is due on {first_payment_date}. Dial {phone_number} to check status."
        return sms_gateway.send_sms(phone_number, message)
    
    @staticmethod
    def payment_reminder(phone_number: str, group_name: str, amount: float, due_date: str):
        """Send payment due reminder."""
        message = f"Reminder: Your contribution of GHS {amount:.2f} to {group_name} is due on {due_date}."
        return sms_gateway.send_sms(phone_number, message)
    
    @staticmethod
    def payout_due_notification(phone_number: str, group_name: str, amount: float, date: str):
        """Send notification about upcoming payout."""
        message = f"Good news! You will receive GHS {amount:.2f} from {group_name} on {date}."
        return sms_gateway.send_sms(phone_number, message)


# Singleton instance
sms_gateway = SMSGateway()

