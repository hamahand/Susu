#!/usr/bin/env python3
"""
Quick test to validate your MTN MoMo subscription key.
"""

import requests
import sys

def test_subscription_key(subscription_key):
    """Test if the subscription key is valid."""
    
    print("Testing MTN MoMo Subscription Key...")
    print(f"Key: {subscription_key[:10]}...")
    
    # Try to access the collection API
    url = "https://sandbox.momodeveloper.mtn.com/collection/v1_0/account/balance"
    
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 401:
            print("✅ Subscription key is valid!")
            print("   (401 is expected without API user - key format is correct)")
            return True
        elif response.status_code == 403:
            print("❌ Subscription key is invalid or not authorized")
            return False
        else:
            print(f"Response: {response.status_code}")
            print(f"Body: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        key = sys.argv[1]
    else:
        key = input("Enter your Collection Subscription Key: ").strip()
    
    if key:
        test_subscription_key(key)
    else:
        print("❌ No key provided")

