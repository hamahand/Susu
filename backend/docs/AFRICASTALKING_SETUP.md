# AfricaTalking USSD Setup Guide

This guide will help you set up and test your USSD application with AfricaTalking's sandbox and production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Sandbox Setup](#sandbox-setup)
3. [Local Development](#local-development)
4. [Testing USSD](#testing-ussd)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- AfricaTalking account ([Sign up here](https://account.africastalking.com/auth/register))
- Python 3.8+
- ngrok or similar tunneling service (for local testing)

---

## Sandbox Setup

### 1. Create an AfricaTalking Account

1. Go to [AfricaTalking](https://account.africastalking.com/auth/register)
2. Sign up for a free account
3. Verify your email address

### 2. Access the Sandbox

1. Log in to your dashboard at [account.africastalking.com](https://account.africastalking.com/)
2. By default, you'll start in the **Sandbox** environment
3. Note: The sandbox is free but uses test credentials

### 3. Get Your API Credentials

1. In the dashboard, go to **Settings** → **API Key**
2. Generate an API key
3. Copy your credentials:
   - **Username**: `sandbox` (for sandbox environment)
   - **API Key**: Your generated key (looks like `atsk_xxxxxxxxxxxx`)

### 4. Configure USSD Service

1. In the dashboard, go to **USSD** → **Create Channel**
2. Fill in the details:
   - **Name**: SusuSave USSD
   - **USSD Code**: Leave empty (sandbox assigns automatically, usually `*384*12345#`)
   - **Callback URL**: Your public URL (see ngrok setup below)
3. Click **Create Channel**
4. Note your assigned USSD code

---

## Local Development

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create or update your `.env` file:

```bash
# Copy example file
cp env.example .env

# Edit .env file
nano .env
```

Add your AfricaTalking credentials:

```env
# AfricaTalking Configuration
AT_USERNAME=sandbox
AT_API_KEY=your_api_key_here
AT_ENVIRONMENT=sandbox
AT_USSD_SERVICE_CODE=*384*12345#
```

### 3. Set Up ngrok for Local Testing

AfricaTalking needs a public URL to send USSD callbacks. Use ngrok to expose your local server:

```bash
# Install ngrok (if not already installed)
# macOS
brew install ngrok

# Or download from https://ngrok.com/download

# Start your backend server
cd backend
python -m uvicorn app.main:app --reload --port 8000

# In a new terminal, start ngrok
ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

### 4. Update AfricaTalking Callback URL

1. Copy your ngrok HTTPS URL (e.g., `https://abc123.ngrok.io`)
2. Go to AfricaTalking dashboard → **USSD** → Your channel
3. Update the **Callback URL** to: `https://abc123.ngrok.io/ussd/callback`
4. Save changes

**Important**: Every time you restart ngrok, the URL changes, so you'll need to update the callback URL in AfricaTalking dashboard.

---

## Testing USSD

### Method 1: AfricaTalking Simulator

1. In the AfricaTalking dashboard, go to **USSD** → **Simulator**
2. Enter a test phone number (e.g., `+254700000001`)
3. Enter your USSD code (e.g., `*384*12345#`)
4. Click **Dial**
5. Interact with your USSD menu

### Method 2: Local Test Script

Use our provided test script to simulate USSD requests:

```bash
cd backend

# Interactive mode
python test_africastalking_ussd.py

# Automated tests
python test_africastalking_ussd.py test
```

### Method 3: Mobile App (Sandbox)

Download the AfricaTalking Sandbox app:
- Android: [Google Play Store](https://play.google.com/store/apps/details?id=com.africastalking.mobile.android)
- iOS: [App Store](https://apps.apple.com/us/app/africastalking-sandbox/id1435432093)

1. Open the app
2. Log in with your AfricaTalking credentials
3. Dial your USSD code
4. Interact with your application

---

## USSD Flow Example

Here's how users will interact with your USSD application:

```
Dial: *384*12345#

Screen 1 (Main Menu):
----------------------
CON Welcome to SusuSave
1. Join Group
2. Pay Contribution
3. Check Balance/Status
4. My Payout Date

User enters: 1

Screen 2 (Join Group):
----------------------
CON Enter Group Code (e.g., SUSU1234):

User enters: SUSU5678

Screen 3 (Success):
-------------------
END Success! You joined Family Savings.
Position: 3
Contribution: GHS 50
You will receive an SMS with details.
```

---

## Production Deployment

### 1. Switch to Live Account

1. In AfricaTalking dashboard, toggle to **Live** environment
2. Add funds to your account (for SMS and payment features)
3. Generate new production API key

### 2. Apply for USSD Code

1. Go to **USSD** → **Create Channel**
2. Click **Apply for USSD Code**
3. Fill in the application form:
   - **Service Description**: Describe SusuSave
   - **Expected Traffic**: Estimate daily users
   - **Business Details**: Company information
4. Submit and wait for approval (usually 2-5 business days)

### 3. Update Production Environment

```env
AT_USERNAME=your_live_username
AT_API_KEY=your_live_api_key
AT_ENVIRONMENT=production
AT_USSD_SERVICE_CODE=*920*55#  # Your approved code
```

### 4. Update Callback URL

1. Deploy your backend to a production server
2. Update AfricaTalking callback URL to your production domain
3. Example: `https://api.sususave.com/ussd/callback`

### 5. SSL Certificate

- **Required**: AfricaTalking only accepts HTTPS URLs
- Use Let's Encrypt or your hosting provider's SSL certificate
- Ensure your certificate is valid and not self-signed

---

## Troubleshooting

### Common Issues

#### 1. Callback URL Not Reachable

**Error**: AfricaTalking can't reach your callback URL

**Solutions**:
- ✅ Ensure ngrok is running (for local dev)
- ✅ Check your server is running on the correct port
- ✅ Verify HTTPS is enabled (production)
- ✅ Test URL manually: `curl https://your-url/ussd/callback`
- ✅ Check firewall rules aren't blocking AfricaTalking IPs

#### 2. USSD Session Timeout

**Issue**: Session ends unexpectedly

**Solutions**:
- ✅ Ensure you're returning `CON` for continue, `END` to finish
- ✅ Check session storage is working (USSDSession class)
- ✅ Response time should be < 8 seconds
- ✅ Consider using Redis for session persistence

#### 3. Invalid Response Format

**Error**: USSD shows error or blank screen

**Solutions**:
- ✅ Ensure response is plain text (not JSON)
- ✅ Verify response starts with `CON` or `END`
- ✅ Check for special characters that might break formatting
- ✅ Keep messages under 160 characters per screen

#### 4. Phone Number Format Issues

**Issue**: User lookup fails

**Solutions**:
- ✅ AfricaTalking sends numbers with country code (e.g., `+256700000001`)
- ✅ Store numbers in same format in database
- ✅ Validate phone number format in user creation

### Debug Mode

Enable detailed logging in your backend:

```python
# In app/services/ussd_service.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add in handle_ussd_request
logger.debug(f"Session: {session_id}, Phone: {phone_number}, Text: {text}")
```

### Check Logs

View AfricaTalking request logs:
1. Dashboard → **USSD** → **Logs**
2. Check request/response data
3. Look for error messages

---

## Resources

- [AfricaTalking USSD Documentation](https://developers.africastalking.com/docs/ussd/overview)
- [AfricaTalking API Reference](https://developers.africastalking.com/docs)
- [USSD Best Practices](https://developers.africastalking.com/docs/ussd/best_practices)
- [Python SDK Documentation](https://github.com/AfricasTalkingLtd/africastalking-python)

---

## Support

- **AfricaTalking Support**: support@africastalking.com
- **Community Forum**: [community.africastalking.com](https://community.africastalking.com/)
- **GitHub Issues**: [SusuSave Repository](https://github.com/your-repo/issues)

---

## Next Steps

1. ✅ Set up sandbox account
2. ✅ Configure local environment
3. ✅ Test USSD flows
4. ✅ Add SMS notifications (optional)
5. ✅ Apply for production USSD code
6. ✅ Deploy to production
7. ✅ Monitor and optimize

Happy coding! 🚀

