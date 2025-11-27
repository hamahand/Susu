# 🚀 Docker Quick Start - SusuSave

Get the entire SusuSave platform running in 2 minutes with Docker!

## Prerequisites

✅ Docker Desktop installed and running ([Download here](https://www.docker.com/products/docker-desktop))

## Quick Start

### 1. Start Everything

```bash
cd /path/to/susu
chmod +x docker-start.sh
./docker-start.sh up
```

### 2. Wait ~15 seconds for services to start

### 3. Open in Browser

- **Web App**: http://localhost:5173
- **Admin Panel**: http://localhost:5174
- **API Docs**: http://localhost:8000/docs

### 4. Stop When Done

```bash
./docker-start.sh down
```

## What Gets Started?

| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |
| Backend API | 8000 | FastAPI server |
| Web App | 5173 | User PWA |
| Admin Panel | 5174 | Admin dashboard |

## Common Commands

```bash
# View logs
./docker-start.sh logs

# View backend logs only
./docker-start.sh logs backend

# Check status
./docker-start.sh ps

# Restart everything
./docker-start.sh restart

# Clean rebuild
./docker-start.sh rebuild

# Database shell
./docker-start.sh db

# Backend shell
./docker-start.sh shell

# Run tests
./docker-start.sh test
```

## Troubleshooting

### "Port already in use"
```bash
# Kill conflicting process
kill -9 $(lsof -ti:8000)
kill -9 $(lsof -ti:5432)
```

### "Docker daemon not running"
```bash
# Start Docker Desktop
open -a Docker
```

### Services not starting
```bash
# Clean restart
./docker-start.sh clean
./docker-start.sh up
```

### See all logs
```bash
docker-compose logs -f
```

## Environment Configuration

Configuration is automatic! The script creates `.env.docker` from `env.example`.

To customize:
```bash
nano backend/.env.docker
./docker-start.sh restart backend
```

## Production Mode

```bash
# Start with Nginx reverse proxy
./docker-start.sh up prod
```

## Full Documentation

See [DOCKER_SETUP.md](./DOCKER_SETUP.md) for complete documentation including:
- Architecture details
- Production deployment
- Database backups
- Monitoring
- Advanced troubleshooting

## Need Help?

1. Check logs: `./docker-start.sh logs`
2. Check status: `./docker-start.sh ps`
3. Clean restart: `./docker-start.sh clean && ./docker-start.sh up`
4. Read [DOCKER_SETUP.md](./DOCKER_SETUP.md)

---

**Quick Reference:**
```bash
./docker-start.sh up       # Start
./docker-start.sh down     # Stop
./docker-start.sh restart  # Restart
./docker-start.sh logs     # View logs
./docker-start.sh ps       # Status
```

