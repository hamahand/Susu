# MTN Credentials Setup Guide

**Purpose**: Get your MTN API credentials and configure them properly  
**Time Required**: 15-30 minutes  
**Date**: October 23, 2025

---

## 📋 Overview

You need credentials from THREE different MTN services:

1. **MTN API** (for SMS and USSD) - From MTN Developer Portal
2. **MTN Mobile Money** (for payments) - From MTN MoMo Developer Portal
3. **MTN KYC** (for compliance) - Uses same credentials as MTN API

---

## 🎯 Step 1: Create MTN Developer Account

### 1.1 Register at MTN Developer Portal

1. Go to: **https://developer.mtn.com/**
2. Click "Sign Up" or "Create Account"
3. Fill in your details:
   - Email address
   - Phone number (Ghana number recommended)
   - Company/Organization name
   - Developer type (Individual/Company)
4. Verify your email
5. Complete your profile

### 1.2 Login to Dashboard

1. Go to: **https://developer.mtn.com/login**
2. Enter your credentials
3. You should see the Developer Dashboard

---

## 🔑 Step 2: Get MTN API Credentials (SMS & USSD)

### 2.1 Create New Application

1. In the Developer Dashboard, click **"My Apps"** or **"Applications"**
2. Click **"Create New App"** or **"Add Application"**
3. Fill in application details:
   ```
   App Name: SusuSave
   Description: Hybrid ROSCA Platform for susu savings groups
   Category: Financial Services
   Platform: Web & Mobile
   Country: Ghana
   ```
4. Click **"Create"** or **"Submit"**

### 2.2 Subscribe to APIs

You need to subscribe to these APIs:

1. **SMS API**
   - In your app dashboard, click "Add API" or "Subscribe"
   - Select "SMS API"
   - Choose environment: **Sandbox** (for testing)
   - Click "Subscribe"

2. **USSD API** (if available)
   - Click "Add API" or "Subscribe"
   - Select "USSD API" or "Mobile Messaging"
   - Choose environment: **Sandbox**
   - Click "Subscribe"

### 2.3 Get Your Credentials

After subscribing, you'll get:

```
Consumer Key (Client ID): xxxxxxxxxxxxxxxxxxxxxxxxxxxx
Consumer Secret: yyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

**⚠️ IMPORTANT:** Save these immediately! The secret might only be shown once.

**Location to find credentials:**
- Usually in "Credentials" tab
- Or "API Keys" section
- Or under each subscribed API

### 2.4 Get API Base URL

Check the API documentation for the correct endpoint:

**For Ghana:**
- Sandbox: `https://sandbox.api.mtn.com/v1`
- Production: `https://api.mtn.com/gh/v1`

Or check MTN's documentation for the exact URL.

---

## 💰 Step 3: Get MTN Mobile Money Credentials

### 3.1 Register at MTN MoMo Developer Portal

1. Go to: **https://momodeveloper.mtn.com/**
2. Click "Sign Up" (separate from MTN API account)
3. Fill in your details
4. Verify your email
5. Login to dashboard

### 3.2 Create MoMo Sandbox User

For sandbox testing, you need to create an API user:

```bash
# Run this from your project directory
cd /Users/maham/susu/backend

# This script should create sandbox credentials
python setup_mtn_momo.py
```

Or manually via API:

```bash
# 1. Get your Subscription Key from MoMo portal
SUBSCRIPTION_KEY="your_subscription_key_here"

# 2. Generate API User
curl -X POST https://sandbox.momodeveloper.mtn.com/v1_0/apiuser \
  -H "X-Reference-Id: $(uuidgen)" \
  -H "Ocp-Apim-Subscription-Key: $SUBSCRIPTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{"providerCallbackHost": "your_callback_url"}'

# 3. Get API Key for that user
curl -X POST https://sandbox.momodeveloper.mtn.com/v1_0/apiuser/{apiuser}/apikey \
  -H "Ocp-Apim-Subscription-Key: $SUBSCRIPTION_KEY"
```

### 3.3 MoMo Credentials You Need

```
Subscription Key: Your primary subscription key
API User: The UUID you generated
API Key: The key returned from the API
```

---

## ⚙️ Step 4: Configure Your Application

### 4.1 Create .env File

```bash
cd /Users/maham/susu/backend
cp env.example .env
```

### 4.2 Edit .env File

Open `/Users/maham/susu/backend/.env` and update these sections:

#### MTN API Configuration (SMS & USSD)

```env
# MTN API Configuration
MTN_CONSUMER_KEY=your_actual_consumer_key_from_step_2
MTN_CONSUMER_SECRET=your_actual_consumer_secret_from_step_2
MTN_ENVIRONMENT=sandbox  # Change to "production" when ready
MTN_BASE_URL=https://sandbox.api.mtn.com/v1  # Or correct Ghana URL
MTN_USSD_SERVICE_CODE=*920*55#  # Your assigned USSD code
MTN_CALLBACK_URL=https://your-domain.com/ussd/callback  # More on this below
```

#### MTN Mobile Money Configuration

```env
# MTN Mobile Money Configuration
MTN_MOMO_SUBSCRIPTION_KEY=your_momo_subscription_key_from_step_3
MTN_MOMO_API_USER=your_api_user_uuid_from_step_3
MTN_MOMO_API_KEY=your_api_key_from_step_3
MTN_MOMO_TARGET_ENVIRONMENT=sandbox  # Change to "production" when ready
MTN_MOMO_BASE_URL=https://sandbox.momodeveloper.mtn.com
MTN_MOMO_CURRENCY=GHS
```

#### Enable MTN Services

```env
# Enable MTN Services
ENABLE_MTN_USSD=true
ENABLE_MTN_SMS=true
ENABLE_MTN_MOMO=true
USE_MTN_SERVICES=true
ENABLE_MTN_KYC=true
```

### 4.3 Security Settings

**⚠️ IMPORTANT:** Generate secure keys:

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Update in `.env`:

```env
SECRET_KEY=your_generated_secret_key_here
ENCRYPTION_KEY=your_generated_encryption_key_here
```

---

## 🌐 Step 5: Set Up Public Callback URL

MTN needs to send requests to your server. You need a public URL.

### Option A: Using ngrok (Development/Testing)

1. **Install ngrok:**
   ```bash
   # macOS
   brew install ngrok
   
   # Or download from https://ngrok.com/download
   ```

2. **Start ngrok:**
   ```bash
   ngrok http 8000
   ```

3. **Copy the URL:**
   ```
   Forwarding: https://abc123.ngrok-free.app -> http://localhost:8000
   ```

4. **Update .env:**
   ```env
   MTN_CALLBACK_URL=https://abc123.ngrok-free.app/ussd/callback
   ```

### Option B: Using Production Domain

If you have a production server:

```env
MTN_CALLBACK_URL=https://api.yourdomain.com/ussd/callback
```

### 5.3 Register Callback URL with MTN

1. Go to MTN Developer Portal
2. Open your SusuSave application
3. Find "Webhook" or "Callback URL" settings
4. Add your callback URL
5. Save changes

---

## 🧪 Step 6: Test Your Configuration

### 6.1 Restart Backend

```bash
cd /Users/maham/susu
docker-compose restart backend
```

### 6.2 Watch Logs

```bash
docker logs sususave_backend --tail 50 --follow
```

**Look for:**
- ✅ "Successfully obtained MTN access token"
- ✅ "MTN SMS Integration initialized"
- ❌ Any authentication errors

### 6.3 Test SMS Sending

```bash
# Test via Python
cd /Users/maham/susu/backend

python3 << EOF
from app.integrations.mtn_sms_integration import mtn_sms_service

result = mtn_sms_service.send_single_sms(
    phone_number="+233244555555",  # Use your test number
    message="Test SMS from SusuSave!"
)

print(result)
EOF
```

**Expected:** SMS sent successfully or detailed error message

### 6.4 Test USSD

```bash
# Test USSD endpoint
curl -X POST http://localhost:8000/ussd/callback \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "sessionId=test123&serviceCode=*920*55%23&phoneNumber=%2B233244555555&text="
```

**Expected:** USSD menu response (same as before, but now using MTN)

### 6.5 Test Mobile Money

```bash
# Test MoMo validation
curl -X POST http://localhost:8000/payments/validate-account \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+233244555555"}'
```

### 6.6 Check Health

```bash
curl http://localhost:8000/ussd/health
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "ussd",
  "provider": "MTN",
  "environment": "sandbox",
  "service_code": "*920*55#",
  "callback_url": "https://your-ngrok-url.ngrok-free.app/ussd/callback"
}
```

---

## 🐛 Step 7: Troubleshooting

### Issue 1: Still Getting 418 Error

**Possible causes:**
1. **Wrong endpoint URL**
   - Check MTN documentation for Ghana-specific URL
   - Try: `https://sandbox.api.mtn.com/v1` or `https://api.mtn.com/gh/v1`

2. **Credentials not activated**
   - Some MTN accounts require manual activation
   - Contact MTN support to activate your sandbox credentials

3. **Invalid credentials format**
   - Ensure no extra spaces in .env file
   - Check credentials are copied correctly

**Solution:**
```bash
# Test credentials directly
curl -X POST https://sandbox.api.mtn.com/v1/oauth/token \
  -H "Authorization: Basic $(echo -n 'YOUR_KEY:YOUR_SECRET' | base64)" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials"
```

If this fails, your credentials are invalid.

### Issue 2: Callback URL Not Working

**Possible causes:**
1. ngrok not running
2. Callback not registered with MTN
3. Firewall blocking requests

**Solution:**
```bash
# Test ngrok is accessible
curl https://your-ngrok-url.ngrok-free.app/

# Check backend is responding
curl https://your-ngrok-url.ngrok-free.app/ussd/health
```

### Issue 3: MoMo Credentials Invalid

**Solution:**
```bash
# Re-run setup script
cd /Users/maham/susu/backend
python setup_mtn_momo.py

# Or manually create new API user following Step 3.2
```

### Issue 4: SMS Not Sending

**Check:**
1. Phone number format: Must have country code (+233...)
2. Sender ID registered with MTN
3. SMS quota available in sandbox

**Debug:**
```bash
# Check logs for specific error
docker logs sususave_backend 2>&1 | grep -i "sms\|error"
```

---

## 📞 Step 8: Request USSD Short Code

### For Production USSD

1. **Contact MTN Ghana:**
   - Email: api.support@mtn.com.gh
   - Or contact via Developer Portal support

2. **Request USSD short code:**
   ```
   Subject: USSD Short Code Application for SusuSave

   Hello,

   I am developing a ROSCA (susu) savings platform called SusuSave.
   I would like to request a USSD short code for Ghana.

   Application Details:
   - App Name: SusuSave
   - Purpose: Susu savings group management
   - Features: Join groups, make payments, check balance
   - Target Users: Ghana mobile users

   Current callback URL: https://your-domain.com/ussd/callback

   Please let me know the process and requirements.

   Thank you,
   [Your Name]
   ```

3. **Wait for approval:**
   - Usually takes 1-2 weeks
   - May require additional documentation
   - May have setup fees

4. **Update configuration:**
   ```env
   MTN_USSD_SERVICE_CODE=*920*55#  # Your assigned code
   ```

---

## ✅ Step 9: Verify Everything Works

### Complete Integration Test

```bash
# Run this comprehensive test
cd /Users/maham/susu/backend

# 1. Test authentication
curl -s http://localhost:8000/ussd/health | python3 -m json.tool

# 2. Test USSD
python test_africastalking_ussd.py test

# 3. Test SMS (if you have test credits)
# SMS will be sent to real phone

# 4. Check logs for any errors
docker logs sususave_backend --tail 100 | grep -i "error\|warn"
```

**Success Indicators:**
- ✅ No "418 I'm a teapot" errors
- ✅ "Successfully obtained MTN access token" in logs
- ✅ USSD tests pass
- ✅ SMS sent to real phone (if testing)
- ✅ Health check shows "healthy"

---

## 📚 Resources

### Official Documentation
- **MTN Developer Portal**: https://developer.mtn.com/
- **MTN MoMo Portal**: https://momodeveloper.mtn.com/
- **MTN API Docs**: https://developer.mtn.com/docs/
- **MoMo API Docs**: https://momodeveloper.mtn.com/api-documentation/

### Support Channels
- **MTN API Support**: api.support@mtn.com
- **MTN Ghana**: api.support@mtn.com.gh
- **Developer Forum**: Check MTN developer portal for community forum

### Project Documentation
- `MTN_USSD_ERROR_DIAGNOSIS.md` - Error details
- `USSD_TESTING_GUIDE.md` - Testing instructions
- `MOMO_SETUP_GUIDE.md` - Mobile Money setup
- `backend/README_AFRICASTALKING.md` - Alternative to MTN

---

## 🔐 Security Best Practices

### 1. Never Commit Credentials
```bash
# Ensure .env is in .gitignore
echo ".env" >> /Users/maham/susu/.gitignore
```

### 2. Use Environment Variables in Production
```bash
# Don't use .env file in production
# Set environment variables directly:
export MTN_CONSUMER_KEY="your_key"
export MTN_CONSUMER_SECRET="your_secret"
```

### 3. Rotate Credentials Regularly
- Change API keys every 90 days
- Use different credentials for different environments
- Revoke old credentials when not needed

### 4. Monitor Usage
- Check MTN dashboard for unusual activity
- Set up alerts for high SMS/API usage
- Monitor logs for failed authentication attempts

---

## 💡 Quick Reference

### Environment Variables Needed

```env
# Required for MTN SMS & USSD
MTN_CONSUMER_KEY=xxx
MTN_CONSUMER_SECRET=yyy
MTN_BASE_URL=https://sandbox.api.mtn.com/v1
MTN_CALLBACK_URL=https://your-domain.com/ussd/callback

# Required for MTN Mobile Money
MTN_MOMO_SUBSCRIPTION_KEY=xxx
MTN_MOMO_API_USER=uuid-here
MTN_MOMO_API_KEY=yyy

# Enable services
USE_MTN_SERVICES=true
ENABLE_MTN_USSD=true
ENABLE_MTN_SMS=true
ENABLE_MTN_MOMO=true
```

### Quick Test Commands

```bash
# Health check
curl http://localhost:8000/ussd/health

# Test USSD
python test_africastalking_ussd.py test

# Watch logs
docker logs sususave_backend -f

# Restart after config change
docker-compose restart backend
```

---

## ❓ FAQ

**Q: Do I need separate accounts for MTN API and MTN MoMo?**  
A: Yes, they are different services with different portals.

**Q: How much does it cost?**  
A: Sandbox is free. Production has per-SMS and per-transaction fees. Check MTN pricing.

**Q: Can I use the same credentials for sandbox and production?**  
A: No, you need separate credentials for each environment.

**Q: What if MTN services are not available in my region?**  
A: Use AfricasTalking instead - see `backend/README_AFRICASTALKING.md`

**Q: How long do sandbox credentials last?**  
A: Usually 30-90 days, then you may need to request extension or go to production.

**Q: Can I test without real phone numbers?**  
A: Yes, in sandbox you can use test numbers provided by MTN.

---

**Last Updated**: October 23, 2025  
**Status**: Ready for Implementation  
**Estimated Setup Time**: 15-30 minutes (excluding MTN approval time)

