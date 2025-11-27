import { Platform } from 'react-native';

// App configuration
const envApiUrl = (typeof process !== 'undefined' && process.env && process.env.EXPO_PUBLIC_API_URL)
  ? process.env.EXPO_PUBLIC_API_URL
  : undefined;

// Get the correct localhost URL based on platform
const getDevApiUrl = () => {
  if (Platform.OS === 'android') {
    // Android emulator uses 10.0.2.2 to access host machine
    // Fallback to localhost if 10.0.2.2 doesn't work
    return 'http://10.0.2.2:8000';
  } else if (Platform.OS === 'ios') {
    // iOS simulator can access localhost directly
    return 'http://localhost:8000';
  }
  // Default for web or other platforms
  return 'http://localhost:8000';
};

// Alternative URLs for testing
const getAlternativeApiUrl = () => {
  if (Platform.OS === 'android') {
    // Try localhost as fallback for Android
    return 'http://localhost:8000';
  }
  return getDevApiUrl();
};

export const config = {
  // API Base URL - Prefer env override for emulator/device differences
  API_BASE_URL: envApiUrl
    ? envApiUrl
    : (__DEV__ ? getDevApiUrl() : 'https://api.sususave.com'),

  // App Info
  APP_NAME: 'SusuSave',
  APP_VERSION: '1.0.0',

  // Other configs
  DEFAULT_CURRENCY: 'GHS',
  DEFAULT_PHONE_PREFIX: '+233',
};

