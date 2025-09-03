export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  role: 'ADMIN' | 'TRADER' | 'VIEWER';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface TokenData {
  access_token: string;
  token_type: string;
}