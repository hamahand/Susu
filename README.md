# SusuSave - Hybrid ROSCA Platform

## Overview

SusuSave is a comprehensive Rotating Savings and Credit Association (ROSCA) platform that supports both **mobile app users** (group creators/admins) and **USSD users** (participants) with automated Mobile Money (MoMo) integration.

### Key Features

- 🏦 **Automated Contributions**: Scheduled MoMo debits for all group members
- 💰 **Smart Payouts**: Automatic distribution when all members have paid
- 📱 **Mobile App**: Full-featured React Native app for group management
- ☎️ **USSD Access**: AfricaTalking USSD integration for feature phone users
- 📲 **SMS Notifications**: Real-time SMS via AfricaTalking API
- 🔄 **Retry Logic**: Automatic payment retry for failed transactions
- 🔒 **Secure**: Encrypted sensitive data, JWT authentication, audit logging
- 🌍 **Ghana-Ready**: MTN Mobile Money integration (mock for development)

## Architecture

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│  Mobile App │       │ USSD Gateway │       │   Backend   │
│ (React      │──────▶│  (Africa's   │──────▶│  (FastAPI)  │
│  Native)    │       │   Talking)   │       │             │
└─────────────┘       └──────────────┘       └─────────────┘
                                                     │
                                    ┌────────────────┴────────────────┐
                                    │                                 │
                              ┌─────▼──────┐                  ┌──────▼──────┐
                              │ PostgreSQL │                  │  MoMo API   │
                              │  Database  │                  │   (Mock)    │
                              └────────────┘                  └─────────────┘
```

## Project Structure

```
susu/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Helper functions
│   │   ├── cron/           # Background jobs
│   │   ├── integrations/   # MoMo & SMS mocks
│   │   ├── config.py       # Settings
│   │   ├── database.py     # DB connection
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── test_ussd.py        # USSD testing tool
├── mobile/                  # React Native App (TBD)
├── docker-compose.yml       # Docker services
├── docs/                    # Documentation
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (recommended)
- Node.js 18+ (for mobile app)

### Option 1: Docker (Recommended)

```bash
# Clone and navigate
cd susu

# Start all services
docker-compose up -d

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f backend
```

The API will be available at **http://localhost:8000**

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

#### Database Setup (if not using Docker)

```bash
# Install PostgreSQL and create database
createdb sususave
createuser sususer
psql -c "ALTER USER sususer WITH PASSWORD 'suspass';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE sususave TO sususer;"
```

## API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Get JWT token
- `GET /auth/me` - Get current user

#### Groups
- `POST /groups` - Create group (returns group_code)
- `GET /groups/my-groups` - List user's groups
- `POST /groups/join` - Join group via code
- `GET /groups/{id}/dashboard` - Real-time dashboard

#### Payments
- `POST /payments/manual-trigger` - Trigger payment
- `GET /payments/history` - Payment history
- `POST /payments/{id}/retry` - Retry failed payment

#### Payouts
- `POST /payouts/{id}/approve` - Approve payout (admin)
- `GET /payouts/{group_id}/current` - Current payout

#### USSD
- `POST /ussd/callback` - Africa's Talking webhook

## USSD Flow (AfricaTalking Integration)

```
Dial: *384*12345#  (sandbox) or your assigned code

Main Menu:
1. Join Group        → Enter group code → Confirmation + SMS
2. Pay Contribution  → Select group → Payment processed + SMS
3. Check Status      → View all groups and positions
4. My Payout Date    → See when you'll receive funds
```

### Testing USSD

```bash
cd backend

# Interactive testing
python test_africastalking_ussd.py

# Automated tests
python test_africastalking_ussd.py test

# curl testing
./test_ussd_curl.sh
```

**See [AfricaTalking Quick Reference](AFRICASTALKING_QUICKREF.md) for complete setup guide.**

## Database Schema

### Core Tables

- **users**: User accounts (app + USSD)
- **groups**: ROSCA groups with rotation settings
- **memberships**: User-group links with rotation position
- **payments**: Contribution records with retry tracking
- **payouts**: Distribution records
- **audit_logs**: Immutable financial audit trail

See `/backend/app/models/` for detailed schemas.

## Background Jobs (Scheduler)

The system runs three automated jobs:

1. **Daily Payment Check** (6:00 AM)
   - Initiates MoMo debits for all active group members
   - Creates payment records

2. **Payment Retry** (Every 6 hours)
   - Retries failed payments (max 3 attempts)
   - Sends SMS notifications

3. **Payout Processing** (Every 2 hours)
   - Checks if rounds are complete
   - Credits recipient's MoMo wallet
   - Advances to next round

## Configuration

Key environment variables (see `backend/env.example`):

```bash
# Database
DATABASE_URL=postgresql://sususer:suspass@localhost:5432/sususave

# Security
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-fernet-key

# Features
ENABLE_SCHEDULER=True
ENABLE_REAL_SMS=False
ENABLE_REAL_MOMO=False

# Africa's Talking
AT_USERNAME=your-username
AT_API_KEY=your-api-key
```

### Generating Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY (Python)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Mock Integrations

### MTN Mobile Money Mock

Located at `/backend/app/integrations/momo_mock.py`

- Simulates wallet debits/credits
- 10% random failure rate for testing
- Stores transactions in `momo_transactions.json`
- Auto-initializes wallets with GHS 100-1000

### SMS Gateway Mock

Located at `/backend/app/integrations/sms_mock.py`

- Logs all SMS to `sms_logs.txt` and console
- Templates for payment confirmations, failures, payouts

## Mobile App Development

Coming soon. The React Native app will include:

- Group creation wizard
- Real-time dashboard
- Member management
- Payout approvals
- Transaction history

## Testing

```bash
cd backend

# Run tests
pytest

# Test coverage
pytest --cov=app tests/
```

## Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Configure real MoMo API credentials
- [ ] Set up Africa's Talking account
- [ ] Configure SMS gateway
- [ ] Enable SSL/TLS (use reverse proxy)
- [ ] Set up database backups
- [ ] Configure monitoring (e.g., Sentry)
- [ ] Review CORS settings
- [ ] Set `ENABLE_REAL_SMS=True` and `ENABLE_REAL_MOMO=True`

### Example Production Deployment

```bash
# Build and push Docker image
docker build -t sususave:latest ./backend
docker push your-registry/sususave:latest

# Deploy with environment-specific configs
docker run -d \
  --name sususave \
  -p 8000:8000 \
  --env-file .env.production \
  your-registry/sususave:latest
```

## Troubleshooting

### Common Issues

**Database connection errors**
```bash
# Check PostgreSQL is running
docker-compose ps
# View logs
docker-compose logs db
```

**Scheduler not running**
- Check `ENABLE_SCHEDULER=True` in `.env`
- View logs: `docker-compose logs backend`

**USSD test errors**
- Ensure backend is running on port 8000
- Check `/ussd/callback` endpoint exists

## Documentation

### General
- [Quick Start Guide](QUICK_START.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Project Status](PROJECT_STATUS.md)

### AfricaTalking USSD & SMS
- [Quick Reference](AFRICASTALKING_QUICKREF.md) ⚡ **Start here!**
- [Full Setup Guide](backend/docs/AFRICASTALKING_SETUP.md)
- [Quick Start](backend/docs/USSD_QUICKSTART.md)
- [Integration Checklist](backend/AFRICASTALKING_CHECKLIST.md)
- [AfricaTalking README](backend/README_AFRICASTALKING.md)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Troubleshooting

### Startup Script Errors

If you see "invalid integer" errors when running `start-prod.sh` or `start-dev.sh`:

**Problem**: ANSI color codes being captured in port variables  
**Solution**: This has been fixed. If you have an old version, update the `ask_port()` function to redirect output to stderr using `>&2`.

### PostgreSQL Issues

**Homebrew PostgreSQL shared memory errors**:
```bash
# Error: "could not create shared memory segment: Cannot allocate memory"

# Solution 1: Clear shared memory segments
brew services stop postgresql@15
ipcs -m | grep $(whoami) | awk '{print $2}' | xargs -n1 ipcrm -m
brew services start postgresql@15

# Solution 2: Use Docker instead (recommended)
./docker-start.sh up
```

**Missing postgresql.conf**:
```bash
# Reinstall PostgreSQL
brew uninstall postgresql@15
brew install postgresql@15
brew services start postgresql@15
```

### Login Issues

**Backend not responding**:
```bash
# Check if backend is running
curl http://localhost:8000/docs

# Check Docker containers
docker ps | grep sususave

# Check local process
lsof -ti:8000
```

**Database migration errors**:
```bash
# For Docker - clean slate
docker-compose down -v
docker-compose up --build

# For local - reset migrations
cd backend
rm -rf alembic/versions/*
alembic revision --autogenerate -m "initial_schema"
alembic upgrade head
```

### Port Conflicts

```bash
# Check what's using a port
lsof -ti:8000  # Backend
lsof -ti:3000  # Frontend
lsof -ti:5432  # PostgreSQL

# Kill the process
kill -9 $(lsof -ti:8000)
```

### Environment Variables

**Missing .env file**:
```bash
# For local development
cd backend
cp env.example .env
# Edit .env and add your API keys

# For Docker
cp env.example .env.docker
# Edit .env.docker (uses 'db' instead of 'localhost')
```

**Generate keys**:
```bash
# SECRET_KEY
openssl rand -hex 32

# ENCRYPTION_KEY (needs Python cryptography)
cd backend && source venv/bin/activate
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Docker Setup

For detailed Docker setup and usage, see **[DOCKER_SETUP.md](DOCKER_SETUP.md)**.

Quick commands:
```bash
# Easy start with helper script
./docker-start.sh up

# Manual start
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop everything
docker-compose down

# Clean restart (removes all data!)
docker-compose down -v && docker-compose up --build
```

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Link to repo]
- Email: support@sususave.com
- 📖 Documentation: See `/docs` folder and **[DOCKER_SETUP.md](DOCKER_SETUP.md)**

---

**Built with ❤️ for financial inclusion in Ghana and beyond**

