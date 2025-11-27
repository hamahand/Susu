# AfricaTalking USSD Integration for SusuSave

Complete integration with AfricaTalking USSD API for mobile money-based savings groups.

## Overview

This integration enables users to interact with SusuSave through USSD (Unstructured Supplementary Service Data) - the feature that works on any mobile phone without internet or smartphone requirements.

### Features

✅ **USSD Menu System**
- Join savings groups
- Make contributions
- Check balance and status
- View payout information

✅ **SMS Notifications** (Optional)
- Welcome messages
- Payment confirmations
- Payout notifications
- Payment reminders

✅ **Sandbox & Production Ready**
- Test in AfricaTalking sandbox
- Easy switch to production

✅ **Automatic User Creation**
- USSD users auto-created on first dial
- Phone number-based authentication

## Quick Start

### 1. Get AfricaTalking Account

```bash
# Sign up at https://account.africastalking.com/
# Free sandbox account for testing
```

### 2. Install & Configure

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp env.example .env
nano .env  # Add your AT credentials
```

### 3. Setup Local Testing

```bash
# Terminal 1: Start backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Expose with ngrok
ngrok http 8000

# Copy ngrok URL and update in AfricaTalking dashboard
# Callback URL: https://your-ngrok-url.ngrok.io/ussd/callback
```

### 4. Test

```bash
# Option A: Test script
python test_africastalking_ussd.py

# Option B: Web simulator
# AfricaTalking Dashboard → USSD → Simulator

# Option C: Mobile app
# Download AfricaTalking Sandbox app
```

## USSD Menu Flow

```
*384*12345#  (Your USSD code)
│
├─ 1. Join Group
│  └─ Enter Group Code
│     └─ Confirmation + SMS
│
├─ 2. Pay Contribution
│  └─ Select Group
│     └─ Payment Confirmation + SMS
│
├─ 3. Check Balance/Status
│  └─ Display all groups status
│
└─ 4. My Payout Date
   └─ Display payout schedule
```

## Environment Variables

Required variables in `.env`:

```env
# AfricaTalking Configuration
AT_USERNAME=sandbox                 # "sandbox" for testing
AT_API_KEY=atsk_xxxxxxxxxxxxx      # From AT dashboard
AT_ENVIRONMENT=sandbox              # "sandbox" or "production"
AT_USSD_SERVICE_CODE=*384*12345#   # Your assigned code

# Optional: Enable real SMS
ENABLE_REAL_SMS=False              # Set True to send actual SMS
```

## File Structure

```
backend/
├── app/
│   ├── routers/
│   │   └── ussd.py                    # USSD callback endpoint
│   ├── services/
│   │   └── ussd_service.py            # USSD business logic
│   └── integrations/
│       ├── africastalking_integration.py  # AT SDK wrapper
│       └── sms_sender.py              # Unified SMS sender
├── docs/
│   ├── AFRICASTALKING_SETUP.md        # Full setup guide
│   └── USSD_QUICKSTART.md             # Quick start guide
├── test_africastalking_ussd.py        # Test script
└── AFRICASTALKING_CHECKLIST.md        # Integration checklist
```

## API Endpoints

### USSD Callback
```
POST /ussd/callback
```

**Request** (from AfricaTalking):
```
sessionId: string
serviceCode: string
phoneNumber: string (with country code)
text: string (user input, concatenated with *)
```

**Response** (plain text):
```
CON [message]  # Continue session
END [message]  # End session
```

### Health Check
```
GET /ussd/health
```

Returns USSD service status and configuration.

## Testing

### Manual Testing

```bash
# Test callback directly
curl -X POST http://localhost:8000/ussd/callback \
  -d "sessionId=test-123" \
  -d "serviceCode=*384*12345#" \
  -d "phoneNumber=+256700000001" \
  -d "text="

# Expected response: "CON Welcome to SusuSave..."
```

### Automated Testing

```bash
# Run all tests
python test_africastalking_ussd.py test

# Interactive mode
python test_africastalking_ussd.py
```

### Test Scenarios

1. **New user joins group**
   - Dial → 1 → Enter group code → Success

2. **User makes payment**
   - Dial → 2 → Select group → Confirmation

3. **Check status**
   - Dial → 3 → View all groups

4. **Check payout date**
   - Dial → 4 → View payout schedule

## Production Deployment

### 1. Apply for USSD Code

```bash
# In AfricaTalking dashboard:
# 1. Switch to "Live" environment
# 2. USSD → Apply for USSD Code
# 3. Fill application (2-5 business days)
```

### 2. Update Configuration

```env
AT_USERNAME=your_live_username
AT_API_KEY=atsk_live_key_here
AT_ENVIRONMENT=production
AT_USSD_SERVICE_CODE=*920*55#  # Your approved code
ENABLE_REAL_SMS=True
```

### 3. Deploy Backend

```bash
# Deploy to production server with HTTPS
# Update callback URL in AT dashboard
# Example: https://api.sususave.com/ussd/callback
```

### 4. Monitor & Scale

- Enable logging
- Set up error monitoring
- Monitor response times (< 8 seconds required)
- Consider Redis for session storage

## SMS Integration

### Enable SMS

```env
ENABLE_REAL_SMS=True
```

### SMS Types

The system automatically sends:

1. **Welcome SMS** - When joining a group
2. **Payment Confirmation** - After successful payment
3. **Payout Notification** - When receiving payout
4. **Payment Reminder** - For overdue payments

### Custom SMS

```python
from app.integrations.sms_sender import send_sms

send_sms(
    phone_number="+256700000001",
    message="Your custom message"
)
```

## Performance Considerations

- **Response Time**: Must be < 8 seconds (AT timeout)
- **Session Storage**: In-memory dict (dev) → Redis (production)
- **Database**: Optimize queries for speed
- **Error Handling**: Always return valid CON/END response

## Security

- ✅ HTTPS required (production)
- ✅ Phone numbers encrypted in database
- ✅ API keys in environment variables
- ✅ Input validation on all user inputs
- ✅ Session cleanup on completion
- ✅ Rate limiting (via SlowAPI)

## Troubleshooting

### Common Issues

**"Callback URL not reachable"**
```bash
# Check ngrok is running
# Verify HTTPS URL
# Test manually with curl
```

**"Session timeout"**
```bash
# Ensure response < 8 seconds
# Check for blocking operations
# Review error logs
```

**"SMS not sending"**
```bash
# Verify ENABLE_REAL_SMS=True
# Check AT credentials
# Review account balance (production)
```

### Debug Logging

```python
# Add to ussd_service.py
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Log all requests
logger.debug(f"USSD Request - Session: {session_id}, Text: {text}")
```

### View Logs

```bash
# Backend logs
tail -f app.log

# SMS logs (mock)
tail -f sms_logs.txt

# AfricaTalking dashboard
# Dashboard → USSD → Logs
```

## Resources

### Documentation
- [Quick Start Guide](docs/USSD_QUICKSTART.md)
- [Full Setup Guide](docs/AFRICASTALKING_SETUP.md)
- [Integration Checklist](AFRICASTALKING_CHECKLIST.md)

### AfricaTalking
- [USSD Documentation](https://developers.africastalking.com/docs/ussd/overview)
- [Python SDK](https://github.com/AfricasTalkingLtd/africastalking-python)
- [API Reference](https://developers.africastalking.com/docs)
- [Best Practices](https://developers.africastalking.com/docs/ussd/best_practices)

### Support
- AfricaTalking Support: support@africastalking.com
- Community Forum: [community.africastalking.com](https://community.africastalking.com/)

## Contributing

When adding new USSD features:

1. Update menu in `ussd_service.py`
2. Add test scenarios in `test_africastalking_ussd.py`
3. Update documentation
4. Test in sandbox before production
5. Keep messages < 160 characters
6. Ensure response time < 8 seconds

## License

Same as main SusuSave project (see LICENSE file).

---

**Ready to go live?** Follow the [Production Deployment](#production-deployment) section above!

For questions, check the [troubleshooting guide](docs/AFRICASTALKING_SETUP.md#troubleshooting) or open an issue.

