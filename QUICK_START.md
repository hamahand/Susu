# SusuSave Quick Start Guide

Get up and running with SusuSave in 5 minutes!

---

## 🚀 Quick Start (Docker)

### 1. Start Services

```bash
# Clone repository
git clone <repository-url>
cd susu

# Start all services with Docker Compose
docker-compose up -d

# Wait for services to be healthy (takes ~30 seconds)
docker-compose ps
```

### 2. Seed Test Data

```bash
# Run seed script to create test users and groups
docker-compose exec backend python seed_data.py
```

### 3. Test the API

Visit **http://localhost:8000/docs** for interactive API documentation.

---

## 📱 Test Workflows

### Workflow 1: Mobile App User (Group Admin)

#### Step 1: Register & Login

```bash
# Register new user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+233244123456",
    "name": "John Doe",
    "password": "password123",
    "user_type": "app"
  }'

# Login to get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+233244123456",
    "password": "password123"
  }'

# Copy the "access_token" from response
```

#### Step 2: Create a Group

```bash
curl -X POST http://localhost:8000/groups \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Family Savings",
    "contribution_amount": 50.0,
    "num_cycles": 12
  }'

# Note the "group_code" from response (e.g., SUSU1A2B)
```

#### Step 3: View Dashboard

```bash
curl -X GET http://localhost:8000/groups/1/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### Workflow 2: USSD User (Group Member)

#### Start USSD Simulator

```bash
docker-compose exec backend python test_ussd.py
```

#### Test Flow:

```
1. Enter phone number: +233244987654
2. See main menu
3. Select option 1 (Join Group)
4. Enter group code: SUSU1A2B
5. See confirmation message
```

---

## 🔧 Using Test Data

After running `seed_data.py`, you have:

### Test Users

**App Users (Login via API):**
- Phone: `+233244111111`, Password: `password123`
- Phone: `+233244222222`, Password: `password123`

**USSD Users (Use with USSD simulator):**
- `+233244333333`
- `+233244444444`
- `+233244555555`

### Test Groups

- Code: `SUSU1234` - Monthly Rent Fund (GHS 50)
- Code: `SUSU5678` - Business Startup Fund (GHS 100)

---

## 🧪 Common Testing Scenarios

### Scenario 1: Make a Payment

```bash
# Login as admin
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+233244111111","password":"password123"}' \
  | jq -r '.access_token')

# Trigger payment
curl -X POST http://localhost:8000/payments/manual-trigger \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"group_id": 1}'
```

### Scenario 2: View Payment History

```bash
curl -X GET http://localhost:8000/payments/history \
  -H "Authorization: Bearer $TOKEN"
```

### Scenario 3: Check Group Status (USSD)

```bash
# Run USSD simulator
python backend/test_ussd.py

# Flow: Dial > Option 3 (Check Status)
```

---

## 📊 Monitor System

### View Logs

```bash
# Backend logs
docker-compose logs -f backend

# Database logs
docker-compose logs -f db

# All logs
docker-compose logs -f
```

### Check SMS & MoMo Logs

```bash
# SMS logs (in real-time)
docker-compose exec backend tail -f sms_logs.txt

# MoMo transactions
docker-compose exec backend cat momo_transactions.json
```

### Health Check

```bash
curl http://localhost:8000/health
```

---

## 🎯 Testing Scheduler Jobs

The scheduler runs these jobs automatically:

1. **Daily Payment Check** - 6:00 AM
2. **Payment Retry** - Every 6 hours
3. **Payout Processing** - Every 2 hours

### Manually Trigger Jobs (for testing)

```bash
# Access Python shell
docker-compose exec backend python

# In Python:
from app.database import SessionLocal
from app.cron.scheduler import SusuScheduler

db = SessionLocal()

# Run daily payment check
SusuScheduler.daily_payment_check()

# Run payout processing
SusuScheduler.process_pending_payouts()

exit()
```

---

## 🛠 Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker --version

# Restart services
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs backend
```

### Database Connection Error

```bash
# Check database is running
docker-compose ps db

# Restart database
docker-compose restart db

# Check connection
docker-compose exec db psql -U sususer -d sususave
```

### Can't Login

```bash
# Verify user was created
docker-compose exec db psql -U sususer -d sususave -c "SELECT * FROM users;"

# Re-run seed script
docker-compose exec backend python seed_data.py
```

---

## 📚 Next Steps

1. **Explore API**: Visit http://localhost:8000/docs
2. **Read Full Documentation**: See [README.md](README.md)
3. **Review API Reference**: See [docs/API.md](docs/API.md)
4. **Learn Deployment**: See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
5. **Build Mobile App**: See mobile app setup (coming soon)

---

## 🎉 Success Indicators

You should see:

✅ Docker containers running (3: backend, db, redis)
✅ API docs accessible at http://localhost:8000/docs
✅ Health check returns `{"status": "healthy"}`
✅ Test users can login and get JWT tokens
✅ Groups can be created and joined
✅ Payments can be triggered
✅ USSD simulator works
✅ SMS logs show messages sent
✅ MoMo transactions recorded

---

## 🆘 Get Help

- **Documentation**: Full docs in `/docs` folder
- **API Reference**: http://localhost:8000/docs
- **Issues**: Check logs with `docker-compose logs`
- **Reset Everything**: `docker-compose down -v && docker-compose up -d`

---

Happy testing! 🚀

