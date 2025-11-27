#!/usr/bin/env python3
"""
Fix AfricasTalking USSD Network Error

This script helps you configure AfricasTalking USSD properly to resolve network errors.
"""

import os
import sys
from pathlib import Path

def main():
    print("🔧 AfricasTalking USSD Network Error Fix")
    print("=" * 50)
    
    # Check if .env exists
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Please run: cp env.example .env")
        return
    
    print("✅ .env file found")
    
    # Read current configuration
    with open(env_path, 'r') as f:
        content = f.read()
    
    print("\n📋 Current Configuration Issues:")
    print("-" * 30)
    
    issues = []
    
    # Check AT_API_KEY
    if "AT_API_KEY=your-at-api-key-from-dashboard" in content:
        issues.append("❌ AT_API_KEY is placeholder - needs real API key")
    else:
        print("✅ AT_API_KEY is configured")
    
    # Check provider setting
    if "USE_MTN_SERVICES=True" in content:
        issues.append("⚠️  USE_MTN_SERVICES=True - should be False for AfricasTalking")
    else:
        print("✅ USE_MTN_SERVICES is set to False (AfricasTalking)")
    
    # Check callback URL
    if "ngrok" in content:
        issues.append("⚠️  Using ngrok URL - may be expired or not registered")
    
    if issues:
        print("\n🚨 Issues Found:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n🛠️  Solution Steps:")
        print("=" * 30)
        
        print("\n1️⃣ Get AfricasTalking API Key:")
        print("   • Go to: https://account.africastalking.com/")
        print("   • Login to your account")
        print("   • Go to Settings → API Key")
        print("   • Copy your API key (starts with 'atsk_')")
        
        print("\n2️⃣ Update .env file:")
        print("   • Replace AT_API_KEY=your-at-api-key-from-dashboard")
        print("   • With AT_API_KEY=atsk_your_actual_key_here")
        
        print("\n3️⃣ Switch to AfricasTalking provider:")
        print("   • Change USE_MTN_SERVICES=True to USE_MTN_SERVICES=False")
        
        print("\n4️⃣ Update callback URL:")
        print("   • Get a permanent ngrok URL or deploy to production")
        print("   • Register the URL in AfricasTalking dashboard")
        
        print("\n5️⃣ Test the configuration:")
        print("   • Run: python verify_ussd_setup.py")
        print("   • Run: python test_africastalking_ussd.py test")
        
        # Offer to make changes
        print("\n🤖 Would you like me to help you make these changes?")
        print("   (You'll need to provide your AfricasTalking API key)")
        
    else:
        print("\n✅ No issues found! Your configuration looks good.")
        print("\n🧪 Testing AfricasTalking connection...")
        
        # Test the connection
        try:
            import requests
            response = requests.get('http://localhost:8000/ussd/health', timeout=5)
            if response.status_code == 200:
                print("✅ USSD endpoint is healthy")
                data = response.json()
                print(f"   Provider: {data.get('provider', 'Unknown')}")
                print(f"   Service Code: {data.get('service_code', 'Unknown')}")
            else:
                print(f"❌ USSD endpoint returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Cannot connect to USSD endpoint: {e}")
            print("   Make sure the backend is running: python -m uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()
