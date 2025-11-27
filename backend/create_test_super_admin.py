#!/usr/bin/env python3
"""
Create a super admin user programmatically.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, UserType, AdminRole
from app.utils.auth import get_password_hash
from app.utils.encryption import encrypt_field, decrypt_field


def create_super_admin():
    """Create a super admin user."""
    db = SessionLocal()
    
    try:
        # Check if any super admin already exists
        existing_admin = db.query(User).filter(User.is_system_admin == True).first()
        if existing_admin:
            print("✅ Super admin already exists!")
            try:
                phone = decrypt_field(existing_admin.phone_number)
                print(f"   Admin: {existing_admin.name}")
                print(f"   Phone: {phone}")
                print(f"   Role: {existing_admin.admin_role}")
            except:
                pass
            return existing_admin
        
        # Create super admin with default credentials
        phone_number = "+233244999999"
        name = "Super Admin"
        password = "admin123"
        
        # Check if user with this phone already exists
        all_users = db.query(User).all()
        for u in all_users:
            try:
                if decrypt_field(u.phone_number) == phone_number:
                    print(f"✅ User with phone {phone_number} already exists!")
                    print(f"   Promoting to super admin...")
                    u.is_system_admin = True
                    u.admin_role = "super_admin"
                    db.add(u)
                    db.commit()
                    print(f"✅ User {u.name} promoted to Super Admin!")
                    return u
            except:
                continue
        
        # Create super admin
        encrypted_phone = encrypt_field(phone_number)
        
        super_admin = User(
            phone_number=encrypted_phone,
            name=name,
            user_type=UserType.APP,
            password_hash=get_password_hash(password),
            is_system_admin=True,
            admin_role="super_admin",
            momo_account_id=encrypted_phone,
            kyc_verified=True,
            kyc_provider="admin_setup"
        )
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print("✅ Super Admin Created Successfully!")
        print(f"   Name: {super_admin.name}")
        print(f"   Phone: {phone_number}")
        print(f"   Password: {password}")
        print(f"   Role: {super_admin.admin_role}")
        
        return super_admin
        
    except Exception as e:
        print(f"❌ Error creating super admin: {e}")
        db.rollback()
        return None
    finally:
        db.close()


if __name__ == "__main__":
    create_super_admin()
