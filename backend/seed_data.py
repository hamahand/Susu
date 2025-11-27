#!/usr/bin/env python3
"""
Seed script to populate database with test data.
Run this after creating tables: python seed_data.py
"""

from app.database import SessionLocal, engine, Base
from app.models import User, Group, Membership, Payment, UserType, GroupStatus, PaymentStatus
from app.utils import encrypt_field, get_password_hash
import random

def seed_database():
    """Populate database with test data."""
    
    print("🌱 Seeding database with test data...\n")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create test users
        print("Creating users...")
        
        # App users (admins)
        admin1 = User(
            phone_number=encrypt_field("+233244111111"),
            name="Kwame Admin",
            user_type=UserType.APP,
            momo_account_id=encrypt_field("+233244111111"),
            password_hash=get_password_hash("password123")
        )
        
        admin2 = User(
            phone_number=encrypt_field("+233244222222"),
            name="Ama Creator",
            user_type=UserType.APP,
            momo_account_id=encrypt_field("+233244222222"),
            password_hash=get_password_hash("password123")
        )
        
        # USSD users (members)
        member1 = User(
            phone_number=encrypt_field("+233244333333"),
            name="Kofi Member",
            user_type=UserType.USSD,
            momo_account_id=encrypt_field("+233244333333")
        )
        
        member2 = User(
            phone_number=encrypt_field("+233244444444"),
            name="Akua Member",
            user_type=UserType.USSD,
            momo_account_id=encrypt_field("+233244444444")
        )
        
        member3 = User(
            phone_number=encrypt_field("+233244555555"),
            name="Yaw Member",
            user_type=UserType.USSD,
            momo_account_id=encrypt_field("+233244555555")
        )
        
        db.add_all([admin1, admin2, member1, member2, member3])
        db.commit()
        
        print(f"✅ Created {5} users")
        
        # Create test groups
        print("\nCreating groups...")
        
        group1 = Group(
            group_code="SUSU1234",
            name="Monthly Rent Fund",
            contribution_amount=50.00,
            num_cycles=5,
            current_round=1,
            creator_id=admin1.id,
            status=GroupStatus.ACTIVE
        )
        
        group2 = Group(
            group_code="SUSU5678",
            name="Business Startup Fund",
            contribution_amount=100.00,
            num_cycles=10,
            current_round=1,
            creator_id=admin2.id,
            status=GroupStatus.ACTIVE
        )
        
        db.add_all([group1, group2])
        db.commit()
        
        print(f"✅ Created {2} groups")
        
        # Create memberships for group 1
        print("\nCreating memberships...")
        
        memberships_group1 = [
            Membership(
                user_id=admin1.id,
                group_id=group1.id,
                rotation_position=1,
                is_admin=True,
                is_active=True
            ),
            Membership(
                user_id=member1.id,
                group_id=group1.id,
                rotation_position=2,
                is_admin=False,
                is_active=True
            ),
            Membership(
                user_id=member2.id,
                group_id=group1.id,
                rotation_position=3,
                is_admin=False,
                is_active=True
            ),
            Membership(
                user_id=member3.id,
                group_id=group1.id,
                rotation_position=4,
                is_admin=False,
                is_active=True
            ),
        ]
        
        # Create memberships for group 2
        memberships_group2 = [
            Membership(
                user_id=admin2.id,
                group_id=group2.id,
                rotation_position=1,
                is_admin=True,
                is_active=True
            ),
            Membership(
                user_id=member1.id,
                group_id=group2.id,
                rotation_position=2,
                is_admin=False,
                is_active=True
            ),
        ]
        
        db.add_all(memberships_group1 + memberships_group2)
        db.commit()
        
        print(f"✅ Created {len(memberships_group1) + len(memberships_group2)} memberships")
        
        # Create some sample payments
        print("\nCreating sample payments...")
        
        payment1 = Payment(
            transaction_id="MOMO" + "".join(random.choices("0123456789ABCDEF", k=12)),
            user_id=admin1.id,
            group_id=group1.id,
            round_number=1,
            amount=50.00,
            status=PaymentStatus.SUCCESS,
            retry_count=0
        )
        
        payment2 = Payment(
            transaction_id="MOMO" + "".join(random.choices("0123456789ABCDEF", k=12)),
            user_id=member1.id,
            group_id=group1.id,
            round_number=1,
            amount=50.00,
            status=PaymentStatus.SUCCESS,
            retry_count=0
        )
        
        db.add_all([payment1, payment2])
        db.commit()
        
        print(f"✅ Created {2} sample payments")
        
        print("\n" + "="*60)
        print("✨ Database seeded successfully!")
        print("="*60)
        
        print("\n📋 Test Credentials:")
        print("\nApp Users (for mobile app login):")
        print("  1. Phone: +233244111111, Password: password123 (Kwame Admin)")
        print("  2. Phone: +233244222222, Password: password123 (Ama Creator)")
        
        print("\nUSSD Users (for USSD testing):")
        print("  1. +233244333333 (Kofi Member)")
        print("  2. +233244444444 (Akua Member)")
        print("  3. +233244555555 (Yaw Member)")
        
        print("\nGroups:")
        print(f"  1. Code: SUSU1234, Name: Monthly Rent Fund")
        print(f"  2. Code: SUSU5678, Name: Business Startup Fund")
        
        print("\n🚀 You can now start testing the API!")
        print("   API Docs: http://localhost:8000/docs")
        print("   USSD Test: python test_ussd.py\n")
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

