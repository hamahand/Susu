#!/usr/bin/env python3
"""
Quick MTN MoMo Payment Test
Simple script to test basic payment functionality.
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PHONE = "+233244333333"  # Kofi Member from seed data
TEST_PASSWORD = "password123"

def quick_test():
    """Quick test of payment functionality."""
    print("🧪 Quick MTN MoMo Payment Test")
    print("=" * 40)
    
    # 1. Login
    print("\n1. 🔐 Logging in...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "phone_number": TEST_PHONE,
            "password": TEST_PASSWORD
        })
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        print("Start with: docker-compose up backend")
        return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # 2. Get user info
    print("\n2. 👤 Getting user info...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ User: {user_info.get('name', 'Unknown')}")
            print(f"   Email: {user_info.get('email', 'Unknown')}")
            print(f"   KYC Verified: {user_info.get('kyc_verified', False)}")
        else:
            print(f"❌ Failed to get user info: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        return False
    
    # 3. Get groups
    print("\n3. 👥 Getting user groups...")
    try:
        response = requests.get(f"{BASE_URL}/groups/my-groups", headers=headers)
        if response.status_code == 200:
            groups = response.json()
            if not groups:
                print("❌ No groups found. Create a group first.")
                return False
            
            group = groups[0]
            print(f"✅ Found group: {group.get('name', 'Unknown')}")
            print(f"   ID: {group.get('id')}")
            print(f"   Contribution: GHS {group.get('contribution_amount', 0)}")
            print(f"   Cash Only: {group.get('cash_only', False)}")
            
            group_id = group["id"]
        else:
            print(f"❌ Failed to get groups: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting groups: {e}")
        return False
    
    # 4. Test payment trigger
    print("\n4. 💰 Testing payment trigger...")
    try:
        data = {"group_id": group_id}
        response = requests.post(f"{BASE_URL}/payments/manual-trigger", 
                               json=data, headers=headers)
        
        if response.status_code == 200:
            payment = response.json()
            print(f"✅ Payment triggered successfully:")
            print(f"   Payment ID: {payment.get('id')}")
            print(f"   Status: {payment.get('status')}")
            print(f"   Amount: GHS {payment.get('amount', 0)}")
            print(f"   Transaction ID: {payment.get('transaction_id', 'None')}")
            return True
        else:
            print(f"❌ Failed to trigger payment: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error triggering payment: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    
    if success:
        print("\n🎉 Quick test passed!")
        print("\n📝 Next steps:")
        print("1. Set up MTN MoMo credentials")
        print("2. Run: python3 setup_mtn_momo.py")
        print("3. Test with full script: python3 test_momo_payment.py")
    else:
        print("\n❌ Quick test failed!")
        print("Check the error messages above for details.")
    
    sys.exit(0 if success else 1)
