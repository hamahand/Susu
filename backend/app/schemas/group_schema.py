from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from ..models.group import GroupStatus
from ..models.invitation import InvitationStatus


class GroupBase(BaseModel):
    """Base group schema."""
    name: str = Field(..., description="Group name")
    contribution_amount: float = Field(..., gt=0, description="Amount per cycle")
    num_cycles: int = Field(..., gt=0, description="Total number of cycles")


class GroupCreate(GroupBase):
    """Schema for creating a new group."""
    cash_only: bool = Field(False, description="If True, group uses cash payments only (no MOMO)")


class MemberInfo(BaseModel):
    """Schema for member information in group."""
    user_id: int
    name: str
    display_name: str  # Real name for admins/self, alias for others
    alias: Optional[str] = None  # Only shown to admins
    phone_number: str
    rotation_position: int
    is_admin: bool
    paid_current_round: bool = False
    
    class Config:
        from_attributes = True


class GroupResponse(GroupBase):
    """Schema for group response."""
    id: int
    group_code: str
    current_round: int
    status: GroupStatus
    cash_only: bool
    creator_id: int
    created_at: datetime
    member_count: Optional[int] = 0
    show_alias_to_members: Optional[bool] = True
    show_real_name_to_members: Optional[bool] = False
    show_phone_to_members: Optional[bool] = False
    
    class Config:
        from_attributes = True


class GroupDashboard(GroupResponse):
    """Schema for group dashboard with detailed stats."""
    total_collected_current_round: float
    members: List[MemberInfo]
    next_recipient: Optional[MemberInfo] = None
    next_payout_date: Optional[datetime] = None


class GroupJoin(BaseModel):
    """Schema for joining a group."""
    group_code: str = Field(..., description="Unique group code")


class RotationUpdate(BaseModel):
    """Schema for updating rotation order."""
    member_positions: List[dict] = Field(..., description="List of {user_id, position}")


class GroupInviteRequest(BaseModel):
    """Schema for inviting a member to a group."""
    phone_number: str = Field(..., description="Phone number of the person to invite (with country code)")


class InvitationResponse(BaseModel):
    """Schema for invitation response."""
    id: int
    group_id: int
    group_name: str
    phone_number: str
    status: InvitationStatus
    invited_by_name: str
    created_at: datetime
    accepted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InvitationAcceptRequest(BaseModel):
    """Schema for accepting an invitation (optional, for explicit acceptance)."""
    invitation_id: int


class GroupPrivacyUpdate(BaseModel):
    """Schema for updating group privacy settings."""
    show_alias_to_members: bool = Field(..., description="Whether to show aliases to non-admin members")
    show_real_name_to_members: bool = Field(..., description="Whether to show real names to non-admin members")
    show_phone_to_members: bool = Field(..., description="Whether to show phone numbers to non-admin members")

