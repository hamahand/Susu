# MTN KYC Quick Start Guide

## 5-Minute Setup

### 1. Subscribe to KYC API
```
1. Go to https://developers.mtn.com/
2. Login as: shitoutech@proton.me
3. Open app: SusuSavinggh
4. Subscribe to: MTN Customer KYC API v1
5. Wait for approval ✓
```

### 2. Update .env
```bash
ENABLE_MTN_KYC=True
MTN_KYC_BASE_URL=https://api.mtn.com/v1
REQUIRE_KYC_FOR_PAYMENTS=True
```

### 3. Run Migration
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 4. Test It
```bash
python test_mtn_kyc.py
```

### 5. Verify Users
```bash
python verify_existing_users.py
```

## Done! 🎉

---

## Quick Commands

### Test KYC Integration
```bash
python test_mtn_kyc.py
```

### Verify All Users
```bash
python verify_existing_users.py
```

### Verify Specific Users
```python
from app.services.kyc_service import kyc_service
from app.database import SessionLocal

db = SessionLocal()
result = kyc_service.verify_user(db, user_id=1, phone_number="+233240000000")
print(result)
```

### Check Verification Stats
```python
from app.models import User
from app.database import SessionLocal

db = SessionLocal()
total = db.query(User).count()
verified = db.query(User).filter(User.kyc_verified == True).count()
print(f"Verified: {verified}/{total}")
```

---

## API Endpoints

### Check Status
```bash
curl http://localhost:8000/kyc/status \
  -H "Authorization: Bearer TOKEN"
```

### Trigger Verification
```bash
curl -X POST http://localhost:8000/kyc/verify \
  -H "Authorization: Bearer TOKEN"
```

### Get Requirements
```bash
curl http://localhost:8000/kyc/requirements
```

---

## Troubleshooting

### Problem: "MTN authentication failed"
**Solution**: Check MTN_CONSUMER_KEY and MTN_CONSUMER_SECRET in .env

### Problem: "Verification failed"
**Solution**: Ensure phone number is valid MTN Ghana number

### Problem: "MoMo account not found"
**Solution**: User needs to activate MTN MoMo (dial *170#)

### Problem: "KYC API subscription not found"
**Solution**: Subscribe to MTN Customer KYC API v1 in portal

---

## Configuration

### Disable KYC (for testing)
```bash
ENABLE_MTN_KYC=False
```

### Allow Payments Without KYC
```bash
REQUIRE_KYC_FOR_PAYMENTS=False
```

### Production Mode
```bash
MTN_ENVIRONMENT=production
```

---

## Full Documentation

- **Complete Guide**: `backend/docs/KYC_IMPLEMENTATION.md`
- **MTN Setup**: `backend/docs/MTN_SETUP.md`  
- **Implementation Summary**: `MTN_KYC_IMPLEMENTATION_COMPLETE.md`

---

## Support

**Email**: shitoutech@proton.me  
**Phone**: 0532926681  
**MTN Portal**: https://developers.mtn.com/

