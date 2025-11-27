#!/bin/bash

# Test iOS Login Fix
# This script helps verify that iOS login is working correctly

set -e

echo "🔍 iOS Login Test Script"
echo "========================"
echo ""

# Check if backend is running
echo "1️⃣ Checking backend connection..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "❌ Backend is not running!"
    echo ""
    echo "Start the backend first:"
    echo "  cd ../../backend"
    echo "  python run.py"
    exit 1
fi

echo ""

# Check node_modules
echo "2️⃣ Checking dependencies..."
if [ -d "node_modules" ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Dependencies not installed!"
    echo "Installing now..."
    npm install
fi

echo ""

# Show current config
echo "3️⃣ Current Configuration:"
echo "  Platform Detection: Enabled"
echo "  iOS Simulator: http://localhost:8000"
echo "  Android Emulator: http://10.0.2.2:8000"

if [ -f ".env" ]; then
    echo ""
    echo "📄 Found .env file:"
    cat .env
fi

echo ""
echo ""

# Provide test instructions
echo "4️⃣ Test Instructions:"
echo "====================="
echo ""
echo "The app will launch in iOS Simulator..."
echo ""
echo "To test login:"
echo "  1. Wait for app to load"
echo "  2. Tap 'Login'"
echo "  3. Enter phone: +256700000001"
echo "  4. Enter password: password123"
echo "  5. Tap 'Login' button"
echo ""
echo "Expected result: Successfully logged in ✅"
echo ""
echo "Press Enter to continue or Ctrl+C to cancel..."
read

# Start iOS simulator
echo ""
echo "🚀 Starting iOS Simulator..."
echo ""
npm run ios

echo ""
echo "✅ Test complete!"

