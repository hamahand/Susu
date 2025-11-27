# MTN KYC Implementation Guide

## Overview

SusuSave now includes MTN Customer KYC (Know Your Customer) verification to comply with Ghana's financial regulations. This ensures that all users conducting financial transactions are properly verified through MTN's KYC API.

## Why KYC?

**Regulatory Compliance**: Ghana's financial services regulations require proper customer verification for platforms handling money transfers and financial transactions.

**Security**: KYC verification helps prevent fraud and ensures that users are who they claim to be.

**Trust**: Verified users create a more trustworthy community within the susu groups.

## How It Works

### Verification Flow

1. **User Registration**: When a user registers (via mobile app or USSD), their phone number is automatically verified
2. **MTN Verification**: The system checks:
   - Is this a valid MTN Ghana phone number?
   - Does the user have an active MTN Mobile Money account?
3. **Database Update**: Verification status is stored in the user's profile
4. **Payment Protection**: Unverified users cannot make or receive payments

### User Experience

#### Verified Users
- ✅ Can make payments to groups
- ✅ Can receive payouts
- ✅ Full access to all features
- Green verification badge in profile

#### Unverified Users
- ✅ Can create an account
- ✅ Can join groups
- ✅ Can view group information
- ❌ Cannot make payments
- ❌ Cannot receive payouts
- Clear message explaining verification requirement

## Technical Implementation

### Database Schema

Three new fields added to the `users` table:

```sql
kyc_verified BOOLEAN DEFAULT false NOT NULL
kyc_verified_at TIMESTAMP NULL
kyc_provider VARCHAR NULL  -- "MTN", "manual", etc.
```

### API Endpoints

#### Check KYC Status
```http
GET /kyc/status
Authorization: Bearer {token}
```

Response:
```json
{
  "verified": true,
  "verified_at": "2025-10-22T12:00:00",
  "provider": "MTN",
  "required_for_payments": true,
  "message": "Verified"
}
```

#### Trigger Verification
```http
POST /kyc/verify
Authorization: Bearer {token}
```

Response:
```json
{
  "success": true,
  "verified": true,
  "message": "User verified successfully",
  "provider": "MTN"
}
```

#### Get Requirements
```http
GET /kyc/requirements
```

Response:
```json
{
  "required": true,
  "provider": "MTN",
  "country": "Ghana",
  "compliance": "Bank of Ghana KYC requirements for financial services",
  "help_url": "https://developers.mtn.com/products/mtn-customer-kyc-api-v1-product"
}
```

### Verification Process

#### Automatic Verification (During Registration)

When a user registers:

```python
# After user creation
from app.services.kyc_service import kyc_service

kyc_result = kyc_service.verify_user(db, user.id, phone_number)
```

The service performs:
1. **Phone Verification**: Checks if number is valid MTN number
2. **MoMo Validation**: Checks if active MoMo account exists
3. **Database Update**: Stores verification status

#### Manual Verification (Retry)

Users can manually trigger verification:

```python
result = kyc_service.retry_verification(db, user_id)
```

### Payment Protection

#### Payment Endpoint
```python
# In payments.py
if settings.REQUIRE_KYC_FOR_PAYMENTS and not current_user.kyc_verified:
    raise HTTPException(
        status_code=403,
        detail="KYC verification required for payments"
    )
```

#### Payout Endpoint
```python
# In payout_service.py
if settings.REQUIRE_KYC_FOR_PAYMENTS and not recipient.kyc_verified:
    raise HTTPException(
        status_code=403,
        detail="Recipient must complete KYC verification"
    )
```

## Setup Instructions

### 1. Subscribe to MTN KYC API

1. Log in to [MTN Developer Portal](https://developers.mtn.com/)
2. Navigate to your application (SusuSavinggh)
3. Subscribe to **MTN Customer KYC API v1**
4. Ensure it's approved for Ghana

### 2. Configure Environment

Update `.env` file:

```bash
# MTN KYC Configuration
ENABLE_MTN_KYC=True
MTN_KYC_BASE_URL=https://api.mtn.com/v1
REQUIRE_KYC_FOR_PAYMENTS=True

# Existing MTN credentials (already configured)
MTN_CONSUMER_KEY=J7SH4tF6QqAsa6VYFhtGRwgpvPjYnF9y
MTN_CONSUMER_SECRET=1gBhKETCBKLMyILR
MTN_ENVIRONMENT=sandbox
```

### 3. Run Database Migration

```bash
cd backend
source venv/bin/activate

# Run migration
alembic upgrade head
```

This adds the KYC fields to existing users (all start as unverified).

### 4. Verify Existing Users

Run the bulk verification script:

```bash
python verify_existing_users.py
```

This will:
- Find all unverified users
- Verify each through MTN KYC API
- Update database with results
- Generate a report

### 5. Test the Integration

```bash
python test_mtn_kyc.py
```

This tests:
- Configuration
- OAuth token retrieval
- Phone verification
- MoMo validation
- Full KYC flow

## Configuration Options

### Enable/Disable KYC

```bash
# Enable KYC verification
ENABLE_MTN_KYC=True

# Disable KYC (users auto-verified)
ENABLE_MTN_KYC=False
```

### Require for Payments

```bash
# Require KYC for all payments
REQUIRE_KYC_FOR_PAYMENTS=True

# Allow payments without KYC
REQUIRE_KYC_FOR_PAYMENTS=False
```

### Environment

```bash
# Sandbox (testing)
MTN_ENVIRONMENT=sandbox

# Production
MTN_ENVIRONMENT=production
```

## Error Handling

### Common Issues

#### 1. Verification Failed

**Error**: "Phone number verification failed"

**Causes**:
- Not an MTN number
- Invalid phone number format
- Network issues

**Solution**:
- Verify phone number is MTN Ghana
- Check format: +233XXXXXXXXX or 233XXXXXXXXX
- Retry verification

#### 2. MoMo Account Not Found

**Error**: "MoMo account validation failed"

**Causes**:
- User doesn't have MTN MoMo account
- Account is inactive

**Solution**:
- User must activate MTN MoMo
- Dial *170# to register for MoMo
- Retry after activation

#### 3. OAuth Token Failed

**Error**: "MTN authentication failed"

**Causes**:
- Invalid consumer key/secret
- API subscription not active
- Network issues

**Solution**:
- Verify credentials in MTN Developer Portal
- Check API subscription status
- Ensure internet connectivity

## User Messages

### Clear Communication

When verification fails, users receive clear messages:

```
KYC verification required for payments. 
Please verify your account to make payments.
```

When verification is pending:

```
Your account verification is in progress.
You can join groups but cannot make payments yet.
```

When verification succeeds:

```
Your account is verified! 
You can now make payments and receive payouts.
```

## Monitoring & Maintenance

### Check Verification Stats

```python
from app.models import User
from app.database import SessionLocal

db = SessionLocal()

total_users = db.query(User).count()
verified_users = db.query(User).filter(User.kyc_verified == True).count()

print(f"Total Users: {total_users}")
print(f"Verified: {verified_users}")
print(f"Unverified: {total_users - verified_users}")
```

### Bulk Re-verification

If you need to re-verify all users:

```bash
python verify_existing_users.py --all
```

### View Verification Logs

Check application logs for verification attempts:

```bash
tail -f logs/app.log | grep KYC
```

## Compliance Notes

### Ghana Regulatory Requirements

- **Bank of Ghana**: Requires KYC for financial service providers
- **Anti-Money Laundering (AML)**: KYC helps prevent financial crimes
- **Data Protection**: User data is encrypted and securely stored

### Data Retention

- Verification status: Stored indefinitely
- Verification date: Stored for audit trail
- Provider information: Stored for compliance

### User Privacy

- Phone numbers: Encrypted in database
- Verification details: Not shared with third parties
- MTN API calls: Follow OAuth 2.0 security standards

## Production Checklist

Before going live:

- [ ] MTN KYC API subscription approved
- [ ] Production credentials configured
- [ ] Environment set to `production`
- [ ] Database migration completed
- [ ] Existing users verified
- [ ] Error handling tested
- [ ] User flow tested end-to-end
- [ ] Compliance documentation ready
- [ ] Monitoring and logging enabled

## Support Resources

### MTN Documentation
- [KYC API Product Page](https://developers.mtn.com/products/mtn-customer-kyc-api-v1-product)
- [OAuth 2.0 Guide](https://developers.mtn.com/getting-started/understanding-oauth-20)
- [Developer Portal](https://developers.mtn.com/)

### Contact
- **MTN Developer Support**: Through developer portal
- **Email**: shitoutech@proton.me
- **Phone**: 0532926681

## Troubleshooting

### Test Checklist

If verification isn't working:

1. ✅ Check `ENABLE_MTN_KYC=True` in `.env`
2. ✅ Verify MTN credentials are correct
3. ✅ Confirm API subscription is active
4. ✅ Run `python test_mtn_kyc.py`
5. ✅ Check application logs for errors
6. ✅ Verify phone number is valid MTN number
7. ✅ Test with known working MTN number

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('app.integrations.mtn_kyc_integration').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Identity Document Verification**: Add ID card verification
2. **Biometric Verification**: Add fingerprint/face recognition
3. **Enhanced KYC Levels**: Different levels based on transaction amounts
4. **Automated Re-verification**: Periodic re-verification of users
5. **KYC Expiry**: Set expiry dates for verification

### Mobile App Integration

Display verification status in:
- User profile screen
- Payment flow
- Group membership view
- Settings screen

## Conclusion

MTN KYC integration ensures SusuSave complies with Ghana's financial regulations while maintaining a smooth user experience. Users are verified automatically during registration, and unverified users are clearly informed about requirements.

For technical support or questions, contact shitoutech@proton.me.

---

**Last Updated**: October 22, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready

