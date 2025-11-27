#!/bin/bash

# SusuSave Production Environment Startup Script
# This script starts all production services with optimizations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Production ports
LANDING_PORT=80
PWA_PORT=3000
ADMIN_PORT=3001
BACKEND_PORT=8000

# PID file to track running processes
PID_FILE="/var/tmp/susu_prod_pids.txt"
LOG_DIR="/var/log/susu"

# Create log directory (may need sudo)
if [ ! -d "$LOG_DIR" ]; then
    echo "Creating log directory (may require sudo password)..."
    sudo mkdir -p "$LOG_DIR"
    sudo chown $(whoami) "$LOG_DIR"
fi

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
        sudo kill -9 $pid 2>/dev/null || true
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
    
    print_success "All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Clear PID file
> "$PID_FILE"

print_header "🚀 SusuSave Production Environment"
echo ""
print_warning "PRODUCTION MODE - Optimized for performance"
echo ""
print_info "This script will start all production services:"
echo "  🐳 Docker Services (PostgreSQL + Redis)"
echo "  📄 Landing Page (Production Build)"
echo "  🌐 PWA Web App (Production Build)"
echo "  👑 Admin CRM Portal (Production Build)"
echo "  🔧 Backend API (Production Mode - Multiple Workers)"
echo "  🌍 Ngrok Tunnel (Optional - for testing)"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# ============================================
# Pre-flight Checks
# ============================================
print_header "🔍 Pre-flight Checks"

print_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

print_info "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi
print_success "Node.js found: $(node --version)"

print_info "Checking npm installation..."
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi
print_success "npm found: $(npm --version)"

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
# 1. Build and Start Backend API
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
    
    # Install/update dependencies
    print_info "Checking dependencies..."
    pip install -q -r requirements.txt
    
    # Run database migrations
    print_info "Running database migrations..."
    alembic upgrade head 2>&1 | tee -a "$LOG_DIR/backend.log"
    
    # Start with gunicorn (production WSGI server) with multiple workers
    print_info "Starting with Gunicorn (4 workers)..."
    nohup gunicorn app.main:app \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:$BACKEND_PORT \
        --access-logfile "$LOG_DIR/backend-access.log" \
        --error-logfile "$LOG_DIR/backend-error.log" \
        --log-level warning \
        --timeout 120 \
        --keep-alive 5 \
        > "$LOG_DIR/backend.log" 2>&1 &
    
    echo $! >> "$PID_FILE"
    
    sleep 5
    if curl -s http://localhost:$BACKEND_PORT/docs > /dev/null; then
        print_success "Backend API running at http://localhost:$BACKEND_PORT"
        print_info "API Docs: http://localhost:$BACKEND_PORT/docs"
    else
        print_warning "Backend API may be starting. Check $LOG_DIR/backend.log"
    fi
else
    print_warning "Skipping Backend API"
fi

# ============================================
# 2. Optional: Start Ngrok
# ============================================
print_header "2️⃣  Ngrok Tunnel (Optional)"

read -p "Start ngrok tunnel for testing? (y/n): " start_ngrok
if [ "$start_ngrok" = "y" ] || [ "$start_ngrok" = "Y" ]; then
    if [ "$BACKEND_PORT" != "skip" ]; then
        print_info "Starting ngrok tunnel for port $BACKEND_PORT..."
        
        if ! command -v ngrok &> /dev/null; then
            print_error "ngrok is not installed. Install it from https://ngrok.com/"
            print_warning "Skipping ngrok tunnel"
        else
            nohup ngrok http $BACKEND_PORT --log=stdout > "$LOG_DIR/ngrok.log" 2>&1 &
            echo $! >> "$PID_FILE"
            
            sleep 3
            
            NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o 'https://[^"]*\.ngrok[^"]*' | head -1)
            
            if [ ! -z "$NGROK_URL" ]; then
                print_success "Ngrok tunnel running: $NGROK_URL"
                print_info "AfricaTalking USSD Callback URL:"
                echo -e "${CYAN}   $NGROK_URL/ussd/callback${NC}"
            else
                print_warning "Could not get ngrok URL. Check $LOG_DIR/ngrok.log"
            fi
        fi
    else
        print_warning "Skipping ngrok (no backend running)"
    fi
else
    print_warning "Skipping ngrok tunnel"
fi

# ============================================
# 3. Build and Start Landing Page
# ============================================
print_header "3️⃣  Landing Page (Port $LANDING_PORT)"

if ! check_port $LANDING_PORT; then
    LANDING_PORT=$(ask_port "Landing Page" $LANDING_PORT)
fi

if [ "$LANDING_PORT" != "skip" ]; then
    print_info "Starting Landing Page on port $LANDING_PORT..."
    cd /Users/maham/susu/web
    
    # Use a production-ready server (nginx or http-server with caching)
    if command -v http-server &> /dev/null; then
        print_info "Using http-server (with caching enabled)..."
        nohup http-server -p $LANDING_PORT -c-1 --cors > "$LOG_DIR/landing.log" 2>&1 &
        echo $! >> "$PID_FILE"
    else
        print_warning "http-server not found. Install with: npm install -g http-server"
        print_info "Using Python HTTP server (not recommended for production)..."
        
        if [ $LANDING_PORT -lt 1024 ]; then
            nohup sudo python3 -m http.server $LANDING_PORT > "$LOG_DIR/landing.log" 2>&1 &
        else
            nohup python3 -m http.server $LANDING_PORT > "$LOG_DIR/landing.log" 2>&1 &
        fi
        echo $! >> "$PID_FILE"
    fi
    
    sleep 2
    print_success "Landing Page running at http://localhost:$LANDING_PORT"
else
    print_warning "Skipping Landing Page"
fi

# ============================================
# 4. Build and Start PWA Web App
# ============================================
print_header "4️⃣  PWA Web App (Port $PWA_PORT)"

if ! check_port $PWA_PORT; then
    PWA_PORT=$(ask_port "PWA Web App" $PWA_PORT)
fi

if [ "$PWA_PORT" != "skip" ]; then
    cd /Users/maham/susu/web/app
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found. Running npm install..."
        npm install
    fi
    
    # Build production version
    print_info "Building PWA for production..."
    npm run build 2>&1 | tee -a "$LOG_DIR/pwa-build.log"
    
    if [ ! -d "dist" ]; then
        print_error "Build failed. Check $LOG_DIR/pwa-build.log"
    else
        print_success "Build completed successfully"
        
        # Serve with production server
        print_info "Starting PWA Web App on port $PWA_PORT..."
        
        if command -v http-server &> /dev/null; then
            print_info "Using http-server..."
            nohup http-server dist -p $PWA_PORT -c-1 --cors --gzip > "$LOG_DIR/pwa.log" 2>&1 &
            echo $! >> "$PID_FILE"
        else
            print_warning "http-server not found. Using npm preview..."
            nohup npm run preview -- --port $PWA_PORT > "$LOG_DIR/pwa.log" 2>&1 &
            echo $! >> "$PID_FILE"
        fi
        
        sleep 3
        print_success "PWA Web App running at http://localhost:$PWA_PORT"
    fi
else
    print_warning "Skipping PWA Web App"
fi

# ============================================
# 5. Build and Start Admin CRM Portal
# ============================================
print_header "5️⃣  Admin CRM Portal (Port $ADMIN_PORT)"

if ! check_port $ADMIN_PORT; then
    ADMIN_PORT=$(ask_port "Admin CRM Portal" $ADMIN_PORT)
fi

if [ "$ADMIN_PORT" != "skip" ]; then
    cd /Users/maham/susu/web/admin
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found. Running npm install..."
        npm install
    fi
    
    # Build production version
    print_info "Building Admin CRM Portal for production..."
    npm run build 2>&1 | tee -a "$LOG_DIR/admin-build.log"
    
    if [ ! -d "dist" ]; then
        print_error "Build failed. Check $LOG_DIR/admin-build.log"
    else
        print_success "Build completed successfully"
        
        # Serve with production server
        print_info "Starting Admin CRM Portal on port $ADMIN_PORT..."
        
        if command -v http-server &> /dev/null; then
            print_info "Using http-server..."
            nohup http-server dist -p $ADMIN_PORT -c-1 --cors --gzip > "$LOG_DIR/admin.log" 2>&1 &
            echo $! >> "$PID_FILE"
        else
            print_warning "http-server not found. Using npm preview..."
            nohup npm run preview -- --port $ADMIN_PORT > "$LOG_DIR/admin.log" 2>&1 &
            echo $! >> "$PID_FILE"
        fi
        
        sleep 3
        print_success "Admin CRM Portal running at http://localhost:$ADMIN_PORT"
        print_info "Login with your super admin credentials"
    fi
else
    print_warning "Skipping Admin CRM Portal"
fi

# ============================================
# Summary
# ============================================
echo ""
print_header "🎉 Production Environment Ready!"
echo ""
print_success "Services Running:"
echo ""
echo -e "${GREEN}✓${NC} Docker DB:        PostgreSQL (Port 5432)"
echo -e "${GREEN}✓${NC} Docker Redis:     Redis (Port 6379)"
if [ "$BACKEND_PORT" != "skip" ]; then
    echo -e "${GREEN}✓${NC} Backend API:      http://localhost:$BACKEND_PORT"
    echo -e "${GREEN}✓${NC} API Docs:         http://localhost:$BACKEND_PORT/docs"
    echo -e "${CYAN}ℹ${NC}  Workers:          4 (Gunicorn)"
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
echo ""
print_info "Logs are available in: $LOG_DIR"
echo ""
print_info "To monitor logs:"
echo "  Docker:   docker-compose logs -f db"
echo "  Backend:  tail -f $LOG_DIR/backend.log"
echo "  Landing:  tail -f $LOG_DIR/landing.log"
echo "  PWA:      tail -f $LOG_DIR/pwa.log"
echo "  Admin:    tail -f $LOG_DIR/admin.log"
echo ""
print_warning "Press Ctrl+C to stop all services"
echo ""

# Save service info to file
cat > /var/tmp/susu_services.txt <<EOF
SusuSave Production Services

Started: $(date)

Docker DB: PostgreSQL (Port 5432)
Docker Redis: Redis (Port 6379)
Backend API: http://localhost:$BACKEND_PORT
Landing Page: http://localhost:$LANDING_PORT
PWA Web App: http://localhost:$PWA_PORT
Admin Portal: http://localhost:$ADMIN_PORT
$([ ! -z "$NGROK_URL" ] && echo "Ngrok: $NGROK_URL")

Logs: $LOG_DIR
PIDs: $PID_FILE
EOF

print_success "Service info saved to /var/tmp/susu_services.txt"

# Keep script running
while true; do
    # Health check every 60 seconds
    sleep 60
    
    # Check if services are still running
    if [ "$BACKEND_PORT" != "skip" ]; then
        if ! curl -s http://localhost:$BACKEND_PORT/docs > /dev/null; then
            print_warning "Backend API health check failed!"
        fi
    fi
done

