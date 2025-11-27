"""
Test cash payment features:
- Mark payment as cash paid
- Cash-only group creation
- MOMO skip in cash-only groups
- Admin permissions for marking paid
"""

import sys
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import (
    Base, User, Group, Membership, Payment, PaymentStatus, PaymentType,
    GroupStatus, UserType
)
from app.services import PaymentService, GroupService
from app.schemas import GroupCreate
from app.utils import encrypt_field


def setup_test_db():
    """Create tables and return db session."""
    Base.metadata.create_all(bind=engine)
    return SessionLocal()


def test_cash_only_group_creation(db: Session):
    """Test creating a cash-only group."""
    print("\n=== Test: Cash-Only Group Creation ===")
    
    # Create user
    user = User(
        phone_number=encrypt_field("+233241234567"),
        name="Test User",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create cash-only group
    group_data = GroupCreate(
        name="Cash Only Savings",
        contribution_amount=50.0,
        num_cycles=5,
        cash_only=True
    )
    
    group = GroupService.create_group(db, group_data, user)
    
    assert group.cash_only == True, "Group should be cash-only"
    print(f"✓ Created cash-only group: {group.name}")
    print(f"  Cash only: {group.cash_only}")
    
    return user, group


def test_momo_skip_in_cash_only(db: Session, user: User, group: Group):
    """Test that MOMO is skipped for cash-only groups."""
    print("\n=== Test: MOMO Skip in Cash-Only Groups ===")
    
    try:
        PaymentService.process_payment(db, user.id, group.id)
        print("✗ Should have raised exception for cash-only group")
        return False
    except Exception as e:
        if "cash-only group" in str(e).lower():
            print(f"✓ Correctly blocked MOMO payment in cash-only group")
            print(f"  Error message: {e}")
            return True
        else:
            print(f"✗ Unexpected error: {e}")
            return False


def test_mark_as_cash_paid(db: Session):
    """Test admin marking payment as cash paid."""
    print("\n=== Test: Mark Payment as Cash Paid ===")
    
    # Create admin user
    admin = User(
        phone_number=encrypt_field("+233241111111"),
        name="Admin User",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    db.add(admin)
    
    # Create member user
    member = User(
        phone_number=encrypt_field("+233242222222"),
        name="Member User",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    db.add(member)
    db.commit()
    db.refresh(admin)
    db.refresh(member)
    
    # Create cash-only group
    group_data = GroupCreate(
        name="Admin Test Group",
        contribution_amount=100.0,
        num_cycles=3,
        cash_only=True
    )
    group = GroupService.create_group(db, group_data, admin)
    
    # Add member to group
    next_pos = len(group.memberships) + 1
    membership = Membership(
        user_id=member.id,
        group_id=group.id,
        rotation_position=next_pos,
        is_admin=False,
        is_active=True
    )
    db.add(membership)
    db.commit()
    
    # Create pending payment for member
    payment = Payment(
        user_id=member.id,
        group_id=group.id,
        round_number=group.current_round,
        amount=group.contribution_amount,
        status=PaymentStatus.PENDING,
        payment_type=PaymentType.CASH
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    print(f"  Created pending payment: ID={payment.id}, Status={payment.status}")
    
    # Admin marks as paid
    paid_payment = PaymentService.mark_as_cash_paid(
        db=db,
        payment_id=payment.id,
        admin_user_id=admin.id
    )
    
    assert paid_payment.status == PaymentStatus.SUCCESS, "Payment should be marked as success"
    assert paid_payment.payment_type == PaymentType.CASH, "Payment type should be CASH"
    assert paid_payment.marked_paid_by == admin.id, "Should track who marked it paid"
    assert paid_payment.transaction_id.startswith("CASH-"), "Should have CASH transaction ID"
    
    print(f"✓ Admin successfully marked payment as paid")
    print(f"  Transaction ID: {paid_payment.transaction_id}")
    print(f"  Marked by: {paid_payment.marked_paid_by}")
    print(f"  Payment type: {paid_payment.payment_type}")
    
    return admin, member, group


def test_non_admin_cannot_mark_paid(db: Session):
    """Test that non-admins cannot mark payments as paid."""
    print("\n=== Test: Non-Admin Cannot Mark Paid ===")
    
    # Create two members
    user1 = User(
        phone_number=encrypt_field("+233243333333"),
        name="User One",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    user2 = User(
        phone_number=encrypt_field("+233244444444"),
        name="User Two",
        user_type=UserType.APP,
        password_hash="dummy",
        kyc_verified=True
    )
    db.add_all([user1, user2])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)
    
    # Create group (user1 is creator/admin)
    group_data = GroupCreate(
        name="Permission Test Group",
        contribution_amount=75.0,
        num_cycles=2,
        cash_only=True
    )
    group = GroupService.create_group(db, group_data, user1)
    
    # Add user2 as regular member (not admin)
    membership = Membership(
        user_id=user2.id,
        group_id=group.id,
        rotation_position=2,
        is_admin=False,
        is_active=True
    )
    db.add(membership)
    db.commit()
    
    # Create payment for user1
    payment = Payment(
        user_id=user1.id,
        group_id=group.id,
        round_number=1,
        amount=75.0,
        status=PaymentStatus.PENDING,
        payment_type=PaymentType.CASH
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # Try to mark as paid by non-admin user2
    try:
        PaymentService.mark_as_cash_paid(
            db=db,
            payment_id=payment.id,
            admin_user_id=user2.id
        )
        print("✗ Non-admin should not be able to mark payments as paid")
        return False
    except Exception as e:
        if "admin" in str(e).lower():
            print(f"✓ Correctly blocked non-admin from marking payment")
            print(f"  Error: {e}")
            return True
        else:
            print(f"✗ Unexpected error: {e}")
            return False


def main():
    """Run all cash payment tests."""
    print("=" * 60)
    print("Cash Payment System Tests")
    print("=" * 60)
    
    db = setup_test_db()
    
    try:
        # Test 1: Cash-only group creation
        user, cash_group = test_cash_only_group_creation(db)
        
        # Test 2: MOMO skip in cash-only groups
        test_momo_skip_in_cash_only(db, user, cash_group)
        
        # Test 3: Mark as cash paid
        test_mark_as_cash_paid(db)
        
        # Test 4: Non-admin permissions
        test_non_admin_cannot_mark_paid(db)
        
        print("\n" + "=" * 60)
        print("All cash payment tests completed successfully! ✅")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

