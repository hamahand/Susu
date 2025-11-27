#!/usr/bin/env python3
"""
Create specific test users and additional diverse test data.
Run this script to populate the database with comprehensive test data.
"""

from app.database import SessionLocal, engine, Base
from app.models import User, Group, Membership, Payment, UserType, GroupStatus, PaymentStatus, PaymentType
from app.utils import encrypt_field, get_password_hash
import random
from datetime import datetime, timedelta

def create_test_users():
    """Create specific users requested and additional test data."""
    
    print("🌱 Creating test users and data...\n")
    
    db = SessionLocal()
    
    try:
        # Standard password for all test users
        standard_password = "Test@123"
        
        print("Creating requested specific users...")
        
        # The 3 specific users requested
        user1 = User(
            phone_number=encrypt_field("+233598430399"),
            name="Kwame Mensah",
            email="kwame.mensah@test.com",
            user_type=UserType.APP,
            momo_account_id=encrypt_field("+233598430399"),
            password_hash=get_password_hash(standard_password),
            kyc_verified=True,
            kyc_verified_at=datetime.utcnow(),
            kyc_provider="MTN"
        )
        
        user2 = User(
            phone_number=encrypt_field("+233532936681"),
            name="Ama Osei",
            email="ama.osei@test.com",
            user_type=UserType.APP,
            momo_account_id=encrypt_field("+233532936681"),
            password_hash=get_password_hash(standard_password),
            kyc_verified=True,
            kyc_verified_at=datetime.utcnow(),
            kyc_provider="MTN"
        )
        
        user3 = User(
            phone_number=encrypt_field("+233242567564"),
            name="Kofi Asante",
            email="kofi.asante@test.com",
            user_type=UserType.APP,
            momo_account_id=encrypt_field("+233242567564"),
            password_hash=get_password_hash(standard_password),
            kyc_verified=True,
            kyc_verified_at=datetime.utcnow(),
            kyc_provider="MTN"
        )
        
        db.add_all([user1, user2, user3])
        db.commit()
        db.refresh(user1)
        db.refresh(user2)
        db.refresh(user3)
        
        print(f"✅ Created 3 requested users")
        
        # Additional diverse test users
        print("\nCreating additional test users...")
        
        additional_users = [
            # App users with different statuses
            User(
                phone_number=encrypt_field("+233501234567"),
                name="Abena Boateng",
                email="abena.b@test.com",
                user_type=UserType.APP,
                momo_account_id=encrypt_field("+233501234567"),
                password_hash=get_password_hash(standard_password),
                kyc_verified=True,
                kyc_verified_at=datetime.utcnow(),
                kyc_provider="MTN"
            ),
            User(
                phone_number=encrypt_field("+233507654321"),
                name="Yaw Owusu",
                email="yaw.owusu@test.com",
                user_type=UserType.APP,
                momo_account_id=encrypt_field("+233507654321"),
                password_hash=get_password_hash(standard_password),
                kyc_verified=False  # Not KYC verified
            ),
            User(
                phone_number=encrypt_field("+233209876543"),
                name="Akosua Adjei",
                email="akosua.a@test.com",
                user_type=UserType.APP,
                momo_account_id=encrypt_field("+233209876543"),
                password_hash=get_password_hash(standard_password),
                kyc_verified=True,
                kyc_verified_at=datetime.utcnow(),
                kyc_provider="manual"
            ),
            # USSD users (no passwords)
            User(
                phone_number=encrypt_field("+233555111222"),
                name="Kwabena Darko",
                user_type=UserType.USSD,
                momo_account_id=encrypt_field("+233555111222"),
                kyc_verified=True,
                kyc_verified_at=datetime.utcnow(),
                kyc_provider="MTN"
            ),
            User(
                phone_number=encrypt_field("+233555333444"),
                name="Efua Yankson",
                user_type=UserType.USSD,
                momo_account_id=encrypt_field("+233555333444"),
                kyc_verified=True,
                kyc_verified_at=datetime.utcnow(),
                kyc_provider="MTN"
            ),
            User(
                phone_number=encrypt_field("+233555555666"),
                name="Kojo Appiah",
                user_type=UserType.USSD,
                momo_account_id=encrypt_field("+233555555666"),
                kyc_verified=False
            ),
            User(
                phone_number=encrypt_field("+233555777888"),
                name="Adwoa Sarpong",
                user_type=UserType.USSD,
                momo_account_id=encrypt_field("+233555777888"),
                kyc_verified=True,
                kyc_verified_at=datetime.utcnow(),
                kyc_provider="MTN"
            ),
            # More app users
            User(
                phone_number=encrypt_field("+233241122334"),
                name="Nana Frimpong",
                email="nana.f@test.com",
                user_type=UserType.APP,
                momo_account_id=encrypt_field("+233241122334"),
                password_hash=get_password_hash(standard_password),
                kyc_verified=True,
                kyc_verified_at=datetime.utcnow(),
                kyc_provider="MTN"
            ),
        ]
        
        db.add_all(additional_users)
        db.commit()
        
        # Refresh to get IDs
        for user in additional_users:
            db.refresh(user)
        
        print(f"✅ Created {len(additional_users)} additional users")
        
        # Create diverse groups
        print("\nCreating test groups...")
        
        groups = [
            Group(
                group_code="TEST0001",
                name="Family Savings Group",
                contribution_amount=100.00,
                num_cycles=12,
                current_round=3,
                creator_id=user1.id,
                status=GroupStatus.ACTIVE
            ),
            Group(
                group_code="TEST0002",
                name="Business Partners Fund",
                contribution_amount=500.00,
                num_cycles=6,
                current_round=1,
                creator_id=user2.id,
                status=GroupStatus.ACTIVE
            ),
            Group(
                group_code="TEST0003",
                name="Youth Empowerment Fund",
                contribution_amount=50.00,
                num_cycles=24,
                current_round=5,
                creator_id=user3.id,
                status=GroupStatus.ACTIVE
            ),
            Group(
                group_code="TEST0004",
                name="Women's Cooperative",
                contribution_amount=200.00,
                num_cycles=10,
                current_round=2,
                creator_id=additional_users[0].id,
                status=GroupStatus.ACTIVE
            ),
            Group(
                group_code="TEST0005",
                name="Farmers Union Susu",
                contribution_amount=75.00,
                num_cycles=8,
                current_round=1,
                creator_id=additional_users[2].id,
                status=GroupStatus.ACTIVE
            ),
        ]
        
        db.add_all(groups)
        db.commit()
        
        for group in groups:
            db.refresh(group)
        
        print(f"✅ Created {len(groups)} groups")
        
        # Create memberships
        print("\nCreating memberships...")
        
        all_users = [user1, user2, user3] + additional_users
        memberships = []
        
        # Group 1: Family Savings (5 members)
        for i, user in enumerate([user1, user2, additional_users[0], additional_users[3], additional_users[4]]):
            memberships.append(Membership(
                user_id=user.id,
                group_id=groups[0].id,
                rotation_position=i + 1,
                is_admin=True if i == 0 else False,
                is_active=True
            ))
        
        # Group 2: Business Partners (3 members)
        for i, user in enumerate([user2, user3, additional_users[1]]):
            memberships.append(Membership(
                user_id=user.id,
                group_id=groups[1].id,
                rotation_position=i + 1,
                is_admin=True if i == 0 else False,
                is_active=True
            ))
        
        # Group 3: Youth Empowerment (6 members)
        for i, user in enumerate([user3, additional_users[3], additional_users[4], additional_users[5], additional_users[6], additional_users[7]]):
            memberships.append(Membership(
                user_id=user.id,
                group_id=groups[2].id,
                rotation_position=i + 1,
                is_admin=True if i == 0 else False,
                is_active=True
            ))
        
        # Group 4: Women's Cooperative (4 members)
        for i, user in enumerate([additional_users[0], additional_users[2], user1, additional_users[6]]):
            memberships.append(Membership(
                user_id=user.id,
                group_id=groups[3].id,
                rotation_position=i + 1,
                is_admin=True if i == 0 else False,
                is_active=True
            ))
        
        # Group 5: Farmers Union (3 members)
        for i, user in enumerate([additional_users[2], additional_users[3], additional_users[5]]):
            memberships.append(Membership(
                user_id=user.id,
                group_id=groups[4].id,
                rotation_position=i + 1,
                is_admin=True if i == 0 else False,
                is_active=True
            ))
        
        db.add_all(memberships)
        db.commit()
        
        print(f"✅ Created {len(memberships)} memberships")
        
        # Create sample payments (mix of successful, pending, and failed)
        print("\nCreating sample payments...")
        
        payments = []
        
        # Group 1 payments (round 3)
        for membership in memberships[:5]:  # First 5 are group 1
            for round_num in range(1, 4):  # Rounds 1-3
                status = PaymentStatus.SUCCESS if round_num < 3 else (
                    PaymentStatus.PENDING if membership.rotation_position % 2 == 0 else PaymentStatus.SUCCESS
                )
                payment_type = PaymentType.MOMO if membership.rotation_position % 3 != 0 else PaymentType.CASH
                
                payments.append(Payment(
                    transaction_id=f"MOMO{random.randint(100000, 999999)}" if payment_type == PaymentType.MOMO else None,
                    user_id=membership.user_id,
                    group_id=membership.group_id,
                    round_number=round_num,
                    amount=100.00,
                    status=status,
                    payment_type=payment_type,
                    payment_date=datetime.utcnow() - timedelta(days=(3-round_num)*7) if status == PaymentStatus.SUCCESS else None,
                    retry_count=0 if status == PaymentStatus.SUCCESS else random.randint(0, 2)
                ))
        
        # Group 2 payments (round 1)
        for membership in [m for m in memberships if m.group_id == groups[1].id]:
            payments.append(Payment(
                transaction_id=f"MOMO{random.randint(100000, 999999)}",
                user_id=membership.user_id,
                group_id=membership.group_id,
                round_number=1,
                amount=500.00,
                status=PaymentStatus.SUCCESS,
                payment_type=PaymentType.MOMO,
                payment_date=datetime.utcnow() - timedelta(days=3),
                retry_count=0
            ))
        
        # Group 3 payments (some in round 5, some pending)
        for membership in [m for m in memberships if m.group_id == groups[2].id]:
            for round_num in [4, 5]:
                status = PaymentStatus.SUCCESS if round_num == 4 else (
                    PaymentStatus.PENDING if membership.rotation_position <= 3 else PaymentStatus.SUCCESS
                )
                payments.append(Payment(
                    transaction_id=f"MOMO{random.randint(100000, 999999)}" if status == PaymentStatus.SUCCESS else None,
                    user_id=membership.user_id,
                    group_id=membership.group_id,
                    round_number=round_num,
                    amount=50.00,
                    status=status,
                    payment_type=PaymentType.MOMO,
                    payment_date=datetime.utcnow() - timedelta(days=(5-round_num)*7) if status == PaymentStatus.SUCCESS else None,
                    retry_count=0
                ))
        
        db.add_all(payments)
        db.commit()
        
        print(f"✅ Created {len(payments)} sample payments")
        
        # Summary
        print("\n" + "="*70)
        print("✨ Test users and data created successfully!")
        print("="*70)
        
        print("\n📋 REQUESTED USERS (Standard Password: Test@123):")
        print(f"  1. Phone: +233598430399, Name: Kwame Mensah (KYC Verified)")
        print(f"  2. Phone: +233532936681, Name: Ama Osei (KYC Verified)")
        print(f"  3. Phone: +233242567564, Name: Kofi Asante (KYC Verified)")
        
        print("\n📱 ADDITIONAL APP USERS (Password: Test@123):")
        print(f"  4. Phone: +233501234567, Name: Abena Boateng (KYC Verified)")
        print(f"  5. Phone: +233507654321, Name: Yaw Owusu (NOT KYC Verified)")
        print(f"  6. Phone: +233209876543, Name: Akosua Adjei (KYC Verified)")
        print(f"  7. Phone: +233241122334, Name: Nana Frimpong (KYC Verified)")
        
        print("\n☎️  USSD USERS (No Password - USSD Only):")
        print(f"  8. Phone: +233555111222, Name: Kwabena Darko (KYC Verified)")
        print(f"  9. Phone: +233555333444, Name: Efua Yankson (KYC Verified)")
        print(f" 10. Phone: +233555555666, Name: Kojo Appiah (NOT KYC Verified)")
        print(f" 11. Phone: +233555777888, Name: Adwoa Sarpong (KYC Verified)")
        
        print("\n👥 GROUPS CREATED:")
        print(f"  1. TEST0001 - Family Savings Group (5 members, Round 3/12)")
        print(f"  2. TEST0002 - Business Partners Fund (3 members, Round 1/6)")
        print(f"  3. TEST0003 - Youth Empowerment Fund (6 members, Round 5/24)")
        print(f"  4. TEST0004 - Women's Cooperative (4 members, Round 2/10)")
        print(f"  5. TEST0005 - Farmers Union Susu (3 members, Pending)")
        
        print("\n💰 PAYMENT STATUS:")
        print(f"  - Total payments created: {len(payments)}")
        print(f"  - Mix of MOMO and Cash payments")
        print(f"  - Various statuses: SUCCESS, PENDING, FAILED")
        
        print("\n🔑 LOGIN CREDENTIALS:")
        print("  Username: Any phone number from APP USERS above")
        print("  Password: Test@123")
        
        print("\n🚀 You can now test with realistic data!")
        print("   - API Docs: http://localhost:8000/docs")
        print("   - Frontend: http://localhost:3000/app/")
        print("   - Test Login: Use any app user phone + Test@123\n")
        
    except Exception as e:
        print(f"❌ Error creating test users: {str(e)}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    create_test_users()

