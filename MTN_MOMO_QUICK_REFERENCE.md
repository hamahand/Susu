# MTN MoMo Quick Reference

**Official Testing Guide**: [MTN MoMo Testing Documentation](https://momodeveloper.mtn.com/api-documentation/testing)

---

## Quick Links

| Resource | URL |
|----------|-----|
| **Testing Guide** | https://momodeveloper.mtn.com/api-documentation/testing |
| **Developer Portal** | https://momodeveloper.mtn.com/ |
| **Collections API** | https://momodeveloper.mtn.com/products/collections |
| **Disbursements API** | https://momodeveloper.mtn.com/products/disbursements |

---

## Setup

### 1. Get Subscription Keys

```bash
# Visit MTN Developer Portal
https://momodeveloper.mtn.com/

# Subscribe to:
- Collections API (for receiving payments)
- Disbursements API (for sending payouts)

# Copy subscription keys
```

### 2. Run Setup Script

```bash
cd /Users/maham/susu/backend
python setup_mtn_momo.py
# Enter your subscription key when prompted
```

### 3. Configure Environment

Edit `backend/.env`:
```env
MTN_MOMO_SUBSCRIPTION_KEY=your-key-here
MTN_MOMO_TARGET_ENVIRONMENT=sandbox
MTN_MOMO_BASE_URL=https://sandbox.momodeveloper.mtn.com
MTN_MOMO_CURRENCY=GHS
```

---

## Testing

### Run Test Script

```bash
cd /Users/maham/susu/backend
python test_mtn_momo_payment.py
```

**Test Menu**:
1. Test User Payment
2. Test Admin Request Payment  
3. Test Check Payment Status
4. Test Payout
5. Run All Tests

### Test Phone Numbers

**Format**: `233XXXXXXXXX` (Ghana)  
**Example**: `233240000000`

**Sandbox Behavior**:
- All transactions are simulated
- No real money transferred
- Instant completion
- Free testing

---

## API Endpoints (Your Backend)

### Request Payment (Collections)
```bash
POST /payments/admin/request-payment
{
  "payment_id": 1,
  "phone_number": "+233240000000"
}
```

### Check Payment Status
```bash
GET /payments/{payment_id}/status
```

### User Pays Own Payment
```bash
POST /payments/{payment_id}/pay-now
```

---

## Common Commands

```bash
# Setup MTN MoMo
cd backend && python setup_mtn_momo.py

# Run tests
cd backend && python test_mtn_momo_payment.py

# Check configuration
cd backend && python verify_ussd_setup.py

# Start backend
cd backend && python -m uvicorn app.main:app --reload

# View logs
docker logs sususave_backend --tail 50
```

---

## Sandbox vs Production

### Sandbox (Current)
```env
MTN_MOMO_TARGET_ENVIRONMENT=sandbox
MTN_MOMO_BASE_URL=https://sandbox.momodeveloper.mtn.com
```
- Free testing
- Simulated transactions
- Instant results
- Test phone numbers

### Production (When Ready)
```env
MTN_MOMO_TARGET_ENVIRONMENT=production
MTN_MOMO_BASE_URL=https://momodeveloper.mtn.com
```
- Real money transfers
- Real phone numbers
- Actual processing time
- Production credentials needed

---

## Troubleshooting

### Error: "Invalid subscription key"
✅ **Solution**: Check subscription key in `.env`  
✅ Verify you subscribed to Collections/Disbursements

### Error: "MSISDN format error"
✅ **Solution**: Use format `233XXXXXXXXX` (no + or spaces)

### Transaction Status "PENDING"
✅ **Sandbox**: Should complete instantly  
✅ **Production**: Wait up to 30 seconds

### Setup Script Fails
✅ **Solution**: Re-run with correct subscription key:
```bash
cd backend
python setup_mtn_momo.py
```

---

## Documentation

- `MTN_MOMO_TESTING_GUIDE.md` - Complete testing guide
- `MTN_MOMO_SANDBOX_SETUP.md` - Detailed setup
- `MTN_MOMO_QUICK_START.md` - 10-minute setup
- `backend/test_mtn_momo_payment.py` - Test script
- [Official MTN Docs](https://momodeveloper.mtn.com/api-documentation/testing)

---

## Support

**MTN Support**: support@momo.mtn.com  
**Developer Portal**: https://momodeveloper.mtn.com/support

---

**Last Updated**: October 23, 2025  
**Official Reference**: [MTN MoMo Testing](https://momodeveloper.mtn.com/api-documentation/testing)

