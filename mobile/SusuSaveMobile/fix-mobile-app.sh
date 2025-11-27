#!/bin/bash

# Mobile App Quick Fix Script
# This script addresses common mobile app issues

echo "🔧 SusuSave Mobile App Quick Fix"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "src" ]; then
    print_error "Please run this script from the mobile app directory (mobile/SusuSaveMobile)"
    exit 1
fi

print_status "Starting mobile app troubleshooting..."

# Step 1: Check backend status
print_status "Checking backend status..."
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "Backend is running and accessible"
else
    print_error "Backend is not accessible at http://localhost:8000"
    print_warning "Please start the backend server first:"
    echo "  cd ../../backend"
    echo "  uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    exit 1
fi

# Step 2: Clear caches
print_status "Clearing mobile app caches..."
rm -rf node_modules/.cache
rm -rf .expo
print_success "Caches cleared"

# Step 3: Check platform-specific API URLs
print_status "Checking API configuration..."
if [ -f "src/config.ts" ]; then
    print_success "Config file exists"
    echo "Current API configuration:"
    grep -A 10 "API_BASE_URL" src/config.ts
else
    print_error "Config file not found!"
fi

# Step 4: Install dependencies
print_status "Installing/updating dependencies..."
npm install
print_success "Dependencies updated"

# Step 5: Clear Expo cache and restart
print_status "Clearing Expo cache..."
npx expo start --clear --no-dev --minify

print_success "Mobile app troubleshooting complete!"
echo ""
echo "Next steps:"
echo "1. The app should now start with cleared cache"
echo "2. Test login functionality"
echo "3. Check the Debug tab for connectivity tests"
echo "4. If issues persist, check the troubleshooting guide:"
echo "   cat MOBILE_APP_TROUBLESHOOTING_GUIDE.md"
echo ""
echo "Platform-specific URLs:"
echo "- iOS Simulator: http://localhost:8000"
echo "- Android Emulator: http://10.0.2.2:8000"
echo "- Physical Device: Set EXPO_PUBLIC_API_URL in .env"
