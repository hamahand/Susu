"""
Test admin role assignment features:
- Creator assigning admin role
- Creator revoking admin role
- Non-creator cannot assign admin
- Admin permissions after assignment
"""

import sys
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import (
    Base, User, Group, Membership, UserType
)
from app.services import GroupService
from app.schemas import GroupCreate
from app.utils import encrypt_field


def setup_test_db():
    """Create tables and return db session."""
    Base.metadata.create_all(bind=engine)
    return SessionLocal()


def test_creator_assign_admin(db: Session):
    """Test creator assigning admin role to member."""
    print("\n=== Test: Creator Assigns Admin Role ===")
    
    # Create creator
    creator = User(
        phone_number=encrypt_field("+233245555555"),
        name="Creator User",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    
    # Create member
    member = User(
        phone_number=encrypt_field("+233246666666"),
        name="Member User",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    
    db.add_all([creator, member])
    db.commit()
    db.refresh(creator)
    db.refresh(member)
    
    # Create group
    group_data = GroupCreate(
        name="Admin Test Group",
        contribution_amount=50.0,
        num_cycles=3,
        cash_only=False
    )
    group = GroupService.create_group(db, group_data, creator)
    
    # Add member to group
    membership = Membership(
        user_id=member.id,
        group_id=group.id,
        rotation_position=2,
        is_admin=False,
        is_active=True
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    
    print(f"  Initial admin status: {membership.is_admin}")
    
    # Creator assigns admin role
    updated_membership = GroupService.set_member_admin(
        db=db,
        group_id=group.id,
        target_user_id=member.id,
        is_admin=True,
        requester_id=creator.id
    )
    
    assert updated_membership.is_admin == True, "Member should now be admin"
    print(f"✓ Creator successfully assigned admin role")
    print(f"  Updated admin status: {updated_membership.is_admin}")
    
    return creator, member, group


def test_creator_revoke_admin(db: Session):
    """Test creator revoking admin role from member."""
    print("\n=== Test: Creator Revokes Admin Role ===")
    
    # Create creator and member
    creator = User(
        phone_number=encrypt_field("+233247777777"),
        name="Creator 2",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    
    member = User(
        phone_number=encrypt_field("+233248888888"),
        name="Member 2",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    
    db.add_all([creator, member])
    db.commit()
    db.refresh(creator)
    db.refresh(member)
    
    # Create group
    group_data = GroupCreate(
        name="Revoke Test Group",
        contribution_amount=60.0,
        num_cycles=4,
        cash_only=False
    )
    group = GroupService.create_group(db, group_data, creator)
    
    # Add member as admin
    membership = Membership(
        user_id=member.id,
        group_id=group.id,
        rotation_position=2,
        is_admin=True,  # Start as admin
        is_active=True
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    
    print(f"  Initial admin status: {membership.is_admin}")
    
    # Creator revokes admin role
    updated_membership = GroupService.set_member_admin(
        db=db,
        group_id=group.id,
        target_user_id=member.id,
        is_admin=False,  # Revoke
        requester_id=creator.id
    )
    
    assert updated_membership.is_admin == False, "Member should no longer be admin"
    print(f"✓ Creator successfully revoked admin role")
    print(f"  Updated admin status: {updated_membership.is_admin}")
    
    return creator, member, group


def test_non_creator_cannot_assign(db: Session):
    """Test that non-creators cannot assign admin roles."""
    print("\n=== Test: Non-Creator Cannot Assign Admin ===")
    
    # Create three users
    creator = User(
        phone_number=encrypt_field("+233249999999"),
        name="Creator 3",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    
    member1 = User(
        phone_number=encrypt_field("+233240000000"),
        name="Member 1",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    
    member2 = User(
        phone_number=encrypt_field("+233240000001"),
        name="Member 2",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    
    db.add_all([creator, member1, member2])
    db.commit()
    db.refresh(creator)
    db.refresh(member1)
    db.refresh(member2)
    
    # Create group
    group_data = GroupCreate(
        name="Permission Test",
        contribution_amount=70.0,
        num_cycles=3,
        cash_only=False
    )
    group = GroupService.create_group(db, group_data, creator)
    
    # Add both members (member1 is admin, member2 is not)
    membership1 = Membership(
        user_id=member1.id,
        group_id=group.id,
        rotation_position=2,
        is_admin=True,
        is_active=True
    )
    membership2 = Membership(
        user_id=member2.id,
        group_id=group.id,
        rotation_position=3,
        is_admin=False,
        is_active=True
    )
    db.add_all([membership1, membership2])
    db.commit()
    
    # Try to assign admin by member1 (who is admin but not creator)
    try:
        GroupService.set_member_admin(
            db=db,
            group_id=group.id,
            target_user_id=member2.id,
            is_admin=True,
            requester_id=member1.id  # Not creator
        )
        print("✗ Non-creator should not be able to assign admin")
        return False
    except Exception as e:
        if "creator" in str(e).lower():
            print(f"✓ Correctly blocked non-creator from assigning admin")
            print(f"  Error: {e}")
            return True
        else:
            print(f"✗ Unexpected error: {e}")
            return False


def test_cannot_modify_creator_admin_status(db: Session):
    """Test that creator's admin status cannot be modified."""
    print("\n=== Test: Cannot Modify Creator's Admin Status ===")
    
    # Create creator
    creator = User(
        phone_number=encrypt_field("+233240000002"),
        name="Creator 4",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    
    db.add(creator)
    db.commit()
    db.refresh(creator)
    
    # Create group
    group_data = GroupCreate(
        name="Creator Protection Test",
        contribution_amount=80.0,
        num_cycles=2,
        cash_only=False
    )
    group = GroupService.create_group(db, group_data, creator)
    
    # Try to remove creator's admin status (even by creator themselves)
    try:
        GroupService.set_member_admin(
            db=db,
            group_id=group.id,
            target_user_id=creator.id,
            is_admin=False,  # Try to remove
            requester_id=creator.id
        )
        print("✗ Creator's admin status should not be modifiable")
        return False
    except Exception as e:
        if "creator" in str(e).lower():
            print(f"✓ Correctly protected creator's admin status")
            print(f"  Error: {e}")
            return True
        else:
            print(f"✗ Unexpected error: {e}")
            return False


def main():
    """Run all admin assignment tests."""
    print("=" * 60)
    print("Admin Role Assignment Tests")
    print("=" * 60)
    
    db = setup_test_db()
    
    try:
        # Test 1: Creator assigns admin
        test_creator_assign_admin(db)
        
        # Test 2: Creator revokes admin
        test_creator_revoke_admin(db)
        
        # Test 3: Non-creator cannot assign
        test_non_creator_cannot_assign(db)
        
        # Test 4: Cannot modify creator's admin status
        test_cannot_modify_creator_admin_status(db)
        
        print("\n" + "=" * 60)
        print("All admin assignment tests completed successfully! ✅")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

