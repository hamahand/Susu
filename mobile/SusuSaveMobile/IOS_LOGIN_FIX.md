# iOS Login Fix - Complete Guide

## Problem Fixed
iOS users couldn't log in because the app was trying to connect to `http://10.0.2.2:8000`, which is Android's special address for accessing the host machine. iOS simulators and devices need different addresses.

## Solution Implemented
Updated `/src/config.ts` to automatically detect the platform and use the correct API URL:
- **Android Emulator**: `http://10.0.2.2:8000`
- **iOS Simulator**: `http://localhost:8000`
- **Production**: `https://api.sususave.com`

## Testing the Fix

### 1. iOS Simulator
```bash
# Make sure your backend is running on port 8000
cd backend
python run.py

# In a new terminal, start the iOS simulator
cd mobile/SusuSaveMobile
npm run ios
```

The iOS simulator should now connect to `http://localhost:8000` and login should work.

### 2. Physical iOS Device
For testing on a real iPhone/iPad connected to the same WiFi network:

1. Find your computer's local IP address:
   ```bash
   # On macOS
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Example output: inet 192.168.1.100
   ```

2. Create a `.env` file in `/mobile/SusuSaveMobile/`:
   ```bash
   EXPO_PUBLIC_API_URL=http://192.168.1.100:8000
   ```
   Replace `192.168.1.100` with your actual IP address.

3. Restart the Expo server:
   ```bash
   npm start -- --clear
   ```

4. Make sure your backend allows connections from your local network:
   ```bash
   # Run backend with 0.0.0.0 to accept connections from any interface
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### 3. Android Emulator (No Changes Needed)
Android should continue to work as before:
```bash
npm run android
```

## Environment Variables

You can override the API URL for any platform by setting:
```bash
EXPO_PUBLIC_API_URL=http://your-api-url:8000
```

This is useful for:
- Testing on physical devices
- Using a custom backend URL
- Testing staging environments

## Common Issues

### Issue 1: "Network Error" on iOS
**Solution**: Make sure the backend is running and accessible at `http://localhost:8000`

Test with curl:
```bash
curl http://localhost:8000/health
```

### Issue 2: Physical Device Can't Connect
**Solution**: Ensure:
1. Device and computer are on the same WiFi network
2. Computer's firewall allows connections on port 8000
3. Backend is running with `--host 0.0.0.0`
4. `.env` file has the correct local IP address

### Issue 3: Works on Simulator but Not Physical Device
**Solution**: Physical devices can't access `localhost` - they need your computer's actual IP address. Create a `.env` file with `EXPO_PUBLIC_API_URL=http://YOUR_LOCAL_IP:8000`

## Files Changed
- `/mobile/SusuSaveMobile/src/config.ts` - Added platform detection for API URLs

## Verification Steps
1. ✅ Start backend server
2. ✅ Launch iOS simulator: `npm run ios`
3. ✅ Navigate to Login screen
4. ✅ Enter phone number (e.g., +256700000001)
5. ✅ Enter password
6. ✅ Tap "Login" button
7. ✅ Should successfully authenticate and navigate to home screen

## Additional Notes
- The fix is backward compatible - Android emulator still works
- Production builds automatically use `https://api.sususave.com`
- Development mode (`__DEV__`) automatically uses the correct local URL
- You can always override with `EXPO_PUBLIC_API_URL` environment variable

