#!/usr/bin/env python3
"""
USSD Setup Verification Script

This script checks the configuration status for both MTN and AfricasTalking USSD providers.
Run this to verify your USSD setup is complete and ready for testing/production.

Usage:
    python verify_ussd_setup.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def load_env_file(env_path: Path) -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
    if not env_path.exists():
        return env_vars
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def check_env_file() -> Tuple[bool, Dict[str, str]]:
    """Check if .env file exists and load variables."""
    print_header("1. Environment File Check")
    
    backend_dir = Path(__file__).parent
    env_path = backend_dir / '.env'
    env_example_path = backend_dir / 'env.example'
    
    if not env_path.exists():
        print_error(f".env file not found at: {env_path}")
        if env_example_path.exists():
            print_info(f"Found env.example at: {env_example_path}")
            print_info("Create .env file by running:")
            print(f"    cd {backend_dir}")
            print(f"    cp env.example .env")
            print(f"    # Then edit .env with your actual credentials")
        return False, {}
    
    print_success(f".env file found at: {env_path}")
    env_vars = load_env_file(env_path)
    print_info(f"Loaded {len(env_vars)} environment variables")
    
    return True, env_vars

def check_mtn_config(env_vars: Dict[str, str]) -> Dict:
    """Check MTN USSD configuration."""
    print_header("2. MTN USSD Configuration")
    
    status = {
        'configured': False,
        'warnings': [],
        'errors': [],
        'info': []
    }
    
    # Required variables
    required = {
        'MTN_CONSUMER_KEY': 'MTN API Consumer Key',
        'MTN_CONSUMER_SECRET': 'MTN API Consumer Secret',
        'MTN_USSD_SERVICE_CODE': 'MTN USSD Service Code (e.g., *920*55#)',
    }
    
    # Optional but recommended
    optional = {
        'MTN_CALLBACK_URL': 'MTN Callback URL (HTTPS required)',
        'MTN_ENVIRONMENT': 'MTN Environment (sandbox/production)',
        'ENABLE_MTN_USSD': 'Enable MTN USSD Service',
        'USE_MTN_SERVICES': 'Use MTN as primary provider'
    }
    
    # Check required variables
    missing_required = []
    for var, description in required.items():
        value = env_vars.get(var, '').strip()
        if not value or value.startswith('your-') or value == 'placeholder':
            print_error(f"{var} is missing or placeholder")
            missing_required.append(var)
            status['errors'].append(f"{var} not configured")
        else:
            print_success(f"{var} is configured")
            
            # Check for default/example values
            if var == 'MTN_CONSUMER_KEY' and value == 'J7SH4tF6QqAsa6VYFhtGRwgpvPjYnF9y':
                print_warning("Using example MTN credentials (sandbox only)")
                status['warnings'].append("Using example MTN sandbox credentials")
    
    # Check optional variables
    for var, description in optional.items():
        value = env_vars.get(var, '').strip()
        if not value:
            print_warning(f"{var} not set (optional)")
        else:
            print_success(f"{var} = {value}")
            
            # Check callback URL
            if var == 'MTN_CALLBACK_URL':
                if 'ngrok' in value:
                    print_warning("Using ngrok URL (temporary, not for production)")
                    status['warnings'].append("Callback URL is temporary (ngrok)")
                elif not value.startswith('https://'):
                    print_error("Callback URL must use HTTPS")
                    status['errors'].append("Callback URL is not HTTPS")
    
    if not missing_required:
        status['configured'] = True
        print_success("\nMTN USSD configuration is complete!")
    else:
        print_error(f"\nMTN USSD configuration incomplete ({len(missing_required)} variables missing)")
    
    return status

def check_africastalking_config(env_vars: Dict[str, str]) -> Dict:
    """Check AfricasTalking USSD configuration."""
    print_header("3. AfricasTalking USSD Configuration")
    
    status = {
        'configured': False,
        'warnings': [],
        'errors': [],
        'info': []
    }
    
    # Required variables
    required = {
        'AT_USERNAME': 'AfricasTalking Username',
        'AT_API_KEY': 'AfricasTalking API Key',
        'AT_USSD_SERVICE_CODE': 'AfricasTalking USSD Service Code',
    }
    
    # Optional
    optional = {
        'AT_ENVIRONMENT': 'AfricasTalking Environment (sandbox/production)',
    }
    
    # Check required variables
    missing_required = []
    for var, description in required.items():
        value = env_vars.get(var, '').strip()
        if not value or value.startswith('your-') or value == 'placeholder':
            print_error(f"{var} is missing or placeholder")
            missing_required.append(var)
            status['errors'].append(f"{var} not configured")
        else:
            print_success(f"{var} is configured")
            
            # Check for sandbox mode
            if var == 'AT_USERNAME' and value == 'sandbox':
                print_info("Using AfricasTalking sandbox mode (for testing)")
                status['info'].append("Using sandbox mode")
            
            # Check for placeholder API key
            if var == 'AT_API_KEY' and 'dashboard' in value.lower():
                print_error("API key is still placeholder value")
                status['errors'].append("API key is placeholder")
    
    # Check optional variables
    for var, description in optional.items():
        value = env_vars.get(var, '').strip()
        if not value:
            print_warning(f"{var} not set (optional)")
        else:
            print_success(f"{var} = {value}")
    
    if not missing_required:
        status['configured'] = True
        print_success("\nAfricasTalking USSD configuration is complete!")
    else:
        print_error(f"\nAfricasTalking USSD configuration incomplete ({len(missing_required)} variables missing)")
    
    return status

def check_active_provider(env_vars: Dict[str, str]) -> str:
    """Determine which provider is currently active."""
    print_header("4. Active Provider")
    
    use_mtn = env_vars.get('USE_MTN_SERVICES', 'True').strip().lower() in ['true', '1', 'yes']
    
    if use_mtn:
        print_info("Current provider: MTN")
        print_info("Service Code: " + env_vars.get('MTN_USSD_SERVICE_CODE', '*920*55#'))
        return 'MTN'
    else:
        print_info("Current provider: AfricasTalking")
        print_info("Service Code: " + env_vars.get('AT_USSD_SERVICE_CODE', '*384*12345#'))
        return 'AfricasTalking'

def check_database_config(env_vars: Dict[str, str]):
    """Check database configuration."""
    print_header("5. Database Configuration")
    
    db_url = env_vars.get('DATABASE_URL', '')
    if not db_url:
        print_error("DATABASE_URL not configured")
        return
    
    print_success("DATABASE_URL is configured")
    
    # Parse database URL (basic check)
    if db_url.startswith('postgresql://'):
        print_success("Using PostgreSQL database")
    elif db_url.startswith('sqlite://'):
        print_warning("Using SQLite database (not recommended for production)")
    else:
        print_warning("Unknown database type")

def check_security_config(env_vars: Dict[str, str]):
    """Check security configuration."""
    print_header("6. Security Configuration")
    
    # Check SECRET_KEY
    secret_key = env_vars.get('SECRET_KEY', '')
    if not secret_key:
        print_error("SECRET_KEY not configured")
    elif 'change-in-production' in secret_key.lower() or secret_key == 'your-secret-key-change-in-production':
        print_error("SECRET_KEY is using default/example value - CHANGE THIS!")
    else:
        print_success("SECRET_KEY is configured")
    
    # Check ENCRYPTION_KEY
    encryption_key = env_vars.get('ENCRYPTION_KEY', '')
    if not encryption_key:
        print_error("ENCRYPTION_KEY not configured")
    elif 'generate' in encryption_key.lower():
        print_error("ENCRYPTION_KEY is placeholder - generate a real key")
        print_info("Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'")
    else:
        print_success("ENCRYPTION_KEY is configured")

def check_ussd_endpoint():
    """Check if USSD endpoint is accessible."""
    print_header("7. USSD Endpoint Check")
    
    try:
        import requests
        response = requests.get('http://localhost:8000/ussd/health', timeout=5)
        if response.status_code == 200:
            print_success("USSD endpoint is accessible")
            data = response.json()
            print_info(f"Provider: {data.get('provider', 'Unknown')}")
            print_info(f"Environment: {data.get('environment', 'Unknown')}")
            print_info(f"Service Code: {data.get('service_code', 'Unknown')}")
            return True
        else:
            print_error(f"USSD endpoint returned status {response.status_code}")
            return False
    except ImportError:
        print_warning("requests library not available, skipping endpoint check")
        print_info("Install with: pip install requests")
        return None
    except Exception as e:
        print_error(f"Cannot reach USSD endpoint: {e}")
        print_info("Make sure backend server is running:")
        print_info("    cd backend && python -m uvicorn app.main:app --reload")
        return False

def print_summary(env_exists: bool, mtn_status: Dict, at_status: Dict, active_provider: str):
    """Print verification summary."""
    print_header("VERIFICATION SUMMARY")
    
    if not env_exists:
        print_error("❌ .env file does not exist")
        print_info("\nNext Steps:")
        print("1. Create .env file from env.example")
        print("2. Configure your credentials")
        print("3. Run this script again")
        return
    
    # Overall status
    all_good = True
    
    print("\n📊 Configuration Status:")
    print(f"  Environment File: {Colors.GREEN}✅ Found{Colors.END}")
    
    if active_provider == 'MTN':
        if mtn_status['configured']:
            print(f"  MTN USSD: {Colors.GREEN}✅ Configured{Colors.END}")
        else:
            print(f"  MTN USSD: {Colors.RED}❌ Not configured{Colors.END}")
            all_good = False
        
        if at_status['configured']:
            print(f"  AfricasTalking: {Colors.YELLOW}⚠️  Configured but not active{Colors.END}")
        else:
            print(f"  AfricasTalking: {Colors.YELLOW}⚠️  Not configured (not needed for MTN){Colors.END}")
    else:
        if at_status['configured']:
            print(f"  AfricasTalking: {Colors.GREEN}✅ Configured{Colors.END}")
        else:
            print(f"  AfricasTalking: {Colors.RED}❌ Not configured{Colors.END}")
            all_good = False
        
        if mtn_status['configured']:
            print(f"  MTN USSD: {Colors.YELLOW}⚠️  Configured but not active{Colors.END}")
        else:
            print(f"  MTN USSD: {Colors.YELLOW}⚠️  Not configured (not needed for AT){Colors.END}")
    
    # Warnings
    active_status = mtn_status if active_provider == 'MTN' else at_status
    if active_status['warnings']:
        print(f"\n⚠️  Warnings ({len(active_status['warnings'])}):")
        for warning in active_status['warnings']:
            print(f"  - {warning}")
    
    # Errors
    if active_status['errors']:
        print(f"\n❌ Errors ({len(active_status['errors'])}):")
        for error in active_status['errors']:
            print(f"  - {error}")
        all_good = False
    
    # Final verdict
    print()
    if all_good and not active_status['errors']:
        print_success("🎉 USSD setup is complete and ready for testing!")
        print_info("\nNext Steps:")
        print("1. Start backend server: cd backend && python -m uvicorn app.main:app --reload")
        print("2. Run USSD tests: cd backend && python test_africastalking_ussd.py test")
        print("3. Test with curl: cd backend && ./test_ussd_curl.sh")
    else:
        print_error("❌ USSD setup is incomplete")
        print_info("\nNext Steps:")
        print("1. Review errors and warnings above")
        print("2. Update .env file with correct credentials")
        print("3. Run this script again to verify")
        print("\nSee USSD_SETUP_INSTRUCTIONS.md for detailed setup guide")

def main():
    """Main verification function."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{'USSD Setup Verification Tool':^60}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    # Run checks
    env_exists, env_vars = check_env_file()
    
    if not env_exists:
        print_error("\n❌ Cannot proceed without .env file")
        print_info("\nCreate .env file first:")
        print("    cd backend")
        print("    cp env.example .env")
        print("    # Edit .env with your credentials")
        return 1
    
    mtn_status = check_mtn_config(env_vars)
    at_status = check_africastalking_config(env_vars)
    active_provider = check_active_provider(env_vars)
    check_database_config(env_vars)
    check_security_config(env_vars)
    check_ussd_endpoint()
    
    # Print summary
    print_summary(env_exists, mtn_status, at_status, active_provider)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

