# MTN MoMo Testing Guide

**Official Documentation**: [MTN MoMo Testing](https://momodeveloper.mtn.com/api-documentation/testing)

---

## Overview

This guide covers testing your MTN Mobile Money integration using the MTN MoMo Sandbox environment.

## Official MTN Testing Documentation

MTN provides comprehensive testing documentation at:  
**https://momodeveloper.mtn.com/api-documentation/testing**

This page includes:
- Sandbox environment details
- Test phone numbers
- Test scenarios
- Expected responses
- Common testing workflows

---

## MTN MoMo Sandbox Setup

### Prerequisites

1. **MTN MoMo Developer Account**
   - Sign up at https://momodeveloper.mtn.com/
   - Verify your email

2. **Subscribe to Products**
   - Collections API (for receiving payments)
   - Disbursements API (for sending payouts)

3. **Get Subscription Keys**
   - Go to Products → Collections → Subscribe
   - Go to Products → Disbursements → Subscribe
   - Copy your subscription keys

### Running the Setup Script

Your project includes an automated setup script:

```bash
cd /Users/maham/susu/backend
python setup_mtn_momo.py
```

This script will:
1. Prompt for your subscription key
2. Create API user
3. Generate API key
4. Save credentials to `.env`
5. Test the connection

---

## Test Credentials

### Sandbox Environment

```env
MTN_MOMO_TARGET_ENVIRONMENT=sandbox
MTN_MOMO_BASE_URL=https://sandbox.momodeveloper.mtn.com
MTN_MOMO_CURRENCY=GHS
```

### Test Phone Numbers

According to the [official MTN testing documentation](https://momodeveloper.mtn.com/api-documentation/testing):

**For Ghana (GHS)**:
- Use valid Ghana phone numbers starting with `233`
- Format: `233XXXXXXXXX` (without + sign)
- Example: `233240000000`

**Sandbox Behavior**:
- All transactions in sandbox are simulated
- No real money is transferred
- Transactions complete instantly
- Use for testing all payment flows

---

## Testing Payment Collection

### Test Scenario 1: Request Payment from User

**Endpoint**: Request to Pay (Collections)

```bash
# Test with your backend
curl -X POST http://localhost:8000/payments/admin/request-payment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "payment_id": 1,
    "phone_number": "+233240000000"
  }'
```

**Expected Flow**:
1. Backend sends request to MTN MoMo API
2. MTN returns transaction reference ID
3. In production: User receives prompt on phone
4. In sandbox: Transaction auto-completes
5. Backend can check status

### Test Scenario 2: Check Payment Status

```bash
curl -X GET http://localhost:8000/payments/1/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Possible Statuses**:
- `PENDING` - Payment initiated
- `SUCCESSFUL` - Payment completed
- `FAILED` - Payment rejected

---

## Testing Payouts (Disbursements)

### Test Scenario: Send Payout to Winner

```python
# Using the MTN MoMo integration directly
from app.integrations.mtn_momo_integration import mtn_momo_service

result = mtn_momo_service.transfer(
    phone_number="233240000000",
    amount=200.00,
    reference="PAYOUT_ROUND1",
    payee_message="Congratulations! Your susu payout"
)

print(f"Status: {result['status']}")
print(f"Reference: {result['reference_id']}")
```

**Expected Response**:
```json
{
  "status": "success",
  "reference_id": "abc123-def456-ghi789",
  "message": "Transfer initiated"
}
```

---

## Testing with Your Test Script

Your project includes a comprehensive test script:

```bash
cd /Users/maham/susu/backend
python test_mtn_momo_payment.py
```

**Interactive Test Menu**:
```
MTN MoMo Payment Testing
========================
1. Test User Payment (User pays their contribution)
2. Test Admin Request Payment (Admin requests payment from user)
3. Test Check Payment Status
4. Test Payout (Disbursement)
5. Run All Tests
0. Exit

Choose an option:
```

---

## MTN MoMo Sandbox Test Scenarios

Based on the [official documentation](https://momodeveloper.mtn.com/api-documentation/testing):

### Collections (Receiving Payments)

**Test Case 1: Successful Payment**
```json
{
  "amount": "50.00",
  "currency": "GHS",
  "externalId": "test-payment-123",
  "payer": {
    "partyIdType": "MSISDN",
    "partyId": "233240000000"
  },
  "payerMessage": "Payment for Round 1",
  "payeeNote": "Group: Family Susu"
}
```

**Expected Result**: `SUCCESSFUL`

**Test Case 2: Insufficient Funds**
- Test behavior when user has insufficient balance
- Expected Result: `FAILED`

**Test Case 3: Expired Request**
- Test timeout scenarios
- Expected Result: `FAILED`

### Disbursements (Sending Payouts)

**Test Case 1: Successful Payout**
```json
{
  "amount": "200.00",
  "currency": "GHS",
  "externalId": "payout-round1-123",
  "payee": {
    "partyIdType": "MSISDN",
    "partyId": "233240000000"
  },
  "payerMessage": "Susu payout - Round 1",
  "payeeNote": "Congratulations!"
}
```

**Expected Result**: `SUCCESSFUL`

---

## Monitoring and Debugging

### Check Transaction Status

```python
from app.integrations.mtn_momo_integration import mtn_momo_service

# For collections (payments received)
status = mtn_momo_service.get_transaction_status(reference_id)

print(f"Status: {status['status']}")
print(f"Amount: {status['amount']}")
print(f"Currency: {status['currency']}")
```

### View Transaction History

Check your MTN MoMo Developer Dashboard:
1. Login to https://momodeveloper.mtn.com/
2. Go to **Sandbox** → **Transactions**
3. View all test transactions
4. Check request/response details

### Enable Debug Logging

Edit your `.env` file:
```env
# Enable detailed logging
LOG_LEVEL=DEBUG
```

Then check logs:
```bash
# If using Docker
docker logs sususave_backend --tail 100

# If running directly
tail -f app.log
```

---

## Common Test Scenarios for SusuSave

### Scenario 1: Member Makes Payment

**Flow**:
1. Member sees unpaid contribution in dashboard
2. Clicks "Pay Now" button
3. Backend calls MTN MoMo Collections API
4. MTN initiates payment request
5. Member approves on phone (sandbox: auto-approved)
6. Backend checks status and updates database
7. Dashboard shows payment as complete

**Test Command**:
```bash
cd backend
python test_mtn_momo_payment.py
# Select option 1: Test User Payment
```

### Scenario 2: Admin Requests Payment

**Flow**:
1. Admin sees member with unpaid contribution
2. Admin clicks "Request Payment" button
3. Backend calls MTN MoMo Collections API with member's phone
4. MTN sends payment request to member's phone
5. Member approves (sandbox: auto-approved)
6. Payment status updates
7. Dashboard refreshes

**Test Command**:
```bash
cd backend
python test_mtn_momo_payment.py
# Select option 2: Test Admin Request Payment
```

### Scenario 3: Automatic Payout to Winner

**Flow**:
1. Round completes (all members paid)
2. System identifies winner for this round
3. Backend calls MTN MoMo Disbursements API
4. MTN sends money to winner's MoMo account
5. Winner receives SMS notification
6. Database updates payout status

**Test Command**:
```bash
cd backend
python test_mtn_momo_payment.py
# Select option 4: Test Payout
```

---

## Validation and Error Handling

### Phone Number Validation

```python
# Valid formats
"233240000000"    # ✅ Correct
"+233240000000"   # ✅ Correct (+ removed automatically)
"0240000000"      # ✅ Correct (converted to 233240000000)

# Invalid formats
"240000000"       # ❌ Missing country code
"233-24-000-0000" # ❌ Contains dashes
"233 24 000 0000" # ❌ Contains spaces
```

### Error Responses

**Common Errors**:

1. **Invalid Subscription Key**
   ```json
   {
     "error": "Access denied due to invalid subscription key"
   }
   ```
   **Solution**: Check your subscription key in `.env`

2. **Invalid Phone Number**
   ```json
   {
     "error": "Invalid MSISDN format"
   }
   ```
   **Solution**: Ensure phone number format is correct (233XXXXXXXXX)

3. **Insufficient Permissions**
   ```json
   {
     "error": "Not authorized"
   }
   ```
   **Solution**: Ensure you've subscribed to the product (Collections/Disbursements)

4. **Duplicate Transaction**
   ```json
   {
     "error": "Duplicate reference"
   }
   ```
   **Solution**: Use unique reference ID for each transaction

---

## Integration Testing Checklist

### Collections API Testing

- [ ] **Basic Payment Request**
  - [ ] Create payment request
  - [ ] Verify reference ID returned
  - [ ] Check transaction status
  - [ ] Verify amount and currency

- [ ] **Payment Status Checking**
  - [ ] Check status immediately after request
  - [ ] Check status after delay
  - [ ] Handle pending status
  - [ ] Handle successful status
  - [ ] Handle failed status

- [ ] **Error Scenarios**
  - [ ] Invalid phone number
  - [ ] Invalid amount (negative, zero)
  - [ ] Missing required fields
  - [ ] Duplicate reference ID

### Disbursements API Testing

- [ ] **Basic Payout**
  - [ ] Create payout request
  - [ ] Verify reference ID returned
  - [ ] Check transaction status
  - [ ] Verify recipient received notification

- [ ] **Account Validation**
  - [ ] Validate recipient account exists
  - [ ] Check account is active
  - [ ] Verify KYC status (if required)

- [ ] **Error Scenarios**
  - [ ] Invalid recipient phone
  - [ ] Insufficient balance (provider side)
  - [ ] Invalid amount

---

## Switching to Production

### Prerequisites

1. **Complete Sandbox Testing**
   - All test scenarios pass
   - Error handling verified
   - Integration stable

2. **Get Production Credentials**
   - Apply for production access on MTN MoMo portal
   - Wait for approval (can take days/weeks)
   - Receive production subscription keys

3. **Update Configuration**

Edit `.env`:
```env
MTN_MOMO_TARGET_ENVIRONMENT=production
MTN_MOMO_BASE_URL=https://momodeveloper.mtn.com
MTN_MOMO_SUBSCRIPTION_KEY=your-production-key
```

4. **Re-run Setup**
```bash
cd backend
python setup_mtn_momo.py
# Use production subscription key when prompted
```

5. **Test with Small Amounts**
   - Start with real but small transactions
   - Verify money flows correctly
   - Monitor for errors

6. **Go Live**
   - Full testing with real users
   - Monitor transaction volume
   - Set up alerts for failures

---

## Monitoring Production

### Key Metrics to Track

1. **Transaction Success Rate**
   - Target: >95% success rate
   - Alert if drops below 90%

2. **Response Times**
   - Target: <3 seconds average
   - Alert if exceeds 10 seconds

3. **Error Rates by Type**
   - Invalid phone numbers
   - Insufficient funds
   - Network errors
   - API errors

4. **Transaction Volume**
   - Daily/weekly trends
   - Peak times
   - Growth patterns

### Setting Up Alerts

```python
# Example: Alert on high failure rate
if failed_transactions / total_transactions > 0.1:
    send_alert("MoMo failure rate exceeds 10%")
```

---

## Troubleshooting

### Issue: "Subscription key is invalid"

**Solution**:
1. Verify key in MTN Developer Portal
2. Check you've subscribed to the product
3. Ensure no extra spaces in `.env`
4. Try regenerating the key

### Issue: "MSISDN format error"

**Solution**:
```python
# Correct the phone number format
phone = "+233 24 000 0000"
phone = phone.replace("+", "").replace(" ", "")  # "233240000000"
```

### Issue: "Transaction status stays PENDING"

**Solution**:
1. In sandbox: Should complete instantly
2. In production: Wait up to 30 seconds
3. Check MTN MoMo dashboard for transaction details
4. Verify callback URL is set up (if using webhooks)

### Issue: "API user creation fails"

**Solution**:
```bash
# Re-run setup script with fresh credentials
cd backend
rm -f .env  # Backup first!
python setup_mtn_momo.py
```

---

## Additional Resources

### Official MTN Documentation
- **Testing Guide**: https://momodeveloper.mtn.com/api-documentation/testing
- **Collections API**: https://momodeveloper.mtn.com/products/collections
- **Disbursements API**: https://momodeveloper.mtn.com/products/disbursements
- **Developer Portal**: https://momodeveloper.mtn.com/

### Your Project Documentation
- `MTN_MOMO_SANDBOX_SETUP.md` - Setup guide
- `MTN_MOMO_QUICK_START.md` - Quick start
- `backend/setup_mtn_momo.py` - Setup script
- `backend/test_mtn_momo_payment.py` - Test script
- `backend/app/integrations/mtn_momo_integration.py` - Implementation

### Support
- **MTN Support**: support@momo.mtn.com
- **Developer Forum**: https://momodeveloper.mtn.com/support

---

## Quick Reference

### Test Payment Request
```bash
curl -X POST http://localhost:8000/payments/1/pay-now \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Check Payment Status
```bash
curl -X GET http://localhost:8000/payments/1/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Run All Tests
```bash
cd backend
python test_mtn_momo_payment.py
```

### Check MTN MoMo Configuration
```bash
cd backend
python verify_ussd_setup.py
# Also checks MoMo configuration
```

---

## Summary

✅ **MTN MoMo Sandbox Testing**:
- Use official documentation: https://momodeveloper.mtn.com/api-documentation/testing
- Test with provided test script: `test_mtn_momo_payment.py`
- Verify all scenarios before production
- Monitor transactions in MTN Developer Portal

✅ **Integration Complete**:
- Collections API for receiving payments
- Disbursements API for sending payouts
- Comprehensive error handling
- Status tracking and monitoring

✅ **Ready for Production**:
- All sandbox tests passing
- Error handling verified
- Documentation complete
- Support resources available

---

**Last Updated**: October 23, 2025  
**Official Reference**: [MTN MoMo Testing Documentation](https://momodeveloper.mtn.com/api-documentation/testing)

