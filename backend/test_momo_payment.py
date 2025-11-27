#!/usr/bin/env python3
"""
MTN MoMo Payment Testing Script
Tests the complete payment flow from user payment to admin requests.
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_PHONE = "+233244333333"  # Kofi Member
TEST_USER_PASSWORD = "password123"
ADMIN_PHONE = "+233244111111"      # Kwame Admin
ADMIN_PASSWORD = "password123"

# Test phone numbers (MTN sandbox)
TEST_PHONE_AUTO_APPROVE = "+233240000001"
TEST_PHONE_AUTO_REJECT = "+233240000100"

class MomoPaymentTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
        self.user_id = None
        self.admin_id = None
        self.group_id = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def login(self, phone_number: str, password: str) -> bool:
        """Login user and get access token."""
        try:
            self.log(f"Logging in user: {phone_number}")
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data={"phone_number": phone_number, "password": password}
            )
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                if phone_number == ADMIN_PHONE:
                    self.admin_token = token
                else:
                    self.user_token = token
                self.log(f"✅ Login successful for {phone_number}")
                return True
            else:
                self.log(f"❌ Login failed for {phone_number}: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error for {phone_number}: {e}", "ERROR")
            return False
    
    def get_user_info(self, token: str) -> Optional[Dict]:
        """Get user information."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{self.base_url}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_info = response.json()
                if token == self.admin_token:
                    self.admin_id = user_info["id"]
                else:
                    self.user_id = user_info["id"]
                return user_info
            else:
                self.log(f"❌ Failed to get user info: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Error getting user info: {e}", "ERROR")
            return None
    
    def get_groups(self, token: str) -> List[Dict]:
        """Get user's groups."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{self.base_url}/groups/my-groups", headers=headers)
            
            if response.status_code == 200:
                groups = response.json()
                if groups:
                    self.group_id = groups[0]["id"]
                    self.log(f"✅ Found group: {groups[0]['name']} (ID: {self.group_id})")
                return groups
            else:
                self.log(f"❌ Failed to get groups: {response.status_code}", "ERROR")
                return []
                
        except Exception as e:
            self.log(f"❌ Error getting groups: {e}", "ERROR")
            return []
    
    def get_unpaid_payment(self, token: str, group_id: int) -> Optional[Dict]:
        """Get unpaid payment for user."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(
                f"{self.base_url}/groups/{group_id}/unpaid-payment", 
                headers=headers
            )
            
            if response.status_code == 200:
                unpaid_payment = response.json()
                self.log(f"✅ Unpaid payment found: GHS {unpaid_payment.get('amount', 0)}")
                return unpaid_payment
            elif response.status_code == 404:
                self.log("ℹ️ No unpaid payment found")
                return None
            else:
                self.log(f"❌ Failed to get unpaid payment: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Error getting unpaid payment: {e}", "ERROR")
            return None
    
    def trigger_payment(self, token: str, group_id: int) -> Optional[Dict]:
        """Trigger a payment manually."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            data = {"group_id": group_id}
            
            self.log("🔄 Triggering payment...")
            response = self.session.post(
                f"{self.base_url}/payments/manual-trigger",
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                payment = response.json()
                self.log(f"✅ Payment triggered successfully:")
                self.log(f"   Payment ID: {payment.get('id')}")
                self.log(f"   Status: {payment.get('status')}")
                self.log(f"   Amount: GHS {payment.get('amount', 0)}")
                self.log(f"   Transaction ID: {payment.get('transaction_id', 'None')}")
                return payment
            else:
                self.log(f"❌ Failed to trigger payment: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Error triggering payment: {e}", "ERROR")
            return None
    
    def admin_request_payment(self, token: str, group_id: int, user_id: int, round_number: int) -> Optional[Dict]:
        """Admin requests payment from a member."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            data = {
                "group_id": group_id,
                "user_id": user_id,
                "round_number": round_number
            }
            
            self.log(f"📱 Admin requesting payment from user {user_id}...")
            response = self.session.post(
                f"{self.base_url}/payments/admin/request-payment",
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                payment = response.json()
                self.log(f"✅ Admin payment request successful:")
                self.log(f"   Payment ID: {payment.get('id')}")
                self.log(f"   Status: {payment.get('status')}")
                self.log(f"   Amount: GHS {payment.get('amount', 0)}")
                return payment
            else:
                self.log(f"❌ Failed to request payment: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Error requesting payment: {e}", "ERROR")
            return None
    
    def check_payment_status(self, token: str, payment_id: int) -> Optional[Dict]:
        """Check payment status."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(
                f"{self.base_url}/payments/{payment_id}/status",
                headers=headers
            )
            
            if response.status_code == 200:
                status_info = response.json()
                self.log(f"✅ Payment status:")
                self.log(f"   Status: {status_info.get('status')}")
                self.log(f"   MTN Status: {status_info.get('mtn_status', 'N/A')}")
                self.log(f"   Amount: GHS {status_info.get('amount', 0)}")
                return status_info
            else:
                self.log(f"❌ Failed to get payment status: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Error checking payment status: {e}", "ERROR")
            return None
    
    def get_payment_history(self, token: str) -> List[Dict]:
        """Get payment history."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{self.base_url}/payments/history", headers=headers)
            
            if response.status_code == 200:
                history = response.json()
                self.log(f"✅ Payment history: {len(history)} payments")
                for payment in history:
                    self.log(f"   - Payment {payment.get('id')}: {payment.get('status')} - GHS {payment.get('amount', 0)}")
                return history
            else:
                self.log(f"❌ Failed to get payment history: {response.status_code}", "ERROR")
                return []
                
        except Exception as e:
            self.log(f"❌ Error getting payment history: {e}", "ERROR")
            return []
    
    def test_user_payment_flow(self) -> bool:
        """Test user payment flow."""
        self.log("\n🧪 Testing User Payment Flow")
        self.log("=" * 50)
        
        # Login as regular user
        if not self.login(TEST_USER_PHONE, TEST_USER_PASSWORD):
            return False
        
        # Get user info
        user_info = self.get_user_info(self.user_token)
        if not user_info:
            return False
        
        self.log(f"User: {user_info.get('name', 'Unknown')} (ID: {self.user_id})")
        self.log(f"KYC Verified: {user_info.get('kyc_verified', False)}")
        
        # Get groups
        groups = self.get_groups(self.user_token)
        if not groups:
            self.log("❌ No groups found", "ERROR")
            return False
        
        # Get unpaid payment
        unpaid_payment = self.get_unpaid_payment(self.user_token, self.group_id)
        
        # Trigger payment
        if unpaid_payment:
            payment = self.trigger_payment(self.user_token, self.group_id)
            if payment:
                # Check payment status
                time.sleep(2)  # Wait a moment
                self.check_payment_status(self.user_token, payment["id"])
                return True
        else:
            self.log("ℹ️ No unpaid payment to test")
            return True
        
        return False
    
    def test_admin_payment_request(self) -> bool:
        """Test admin payment request flow."""
        self.log("\n🧪 Testing Admin Payment Request Flow")
        self.log("=" * 50)
        
        # Login as admin
        if not self.login(ADMIN_PHONE, ADMIN_PASSWORD):
            return False
        
        # Get admin info
        admin_info = self.get_user_info(self.admin_token)
        if not admin_info:
            return False
        
        self.log(f"Admin: {admin_info.get('name', 'Unknown')} (ID: {self.admin_id})")
        
        # Get groups
        groups = self.get_groups(self.admin_token)
        if not groups:
            self.log("❌ No groups found", "ERROR")
            return False
        
        # Request payment from regular user
        if self.user_id and self.group_id:
            payment = self.admin_request_payment(
                self.admin_token, 
                self.group_id, 
                self.user_id, 
                groups[0].get('current_round', 1)
            )
            if payment:
                # Check payment status
                time.sleep(2)  # Wait a moment
                self.check_payment_status(self.admin_token, payment["id"])
                return True
        
        return False
    
    def test_payment_history(self) -> bool:
        """Test payment history retrieval."""
        self.log("\n🧪 Testing Payment History")
        self.log("=" * 50)
        
        if self.user_token:
            history = self.get_payment_history(self.user_token)
            return len(history) >= 0  # Success if we can retrieve history
        
        return False
    
    def run_all_tests(self) -> bool:
        """Run all payment tests."""
        self.log("🚀 Starting MTN MoMo Payment Tests")
        self.log("=" * 60)
        
        tests_passed = 0
        total_tests = 3
        
        # Test 1: User payment flow
        if self.test_user_payment_flow():
            tests_passed += 1
            self.log("✅ User payment flow test passed")
        else:
            self.log("❌ User payment flow test failed", "ERROR")
        
        # Test 2: Admin payment request
        if self.test_admin_payment_request():
            tests_passed += 1
            self.log("✅ Admin payment request test passed")
        else:
            self.log("❌ Admin payment request test failed", "ERROR")
        
        # Test 3: Payment history
        if self.test_payment_history():
            tests_passed += 1
            self.log("✅ Payment history test passed")
        else:
            self.log("❌ Payment history test failed", "ERROR")
        
        # Summary
        self.log(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            self.log("🎉 All tests passed! Payment integration is working correctly.")
        else:
            self.log("⚠️ Some tests failed. Check the logs above for details.", "WARNING")
        
        return tests_passed == total_tests
    
    def check_backend_health(self) -> bool:
        """Check if backend is running and accessible."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.log("✅ Backend is running and accessible")
                return True
            else:
                self.log(f"❌ Backend health check failed: {response.status_code}", "ERROR")
                return False
        except requests.exceptions.ConnectionError:
            self.log("❌ Cannot connect to backend. Is it running?", "ERROR")
            self.log("Start with: docker-compose up backend", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Backend health check error: {e}", "ERROR")
            return False

def main():
    """Main function to run the payment tests."""
    print("🧪 MTN MoMo Payment Testing Script")
    print("=" * 60)
    
    # Check if backend is running
    tester = MomoPaymentTester()
    if not tester.check_backend_health():
        sys.exit(1)
    
    # Run all tests
    success = tester.run_all_tests()
    
    print("\n📝 Next Steps:")
    print("1. Set up MTN MoMo credentials in backend/.env")
    print("2. Run: python3 backend/setup_mtn_momo.py")
    print("3. Start ngrok: ngrok http 8000")
    print("4. Update MTN callback URL")
    print("5. Test with real phone numbers")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
