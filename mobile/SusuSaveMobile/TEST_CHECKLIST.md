# iOS Login Fix - Test Checklist

## Pre-Test Setup ✅

- [ ] Backend is running (`python run.py` or Docker)
- [ ] Backend accessible at `http://localhost:8000`
- [ ] Test backend: `curl http://localhost:8000/`
- [ ] Node modules installed in mobile app
- [ ] Xcode command line tools installed (macOS only)

## Test 1: iOS Simulator Login ✅

### Steps
1. [ ] Open terminal in `/mobile/SusuSaveMobile`
2. [ ] Run: `npm run ios`
3. [ ] Wait for iOS simulator to launch
4. [ ] Wait for app to load
5. [ ] Tap "Login" button
6. [ ] Enter phone: `+256700000001`
7. [ ] Enter password: `password123`
8. [ ] Tap "Login" button

### Expected Result
- [ ] ✅ Login successful
- [ ] ✅ Navigates to home/dashboard screen
- [ ] ✅ Shows user information
- [ ] ✅ No network errors

### If Failed
- Check backend logs for incoming request
- Check Expo terminal for error messages
- Verify backend is at `http://localhost:8000`
- Try: `curl http://localhost:8000/health`

## Test 2: Android Emulator Login ✅

### Steps
1. [ ] Start Android emulator
2. [ ] Open terminal in `/mobile/SusuSaveMobile`
3. [ ] Run: `npm run android`
4. [ ] Wait for app to load
5. [ ] Login with same credentials

### Expected Result
- [ ] ✅ Login successful (should still work as before)
- [ ] ✅ No regressions

## Test 3: OTP Login (iOS) ✅

### Steps
1. [ ] Tap "Login with OTP"
2. [ ] Enter phone: `+256700000001`
3. [ ] Tap "Request OTP"
4. [ ] Check backend logs for OTP code
5. [ ] Enter OTP code
6. [ ] Tap "Verify"

### Expected Result
- [ ] ✅ OTP sent (logged to backend)
- [ ] ✅ OTP verification successful
- [ ] ✅ Logged in successfully

## Test 4: Registration (iOS) ✅

### Steps
1. [ ] Tap "Sign Up"
2. [ ] Enter new phone number
3. [ ] Enter username
4. [ ] Enter password
5. [ ] Tap "Register"

### Expected Result
- [ ] ✅ Registration successful
- [ ] ✅ Automatically logged in
- [ ] ✅ Redirected to home screen

## Test 5: Physical iOS Device (Optional) ✅

### Pre-requisites
- [ ] iPhone/iPad on same WiFi as computer
- [ ] Expo Go app installed on device
- [ ] Computer's local IP address known

### Setup
1. [ ] Create `.env` file with: `EXPO_PUBLIC_API_URL=http://YOUR_IP:8000`
2. [ ] Backend running with: `uvicorn main:app --host 0.0.0.0 --port 8000`
3. [ ] Run: `npm start -- --clear`
4. [ ] Scan QR code with iPhone Camera app

### Test
- [ ] App opens in Expo Go
- [ ] Can see login screen
- [ ] Login successful

### Expected Result
- [ ] ✅ Physical device connects to backend
- [ ] ✅ Login works on real iPhone

## Test 6: API Endpoints (iOS) ✅

After successful login:

- [ ] Can view "My Groups" screen
- [ ] Can view profile
- [ ] Can create new group
- [ ] Can join group with code
- [ ] All API calls work correctly

## Test 7: Platform Detection ✅

### Verify Configuration
1. [ ] Add console log to `config.ts`:
   ```typescript
   console.log('Platform:', Platform.OS);
   console.log('API URL:', config.API_BASE_URL);
   ```
2. [ ] Check Expo terminal output

### Expected Output
- **iOS**: `Platform: ios`, `API URL: http://localhost:8000`
- **Android**: `Platform: android`, `API URL: http://10.0.2.2:8000`

## Test 8: Environment Override ✅

### Steps
1. [ ] Create `.env`: `EXPO_PUBLIC_API_URL=http://example.com:8000`
2. [ ] Restart: `npm start -- --clear`
3. [ ] Check console logs

### Expected Result
- [ ] Uses environment variable value
- [ ] Overrides platform detection

## Test 9: Production Build ✅

### Steps
1. [ ] Build production app
2. [ ] Check API URL in production

### Expected Result
- [ ] Production uses: `https://api.sususave.com`
- [ ] Not localhost URLs

## Regression Tests ✅

- [ ] Android emulator still works (no breaking changes)
- [ ] Web build still works (if applicable)
- [ ] All existing features still work
- [ ] No new TypeScript errors
- [ ] No new lint errors

## Performance Tests ✅

- [ ] Login response time < 2 seconds
- [ ] No memory leaks
- [ ] App doesn't crash
- [ ] Smooth navigation

## Summary

### Platform Support
- [ ] ✅ iOS Simulator - WORKING
- [ ] ✅ Android Emulator - WORKING
- [ ] ✅ iOS Device - WORKING (with .env)
- [ ] ✅ Android Device - WORKING (with .env)
- [ ] ✅ Production - READY

### Issues Found
_(List any issues discovered during testing)_

---

### Notes
- All tests should pass without modifications
- Platform detection is automatic
- Environment variables work for custom setups
- Backward compatible with existing Android setup

### Test Results
Date: ___________
Tester: ___________
iOS Simulator: ☐ PASS ☐ FAIL
Android Emulator: ☐ PASS ☐ FAIL
Overall Status: ☐ READY FOR PRODUCTION

