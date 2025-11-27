import apiClient from './client';
import {
  User,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
} from '../types/api';

// Wait for API client to be ready
const waitForApiClient = async () => {
  // First, wait for the initialization promise
  await import('./client').then(module => module.apiClientReady);
  
  // Check if apiClient is now available
  if (!apiClient) {
    // Wait a bit more for it to be set
    let attempts = 0;
    while (!apiClient && attempts < 20) {
      await new Promise(resolve => setTimeout(resolve, 100));
      attempts++;
    }
  }
  
  if (!apiClient) {
    throw new Error('API client not available');
  }
  return apiClient;
};

export const authService = {
  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<User> {
    const client = await waitForApiClient();
    const response = await client.post<User>('/auth/register', data);
    return response.data;
  },

  /**
   * Login user and get JWT token
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const client = await waitForApiClient();
    const response = await client.post<LoginResponse>('/auth/login', data);
    return response.data;
  },

  /**
   * Request OTP for phone login
   */
  async requestOtp(phoneNumber: string): Promise<{ sent_to: string; ttl_minutes: number }> {
    const client = await waitForApiClient();
    const response = await client.post<{ sent_to: string; ttl_minutes: number }>(
      '/auth/request-otp',
      { phone_number: phoneNumber }
    );
    return response.data;
  },

  /**
   * Verify OTP and receive JWT token
   */
  async verifyOtp(phoneNumber: string, code: string): Promise<LoginResponse> {
    const client = await waitForApiClient();
    const response = await client.post<LoginResponse>(
      '/auth/verify-otp',
      { phone_number: phoneNumber, code }
    );
    return response.data;
  },

  /**
   * Update profile (username and optional email)
   */
  async updateProfile(payload: { username?: string; email?: string }): Promise<User> {
    const client = await waitForApiClient();
    const response = await client.put<User>('/auth/profile', payload);
    return response.data;
  },

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    const client = await waitForApiClient();
    const response = await client.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Logout (client-side only - clear storage)
   */
  async logout(): Promise<void> {
    // No backend call needed, just clear local storage
    // This is handled by the auth context
  },
};

