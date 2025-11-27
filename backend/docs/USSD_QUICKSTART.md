# USSD Quick Start Guide

Get your AfricaTalking USSD integration running in under 10 minutes!

## Quick Setup (Development)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Get AfricaTalking Credentials

1. Go to [AfricaTalking](https://account.africastalking.com/auth/register)
2. Sign up (free)
3. Go to **Settings** → **API Key** → Generate
4. Copy your API key

### 3. Configure Environment

```bash
# Create .env file
cp env.example .env

# Edit .env
nano .env
```

Add your credentials:
```env
AT_USERNAME=sandbox
AT_API_KEY=atsk_your_key_here
AT_ENVIRONMENT=sandbox
```

### 4. Start Backend

```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 5. Expose with ngrok

In a new terminal:
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Expose port 8000
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 6. Configure AfricaTalking

1. Go to AfricaTalking Dashboard → **USSD** → **Create Channel**
2. Set Callback URL: `https://abc123.ngrok.io/ussd/callback`
3. Copy your assigned USSD code (e.g., `*384*12345#`)

### 7. Test!

**Option A: Web Simulator**
- Dashboard → **USSD** → **Simulator**
- Enter test phone: `+254700000001`
- Dial your code

**Option B: Test Script**
```bash
python test_africastalking_ussd.py
```

**Option C: Mobile App**
- Download AfricaTalking Sandbox app
- Dial your USSD code

## USSD Menu Structure

```
*384*12345#
├── 1. Join Group
│   └── Enter Group Code → Success/Error
├── 2. Pay Contribution
│   └── Select Group → Payment Confirmation
├── 3. Check Balance/Status
│   └── Display Status
└── 4. My Payout Date
    └── Display Payout Info
```

## Sample Interaction

```bash
# User dials *384*12345#
> CON Welcome to SusuSave
  1. Join Group
  2. Pay Contribution
  3. Check Balance/Status
  4. My Payout Date

# User enters: 1
> CON Enter Group Code (e.g., SUSU1234):

# User enters: SUSU5678
> END Success! You joined Family Savings.
  Position: 3
  Contribution: GHS 50
  You will receive an SMS with details.
```

## Testing Tips

### Create Test Group

Use the API or web interface to create a test group:

```bash
# First, get auth token (register/login)
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+254700000001",
    "name": "Test User",
    "password": "password123"
  }'

# Create a group
curl -X POST http://localhost:8000/groups/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Group",
    "contribution_amount": 50,
    "num_cycles": 10,
    "frequency": "MONTHLY"
  }'

# Note the group_code from response
```

### Test Join via USSD

1. Dial USSD code
2. Select "1" (Join Group)
3. Enter the group code you created
4. Verify success message

## Common Issues

### "Callback URL not reachable"
- ✅ Check ngrok is running
- ✅ Verify backend is running
- ✅ Use HTTPS URL from ngrok

### "Session timeout"
- ✅ Ensure responses start with `CON` or `END`
- ✅ Check server response time < 8 seconds
- ✅ Look at backend logs for errors

### "No response" 
- ✅ Check backend logs
- ✅ Verify endpoint is `/ussd/callback`
- ✅ Test manually: `curl -X POST https://your-url/ussd/callback -d "sessionId=test&serviceCode=*384*12345#&phoneNumber=+254700000001&text="`

## Next Steps

- ✅ Test all menu options
- ✅ Create test groups and memberships
- ✅ Test payment flow
- ✅ Enable SMS notifications (set `use_africastalking=True`)
- ✅ Add error handling for edge cases
- ✅ Apply for production USSD code

## Resources

- [Full Setup Guide](./AFRICASTALKING_SETUP.md)
- [AfricaTalking Docs](https://developers.africastalking.com/docs/ussd/overview)
- [API Documentation](../API.md)

---

**Need Help?** Check the [troubleshooting section](./AFRICASTALKING_SETUP.md#troubleshooting) in the full setup guide.

