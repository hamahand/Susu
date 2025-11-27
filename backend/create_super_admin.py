"""
Script to create the first super admin user.
Run this once to set up the initial admin account.

Usage:
    python create_super_admin.py
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
    """Create the first super admin user."""
    db = SessionLocal()
    
    try:
        # Check if any super admin already exists
        existing_admin = db.query(User).filter(User.is_system_admin == True).first()
        if existing_admin:
            print("❌ A super admin already exists!")
            print(f"   Admin: {existing_admin.name}")
            try:
                phone = decrypt_field(existing_admin.phone_number)
                print(f"   Phone: {phone}")
            except:
                pass
            print("\n   To create additional admins, use the admin API or database directly.")
            return
        
        # Prompt for admin details
        print("🔐 Create Super Admin Account")
        print("=" * 50)
        
        name = input("Admin Name: ").strip()
        if not name:
            print("❌ Name cannot be empty")
            return
        
        phone_number = input("Phone Number (with country code, e.g., +233201234567): ").strip()
        if not phone_number.startswith("+"):
            print("❌ Phone number must start with + and country code")
            return
        
        # Check if user with this phone already exists
        all_users = db.query(User).all()
        for u in all_users:
            try:
                if decrypt_field(u.phone_number) == phone_number:
                    print(f"❌ User with phone {phone_number} already exists!")
                    print(f"   Would you like to promote this user to super admin? (y/n)")
                    choice = input().strip().lower()
                    if choice == 'y':
                        u.is_system_admin = True
                        u.admin_role = "super_admin"  # Pass string directly
                        db.add(u)
                        db.commit()
                        print(f"✅ User {u.name} promoted to Super Admin!")
                        return
                    else:
                        return
            except:
                continue
        
        password = input("Password (min 6 characters): ").strip()
        if len(password) < 6:
            print("❌ Password must be at least 6 characters")
            return
        
        confirm_password = input("Confirm Password: ").strip()
        if password != confirm_password:
            print("❌ Passwords do not match")
            return
        
        # Create super admin
        encrypted_phone = encrypt_field(phone_number)
        
        super_admin = User(
            phone_number=encrypted_phone,
            name=name,
            user_type=UserType.APP,
            password_hash=get_password_hash(password),
            is_system_admin=True,
            admin_role="super_admin",  # Pass string directly
            momo_account_id=encrypted_phone,
            kyc_verified=True,  # Auto-verify admin
            kyc_provider="admin_setup"
        )
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print("\n" + "=" * 50)
        print("✅ Super Admin Created Successfully!")
        print("=" * 50)
        print(f"   ID: {super_admin.id}")
        print(f"   Name: {super_admin.name}")
        print(f"   Phone: {phone_number}")
        print(f"   Role: {super_admin.admin_role.value}")
        print("\n🔑 You can now log in to the admin portal with these credentials.")
        print(f"   Admin API: http://localhost:8000/admin/")
        print(f"   API Docs: http://localhost:8000/docs#/Admin")
        
    except Exception as e:
        print(f"\n❌ Error creating super admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_super_admin()

