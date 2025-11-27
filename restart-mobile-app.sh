#!/bin/bash

# Mobile App Restart Script with Fixes
echo "🚀 Restarting Mobile App with Fixes"
echo "===================================="

# Kill existing processes
echo "1. Stopping existing processes..."
pkill -f "expo start" 2>/dev/null || true
pkill -f "node.*8081" 2>/dev/null || true
pkill -f "node.*8082" 2>/dev/null || true

# Wait a moment
sleep 2

# Navigate to mobile app directory
cd mobile/SusuSaveMobile

# Clear caches
echo "2. Clearing caches..."
rm -rf node_modules/.cache 2>/dev/null || true
rm -rf .expo 2>/dev/null || true

# Install dependencies
echo "3. Installing dependencies..."
npm install

# Start the app with clear cache
echo "4. Starting mobile app..."
echo "   - Backend should be running on port 8000"
echo "   - Mobile app will start on port 8082"
echo "   - Use Debug tab to test connectivity"
echo ""

npx expo start --clear --port 8082

echo ""
echo "✅ Mobile app restarted with fixes!"
echo ""
echo "📱 Next Steps:"
echo "1. Open the app on your device/emulator"
echo "2. Go to Debug tab (bug icon)"
echo "3. Tap 'Test Backend Connection'"
echo "4. The app will automatically find the working API URL"
echo "5. Try logging in with your credentials"
echo ""
echo "🔧 If Android still has issues:"
echo "- The app will try multiple URLs automatically"
echo "- Check the console logs for connection attempts"
echo "- Use the Debug tab to see which URL works"