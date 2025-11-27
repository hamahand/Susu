import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { config } from '../config';
import { getToken, removeToken, removeUser } from '../utils/storage';
import { ApiError } from '../types/api';
import { Platform } from 'react-native';

// Alternative API URLs for fallback
const getAlternativeUrls = () => {
  if (Platform.OS === 'android') {
    return [
      'http://10.0.2.2:8000',  // Android emulator default
      'http://localhost:8000',  // Fallback
      'http://127.0.0.1:8000',  // Another fallback
    ];
  }
  return [config.API_BASE_URL];
};

// Create axios instance with retry logic
const createApiClient = (baseURL: string): AxiosInstance => {
  return axios.create({
    baseURL,
    timeout: 10000, // Reduced timeout for faster fallback
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

// Test API connectivity
const testApiConnection = async (url: string): Promise<boolean> => {
  try {
    const client = createApiClient(url);
    await client.get('/health');
    return true;
  } catch (error) {
    return false;
  }
};

// Find working API URL
const findWorkingApiUrl = async (): Promise<string> => {
  const urls = getAlternativeUrls();
  
  for (const url of urls) {
    console.log(`Testing API URL: ${url}`);
    if (await testApiConnection(url)) {
      console.log(`✅ Working API URL: ${url}`);
      return url;
    }
  }
  
  // If no URL works, return the default
  console.log(`❌ No working API URL found, using default: ${config.API_BASE_URL}`);
  return config.API_BASE_URL;
};

// Create the main API client
let apiClient: AxiosInstance;
let currentApiUrl: string;

const initializeApiClient = async () => {
  currentApiUrl = await findWorkingApiUrl();
  apiClient = createApiClient(currentApiUrl);
  
  // Add interceptors
  setupInterceptors(apiClient);
  
  return apiClient;
};

// Setup interceptors
const setupInterceptors = (client: AxiosInstance) => {
  // Request interceptor - Add JWT token
  client.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      const token = await getToken();
      
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor - Handle errors
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError<ApiError>) => {
      if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        
        // Handle 401 Unauthorized - Token expired or invalid
        if (status === 401) {
          // Clear stored auth data
          await removeToken();
          await removeUser();
        }
        
        // Extract error message
        const errorMessage = error.response.data?.detail || 'An error occurred';
        
        return Promise.reject(new Error(errorMessage));
      } else if (error.request) {
        // Request was made but no response received
        return Promise.reject(new Error('Network error. Please check your connection.'));
      } else {
        // Something else happened
        return Promise.reject(new Error('An unexpected error occurred'));
      }
    }
  );
};

// Initialize the API client
const initPromise = initializeApiClient();

// Export a promise that resolves when client is ready
export const apiClientReady = initPromise;

// Export default - this will be undefined initially but will be set by initPromise
export default apiClient;

