from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SetAdminRequest(BaseModel):
    """Schema for setting/removing admin role."""
    is_admin: bool


class MembershipResponse(BaseModel):
    """Schema for membership response."""
    id: int
    user_id: int
    group_id: int
    rotation_position: int
    is_admin: bool
    is_active: bool
    join_date: datetime
    
    class Config:
        from_attributes = True

