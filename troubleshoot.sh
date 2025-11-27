#!/bin/bash

# SusuSave Troubleshooting Guide
echo "🔧 SusuSave Troubleshooting Guide"
echo "=================================="
echo ""

echo "📱 Mobile App Issues:"
echo "1. Network Error on Login:"
echo "   - Check if backend is running: curl http://127.0.0.1:8000/health"
echo "   - For Android emulator, use: http://10.0.2.2:8000"
echo "   - For iOS simulator, use: http://127.0.0.1:8000"
echo "   - For physical device, use your computer's IP: http://192.168.x.x:8000"
echo ""

echo "2. Start Mobile App:"
echo "   cd /Users/maham/susu/mobile/SusuSaveMobile"
echo "   EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npx expo start --localhost --clear"
echo ""

echo "🌐 Web App Issues:"
echo "1. Favicon Not Showing:"
echo "   - Favicon files copied to: web/app/public/pwa-icons/"
echo "   - Restart the web dev server if needed"
echo "   - Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)"
echo ""

echo "2. Start Web App:"
echo "   cd /Users/maham/susu/web/app"
echo "   npm run dev"
echo ""

echo "🔧 Backend Issues:"
echo "1. Start Backend:"
echo "   cd /Users/maham/susu/backend"
echo "   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""

echo "2. Test API Endpoints:"
echo "   curl http://127.0.0.1:8000/health"
echo "   curl http://127.0.0.1:8000/docs"
echo ""

echo "📋 Quick Fixes:"
echo "- Clear Expo cache: npx expo start --clear"
echo "- Clear browser cache: Hard refresh (Ctrl+Shift+R)"
echo "- Restart all services"
echo "- Check firewall settings"
echo ""

echo "🌍 Network Configuration:"
echo "- Localhost (127.0.0.1): Works for web and iOS simulator"
echo "- 10.0.2.2: Works for Android emulator"
echo "- Your IP (192.168.x.x): Works for physical devices"
echo ""

echo "Run this script with: ./troubleshoot.sh"
