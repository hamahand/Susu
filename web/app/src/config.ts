// App configuration
const isDev = import.meta.env.MODE === 'development';

export const config = {
  // API Base URL
  API_BASE_URL: import.meta.env.VITE_API_URL || (isDev ? 'http://localhost:8000' : 'https://api.sususave.com'),

  // App Info
  APP_NAME: 'SusuSave',
  APP_VERSION: '1.0.0',

  // Other configs
  DEFAULT_CURRENCY: 'GHS',
  DEFAULT_PHONE_PREFIX: '+233',
};

