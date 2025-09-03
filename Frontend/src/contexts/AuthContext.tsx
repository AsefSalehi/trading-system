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
    console.log('🔍 AuthContext: register function called');
    console.log('📝 AuthContext: userData received:', userData);
    
    try {
      console.log('🚀 AuthContext: calling authApi.register');
      const tokenResponse = await authApi.register(userData);
      console.log('✅ AuthContext: token received:', tokenResponse);
      
      localStorage.setItem('auth_token', tokenResponse.access_token);
      console.log('💾 AuthContext: token stored in localStorage');

      // Get user data after successful registration
      console.log('🚀 AuthContext: fetching current user data');
      const userDataResponse = await authApi.getCurrentUser();
      console.log('✅ AuthContext: user data received:', userDataResponse);
      
      setUser(userDataResponse);
      console.log('✅ AuthContext: registration completed successfully');
    } catch (error) {
      console.error('❌ AuthContext: registration failed:', error);
      
      // Type guard for axios error
      const isAxiosError = (err: unknown): err is { message: string; response?: { data: any; status: number }; config?: any } => {
        return typeof err === 'object' && err !== null && 'message' in err;
      };
      
      if (isAxiosError(error)) {
        console.error('❌ AuthContext: error details:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status,
          config: error.config
        });
      }
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
