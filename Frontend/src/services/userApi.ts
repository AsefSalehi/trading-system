import api from './api';
import type { User } from '../types/auth';

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  role?: 'ADMIN' | 'ANALYST' | 'TRADER' | 'VIEWER';
}

export interface UserUpdate {
  email?: string;
  username?: string;
  full_name?: string;
  role?: 'ADMIN' | 'ANALYST' | 'TRADER' | 'VIEWER';
  is_active?: boolean;
}

export const userApi = {
  // User CRUD operations
  createUser: async (userData: UserCreate): Promise<User> => {
    const response = await api.post('/users/', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/users/me');
    return response.data;
  },

  getUsers: async (skip: number = 0, limit: number = 100): Promise<User[]> => {
    const response = await api.get('/users/', {
      params: { skip, limit }
    });
    return response.data;
  },

  getUserById: async (userId: number): Promise<User> => {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  },

  updateUser: async (userId: number, userData: UserUpdate): Promise<User> => {
    const response = await api.put(`/users/${userId}`, userData);
    return response.data;
  },

  deleteUser: async (userId: number): Promise<{ message: string }> => {
    const response = await api.delete(`/users/${userId}`);
    return response.data;
  },

  // Profile management
  updateCurrentUserProfile: async (userData: UserUpdate): Promise<User> => {
    // Get current user ID first
    const currentUser = await userApi.getCurrentUser();
    return userApi.updateUser(parseInt(currentUser.id), userData);
  },
};