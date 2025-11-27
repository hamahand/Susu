"""
Test script for the Group Invitation Feature.

This script tests the complete invitation workflow:
1. Admin invites a member by phone number
2. SMS is sent (mock)
3. Invitee joins group using code
4. Invitation is automatically accepted
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import User, Group, Membership, GroupInvitation, InvitationStatus
from app.services.group_service import GroupService
from app.schemas import GroupCreate, GroupInviteRequest
from app.utils import encrypt_field, decrypt_field
import pytest


def setup_test_data(db: Session):
    """Create test users and group."""
    print("\n🔧 Setting up test data...")
    
    # Create admin user
    admin = User(
        phone_number=encrypt_field("+233201111111"),
        name="Admin User",
        email="admin@test.com",
        user_type="app",
        password_hash="hashed_password"
    )
    db.add(admin)
    db.flush()
    
    # Create invitee user (registered)
    invitee = User(
        phone_number=encrypt_field("+233202222222"),
        name="Invitee User",
        email="invitee@test.com",
        user_type="app",
        password_hash="hashed_password"
    )
    db.add(invitee)
    db.flush()
    
    # Create group with admin
    group_data = GroupCreate(
        name="Test Group",
        contribution_amount=100.0,
        num_cycles=10
    )
    group = GroupService.create_group(db, group_data, admin)
    
    print(f"✅ Created admin user: {admin.name} (ID: {admin.id})")
    print(f"✅ Created invitee user: {invitee.name} (ID: {invitee.id})")
    print(f"✅ Created group: {group.name} (ID: {group.id}, Code: {group.group_code})")
    
    return admin, invitee, group


def test_invite_member(db: Session, admin: User, group: Group, phone_number: str):
    """Test inviting a member to a group."""
    print(f"\n📨 Testing invitation to {phone_number}...")
    
    try:
        invitation = GroupService.invite_member(
            db=db,
            group_id=group.id,
            phone_number=phone_number,
            inviter=admin
        )
        
        print(f"✅ Invitation created:")
        print(f"   - ID: {invitation.id}")
        print(f"   - Status: {invitation.status}")
        print(f"   - Group: {invitation.group_name}")
        print(f"   - Invited by: {invitation.invited_by_name}")
        print(f"   - Phone: {invitation.phone_number}")
        
        return invitation
        
    except Exception as e:
        print(f"❌ Failed to create invitation: {e}")
        raise


def test_get_pending_invitations(db: Session, group: Group):
    """Test getting pending invitations."""
    print(f"\n📋 Getting pending invitations for group {group.id}...")
    
    invitations = GroupService.get_pending_invitations(db, group.id)
    
    print(f"✅ Found {len(invitations)} pending invitation(s)")
    for inv in invitations:
        print(f"   - {inv.phone_number} (Status: {inv.status})")
    
    return invitations


def test_join_group(db: Session, invitee: User, group: Group):
    """Test joining a group (should auto-accept invitation)."""
    print(f"\n🚪 Testing group join for {invitee.name}...")
    
    try:
        membership = GroupService.join_group(db, group.group_code, invitee)
        
        print(f"✅ Successfully joined group:")
        print(f"   - Group ID: {membership.group_id}")
        print(f"   - Rotation Position: {membership.rotation_position}")
        print(f"   - Is Admin: {membership.is_admin}")
        
        return membership
        
    except Exception as e:
        print(f"❌ Failed to join group: {e}")
        raise


def test_invitation_auto_accepted(db: Session, group: Group, phone_number: str):
    """Test that invitation was auto-accepted."""
    print(f"\n✔️  Checking if invitation was auto-accepted...")
    
    encrypted_phone = encrypt_field(phone_number)
    invitation = db.query(GroupInvitation).filter(
        GroupInvitation.group_id == group.id,
        GroupInvitation.phone_number == encrypted_phone
    ).first()
    
    if invitation:
        print(f"✅ Invitation status: {invitation.status}")
        if invitation.status == InvitationStatus.ACCEPTED:
            print(f"   - Accepted at: {invitation.accepted_at}")
            return True
        else:
            print(f"❌ Invitation still {invitation.status}")
            return False
    else:
        print(f"❌ No invitation found for {phone_number}")
        return False


def test_cannot_invite_existing_member(db: Session, admin: User, group: Group, phone_number: str):
    """Test that you cannot invite an existing member."""
    print(f"\n🚫 Testing duplicate invitation (should fail)...")
    
    try:
        invitation = GroupService.invite_member(
            db=db,
            group_id=group.id,
            phone_number=phone_number,
            inviter=admin
        )
        print(f"❌ ERROR: Should not have been able to invite existing member!")
        return False
    except Exception as e:
        print(f"✅ Correctly prevented duplicate invitation: {e}")
        return True


def test_non_admin_cannot_invite(db: Session, invitee: User, group: Group):
    """Test that non-admins cannot invite members."""
    print(f"\n🚫 Testing non-admin invitation (should fail)...")
    
    try:
        invitation = GroupService.invite_member(
            db=db,
            group_id=group.id,
            phone_number="+233203333333",
            inviter=invitee
        )
        print(f"❌ ERROR: Non-admin should not be able to invite!")
        return False
    except Exception as e:
        print(f"✅ Correctly prevented non-admin invitation: {e}")
        return True


def run_all_tests():
    """Run all invitation feature tests."""
    print("=" * 60)
    print("🧪 GROUP INVITATION FEATURE TESTS")
    print("=" * 60)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Setup test data
        admin, invitee, group = setup_test_data(db)
        invitee_phone = decrypt_field(invitee.phone_number)
        
        # Test 1: Invite member
        invitation = test_invite_member(db, admin, group, invitee_phone)
        
        # Test 2: Get pending invitations
        invitations = test_get_pending_invitations(db, group)
        assert len(invitations) == 1, "Should have 1 pending invitation"
        
        # Test 3: Join group (should auto-accept)
        membership = test_join_group(db, invitee, group)
        
        # Test 4: Verify invitation was auto-accepted
        assert test_invitation_auto_accepted(db, group, invitee_phone), "Invitation should be accepted"
        
        # Test 5: No more pending invitations
        invitations = test_get_pending_invitations(db, group)
        assert len(invitations) == 0, "Should have no pending invitations"
        
        # Test 6: Cannot invite existing member
        assert test_cannot_invite_existing_member(db, admin, group, invitee_phone), "Should prevent duplicate"
        
        # Test 7: Non-admin cannot invite
        assert test_non_admin_cannot_invite(db, invitee, group), "Should prevent non-admin invite"
        
        # Test 8: Invite new unregistered user
        print(f"\n📨 Testing invitation to unregistered user...")
        new_user_phone = "+233204444444"
        invitation2 = test_invite_member(db, admin, group, new_user_phone)
        assert invitation2.status == InvitationStatus.PENDING, "Should create pending invitation"
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
        # Cleanup
        db.rollback()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n⚠️  NOTE: This is a test script. It will rollback all changes.\n")
    run_all_tests()

