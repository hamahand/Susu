# SusuSave Deployment Guide

## Production Deployment

This guide covers deploying SusuSave to a production environment.

---

## Pre-Deployment Checklist

### 1. Infrastructure Requirements

- **Server**: Linux VPS (Ubuntu 22.04 LTS recommended)
- **RAM**: Minimum 2GB, recommended 4GB+
- **CPU**: 2+ cores
- **Storage**: 20GB+ SSD
- **Database**: PostgreSQL 15+ (managed service recommended)
- **Domain**: SSL certificate (Let's Encrypt)

### 2. External Services

- [ ] PostgreSQL database (AWS RDS, DigitalOcean, or self-hosted)
- [ ] Africa's Talking account (USSD & SMS)
- [ ] MTN Mobile Money API credentials
- [ ] Redis instance (optional, for USSD sessions)
- [ ] Monitoring service (Sentry, CloudWatch, etc.)

### 3. Security Configuration

- [ ] Generate strong `SECRET_KEY`
- [ ] Generate `ENCRYPTION_KEY` for data encryption
- [ ] Set up firewall rules
- [ ] Configure SSL/TLS certificates
- [ ] Set up database backups
- [ ] Configure log rotation

---

## Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/your-org/sususave.git
cd sususave
```

#### Step 3: Configure Environment

```bash
# Copy environment template
cp backend/env.example backend/.env

# Edit with production values
nano backend/.env
```

**Production `.env` example:**
```bash
# Database (use managed PostgreSQL)
DATABASE_URL=postgresql://sususer:STRONG_PASSWORD@db.example.com:5432/sususave

# Security (CRITICAL!)
SECRET_KEY=your-generated-secret-key-use-openssl-rand-hex-32
ENCRYPTION_KEY=your-fernet-key-generate-with-python-cryptography

# Mobile Money (PRODUCTION)
ENABLE_REAL_MOMO=True
MTN_MOMO_SUBSCRIPTION_KEY=your-mtn-api-key
MTN_MOMO_USER_ID=your-user-id
MTN_MOMO_API_KEY=your-api-key
MTN_MOMO_BASE_URL=https://proxy.momoapi.mtn.com

# SMS (PRODUCTION)
ENABLE_REAL_SMS=True
AT_USERNAME=your-africas-talking-username
AT_API_KEY=your-africas-talking-api-key

# Scheduler
ENABLE_SCHEDULER=True
PAYMENT_CHECK_HOUR=6
RETRY_INTERVAL_HOURS=6
PAYOUT_CHECK_INTERVAL_HOURS=2

# Redis (recommended for production)
REDIS_URL=redis://your-redis-host:6379/0
USE_REDIS=True

# CORS (your mobile app domains)
CORS_ORIGINS=["https://app.sususave.com","https://admin.sususave.com"]
```

#### Step 4: Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    image: sususave/backend:latest
    container_name: sususave_backend_prod
    restart: unless-stopped
    command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - sususave_network

  redis:
    image: redis:7-alpine
    container_name: sususave_redis_prod
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - sususave_network

  nginx:
    image: nginx:alpine
    container_name: sususave_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - certbot_data:/var/www/certbot
    depends_on:
      - backend
    networks:
      - sususave_network

  certbot:
    image: certbot/certbot
    container_name: sususave_certbot
    volumes:
      - ./nginx/ssl:/etc/letsencrypt
      - certbot_data:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

volumes:
  redis_data:
  certbot_data:

networks:
  sususave_network:
    driver: bridge
```

#### Step 5: Configure Nginx

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name api.sususave.com;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$host$request_uri;
        }
    }

    server {
        listen 443 ssl;
        server_name api.sususave.com;

        ssl_certificate /etc/nginx/ssl/live/api.sususave.com/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/live/api.sususave.com/privkey.pem;

        client_max_body_size 10M;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### Step 6: Get SSL Certificate

```bash
# Create directories
mkdir -p nginx/ssl

# Get certificate (first time)
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot \
  --webroot-path /var/www/certbot \
  -d api.sususave.com \
  --email admin@sususave.com \
  --agree-tos \
  --no-eff-email
```

#### Step 7: Deploy

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

### Option 2: Traditional VPS Deployment

#### Step 1: Install Dependencies

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql-client nginx

# Install Supervisor for process management
sudo apt install -y supervisor
```

#### Step 2: Set Up Application

```bash
# Create app directory
sudo mkdir -p /var/www/sususave
cd /var/www/sususave

# Clone repository
sudo git clone https://github.com/your-org/sususave.git .

# Set up Python environment
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp env.example .env
nano .env  # Edit with production values

# Run migrations
alembic upgrade head
```

#### Step 3: Configure Supervisor

Create `/etc/supervisor/conf.d/sususave.conf`:

```ini
[program:sususave]
command=/var/www/sususave/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
directory=/var/www/sususave/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/sususave/backend.log
environment=PATH="/var/www/sususave/backend/venv/bin"
```

```bash
# Create log directory
sudo mkdir -p /var/log/sususave
sudo chown www-data:www-data /var/log/sususave

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start sususave

# Check status
sudo supervisorctl status sususave
```

#### Step 4: Configure Nginx

Create `/etc/nginx/sites-available/sususave`:

```nginx
server {
    listen 80;
    server_name api.sususave.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/sususave /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.sususave.com
```

---

## Africa's Talking Configuration

### 1. USSD Setup

1. Log in to [Africa's Talking](https://account.africastalking.com/)
2. Go to **USSD** → **Create Channel**
3. Set **Service Code**: `*920*55#` (or your assigned code)
4. Set **Callback URL**: `https://api.sususave.com/ussd/callback`
5. Test in Sandbox mode first

### 2. SMS Setup

1. Go to **SMS** → **Settings**
2. Configure **Sender ID** (if applicable)
3. Add API key to `.env`:
   ```bash
   AT_USERNAME=your-username
   AT_API_KEY=your-api-key
   ```

---

## MTN Mobile Money Integration

### 1. Get API Access

1. Register at [MTN MoMo Developer Portal](https://momodeveloper.mtn.com/)
2. Create **Sandbox** and **Production** apps
3. Subscribe to **Collections** and **Disbursements** products
4. Get API credentials

### 2. Update Integration Code

Replace mock in `/backend/app/integrations/momo_real.py`:

```python
import requests
from app.config import settings

class MTNMoMoAPI:
    def __init__(self):
        self.base_url = settings.MTN_MOMO_BASE_URL
        self.subscription_key = settings.MTN_MOMO_SUBSCRIPTION_KEY
        self.user_id = settings.MTN_MOMO_USER_ID
        self.api_key = settings.MTN_MOMO_API_KEY
    
    def debit_wallet(self, phone_number, amount, reference):
        # Implement Collections API
        pass
    
    def credit_wallet(self, phone_number, amount, reference):
        # Implement Disbursements API
        pass
```

---

## Monitoring & Logging

### 1. Set Up Sentry

```bash
pip install sentry-sdk[fastapi]
```

Update `app/main.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### 2. Log Rotation

Create `/etc/logrotate.d/sususave`:

```
/var/log/sususave/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        supervisorctl restart sususave
    endscript
}
```

---

## Database Backups

### Automated PostgreSQL Backup

Create `/usr/local/bin/backup_sususave.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/sususave"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="sususave_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

pg_dump -h your-db-host -U sususer -d sususave | gzip > $BACKUP_DIR/$FILENAME

# Keep only last 30 days
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $FILENAME"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup_sususave.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup_sususave.sh
```

---

## Scaling Considerations

### Horizontal Scaling

Use load balancer (nginx, HAProxy) with multiple backend instances:

```yaml
services:
  backend_1:
    image: sususave/backend:latest
    # ... config
  
  backend_2:
    image: sususave/backend:latest
    # ... config
  
  load_balancer:
    image: nginx:alpine
    # Configure upstream servers
```

### Database Optimization

- Use connection pooling (SQLAlchemy default)
- Create indexes on frequently queried fields
- Use read replicas for analytics

---

## Troubleshooting

### Check Service Status

```bash
# Docker
docker-compose ps
docker-compose logs backend

# Supervisor
sudo supervisorctl status
sudo tail -f /var/log/sususave/backend.log
```

### Common Issues

**Database connection refused**
```bash
# Check PostgreSQL is accessible
psql -h your-db-host -U sususer -d sususave

# Check DATABASE_URL in .env
```

**Scheduler not running**
```bash
# Check logs for scheduler messages
docker-compose logs backend | grep "Scheduler"

# Verify ENABLE_SCHEDULER=True
```

---

## Security Best Practices

1. **Never commit** `.env` files
2. **Rotate secrets** regularly
3. **Use managed databases** with automatic backups
4. **Enable firewall** (UFW on Ubuntu)
5. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`
6. **Monitor logs** for suspicious activity
7. **Use HTTPS only** in production
8. **Implement rate limiting** on all endpoints

---

## Support

For deployment issues:
- Documentation: [docs.sususave.com](https://docs.sususave.com)
- Email: devops@sususave.com
- Slack: #deployment channel

