#!/usr/bin/env python3
"""
MTN KYC Integration Test Script

This script tests the MTN KYC integration including:
- OAuth token retrieval
- Phone number verification
- MoMo account validation
- Full KYC verification flow

Usage:
    python test_mtn_kyc.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.mtn_kyc_integration import mtn_kyc_service
from app.config import settings


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(test_name, result, success=None):
    """Print test result."""
    if success is None:
        success = result.get("verified", False) or result.get("valid", False)
    
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    print(f"Result: {result}")


def test_configuration():
    """Test 1: Verify configuration."""
    print_header("TEST 1: Configuration Check")
    
    config = {
        "KYC Enabled": settings.ENABLE_MTN_KYC,
        "KYC Base URL": settings.MTN_KYC_BASE_URL,
        "MTN Environment": settings.MTN_ENVIRONMENT,
        "Consumer Key": settings.MTN_CONSUMER_KEY[:10] + "..." if settings.MTN_CONSUMER_KEY else None,
        "Require KYC for Payments": settings.REQUIRE_KYC_FOR_PAYMENTS,
    }
    
    print("\nConfiguration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Check if all required settings are present
    missing = []
    if not settings.MTN_CONSUMER_KEY:
        missing.append("MTN_CONSUMER_KEY")
    if not settings.MTN_CONSUMER_SECRET:
        missing.append("MTN_CONSUMER_SECRET")
    
    if missing:
        print(f"\n❌ FAIL - Missing configuration: {', '.join(missing)}")
        return False
    else:
        print("\n✅ PASS - All configuration present")
        return True


def test_oauth_token():
    """Test 2: OAuth token retrieval."""
    print_header("TEST 2: OAuth Token Retrieval")
    
    try:
        token = mtn_kyc_service._get_oauth_token()
        
        if token:
            print(f"\n✅ PASS - Token obtained")
            print(f"Token (first 20 chars): {token[:20]}...")
            return True
        else:
            print(f"\n❌ FAIL - No token received")
            return False
            
    except Exception as e:
        print(f"\n❌ FAIL - Error: {e}")
        return False


def test_phone_verification(phone_number):
    """Test 3: Phone number verification."""
    print_header("TEST 3: Phone Number Verification")
    
    print(f"\nTesting phone: {phone_number}")
    
    try:
        result = mtn_kyc_service.verify_phone_number(phone_number)
        print_result("Phone Verification", result, result.get("verified"))
        return result.get("verified", False)
        
    except Exception as e:
        print(f"\n❌ FAIL - Error: {e}")
        return False


def test_momo_validation(phone_number):
    """Test 4: MoMo account validation."""
    print_header("TEST 4: MoMo Account Validation")
    
    print(f"\nTesting phone: {phone_number}")
    
    try:
        result = mtn_kyc_service.verify_momo_account(phone_number)
        print_result("MoMo Validation", result, result.get("valid"))
        return result.get("valid", False)
        
    except Exception as e:
        print(f"\n❌ FAIL - Error: {e}")
        return False


def test_full_kyc(phone_number):
    """Test 5: Full KYC verification."""
    print_header("TEST 5: Full KYC Verification")
    
    print(f"\nTesting phone: {phone_number}")
    
    try:
        result = mtn_kyc_service.perform_kyc_verification(phone_number)
        
        print("\nKYC Verification Result:")
        print(f"  Overall Verified: {result.get('verified')}")
        print(f"  Phone Verified: {result.get('phone_verified')}")
        print(f"  MoMo Verified: {result.get('momo_verified')}")
        print(f"  Provider: {result.get('provider')}")
        print(f"  Message: {result.get('message')}")
        
        if result.get("details"):
            print("\nDetails:")
            print(f"  Phone Check: {result['details'].get('phone_check', {}).get('message')}")
            print(f"  MoMo Check: {result['details'].get('momo_check', {}).get('message')}")
        
        print_result("Full KYC", result, result.get("verified"))
        return result.get("verified", False)
        
    except Exception as e:
        print(f"\n❌ FAIL - Error: {e}")
        return False


def test_kyc_requirements():
    """Test 6: Get KYC requirements."""
    print_header("TEST 6: KYC Requirements")
    
    try:
        requirements = mtn_kyc_service.get_kyc_requirements()
        
        print("\nKYC Requirements:")
        print(f"  Required: {requirements.get('required')}")
        print(f"  Provider: {requirements.get('provider')}")
        print(f"  Country: {requirements.get('country')}")
        print(f"  Compliance: {requirements.get('compliance')}")
        print(f"  Help URL: {requirements.get('help_url')}")
        
        if requirements.get('checks'):
            print("\n  Checks:")
            for check in requirements['checks']:
                print(f"    - {check.get('name')}: {check.get('description')}")
        
        print("\n✅ PASS - Requirements retrieved")
        return True
        
    except Exception as e:
        print(f"\n❌ FAIL - Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  MTN KYC INTEGRATION TEST SUITE")
    print("=" * 80)
    print(f"\nEnvironment: {settings.MTN_ENVIRONMENT}")
    print(f"KYC Enabled: {settings.ENABLE_MTN_KYC}")
    
    # Test phone number
    # For sandbox, use MTN's test numbers
    # For production, use your actual phone number
    test_phone = "+233240000000"  # Replace with actual test number
    
    print(f"\nTest Phone Number: {test_phone}")
    print("\n⚠️  NOTE: For actual verification, use a real MTN Ghana number")
    print("⚠️  Sandbox may have limited functionality")
    
    # Confirm before proceeding
    response = input("\nProceed with tests? (yes/no): ")
    if response.lower() != "yes":
        print("Tests cancelled.")
        return
    
    # Run tests
    results = []
    
    # Test 1: Configuration
    results.append(("Configuration", test_configuration()))
    
    # Test 2: OAuth Token
    results.append(("OAuth Token", test_oauth_token()))
    
    # Only proceed with API tests if configuration is OK
    if results[0][1] and results[1][1]:
        # Test 3: Phone Verification
        results.append(("Phone Verification", test_phone_verification(test_phone)))
        
        # Test 4: MoMo Validation
        results.append(("MoMo Validation", test_momo_validation(test_phone)))
        
        # Test 5: Full KYC
        results.append(("Full KYC", test_full_kyc(test_phone)))
        
        # Test 6: Requirements
        results.append(("Requirements", test_kyc_requirements()))
    else:
        print("\n⚠️  Skipping API tests due to configuration/token errors")
    
    # Print summary
    print("\n" + "=" * 80)
    print("  TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    print("\nTest Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print("\n" + "=" * 80)
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check configuration and credentials.")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

