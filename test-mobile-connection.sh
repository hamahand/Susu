#!/bin/bash

# Mobile App Connection Test Script
echo "🔍 Testing Mobile App Backend Connection"
echo "========================================"

# Test backend connectivity
echo "1. Testing backend health endpoint..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Backend is healthy and running"
else
    echo "❌ Backend is not responding"
    exit 1
fi

# Test Android emulator connectivity
echo "2. Testing Android emulator connectivity..."
if curl -s http://10.0.2.2:8000/health | grep -q "healthy"; then
    echo "✅ Android emulator can reach backend"
else
    echo "❌ Android emulator cannot reach backend"
fi

# Test iOS simulator connectivity
echo "3. Testing iOS simulator connectivity..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ iOS simulator can reach backend"
else
    echo "❌ iOS simulator cannot reach backend"
fi

# Check if mobile app is running
echo "4. Checking mobile app status..."
if pgrep -f "expo start" > /dev/null; then
    echo "✅ Mobile app development server is running"
else
    echo "❌ Mobile app development server is not running"
    echo "   Run: cd mobile/SusuSaveMobile && npx expo start --clear"
fi

echo ""
echo "📱 Next Steps:"
echo "1. Open the mobile app on your device/emulator"
echo "2. Navigate to the Debug tab (bug icon)"
echo "3. Tap 'Test Backend Connection'"
echo "4. If successful, try logging in"
echo ""
echo "🔧 If issues persist:"
echo "- Check the troubleshooting guide: MOBILE_APP_TROUBLESHOOTING_GUIDE.md"
echo "- Run the fix script: ./fix-mobile-app.sh"
