import api from './api';
import type {
  User,
  LoginRequest,
  RegisterRequest
} from '../types/auth';

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export const authApi = {
  // Authentication - Using correct backend endpoints
  login: async (credentials: LoginRequest): Promise<Token> => {
    // Backend expects JSON login via /auth/login/json
    const response = await api.post('/auth/login/json', {
      username: credentials.username,
      password: credentials.password,
    });
    return response.data;
  },

  loginOAuth2: async (credentials: LoginRequest): Promise<Token> => {
    // Alternative OAuth2 form-based login
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  refreshToken: async (): Promise<Token> => {
    const response = await api.post('/auth/refresh');
    return response.data;
  },

  logout: async (): Promise<{ message: string }> => {
    const response = await api.post('/auth/logout');
    localStorage.removeItem('auth_token');
    return response.data;
  },

  // User profile - Using correct endpoints
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // Public user registration
  register: async (userData: RegisterRequest): Promise<Token> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  // Token validation
  validateToken: async (): Promise<boolean> => {
    try {
      await api.get('/auth/me');
      return true;
    } catch {
      return false;
    }
  },
};
