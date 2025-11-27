# 🐳 SusuSave Docker - Complete Guide

**One command to run everything. Zero setup headaches.**

---

## 🚀 Quickest Start (2 Minutes)

```bash
cd /path/to/susu
./docker-start.sh up
```

**Wait 15 seconds, then open:**
- 📱 Web App: http://localhost:5173
- 🎛️ Admin: http://localhost:5174  
- 📖 API Docs: http://localhost:8000/docs

**Stop everything:**
```bash
./docker-start.sh down
```

**That's it!** 🎉

---

## 📋 What's Included

### 5 Services Running in Docker

| Service | Port | What It Does |
|---------|------|--------------|
| **PostgreSQL** | 5432 | Stores all data (users, groups, payments) |
| **Redis** | 6379 | Caches sessions, speeds up USSD |
| **Backend** | 8000 | FastAPI server with all business logic |
| **Web App** | 5173 | React PWA for users |
| **Admin Panel** | 5174 | React dashboard for admins |

**Bonus:** Nginx reverse proxy in production mode

---

## 🎯 Common Commands

### Daily Use
```bash
./docker-start.sh up        # Start everything
./docker-start.sh down      # Stop everything
./docker-start.sh restart   # Quick restart
./docker-start.sh logs      # See what's happening
./docker-start.sh ps        # Check status
```

### Development
```bash
./docker-start.sh logs backend    # Backend logs only
./docker-start.sh logs webapp     # Web app logs only
./docker-start.sh shell backend   # Open backend shell
./docker-start.sh db              # Open database CLI
./docker-start.sh test            # Run tests
```

### Database
```bash
./docker-start.sh db              # PostgreSQL shell
./docker-start.sh migrate         # Run migrations
./docker-start.sh seed            # Add test data
```

### Maintenance
```bash
./docker-start.sh rebuild         # Rebuild everything
./docker-start.sh clean           # Remove all data (⚠️ destructive)
```

### Production
```bash
./docker-start.sh up prod         # Start with nginx
```

---

## 📚 Documentation

### For Different Audiences

**Just want to run it?**  
👉 [DOCKER_QUICK_START.md](./DOCKER_QUICK_START.md) - 2 minute guide

**Need full documentation?**  
👉 [DOCKER_SETUP.md](./DOCKER_SETUP.md) - Complete 600+ line guide

**Want to know what changed?**  
👉 [DOCKER_UPDATE_SUMMARY.md](./DOCKER_UPDATE_SUMMARY.md) - All updates

---

## 🏗️ Architecture

### Development Mode (Default)

```
Your Computer
│
├─ PostgreSQL :5432   (Database)
├─ Redis :6379        (Cache)
├─ Backend :8000      (FastAPI API)
├─ Web App :5173      (React PWA)
└─ Admin :5174        (React Dashboard)
```

All services talk to each other inside a Docker network. Your browser talks to them via localhost.

### Production Mode

```
Internet → Nginx :80/443 (SSL, Rate Limit)
            │
            ├─ /api/*     → Backend (3 workers)
            ├─ /admin/*   → Admin Panel
            └─ /*         → Web App
```

---

## 🛠️ Setup Details

### What docker-start.sh Does

1. ✅ Checks Docker is installed and running
2. ✅ Creates `.env.docker` if needed
3. ✅ Builds all 5 Docker images
4. ✅ Starts all containers
5. ✅ Runs database migrations automatically
6. ✅ Waits for services to be healthy
7. ✅ Shows you the URLs to open

**You do nothing. Script does everything.**

### First Run vs Later Runs

**First run (slow):**
- Downloads base images (Python, Node, PostgreSQL, Redis, Nginx)
- Installs dependencies (pip packages, npm packages)
- Builds everything
- Takes 3-5 minutes

**Later runs (fast):**
- Uses cached images
- Starts containers only
- Takes 10-15 seconds

---

## 🔧 Configuration

### Environment Variables

Configuration is automatic! The script creates `backend/.env.docker` from `backend/env.example`.

**To customize:**
```bash
nano backend/.env.docker
./docker-start.sh restart backend
```

**Key settings for Docker:**
```env
# Use service names, not localhost
DATABASE_URL=postgresql://sususer:suspass@db:5432/sususave
REDIS_URL=redis://redis:6379/0

# Add your API keys
MTN_MOMO_SUBSCRIPTION_KEY=your-key
AT_API_KEY=your-key
```

### Ports

Default ports:
- Backend: 8000
- Web App: 5173
- Admin: 5174
- PostgreSQL: 5432
- Redis: 6379
- Nginx: 80, 443 (production only)

**Change ports** in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Map to different host port
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find and kill
lsof -ti:8000 | xargs kill -9
lsof -ti:5432 | xargs kill -9
```

### Docker Not Running

```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker
```

### Service Won't Start

```bash
# Check logs
./docker-start.sh logs backend

# Try clean restart
./docker-start.sh clean
./docker-start.sh up
```

### Database Issues

```bash
# Verify connection
./docker-start.sh db
\dt
\q

# Reset everything (⚠️ deletes data)
./docker-start.sh clean
./docker-start.sh up
```

### "Can't connect to database"

**Check .env.docker has correct URL:**
```bash
cat backend/.env.docker | grep DATABASE_URL
```

**Should show:**
```
DATABASE_URL=postgresql://sususer:suspass@db:5432/sususave
```

**NOT:**
```
DATABASE_URL=postgresql://...@localhost:5432/...  ❌ Wrong!
```

---

## 💡 How It Works

### Multi-Stage Builds

**Dockerfiles use 3 stages:**

1. **Base** - Install dependencies
2. **Development** - Hot reload, debugging tools
3. **Production** - Optimized, multi-worker, non-root

```dockerfile
FROM python:3.11-slim as base
# Install dependencies

FROM base as development
CMD ["uvicorn", "--reload"]  # Hot reload

FROM base as production
CMD ["uvicorn", "--workers", "4"]  # Optimized
```

### Docker Compose Profiles

```bash
# Development (default)
docker-compose up  # Backend, DB, Redis, Web, Admin

# Production
docker-compose --profile production up  # + Nginx
```

### Health Checks

All services have health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
  interval: 30s
  timeout: 10s
  retries: 3
```

Service won't be "ready" until health check passes.

---

## 🎓 Learn More

### Files You Should Know About

**Configuration:**
- `docker-compose.yml` - Development services
- `docker-compose.prod.yml` - Production services
- `backend/Dockerfile` - Backend image
- `web/app/Dockerfile` - Web app image
- `web/admin/Dockerfile` - Admin image

**Scripts:**
- `docker-start.sh` - Main control script
- `backend/alembic/` - Database migrations

**Documentation:**
- `DOCKER_QUICK_START.md` - Quick reference
- `DOCKER_SETUP.md` - Complete guide
- `DOCKER_UPDATE_SUMMARY.md` - What changed

### Docker Commands (If You Want)

You can use `docker-compose` directly:

```bash
docker-compose up -d              # Start detached
docker-compose down               # Stop
docker-compose logs -f backend    # Follow logs
docker-compose restart backend    # Restart service
docker-compose ps                 # List services
docker-compose exec backend sh    # Shell access
```

But `./docker-start.sh` is easier! 😊

---

## 🚢 Production Deployment

### Pre-Deployment Checklist

- [ ] Set up external database (AWS RDS, etc.)
- [ ] Set up external Redis (ElastiCache, etc.)
- [ ] Get SSL certificates (Let's Encrypt)
- [ ] Configure domain and DNS
- [ ] Update `.env.production` with real credentials
- [ ] Set strong `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Enable real SMS and MoMo
- [ ] Set up monitoring (optional but recommended)
- [ ] Configure backups
- [ ] Load test

### Deploy

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Push to registry
docker-compose -f docker-compose.prod.yml push

# On server
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

**See [DOCKER_SETUP.md](./DOCKER_SETUP.md) for complete production guide.**

---

## 📊 Status & Health

### Check Everything

```bash
./docker-start.sh ps
```

### Check Individual Services

```bash
# Backend
curl http://localhost:8000/docs

# Web App
curl http://localhost:5173

# Admin
curl http://localhost:5174

# Database
docker-compose exec db pg_isready -U sususer

# Redis
docker-compose exec redis redis-cli ping
```

### Monitor Resources

```bash
docker stats
```

---

## 🔐 Security Notes

### Development (Safe Defaults)

- Default passwords (sususer/suspass)
- Mock SMS and MoMo
- Sandbox API keys
- HTTP only (no SSL)

**✅ Fine for local development**

### Production (Must Change!)

- Strong database passwords
- Real API keys in environment variables
- SSL/TLS enabled
- Rate limiting enabled
- Non-root users in containers
- Security headers configured

**See [DOCKER_SETUP.md](./DOCKER_SETUP.md) Security section.**

---

## 🆘 Get Help

**Something not working?**

1. Check logs: `./docker-start.sh logs`
2. Check service status: `./docker-start.sh ps`
3. Try troubleshooting section above
4. Read [DOCKER_SETUP.md](./DOCKER_SETUP.md) - Troubleshooting (15+ scenarios)
5. Clean restart: `./docker-start.sh clean && ./docker-start.sh up`

**Still stuck?**
- Check Docker Desktop is running and has enough resources (4GB RAM+)
- Verify Docker version: `docker --version` (need 20.10+)
- Check ports aren't in use: `lsof -ti:8000`

---

## 📈 Performance Tips

### Development

- **Give Docker more resources** (8GB RAM recommended)
- **Use SSD** for Docker volumes
- **Close unused containers**: `docker-compose down`
- **Prune regularly**: `docker system prune`

### Production

- **Scale backend**: `docker-compose up --scale backend=3`
- **Use external DB and Redis** (managed services)
- **Enable nginx caching**
- **Monitor with Prometheus/Grafana**
- **Set resource limits** (already configured in prod compose)

---

## 🎯 Quick Reference Card

```bash
# ESSENTIAL COMMANDS
./docker-start.sh up        # Start everything
./docker-start.sh down      # Stop everything
./docker-start.sh logs      # View logs
./docker-start.sh ps        # Check status

# DEVELOPMENT
./docker-start.sh shell     # Backend shell
./docker-start.sh db        # Database shell
./docker-start.sh test      # Run tests

# MAINTENANCE
./docker-start.sh restart   # Restart
./docker-start.sh rebuild   # Rebuild
./docker-start.sh clean     # Remove all (⚠️)

# PRODUCTION
./docker-start.sh up prod   # Production mode
```

**URLs:**
- Web: http://localhost:5173
- Admin: http://localhost:5174
- API: http://localhost:8000/docs

---

## 🎉 Success!

If you see all services running:

```bash
$ ./docker-start.sh ps

NAME                 STATUS              PORTS
sususave_backend     Up (healthy)        0.0.0.0:8000->8000/tcp
sususave_webapp      Up                  0.0.0.0:5173->5173/tcp
sususave_admin       Up                  0.0.0.0:5174->5173/tcp
sususave_db          Up (healthy)        0.0.0.0:5432->5432/tcp
sususave_redis       Up (healthy)        0.0.0.0:6379->6379/tcp
```

**🎊 You're all set! Start building!**

---

## 📖 Documentation Index

| Document | Purpose | Audience |
|----------|---------|----------|
| **README_DOCKER.md** | Overview and quick reference | Everyone |
| **DOCKER_QUICK_START.md** | 2-minute getting started | New users |
| **DOCKER_SETUP.md** | Complete 600+ line guide | Developers, DevOps |
| **DOCKER_UPDATE_SUMMARY.md** | What changed in this update | Existing users |

---

**Last Updated:** October 22, 2025  
**Maintained By:** SusuSave Team  
**License:** MIT

**Questions?** Read [DOCKER_SETUP.md](./DOCKER_SETUP.md) for answers to everything!

