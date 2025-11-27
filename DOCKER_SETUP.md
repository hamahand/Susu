# 🐳 Docker Setup Guide for SusuSave

Complete guide for running SusuSave with Docker Compose - includes backend, web app, admin panel, and all dependencies.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Detailed Setup](#detailed-setup)
- [Commands Reference](#commands-reference)
- [Environment Configuration](#environment-configuration)
- [Development Workflow](#development-workflow)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Docker Desktop** (macOS/Windows) or **Docker Engine** (Linux)
  - Download: https://www.docker.com/products/docker-desktop
  - Minimum version: Docker 20.10+, Docker Compose 2.0+
- **4GB RAM minimum** (8GB+ recommended)
- **10GB free disk space**

### Verify Installation

```bash
docker --version
docker-compose --version
docker info
```

## Quick Start

### 1. Clone and Navigate

```bash
cd /path/to/susu
```

### 2. Start All Services

The simplest way to get everything running:

```bash
chmod +x docker-start.sh
./docker-start.sh up
```

This will automatically:
- ✅ Check Docker prerequisites
- ✅ Create `.env.docker` from `env.example`
- ✅ Build all Docker images
- ✅ Start PostgreSQL, Redis, Backend, Web App, and Admin Panel
- ✅ Run database migrations
- ✅ Show service URLs

### 3. Access the Services

After startup (wait ~15 seconds), access:

| Service | URL | Description |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | FastAPI backend |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Web App** | http://localhost:5173 | User-facing PWA |
| **Admin Panel** | http://localhost:5174 | Admin dashboard |
| **PostgreSQL** | localhost:5432 | Database (credentials: sususer/suspass) |
| **Redis** | localhost:6379 | Session cache |

### 4. Stop Services

```bash
./docker-start.sh down
```

## Architecture

### Docker Services

```
┌─────────────────────────────────────────────────┐
│                  Docker Network                  │
│  (sususave_network)                             │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │PostgreSQL│  │  Redis   │  │   Backend    │  │
│  │  :5432   │  │  :6379   │  │ FastAPI:8000 │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │   Web App    │  │ Admin Panel  │            │
│  │ Vite :5173   │  │ Vite :5174   │            │
│  └──────────────┘  └──────────────┘            │
│                                                  │
│  ┌──────────────────────────────┐ (Optional)   │
│  │     Nginx Reverse Proxy      │ Production   │
│  │       :80 / :443             │              │
│  └──────────────────────────────┘              │
└─────────────────────────────────────────────────┘
```

### Service Details

1. **Database (PostgreSQL)**
   - Persistent data storage
   - Health checks enabled
   - Automatic backup support

2. **Cache (Redis)**
   - USSD session management
   - Rate limiting
   - Optional but recommended

3. **Backend (FastAPI)**
   - Python 3.11
   - Auto-reload in dev mode
   - Runs migrations on startup

4. **Web App (React + Vite)**
   - Progressive Web App
   - Hot module replacement
   - Service worker support

5. **Admin Panel (React + Vite)**
   - Management dashboard
   - Real-time analytics
   - User administration

6. **Nginx (Production only)**
   - SSL/TLS termination
   - Load balancing
   - Static file serving
   - Rate limiting

## Detailed Setup

### Step 1: Environment Configuration

The startup script creates `.env.docker` automatically, but you can customize it:

```bash
# Copy example if not done automatically
cp backend/env.example backend/.env.docker

# Edit with your credentials
nano backend/.env.docker
```

**Important settings for Docker:**

```env
# Use Docker service names (not localhost)
DATABASE_URL=postgresql://sususer:suspass@db:5432/sususave
REDIS_URL=redis://redis:6379/0
USE_REDIS=True

# Add your API keys
MTN_MOMO_SUBSCRIPTION_KEY=your-key-here
AT_API_KEY=your-key-here
```

### Step 2: Build Images

```bash
# Build all images without starting
docker-compose build

# Or build specific service
docker-compose build backend
```

### Step 3: Start Services

```bash
# Development mode (hot reload enabled)
./docker-start.sh up

# Production mode (with nginx)
./docker-start.sh up prod

# Or manually with docker-compose
docker-compose up -d
```

### Step 4: Verify Services

```bash
# Check running containers
docker-compose ps

# View all logs
docker-compose logs -f

# Check specific service
docker-compose logs -f backend
```

## Commands Reference

### Using docker-start.sh (Recommended)

```bash
# Basic commands
./docker-start.sh up              # Start in development mode
./docker-start.sh up prod         # Start in production mode
./docker-start.sh down            # Stop all services
./docker-start.sh restart         # Restart services
./docker-start.sh rebuild         # Rebuild and restart

# Logs
./docker-start.sh logs            # View all logs
./docker-start.sh logs backend    # View backend logs
./docker-start.sh logs webapp     # View web app logs

# Service status
./docker-start.sh ps              # Show running services

# Database operations
./docker-start.sh db              # Connect to PostgreSQL
./docker-start.sh migrate         # Run migrations
./docker-start.sh seed            # Seed test data

# Shell access
./docker-start.sh shell           # Backend shell (default)
./docker-start.sh shell webapp    # Web app shell
./docker-start.sh shell admin     # Admin shell

# Testing
./docker-start.sh test            # Run backend tests

# Cleanup
./docker-start.sh clean           # Remove all containers and volumes
```

### Using docker-compose Directly

```bash
# Start services
docker-compose up -d              # Detached mode
docker-compose up --build         # Rebuild images

# Stop services
docker-compose down               # Stop and remove containers
docker-compose down -v            # Also remove volumes (clean slate)

# Logs
docker-compose logs -f            # Follow all logs
docker-compose logs -f backend    # Follow backend logs
docker-compose logs --tail=100 backend  # Last 100 lines

# Service management
docker-compose ps                 # List services
docker-compose restart backend    # Restart service
docker-compose stop webapp        # Stop service
docker-compose start webapp       # Start service

# Execute commands
docker-compose exec backend sh    # Open shell
docker-compose exec db psql -U sususer -d sususave  # Database

# Scale services (production)
docker-compose up -d --scale backend=3
```

## Environment Configuration

### Development vs Production

**Development (.env.docker):**
```env
DATABASE_URL=postgresql://sususer:suspass@db:5432/sususave
ENABLE_REAL_SMS=False
ENABLE_REAL_MOMO=False
MTN_ENVIRONMENT=sandbox
```

**Production:**
```env
# Use external database
DATABASE_URL=postgresql://user:pass@prod-db-host:5432/sususave

# Use external Redis
REDIS_URL=redis://prod-redis-host:6379/0

# Enable real services
ENABLE_REAL_SMS=True
ENABLE_REAL_MOMO=True
MTN_ENVIRONMENT=production
MTN_MOMO_TARGET_ENVIRONMENT=production

# Production callbacks
MTN_CALLBACK_URL=https://your-domain.com/ussd/callback
```

### Updating Environment Variables

After changing `.env.docker`:

```bash
# Restart affected service
docker-compose restart backend

# Or rebuild if dependencies changed
docker-compose up --build -d backend
```

## Development Workflow

### Making Code Changes

**Backend code** is mounted as a volume with hot reload:

1. Edit files in `backend/app/`
2. Uvicorn auto-reloads
3. Watch logs: `./docker-start.sh logs backend`

**Frontend code** (web app & admin) also has hot reload:

1. Edit files in `web/app/src/` or `web/admin/src/`
2. Vite auto-reloads
3. Browser updates automatically

### Database Migrations

```bash
# Create new migration (on host machine, outside Docker)
cd backend
source venv/bin/activate  # If you have local env
alembic revision --autogenerate -m "description"

# Or create migration inside Docker
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations (automatic on startup, or manually)
./docker-start.sh migrate
# or
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

### Database Access

```bash
# Interactive psql
./docker-start.sh db

# Or manually
docker-compose exec db psql -U sususer -d sususave

# Common SQL commands
\dt                    # List tables
\d users              # Describe table
SELECT * FROM users LIMIT 10;
\q                    # Quit
```

### Debugging

```bash
# View logs in real-time
./docker-start.sh logs backend

# Check service health
curl http://localhost:8000/docs
curl http://localhost:5173/

# Inspect container
docker inspect sususave_backend

# Open shell for debugging
./docker-start.sh shell backend

# Inside container, test database connection
python -c "from app.database import SessionLocal; print('DB OK')"
```

### Running Tests

```bash
# Run all backend tests
./docker-start.sh test

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py

# Run with coverage
docker-compose exec backend pytest --cov=app tests/

# Run frontend tests (if configured)
docker-compose exec webapp npm test
docker-compose exec admin npm test
```

## Production Deployment

### Pre-deployment Checklist

- [ ] Update `.env.docker` with production credentials
- [ ] Generate strong `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Set `ENABLE_REAL_SMS=True` and `ENABLE_REAL_MOMO=True`
- [ ] Configure production database (AWS RDS, Google Cloud SQL, etc.)
- [ ] Configure production Redis (ElastiCache, Cloud Memorystore, etc.)
- [ ] Set up SSL certificates
- [ ] Configure domain and DNS
- [ ] Set up backup strategy
- [ ] Configure monitoring and alerts

### Production docker-compose.yml

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    image: your-registry/sususave-backend:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
    restart: always

  webapp:
    build:
      context: ./web/app
      dockerfile: Dockerfile
      target: production
    image: your-registry/sususave-webapp:latest
    restart: always

  admin:
    build:
      context: ./web/admin
      dockerfile: Dockerfile
      target: production
    image: your-registry/sususave-admin:latest
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - webapp
      - admin
    restart: always
```

### Deploy to Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Push to registry
docker-compose -f docker-compose.prod.yml push

# On production server, pull and start
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### SSL/TLS Setup

**Option 1: Let's Encrypt (Recommended)**

```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Certificates will be in /etc/letsencrypt/live/your-domain.com/
# Update nginx.conf to use them
```

**Option 2: Self-signed (Development)**

```bash
# Script creates self-signed certs automatically
./docker-start.sh up prod
```

## Troubleshooting

### Port Already in Use

**Problem:** "Port 8000 is already allocated"

**Solution:**
```bash
# Find what's using the port
lsof -ti:8000
lsof -ti:5432
lsof -ti:6379

# Kill the process
kill -9 $(lsof -ti:8000)

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Map to different host port
```

### Docker Daemon Not Running

**Problem:** "Cannot connect to Docker daemon"

**Solution:**
```bash
# macOS - Start Docker Desktop
open -a Docker

# Linux - Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify
docker info
```

### Container Keeps Restarting

**Problem:** Service shows "Restarting" in `docker-compose ps`

**Solution:**
```bash
# Check logs
docker-compose logs backend

# Common causes:
# 1. Database not ready - wait longer
# 2. Migration error - check alembic versions
# 3. Missing environment variables - verify .env.docker
# 4. Port conflict - change port mapping

# Clean restart
docker-compose down -v
docker-compose up --build
```

### Database Connection Errors

**Problem:** "Could not connect to database"

**Solution:**
```bash
# Check if database is running
docker-compose ps db

# Check database health
docker-compose exec db pg_isready -U sususer

# Verify DATABASE_URL in .env.docker
# Must use 'db' as hostname, not 'localhost'
DATABASE_URL=postgresql://sususer:suspass@db:5432/sususave

# Test connection from backend
docker-compose exec backend python -c "from app.database import engine; print(engine.url)"
```

### Permission Errors

**Problem:** "Permission denied" errors

**Solution:**
```bash
# Fix script permissions
chmod +x docker-start.sh

# Fix file ownership
sudo chown -R $USER:$USER .

# If Docker can't access files on Linux
sudo usermod -aG docker $USER
newgrp docker
```

### Out of Disk Space

**Problem:** "No space left on device"

**Solution:**
```bash
# Remove unused images and containers
docker system prune -a

# Remove unused volumes
docker volume prune

# Check disk usage
docker system df

# Remove specific old images
docker images
docker rmi <image-id>
```

### Migration Errors

**Problem:** "Alembic migration failed"

**Solution:**
```bash
# Check current version
docker-compose exec backend alembic current

# Check migration history
docker-compose exec backend alembic history

# Clean slate (WARNING: deletes all data)
docker-compose down -v
docker-compose up --build

# Or manually fix migration
docker-compose exec backend alembic stamp head
docker-compose exec backend alembic upgrade head
```

### Frontend Not Loading

**Problem:** Web app or admin panel shows errors

**Solution:**
```bash
# Check if Vite is running
docker-compose logs webapp
docker-compose logs admin

# Check if backend is accessible
curl http://localhost:8000/docs

# Verify environment variables
docker-compose exec webapp env | grep VITE

# Rebuild node_modules
docker-compose down
docker-compose up --build webapp
```

### Redis Connection Issues

**Problem:** "Could not connect to Redis"

**Solution:**
```bash
# Check Redis status
docker-compose ps redis

# Test Redis
docker-compose exec redis redis-cli ping
# Should return: PONG

# Verify REDIS_URL
docker-compose exec backend env | grep REDIS

# Can disable Redis if not needed
# In .env.docker: USE_REDIS=False
```

### Network Issues

**Problem:** Containers can't communicate

**Solution:**
```bash
# Check network
docker network ls
docker network inspect susu_sususave_network

# Recreate network
docker-compose down
docker network prune
docker-compose up

# Verify service names resolve
docker-compose exec backend ping db
docker-compose exec backend ping redis
```

## Data Management

### Backup Database

```bash
# Create backup
docker-compose exec db pg_dump -U sususer sususave > backup_$(date +%Y%m%d).sql

# Automated backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR
docker-compose exec -T db pg_dump -U sususer sususave | gzip > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz
EOF
chmod +x backup.sh

# Run daily (cron)
0 2 * * * /path/to/backup.sh
```

### Restore Database

```bash
# Restore from backup
docker-compose exec -T db psql -U sususer sususave < backup_20251022.sql

# Or from gzipped backup
gunzip -c backup_20251022.sql.gz | docker-compose exec -T db psql -U sususer sususave
```

### Volume Management

```bash
# List volumes
docker volume ls | grep susu

# Inspect volume
docker volume inspect susu_postgres_data

# Backup volume
docker run --rm -v susu_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz /data

# Restore volume
docker run --rm -v susu_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_data.tar.gz -C /
```

## Monitoring

### Resource Usage

```bash
# Real-time stats
docker stats

# Specific container
docker stats sususave_backend

# Format output
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Health Checks

```bash
# Check all service health
docker-compose ps

# Backend health
curl -f http://localhost:8000/docs || echo "Backend unhealthy"

# Database health
docker-compose exec db pg_isready -U sususer || echo "Database unhealthy"

# Redis health
docker-compose exec redis redis-cli ping || echo "Redis unhealthy"
```

### Logs Management

```bash
# View logs with timestamps
docker-compose logs -f -t

# View last 100 lines
docker-compose logs --tail=100 backend

# Export logs
docker-compose logs --no-color > logs_$(date +%Y%m%d).txt

# Rotate logs (prevent disk fill)
docker-compose down
docker system prune
docker-compose up -d
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI with Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Nginx Docker Image](https://hub.docker.com/_/nginx)
- [Vite Production Build](https://vitejs.dev/guide/build.html)

## Support

If you encounter issues:

1. Check logs: `./docker-start.sh logs`
2. Check service status: `./docker-start.sh ps`
3. Try clean restart: `./docker-start.sh clean && ./docker-start.sh up`
4. Verify Docker resources (CPU, Memory, Disk)
5. Review this guide's Troubleshooting section
6. Check Docker is running: `docker info`

---

**Last Updated:** October 22, 2025
**Maintained by:** SusuSave Development Team
