#!/usr/bin/env python3
"""
Test script for MTN MoMo payment flow.

This script tests the complete payment flow:
1. User initiates payment
2. Admin requests payment from member
3. Check payment status

Usage:
    python test_mtn_momo_payment.py
"""

import requests
import json
import sys
from typing import Optional


class MoMoPaymentTester:
    """Helper class for testing MTN MoMo payments."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.admin_token = None
    
    def login(self, phone_number: str, password: str) -> Optional[str]:
        """Login and get auth token."""
        url = f"{self.base_url}/auth/login"
        
        data = {
            "phone_number": phone_number,
            "password": password
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get("access_token")
                print(f"✅ Login successful")
                return token
            else:
                print(f"❌ Login failed: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Login request failed: {e}")
            return None
    
    def get_user_groups(self, token: str):
        """Get user's groups."""
        url = f"{self.base_url}/groups/my-groups"
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                groups = response.json()
                print(f"\n📊 User's Groups ({len(groups)}):")
                for group in groups:
                    print(f"   - {group['name']} (ID: {group['id']})")
                return groups
            else:
                print(f"❌ Failed to get groups: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return []
    
    def request_payment_as_admin(
        self,
        token: str,
        group_id: int,
        user_id: int,
        round_number: int
    ):
        """Admin requests payment from a member."""
        url = f"{self.base_url}/payments/admin/request-payment"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "group_id": group_id,
            "user_id": user_id,
            "round_number": round_number
        }
        
        try:
            print(f"\n📱 Requesting payment from user {user_id} for group {group_id}...")
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                payment = response.json()
                print(f"✅ Payment request sent!")
                print(f"   Payment ID: {payment['id']}")
                print(f"   Amount: GHS {payment['amount']}")
                print(f"   Status: {payment['status']}")
                print(f"   Transaction ID: {payment.get('transaction_id', 'N/A')}")
                return payment
            else:
                print(f"❌ Payment request failed: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def pay_own_payment(self, token: str, payment_id: int):
        """User pays their own payment."""
        url = f"{self.base_url}/payments/{payment_id}/pay-now"
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            print(f"\n💳 Paying payment ID {payment_id}...")
            
            response = requests.post(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                payment = response.json()
                print(f"✅ Payment initiated!")
                print(f"   Payment ID: {payment['id']}")
                print(f"   Amount: GHS {payment['amount']}")
                print(f"   Status: {payment['status']}")
                print(f"   Transaction ID: {payment.get('transaction_id', 'N/A')}")
                return payment
            else:
                print(f"❌ Payment failed: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def check_payment_status(self, token: str, payment_id: int):
        """Check payment status."""
        url = f"{self.base_url}/payments/{payment_id}/status"
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                status = response.json()
                print(f"\n🔍 Payment Status:")
                print(f"   Payment ID: {status['payment_id']}")
                print(f"   Local Status: {status['status']}")
                print(f"   MTN Status: {status.get('mtn_status', 'N/A')}")
                print(f"   Amount: GHS {status['amount']}")
                print(f"   Transaction ID: {status.get('transaction_id', 'N/A')}")
                return status
            else:
                print(f"❌ Status check failed: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def run_test_scenario_1(self):
        """Test Scenario 1: User pays their own contribution."""
        print("\n" + "=" * 70)
        print("Test Scenario 1: User Pays Own Contribution")
        print("=" * 70)
        
        # Login as member
        print("\n1. Login as member...")
        phone = input("Member phone number (e.g., +233240000001): ").strip()
        password = input("Password: ").strip()
        
        token = self.login(phone, password)
        if not token:
            print("❌ Test failed: Could not login")
            return
        
        # Get groups
        print("\n2. Get user's groups...")
        groups = self.get_user_groups(token)
        if not groups:
            print("❌ Test failed: No groups found")
            return
        
        # Select group
        group_id = int(input(f"\nEnter group ID to pay: "))
        
        # For this test, we'll create a payment first
        # In real scenario, payment would already exist
        print("\n3. Initiating payment...")
        payment = self.request_payment_as_admin(token, group_id, 1, 1)
        
        if payment:
            print("\n4. Checking payment status...")
            import time
            time.sleep(2)
            self.check_payment_status(token, payment['id'])
    
    def run_test_scenario_2(self):
        """Test Scenario 2: Admin requests payment from member."""
        print("\n" + "=" * 70)
        print("Test Scenario 2: Admin Requests Payment from Member")
        print("=" * 70)
        
        # Login as admin
        print("\n1. Login as admin...")
        admin_phone = input("Admin phone number (e.g., +233598430399): ").strip()
        admin_password = input("Admin password: ").strip()
        
        admin_token = self.login(admin_phone, admin_password)
        if not admin_token:
            print("❌ Test failed: Could not login as admin")
            return
        
        # Get groups
        print("\n2. Get admin's groups...")
        groups = self.get_user_groups(admin_token)
        if not groups:
            print("❌ Test failed: No groups found")
            return
        
        # Select group and member
        group_id = int(input("\nEnter group ID: "))
        member_id = int(input("Enter member user ID: "))
        round_number = int(input("Enter round number: "))
        
        # Request payment
        print("\n3. Requesting payment from member...")
        payment = self.request_payment_as_admin(
            admin_token,
            group_id,
            member_id,
            round_number
        )
        
        if payment:
            print("\n4. Checking payment status...")
            import time
            time.sleep(2)
            self.check_payment_status(admin_token, payment['id'])
    
    def run_interactive_test(self):
        """Run interactive test."""
        print("\n" + "=" * 70)
        print("MTN MoMo Payment Flow Tester")
        print("=" * 70)
        
        print("\nSelect test scenario:")
        print("1. User pays own contribution")
        print("2. Admin requests payment from member")
        print("3. Check existing payment status")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            self.run_test_scenario_1()
        elif choice == "2":
            self.run_test_scenario_2()
        elif choice == "3":
            token = self.login(
                input("Phone number: ").strip(),
                input("Password: ").strip()
            )
            if token:
                payment_id = int(input("Payment ID: "))
                self.check_payment_status(token, payment_id)
        elif choice == "4":
            print("\nExiting...")
            return
        else:
            print("\n❌ Invalid choice")
        
        # Ask to run another test
        if input("\nRun another test? (y/n): ").lower() == 'y':
            self.run_interactive_test()


def main():
    """Main entry point."""
    tester = MoMoPaymentTester()
    
    try:
        tester.run_interactive_test()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

