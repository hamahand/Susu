# SusuSave Mobile App

React Native mobile application for SusuSave - A hybrid ROSCA (Rotating Savings and Credit Association) platform.

## Features

- ✅ User Authentication (Register/Login)
- ✅ Create and Manage Savings Groups
- ✅ Real-time Group Dashboard
- ✅ Member Payment Tracking
- ✅ Payout Approval (Admin)
- ✅ Transaction History
- ✅ User Profile & Statistics

## Tech Stack

- **Framework**: Expo with React Native
- **Language**: TypeScript
- **UI Library**: React Native Paper
- **Navigation**: React Navigation v6
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Storage**: AsyncStorage

## Prerequisites

- Node.js 18+ installed
- npm or yarn
- Expo CLI (optional, installed automatically)
- iOS Simulator (Mac only) or Android Emulator
- SusuSave Backend running (default: http://localhost:8000)

## Installation

```bash
# Install dependencies
npm install

# For iOS (Mac only)
npx pod-install

# Or use yarn
yarn install
```

## Running the App

### Development Mode

```bash
# Start Expo development server
npm start

# Run on iOS simulator
npm run ios

# Run on Android emulator
npm run android

# Run on web browser
npm run web
```

### Using Expo Go App

1. Install Expo Go app on your phone
2. Run `npm start`
3. Scan the QR code with:
   - **iOS**: Camera app
   - **Android**: Expo Go app

## Configuration

### API Base URL

The app automatically detects your platform and uses the correct API URL:

- **Android Emulator**: `http://10.0.2.2:8000` (automatic)
- **iOS Simulator**: `http://localhost:8000` (automatic)
- **Production**: `https://api.sususave.com` (automatic)

#### Testing on Physical Devices

For testing on a real iPhone or Android phone:

1. Find your computer's local IP address:
   ```bash
   # macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Windows
   ipconfig
   ```

2. Create a `.env` file in this directory:
   ```bash
   EXPO_PUBLIC_API_URL=http://192.168.1.100:8000
   ```
   Replace `192.168.1.100` with your actual IP address.

3. Restart Expo:
   ```bash
   npm start -- --clear
   ```

4. Make sure your backend accepts connections from your network:
   ```bash
   # In backend directory
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Project Structure

```
src/
├── api/                 # API client and services
│   ├── client.ts       # Axios instance
│   ├── authService.ts  # Authentication API
│   ├── groupService.ts # Group management API
│   ├── paymentService.ts
│   └── payoutService.ts
├── components/          # Reusable components
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Card.tsx
│   ├── StatusBadge.tsx
│   ├── GroupCard.tsx
│   └── LoadingSpinner.tsx
├── navigation/          # Navigation configuration
│   ├── AppNavigator.tsx
│   └── types.ts
├── screens/             # Screen components
│   ├── WelcomeScreen.tsx
│   ├── LoginScreen.tsx
│   ├── RegisterScreen.tsx
│   ├── MyGroupsScreen.tsx
│   ├── CreateGroupScreen.tsx
│   ├── GroupDashboardScreen.tsx
│   └── ProfileScreen.tsx
├── store/               # State management
│   └── authContext.tsx  # Auth context
├── types/               # TypeScript types
│   └── api.ts
├── utils/               # Utility functions
│   └── storage.ts       # AsyncStorage helpers
├── theme/               # Theme configuration
│   └── index.ts
└── config.ts            # App configuration
```

## Screens

### Authentication Flow
1. **WelcomeScreen** - App introduction with login/signup
2. **LoginScreen** - User login
3. **RegisterScreen** - New user registration

### Main App Flow
1. **MyGroupsScreen** - List of user's groups
2. **CreateGroupScreen** - Create new savings group
3. **GroupDashboardScreen** - Group details, members, payouts
4. **ProfileScreen** - User profile and settings

## Testing

### Test Credentials

After running the backend seed script, you can use:

- Phone: `+233244111111`
- Password: `password123`

### Test Groups

- Code: `SUSU1234` - Monthly Rent Fund
- Code: `SUSU5678` - Business Startup Fund

## Backend Connection

Ensure the SusuSave backend is running:

```bash
cd ../../backend
docker-compose up -d
```

API should be accessible at http://localhost:8000

## Troubleshooting

### iOS Login Issues

**Problem**: iPhone users can't log in but Android works.

**Solution**: This is now fixed automatically! The app detects your platform and uses the correct URL. For details, see `IOS_LOGIN_FIX.md`.

### Cannot connect to backend

The app now automatically uses the correct URL for each platform:
- **iOS Simulator**: `http://localhost:8000` ✅ Automatic
- **Android Emulator**: `http://10.0.2.2:8000` ✅ Automatic
- **Physical Device**: Set `EXPO_PUBLIC_API_URL` in `.env` file (see Configuration section)

**For Physical Devices:**
1. Make sure device and computer are on the same WiFi network
2. Create `.env` file with your computer's IP address
3. Backend must run with `--host 0.0.0.0` to accept network connections

**Test Backend Connection:**
```bash
# From iOS simulator
curl http://localhost:8000/health

# From Android emulator
curl http://10.0.2.2:8000/health

# From physical device (replace with your IP)
curl http://192.168.1.100:8000/health
```

### Module not found errors

```bash
# Clear cache and reinstall
rm -rf node_modules
npm install
npm start -- --clear
```

### iOS build errors

```bash
cd ios
pod install
cd ..
npm run ios
```

## Building for Production

### iOS

```bash
# Create production build
eas build --platform ios

# Submit to App Store
eas submit --platform ios
```

### Android

```bash
# Create production build
eas build --platform android

# Submit to Play Store
eas submit --platform android
```

## Environment Variables

For production, configure:

- `API_BASE_URL` - Production API URL
- Backend URL in cloud deployment
- SSL/TLS for secure connections

## Features Roadmap

- [ ] Push Notifications
- [ ] Biometric Authentication
- [ ] Dark Mode
- [ ] Multiple Languages
- [ ] In-app Messaging
- [ ] Payment Reminders
- [ ] Analytics Dashboard

## Support

For issues and questions:
- Backend Issues: See `../../backend/README.md`
- Mobile Issues: Check Expo documentation
- API Issues: Check `../../docs/API.md`

## License

MIT License - See LICENSE file for details

---

**Built with ❤️ for financial inclusion**

