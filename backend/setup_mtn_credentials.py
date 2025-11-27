#!/usr/bin/env python3
"""
Helper script to set up MTN credentials interactively.
This script helps you configure your .env file with MTN credentials.

Usage:
    python setup_mtn_credentials.py
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_info(text):
    """Print info message."""
    print(f"ℹ️  {text}")


def print_success(text):
    """Print success message."""
    print(f"✅ {text}")


def print_warning(text):
    """Print warning message."""
    print(f"⚠️  {text}")


def print_error(text):
    """Print error message."""
    print(f"❌ {text}")


def get_input(prompt, default=None, required=True):
    """Get user input with optional default."""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    value = input(full_prompt).strip()
    
    if not value and default:
        return default
    
    if not value and required:
        print_warning("This field is required!")
        return get_input(prompt, default, required)
    
    return value


def update_env_file(env_path, updates):
    """Update .env file with new values."""
    # Read existing file
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        print_error(f".env file not found at {env_path}")
        return False
    
    # Update lines
    updated_lines = []
    keys_updated = set()
    
    for line in lines:
        updated = False
        for key, value in updates.items():
            if line.startswith(f"{key}="):
                updated_lines.append(f"{key}={value}\n")
                keys_updated.add(key)
                updated = True
                break
        
        if not updated:
            updated_lines.append(line)
    
    # Add any keys that weren't in the file
    for key, value in updates.items():
        if key not in keys_updated:
            updated_lines.append(f"\n{key}={value}\n")
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    return True


def main():
    """Main setup function."""
    print_header("MTN Credentials Setup Assistant")
    
    print("This script will help you configure MTN credentials in your .env file.")
    print("You'll need credentials from:")
    print("  1. MTN Developer Portal (https://developer.mtn.com/)")
    print("  2. MTN MoMo Developer Portal (https://momodeveloper.mtn.com/)")
    print()
    
    # Find .env file
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print_warning(".env file not found. Creating from env.example...")
        example_path = Path(__file__).parent / "env.example"
        if example_path.exists():
            import shutil
            shutil.copy(example_path, env_path)
            print_success("Created .env file")
        else:
            print_error("env.example not found!")
            return 1
    
    print_info(f"Will update: {env_path}")
    print()
    
    # Ask if user has credentials
    print("Do you have your MTN credentials ready?")
    print("  If not, visit: https://developer.mtn.com/ to get them")
    ready = get_input("Continue? (yes/no)", "yes", required=True).lower()
    
    if ready not in ['yes', 'y']:
        print()
        print_info("Please get your credentials first, then run this script again.")
        print_info("See MTN_CREDENTIALS_SETUP_GUIDE.md for detailed instructions.")
        return 0
    
    updates = {}
    
    # MTN API Credentials
    print_header("1. MTN API Credentials (SMS & USSD)")
    print("From: https://developer.mtn.com/ → Your App → Credentials")
    print()
    
    consumer_key = get_input("MTN Consumer Key", required=True)
    consumer_secret = get_input("MTN Consumer Secret", required=True)
    
    updates['MTN_CONSUMER_KEY'] = consumer_key
    updates['MTN_CONSUMER_SECRET'] = consumer_secret
    
    # Environment
    print()
    env_type = get_input("Environment (sandbox/production)", "sandbox", required=True)
    updates['MTN_ENVIRONMENT'] = env_type
    
    # Base URL
    print()
    print("API Base URL - Check MTN documentation for Ghana:")
    print("  Sandbox: https://sandbox.api.mtn.com/v1")
    print("  Production: https://api.mtn.com/gh/v1")
    base_url = get_input("MTN Base URL", "https://sandbox.api.mtn.com/v1", required=True)
    updates['MTN_BASE_URL'] = base_url
    
    # Callback URL
    print()
    print("Callback URL - Your public USSD endpoint:")
    print("  With ngrok: https://abc123.ngrok-free.app/ussd/callback")
    print("  Production: https://api.yourdomain.com/ussd/callback")
    callback_url = get_input("MTN Callback URL", required=True)
    updates['MTN_CALLBACK_URL'] = callback_url
    
    # MTN Mobile Money
    print_header("2. MTN Mobile Money Credentials")
    print("From: https://momodeveloper.mtn.com/ → Your App → Credentials")
    print()
    
    has_momo = get_input("Do you have MTN MoMo credentials? (yes/no)", "no").lower()
    
    if has_momo in ['yes', 'y']:
        momo_sub_key = get_input("MoMo Subscription Key", required=True)
        momo_api_user = get_input("MoMo API User (UUID)", required=True)
        momo_api_key = get_input("MoMo API Key", required=True)
        
        updates['MTN_MOMO_SUBSCRIPTION_KEY'] = momo_sub_key
        updates['MTN_MOMO_API_USER'] = momo_api_user
        updates['MTN_MOMO_API_KEY'] = momo_api_key
        updates['MTN_MOMO_TARGET_ENVIRONMENT'] = env_type
        updates['ENABLE_MTN_MOMO'] = 'true'
    else:
        print_info("Skipping MoMo credentials. You can add them later.")
        updates['ENABLE_MTN_MOMO'] = 'false'
    
    # Enable services
    print_header("3. Enable MTN Services")
    
    updates['USE_MTN_SERVICES'] = 'true'
    updates['ENABLE_MTN_USSD'] = 'true'
    updates['ENABLE_MTN_SMS'] = 'true'
    updates['ENABLE_MTN_KYC'] = 'true'
    
    # Security keys
    print_header("4. Security Keys")
    
    generate_keys = get_input("Generate new security keys? (recommended) (yes/no)", "yes").lower()
    
    if generate_keys in ['yes', 'y']:
        print_info("Generating SECRET_KEY...")
        import secrets
        secret_key = secrets.token_hex(32)
        updates['SECRET_KEY'] = secret_key
        print_success("Generated SECRET_KEY")
        
        print_info("Generating ENCRYPTION_KEY...")
        try:
            from cryptography.fernet import Fernet
            encryption_key = Fernet.generate_key().decode()
            updates['ENCRYPTION_KEY'] = encryption_key
            print_success("Generated ENCRYPTION_KEY")
        except ImportError:
            print_warning("cryptography library not installed. Skipping ENCRYPTION_KEY.")
            print_info("Install with: pip install cryptography")
    
    # Summary
    print_header("Summary")
    print("Will update the following in .env:")
    print()
    for key, value in updates.items():
        if 'SECRET' in key or 'KEY' in key:
            # Mask sensitive values
            display_value = value[:8] + "..." if len(value) > 8 else "***"
        else:
            display_value = value
        print(f"  {key} = {display_value}")
    print()
    
    # Confirm
    confirm = get_input("Apply these changes? (yes/no)", "yes").lower()
    
    if confirm not in ['yes', 'y']:
        print_warning("Setup cancelled. No changes made.")
        return 0
    
    # Update file
    print()
    print_info("Updating .env file...")
    
    if update_env_file(env_path, updates):
        print_success(f"Successfully updated {env_path}")
        
        # Next steps
        print_header("✅ Setup Complete!")
        print()
        print("Next steps:")
        print()
        print("1. Register your callback URL with MTN:")
        print(f"   {callback_url}")
        print()
        print("2. Restart your backend:")
        print("   docker-compose restart backend")
        print()
        print("3. Test the integration:")
        print("   curl http://localhost:8000/ussd/health")
        print("   python test_africastalking_ussd.py test")
        print()
        print("4. Check logs for any errors:")
        print("   docker logs sususave_backend --tail 50 --follow")
        print()
        print("5. Look for this message in logs:")
        print("   ✅ 'Successfully obtained MTN access token'")
        print()
        print("📚 Documentation:")
        print("   - MTN_CREDENTIALS_SETUP_GUIDE.md (detailed guide)")
        print("   - MTN_SETUP_CHECKLIST.md (track progress)")
        print("   - USSD_TESTING_GUIDE.md (testing instructions)")
        print()
        print_success("Setup complete! Good luck! 🚀")
        return 0
    else:
        print_error("Failed to update .env file")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print_warning("Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)

