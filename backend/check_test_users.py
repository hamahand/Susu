#!/usr/bin/env python3
"""
Check if test users exist in the database.
"""

from app.database import SessionLocal
from app.models import User
from app.utils import decrypt_field

def check_test_users():
    """Check if test users exist in database."""
    print("🔍 Checking test users in database...")
    
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        if not users:
            print("❌ No users found in database.")
            print("Run: python3 seed_data.py")
            return False
        
        print(f"✅ Found {len(users)} users in database:")
        
        test_users = [
            ("+233244111111", "Kwame Admin"),
            ("+233244222222", "Ama Creator"), 
            ("+233244333333", "Kofi Member"),
            ("+233244444444", "Akua Member"),
            ("+233244555555", "Yaw Member")
        ]
        
        for user in users:
            try:
                decrypted_phone = decrypt_field(user.phone_number)
                user_name = user.name
                user_type = user.user_type.value if user.user_type else "Unknown"
                has_password = "Yes" if user.password_hash else "No"
                
                print(f"   📱 {decrypted_phone} - {user_name} ({user_type}) - Password: {has_password}")
                
            except Exception as e:
                print(f"   ❌ Could not decrypt user {user.id}: {e}")
        
        print(f"\n📝 Test users for login:")
        print(f"   Regular User: +233244333333 / password123")
        print(f"   Admin User: +233244111111 / password123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking users: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    check_test_users()
