#!/bin/bash

# SusuSave Development Environment Startup Script
# This script starts all development services with interactive port selection

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default ports
LANDING_PORT=8080
PWA_PORT=3000
ADMIN_PORT=3001
BACKEND_PORT=8000
EXPO_PORT=8081

# PID file to track running processes
PID_FILE="/tmp/susu_dev_pids.txt"
LOG_DIR="/tmp/susu_logs"

# Create log directory
mkdir -p "$LOG_DIR"

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✅ ${NC}$1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  ${NC}$1"
}

print_error() {
    echo -e "${RED}❌ ${NC}$1"
}

print_header() {
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}   $1${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        print_warning "Killing process on port $port (PID: $pid)" >&2
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Function to ask user for port
ask_port() {
    local service=$1
    local default_port=$2
    local new_port
    
    echo "" >&2
    print_warning "Port $default_port is in use by another process" >&2
    echo -e "${CYAN}Options:${NC}" >&2
    echo "  1. Kill the existing process and use port $default_port" >&2
    echo "  2. Choose a different port" >&2
    echo "  3. Skip starting $service" >&2
    read -p "Choose option (1/2/3): " choice
    
    case $choice in
        1)
            kill_port $default_port
            echo $default_port
            ;;
        2)
            read -p "Enter new port for $service: " new_port
            echo $new_port
            ;;
        3)
            echo "skip"
            ;;
        *)
            print_error "Invalid choice. Skipping $service" >&2
            echo "skip"
            ;;
    esac
}

# Function to cleanup on exit
cleanup() {
    echo ""
    print_header "Shutting Down Services"
    
    # Stop Docker containers
    print_info "Stopping Docker containers..."
    cd /Users/maham/susu
    docker-compose down 2>&1 | tee -a "$LOG_DIR/docker.log" || true
    
    if [ -f "$PID_FILE" ]; then
        while read pid; do
            if ps -p $pid > /dev/null 2>&1; then
                print_info "Stopping process $pid"
                kill $pid 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm "$PID_FILE"
    fi
    
    # Kill emulator
    pkill -f "emulator @Pixel_8_Pro" 2>/dev/null || true
    
    print_success "All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Clear PID file
> "$PID_FILE"

print_header "🚀 SusuSave Development Environment"
echo ""
print_info "This script will start all development services:"
echo "  🐳 Docker Services (PostgreSQL + Redis)"
echo "  📄 Landing Page (Python HTTP Server)"
echo "  🌐 PWA Web App (React + Vite)"
echo "  👑 Admin CRM Portal (React + Vite)"
echo "  🔧 Backend API (FastAPI)"
echo "  🌍 Ngrok Tunnel (for USSD callbacks)"
echo "  📱 iOS Simulator (Expo)"
echo "  🤖 Android Emulator (Expo)"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# ============================================
# 0. Start Docker Services (Database)
# ============================================
print_header "0️⃣  Docker Services (PostgreSQL + Redis)"

print_info "Checking Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    print_warning "Please install Docker Desktop from https://docker.com"
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running"
    print_warning "Please start Docker Desktop and try again"
    exit 1
fi
print_success "Docker is running"

print_info "Starting PostgreSQL and Redis containers..."
cd /Users/maham/susu
docker-compose up -d db redis 2>&1 | tee -a "$LOG_DIR/docker.log"

# Wait for database to be ready
print_info "Waiting for database to be ready..."
sleep 5

if docker ps | grep -q sususave_db; then
    print_success "PostgreSQL container running"
else
    print_error "Failed to start PostgreSQL container"
    print_info "Check logs: docker-compose logs db"
    exit 1
fi

if docker ps | grep -q sususave_redis; then
    print_success "Redis container running"
else
    print_warning "Redis container not running (optional service)"
fi

# ============================================
# 1. Check and Start Backend API
# ============================================
print_header "1️⃣  Backend API (Port $BACKEND_PORT)"

if ! check_port $BACKEND_PORT; then
    BACKEND_PORT=$(ask_port "Backend API" $BACKEND_PORT)
fi

if [ "$BACKEND_PORT" != "skip" ]; then
    print_info "Starting Backend API on port $BACKEND_PORT..."
    cd /Users/maham/susu/backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > "$LOG_DIR/backend.log" 2>&1 &
    echo $! >> "$PID_FILE"
    
    sleep 3
    if curl -s http://localhost:$BACKEND_PORT/docs > /dev/null; then
        print_success "Backend API running at http://localhost:$BACKEND_PORT"
        print_info "API Docs: http://localhost:$BACKEND_PORT/docs"
    else
        print_error "Backend API failed to start. Check $LOG_DIR/backend.log"
    fi
else
    print_warning "Skipping Backend API"
fi

# ============================================
# 2. Check and Start Ngrok
# ============================================
print_header "2️⃣  Ngrok Tunnel"

if [ "$BACKEND_PORT" != "skip" ]; then
    print_info "Starting ngrok tunnel for port $BACKEND_PORT..."
    
    # Check if ngrok is installed
    if ! command -v ngrok &> /dev/null; then
        print_error "ngrok is not installed. Install it from https://ngrok.com/"
        print_warning "Skipping ngrok tunnel"
    else
        nohup ngrok http $BACKEND_PORT --log=stdout > "$LOG_DIR/ngrok.log" 2>&1 &
        echo $! >> "$PID_FILE"
        
        sleep 3
        
        # Extract ngrok URL
        NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o 'https://[^"]*\.ngrok[^"]*' | head -1)
        
        if [ ! -z "$NGROK_URL" ]; then
            print_success "Ngrok tunnel running: $NGROK_URL"
            print_info "AfricaTalking USSD Callback URL:"
            echo -e "${CYAN}   $NGROK_URL/ussd/callback${NC}"
            print_info "Ngrok Dashboard: http://localhost:4040"
        else
            print_warning "Could not get ngrok URL. Check $LOG_DIR/ngrok.log"
        fi
    fi
else
    print_warning "Skipping ngrok (no backend running)"
fi

# ============================================
# 3. Check and Start Landing Page
# ============================================
print_header "3️⃣  Landing Page (Port $LANDING_PORT)"

if ! check_port $LANDING_PORT; then
    LANDING_PORT=$(ask_port "Landing Page" $LANDING_PORT)
fi

if [ "$LANDING_PORT" != "skip" ]; then
    print_info "Starting Landing Page on port $LANDING_PORT..."
    cd /Users/maham/susu/web
    nohup python3 -m http.server $LANDING_PORT > "$LOG_DIR/landing.log" 2>&1 &
    echo $! >> "$PID_FILE"
    
    sleep 2
    print_success "Landing Page running at http://localhost:$LANDING_PORT"
else
    print_warning "Skipping Landing Page"
fi

# ============================================
# 4. Check and Start PWA Web App
# ============================================
print_header "4️⃣  PWA Web App (Port $PWA_PORT)"

if ! check_port $PWA_PORT; then
    PWA_PORT=$(ask_port "PWA Web App" $PWA_PORT)
fi

if [ "$PWA_PORT" != "skip" ]; then
    print_info "Starting PWA Web App on port $PWA_PORT..."
    cd /Users/maham/susu/web/app
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found. Running npm install..."
        npm install
    fi
    
    # Set port in environment
    export PORT=$PWA_PORT
    nohup npm run dev -- --port $PWA_PORT > "$LOG_DIR/pwa.log" 2>&1 &
    echo $! >> "$PID_FILE"
    
    sleep 5
    print_success "PWA Web App running at http://localhost:$PWA_PORT"
else
    print_warning "Skipping PWA Web App"
fi

# ============================================
# 5. Check and Start Admin CRM Portal
# ============================================
print_header "5️⃣  Admin CRM Portal (Port $ADMIN_PORT)"

if ! check_port $ADMIN_PORT; then
    ADMIN_PORT=$(ask_port "Admin CRM Portal" $ADMIN_PORT)
fi

if [ "$ADMIN_PORT" != "skip" ]; then
    print_info "Starting Admin CRM Portal on port $ADMIN_PORT..."
    cd /Users/maham/susu/web/admin
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found. Running npm install..."
        npm install
    fi
    
    # Set port in environment
    export PORT=$ADMIN_PORT
    nohup npm run dev -- --port $ADMIN_PORT > "$LOG_DIR/admin.log" 2>&1 &
    echo $! >> "$PID_FILE"
    
    sleep 5
    print_success "Admin CRM Portal running at http://localhost:$ADMIN_PORT"
    print_info "Login with your super admin credentials"
else
    print_warning "Skipping Admin CRM Portal"
fi

# ============================================
# 6. Start Android Emulator
# ============================================
print_header "6️⃣  Android Emulator"

read -p "Start Android emulator? (y/n): " start_android
if [ "$start_android" = "y" ] || [ "$start_android" = "Y" ]; then
    print_info "Setting up Android environment..."
    export ANDROID_HOME="$HOME/Library/Android/sdk"
    export ANDROID_SDK_ROOT="$HOME/Library/Android/sdk"
    export PATH="$ANDROID_SDK_ROOT/emulator:$ANDROID_SDK_ROOT/platform-tools:$PATH"
    
    # Check if emulator is already running
    EMULATOR_RUNNING=$($ANDROID_SDK_ROOT/platform-tools/adb devices | grep "emulator-" | grep "device" || true)
    
    if [ -z "$EMULATOR_RUNNING" ]; then
        print_info "Launching Pixel 8 Pro emulator..."
        nohup $ANDROID_SDK_ROOT/emulator/emulator @Pixel_8_Pro -no-snapshot-load > "$LOG_DIR/emulator.log" 2>&1 &
        
        print_info "Waiting for emulator to boot (this may take 1-2 minutes)..."
        $ANDROID_SDK_ROOT/platform-tools/adb wait-for-device
        
        # Wait for boot to complete
        while [ "$($ANDROID_SDK_ROOT/platform-tools/adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" != "1" ]; do
            sleep 2
        done
        
        print_success "Android emulator is ready!"
    else
        print_success "Android emulator is already running"
    fi
else
    print_warning "Skipping Android emulator"
fi

# ============================================
# 7. Start Expo (for both iOS and Android)
# ============================================
print_header "7️⃣  Expo Development Server"

read -p "Start Expo for mobile development? (y/n): " start_expo
if [ "$start_expo" = "y" ] || [ "$start_expo" = "Y" ]; then
    print_info "Starting Expo..."
    cd /Users/maham/susu/mobile/SusuSaveMobile
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found. Running npm install..."
        npm install
    fi
    
    # Set API URL
    if [ "$BACKEND_PORT" != "skip" ]; then
        export EXPO_PUBLIC_API_URL="http://127.0.0.1:$BACKEND_PORT"
    else
        export EXPO_PUBLIC_API_URL="http://127.0.0.1:8000"
    fi
    
    print_info "Starting Expo with API URL: $EXPO_PUBLIC_API_URL"
    
    # Start Expo in the foreground (so we can interact with it)
    npx expo start --localhost --clear
else
    print_warning "Skipping Expo"
fi

# ============================================
# Summary
# ============================================
echo ""
print_header "🎉 Development Environment Ready!"
echo ""
print_success "Services Running:"
echo ""
echo -e "${GREEN}✓${NC} Docker DB:        PostgreSQL (Port 5432)"
echo -e "${GREEN}✓${NC} Docker Redis:     Redis (Port 6379)"
if [ "$BACKEND_PORT" != "skip" ]; then
    echo -e "${GREEN}✓${NC} Backend API:      http://localhost:$BACKEND_PORT"
    echo -e "${GREEN}✓${NC} API Docs:         http://localhost:$BACKEND_PORT/docs"
fi
if [ ! -z "$NGROK_URL" ]; then
    echo -e "${GREEN}✓${NC} Ngrok Tunnel:     $NGROK_URL"
    echo -e "${GREEN}✓${NC} Ngrok Dashboard:  http://localhost:4040"
fi
if [ "$LANDING_PORT" != "skip" ]; then
    echo -e "${GREEN}✓${NC} Landing Page:     http://localhost:$LANDING_PORT"
fi
if [ "$PWA_PORT" != "skip" ]; then
    echo -e "${GREEN}✓${NC} PWA Web App:      http://localhost:$PWA_PORT"
fi
if [ "$ADMIN_PORT" != "skip" ]; then
    echo -e "${GREEN}✓${NC} Admin Portal:     http://localhost:$ADMIN_PORT"
fi
if [ "$start_android" = "y" ] || [ "$start_android" = "Y" ]; then
    echo -e "${GREEN}✓${NC} Android Emulator: Running (Pixel 8 Pro)"
fi
echo ""
print_info "Logs are available in: $LOG_DIR"
echo ""
print_warning "Press Ctrl+C to stop all services"
echo ""

# Keep script running
while true; do
    sleep 1
done

