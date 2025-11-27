# Quick Test: PWA Login

## 🚀 Quick Start

### 1. Open the PWA
Open your browser and go to:
```
http://localhost:3000/app/login
```

### 2. Login with Test Credentials
```
Phone Number: +233244999888
Password: testpass123
```

### 3. Click "Login"
You should be redirected to the dashboard!

---

## ✅ What Was Fixed

The PWA login was broken because:
- Frontend was sending `username` field → Backend expected `phone_number`
- Frontend was using form-urlencoded → Backend expected JSON

Both issues are now fixed in `/web/app/src/api/authService.ts`

---

## 🔄 Alternative: OTP Login

You can also login with OTP (no password needed):

1. Enter phone number
2. Click "Login with OTP"
3. Enter the OTP code sent to your phone
4. Access granted!

---

## 🧪 Automated Testing

Run the automated test script:
```bash
cd /Users/maham/susu
./test_pwa_login.sh
```

This will:
✅ Create a test user
✅ Login via API
✅ Verify authentication
✅ Show test credentials

---

## 📝 Create New Users

### Via API:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+233244555666",
    "name": "Your Name",
    "password": "yourpassword123",
    "user_type": "app"
  }'
```

### Via PWA:
1. Go to http://localhost:3000/app/register
2. Fill in the form
3. Click "Sign Up"

---

## 🔍 Troubleshooting

### Can't connect to backend?
```bash
# Check if backend is running
curl http://localhost:8000/docs

# If not, start it:
cd /Users/maham/susu/backend
python -m app.main
```

### Frontend not loading?
```bash
# Check if Vite is running on port 3000
lsof -ti:3000

# If not, start it:
cd /Users/maham/susu/web/app
npm run dev
```

### Login still not working?
1. Open browser console (F12)
2. Check for JavaScript errors
3. Check Network tab for failed requests
4. Verify you're using the correct credentials
5. Clear browser cache and cookies

---

## 📊 Backend Status

Check backend health:
```bash
curl http://localhost:8000/health
```

View API documentation:
```
http://localhost:8000/docs
```

---

## 🎯 Next Steps

After confirming login works:

1. ✅ Test dashboard features
2. ✅ Test group creation
3. ✅ Test payment methods
4. ✅ Test mobile app login
5. ✅ Deploy to production

---

## 📚 More Info

- Full fix details: `PWA_LOGIN_FIX.md`
- Complete summary: `LOGIN_ISSUES_FIXED.md`
- Backend tests: `backend/tests/test_auth.py`

