#!/usr/bin/env python3
"""
Verify Existing Users Script

This script verifies all existing users in the database via MTN KYC API.
Run this after implementing KYC to retroactively verify existing users.

Usage:
    python verify_existing_users.py [--all] [--unverified-only]
"""

import sys
import os
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User
from app.services.kyc_service import kyc_service
from app.utils import decrypt_field
from app.config import settings


def verify_all_users(db: Session, unverified_only: bool = True):
    """
    Verify all users in the database.
    
    Args:
        db: Database session
        unverified_only: Only verify users who are not already verified
    """
    print("=" * 80)
    print("MTN KYC - Existing Users Verification Script")
    print("=" * 80)
    print(f"Environment: {settings.MTN_ENVIRONMENT}")
    print(f"KYC Enabled: {settings.ENABLE_MTN_KYC}")
    print(f"Required for Payments: {settings.REQUIRE_KYC_FOR_PAYMENTS}")
    print("=" * 80)
    print()
    
    # Get users to verify
    query = db.query(User)
    
    if unverified_only:
        query = query.filter(User.kyc_verified == False)
        print("📋 Verifying UNVERIFIED users only")
    else:
        print("📋 Verifying ALL users")
    
    users = query.all()
    
    if not users:
        print("✅ No users to verify!")
        return
    
    print(f"📊 Found {len(users)} users to verify\n")
    
    # Verify each user
    results = {
        "total": len(users),
        "verified": 0,
        "failed": 0,
        "errors": []
    }
    
    for idx, user in enumerate(users, 1):
        print(f"[{idx}/{len(users)}] Processing User ID {user.id}...")
        
        try:
            # Decrypt phone number
            phone_number = decrypt_field(user.phone_number)
            print(f"  Phone: {phone_number[:6]}...{phone_number[-4:]}")
            
            # Verify user
            result = kyc_service.verify_user(db, user.id, phone_number)
            
            if result.get("verified"):
                results["verified"] += 1
                print(f"  ✅ VERIFIED - Provider: {result.get('provider')}")
            else:
                results["failed"] += 1
                print(f"  ❌ FAILED - {result.get('message')}")
                results["errors"].append({
                    "user_id": user.id,
                    "phone": f"{phone_number[:6]}...{phone_number[-4:]}",
                    "message": result.get("message")
                })
            
        except Exception as e:
            results["failed"] += 1
            error_msg = str(e)
            print(f"  ❌ ERROR - {error_msg}")
            results["errors"].append({
                "user_id": user.id,
                "message": error_msg
            })
        
        print()
    
    # Print summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"Total Processed: {results['total']}")
    print(f"✅ Verified: {results['verified']}")
    print(f"❌ Failed: {results['failed']}")
    print()
    
    if results['errors']:
        print("ERRORS:")
        for idx, error in enumerate(results['errors'][:20], 1):  # Show first 20
            print(f"  {idx}. User {error.get('user_id')}: {error.get('message')}")
        
        if len(results['errors']) > 20:
            print(f"  ... and {len(results['errors']) - 20} more errors")
        print()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"kyc_verification_results_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("MTN KYC Verification Results\n")
        f.write("=" * 80 + "\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Total: {results['total']}\n")
        f.write(f"Verified: {results['verified']}\n")
        f.write(f"Failed: {results['failed']}\n")
        f.write("\n")
        
        if results['errors']:
            f.write("Errors:\n")
            for error in results['errors']:
                f.write(f"  User {error.get('user_id')}: {error.get('message')}\n")
    
    print(f"📄 Results saved to: {filename}")
    print("=" * 80)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Verify existing users via MTN KYC API"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Verify all users (including already verified)"
    )
    parser.add_argument(
        "--unverified-only",
        action="store_true",
        default=True,
        help="Only verify unverified users (default)"
    )
    
    args = parser.parse_args()
    
    # Determine which users to verify
    unverified_only = not args.all
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Confirm before proceeding
        if not settings.ENABLE_MTN_KYC:
            print("⚠️  WARNING: MTN KYC is DISABLED in settings!")
            print("Users will be auto-verified without actual MTN verification.")
            response = input("Continue anyway? (yes/no): ")
            if response.lower() != "yes":
                print("Aborted.")
                return
        
        print("\n⚠️  This will verify users via MTN KYC API.")
        print("This may take several minutes depending on the number of users.")
        response = input("\nContinue? (yes/no): ")
        
        if response.lower() != "yes":
            print("Aborted.")
            return
        
        print()
        
        # Run verification
        verify_all_users(db, unverified_only)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()

