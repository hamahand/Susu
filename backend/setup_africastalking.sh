#!/bin/bash
# AfricaTalking USSD Setup Helper Script
# This script helps you get started with AfricaTalking integration quickly

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  AfricaTalking USSD Setup Helper                  ║${NC}"
echo -e "${BLUE}║  SusuSave Project                                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to prompt for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local result
    
    read -p "$prompt [$default]: " result
    echo "${result:-$default}"
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

if ! command_exists pip; then
    echo -e "${RED}❌ pip not found. Please install pip${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip found${NC}"

# Check if .env exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [[ ! $overwrite =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Keeping existing .env file${NC}"
        USE_EXISTING_ENV=true
    fi
fi

# Create/update .env file
if [ "$USE_EXISTING_ENV" != "true" ]; then
    echo ""
    echo -e "${YELLOW}Setting up .env file...${NC}"
    
    if [ ! -f "env.example" ]; then
        echo -e "${RED}❌ env.example not found${NC}"
        exit 1
    fi
    
    # Copy example
    cp env.example .env
    
    # Prompt for AfricaTalking credentials
    echo ""
    echo -e "${BLUE}Please provide your AfricaTalking credentials:${NC}"
    echo "Get these from: https://account.africastalking.com/"
    echo ""
    
    AT_USERNAME=$(prompt_with_default "AfricaTalking Username" "sandbox")
    AT_API_KEY=$(prompt_with_default "AfricaTalking API Key" "your-api-key-here")
    AT_ENVIRONMENT=$(prompt_with_default "Environment (sandbox/production)" "sandbox")
    AT_USSD_CODE=$(prompt_with_default "USSD Service Code" "*384*12345#")
    
    # Update .env file
    sed -i.bak "s/AT_USERNAME=.*/AT_USERNAME=$AT_USERNAME/" .env
    sed -i.bak "s/AT_API_KEY=.*/AT_API_KEY=$AT_API_KEY/" .env
    sed -i.bak "s/AT_ENVIRONMENT=.*/AT_ENVIRONMENT=$AT_ENVIRONMENT/" .env
    sed -i.bak "s|AT_USSD_SERVICE_CODE=.*|AT_USSD_SERVICE_CODE=$AT_USSD_CODE|" .env
    rm .env.bak 2>/dev/null || true
    
    echo -e "${GREEN}✓ .env file created${NC}"
fi

# Install dependencies
echo ""
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check if ngrok is installed
echo ""
echo -e "${YELLOW}Checking for ngrok...${NC}"
if command_exists ngrok; then
    echo -e "${GREEN}✓ ngrok found${NC}"
else
    echo -e "${YELLOW}⚠️  ngrok not found${NC}"
    echo "You'll need ngrok to test USSD locally."
    echo "Install it:"
    echo "  macOS: brew install ngrok"
    echo "  Other: https://ngrok.com/download"
fi

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Setup Complete! 🎉                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo ""
echo "1. Start the backend server:"
echo -e "   ${YELLOW}python -m uvicorn app.main:app --reload --port 8000${NC}"
echo ""
echo "2. In a new terminal, start ngrok:"
echo -e "   ${YELLOW}ngrok http 8000${NC}"
echo ""
echo "3. Copy your ngrok HTTPS URL and configure it in AfricaTalking:"
echo "   Dashboard → USSD → Create Channel → Set callback URL"
echo -e "   ${YELLOW}https://your-ngrok-url.ngrok.io/ussd/callback${NC}"
echo ""
echo "4. Test your USSD integration:"
echo -e "   ${YELLOW}python test_africastalking_ussd.py${NC}"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "   Quick Ref:  ../AFRICASTALKING_QUICKREF.md"
echo "   Full Guide: docs/AFRICASTALKING_SETUP.md"
echo "   Quick Start: docs/USSD_QUICKSTART.md"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"

