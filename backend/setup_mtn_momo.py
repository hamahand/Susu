#!/usr/bin/env python3
"""
MTN MoMo Sandbox Setup Script

This script helps you set up MTN Mobile Money sandbox credentials.
It will:
1. Create an API user
2. Generate an API key
3. Update your .env file with the credentials

Prerequisites:
- MTN MoMo subscription key from https://momodeveloper.mtn.com/
- A callback host (e.g., your ngrok URL without https://)

Usage:
    python setup_mtn_momo.py
"""

import requests
import uuid
import os
import sys
from pathlib import Path


class MTNMoMoSetup:
    """Helper class for MTN MoMo sandbox setup."""
    
    def __init__(self):
        self.base_url = "https://sandbox.momodeveloper.mtn.com"
        self.subscription_key = None
        self.callback_host = None
        self.api_user = None
        self.api_key = None
    
    def prompt_user(self):
        """Prompt user for required information."""
        print("=" * 70)
        print("MTN MoMo Sandbox Setup")
        print("=" * 70)
        print("\nThis script will help you set up MTN MoMo sandbox credentials.")
        print("\nPrerequisites:")
        print("1. MTN MoMo subscription key from https://momodeveloper.mtn.com/")
        print("2. Callback host (e.g., your-ngrok-url.ngrok-free.app)")
        print("\n")
        
        # Get subscription key
        self.subscription_key = input("Enter your Collection Subscription Key: ").strip()
        if not self.subscription_key:
            print("❌ Error: Subscription key is required!")
            sys.exit(1)
        
        # Get callback host
        default_host = "your-app.ngrok-free.app"
        callback_input = input(f"Enter callback host (default: {default_host}): ").strip()
        self.callback_host = callback_input if callback_input else default_host
        
        # Remove https:// or http:// if present
        self.callback_host = self.callback_host.replace("https://", "").replace("http://", "")
        
        print(f"\n✓ Subscription Key: {self.subscription_key[:10]}...")
        print(f"✓ Callback Host: {self.callback_host}")
    
    def create_api_user(self):
        """Create API user in MTN MoMo sandbox."""
        print("\n" + "-" * 70)
        print("Step 1: Creating API User")
        print("-" * 70)
        
        # Generate UUID for API user
        self.api_user = str(uuid.uuid4())
        
        url = f"{self.base_url}/v1_0/apiuser"
        
        headers = {
            "X-Reference-Id": self.api_user,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "providerCallbackHost": self.callback_host
        }
        
        try:
            print(f"\nSending request to: {url}")
            print(f"API User ID: {self.api_user}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 201:
                print("✅ API User created successfully!")
                print(f"   API User ID: {self.api_user}")
                return True
            elif response.status_code == 409:
                print("⚠️  API User already exists (this is okay)")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def create_api_key(self):
        """Create API key for the API user."""
        print("\n" + "-" * 70)
        print("Step 2: Creating API Key")
        print("-" * 70)
        
        url = f"{self.base_url}/v1_0/apiuser/{self.api_user}/apikey"
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        }
        
        try:
            print(f"\nSending request to: {url}")
            
            response = requests.post(url, headers=headers, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                self.api_key = data.get("apiKey")
                print("✅ API Key created successfully!")
                print(f"   API Key: {self.api_key}")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def test_authentication(self):
        """Test authentication with the created credentials."""
        print("\n" + "-" * 70)
        print("Step 3: Testing Authentication")
        print("-" * 70)
        
        url = f"{self.base_url}/collection/token/"
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        }
        
        auth = (self.api_user, self.api_key)
        
        try:
            print(f"\nSending request to: {url}")
            
            response = requests.post(url, headers=headers, auth=auth, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                print("✅ Authentication successful!")
                print(f"   Access Token: {access_token[:20]}...")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def update_env_file(self):
        """Update .env file with the new credentials."""
        print("\n" + "-" * 70)
        print("Step 4: Updating .env File")
        print("-" * 70)
        
        env_path = Path(__file__).parent / ".env"
        env_example_path = Path(__file__).parent / "env.example"
        
        # Create .env from example if it doesn't exist
        if not env_path.exists():
            if env_example_path.exists():
                print(f"\nCreating .env from env.example...")
                with open(env_example_path, 'r') as f:
                    content = f.read()
                with open(env_path, 'w') as f:
                    f.write(content)
                print("✓ Created .env file")
            else:
                print("⚠️  Warning: No .env or env.example file found")
                print("   You'll need to create a .env file manually")
                return False
        
        # Read current .env
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update or add MTN MoMo credentials
        updates = {
            "MTN_MOMO_SUBSCRIPTION_KEY": self.subscription_key,
            "MTN_MOMO_API_USER": self.api_user,
            "MTN_MOMO_API_KEY": self.api_key,
        }
        
        updated_lines = []
        found_keys = set()
        
        for line in lines:
            updated = False
            for key, value in updates.items():
                if line.startswith(f"{key}="):
                    updated_lines.append(f"{key}={value}\n")
                    found_keys.add(key)
                    updated = True
                    break
            
            if not updated:
                updated_lines.append(line)
        
        # Add missing keys
        for key, value in updates.items():
            if key not in found_keys:
                updated_lines.append(f"{key}={value}\n")
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        
        print(f"\n✅ Updated {env_path}")
        print("\nAdded/Updated:")
        for key in updates.keys():
            print(f"   ✓ {key}")
        
        return True
    
    def display_summary(self):
        """Display setup summary."""
        print("\n" + "=" * 70)
        print("Setup Complete! 🎉")
        print("=" * 70)
        
        print("\nYour MTN MoMo Sandbox Credentials:")
        print(f"   Subscription Key: {self.subscription_key}")
        print(f"   API User:         {self.api_user}")
        print(f"   API Key:          {self.api_key}")
        print(f"   Callback Host:    {self.callback_host}")
        
        print("\n⚠️  IMPORTANT:")
        print("   - Keep these credentials secure!")
        print("   - Never commit them to version control")
        print("   - These are for SANDBOX only (testing)")
        
        print("\nNext Steps:")
        print("   1. Restart your backend server")
        print("   2. Test MoMo integration:")
        print("      python test_mtn_momo.py")
        print("   3. Check the MTN_SETUP.md documentation for more details")
        
        print("\nFor production:")
        print("   - Get production subscription keys from MTN")
        print("   - Repeat this process with production credentials")
        print("   - Update MTN_MOMO_TARGET_ENVIRONMENT=production")
        print("   - Update MTN_MOMO_BASE_URL to production URL")
        
        print("\n" + "=" * 70)
    
    def run(self):
        """Run the complete setup process."""
        try:
            # Step 0: Prompt user for inputs
            self.prompt_user()
            
            # Step 1: Create API user
            if not self.create_api_user():
                print("\n❌ Setup failed at API User creation")
                sys.exit(1)
            
            # Step 2: Create API key
            if not self.create_api_key():
                print("\n❌ Setup failed at API Key creation")
                sys.exit(1)
            
            # Step 3: Test authentication
            if not self.test_authentication():
                print("\n⚠️  Warning: Authentication test failed")
                print("   But credentials were created. You can try using them anyway.")
            
            # Step 4: Update .env file
            self.update_env_file()
            
            # Display summary
            self.display_summary()
            
        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    setup = MTNMoMoSetup()
    setup.run()


if __name__ == "__main__":
    main()

