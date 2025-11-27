import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { adminAPI } from '../api/adminClient';
import type { UserDetail } from '../types/admin';

interface AdminAuthContextType {
  user: UserDetail | null;
  loading: boolean;
  login: (phone: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AdminAuthContext = createContext<AdminAuthContextType | undefined>(undefined);

export const AdminAuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = adminAPI.getToken();
    if (token) {
      try {
        const currentUser = await adminAPI.getCurrentUser();
        if (currentUser.is_system_admin) {
          setUser(currentUser);
        } else {
          adminAPI.clearToken();
        }
      } catch (error) {
        adminAPI.clearToken();
      }
    }
    setLoading(false);
  };

  const login = async (phone: string, password: string) => {
    await adminAPI.login(phone, password);
    const currentUser = await adminAPI.getCurrentUser();
    
    if (!currentUser.is_system_admin) {
      adminAPI.clearToken();
      throw new Error('Access denied. System administrator privileges required.');
    }
    
    setUser(currentUser);
  };

  const logout = () => {
    adminAPI.clearToken();
    setUser(null);
  };

  return (
    <AdminAuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AdminAuthContext.Provider>
  );
};

export const useAdminAuth = () => {
  const context = useContext(AdminAuthContext);
  if (context === undefined) {
    throw new Error('useAdminAuth must be used within AdminAuthProvider');
  }
  return context;
};

