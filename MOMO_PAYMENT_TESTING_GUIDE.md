# 🧪 MTN MoMo Payment Testing Guide

**Date**: October 23, 2025  
**Status**: ✅ Complete Testing Suite Ready

---

## 🎯 **Testing Scripts Overview**

I've created comprehensive testing scripts for your MTN MoMo payment integration:

### **1. Comprehensive Test Script**
**File**: `backend/test_momo_payment.py`
- Complete payment flow testing
- User payment flow
- Admin payment requests
- Payment history verification
- Status checking

### **2. Quick Test Script**
**File**: `backend/quick_momo_test.py`
- Basic functionality test
- Login verification
- Payment trigger test
- Quick validation

---

## 🚀 **How to Run the Tests**

### **Prerequisites**
1. Backend services running
2. Database seeded with test data
3. MTN MoMo credentials configured (optional for basic tests)

### **Quick Test (Recommended First)**
```bash
cd /Users/maham/susu/backend
python3 quick_momo_test.py
```

### **Comprehensive Test**
```bash
cd /Users/maham/susu/backend
python3 test_momo_payment.py
```

---

## 🧪 **Test Scenarios Covered**

### **1. User Payment Flow Test**
- ✅ User login verification
- ✅ Group membership check
- ✅ Unpaid payment detection
- ✅ Payment trigger
- ✅ Payment status checking

### **2. Admin Payment Request Test**
- ✅ Admin login verification
- ✅ Admin group access
- ✅ Payment request to member
- ✅ Request status verification

### **3. Payment History Test**
- ✅ Payment history retrieval
- ✅ Payment status tracking
- ✅ Transaction logging

---

## 📊 **Expected Test Results**

### **Successful Test Output**
```
🧪 MTN MoMo Payment Testing Script
============================================================
[14:30:15] INFO: ✅ Backend is running and accessible

🧪 Testing User Payment Flow
==================================================
[14:30:16] INFO: Logging in user: test@example.com
[14:30:16] INFO: ✅ Login successful for test@example.com
[14:30:16] INFO: User: Test User (ID: 1)
[14:30:16] INFO: KYC Verified: True
[14:30:16] INFO: ✅ Found group: Test Group (ID: 1)
[14:30:16] INFO: ✅ Unpaid payment found: GHS 50.0
[14:30:16] INFO: 🔄 Triggering payment...
[14:30:17] INFO: ✅ Payment triggered successfully:
[14:30:17] INFO:    Payment ID: 123
[14:30:17] INFO:    Status: pending
[14:30:17] INFO:    Amount: GHS 50.0
[14:30:17] INFO:    Transaction ID: MTN123456789

🧪 Testing Admin Payment Request Flow
==================================================
[14:30:20] INFO: Logging in user: admin@example.com
[14:30:20] INFO: ✅ Login successful for admin@example.com
[14:30:20] INFO: Admin: Admin User (ID: 2)
[14:30:21] INFO: 📱 Admin requesting payment from user 1...
[14:30:21] INFO: ✅ Admin payment request successful:
[14:30:21] INFO:    Payment ID: 124
[14:30:21] INFO:    Status: pending
[14:30:21] INFO:    Amount: GHS 50.0

🧪 Testing Payment History
==================================================
[14:30:23] INFO: ✅ Payment history: 2 payments
[14:30:23] INFO:    - Payment 123: pending - GHS 50.0
[14:30:23] INFO:    - Payment 124: pending - GHS 50.0

📊 Test Results: 3/3 tests passed
🎉 All tests passed! Payment integration is working correctly.
```

---

## 🔧 **Test Configuration**

### **Test Users**
The scripts use these test accounts (from seed data):
- **Regular User**: `+233244333333` (Kofi Member) / `password123`
- **Admin User**: `+233244111111` (Kwame Admin) / `password123`

### **Test Data Requirements**
- At least one group with test user as member
- Group should have contribution amount set
- User should have unpaid contributions

---

## 🐛 **Troubleshooting Common Issues**

### **Issue 1: "Cannot connect to backend"**
**Solution:**
```bash
cd /Users/maham/susu
docker-compose up backend
```

### **Issue 2: "Login failed"**
**Solution:**
```bash
cd /Users/maham/susu/backend
python3 seed_data.py
```
**Note**: The system uses phone numbers for login, not email addresses. Use the phone numbers from seed data:
- Kofi Member: `+233244333333` / `password123`
- Kwame Admin: `+233244111111` / `password123`

### **Issue 3: "No groups found"**
**Solution:**
- Create a group in the app
- Add test user as member
- Ensure group has contribution amount

### **Issue 4: "Payment trigger failed"**
**Possible Causes:**
- KYC not verified
- User not member of group
- Group is cash-only
- MTN credentials not configured

---

## 📱 **Testing with Mobile Apps**

### **iOS Testing**
```bash
cd /Users/maham/susu/mobile/SusuSaveMobile
npm run ios
```

### **Android Testing**
```bash
cd /Users/maham/susu/mobile/SusuSaveMobile
npm run android
```

### **Web App Testing**
```bash
# Open browser
open http://localhost:5173
```

---

## 🌐 **Testing with MTN Sandbox**

### **1. Set Up MTN Credentials**
```bash
cd /Users/maham/susu/backend
python3 setup_mtn_momo.py
```

### **2. Start ngrok Tunnel**
```bash
ngrok http 8000
```

### **3. Update MTN Callback URL**
- Copy ngrok HTTPS URL
- Update in MTN developer dashboard
- Set callback URL to: `https://your-ngrok-url.ngrok.io/payments/momo/callback`

### **4. Test with Sandbox Numbers**
- **Auto-Approve**: +233240000001 to +233240000099
- **Auto-Reject**: +233240000100 to +233240000199

---

## 📊 **Monitoring Test Results**

### **Backend Logs**
```bash
cd /Users/maham/susu
docker logs sususave_backend --tail 50 --follow
```

### **Database Verification**
```bash
cd /Users/maham/susu/backend
python3 -c "
from app.database import SessionLocal
from app.models.payment import Payment
db = SessionLocal()
payments = db.query(Payment).all()
for p in payments:
    print(f'Payment {p.id}: {p.status} - GHS {p.amount}')
db.close()
"
```

### **API Health Check**
```bash
curl http://localhost:8000/health
```

---

## 🎯 **Test Automation**

### **Run Tests in CI/CD**
```bash
# Add to your CI/CD pipeline
cd /Users/maham/susu/backend
python3 quick_momo_test.py
if [ $? -eq 0 ]; then
    python3 test_momo_payment.py
fi
```

### **Scheduled Testing**
```bash
# Add to crontab for regular testing
0 */6 * * * cd /Users/maham/susu/backend && python3 quick_momo_test.py
```

---

## 📝 **Test Checklist**

- [ ] Backend services running
- [ ] Test data seeded
- [ ] Quick test passes
- [ ] Comprehensive test passes
- [ ] Mobile app payment flow works
- [ ] Web app payment flow works
- [ ] MTN credentials configured (optional)
- [ ] ngrok tunnel running (for MTN testing)
- [ ] Callback URL updated in MTN dashboard
- [ ] Sandbox phone numbers tested

---

## 🎉 **Success Criteria**

### **Basic Tests Pass**
- ✅ User can login
- ✅ Payment can be triggered
- ✅ Payment status can be checked
- ✅ Payment history can be retrieved

### **Advanced Tests Pass**
- ✅ Admin can request payments
- ✅ Payment callbacks work
- ✅ Status updates correctly
- ✅ Error handling works

---

## 🚀 **Next Steps After Testing**

1. **Set up production MTN credentials**
2. **Configure production callback URLs**
3. **Test with real phone numbers**
4. **Monitor payment success rates**
5. **Set up error monitoring and alerts**

---

**Status**: ✅ Complete MTN MoMo Payment Testing Suite  
**Files Created**: 2 comprehensive testing scripts  
**Coverage**: User payments, admin requests, payment history, status checking  

---

**Your MTN MoMo payment integration is now fully testable!** 🎉
