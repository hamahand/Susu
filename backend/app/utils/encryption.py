from cryptography.fernet import Fernet
from typing import Optional
from ..config import settings


class FieldEncryption:
    """Utility class for encrypting and decrypting sensitive database fields."""
    
    def __init__(self):
        # Generate or load encryption key
        if settings.ENCRYPTION_KEY:
            self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        else:
            # For development, generate a key (in production, this should be from env)
            key = Fernet.generate_key()
            self.cipher = Fernet(key)
    
    def encrypt(self, value: str) -> str:
        """Encrypt a string value."""
        if not value:
            return value
        return self.cipher.encrypt(value.encode()).decode()
    
    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt an encrypted string value."""
        if not encrypted_value:
            return encrypted_value
        return self.cipher.decrypt(encrypted_value.encode()).decode()


# Singleton instance
encryptor = FieldEncryption()


def encrypt_field(value: Optional[str]) -> Optional[str]:
    """Helper function to encrypt a field value."""
    if value is None:
        return None
    return encryptor.encrypt(value)


def decrypt_field(value: Optional[str]) -> Optional[str]:
    """Helper function to decrypt a field value."""
    if value is None:
        return None
    return encryptor.decrypt(value)

