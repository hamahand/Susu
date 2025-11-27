from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import datetime

from ..models import Group, User, Membership, Payment, Payout, GroupStatus, PaymentStatus
from ..models.invitation import GroupInvitation, InvitationStatus
from ..schemas import GroupCreate, MemberInfo, InvitationResponse
from ..utils import generate_group_code, decrypt_field, encrypt_field
from .audit_service import AuditService
from ..integrations.sms_sender import send_group_invitation_existing_user, send_group_invitation_new_user


class GroupService:
    """Service for managing groups."""
    
    @staticmethod
    def create_group(db: Session, group_data: GroupCreate, creator: User) -> Group:
        """
        Create a new ROSCA group.
        
        Args:
            db: Database session
            group_data: Group creation data
            creator: User creating the group
            
        Returns:
            Created group
        """
        # Generate unique group code
        group_code = generate_group_code(db)
        
        # Create group
        group = Group(
            group_code=group_code,
            name=group_data.name,
            contribution_amount=group_data.contribution_amount,
            num_cycles=group_data.num_cycles,
            creator_id=creator.id,
            status=GroupStatus.ACTIVE,
            cash_only=group_data.cash_only,
            current_round=1
        )
        
        db.add(group)
        db.flush()
        
        # Add creator as first member and admin
        membership = Membership(
            user_id=creator.id,
            group_id=group.id,
            rotation_position=1,
            is_admin=True,
            is_active=True
        )
        
        db.add(membership)
        db.commit()
        db.refresh(group)
        
        # Audit log
        AuditService.log(
            db=db,
            entity_type="group",
            entity_id=group.id,
            action="create",
            new_value={"name": group.name, "code": group.group_code},
            performed_by=creator.id
        )
        
        return group
    
    @staticmethod
    def get_group(db: Session, group_id: int) -> Optional[Group]:
        """Get group by ID."""
        return db.query(Group).filter(Group.id == group_id).first()
    
    @staticmethod
    def get_group_by_code(db: Session, group_code: str) -> Optional[Group]:
        """Get group by code."""
        return db.query(Group).filter(Group.group_code == group_code).first()
    
    @staticmethod
    def join_group(db: Session, group_code: str, user: User) -> Membership:
        """
        Join a group using group code.
        
        Args:
            db: Database session
            group_code: Unique group code
            user: User joining the group
            
        Returns:
            Created membership
            
        Raises:
            HTTPException: If group not found or user already a member
        """
        # Find group
        group = GroupService.get_group_by_code(db, group_code)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check if user is already a member
        existing = db.query(Membership).filter(
            Membership.user_id == user.id,
            Membership.group_id == group.id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already a member of this group"
            )
        
        # Check if there's a pending invitation for this user's phone number
        pending_invitation = db.query(GroupInvitation).filter(
            GroupInvitation.group_id == group.id,
            GroupInvitation.phone_number == user.phone_number,
            GroupInvitation.status == InvitationStatus.PENDING
        ).first()
        
        # Validate MoMo account (using mock)
        from ..integrations.momo_mock import momo_api
        try:
            phone = decrypt_field(user.phone_number)
            momo_api.validate_account(phone)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"MoMo account validation failed: {str(e)}"
            )
        
        # Get next rotation position
        max_position = db.query(Membership).filter(
            Membership.group_id == group.id
        ).count()
        
        next_position = max_position + 1
        
        # Create membership
        membership = Membership(
            user_id=user.id,
            group_id=group.id,
            rotation_position=next_position,
            is_admin=False,
            is_active=True
        )
        
        db.add(membership)
        
        # If there was a pending invitation, mark it as accepted
        if pending_invitation:
            pending_invitation.status = InvitationStatus.ACCEPTED
            pending_invitation.accepted_at = datetime.utcnow()
        
        db.commit()
        db.refresh(membership)
        
        # Audit log
        audit_value = {"group_id": group.id, "user_id": user.id, "position": next_position}
        if pending_invitation:
            audit_value["invitation_id"] = pending_invitation.id
            audit_value["via_invitation"] = True
        
        AuditService.log(
            db=db,
            entity_type="membership",
            entity_id=membership.id,
            action="join",
            new_value=audit_value,
            performed_by=user.id
        )
        
        return membership
    
    @staticmethod
    def get_group_members(db: Session, group_id: int, current_round: int, current_user_id: int) -> List[MemberInfo]:
        """
        Get all members of a group with their payment status.
        
        Args:
            db: Database session
            group_id: Group ID
            current_round: Current round number
            current_user_id: ID of the user requesting the data
            
        Returns:
            List of member information with privacy-aware display names
        """
        from ..utils.alias_generator import generate_member_alias
        
        # Get the group to access privacy settings
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check if current user is admin
        current_user_membership = db.query(Membership).filter(
            Membership.user_id == current_user_id,
            Membership.group_id == group_id,
            Membership.is_active == True
        ).first()
        
        is_current_user_admin = current_user_membership and current_user_membership.is_admin
        
        memberships = db.query(Membership).filter(
            Membership.group_id == group_id,
            Membership.is_active == True
        ).order_by(Membership.rotation_position).all()
        
        members = []
        for membership in memberships:
            user = membership.user
            
            # Check if user paid for current round
            payment = db.query(Payment).filter(
                Payment.user_id == user.id,
                Payment.group_id == group_id,
                Payment.round_number == current_round,
                Payment.status == PaymentStatus.SUCCESS
            ).first()
            
            # Generate alias for this user in this group
            alias = generate_member_alias(user.id, group_id)
            
            # Determine what information to show based on privacy settings
            decrypted_phone = decrypt_field(user.phone_number)
            
            if user.id == current_user_id:
                # Current user always sees their own real information
                display_name = user.name
                alias_for_admin = alias if is_current_user_admin else None
                phone_number = decrypted_phone
            elif is_current_user_admin:
                # Admin always sees full information
                display_name = user.name
                alias_for_admin = alias
                phone_number = decrypted_phone
            else:
                # Non-admin sees information based on privacy settings
                # Display name
                if group.show_real_name_to_members:
                    display_name = user.name
                else:
                    display_name = alias
                
                # Alias visibility
                if group.show_alias_to_members:
                    alias_for_admin = alias
                else:
                    alias_for_admin = None
                
                # Phone visibility
                if group.show_phone_to_members:
                    phone_number = decrypted_phone
                else:
                    # Mask phone number: show only country code and last 4 digits
                    if decrypted_phone and len(decrypted_phone) > 4:
                        phone_number = decrypted_phone[:3] + "****" + decrypted_phone[-4:]
                    else:
                        phone_number = "********"
            
            members.append(MemberInfo(
                user_id=user.id,
                name=user.name,
                display_name=display_name,
                alias=alias_for_admin,
                phone_number=phone_number,
                rotation_position=membership.rotation_position,
                is_admin=membership.is_admin,
                paid_current_round=payment is not None
            ))
        
        return members
    
    @staticmethod
    def get_dashboard_data(db: Session, group_id: int, current_user_id: int):
        """
        Get dashboard data for a group.
        
        Args:
            db: Database session
            group_id: Group ID
            current_user_id: ID of the user requesting the data
            
        Returns:
            Dashboard data dictionary
        """
        group = GroupService.get_group(db, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Get members with payment status
        members = GroupService.get_group_members(db, group_id, group.current_round, current_user_id)
        
        # Calculate total collected for current round
        total_collected = db.query(Payment).filter(
            Payment.group_id == group_id,
            Payment.round_number == group.current_round,
            Payment.status == PaymentStatus.SUCCESS
        ).count() * group.contribution_amount
        
        # Get next recipient
        next_recipient = None
        payout = db.query(Payout).filter(
            Payout.group_id == group_id,
            Payout.round_number == group.current_round
        ).first()
        
        if payout:
            recipient_membership = db.query(Membership).filter(
                Membership.user_id == payout.recipient_id,
                Membership.group_id == group_id
            ).first()
            
            if recipient_membership:
                recipient = recipient_membership.user
                
                # Generate alias for next recipient
                from ..utils.alias_generator import generate_member_alias
                alias = generate_member_alias(recipient.id, group_id)
                
                # Check if current user is admin
                current_user_membership = db.query(Membership).filter(
                    Membership.user_id == current_user_id,
                    Membership.group_id == group_id,
                    Membership.is_active == True
                ).first()
                
                is_current_user_admin = current_user_membership and current_user_membership.is_admin
                
                # Determine display name based on privacy rules
                if recipient.id == current_user_id:
                    # Current user always sees their own real name
                    display_name = recipient.name
                    alias_for_admin = alias if is_current_user_admin else None
                elif is_current_user_admin:
                    # Admin sees real names and aliases
                    display_name = recipient.name
                    alias_for_admin = alias
                else:
                    # Non-admin sees aliases for others
                    display_name = alias
                    alias_for_admin = None
                
                next_recipient = MemberInfo(
                    user_id=recipient.id,
                    name=recipient.name,
                    display_name=display_name,
                    alias=alias_for_admin,
                    phone_number=decrypt_field(recipient.phone_number),
                    rotation_position=recipient_membership.rotation_position,
                    is_admin=recipient_membership.is_admin,
                    paid_current_round=False
                )
        
        return {
            "group": group,
            "members": members,
            "total_collected_current_round": total_collected,
            "next_recipient": next_recipient,
            "next_payout_date": payout.payout_date if payout else None
        }
    
    @staticmethod
    def get_user_groups(db: Session, user_id: int) -> List[Group]:
        """Get all groups a user is part of."""
        memberships = db.query(Membership).filter(
            Membership.user_id == user_id,
            Membership.is_active == True
        ).all()
        
        groups = [membership.group for membership in memberships]
        
        # Add member count to each group
        for group in groups:
            group.member_count = db.query(Membership).filter(
                Membership.group_id == group.id,
                Membership.is_active == True
            ).count()
        
        return groups
    
    @staticmethod
    def invite_member(
        db: Session, 
        group_id: int, 
        phone_number: str, 
        inviter: User
    ) -> InvitationResponse:
        """
        Invite a member to join a group.
        
        Args:
            db: Database session
            group_id: ID of the group
            phone_number: Phone number of the person to invite
            inviter: User sending the invitation
            
        Returns:
            InvitationResponse with invitation details
            
        Raises:
            HTTPException: If inviter is not admin, user already member, etc.
        """
        # Get the group
        group = GroupService.get_group(db, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check if inviter is an admin of the group
        membership = db.query(Membership).filter(
            Membership.user_id == inviter.id,
            Membership.group_id == group_id,
            Membership.is_active == True
        ).first()
        
        if not membership or not membership.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only group admins can invite members"
            )
        
        # Encrypt the phone number for storage and lookup
        encrypted_phone = encrypt_field(phone_number)
        
        # Check if user with this phone number is already a member
        existing_user = db.query(User).filter(User.phone_number == encrypted_phone).first()
        if existing_user:
            existing_membership = db.query(Membership).filter(
                Membership.user_id == existing_user.id,
                Membership.group_id == group_id,
                Membership.is_active == True
            ).first()
            
            if existing_membership:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already a member of this group"
                )
        
        # Check if there's already a pending invitation for this phone number
        existing_invitation = db.query(GroupInvitation).filter(
            GroupInvitation.group_id == group_id,
            GroupInvitation.phone_number == encrypted_phone,
            GroupInvitation.status == InvitationStatus.PENDING
        ).first()
        
        if existing_invitation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is already a pending invitation for this phone number"
            )
        
        # Create invitation
        invitation = GroupInvitation(
            group_id=group_id,
            phone_number=encrypted_phone,
            invited_by=inviter.id,
            status=InvitationStatus.PENDING
        )
        
        db.add(invitation)
        db.flush()
        
        # Send SMS invitation
        try:
            if existing_user:
                # User exists - send invitation with inviter's name
                send_group_invitation_existing_user(
                    phone_number=phone_number,
                    inviter_name=inviter.name,
                    group_name=group.name,
                    group_code=group.group_code
                )
            else:
                # New user - send registration invitation
                send_group_invitation_new_user(
                    phone_number=phone_number,
                    group_name=group.name,
                    group_code=group.group_code
                )
        except Exception as e:
            # Log the error but don't fail the invitation
            print(f"Failed to send invitation SMS: {e}")
        
        db.commit()
        db.refresh(invitation)
        
        # Audit log
        AuditService.log(
            db=db,
            entity_type="invitation",
            entity_id=invitation.id,
            action="invite",
            new_value={
                "group_id": group_id,
                "phone_number": phone_number,
                "invited_by": inviter.id
            },
            performed_by=inviter.id
        )
        
        # Build response
        return InvitationResponse(
            id=invitation.id,
            group_id=group.id,
            group_name=group.name,
            phone_number=phone_number,
            status=invitation.status,
            invited_by_name=inviter.name,
            created_at=invitation.created_at,
            accepted_at=invitation.accepted_at
        )
    
    @staticmethod
    def accept_invitation(
        db: Session,
        invitation_id: int,
        user: User
    ) -> Membership:
        """
        Accept an invitation and create membership.
        
        Args:
            db: Database session
            invitation_id: ID of the invitation
            user: User accepting the invitation
            
        Returns:
            Created membership
            
        Raises:
            HTTPException: If invitation not found, already accepted, etc.
        """
        # Get the invitation
        invitation = db.query(GroupInvitation).filter(
            GroupInvitation.id == invitation_id
        ).first()
        
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )
        
        # Check if invitation is pending
        if invitation.status != InvitationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invitation is already {invitation.status}"
            )
        
        # Verify the phone number matches
        if decrypt_field(invitation.phone_number) != decrypt_field(user.phone_number):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This invitation is not for your phone number"
            )
        
        # Check if user is already a member
        existing_membership = db.query(Membership).filter(
            Membership.user_id == user.id,
            Membership.group_id == invitation.group_id,
            Membership.is_active == True
        ).first()
        
        if existing_membership:
            # Update invitation status
            invitation.status = InvitationStatus.ACCEPTED
            invitation.accepted_at = datetime.utcnow()
            db.commit()
            return existing_membership
        
        # Get next rotation position
        max_position = db.query(Membership).filter(
            Membership.group_id == invitation.group_id
        ).count()
        
        next_position = max_position + 1
        
        # Create membership
        membership = Membership(
            user_id=user.id,
            group_id=invitation.group_id,
            rotation_position=next_position,
            is_admin=False,
            is_active=True
        )
        
        db.add(membership)
        
        # Update invitation status
        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = datetime.utcnow()
        
        db.commit()
        db.refresh(membership)
        
        # Send welcome SMS
        group = invitation.group
        phone_number = decrypt_field(user.phone_number)
        from ..integrations.sms_sender import send_group_welcome
        try:
            send_group_welcome(
                phone_number=phone_number,
                group_name=group.name,
                group_code=group.group_code,
                position=next_position,
                contribution_amount=group.contribution_amount
            )
        except Exception as e:
            print(f"Failed to send welcome SMS: {e}")
        
        # Audit log
        AuditService.log(
            db=db,
            entity_type="membership",
            entity_id=membership.id,
            action="accept_invitation",
            new_value={
                "invitation_id": invitation_id,
                "group_id": invitation.group_id,
                "user_id": user.id,
                "position": next_position
            },
            performed_by=user.id
        )
        
        return membership
    
    @staticmethod
    def get_pending_invitations(db: Session, group_id: int) -> List[InvitationResponse]:
        """
        Get all pending invitations for a group.
        
        Args:
            db: Database session
            group_id: ID of the group
            
        Returns:
            List of pending invitations
        """
        invitations = db.query(GroupInvitation).filter(
            GroupInvitation.group_id == group_id,
            GroupInvitation.status == InvitationStatus.PENDING
        ).order_by(GroupInvitation.created_at.desc()).all()
        
        result = []
        for invitation in invitations:
            group = invitation.group
            inviter = invitation.inviter
            
            result.append(InvitationResponse(
                id=invitation.id,
                group_id=group.id,
                group_name=group.name,
                phone_number=decrypt_field(invitation.phone_number),
                status=invitation.status,
                invited_by_name=inviter.name,
                created_at=invitation.created_at,
                accepted_at=invitation.accepted_at
            ))
        
        return result
    
    @staticmethod
    def set_member_admin(
        db: Session,
        group_id: int,
        target_user_id: int,
        is_admin: bool,
        requester_id: int
    ) -> Membership:
        """
        Set or remove admin role for a group member.
        Only the group creator can assign/revoke admin roles.
        
        Args:
            db: Database session
            group_id: ID of the group
            target_user_id: ID of user to modify
            is_admin: True to make admin, False to remove admin
            requester_id: ID of user making the request
            
        Returns:
            Updated membership
            
        Raises:
            HTTPException: If requester is not creator or membership not found
        """
        # Get group
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check if requester is group creator
        if group.creator_id != requester_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the group creator can assign or remove admin roles"
            )
        
        # Get target membership
        membership = db.query(Membership).filter(
            Membership.user_id == target_user_id,
            Membership.group_id == group_id,
            Membership.is_active == True
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this group"
            )
        
        # Can't modify creator's admin status
        if target_user_id == group.creator_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify admin status of group creator"
            )
        
        # Update admin status
        membership.is_admin = is_admin
        db.commit()
        db.refresh(membership)
        
        # Send SMS notification
        user = db.query(User).filter(User.id == target_user_id).first()
        phone = decrypt_field(user.phone_number)
        from ..integrations.sms_mock import SMSGateway
        
        message = (
            f"You have been made an admin of '{group.name}'. "
            f"You can now manage payments and members."
        ) if is_admin else (
            f"Your admin role in '{group.name}' has been removed."
        )
        
        try:
            SMSGateway.send_sms(phone, message)
        except Exception as e:
            print(f"Failed to send admin role SMS: {e}")
        
        # Audit log
        AuditService.log(
            db=db,
            entity_type="membership",
            entity_id=membership.id,
            action="set_admin",
            old_value={"is_admin": not is_admin},
            new_value={"is_admin": is_admin},
            performed_by=requester_id
        )
        
        return membership
    
    @staticmethod
    def update_group_privacy(
        db: Session,
        group_id: int,
        show_alias_to_members: bool,
        show_real_name_to_members: bool,
        show_phone_to_members: bool,
        requester_id: int
    ) -> Group:
        """
        Update privacy settings for a group (admin only).
        
        Args:
            db: Database session
            group_id: Group ID
            show_alias_to_members: Whether to show aliases to non-admins
            show_real_name_to_members: Whether to show real names to non-admins
            show_phone_to_members: Whether to show phone numbers to non-admins
            requester_id: ID of the user requesting the change
            
        Returns:
            Updated group
        """
        # Get group
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Verify requester is an admin of this group
        membership = db.query(Membership).filter(
            Membership.user_id == requester_id,
            Membership.group_id == group_id,
            Membership.is_active == True
        ).first()
        
        if not membership or not membership.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only group admins can update privacy settings"
            )
        
        # Store old values for audit log
        old_values = {
            "show_alias_to_members": group.show_alias_to_members,
            "show_real_name_to_members": group.show_real_name_to_members,
            "show_phone_to_members": group.show_phone_to_members
        }
        
        # Update privacy settings
        group.show_alias_to_members = show_alias_to_members
        group.show_real_name_to_members = show_real_name_to_members
        group.show_phone_to_members = show_phone_to_members
        
        db.commit()
        db.refresh(group)
        
        # Audit log
        AuditService.log(
            db=db,
            entity_type="group",
            entity_id=group.id,
            action="update_privacy",
            old_value=old_values,
            new_value={
                "show_alias_to_members": show_alias_to_members,
                "show_real_name_to_members": show_real_name_to_members,
                "show_phone_to_members": show_phone_to_members
            },
            performed_by=requester_id
        )
        
        return group
