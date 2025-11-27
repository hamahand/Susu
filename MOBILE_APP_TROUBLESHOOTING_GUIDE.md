# 📱 Mobile App Troubleshooting Guide

## Current Issues Reported
1. **Changes not showing on phone** - Mobile app not reflecting latest updates
2. **Android login problems** - Android users experiencing login failures

---

## 🔍 Issue Analysis

### Issue 1: Changes Not Showing on Phone

**Possible Causes:**
- Mobile app cache not cleared
- App not restarted after backend changes
- Different API endpoints between web and mobile
- Mobile app using cached data
- Hot reload not working properly

### Issue 2: Android Login Problems

**Possible Causes:**
- Network connectivity issues
- API URL configuration problems
- Android emulator/device specific issues
- Backend server not accessible from Android
- Token storage/retrieval issues

---

## 🛠️ Troubleshooting Steps

### Step 1: Check Backend Status

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check backend logs
cd backend
tail -f logs/app.log
```

### Step 2: Clear Mobile App Cache

```bash
# Navigate to mobile app directory
cd mobile/SusuSaveMobile

# Clear Expo cache
npx expo start --clear

# Or clear npm cache
npm start -- --clear
```

### Step 3: Check Mobile App Configuration

```bash
# Check current API configuration
cat src/config.ts

# Verify environment variables
cat .env
```

### Step 4: Test API Connectivity

```bash
# Test from mobile app directory
curl http://localhost:8000/health

# Test Android emulator connectivity
curl http://10.0.2.2:8000/health
```

### Step 5: Restart Mobile App

```bash
# Stop current app
# Press Ctrl+C in terminal

# Restart with fresh cache
npm start -- --clear

# Or restart specific platform
npm run android -- --clear
npm run ios -- --clear
```

---

## 🔧 Platform-Specific Fixes

### Android Fixes

1. **Check Android Emulator Network:**
```bash
# Ensure Android emulator can reach host
adb shell ping 10.0.2.2

# Check if backend is accessible
adb shell curl http://10.0.2.2:8000/health
```

2. **Android Environment Variables:**
```bash
# Check Android SDK path
echo $ANDROID_HOME
echo $ANDROID_SDK_ROOT

# Should be:
# /Users/maham/Library/Android/sdk
```

3. **Android Emulator Reset:**
```bash
# Reset Android emulator
adb kill-server
adb start-server

# Or restart emulator completely
```

### iOS Fixes

1. **iOS Simulator Reset:**
```bash
# Reset iOS simulator
xcrun simctl shutdown all
xcrun simctl boot "iPhone 15"
```

2. **iOS Cache Clear:**
```bash
# Clear iOS build cache
rm -rf ios/build
npx expo run:ios --clear
```

---

## 🚨 Common Solutions

### Solution 1: Force Refresh Mobile App

```bash
# Method 1: Shake device/simulator and select "Reload"
# Method 2: Press 'r' in terminal running expo
# Method 3: Close and reopen app completely
```

### Solution 2: Check Network Configuration

```bash
# Verify backend is accessible from mobile
# iOS Simulator: http://localhost:8000
# Android Emulator: http://10.0.2.2:8000
# Physical Device: http://YOUR_IP:8000
```

### Solution 3: Reset Mobile App State

```bash
# Clear AsyncStorage (app data)
# In app: Settings > Clear App Data
# Or uninstall and reinstall app
```

### Solution 4: Backend Restart

```bash
# Restart backend server
cd backend
pkill -f uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📋 Diagnostic Checklist

### Backend Checklist
- [ ] Backend server running on port 8000
- [ ] Health endpoint responding: `curl http://localhost:8000/health`
- [ ] Database connection working
- [ ] CORS configured for mobile app
- [ ] API endpoints accessible

### Mobile App Checklist
- [ ] App builds without errors
- [ ] API configuration correct for platform
- [ ] Network requests reaching backend
- [ ] Authentication flow working
- [ ] App cache cleared
- [ ] App restarted after changes

### Platform-Specific Checklist
- [ ] **iOS**: Using `http://localhost:8000`
- [ ] **Android**: Using `http://10.0.2.2:8000`
- [ ] **Physical Device**: Using correct IP address
- [ ] **Emulator/Simulator**: Network connectivity working

---

## 🔄 Quick Fix Commands

### Complete Reset (Nuclear Option)
```bash
# 1. Stop everything
pkill -f uvicorn
pkill -f expo

# 2. Clear all caches
cd mobile/SusuSaveMobile
npx expo start --clear
rm -rf node_modules/.cache

# 3. Restart backend
cd ../../backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 4. Restart mobile app
cd ../mobile/SusuSaveMobile
npm run android -- --clear
```

### Android-Specific Reset
```bash
# Clear Android cache
cd mobile/SusuSaveMobile
npx expo start --clear
adb shell pm clear com.sususave.mobile

# Restart Android emulator
adb kill-server
adb start-server
```

### iOS-Specific Reset
```bash
# Clear iOS cache
cd mobile/SusuSaveMobile
npx expo start --clear
xcrun simctl erase all

# Restart iOS simulator
xcrun simctl shutdown all
xcrun simctl boot "iPhone 15"
```

---

## 📞 Testing Commands

### Test Backend Connectivity
```bash
# Test from host machine
curl http://localhost:8000/health

# Test from Android emulator
adb shell curl http://10.0.2.2:8000/health

# Test from iOS simulator
curl http://localhost:8000/health
```

### Test Mobile App Login
```bash
# Start mobile app with debug logs
cd mobile/SusuSaveMobile
npx expo start --clear --verbose

# Check logs for network requests
# Look for API calls in console
```

---

## 🎯 Next Steps

1. **Run Diagnostic Checklist** - Go through each item systematically
2. **Try Quick Fix Commands** - Start with least invasive solutions
3. **Test Platform-Specific Fixes** - Address Android vs iOS issues separately
4. **Verify Backend Changes** - Ensure mobile app reflects latest updates
5. **Document Results** - Note what works and what doesn't

---

## 📱 Platform Detection Debug

Add this to your mobile app to debug platform detection:

```typescript
// Add to src/config.ts temporarily
console.log('Platform:', Platform.OS);
console.log('API URL:', config.API_BASE_URL);
console.log('Environment:', __DEV__ ? 'development' : 'production');
```

---

## 🚀 Emergency Contacts

If issues persist:
1. Check backend logs: `tail -f backend/logs/app.log`
2. Check mobile app logs in Expo console
3. Verify network connectivity between mobile and backend
4. Test with different devices/emulators
5. Check for recent changes that might have broken mobile app

---

**Last Updated**: December 2024  
**Status**: Active troubleshooting guide for current mobile app issues
