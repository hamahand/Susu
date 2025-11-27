# ✅ Startup Scripts Updated - Docker + Admin CRM

## What's Changed

Both startup scripts (`start-dev.sh` and `start-prod.sh`) have been updated to include:

1. ✅ **Docker Database** - PostgreSQL and Redis run in Docker containers
2. ✅ **Admin CRM Portal** - Automatic startup on port 3001
3. ✅ **Consistent Structure** - Same flow for dev and production
4. ✅ **Proper Cleanup** - Docker containers stop on Ctrl+C
5. ✅ **Production Ready** - Optimized for deployment

## New Service Flow

### Development (`./start-dev.sh`)
```
0️⃣  Docker Services → PostgreSQL + Redis
1️⃣  Backend API → FastAPI (port 8000)
2️⃣  Ngrok Tunnel → Public USSD endpoint
3️⃣  Landing Page → Static site (port 8080)
4️⃣  PWA Web App → User app (port 3000)
5️⃣  Admin CRM Portal → Admin dashboard (port 3001) 🆕
6️⃣  Android Emulator → Mobile testing
7️⃣  Expo Dev Server → React Native dev
```

### Production (`./start-prod.sh`)
```
0️⃣  Docker Services → PostgreSQL + Redis 🆕
1️⃣  Backend API → Multiple workers (port 8000)
2️⃣  Ngrok Tunnel → Optional testing
3️⃣  Landing Page → Production build (port 80)
4️⃣  PWA Web App → Production build (port 3000)
5️⃣  Admin CRM Portal → Production build (port 3001) 🆕
```

## Quick Start

### For Development

```bash
# Make sure Docker Desktop is running!
./start-dev.sh
```

**Services will start automatically:**
- ✅ PostgreSQL in Docker (port 5432)
- ✅ Redis in Docker (port 6379)
- ✅ Backend API (http://localhost:8000)
- ✅ PWA App (http://localhost:3000)
- ✅ **Admin Portal (http://localhost:3001)** 🆕
- ✅ Landing Page (http://localhost:8080)

### For Production

```bash
# Make sure Docker Desktop is running!
./start-prod.sh
```

**All services with production builds**

## Admin Portal Access

After starting with either script:

1. **Create Super Admin** (first time only):
   ```bash
   cd backend
   python create_super_admin.py
   ```

2. **Access Admin Portal**:
   - Dev: http://localhost:3001
   - Prod: http://localhost:3001

3. **Login** with the credentials you created

## Docker Integration

### What Runs in Docker

- ✅ **PostgreSQL 15** - Main database
- ✅ **Redis 7** - Session storage (optional)

### Why Docker?

- **Isolation**: Database runs separately from host
- **Consistency**: Same database version everywhere
- **Easy Setup**: No manual database installation
- **Data Persistence**: Data saved in Docker volumes
- **Production Ready**: Same setup for dev and prod

### Docker Commands

```bash
# View running containers
docker-compose ps

# View database logs
docker-compose logs -f db

# Stop containers
docker-compose down

# Restart containers
docker-compose restart db redis

# Remove all data (CAREFUL!)
docker-compose down -v
```

## Port Summary

| Service | Dev Port | Prod Port | Protocol |
|---------|----------|-----------|----------|
| PostgreSQL | 5432 | 5432 | TCP |
| Redis | 6379 | 6379 | TCP |
| Backend API | 8000 | 8000 | HTTP |
| PWA App | 3000 | 3000 | HTTP |
| **Admin Portal** | **3001** | **3001** | **HTTP** 🆕 |
| Landing Page | 8080 | 80 | HTTP |
| Ngrok | 4040 | 4040 | HTTP |
| Expo | 8081 | - | HTTP |

## Log Files

All logs are saved to:
- **Dev**: `/tmp/susu_logs/`
- **Prod**: `/var/log/susu/`

### Log Files Available

```bash
# Docker
docker-compose logs -f db          # PostgreSQL logs

# Application
tail -f /tmp/susu_logs/docker.log  # Docker startup logs
tail -f /tmp/susu_logs/backend.log # Backend API logs
tail -f /tmp/susu_logs/pwa.log     # PWA app logs
tail -f /tmp/susu_logs/admin.log   # Admin portal logs 🆕
tail -f /tmp/susu_logs/ngrok.log   # Ngrok tunnel logs
```

## Troubleshooting

### Docker Not Running
```
Error: Cannot connect to Docker daemon
```
**Solution**: Start Docker Desktop from Applications

### Port Already in Use
The scripts will automatically:
1. Detect port conflicts
2. Offer to kill the process
3. Let you choose a different port
4. Or skip that service

### Database Connection Failed
```
Error: Could not connect to database
```
**Solution**:
```bash
# Check Docker is running
docker ps

# Check PostgreSQL container
docker-compose ps db

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Admin Portal Won't Start
```bash
# Check if node_modules exists
cd web/admin
ls node_modules

# If missing, install
npm install

# Try starting manually
npm run dev
```

## Stopping Services

### Graceful Shutdown
Press `Ctrl+C` in the terminal running the startup script.

This will automatically:
- Stop all processes
- Stop Docker containers
- Clean up PID files
- Save shutdown time to logs

### Manual Cleanup
```bash
# Kill all ports
lsof -ti:3000,3001,8000,8080,4040,5432,6379 | xargs kill -9

# Stop Docker
docker-compose down

# Check nothing is running
docker ps
lsof -i:8000
```

## What Was Updated

### start-dev.sh Changes
- ✅ Added Docker service startup (section 0)
- ✅ Added Admin Portal startup (section 5)
- ✅ Renumbered sections (Android = 6, Expo = 7)
- ✅ Added Docker cleanup on exit
- ✅ Added Admin Portal to summary
- ✅ Added admin log monitoring

### start-prod.sh Changes
- ✅ Added Docker service startup (section 0)
- ✅ Added Admin Portal build & serve (section 5)
- ✅ Added Docker cleanup on exit
- ✅ Added Admin Portal to summary
- ✅ Added admin log monitoring

## Complete Service Overview

When you run `./start-dev.sh`, you get:

```
🐳 Docker DB (PostgreSQL) ──┐
🐳 Docker Redis             │ Infrastructure
                            │
🔧 Backend API (FastAPI)    │ Core Services
👑 Admin Portal (React)     │ 🆕
🌐 PWA App (React)          │
📄 Landing Page             │
                            │
🌍 Ngrok (Public tunnel)    │ Optional
📱 Mobile (Expo + Emulator) │
```

## Production Deployment

For production deployment:

1. **Start with Docker**:
   ```bash
   ./start-prod.sh
   ```

2. **Access Services**:
   - Landing: http://your-domain.com (port 80)
   - PWA App: http://your-domain.com:3000
   - Admin Portal: http://admin.your-domain.com (port 3001)
   - API: http://api.your-domain.com (port 8000)

3. **Set Up Reverse Proxy** (Nginx/Apache):
   - Route `admin.your-domain.com` → localhost:3001
   - Route `api.your-domain.com` → localhost:8000
   - Route `app.your-domain.com` → localhost:3000
   - Route `your-domain.com` → localhost:80

## Benefits

### Before (Old Scripts)
- Manual database setup required
- No admin portal included
- Inconsistent between dev/prod
- Manual service management

### After (Updated Scripts)
- ✅ Docker handles database automatically
- ✅ Admin portal included
- ✅ Consistent dev/prod flow
- ✅ One command starts everything
- ✅ Graceful shutdown
- ✅ Production optimized

## Next Steps

1. **Start Docker Desktop** (one time)
2. **Run startup script**: `./start-dev.sh`
3. **Create admin** (first time only): `python backend/create_super_admin.py`
4. **Access admin portal**: http://localhost:3001
5. **Start managing your platform!** 🚀

---

**Status**: ✅ Scripts Updated & Production Ready
**Date**: October 2025
**Admin Portal**: Fully Integrated

