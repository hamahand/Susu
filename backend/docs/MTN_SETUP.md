# MTN Integration Setup Guide

This guide will help you set up MTN USSD, SMS, and Mobile Money (MoMo) integration for SusuSave.

## Overview

SusuSave now supports MTN's services in Ghana:
- **USSD**: Interactive menu-based services (*920*55#)
- **SMS**: Send notifications and messages to users
- **MoMo**: Process payments (collections) and payouts (disbursements)

## Prerequisites

1. MTN Developer Account: [https://developers.mtn.com/](https://developers.mtn.com/)
2. MTN MoMo Developer Account: [https://momodeveloper.mtn.com/](https://momodeveloper.mtn.com/)
3. A public callback URL (use ngrok for development)

## Step 1: MTN Developer Portal Setup

### 1.1 Create Developer Account

1. Go to [https://developers.mtn.com/](https://developers.mtn.com/)
2. Click "Register" and create your account
3. Verify your email address
4. Log in to your account

### 1.2 Create Application

1. Navigate to "My Apps" or "Applications"
2. Click "Create App"
3. Fill in the details:
   - **App Name**: SusuSavinggh (or your app name)
   - **Description**: Susu savings platform for Ghana
   - **Entity Name**: Your company/business name
   - **Country**: Ghana
   - **Contact Number**: Your phone number
   - **Callback URL**: `https://76280680be24.ngrok-free.app/ussd/callback`
   - **Channels**: Select SMS, Mobile App, USSD, Other External

4. Submit the application

### 1.3 Get API Credentials

After creating your app, you'll receive:
- **Consumer Key**: `J7SH4tF6QqAsa6VYFhtGRwgpvPjYnF9y`
- **Consumer Secret**: `1gBhKETCBKLMyILR`

**IMPORTANT**: Keep these credentials secure! Never commit them to version control.

### 1.4 Subscribe to Products

Subscribe to the following products:
1. **USSD Interface** - For USSD services
2. **SMS API** (any version) - For sending SMS
3. **MTN Customer KYC API v1** - For user verification (Ghana compliance)
4. Check that all products are approved for Ghana

## Step 2: MTN MoMo Setup

### 2.1 MoMo Developer Account

1. Go to [https://momodeveloper.mtn.com/](https://momodeveloper.mtn.com/)
2. Register for an account
3. Log in and subscribe to products:
   - **Collection**: For receiving payments from users
   - **Disbursement**: For sending money to users

### 2.2 Get Subscription Keys

After subscribing to products, you'll get:
- **Collection Subscription Key** (Ocp-Apim-Subscription-Key)
- **Disbursement Subscription Key**

### 2.3 Sandbox Setup (for Testing)

For sandbox testing, you need to:

1. **Create API User**: Run the setup script (see below)
2. **Create API Key**: The script will generate this for you

#### Using the Setup Script

We've created a helper script to set up MoMo sandbox:

```bash
cd backend
python setup_mtn_momo.py
```

This script will:
1. Create an API user for sandbox
2. Generate an API key
3. Update your `.env` file with the credentials

Alternatively, manually create API user:

```bash
# Create API User
curl -X POST \
  https://sandbox.momodeveloper.mtn.com/v1_0/apiuser \
  -H 'X-Reference-Id: YOUR-UUID-HERE' \
  -H 'Ocp-Apim-Subscription-Key: YOUR-SUBSCRIPTION-KEY' \
  -H 'Content-Type: application/json' \
  -d '{"providerCallbackHost": "your-callback-host"}'

# Create API Key
curl -X POST \
  https://sandbox.momodeveloper.mtn.com/v1_0/apiuser/YOUR-UUID-HERE/apikey \
  -H 'Ocp-Apim-Subscription-Key: YOUR-SUBSCRIPTION-KEY'
```

## Step 3: MTN KYC Setup

### 3.1 KYC Verification (Ghana Compliance)

SusuSave uses MTN's KYC API to verify users in compliance with Ghana's financial regulations.

**What is verified:**
- Valid MTN Ghana phone number
- Active MTN Mobile Money account

**Setup:**
1. Subscribe to **MTN Customer KYC API v1** in the developer portal
2. No additional credentials needed (uses same OAuth as other APIs)
3. KYC verification happens automatically during user registration

**Testing:**
```bash
# Test KYC integration
python test_mtn_kyc.py
```

**See detailed documentation:** [KYC_IMPLEMENTATION.md](./KYC_IMPLEMENTATION.md)

## Step 4: Configure Environment Variables

### 4.1 Create .env file

Copy the example file:
```bash
cd backend
cp env.example .env
```

### 4.2 Update MTN Configuration

Edit `.env` and update these values:

```bash
# MTN API Configuration
MTN_CONSUMER_KEY=J7SH4tF6QqAsa6VYFhtGRwgpvPjYnF9y
MTN_CONSUMER_SECRET=1gBhKETCBKLMyILR
MTN_ENVIRONMENT=sandbox  # Change to "production" when ready
MTN_BASE_URL=https://api.mtn.com/v1
MTN_USSD_SERVICE_CODE=*920*55#
MTN_CALLBACK_URL=https://76280680be24.ngrok-free.app/ussd/callback

# MTN Mobile Money Configuration
MTN_MOMO_SUBSCRIPTION_KEY=your-collection-subscription-key
MTN_MOMO_API_USER=generated-by-setup-script
MTN_MOMO_API_KEY=generated-by-setup-script
MTN_MOMO_TARGET_ENVIRONMENT=sandbox
MTN_MOMO_BASE_URL=https://sandbox.momodeveloper.mtn.com
MTN_MOMO_CURRENCY=GHS

# Enable MTN Services
ENABLE_MTN_USSD=True
ENABLE_MTN_SMS=True
ENABLE_MTN_MOMO=True
USE_MTN_SERVICES=True  # Set to True to use MTN instead of AfricasTalking

# MTN KYC Configuration (Ghana Compliance)
ENABLE_MTN_KYC=True
MTN_KYC_BASE_URL=https://api.mtn.com/v1
REQUIRE_KYC_FOR_PAYMENTS=True
```

## Step 4: Set Up Ngrok (for Development)

MTN needs a public HTTPS callback URL. Use ngrok for local development:

### 4.1 Install Ngrok

```bash
# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

### 4.2 Start Ngrok

```bash
ngrok http 8000
```

You'll get a URL like: `https://76280680be24.ngrok-free.app`

### 4.3 Update Callback URL

Update your `.env` file with the ngrok URL:
```bash
MTN_CALLBACK_URL=https://your-ngrok-url.ngrok-free.app/ussd/callback
```

Also update the callback URL in:
1. MTN Developer Portal (your app settings)
2. MTN MoMo API user (if you created it manually)

## Step 5: Testing

### 5.1 Test KYC Integration

First, test the KYC verification:

```bash
python test_mtn_kyc.py
```

This will test:
- OAuth token retrieval
- Phone number verification
- MoMo account validation
- Full KYC verification flow

### 5.2 Test USSD Integration

1. Start your backend server:
   ```bash
   cd backend
   source venv/bin/activate
   python -m app.main
   ```

2. Test the health endpoint:
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
     "service_code": "*920*55#",
     "callback_url": "https://your-ngrok-url.ngrok-free.app/ussd/callback"
   }
   ```

3. Test USSD callback:
   ```bash
   curl -X POST http://localhost:8000/ussd/callback \
     -H "Content-Type: application/json" \
     -d '{
       "sessionId": "test123",
       "msisdn": "233240000000",
       "ussdString": "",
       "serviceCode": "*920*55#"
     }'
   ```

### 5.2 Test SMS Integration

Create a test script `test_mtn_sms.py`:

```python
from app.integrations.mtn_sms_integration import mtn_sms_service

result = mtn_sms_service.send_single_sms(
    phone_number="+233240000000",
    message="Test SMS from SusuSave"
)

print(result)
```

Run it:
```bash
python test_mtn_sms.py
```

### 5.3 Test MoMo Integration

Create a test script `test_mtn_momo.py`:

```python
from app.integrations.mtn_momo_integration import mtn_momo_service

# Test account validation
result = mtn_momo_service.validate_account("+233240000000")
print("Validation:", result)

# Test payment request
result = mtn_momo_service.request_to_pay(
    phone_number="233240000000",
    amount=10.00,
    reference="TEST001",
    payer_message="Test payment"
)
print("Payment:", result)

# Check transaction status
if result.get("reference_id"):
    status = mtn_momo_service.get_transaction_status(result["reference_id"])
    print("Status:", status)
```

Run it:
```bash
python test_mtn_momo.py
```

## Step 6: Production Deployment

### 6.1 Production Checklist

Before going to production:

- [ ] Get production credentials from MTN Developer Portal
- [ ] Get production MoMo subscription keys
- [ ] Set up a permanent public HTTPS URL (not ngrok)
- [ ] Update callback URLs in MTN portals
- [ ] Update environment variables:
  ```bash
  MTN_ENVIRONMENT=production
  MTN_MOMO_TARGET_ENVIRONMENT=production
  MTN_MOMO_BASE_URL=https://momodeveloper.mtn.com
  ```
- [ ] Test all integrations thoroughly
- [ ] Set up monitoring and logging
- [ ] Implement webhook verification (security)

### 6.2 Security Best Practices

1. **Never commit credentials**: Use environment variables
2. **Verify webhook signatures**: Implement request validation
3. **Use HTTPS only**: Never expose credentials over HTTP
4. **Rotate keys regularly**: Update API keys periodically
5. **Monitor API usage**: Track for unusual activity
6. **Implement rate limiting**: Protect against abuse
7. **Log all transactions**: Keep audit trail

## Troubleshooting

### Common Issues

#### 1. Authentication Failed

**Error**: "MTN authentication failed"

**Solution**:
- Verify your consumer key and secret are correct
- Check that your app is approved in MTN Developer Portal
- Ensure you're using the correct environment (sandbox/production)

#### 2. USSD Not Working

**Error**: "Invalid service code"

**Solution**:
- Verify your USSD code matches what's registered with MTN
- Check that your callback URL is accessible
- Test callback URL with curl

#### 3. MoMo Requests Failing

**Error**: "Failed to obtain MTN MoMo token"

**Solution**:
- Verify subscription key is correct
- Ensure API user and API key are properly configured
- For sandbox, make sure you created the API user
- Check that you subscribed to Collection/Disbursement products

#### 4. Callback URL Not Reachable

**Error**: MTN cannot reach your callback

**Solution**:
- If using ngrok, ensure it's running
- Check firewall settings
- Verify URL is publicly accessible: `curl https://your-url/ussd/health`
- Update callback URL in MTN portal if ngrok URL changed

### Getting Help

1. **MTN Developer Portal**: [https://developers.mtn.com/](https://developers.mtn.com/)
2. **MTN MoMo Docs**: [https://momodeveloper.mtn.com/docs](https://momodeveloper.mtn.com/docs)
3. **MTN Support**: Contact support through developer portal
4. **Project Issues**: Create an issue in the GitHub repository

## API Reference

### USSD Callback Format

**MTN Format** (JSON):
```json
{
  "sessionId": "unique-session-id",
  "msisdn": "233240000000",
  "ussdString": "1*2*3",
  "serviceCode": "*920*55#"
}
```

**Response Format**:
```
CON Welcome to SusuSave
1. Join Group
2. My Groups

END Thank you for using SusuSave!
```

### SMS API

**Send SMS**:
```python
from app.integrations.mtn_sms_integration import mtn_sms_service

result = mtn_sms_service.send_single_sms(
    phone_number="+233240000000",
    message="Your message here",
    sender_id="SusuSave"
)
```

### MoMo API

**Request Payment**:
```python
result = mtn_momo_service.request_to_pay(
    phone_number="233240000000",
    amount=50.00,
    reference="ORDER123",
    payer_message="Payment for Round 1"
)
```

**Send Payout**:
```python
result = mtn_momo_service.transfer(
    phone_number="233240000000",
    amount=100.00,
    reference="PAYOUT001",
    payee_message="Your susu payout"
)
```

**Check Status**:
```python
status = mtn_momo_service.get_transaction_status(reference_id)
```

## Next Steps

1. Complete the setup steps above
2. Test all integrations in sandbox
3. Integrate with your business logic
4. Perform user acceptance testing
5. Deploy to production

For more information, see:
- [USSD Quick Start](./USSD_QUICKSTART.md)
- [API Documentation](../docs/API.md)
- [Deployment Guide](../docs/DEPLOYMENT.md)

