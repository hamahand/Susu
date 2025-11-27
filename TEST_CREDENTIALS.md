# Test User Credentials

Complete list of test users available in the database for testing.

## Quick Login Credentials

**Standard Password for ALL App Users:** `Test@123`

---

## 🎯 Your Requested Users

### 1. Kwame Mensah
- **Phone:** `+233598430399`
- **Password:** `Test@123`
- **Email:** kwame.mensah@test.com
- **Type:** APP User
- **KYC Status:** ✅ Verified (MTN)
- **Groups:** Family Savings Group (Admin), Women's Cooperative

### 2. Ama Osei
- **Phone:** `+233532936681`
- **Password:** `Test@123`
- **Email:** ama.osei@test.com
- **Type:** APP User
- **KYC Status:** ✅ Verified (MTN)
- **Groups:** Family Savings Group, Business Partners Fund (Admin)

### 3. Kofi Asante
- **Phone:** `+233242567564`
- **Password:** `Test@123`
- **Email:** kofi.asante@test.com
- **Type:** APP User
- **KYC Status:** ✅ Verified (MTN)
- **Groups:** Business Partners Fund, Youth Empowerment Fund (Admin)

---

## 📱 Additional App Users (Mobile Login)

### 4. Abena Boateng
- **Phone:** `+233501234567`
- **Password:** `Test@123`
- **Email:** abena.b@test.com
- **KYC Status:** ✅ Verified (MTN)
- **Groups:** Family Savings Group, Women's Cooperative (Admin)

### 5. Yaw Owusu
- **Phone:** `+233507654321`
- **Password:** `Test@123`
- **Email:** yaw.owusu@test.com
- **KYC Status:** ❌ NOT Verified
- **Groups:** Business Partners Fund

### 6. Akosua Adjei
- **Phone:** `+233209876543`
- **Password:** `Test@123`
- **Email:** akosua.a@test.com
- **KYC Status:** ✅ Verified (Manual)
- **Groups:** Women's Cooperative, Farmers Union Susu (Admin)

### 7. Nana Frimpong
- **Phone:** `+233241122334`
- **Password:** `Test@123`
- **Email:** nana.f@test.com
- **KYC Status:** ✅ Verified (MTN)
- **Groups:** Youth Empowerment Fund

---

## ☎️ USSD Users (No Password - USSD Only)

These users can only interact via USSD (*920*55#), not through the mobile app.

### 8. Kwabena Darko
- **Phone:** `+233555111222`
- **KYC Status:** ✅ Verified (MTN)
- **Groups:** Family Savings Group

### 9. Efua Yankson
- **Phone:** `+233555333444`
- **KYC Status:** ✅ Verified (MTN)
- **Groups:** Family Savings Group, Youth Empowerment Fund

### 10. Kojo Appiah
- **Phone:** `+233555555666`
- **KYC Status:** ❌ NOT Verified
- **Groups:** Youth Empowerment Fund, Farmers Union Susu

### 11. Adwoa Sarpong
- **Phone:** `+233555777888`
- **KYC Status:** ✅ Verified (MTN)
- **Groups:** Youth Empowerment Fund, Women's Cooperative, Farmers Union Susu

---

## 👥 Test Groups

### TEST0001 - Family Savings Group
- **Contribution:** GHS 100.00
- **Frequency:** Weekly
- **Cycles:** 12
- **Current Round:** 3
- **Admin:** Kwame Mensah (+233598430399)
- **Members:** 5
  - Kwame Mensah (Admin)
  - Ama Osei
  - Abena Boateng
  - Kwabena Darko (USSD)
  - Efua Yankson (USSD)

### TEST0002 - Business Partners Fund
- **Contribution:** GHS 500.00
- **Frequency:** Monthly
- **Cycles:** 6
- **Current Round:** 1
- **Admin:** Ama Osei (+233532936681)
- **Members:** 3
  - Ama Osei (Admin)
  - Kofi Asante
  - Yaw Owusu

### TEST0003 - Youth Empowerment Fund
- **Contribution:** GHS 50.00
- **Frequency:** Weekly
- **Cycles:** 24
- **Current Round:** 5
- **Admin:** Kofi Asante (+233242567564)
- **Members:** 6
  - Kofi Asante (Admin)
  - Kwabena Darko (USSD)
  - Efua Yankson (USSD)
  - Kojo Appiah (USSD)
  - Adwoa Sarpong (USSD)
  - Nana Frimpong

### TEST0004 - Women's Cooperative
- **Contribution:** GHS 200.00
- **Frequency:** Bi-weekly
- **Cycles:** 10
- **Current Round:** 2
- **Admin:** Abena Boateng (+233501234567)
- **Members:** 4
  - Abena Boateng (Admin)
  - Akosua Adjei
  - Kwame Mensah
  - Adwoa Sarpong (USSD)

### TEST0005 - Farmers Union Susu
- **Contribution:** GHS 75.00
- **Frequency:** Weekly
- **Cycles:** 8
- **Current Round:** 1
- **Admin:** Akosua Adjei (+233209876543)
- **Members:** 3
  - Akosua Adjei (Admin)
  - Kwabena Darko (USSD)
  - Kojo Appiah (USSD)

---

## 💰 Payment Data

- **Total Payments:** 30
- **Payment Types:**
  - Mobile Money (MOMO) - majority
  - Cash - some payments
- **Payment Statuses:**
  - ✅ SUCCESS - completed payments
  - ⏳ PENDING - awaiting payment
  - ❌ FAILED - failed payments (with retry counts)

---

## 🧪 Test Scenarios

### Scenario 1: Successful Login
```bash
Phone: +233598430399
Password: Test@123
Expected: Login successful with JWT token
```

### Scenario 2: KYC Verification Required
```bash
Phone: +233507654321 (Yaw Owusu)
Password: Test@123
Expected: Login successful but KYC not verified
Note: Some actions may be restricted
```

### Scenario 3: Group Admin Functions
```bash
Phone: +233598430399 (Kwame Mensah)
Password: Test@123
Group: TEST0001
Expected: Can manage group, mark payments, approve payouts
```

### Scenario 4: Regular Member
```bash
Phone: +233241122334 (Nana Frimpong)
Password: Test@123
Group: TEST0003
Expected: Can view dashboard, make payments, no admin functions
```

### Scenario 5: USSD Testing
```bash
Phone: +233555111222 (Kwabena Darko)
Method: USSD (*920*55#)
Expected: Can interact via USSD menu
Note: Cannot login to mobile app
```

---

## 📊 Database Statistics

- **Total Users:** 31 (including old test users)
- **App Users:** 11
- **USSD Users:** 4  
- **Total Groups:** 8
- **Total Memberships:** 21+
- **Total Payments:** 30+

---

## 🚀 Quick Test Commands

### Login Test
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+233598430399","password":"Test@123"}'
```

### Get User Groups
```bash
TOKEN="your-jwt-token-here"
curl -X GET http://localhost:8000/groups/my-groups \
  -H "Authorization: Bearer $TOKEN"
```

### Create a New Group
```bash
TOKEN="your-jwt-token-here"
curl -X POST http://localhost:8000/groups \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"New Test Group",
    "contribution_amount":150.0,
    "frequency":"weekly",
    "member_count":5,
    "num_cycles":10
  }'
```

---

## 🔄 Reset Test Data

To recreate all test users from scratch:

```bash
cd backend
source venv/bin/activate
python create_test_users.py
```

---

## 📱 Frontend Testing

1. Open: http://localhost:3000/app/
2. Login with any App User credentials
3. Test creating groups, inviting members, making payments

---

## 🆘 Support

- **API Documentation:** http://localhost:8000/docs
- **Database Script:** `/Users/maham/susu/backend/create_test_users.py`
- **Password for ALL app users:** `Test@123`

**Last Updated:** October 22, 2025


