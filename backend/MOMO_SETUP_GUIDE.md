# MTN MoMo Setup Guide for SusuSave

## What You're Building
Your SusuSave app needs to:
- ✅ Collect monthly contributions automatically
- ✅ Send payouts to susu winners
- ✅ Process transactions server-to-server

## Authentication Method
You'll use **API User + API Key** authentication (NOT bc-authorize).

## Step-by-Step Setup

### 1. Get Your Subscription Key

1. Visit [https://momodeveloper.mtn.com/](https://momodeveloper.mtn.com/)
2. Sign up (or sign in)
3. Go to **Products** → Subscribe to:
   - **Collection** (for receiving payments)
   - **Disbursement** (for sending payouts)
4. Go to your **Profile** → Copy your **Primary Key** (Subscription Key)

### 2. Run Setup Script

```bash
cd /Users/maham/susu/backend
source venv/bin/activate
python setup_mtn_momo.py
```

**Enter when prompted:**
- **Subscription Key**: [paste your Primary Key from step 1]
- **Callback Host**: `76280680be24.ngrok-free.app`

This creates:
- ✅ API User ID (UUID)
- ✅ API Key
- ✅ Updates your `.env` file

### 3. Test Your Setup

```bash
python test_mtn_integration.py
```

Should show:
```
💰 MoMo Configuration:
   API_USER: ✅ CONFIGURED
   API_KEY: ✅ CONFIGURED
```

## API Endpoints You'll Use

### For Collections (Receiving Payments)

**Request Payment from User:**
```
POST /collection/v1_0/requesttopay
Headers:
  - Authorization: Bearer {token}
  - X-Reference-Id: {UUID}
  - X-Target-Environment: sandbox
  - Ocp-Apim-Subscription-Key: {your_key}
Body:
{
  "amount": "50",
  "currency": "GHS",
  "externalId": "SUSU_PAYMENT_001",
  "payer": {
    "partyIdType": "MSISDN",
    "partyId": "233240000000"
  },
  "payerMessage": "Susu monthly contribution",
  "payeeNote": "Thank you!"
}
```

**Check Payment Status:**
```
GET /collection/v1_0/requesttopay/{referenceId}
```

### For Disbursements (Sending Payouts)

**Send Money to Winner:**
```
POST /disbursement/v1_0/transfer
Headers:
  - Authorization: Bearer {token}
  - X-Reference-Id: {UUID}
  - X-Target-Environment: sandbox
Body:
{
  "amount": "500",
  "currency": "GHS",
  "externalId": "SUSU_PAYOUT_001",
  "payee": {
    "partyIdType": "MSISDN",
    "partyId": "233240000000"
  },
  "payerMessage": "Susu payout",
  "payeeNote": "Congratulations on your payout!"
}
```

## You DON'T Need bc-authorize Because:

- ❌ **bc-authorize** is for user-initiated OAuth flows
- ❌ Requires users to approve each transaction on their phone
- ❌ Adds unnecessary complexity for automated transactions

- ✅ **API User auth** is perfect for server-side automation
- ✅ Transactions happen automatically on schedule
- ✅ Simpler, more reliable for susu operations

## How It Works in Your App

```python
# When a user's payment is due:
from app.integrations.mtn_momo_integration import mtn_momo_service

# Request payment from user
result = mtn_momo_service.request_to_pay(
    phone_number="233240000000",
    amount=50.00,
    reference="SUSU_ROUND1_USER123",
    payer_message="Monthly contribution - Round 1"
)

# User receives prompt on their phone to approve
# Check status later
status = mtn_momo_service.get_transaction_status(result['reference_id'])

if status['status'] == 'successful':
    # Mark payment as received
    # Update user's contribution record
```

```python
# When it's time to send payout to winner:
payout = mtn_momo_service.transfer(
    phone_number="233240000000",
    amount=500.00,
    reference="SUSU_PAYOUT_ROUND1",
    payee_message="Congratulations! Your susu payout for Round 1"
)
```

## Production Checklist

Before going live:

- [ ] Get production subscription keys
- [ ] Update environment:
  ```bash
  MTN_MOMO_TARGET_ENVIRONMENT=production
  MTN_MOMO_BASE_URL=https://momodeveloper.mtn.com
  ```
- [ ] Test with real transactions (small amounts)
- [ ] Set up transaction monitoring
- [ ] Implement webhook handlers for payment notifications
- [ ] Add retry logic for failed transactions

## Useful Links

- [MTN MoMo Developer Portal](https://momodeveloper.mtn.com/)
- [Collection API Docs](https://momodeveloper.mtn.com/API-collections#api=collection)
- [Disbursement API Docs](https://momodeveloper.mtn.com/API-collections#api=disbursement)
- [Sandbox Provisioning API](https://momodeveloper.mtn.com/API-collections#api=sandbox-provisioning-api)

## Need Help?

Run the test script to verify everything:
```bash
python test_mtn_integration.py
```

Check logs in your terminal for detailed error messages.

