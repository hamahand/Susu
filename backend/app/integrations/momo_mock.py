import json
import random
import uuid
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path


class InsufficientFundsError(Exception):
    """Exception raised when wallet has insufficient funds."""
    pass


class InvalidAccountError(Exception):
    """Exception raised when account is invalid."""
    pass


class MoMoMockAPI:
    """Mock implementation of MTN Mobile Money API for testing."""
    
    def __init__(self, transactions_file: str = "momo_transactions.json"):
        self.transactions_file = Path(transactions_file)
        self.transactions = self._load_transactions()
        # Mock wallet balances (phone_number -> balance)
        self.wallets: Dict[str, float] = {}
    
    def _load_transactions(self) -> list:
        """Load existing transactions from file."""
        if self.transactions_file.exists():
            with open(self.transactions_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_transactions(self):
        """Save transactions to file."""
        with open(self.transactions_file, 'w') as f:
            json.dump(self.transactions, f, indent=2, default=str)
    
    def _generate_transaction_id(self) -> str:
        """Generate a mock transaction ID."""
        return f"MOMO{uuid.uuid4().hex[:12].upper()}"
    
    def _get_wallet_balance(self, phone_number: str) -> float:
        """Get wallet balance (mock implementation)."""
        if phone_number not in self.wallets:
            # Initialize with random balance between 100-1000 for testing
            self.wallets[phone_number] = random.uniform(100, 1000)
        return self.wallets[phone_number]
    
    def _simulate_failure(self) -> bool:
        """Simulate random 10% failure rate."""
        return random.random() < 0.1
    
    def validate_account(self, phone_number: str) -> Dict:
        """
        Validate if a phone number has a MoMo account.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            Dict with account status
            
        Raises:
            InvalidAccountError: If account is invalid
        """
        # Mock: Accept all phone numbers with Ghana format (+233...)
        if phone_number.startswith('+233') and len(phone_number) >= 13:
            return {
                "valid": True,
                "account_name": f"User {phone_number[-4:]}",
                "account_number": phone_number
            }
        
        raise InvalidAccountError(f"Invalid MoMo account: {phone_number}")
    
    def debit_wallet(self, phone_number: str, amount: float, reference: str = "") -> str:
        """
        Debit amount from user's wallet.
        
        Args:
            phone_number: User's phone number
            amount: Amount to debit
            reference: Payment reference
            
        Returns:
            Transaction ID
            
        Raises:
            InsufficientFundsError: If wallet has insufficient funds
            InvalidAccountError: If account is invalid
        """
        # Validate account
        self.validate_account(phone_number)
        
        # Simulate random failures
        if self._simulate_failure():
            transaction = {
                "transaction_id": None,
                "type": "debit",
                "phone_number": phone_number,
                "amount": amount,
                "status": "failed",
                "reason": "Network error or insufficient funds",
                "reference": reference,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.transactions.append(transaction)
            self._save_transactions()
            raise InsufficientFundsError("Simulated payment failure")
        
        # Check balance
        balance = self._get_wallet_balance(phone_number)
        if balance < amount:
            transaction = {
                "transaction_id": None,
                "type": "debit",
                "phone_number": phone_number,
                "amount": amount,
                "status": "failed",
                "reason": "Insufficient funds",
                "balance": balance,
                "reference": reference,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.transactions.append(transaction)
            self._save_transactions()
            raise InsufficientFundsError(f"Insufficient funds. Balance: {balance}, Required: {amount}")
        
        # Process debit
        self.wallets[phone_number] = balance - amount
        transaction_id = self._generate_transaction_id()
        
        transaction = {
            "transaction_id": transaction_id,
            "type": "debit",
            "phone_number": phone_number,
            "amount": amount,
            "status": "success",
            "new_balance": self.wallets[phone_number],
            "reference": reference,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.transactions.append(transaction)
        self._save_transactions()
        
        return transaction_id
    
    def credit_wallet(self, phone_number: str, amount: float, reference: str = "") -> str:
        """
        Credit amount to user's wallet.
        
        Args:
            phone_number: User's phone number
            amount: Amount to credit
            reference: Payment reference
            
        Returns:
            Transaction ID
            
        Raises:
            InvalidAccountError: If account is invalid
        """
        # Validate account
        self.validate_account(phone_number)
        
        # Simulate random failures (lower rate for credits)
        if random.random() < 0.02:  # 2% failure rate for credits
            transaction = {
                "transaction_id": None,
                "type": "credit",
                "phone_number": phone_number,
                "amount": amount,
                "status": "failed",
                "reason": "Network error",
                "reference": reference,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.transactions.append(transaction)
            self._save_transactions()
            raise Exception("Simulated credit failure")
        
        # Process credit
        balance = self._get_wallet_balance(phone_number)
        self.wallets[phone_number] = balance + amount
        transaction_id = self._generate_transaction_id()
        
        transaction = {
            "transaction_id": transaction_id,
            "type": "credit",
            "phone_number": phone_number,
            "amount": amount,
            "status": "success",
            "new_balance": self.wallets[phone_number],
            "reference": reference,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.transactions.append(transaction)
        self._save_transactions()
        
        return transaction_id
    
    def get_transaction(self, transaction_id: str) -> Optional[Dict]:
        """Get transaction details by ID."""
        for txn in self.transactions:
            if txn.get("transaction_id") == transaction_id:
                return txn
        return None


# Singleton instance
momo_api = MoMoMockAPI()

