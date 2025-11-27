# MTN Integration Quick Start

Get MTN USSD, SMS, and MoMo up and running in 10 minutes!

## Quick Setup (Sandbox)

### 1. Install Dependencies

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and update these values:
# MTN_CONSUMER_KEY=J7SH4tF6QqAsa6VYFhtGRwgpvPjYnF9y
# MTN_CONSUMER_SECRET=1gBhKETCBKLMyILR
# USE_MTN_SERVICES=True
```

### 3. Set Up MoMo Sandbox

You'll need your MTN MoMo subscription key from [momodeveloper.mtn.com](https://momodeveloper.mtn.com/)

```bash
# Run the setup script
python setup_mtn_momo.py

# Follow the prompts:
# - Enter your Collection Subscription Key
# - Enter your callback host (e.g., your-ngrok-url.ngrok-free.app)
```

The script will:
- ✅ Create an API user
- ✅ Generate an API key
- ✅ Update your .env file automatically

### 4. Start Ngrok (for local development)

```bash
# In a new terminal
ngrok http 8000
```

Copy the ngrok URL (e.g., `https://abc123.ngrok-free.app`) and update your `.env`:

```bash
MTN_CALLBACK_URL=https://abc123.ngrok-free.app/ussd/callback
```

### 5. Start the Server

```bash
# Start the backend
python -m app.main
```

### 6. Test Your Integration

```bash
# Run the test suite
python test_mtn_integration.py

# Or test individual services:

# Test USSD health
curl http://localhost:8000/ussd/health

# Test USSD callback
curl -X POST http://localhost:8000/ussd/callback \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test123",
    "msisdn": "233240000000",
    "ussdString": "",
    "serviceCode": "*920*55#"
  }'
```

## Common Use Cases

### Send SMS

```python
from app.integrations.mtn_sms_integration import mtn_sms_service

result = mtn_sms_service.send_single_sms(
    phone_number="+233240000000",
    message="Welcome to SusuSave!"
)

print(result)
```

### Request Payment

```python
from app.integrations.mtn_momo_integration import mtn_momo_service

result = mtn_momo_service.request_to_pay(
    phone_number="233240000000",
    amount=50.00,
    reference="PAYMENT001",
    payer_message="Payment for Round 1"
)

print(f"Payment Status: {result['status']}")
print(f"Reference ID: {result['reference_id']}")
```

### Send Payout

```python
result = mtn_momo_service.transfer(
    phone_number="233240000000",
    amount=100.00,
    reference="PAYOUT001",
    payee_message="Your susu payout"
)

print(f"Transfer Status: {result['status']}")
```

### Check Transaction Status

```python
status = mtn_momo_service.get_transaction_status(reference_id)

print(f"Status: {status['status']}")
print(f"Amount: {status['amount']}")
```

## Troubleshooting

### Issue: Authentication Failed

**Solution:**
```bash
# Check your credentials in .env
echo $MTN_CONSUMER_KEY
echo $MTN_CONSUMER_SECRET

# Make sure they match your MTN Developer Portal
```

### Issue: MoMo API Not Working

**Solution:**
```bash
# Re-run MoMo setup
python setup_mtn_momo.py

# Or check your credentials
echo $MTN_MOMO_SUBSCRIPTION_KEY
echo $MTN_MOMO_API_USER
echo $MTN_MOMO_API_KEY
```

### Issue: Callback URL Not Reachable

**Solution:**
```bash
# Check ngrok is running
curl https://your-ngrok-url.ngrok-free.app/ussd/health

# If ngrok URL changed, update .env:
MTN_CALLBACK_URL=https://new-ngrok-url.ngrok-free.app/ussd/callback
```

## Production Checklist

Before going live:

- [ ] Get production credentials from MTN Developer Portal
- [ ] Get production MoMo subscription keys
- [ ] Update .env:
  ```bash
  MTN_ENVIRONMENT=production
  MTN_MOMO_TARGET_ENVIRONMENT=production
  MTN_MOMO_BASE_URL=https://momodeveloper.mtn.com
  ```
- [ ] Set up permanent HTTPS endpoint (not ngrok)
- [ ] Update callback URL in MTN portals
- [ ] Test all integrations thoroughly
- [ ] Set up monitoring and alerts

## Next Steps

- 📖 Read the full [MTN Setup Guide](./MTN_SETUP.md)
- 🔧 Check the [API Documentation](../../docs/API.md)
- 🚀 See [Deployment Guide](../../docs/DEPLOYMENT.md)

## Need Help?

- MTN Developer Portal: https://developers.mtn.com/
- MTN MoMo Docs: https://momodeveloper.mtn.com/docs
- Project Issues: Create an issue on GitHub

