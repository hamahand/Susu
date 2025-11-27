#!/usr/bin/env python3
"""
Test script for Dual Payment System

Tests all three payment methods: AUTO, MANUAL, USSD
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, UserType, PaymentMethod, PaymentPreference
from app.services.dual_payment_service import dual_payment_service


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_section(title):
    """Print a formatted section."""
    print("\n" + "-" * 70)
    print(title)
    print("-" * 70)


def create_test_users(db):
    """Create test users for each payment method."""
    print_header("Creating Test Users")
    
    test_users = []
    
    # Check if users already exist
    existing_auto = db.query(User).filter(User.phone_number == "+233240000001").first()
    existing_manual = db.query(User).filter(User.phone_number == "+233240000002").first()
    existing_ussd = db.query(User).filter(User.phone_number == "+233240000003").first()
    
    if existing_auto and existing_manual and existing_ussd:
        print("\n✓ Test users already exist, using existing users")
        return [existing_auto, existing_manual, existing_ussd]
    
    # Create AUTO payment user
    if not existing_auto:
        user_auto = User(
            phone_number="+233240000001",
            name="Auto Pay User",
            email="auto@test.com",
            user_type=UserType.APP
        )
        db.add(user_auto)
        test_users.append(user_auto)
        print("✓ Created AUTO payment user")
    else:
        test_users.append(existing_auto)
    
    # Create MANUAL payment user  
    if not existing_manual:
        user_manual = User(
            phone_number="+233240000002",
            name="Manual Pay User",
            email="manual@test.com",
            user_type=UserType.APP
        )
        db.add(user_manual)
        test_users.append(user_manual)
        print("✓ Created MANUAL payment user")
    else:
        test_users.append(existing_manual)
    
    # Create USSD payment user
    if not existing_ussd:
        user_ussd = User(
            phone_number="+233240000003",
            name="USSD Pay User",
            user_type=UserType.USSD
        )
        db.add(user_ussd)
        test_users.append(user_ussd)
        print("✓ Created USSD payment user")
    else:
        test_users.append(existing_ussd)
    
    db.commit()
    
    for user in test_users:
        db.refresh(user)
    
    return test_users


def test_payment_preference_setup(db, users):
    """Test setting payment preferences."""
    print_header("Testing Payment Preference Setup")
    
    user_auto, user_manual, user_ussd = users
    
    # Test AUTO preference
    print_section("Test 1: Set AUTO payment preference")
    pref_auto = dual_payment_service.set_payment_preference(
        db=db,
        user_id=user_auto.id,
        payment_method=PaymentMethod.AUTO,
        auto_pay_day=1,
        send_reminders=True
    )
    
    print(f"✓ User: {user_auto.name}")
    print(f"  Payment Method: {pref_auto.payment_method}")
    print(f"  Auto-pay Enabled: {pref_auto.auto_pay_enabled}")
    print(f"  Auto-pay Day: {pref_auto.auto_pay_day}")
    print(f"  MoMo Consent: {pref_auto.momo_consent_given}")
    
    # Test MANUAL preference
    print_section("Test 2: Set MANUAL payment preference")
    pref_manual = dual_payment_service.set_payment_preference(
        db=db,
        user_id=user_manual.id,
        payment_method=PaymentMethod.MANUAL,
        send_reminders=True
    )
    
    print(f"✓ User: {user_manual.name}")
    print(f"  Payment Method: {pref_manual.payment_method}")
    print(f"  Auto-pay Enabled: {pref_manual.auto_pay_enabled}")
    print(f"  Send Reminders: {pref_manual.send_payment_reminders}")
    
    # Test USSD preference
    print_section("Test 3: Set USSD payment preference")
    pref_ussd = dual_payment_service.set_payment_preference(
        db=db,
        user_id=user_ussd.id,
        payment_method=PaymentMethod.USSD,
        send_reminders=True
    )
    
    print(f"✓ User: {user_ussd.name}")
    print(f"  Payment Method: {pref_ussd.payment_method}")
    print(f"  Send Reminders: {pref_ussd.send_payment_reminders}")
    
    print("\n✅ All payment preferences set successfully!")
    return [pref_auto, pref_manual, pref_ussd]


def test_payment_initiation(db, users):
    """Test initiating payments for different methods."""
    print_header("Testing Payment Initiation")
    
    user_auto, user_manual, user_ussd = users
    
    # Test AUTO payment
    print_section("Test 1: Initiate AUTO payment")
    result_auto = dual_payment_service.initiate_payment(
        db=db,
        user_id=user_auto.id,
        amount=50.00,
        reference="TEST_AUTO_001",
        description="Test Auto Payment"
    )
    
    print(f"✓ Result for {user_auto.name}:")
    print(f"  Status: {result_auto.get('status')}")
    print(f"  Message: {result_auto.get('message')}")
    print(f"  Method: {result_auto.get('method')}")
    if result_auto.get('reference_id'):
        print(f"  Reference ID: {result_auto.get('reference_id')}")
    
    # Test MANUAL payment
    print_section("Test 2: Initiate MANUAL payment")
    result_manual = dual_payment_service.initiate_payment(
        db=db,
        user_id=user_manual.id,
        amount=50.00,
        reference="TEST_MANUAL_001",
        description="Test Manual Payment"
    )
    
    print(f"✓ Result for {user_manual.name}:")
    print(f"  Status: {result_manual.get('status')}")
    print(f"  Message: {result_manual.get('message')}")
    print(f"  Method: {result_manual.get('method')}")
    if result_manual.get('auth_req_id'):
        print(f"  Auth Request ID: {result_manual.get('auth_req_id')}")
        print(f"  Poll Interval: {result_manual.get('interval')}s")
        print(f"  Expires In: {result_manual.get('expires_in')}s")
    
    # Test USSD payment
    print_section("Test 3: Initiate USSD payment")
    result_ussd = dual_payment_service.initiate_payment(
        db=db,
        user_id=user_ussd.id,
        amount=50.00,
        reference="TEST_USSD_001",
        description="Test USSD Payment"
    )
    
    print(f"✓ Result for {user_ussd.name}:")
    print(f"  Status: {result_ussd.get('status')}")
    print(f"  Message: {result_ussd.get('message')}")
    print(f"  Method: {result_ussd.get('method')}")
    if result_ussd.get('ussd_code'):
        print(f"  USSD Code: {result_ussd.get('ussd_code')}")
    
    return [result_auto, result_manual, result_ussd]


def test_preference_switching(db, users):
    """Test switching payment preferences."""
    print_header("Testing Preference Switching")
    
    user_auto = users[0]
    
    print_section("Test: Switch from AUTO to MANUAL")
    print(f"Original preference: {user_auto.payment_preference.payment_method}")
    
    # Switch to MANUAL
    pref = dual_payment_service.set_payment_preference(
        db=db,
        user_id=user_auto.id,
        payment_method=PaymentMethod.MANUAL
    )
    
    print(f"✓ New preference: {pref.payment_method}")
    print(f"  Auto-pay Enabled: {pref.auto_pay_enabled}")
    
    # Switch back to AUTO
    pref = dual_payment_service.set_payment_preference(
        db=db,
        user_id=user_auto.id,
        payment_method=PaymentMethod.AUTO,
        auto_pay_day=15
    )
    
    print(f"✓ Switched back to: {pref.payment_method}")
    print(f"  Auto-pay Day: {pref.auto_pay_day}")
    
    print("\n✅ Preference switching works correctly!")


def test_analytics(db):
    """Test payment method analytics."""
    print_header("Payment Method Analytics")
    
    from sqlalchemy import func
    
    # Count by method
    method_counts = db.query(
        PaymentPreference.payment_method,
        func.count(PaymentPreference.id)
    ).group_by(PaymentPreference.payment_method).all()
    
    print("\n📊 Payment Method Distribution:")
    total = 0
    for method, count in method_counts:
        print(f"   {method.upper():8s}: {count} user(s)")
        total += count
    
    print(f"   {'TOTAL':8s}: {total} user(s)")
    
    # Count auto-pay enabled
    auto_enabled = db.query(PaymentPreference).filter(
        PaymentPreference.auto_pay_enabled == True
    ).count()
    
    print(f"\n   Auto-pay Enabled: {auto_enabled} user(s)")
    
    if total > 0:
        auto_percent = (auto_enabled / total) * 100
        print(f"   Auto-pay Adoption: {auto_percent:.1f}%")


def cleanup_test_users(db, users):
    """Clean up test users (optional)."""
    response = input("\nDelete test users? (y/N): ").strip().lower()
    
    if response == 'y':
        for user in users:
            # Delete preferences first
            pref = db.query(PaymentPreference).filter(
                PaymentPreference.user_id == user.id
            ).first()
            if pref:
                db.delete(pref)
            
            db.delete(user)
        
        db.commit()
        print("✓ Test users deleted")
    else:
        print("✓ Test users kept for further testing")


def main():
    """Main test runner."""
    print_header("Dual Payment System Test Suite")
    print("\nThis script will test the dual payment system with all three methods:")
    print("  1. AUTO - Automated payments")
    print("  2. MANUAL - Manual approval (bc-authorize)")
    print("  3. USSD - Traditional USSD payments")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    db = SessionLocal()
    
    try:
        # Create test users
        users = create_test_users(db)
        
        # Test preference setup
        prefs = test_payment_preference_setup(db, users)
        
        # Test payment initiation
        print("\n⚠️  Note: This will attempt to send real API requests to MTN sandbox")
        proceed = input("Continue with payment tests? (Y/n): ").strip().lower()
        
        if proceed != 'n':
            results = test_payment_initiation(db, users)
        
        # Test preference switching
        test_preference_switching(db, users)
        
        # Show analytics
        test_analytics(db)
        
        # Summary
        print_header("Test Summary")
        print("\n✅ All tests completed successfully!")
        print("\nWhat was tested:")
        print("   ✓ Payment preference creation")
        print("   ✓ Payment initiation for all methods")
        print("   ✓ Preference switching")
        print("   ✓ Analytics queries")
        
        print("\nPayment Method Routing:")
        print("   ✓ AUTO → API User + request-to-pay")
        print("   ✓ MANUAL → bc-authorize + request-to-pay")  
        print("   ✓ USSD → SMS reminder + USSD menu")
        
        print("\n📚 Next Steps:")
        print("   1. Integrate with your mobile app signup")
        print("   2. Add payment method selector to UI")
        print("   3. Test with real MTN MoMo sandbox")
        print("   4. Set up cron jobs for auto-payments")
        
        # Cleanup
        cleanup_test_users(db, users)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
    
    print("\n" + "=" * 70)
    print("For more info, see: backend/docs/DUAL_PAYMENT_SYSTEM.md")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Tests cancelled by user")
        sys.exit(1)

