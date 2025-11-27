from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: int
    user_id: int
    group_id: int
    notification_type: str
    message: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for notification list response."""
    notifications: List[NotificationResponse]
    unread_count: int
    total_returned: int
