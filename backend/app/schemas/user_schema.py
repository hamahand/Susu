from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from typing import Optional
from ..models.user import UserType


class UserBase(BaseModel):
    """Base user schema."""
    phone_number: str = Field(..., description="User's phone number")
    name: str = Field(..., description="User's full name")
    email: Optional[str] = Field(default=None, description="Optional email address")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: Optional[str] = Field(None, description="Password for app users")
    user_type: UserType = Field(UserType.APP, description="User type")
    payment_method: Optional[str] = Field("manual", description="Payment method: auto, manual, or ussd")


class UserLogin(BaseModel):
    """Schema for user login."""
    phone_number: str
    password: str


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    user_type: UserType
    created_at: datetime
    kyc_verified: bool
    kyc_verified_at: Optional[datetime]
    is_system_admin: Optional[bool] = Field(default=False, description="Whether user is a system administrator")
    admin_role: Optional[str] = Field(default=None, description="Admin role if user is system admin")
    
    @field_serializer('phone_number')
    def decrypt_phone(self, phone_number: str) -> str:
        """Decrypt phone number for response."""
        from ..utils import decrypt_field
        try:
            return decrypt_field(phone_number)
        except:
            return phone_number
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded JWT token data."""
    user_id: Optional[int] = None
    phone_number: Optional[str] = None

