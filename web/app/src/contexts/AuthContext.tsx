import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { User, LoginRequest, RegisterRequest, UserType } from '../types/api';
import { authService } from '../api/authService';
import { saveToken, getToken, saveUser, getUser, clearStorage } from '../utils/storage';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  requestOtp: (phoneNumber: string) => Promise<{ sent_to: string; ttl_minutes: number }>;
  loginWithOtp: (phoneNumber: string, code: string) => Promise<void>;
  updateProfile: (payload: { username?: string; email?: string }) => Promise<User>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  loadStoredAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!token && !!user;

  // Load stored authentication on app start
  const loadStoredAuth = async () => {
    try {
      setIsLoading(true);
      const storedToken = getToken();
      const storedUser = getUser();

      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(storedUser);
        
        // Validate token by fetching current user
        try {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
          saveUser(currentUser);
        } catch (error) {
          // Token is invalid, clear storage
          clearStorage();
          setToken(null);
          setUser(null);
        }
      }
    } catch (error) {
      console.error('Error loading stored auth:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Login
  const login = async (data: LoginRequest) => {
    try {
      const response = await authService.login(data);
      const { access_token } = response;

      // Save token
      saveToken(access_token);
      setToken(access_token);

      // Fetch and save user
      const currentUser = await authService.getCurrentUser();
      saveUser(currentUser);
      setUser(currentUser);
    } catch (error) {
      throw error;
    }
  };

  // OTP: request code
  const requestOtp = async (phoneNumber: string) => {
    const res = await authService.requestOtp(phoneNumber);
    return res;
  };

  // OTP: verify and login
  const loginWithOtp = async (phoneNumber: string, code: string) => {
    const response = await authService.verifyOtp(phoneNumber, code);
    const { access_token } = response;
    saveToken(access_token);
    setToken(access_token);
    const currentUser = await authService.getCurrentUser();
    saveUser(currentUser);
    setUser(currentUser);
  };

  // Profile update
  const updateProfile = async (payload: { username?: string; email?: string }) => {
    const updated = await authService.updateProfile(payload);
    saveUser(updated);
    setUser(updated);
    return updated;
  };

  // Register
  const register = async (data: RegisterRequest) => {
    try {
      // Register user
      await authService.register(data);

      // Auto-login after registration
      await login({
        phone_number: data.phone_number,
        password: data.password,
      });
    } catch (error) {
      throw error;
    }
  };

  // Logout
  const logout = () => {
    try {
      clearStorage();
      setToken(null);
      setUser(null);
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  // Load stored auth on mount
  useEffect(() => {
    loadStoredAuth();
  }, []);

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    requestOtp,
    loginWithOtp,
    updateProfile,
    register,
    logout,
    loadStoredAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

