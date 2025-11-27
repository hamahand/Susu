# USSD Setup Instructions

**Complete step-by-step guide to configure USSD for MTN and AfricasTalking**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (5 Minutes)](#quick-start-5-minutes)
3. [MTN USSD Setup](#mtn-ussd-setup)
4. [AfricasTalking USSD Setup](#africastalking-ussd-setup)
5. [Environment Configuration](#environment-configuration)
6. [Callback URL Setup](#callback-url-setup)
7. [Testing Your Setup](#testing-your-setup)
8. [Troubleshooting](#troubleshooting)
9. [Production Deployment](#production-deployment)

---

## Prerequisites

### Required
- ✅ Python 3.8+ installed
- ✅ PostgreSQL database running
- ✅ Backend code downloaded
- ✅ Internet connection

### Optional
- 📱 Mobile phone for testing (Ghana number for MTN)
- 🌐 ngrok installed for local callback testing
- 💳 Payment method for AfricasTalking credits

---

## Quick Start (5 Minutes)

### Step 1: Create Environment File

```bash
cd backend
cp env.example .env
```

### Step 2: Generate Security Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Step 3: Edit `.env` File

Open `backend/.env` and update:

```env
# Security (REQUIRED)
SECRET_KEY=<paste-the-openssl-output-here>
ENCRYPTION_KEY=<paste-the-fernet-output-here>

# Choose your provider
USE_MTN_SERVICES=True  # True for MTN, False for AfricasTalking
```

### Step 4: Verify Setup

```bash
cd backend
python verify_ussd_setup.py
```

### Step 5: Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

That's it for basic setup! Continue reading for provider-specific configuration.

---

## MTN USSD Setup

### Overview

MTN provides USSD services through their Developer Portal. The application already has sandbox credentials configured.

### Option A: Use Existing Sandbox Credentials (Fastest)

The code already has MTN sandbox credentials:
- **Consumer Key**: `J7SH4tF6QqAsa6VYFhtGRwgpvPjYnF9y`
- **Consumer Secret**: `1gBhKETCBKLMyILR`
- **Service Code**: `*920*55#`

**Steps**:

1. **Verify in `.env`**:
   ```env
   USE_MTN_SERVICES=True
   MTN_CONSUMER_KEY=J7SH4tF6QqAsa6VYFhtGRwgpvPjYnF9y
   MTN_CONSUMER_SECRET=1gBhKETCBKLMyILR
   MTN_ENVIRONMENT=sandbox
   MTN_USSD_SERVICE_CODE=*920*55#
   ENABLE_MTN_USSD=True
   ```

2. **Start backend**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

3. **Test locally**:
   ```bash
   curl -X POST http://localhost:8000/ussd/callback \
     -d "sessionId=test123" \
     -d "phoneNumber=+233240000000" \
     -d "serviceCode=*920*55#" \
     -d "text="
   ```

**Note**: The "418 I'm a teapot" authentication error you may see is **expected** with sandbox credentials. USSD still works, but SMS will be logged to file instead of sent.

### Option B: Get Your Own MTN Credentials (Recommended for Production)

#### Step 1: Create MTN Developer Account

1. Go to **https://developers.mtn.com/**
2. Click "Sign Up" or "Register"
3. Fill in your details:
   - Name
   - Email
   - Phone number
   - Country: Ghana
4. Verify your email
5. Complete profile

#### Step 2: Create USSD Application

1. Login to MTN Developer Portal
2. Go to **"My Apps"** or **"Applications"**
3. Click **"Create New App"**
4. Fill in application details:
   - **App Name**: SusuSave (or your name)
   - **Description**: Savings group management platform
   - **Category**: Financial Services
   - **Country**: Ghana
5. Submit application

#### Step 3: Get Credentials

Once approved (usually instant for sandbox):

1. Go to your app dashboard
2. Find **"API Credentials"** section
3. Copy:
   - **Consumer Key**
   - **Consumer Secret**
4. Note your **Environment**: sandbox or production

#### Step 4: Request USSD Code

1. In your app dashboard, find **"USSD"** section
2. Click **"Request USSD Code"**
3. Provide:
   - **Preferred Code**: e.g., `*920*55#` (MTN will assign available code)
   - **Service Description**: "Savings group management"
   - **Expected Usage**: "10,000 sessions/month" (estimate)
4. Submit request
5. Wait for approval (1-5 business days)

#### Step 5: Update `.env` File

```env
MTN_CONSUMER_KEY=your-actual-consumer-key
MTN_CONSUMER_SECRET=your-actual-consumer-secret
MTN_USSD_SERVICE_CODE=*920*YOUR_CODE#
MTN_ENVIRONMENT=sandbox  # Change to "production" when ready
```

#### Step 6: Set Up Callback URL

See [Callback URL Setup](#callback-url-setup) section below.

---

## AfricasTalking USSD Setup

### Step 1: Create AfricasTalking Account

1. Go to **https://account.africastalking.com/auth/register**
2. Click **"Sign Up"**
3. Fill in your details:
   - First Name
   - Last Name
   - Email
   - Phone Number
   - Country
4. Accept terms and create account
5. Verify your email

### Step 2: Get API Credentials

1. Login to AfricasTalking Dashboard
2. Go to **Settings** (top right)
3. Click **"API Key"** tab
4. Copy your **Username** (usually your email or custom username)
5. Click **"Generate API Key"** or view existing key
6. Copy the **API Key** (starts with "atsk_")

**Important**: Save your API key securely. You can't view it again!

### Step 3: Test in Sandbox (Recommended First)

For testing without real credits:

```env
AT_USERNAME=sandbox
AT_API_KEY=your-actual-api-key
AT_ENVIRONMENT=sandbox
```

**Testing in Sandbox**:
- Download "AfricasTalking Sandbox" mobile app (iOS/Android)
- Login with your AT credentials
- Use the app to dial USSD codes
- Free for testing

### Step 4: Apply for USSD Code

1. In AT Dashboard, go to **"USSD"** section
2. Click **"Create Channel"** or **"Request USSD Code"**
3. Fill in details:
   - **Channel Name**: SusuSave
   - **Service Code**: Request a code (e.g., `*384*12345#`)
   - **Description**: Savings group management
   - **Callback URL**: (set up next - see Callback URL Setup)
4. Submit request
5. Wait for approval (2-5 business days)

**Sandbox Code**: In sandbox mode, you can test immediately with default codes.

### Step 5: Update `.env` File

```env
USE_MTN_SERVICES=False  # Use AfricasTalking
AT_USERNAME=sandbox  # or your actual username for production
AT_API_KEY=atsk_your_actual_api_key_here
AT_ENVIRONMENT=sandbox  # or "production"
AT_USSD_SERVICE_CODE=*384*YOUR_CODE#
```

### Step 6: Add Credits (For Production)

1. Go to **"Billing"** in AT Dashboard
2. Click **"Buy Credits"**
3. Choose payment method:
   - Mobile Money
   - Credit Card
   - Bank Transfer
4. Add credits (start with $5-10 for testing)

**Pricing** (approximate):
- USSD: ~$0.005 per session
- SMS: ~$0.03 per message

---

## Environment Configuration

### Complete `.env` File Example

Create `backend/.env` with the following:

```env
# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_URL=postgresql://sususer:suspass@localhost:5432/sususave

# ============================================
# SECURITY (REQUIRED - CHANGE THESE!)
# ============================================
SECRET_KEY=your-generated-secret-key-here
ENCRYPTION_KEY=your-generated-fernet-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# ============================================
# USSD CONFIGURATION
# ============================================
USSD_CODE=*920*55#

# ============================================
# SMS & MOMO (Development)
# ============================================
ENABLE_REAL_SMS=False
ENABLE_REAL_MOMO=False
SMS_LOGS_PATH=sms_logs.txt
MOMO_TRANSACTIONS_PATH=momo_transactions.json

# ============================================
# AFRICASTALKING CONFIGURATION
# ============================================
AT_USERNAME=sandbox
AT_API_KEY=your-at-api-key-here
AT_ENVIRONMENT=sandbox
AT_USSD_SERVICE_CODE=*384*12345#

# ============================================
# MTN CONFIGURATION
# ============================================
MTN_CONSUMER_KEY=J7SH4tF6QqAsa6VYFhtGRwgpvPjYnF9y
MTN_CONSUMER_SECRET=1gBhKETCBKLMyILR
MTN_ENVIRONMENT=sandbox
MTN_BASE_URL=https://api.mtn.com/v1
MTN_USSD_SERVICE_CODE=*920*55#
MTN_CALLBACK_URL=https://your-ngrok-url.ngrok-free.app/ussd/callback

# ============================================
# MTN MOBILE MONEY (Optional)
# ============================================
MTN_MOMO_SUBSCRIPTION_KEY=your-momo-key
MTN_MOMO_API_USER=your-api-user
MTN_MOMO_API_KEY=your-api-key
MTN_MOMO_TARGET_ENVIRONMENT=sandbox
MTN_MOMO_BASE_URL=https://sandbox.momodeveloper.mtn.com
MTN_MOMO_CURRENCY=GHS

# ============================================
# PROVIDER SELECTION
# ============================================
# Set to True to use MTN, False to use AfricasTalking
USE_MTN_SERVICES=True

ENABLE_MTN_USSD=True
ENABLE_MTN_SMS=True
ENABLE_MTN_MOMO=True

# ============================================
# MTN KYC (Ghana Compliance)
# ============================================
ENABLE_MTN_KYC=True
MTN_KYC_BASE_URL=https://api.mtn.com/v1
REQUIRE_KYC_FOR_PAYMENTS=True

# ============================================
# SCHEDULER
# ============================================
ENABLE_SCHEDULER=True
PAYMENT_CHECK_HOUR=6
RETRY_INTERVAL_HOURS=6
PAYOUT_CHECK_INTERVAL_HOURS=2

# ============================================
# REDIS (Optional for USSD Sessions)
# ============================================
REDIS_URL=redis://localhost:6379/0
USE_REDIS=False

# ============================================
# CORS ORIGINS
# ============================================
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8081"]
```

### Key Configuration Options

#### Provider Selection

```env
# Use MTN for USSD and SMS
USE_MTN_SERVICES=True

# Use AfricasTalking for USSD and SMS
USE_MTN_SERVICES=False
```

#### Environment Selection

```env
# MTN
MTN_ENVIRONMENT=sandbox     # for testing
MTN_ENVIRONMENT=production  # for live

# AfricasTalking
AT_ENVIRONMENT=sandbox      # for testing
AT_ENVIRONMENT=production   # for live
```

#### Enable/Disable Features

```env
# Enable real SMS (otherwise logs to file)
ENABLE_REAL_SMS=True

# Enable real Mobile Money (otherwise mock)
ENABLE_REAL_MOMO=True

# Enable MTN specific services
ENABLE_MTN_USSD=True
ENABLE_MTN_SMS=True
ENABLE_MTN_MOMO=True
```

---

## Callback URL Setup

### What is a Callback URL?

When a user dials your USSD code, the provider (MTN or AfricasTalking) sends a request to your **callback URL** with the user's input. Your application responds with the menu to display.

**Format**: `https://your-domain.com/ussd/callback`

### Development Setup (Using ngrok)

For local development, use ngrok to expose your local server:

#### Step 1: Install ngrok

```bash
# macOS
brew install ngrok

# or download from https://ngrok.com/download
```

#### Step 2: Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

#### Step 3: Start ngrok

```bash
# In a new terminal
ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123def456.ngrok-free.app -> http://localhost:8000
```

#### Step 4: Copy HTTPS URL

Copy the HTTPS URL (e.g., `https://abc123def456.ngrok-free.app`)

#### Step 5: Update `.env`

```env
MTN_CALLBACK_URL=https://abc123def456.ngrok-free.app/ussd/callback
```

**Important**: 
- The URL changes every time you restart ngrok (unless you have a paid account)
- You'll need to update the provider dashboard each time

### Register Callback with MTN

1. Login to MTN Developer Portal
2. Go to your app
3. Find USSD settings
4. Set **Callback URL**: `https://your-ngrok-url.ngrok-free.app/ussd/callback`
5. Save changes

### Register Callback with AfricasTalking

1. Login to AT Dashboard
2. Go to **USSD** section
3. Find your USSD channel
4. Set **Callback URL**: `https://your-ngrok-url.ngrok-free.app/ussd/callback`
5. Save changes

### Production Setup (Permanent Domain)

For production, you need a **permanent HTTPS domain**:

#### Option 1: Cloud Hosting (Recommended)

Deploy to cloud platform with automatic HTTPS:

- **Heroku**: `https://your-app.herokuapp.com/ussd/callback`
- **Railway**: `https://your-app.up.railway.app/ussd/callback`
- **Render**: `https://your-app.onrender.com/ussd/callback`
- **AWS/DigitalOcean**: `https://api.yourdomain.com/ussd/callback`

#### Option 2: Your Own Server

1. Get a domain (e.g., yourdomain.com)
2. Set up SSL certificate (use Let's Encrypt - free)
3. Point domain to your server
4. Configure nginx/apache
5. Use URL: `https://api.yourdomain.com/ussd/callback`

#### Requirements

- ✅ **HTTPS** (SSL certificate required)
- ✅ **Publicly accessible** (not localhost)
- ✅ **Fast response** (< 8 seconds, ideally < 3 seconds)
- ✅ **Reliable** (high uptime)

---

## Testing Your Setup

### Test 1: Verify Setup Script

```bash
cd backend
python verify_ussd_setup.py
```

Expected output:
```
✅ .env file found
✅ MTN USSD configuration complete
✅ USSD endpoint is accessible
🎉 USSD setup is complete and ready for testing!
```

### Test 2: Check USSD Health

```bash
curl http://localhost:8000/ussd/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "ussd",
  "provider": "MTN",
  "environment": "sandbox",
  "service_code": "*920*55#"
}
```

### Test 3: Test USSD Menu

```bash
curl -X POST http://localhost:8000/ussd/callback \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "sessionId=test-123" \
  -d "serviceCode=*920*55%23" \
  -d "phoneNumber=%2B233240000000" \
  -d "text="
```

Expected response:
```
CON Welcome to SusuSave
1. Join Group
2. Pay Contribution
3. Check Balance/Status
4. My Payout Date
```

### Test 4: Run Automated Tests

#### AfricasTalking Tests

```bash
cd backend
python test_africastalking_ussd.py test
```

Expected:
```
Test 1: Display Main Menu ✓
Test 2: Check Status ✓
Test 3: Invalid Menu Option ✓
Test 4: Join Group Flow ✓
All tests passed!
```

#### Interactive Testing

```bash
cd backend
python test_africastalking_ussd.py
```

This starts an interactive USSD simulator where you can test all flows.

### Test 5: Test with Real Phone (If Available)

#### Using AfricasTalking Sandbox App

1. Download "AfricasTalking Sandbox" app
2. Login with your AT credentials
3. Go to USSD section
4. Dial your USSD code
5. Test all menu options

#### Using MTN (If Credentials Valid)

1. Use a Ghana MTN phone number
2. Dial your USSD code (e.g., `*920*55#`)
3. Follow prompts
4. Test all flows

---

## Troubleshooting

### Issue: `.env` file not found

**Solution**:
```bash
cd backend
cp env.example .env
# Edit .env with your settings
```

### Issue: "MTN authentication failed: 418 I'm a teapot"

**Explanation**: This is **expected** with sandbox/placeholder credentials.

**Solution**:
- USSD still works (test it!)
- SMS logs to file instead of sending
- For production: Get real MTN credentials

### Issue: "AfricasTalking credentials not configured"

**Solution**:
1. Get API key from AT dashboard
2. Update `.env`:
   ```env
   AT_API_KEY=atsk_your_actual_key_here
   ```

### Issue: "Cannot reach USSD endpoint"

**Solution**:
1. Make sure backend is running:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```
2. Check it's accessible:
   ```bash
   curl http://localhost:8000/ussd/health
   ```

### Issue: "Callback URL not reachable"

**Solution**:
1. Make sure ngrok is running:
   ```bash
   ngrok http 8000
   ```
2. Copy HTTPS URL from ngrok output
3. Update provider dashboard with new URL
4. Test accessibility:
   ```bash
   curl https://your-ngrok-url.ngrok-free.app/ussd/health
   ```

### Issue: "Invalid USSD response"

**Possible causes**:
- Response doesn't start with "CON" or "END"
- Response time > 8 seconds
- Server error

**Solution**:
1. Check backend logs:
   ```bash
   # Look for errors
   tail -f backend/app.log
   ```
2. Test endpoint directly
3. Verify database connection

### Issue: "Session lost/timeout"

**Solution**:
- Response time might be too slow (> 8 seconds)
- Check database queries are optimized
- Consider using Redis for sessions:
  ```env
  USE_REDIS=True
  REDIS_URL=redis://localhost:6379/0
  ```

### Issue: "Database connection error"

**Solution**:
1. Make sure PostgreSQL is running:
   ```bash
   # Check status
   pg_isready
   ```
2. Verify DATABASE_URL in `.env`
3. Test connection:
   ```bash
   psql $DATABASE_URL
   ```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] **Credentials**
  - [ ] Production MTN credentials (if using MTN)
  - [ ] Production AT credentials (if using AT)
  - [ ] Valid USSD codes assigned
  - [ ] API keys tested

- [ ] **Infrastructure**
  - [ ] Production server/cloud hosting
  - [ ] Permanent domain name
  - [ ] SSL certificate installed
  - [ ] Database backed up
  - [ ] Redis installed (recommended)

- [ ] **Configuration**
  - [ ] `.env` file with production settings
  - [ ] Strong SECRET_KEY generated
  - [ ] ENCRYPTION_KEY generated
  - [ ] Database connection pooling enabled
  - [ ] CORS origins configured

- [ ] **Provider Setup**
  - [ ] Callback URLs registered
  - [ ] USSD codes tested
  - [ ] Account funding (for AT)
  - [ ] Webhooks configured

- [ ] **Testing**
  - [ ] All automated tests passing
  - [ ] Manual testing with real phones
  - [ ] Load testing completed
  - [ ] Error handling verified

- [ ] **Monitoring**
  - [ ] Error tracking (Sentry, etc.)
  - [ ] Logging configured
  - [ ] Alerts set up
  - [ ] Health checks enabled

### Deployment Steps

#### Step 1: Prepare Production Environment

```bash
# Clone repository
git clone <your-repo-url>
cd susu

# Install dependencies
cd backend
pip install -r requirements.txt

# Set up database
# Run migrations
alembic upgrade head

# Seed initial data (optional)
python seed_data.py
```

#### Step 2: Configure Production `.env`

```env
# Use production credentials
MTN_ENVIRONMENT=production
AT_ENVIRONMENT=production

# Use real services
ENABLE_REAL_SMS=True
ENABLE_REAL_MOMO=True

# Production database
DATABASE_URL=postgresql://user:pass@prod-db:5432/sususave

# Production callback
MTN_CALLBACK_URL=https://api.yourdomain.com/ussd/callback

# Enable Redis
USE_REDIS=True
REDIS_URL=redis://prod-redis:6379/0
```

#### Step 3: Start Production Server

```bash
# Using gunicorn (recommended)
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 30

# Or using uvicorn
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

#### Step 4: Update Provider Dashboards

1. **MTN Developer Portal**
   - Update callback URL to production
   - Switch environment to production
   - Verify USSD code is active

2. **AfricasTalking Dashboard**
   - Update callback URL to production
   - Switch to production environment
   - Ensure account has credits

#### Step 5: Test in Production

```bash
# Health check
curl https://api.yourdomain.com/ussd/health

# Test with real phone
# Dial your USSD code from a mobile phone
```

#### Step 6: Monitor

- Watch error logs
- Monitor response times
- Track USSD session metrics
- Monitor API usage and costs

---

## Support & Additional Resources

### Documentation
- **Status Report**: `USSD_SETUP_STATUS.md`
- **Quick Start**: `USSD_QUICKSTART.md`
- **Testing Guide**: `USSD_TESTING_GUIDE.md`
- **MTN Integration**: `MTN_INTEGRATION_COMPLETE.md`
- **AfricasTalking**: `AFRICASTALKING_INTEGRATION_SUMMARY.md`

### External Links
- **MTN Developer Portal**: https://developers.mtn.com/
- **MTN MoMo**: https://momodeveloper.mtn.com/
- **AfricasTalking**: https://account.africastalking.com/
- **AT Documentation**: https://developers.africastalking.com/docs/ussd
- **ngrok**: https://ngrok.com/

### Getting Help

1. **Check documentation** in this repository
2. **Run verification script**: `python verify_ussd_setup.py`
3. **Check logs**: Look for error messages
4. **Test endpoint**: Use curl to test directly
5. **Contact provider support**: MTN or AfricasTalking

---

## Quick Command Reference

```bash
# Setup
cd backend
cp env.example .env
python verify_ussd_setup.py

# Start backend
python -m uvicorn app.main:app --reload

# Start ngrok (for local testing)
ngrok http 8000

# Run tests
python test_africastalking_ussd.py test
./test_ussd_curl.sh

# Check health
curl http://localhost:8000/ussd/health

# Test USSD menu
curl -X POST http://localhost:8000/ussd/callback \
  -d "sessionId=test" \
  -d "phoneNumber=+233240000000" \
  -d "serviceCode=*920*55#" \
  -d "text="

# Generate keys
openssl rand -hex 32  # SECRET_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # ENCRYPTION_KEY
```

---

**You're all set!** Follow these instructions step by step, and you'll have USSD running in no time.

**Questions?** Check the documentation or run `python verify_ussd_setup.py` for diagnostics.

**Last Updated**: October 23, 2025  
**Version**: 1.0

