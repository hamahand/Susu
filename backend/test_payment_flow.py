#!/usr/bin/env python3
"""
Test script for payment flow to verify the setup is working correctly.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

def test_payment_flow():
    """Test the complete payment flow."""
    print("🧪 Testing Payment Flow Setup")
    print("=" * 50)
    
    # Step 1: Login
    print("\n1. 🔐 Logging in...")
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
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
    
    # Step 2: Get user info
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
    
    # Step 3: Get groups
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
            print(f"   Current Round: {group.get('current_round', 1)}")
            
            group_id = group["id"]
        else:
            print(f"❌ Failed to get groups: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting groups: {e}")
        return False
    
    # Step 4: Get unpaid payment
    print("\n4. 💰 Getting unpaid payment...")
    try:
        response = requests.get(f"{BASE_URL}/groups/{group_id}/unpaid-payment", headers=headers)
        if response.status_code == 200:
            unpaid_payment = response.json()
            print(f"✅ Unpaid payment found:")
            print(f"   Amount: GHS {unpaid_payment.get('amount', 0)}")
            print(f"   Round: {unpaid_payment.get('round_number', 1)}")
            print(f"   Payment ID: {unpaid_payment.get('id')}")
            
            payment_id = unpaid_payment["id"]
        elif response.status_code == 404:
            print("ℹ️  No unpaid payment found (already paid or not applicable)")
            # Try to trigger a new payment
            print("\n5. 🔄 Triggering new payment...")
            trigger_data = {"group_id": group_id}
            response = requests.post(f"{BASE_URL}/payments/manual-trigger", 
                                   json=trigger_data, headers=headers)
            if response.status_code == 200:
                payment = response.json()
                print(f"✅ Payment triggered:")
                print(f"   Payment ID: {payment.get('id')}")
                print(f"   Status: {payment.get('status')}")
                print(f"   Transaction ID: {payment.get('transaction_id', 'None')}")
                return True
            else:
                print(f"❌ Failed to trigger payment: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        else:
            print(f"❌ Failed to get unpaid payment: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting unpaid payment: {e}")
        return False
    
    # Step 5: Test payment status
    print("\n5. 📊 Checking payment status...")
    try:
        response = requests.get(f"{BASE_URL}/payments/{payment_id}/status", headers=headers)
        if response.status_code == 200:
            status_info = response.json()
            print(f"✅ Payment status:")
            print(f"   Status: {status_info.get('status')}")
            print(f"   MTN Status: {status_info.get('mtn_status', 'N/A')}")
            print(f"   Amount: GHS {status_info.get('amount', 0)}")
        else:
            print(f"❌ Failed to get payment status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting payment status: {e}")
    
    print("\n🎉 Payment flow test completed!")
    print("\n📝 Next steps:")
    print("1. Set up MTN MoMo credentials in backend/.env")
    print("2. Run: python3 backend/setup_mtn_momo.py")
    print("3. Start ngrok: ngrok http 8000")
    print("4. Update MTN callback URL")
    print("5. Test with real phone numbers")
    
    return True

if __name__ == "__main__":
    success = test_payment_flow()
    sys.exit(0 if success else 1)
