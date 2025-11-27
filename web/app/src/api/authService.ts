import apiClient from './client';
import {
  User,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  OTPResponse,
  UpdateProfileRequest,
} from '../types/api';

export const authService = {
  /**
   * Login with phone number and password
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', {
      phone_number: data.phone_number,
      password: data.password,
    });
    return response.data;
  },

  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data);
    return response.data;
  },

  /**
   * Request OTP code
   */
  async requestOtp(phoneNumber: string): Promise<OTPResponse> {
    const response = await apiClient.post<OTPResponse>('/auth/request-otp', {
      phone_number: phoneNumber,
    });
    return response.data;
  },

  /**
   * Verify OTP and login
   */
  async verifyOtp(phoneNumber: string, code: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/verify-otp', {
      phone_number: phoneNumber,
      code,
    });
    return response.data;
  },

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Update user profile
   */
  async updateProfile(data: UpdateProfileRequest): Promise<User> {
    const response = await apiClient.put<User>('/auth/profile', data);
    return response.data;
  },
};

