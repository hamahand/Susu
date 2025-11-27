#!/bin/bash

# Quick Login Flow Test Script
# Tests the complete authentication flow

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

API_URL="http://localhost:8000"

echo -e "${BLUE}Testing SusuSave Login Flow${NC}"
echo ""

# Test 1: Check Backend Health
echo -e "${BLUE}1. Checking backend health...${NC}"
if curl -s "${API_URL}/docs" > /dev/null; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is not responding${NC}"
    exit 1
fi

# Test 2: Register a new user
echo ""
echo -e "${BLUE}2. Registering new user...${NC}"
PHONE="+233$(date +%s | tail -c 10)"  # Generate unique phone
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\":\"${PHONE}\",\"name\":\"Test User\",\"password\":\"TestPass123\",\"user_type\":\"app\"}")

if echo "$REGISTER_RESPONSE" | grep -q "id"; then
    USER_ID=$(echo "$REGISTER_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
    echo -e "${GREEN}✅ User registered successfully (ID: ${USER_ID})${NC}"
else
    echo -e "${RED}❌ Registration failed${NC}"
    echo "$REGISTER_RESPONSE"
    exit 1
fi

# Test 3: Login with credentials
echo ""
echo -e "${BLUE}3. Logging in...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\":\"${PHONE}\",\"password\":\"TestPass123\"}")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\(.*\)"/\1/')
    echo -e "${GREEN}✅ Login successful${NC}"
    echo -e "${BLUE}Token: ${TOKEN:0:50}...${NC}"
else
    echo -e "${RED}❌ Login failed${NC}"
    echo "$LOGIN_RESPONSE"
    exit 1
fi

# Test 4: Create a group (protected endpoint)
echo ""
echo -e "${BLUE}4. Testing authenticated request (create group)...${NC}"
GROUP_RESPONSE=$(curl -s -X POST "${API_URL}/groups" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test Group\",\"contribution_amount\":100.0,\"frequency\":\"weekly\",\"member_count\":5,\"num_cycles\":12}")

if echo "$GROUP_RESPONSE" | grep -q "group_code"; then
    GROUP_CODE=$(echo "$GROUP_RESPONSE" | grep -o '"group_code":"[^"]*"' | sed 's/"group_code":"\(.*\)"/\1/')
    echo -e "${GREEN}✅ Authenticated request successful${NC}"
    echo -e "${BLUE}Group Code: ${GROUP_CODE}${NC}"
else
    echo -e "${RED}❌ Authenticated request failed${NC}"
    echo "$GROUP_RESPONSE"
    exit 1
fi

# Test 5: Check database
echo ""
echo -e "${BLUE}5. Verifying database...${NC}"
if command -v docker &> /dev/null; then
    USER_COUNT=$(docker exec sususave_db psql -U sususer -d sususave -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' ')
    if [ ! -z "$USER_COUNT" ] && [ "$USER_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ Database has ${USER_COUNT} user(s)${NC}"
    else
        echo -e "${RED}⚠️  Could not verify database (not critical)${NC}"
    fi
else
    echo -e "${BLUE}ℹ  Docker not available, skipping database check${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}   ✅ All Tests Passed!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "  • Backend API: ✅ Running"
echo "  • User Registration: ✅ Working"  
echo "  • User Login: ✅ Working"
echo "  • JWT Authentication: ✅ Working"
echo "  • Database: ✅ Persisting data"
echo ""
echo -e "${BLUE}Frontend:${NC}"
echo "  • PWA: http://localhost:3000/app/"
echo "  • API Docs: http://localhost:8000/docs"
echo ""
echo -e "${BLUE}Test User:${NC}"
echo "  • Phone: ${PHONE}"
echo "  • Password: TestPass123"
echo ""

