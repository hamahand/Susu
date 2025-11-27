#!/usr/bin/env python3
"""
Test script for MTN integrations (USSD, SMS, MoMo)

This script tests all MTN services to ensure they're configured correctly.

Usage:
    python test_mtn_integration.py
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.integrations.mtn_ussd_integration import mtn_ussd_service
from app.integrations.mtn_sms_integration import mtn_sms_service
from app.integrations.mtn_momo_integration import mtn_momo_service


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


def test_configuration():
    """Test if MTN services are configured."""
    print_header("MTN Configuration Check")
    
    print("\n📋 Configuration Status:")
    print(f"   USE_MTN_SERVICES: {settings.USE_MTN_SERVICES}")
    print(f"   MTN_ENVIRONMENT: {settings.MTN_ENVIRONMENT}")
    print(f"   MTN_CONSUMER_KEY: {settings.MTN_CONSUMER_KEY[:10]}...")
    print(f"   MTN_CONSUMER_SECRET: {'*' * 20}")
    
    print("\n📱 USSD Configuration:")
    print(f"   ENABLE_MTN_USSD: {settings.ENABLE_MTN_USSD}")
    print(f"   SERVICE_CODE: {settings.MTN_USSD_SERVICE_CODE}")
    print(f"   CALLBACK_URL: {settings.MTN_CALLBACK_URL}")
    print(f"   USSD Service Status: {'✅ Enabled' if mtn_ussd_service.enabled else '❌ Disabled'}")
    
    print("\n💬 SMS Configuration:")
    print(f"   ENABLE_MTN_SMS: {settings.ENABLE_MTN_SMS}")
    print(f"   SMS Service Status: {'✅ Enabled' if mtn_sms_service.enabled else '❌ Disabled'}")
    
    print("\n💰 MoMo Configuration:")
    print(f"   ENABLE_MTN_MOMO: {settings.ENABLE_MTN_MOMO}")
    print(f"   TARGET_ENVIRONMENT: {settings.MTN_MOMO_TARGET_ENVIRONMENT}")
    print(f"   CURRENCY: {settings.MTN_MOMO_CURRENCY}")
    
    if settings.MTN_MOMO_API_USER:
        print(f"   API_USER: {settings.MTN_MOMO_API_USER[:10]}...")
    else:
        print(f"   API_USER: ⚠️  NOT CONFIGURED")
    
    if settings.MTN_MOMO_API_KEY:
        print(f"   API_KEY: {'*' * 20}")
    else:
        print(f"   API_KEY: ⚠️  NOT CONFIGURED")
    
    print(f"   MoMo Service Status: {'✅ Enabled' if mtn_momo_service.enabled else '❌ Disabled'}")
    
    # Check if all required configs are present
    all_configured = all([
        settings.MTN_CONSUMER_KEY,
        settings.MTN_CONSUMER_SECRET,
        settings.USE_MTN_SERVICES
    ])
    
    if all_configured:
        print("\n✅ Basic MTN configuration is complete!")
        return True
    else:
        print("\n❌ MTN configuration is incomplete!")
        print("   Please check your .env file and ensure all required values are set.")
        return False


def test_ussd():
    """Test USSD integration."""
    print_header("Testing MTN USSD Integration")
    
    if not mtn_ussd_service.enabled:
        print("⚠️  USSD service is disabled. Skipping test.")
        return False
    
    print_section("Test 1: Format Response")
    
    try:
        # Test continue response
        continue_response = mtn_ussd_service.continue_session("Welcome to SusuSave\n1. Join Group\n2. My Groups")
        print(f"✓ Continue Response: {continue_response[:50]}...")
        
        # Test end response
        end_response = mtn_ussd_service.end_session("test123", "Thank you!")
        print(f"✓ End Response: {end_response[:50]}...")
        
        print("\n✅ USSD formatting works correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ USSD test failed: {e}")
        return False


def test_sms():
    """Test SMS integration."""
    print_header("Testing MTN SMS Integration")
    
    if not mtn_sms_service.enabled:
        print("⚠️  SMS service is disabled. Skipping test.")
        return False
    
    # Get test phone number
    test_phone = input("\nEnter a test phone number (or press Enter to skip): ").strip()
    
    if not test_phone:
        print("⚠️  Skipping SMS test (no phone number provided)")
        return None
    
    print_section("Test 1: Send Test SMS")
    
    try:
        result = mtn_sms_service.send_single_sms(
            phone_number=test_phone,
            message="Test SMS from SusuSave MTN Integration"
        )
        
        if result.get("sent"):
            print(f"✅ SMS sent successfully!")
            print(f"   Message ID: {result.get('message_id')}")
            print(f"   Status: {result.get('status')}")
            return True
        else:
            print(f"❌ SMS failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"\n❌ SMS test failed: {e}")
        return False


def test_momo():
    """Test MoMo integration."""
    print_header("Testing MTN MoMo Integration")
    
    if not mtn_momo_service.enabled:
        print("⚠️  MoMo service is disabled. Skipping test.")
        return False
    
    # Check if MoMo is properly configured
    if not settings.MTN_MOMO_API_USER or not settings.MTN_MOMO_API_KEY:
        print("❌ MoMo credentials not configured!")
        print("   Run: python setup_mtn_momo.py")
        return False
    
    print_section("Test 1: Account Validation")
    
    # Get test phone number
    test_phone = input("\nEnter a test phone number for MoMo (or press Enter to skip): ").strip()
    
    if not test_phone:
        print("⚠️  Skipping MoMo test (no phone number provided)")
        return None
    
    try:
        # Test account validation
        print(f"\nValidating account: {test_phone}")
        validation_result = mtn_momo_service.validate_account(test_phone)
        
        print(f"Result: {validation_result}")
        
        if validation_result.get("valid"):
            print("✅ Account is valid!")
        else:
            print(f"⚠️  Account validation: {validation_result.get('message')}")
        
        print_section("Test 2: Payment Request")
        
        # Ask if user wants to test payment
        test_payment = input("\n⚠️  Test payment request? This will send a prompt to the phone (y/N): ").strip().lower()
        
        if test_payment == 'y':
            print("\nRequesting test payment of GHS 1.00...")
            
            payment_result = mtn_momo_service.request_to_pay(
                phone_number=test_phone,
                amount=1.00,
                reference="TEST_" + os.urandom(4).hex().upper(),
                payer_message="Test payment from SusuSave",
                payee_note="Test transaction"
            )
            
            print(f"\nPayment Request Result:")
            print(f"   Status: {payment_result.get('status')}")
            print(f"   Reference ID: {payment_result.get('reference_id')}")
            print(f"   Message: {payment_result.get('message')}")
            
            if payment_result.get("status") == "pending":
                print("\n✅ Payment request sent successfully!")
                print("   Check the test phone for payment prompt")
                
                # Wait a bit and check status
                check_status = input("\nCheck payment status? (y/N): ").strip().lower()
                
                if check_status == 'y':
                    import time
                    print("\nWaiting 5 seconds...")
                    time.sleep(5)
                    
                    reference_id = payment_result.get("reference_id")
                    status_result = mtn_momo_service.get_transaction_status(reference_id)
                    
                    print(f"\nTransaction Status:")
                    print(f"   Status: {status_result.get('status')}")
                    print(f"   Amount: {status_result.get('amount')}")
                    print(f"   Currency: {status_result.get('currency')}")
                    
                    if status_result.get("status") == "successful":
                        print("✅ Payment completed successfully!")
                        return True
                    elif status_result.get("status") == "pending":
                        print("⏳ Payment is still pending")
                        return None
                    else:
                        print(f"❌ Payment failed: {status_result.get('reason')}")
                        return False
            else:
                print(f"❌ Payment request failed")
                return False
        else:
            print("⚠️  Skipped payment test")
            return None
            
    except Exception as e:
        print(f"\n❌ MoMo test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test runner."""
    print_header("MTN Integration Test Suite")
    print("\nThis script will test your MTN USSD, SMS, and MoMo integrations.")
    print("\n⚠️  Note: Some tests will send real requests to MTN sandbox.")
    print("   Make sure you have valid sandbox credentials configured.")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    results = {}
    
    # Test configuration
    results['config'] = test_configuration()
    
    if not results['config']:
        print("\n❌ Configuration test failed. Please fix configuration before proceeding.")
        return
    
    # Test USSD
    results['ussd'] = test_ussd()
    
    # Test SMS
    results['sms'] = test_sms()
    
    # Test MoMo
    results['momo'] = test_momo()
    
    # Summary
    print_header("Test Summary")
    
    print("\n📊 Results:")
    for service, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  SKIPPED"
        
        print(f"   {service.upper():10s}: {status}")
    
    # Overall status
    failed_tests = [k for k, v in results.items() if v is False]
    
    if failed_tests:
        print(f"\n❌ {len(failed_tests)} test(s) failed: {', '.join(failed_tests)}")
        print("\nPlease check:")
        print("   1. Your .env configuration")
        print("   2. MTN Developer Portal settings")
        print("   3. Network connectivity")
        print("   4. MTN sandbox status")
    else:
        print("\n✅ All tests passed or skipped!")
        print("\nYour MTN integration is ready to use!")
    
    print("\n" + "=" * 70)
    print("For more information, see: backend/docs/MTN_SETUP.md")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Tests cancelled by user")
        sys.exit(1)

