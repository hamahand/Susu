#!/bin/bash

# SusuSave Docker Compose Startup Script
# Complete Docker orchestration for backend, web app, and admin panel

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print functions
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
    echo ""
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}   $1${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop from https://www.docker.com/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker Desktop."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Check if .env.docker exists
check_env_file() {
    if [ ! -f "backend/.env.docker" ]; then
        print_warning ".env.docker not found. Creating from env.example..."
        
        if [ -f "backend/env.example" ]; then
            cp backend/env.example backend/.env.docker
            
            # Update DATABASE_URL and REDIS_URL for Docker
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' 's|DATABASE_URL=.*|DATABASE_URL=postgresql://sususer:suspass@db:5432/sususave|g' backend/.env.docker
                sed -i '' 's|REDIS_URL=.*|REDIS_URL=redis://redis:6379/0|g' backend/.env.docker
                sed -i '' 's|USE_REDIS=False|USE_REDIS=True|g' backend/.env.docker
            else
                # Linux
                sed -i 's|DATABASE_URL=.*|DATABASE_URL=postgresql://sususer:suspass@db:5432/sususave|g' backend/.env.docker
                sed -i 's|REDIS_URL=.*|REDIS_URL=redis://redis:6379/0|g' backend/.env.docker
                sed -i 's|USE_REDIS=False|USE_REDIS=True|g' backend/.env.docker
            fi
            
            print_success "Created .env.docker from env.example"
            print_warning "Please update backend/.env.docker with your API keys if needed"
        else
            print_error "env.example not found in backend/"
            exit 1
        fi
    else
        print_success "Found .env.docker"
    fi
}

# Create SSL certificates for nginx (development self-signed)
create_ssl_certs() {
    if [ ! -d "docker/nginx/ssl" ]; then
        print_info "Creating self-signed SSL certificates for development..."
        mkdir -p docker/nginx/ssl
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout docker/nginx/ssl/key.pem \
            -out docker/nginx/ssl/cert.pem \
            -subj "/C=GH/ST=Greater Accra/L=Accra/O=SusuSave/OU=Development/CN=localhost" \
            2>/dev/null || print_warning "Could not create SSL certificates (nginx will not start in production mode)"
        
        print_success "SSL certificates created"
    fi
}

# Cleanup function
cleanup() {
    print_header "Stopping Services"
    docker-compose down
    print_success "Services stopped"
}

# Show service URLs
show_urls() {
    echo ""
    print_header "🎉 Services Started Successfully!"
    echo ""
    print_info "Backend API:         ${CYAN}http://localhost:8000${NC}"
    print_info "API Documentation:   ${CYAN}http://localhost:8000/docs${NC}"
    print_info "Web App (PWA):       ${CYAN}http://localhost:5173${NC}"
    print_info "Admin Panel:         ${CYAN}http://localhost:5174${NC}"
    print_info "PostgreSQL:          ${CYAN}localhost:5432${NC}"
    print_info "Redis:               ${CYAN}localhost:6379${NC}"
    echo ""
    print_info "Useful commands:"
    echo "  ${CYAN}docker-compose logs -f${NC}             View all logs"
    echo "  ${CYAN}docker-compose logs -f backend${NC}     View backend logs"
    echo "  ${CYAN}docker-compose logs -f webapp${NC}      View web app logs"
    echo "  ${CYAN}docker-compose logs -f admin${NC}       View admin logs"
    echo "  ${CYAN}docker-compose ps${NC}                  View running services"
    echo "  ${CYAN}./docker-start.sh down${NC}             Stop all services"
    echo "  ${CYAN}./docker-start.sh restart${NC}          Restart all services"
    echo "  ${CYAN}./docker-start.sh rebuild${NC}          Rebuild and restart"
    echo ""
}

# Main execution
main() {
    print_header "🚀 SusuSave Docker Compose Setup"
    
    # Check prerequisites
    check_docker
    check_env_file
    
    # Parse command line arguments
    COMMAND=${1:-"up"}
    MODE=${2:-"dev"}
    
    case $COMMAND in
        up|start)
            print_header "Starting Services"
            
            if [ "$MODE" = "prod" ] || [ "$MODE" = "production" ]; then
                print_info "Starting in PRODUCTION mode with nginx..."
                create_ssl_certs
                print_info "Building and starting all services (including nginx)..."
                docker-compose --profile production up --build -d
            else
                print_info "Starting in DEVELOPMENT mode..."
                print_info "Building and starting all services..."
                print_info "This may take a few minutes on first run..."
                
                # Stop any existing containers
                docker-compose down 2>/dev/null || true
                
                # Start services
                docker-compose up --build -d
            fi
            
            # Wait for services to be healthy
            print_info "Waiting for services to be ready..."
            sleep 15
            
            # Check if services are running
            SERVICES_OK=true
            
            if docker ps | grep -q sususave_backend; then
                print_success "Backend API is running"
            else
                print_error "Backend API failed to start. Check logs with: docker-compose logs backend"
                SERVICES_OK=false
            fi
            
            if docker ps | grep -q sususave_db; then
                print_success "PostgreSQL is running"
            else
                print_error "PostgreSQL failed to start. Check logs with: docker-compose logs db"
                SERVICES_OK=false
            fi
            
            if docker ps | grep -q sususave_redis; then
                print_success "Redis is running"
            else
                print_warning "Redis failed to start. Check logs with: docker-compose logs redis"
            fi
            
            if docker ps | grep -q sususave_webapp; then
                print_success "Web App is running"
            else
                print_warning "Web App failed to start. Check logs with: docker-compose logs webapp"
            fi
            
            if docker ps | grep -q sususave_admin; then
                print_success "Admin Panel is running"
            else
                print_warning "Admin Panel failed to start. Check logs with: docker-compose logs admin"
            fi
            
            if [ "$SERVICES_OK" = true ]; then
                show_urls
            else
                echo ""
                print_error "Some services failed to start. Check the logs for details."
                echo ""
            fi
            ;;
            
        down|stop)
            cleanup
            ;;
            
        restart)
            print_header "Restarting Services"
            docker-compose restart
            print_success "Services restarted"
            show_urls
            ;;
            
        rebuild)
            print_header "Rebuilding and Restarting Services"
            docker-compose down
            docker-compose up --build -d
            sleep 15
            print_success "Services rebuilt and restarted"
            show_urls
            ;;
            
        logs)
            SERVICE=${2:-""}
            if [ -z "$SERVICE" ]; then
                docker-compose logs -f
            else
                docker-compose logs -f $SERVICE
            fi
            ;;
            
        ps|status)
            print_header "Service Status"
            docker-compose ps
            ;;
            
        clean)
            print_header "Cleaning Up"
            print_warning "This will remove all containers, volumes, and data!"
            read -p "Are you sure? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                docker-compose down -v
                docker system prune -f
                print_success "Cleanup complete"
            else
                print_info "Cleanup cancelled"
            fi
            ;;
            
        shell)
            SERVICE=${2:-"backend"}
            print_info "Opening shell in $SERVICE container..."
            docker-compose exec $SERVICE sh
            ;;
            
        db)
            print_info "Connecting to PostgreSQL..."
            docker-compose exec db psql -U sususer -d sususave
            ;;
            
        migrate)
            print_info "Running database migrations..."
            docker-compose exec backend alembic upgrade head
            print_success "Migrations complete"
            ;;
            
        seed)
            print_info "Seeding database with test data..."
            docker-compose exec backend python seed_data.py
            print_success "Database seeded"
            ;;
            
        test)
            print_info "Running backend tests..."
            docker-compose exec backend pytest
            ;;
            
        *)
            echo "Usage: $0 {up|down|restart|rebuild|logs|ps|clean|shell|db|migrate|seed|test} [options]"
            echo ""
            echo "Commands:"
            echo "  up [mode]    - Start all services (mode: dev or prod, default: dev)"
            echo "  down         - Stop all services"
            echo "  restart      - Restart all services"
            echo "  rebuild      - Rebuild and restart all services"
            echo "  logs [svc]   - View logs (optional: specify service name)"
            echo "  ps           - Show running services"
            echo "  clean        - Remove all containers and volumes"
            echo "  shell [svc]  - Open shell in container (default: backend)"
            echo "  db           - Connect to PostgreSQL database"
            echo "  migrate      - Run database migrations"
            echo "  seed         - Seed database with test data"
            echo "  test         - Run backend tests"
            echo ""
            echo "Examples:"
            echo "  ./docker-start.sh up              # Start in development mode"
            echo "  ./docker-start.sh up prod         # Start in production mode with nginx"
            echo "  ./docker-start.sh logs backend    # View backend logs"
            echo "  ./docker-start.sh shell webapp    # Open shell in webapp container"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

