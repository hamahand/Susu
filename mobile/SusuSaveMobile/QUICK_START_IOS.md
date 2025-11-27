# 🚀 Quick Start - iOS Testing

## One-Command Test

```bash
cd mobile/SusuSaveMobile && ./test-ios-login.sh
```

## Manual Test (3 steps)

### 1. Start Backend
```bash
cd backend
python run.py
```

### 2. Launch iOS App
```bash
cd mobile/SusuSaveMobile
npm run ios
```

### 3. Test Login
- Phone: `+256700000001`
- Password: `password123`
- Tap "Login"
- ✅ Should work!

---

## Physical iPhone Testing

### Setup (one-time)
```bash
# 1. Get your computer's IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# 2. Create .env file
echo "EXPO_PUBLIC_API_URL=http://YOUR_IP:8000" > .env

# 3. Run backend with network access
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# 4. Start Expo
cd mobile/SusuSaveMobile
npm start -- --clear
```

### Test
- Scan QR code with Camera app
- Opens in Expo Go
- Login with test credentials
- ✅ Works!

---

## What Changed

| Platform | Old (Broken) | New (Fixed) |
|----------|--------------|-------------|
| iOS Simulator | ❌ `10.0.2.2:8000` | ✅ `localhost:8000` |
| Android Emulator | ✅ `10.0.2.2:8000` | ✅ `10.0.2.2:8000` |

**Result**: iOS login now works! 🎉

---

## Troubleshooting

**Network Error?**
```bash
# Check backend is running
curl http://localhost:8000/health
```

**Still not working?**
- See `IOS_LOGIN_FIX.md` for detailed help
- Check Expo terminal for error messages
- Restart with: `npm start -- --clear`

---

## Test Credentials

| Phone | Password | Role |
|-------|----------|------|
| +256700000001 | password123 | Member |
| +256700000002 | password123 | Member |
| +256700000003 | password123 | Admin |

---

**Need Help?** → Read `IOS_LOGIN_FIX.md`

