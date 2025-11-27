#!/bin/bash

# Test PWA Login Fix
# This script tests the login functionality after the fix

BASE_URL="http://localhost:8000"

echo "🧪 Testing PWA Login Fix"
echo "========================"
echo ""

# Test 1: Create a test user
echo "1️⃣  Creating test user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+233244999888",
    "name": "PWA Test User",
    "password": "testpass123",
    "user_type": "app"
  }')

if echo "$REGISTER_RESPONSE" | grep -q '"id"'; then
  echo "✅ User created successfully"
  echo "$REGISTER_RESPONSE" | python3 -m json.tool
else
  echo "⚠️  User might already exist or registration failed"
  echo "$REGISTER_RESPONSE"
fi

echo ""
echo "2️⃣  Testing login with correct format..."

# Test 2: Login with the new format (JSON with phone_number)
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+233244999888",
    "password": "testpass123"
  }')

if echo "$LOGIN_RESPONSE" | grep -q '"access_token"'; then
  echo "✅ Login successful!"
  echo "$LOGIN_RESPONSE" | python3 -m json.tool
  
  # Extract token
  TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
  
  echo ""
  echo "3️⃣  Testing authenticated endpoint..."
  
  # Test 3: Get current user profile
  ME_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/me" \
    -H "Authorization: Bearer $TOKEN")
  
  if echo "$ME_RESPONSE" | grep -q '"name"'; then
    echo "✅ Authentication working!"
    echo "$ME_RESPONSE" | python3 -m json.tool
  else
    echo "❌ Authentication failed"
    echo "$ME_RESPONSE"
  fi
else
  echo "❌ Login failed"
  echo "$LOGIN_RESPONSE"
fi

echo ""
echo "========================"
echo "✅ Test complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Open http://localhost:5173/app/login"
echo "   2. Login with:"
echo "      Phone: +233244999888"
echo "      Password: testpass123"
echo "   3. You should be redirected to the dashboard"

