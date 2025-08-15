/**
 * 认证相关类型定义
 */

export interface User {
  id: number;
  username: string;
  email: string;
  fullName?: string;
  role: 'ADMIN' | 'USER' | 'GUEST';
  status: 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';
  lastLogin?: string;
  createdAt: string;
  apiQuotaDaily?: number;
  apiQuotaUsed?: number;
  avatar?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  fullName?: string;
}

export interface AuthResponse {
  token?: string;
  expiresIn?: number;
  user?: User;
  message: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

export interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<boolean>;
  register: (userData: RegisterRequest) => Promise<boolean>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  clearError: () => void;
  getCurrentUser: () => Promise<void>;
}

export interface TokenInfo {
  userId: number;
  username: string;
  role: string;
  expiration: string;
  valid: boolean;
}