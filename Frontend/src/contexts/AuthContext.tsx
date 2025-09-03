import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authApi } from '../services/authApi';
import type { User, LoginRequest, RegisterRequest } from '../types/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (userData: Partial<User>) => Promise<void>;
  forceLogout: () => void; // Development helper
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  // Check if user is already logged in on app start
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const isValid = await authApi.validateToken();
          if (isValid) {
            const currentUser = await authApi.getCurrentUser();
            setUser(currentUser);
          } else {
            localStorage.removeItem('auth_token');
          }
        } catch (error) {
          console.error('Failed to validate token:', error);
          localStorage.removeItem('auth_token');
        }
      }
      setIsLoading(false);
    };

    // Add a small delay to ensure smooth loading experience
    const timer = setTimeout(initializeAuth, 100);
    return () => clearTimeout(timer);
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      const tokenResponse = await authApi.login(credentials);
      localStorage.setItem('auth_token', tokenResponse.access_token);

      // Get user data after successful login
      const userData = await authApi.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (userData: RegisterRequest) => {
    try {
      // Note: Backend doesn't have public registration endpoint
      // This would need to be implemented or handled differently
      throw new Error('Public registration not available. Please contact administrator.');
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('auth_token');
      setUser(null);
    }
  };

  const updateUser = async (userData: Partial<User>) => {
    try {
      // Use userApi for profile updates since authApi doesn't have this endpoint
      const { userApi } = await import('../services/userApi');
      const updatedUser = await userApi.updateCurrentUserProfile(userData);
      setUser(updatedUser);
    } catch (error) {
      console.error('Failed to update user:', error);
      throw error;
    }
  };

  const forceLogout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    console.log('Authentication cleared for testing');
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    updateUser,
    forceLogout,
  };

  // Development helper: expose forceLogout globally
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).forceLogout = forceLogout;
      console.log('Development helper: Use window.forceLogout() to test login forms');
    }
  }, []);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
