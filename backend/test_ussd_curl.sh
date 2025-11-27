#!/bin/bash
# USSD Testing Script using curl
# Test your USSD endpoint locally before deploying

BASE_URL="${BASE_URL:-http://localhost:8000}"
USSD_URL="$BASE_URL/ussd/callback"
PHONE="+256700000001"
SERVICE_CODE="*384*12345#"
SESSION_ID="test-session-$(date +%s)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}USSD Testing Script${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Function to send USSD request
send_ussd() {
    local text="$1"
    local description="$2"
    
    echo -e "${YELLOW}$description${NC}"
    echo "Text: '$text'"
    echo ""
    
    response=$(curl -s -X POST "$USSD_URL" \
        -d "sessionId=$SESSION_ID" \
        -d "serviceCode=$SERVICE_CODE" \
        -d "phoneNumber=$PHONE" \
        -d "text=$text")
    
    echo -e "${GREEN}Response:${NC}"
    echo "$response"
    echo ""
    echo "---"
    echo ""
}

# Test 1: Initial request (main menu)
send_ussd "" "Test 1: Main Menu (Initial Request)"

# Test 2: Select option 3 (Check Status)
SESSION_ID="test-session-$(date +%s)"
send_ussd "" "Test 2a: New Session - Main Menu"
send_ussd "3" "Test 2b: Select Option 3 (Check Status)"

# Test 3: Join Group Flow
SESSION_ID="test-session-$(date +%s)"
send_ussd "" "Test 3a: New Session - Main Menu"
send_ussd "1" "Test 3b: Select Option 1 (Join Group)"
send_ussd "1*SUSU1234" "Test 3c: Enter Group Code 'SUSU1234'"

# Test 4: Invalid Option
SESSION_ID="test-session-$(date +%s)"
send_ussd "" "Test 4a: New Session - Main Menu"
send_ussd "9" "Test 4b: Select Invalid Option 9"

# Test 5: Check Payout Date
SESSION_ID="test-session-$(date +%s)"
send_ussd "" "Test 5a: New Session - Main Menu"
send_ussd "4" "Test 5b: Select Option 4 (My Payout Date)"

# Test 6: Health Check
echo -e "${YELLOW}Test 6: Health Check Endpoint${NC}"
echo ""
health_response=$(curl -s "$BASE_URL/ussd/health")
echo -e "${GREEN}Response:${NC}"
echo "$health_response" | python -m json.tool 2>/dev/null || echo "$health_response"
echo ""
echo "---"
echo ""

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}All tests completed!${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo "To test interactively, use:"
echo "  python test_africastalking_ussd.py"
echo ""
echo "To test with AfricaTalking simulator:"
echo "  https://account.africastalking.com/ → USSD → Simulator"

