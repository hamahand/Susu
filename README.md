# SusuSave - Hybrid ROSCA Platform

A comprehensive Rotating Savings and Credit Association (ROSCA) platform supporting both mobile app users (group creators/admins) and USSD users (participants) with automated Mobile Money (MoMo) integration.

## 🏗️ Architecture

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
                              │  Database  │                  │   (MTN)     │
                              └────────────┘                  └─────────────┘
```

## 📦 Project Structure

```
susu/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── integrations/  # MoMo & SMS integrations
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   └── requirements.txt
├── web/                     # Web Applications
│   ├── app/                # PWA Web App (React + Vite)
│   └── admin/              # Admin CRM Portal (React + Vite)
├── mobile/                  # Mobile App
│   └── SusuSaveMobile/     # React Native (Expo)
├── docker-compose.yml       # Docker services
└── .github/workflows/      # CI/CD workflows
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Node.js 20.19.4+ (for mobile app)
- Docker & Docker Compose (recommended)

### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Check services
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
# Edit .env with your settings (see Configuration section)

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
# PWA Web App
cd web/app
npm install
npm run dev  # Runs on http://localhost:5173

# Admin Portal
cd web/admin
npm install
npm run dev  # Runs on http://localhost:5174
```

#### Mobile App Setup

```bash
cd mobile/SusuSaveMobile
npm install
npm start  # Expo dev server
```

## ⚙️ Configuration

### Required Environment Variables

Copy `backend/env.example` to `backend/.env` and configure:

**Security (REQUIRED):**
```bash
# Generate with: openssl rand -hex 32
SECRET_KEY=your-generated-secret-key

# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-generated-encryption-key

# Database connection
DATABASE_URL=postgresql://user:password@localhost:5432/sususave
```

**MTN API (if using MTN services):**
```bash
MTN_CONSUMER_KEY=your-consumer-key
MTN_CONSUMER_SECRET=your-consumer-secret
MTN_MOMO_API_KEY=your-momo-api-key
MTN_CALLBACK_URL=https://your-domain.com/ussd/callback
```

**Africa's Talking (if using AT services):**
```bash
AT_USERNAME=your-username
AT_API_KEY=your-api-key
```

> **⚠️ Security Note:** The application will fail to start if required secrets are missing or using default values. This prevents accidental deployment with insecure defaults.

## 📚 API Documentation

Once the backend is running:

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

## 🔒 Security

### Security Features

- ✅ JWT authentication with configurable expiration
- ✅ Encrypted sensitive data (phone numbers, etc.)
- ✅ Environment-based configuration (no hardcoded secrets)
- ✅ Startup validation for required secrets
- ✅ Automated security audits via GitHub Actions
- ✅ Dependency vulnerability scanning

### Security Audits

The repository includes automated security scanning:

- **Backend**: `pip-audit` scans Python dependencies
- **Frontend**: `npm audit` scans Node.js dependencies
- **Secrets**: `gitleaks` scans for committed secrets

Run audits manually:
```bash
# Backend
cd backend
pip install pip-audit
pip-audit -r requirements.txt

# Frontend
cd web/app  # or web/admin
npm audit

# Mobile
cd mobile/SusuSaveMobile
npm audit
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app tests/
```

## 🐳 Docker Services

The `docker-compose.yml` includes:

- **PostgreSQL** (port 5432) - Database
- **Redis** (port 6379) - Session storage (optional)
- **Backend** (port 8000) - FastAPI application
- **Web App** (port 5173) - PWA frontend
- **Admin Portal** (port 5174) - Admin CRM

## 📱 Mobile App

The React Native mobile app uses Expo:

```bash
cd mobile/SusuSaveMobile
npm start
```

Then:
- Press `i` for iOS simulator
- Press `a` for Android emulator
- Scan QR code with Expo Go app

## 🔄 Background Jobs

The scheduler runs automated jobs:

1. **Daily Payment Check** (6:00 AM) - Initiates MoMo debits
2. **Payment Retry** (Every 6 hours) - Retries failed payments
3. **Payout Processing** (Every 2 hours) - Processes completed rounds

## 🚢 Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Configure real MoMo API credentials
- [ ] Set up Africa's Talking account (if using)
- [ ] Configure SMS gateway
- [ ] Enable SSL/TLS (use reverse proxy)
- [ ] Set up database backups
- [ ] Configure monitoring
- [ ] Review CORS settings
- [ ] Set `ENABLE_REAL_SMS=True` and `ENABLE_REAL_MOMO=True`

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Troubleshooting

### Backend won't start

- Check that all required environment variables are set
- Verify database is running: `docker-compose ps db`
- Check logs: `docker-compose logs backend`

### Database connection errors

```bash
# Check PostgreSQL is running
docker-compose ps db

# View database logs
docker-compose logs db
```

### Port conflicts

```bash
# Check what's using a port
lsof -ti:8000  # Backend
lsof -ti:3000  # Frontend
lsof -ti:5432  # PostgreSQL
```

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/hamahand/Susu/issues)
- Documentation: See `/docs` folder

---

**Built with ❤️ for financial inclusion in Ghana and beyond**

