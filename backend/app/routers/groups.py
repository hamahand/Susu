from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import User, Group
from ..schemas import (
    GroupCreate,
    GroupResponse,
    GroupDashboard,
    GroupJoin,
    RotationUpdate,
    GroupInviteRequest,
    InvitationResponse,
    UnpaidPaymentResponse,
    SetAdminRequest,
    MembershipResponse,
    GroupPrivacyUpdate
)
from ..utils import get_current_user
from ..services import GroupService, PaymentService

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new ROSCA group.
    """
    group = GroupService.create_group(db, group_data, current_user)
    return group


@router.get("/my-groups", response_model=List[GroupResponse])
def get_my_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all groups the current user is part of.
    """
    groups = GroupService.get_user_groups(db, current_user.id)
    return groups


@router.post("/join", status_code=status.HTTP_200_OK)
def join_group(
    join_data: GroupJoin,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Join a group using a group code.
    """
    membership = GroupService.join_group(db, join_data.group_code, current_user)
    return {
        "message": "Successfully joined group",
        "group_id": membership.group_id,
        "rotation_position": membership.rotation_position
    }


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get group details.
    """
    group = GroupService.get_group(db, group_id)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    return group


@router.get("/{group_id}/dashboard")
def get_group_dashboard(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed dashboard data for a group.
    """
    dashboard_data = GroupService.get_dashboard_data(db, group_id, current_user.id)
    return dashboard_data


@router.patch("/{group_id}/rotation")
def update_rotation_order(
    group_id: int,
    rotation_data: RotationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the rotation order for a group (admin only).
    """
    # TODO: Implement rotation update logic
    # This would involve checking if user is admin and updating membership positions
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Rotation update not yet implemented"
    )


@router.post("/{group_id}/invite", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def invite_member(
    group_id: int,
    invite_data: GroupInviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invite a member to join a group (admin only).
    Sends an SMS with the group code to the phone number.
    """
    invitation = GroupService.invite_member(
        db=db,
        group_id=group_id,
        phone_number=invite_data.phone_number,
        inviter=current_user
    )
    return invitation


@router.post("/invitations/{invitation_id}/accept", status_code=status.HTTP_200_OK)
def accept_invitation(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept an invitation to join a group.
    """
    membership = GroupService.accept_invitation(
        db=db,
        invitation_id=invitation_id,
        user=current_user
    )
    return {
        "message": "Successfully accepted invitation",
        "group_id": membership.group_id,
        "rotation_position": membership.rotation_position
    }


@router.get("/{group_id}/invitations", response_model=List[InvitationResponse])
def get_group_invitations(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get pending invitations for a group (admin only).
    """
    # Check if user is an admin of the group
    from ..models import Membership
    membership = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.group_id == group_id,
        Membership.is_active == True
    ).first()
    
    if not membership or not membership.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group admins can view invitations"
        )
    
    invitations = GroupService.get_pending_invitations(db, group_id)
    return invitations


@router.get("/{group_id}/unpaid-payment", response_model=UnpaidPaymentResponse)
def get_unpaid_payment(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get unpaid payment for current user in current round.
    Returns payment details if unpaid, or is_paid=True if already paid.
    """
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Get or create unpaid payment
    payment = PaymentService.get_unpaid_for_user(
        db=db,
        user_id=current_user.id,
        group_id=group_id
    )
    
    if payment is None:
        # Already paid
        return UnpaidPaymentResponse(
            payment_id=None,
            group_id=group.id,
            group_name=group.name,
            round_number=group.current_round,
            amount=group.contribution_amount,
            is_paid=True,
            is_cash_only=group.cash_only
        )
    else:
        # Unpaid
        return UnpaidPaymentResponse(
            payment_id=payment.id,
            group_id=group.id,
            group_name=group.name,
            round_number=payment.round_number,
            amount=payment.amount,
            is_paid=False,
            is_cash_only=group.cash_only
        )


@router.post("/{group_id}/members/{user_id}/set-admin", response_model=MembershipResponse)
def set_member_admin(
    group_id: int,
    user_id: int,
    admin_data: SetAdminRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign or revoke admin role for a group member (creator only).
    """
    membership = GroupService.set_member_admin(
        db=db,
        group_id=group_id,
        target_user_id=user_id,
        is_admin=admin_data.is_admin,
        requester_id=current_user.id
    )
    return membership


@router.patch("/{group_id}/privacy", response_model=GroupResponse)
def update_group_privacy(
    group_id: int,
    privacy_data: GroupPrivacyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update privacy settings for a group (admin only).
    Controls what member information is visible to non-admin members.
    """
    group = GroupService.update_group_privacy(
        db=db,
        group_id=group_id,
        show_alias_to_members=privacy_data.show_alias_to_members,
        show_real_name_to_members=privacy_data.show_real_name_to_members,
        show_phone_to_members=privacy_data.show_phone_to_members,
        requester_id=current_user.id
    )
    return group

