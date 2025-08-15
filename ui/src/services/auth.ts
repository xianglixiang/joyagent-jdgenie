import request from '../utils/request';
import type { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  User, 
  TokenInfo 
} from '../types/auth';

/**
 * 认证服务
 */
class AuthService {
  /**
   * 用户登录
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await request.post('/api/auth/login', credentials);
      return response;
    } catch (error: any) {
      throw new Error(error.message || '登录失败');
    }
  }

  /**
   * 用户注册
   */
  async register(userData: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await request.post('/api/auth/register', userData);
      return response;
    } catch (error: any) {
      throw new Error(error.message || '注册失败');
    }
  }

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<{ success: boolean; data?: User; message?: string }> {
    try {
      const response = await request.get('/api/auth/me');
      return response;
    } catch (error: any) {
      throw new Error(error.message || '获取用户信息失败');
    }
  }

  /**
   * 验证Token
   */
  async validateToken(): Promise<{ success: boolean; valid: boolean; data?: TokenInfo }> {
    try {
      const response = await request.post('/api/auth/validate');
      return response;
    } catch (error: any) {
      throw new Error(error.message || 'Token验证失败');
    }
  }

  /**
   * 刷新Token
   */
  async refreshToken(): Promise<AuthResponse> {
    try {
      const response = await request.post('/api/auth/refresh');
      return response;
    } catch (error: any) {
      throw new Error(error.message || '刷新Token失败');
    }
  }

  /**
   * 用户登出
   */
  async logout(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await request.post('/api/auth/logout');
      return response;
    } catch (error: any) {
      // 即使请求失败也视为登出成功
      return { success: true, message: '登出成功' };
    }
  }

  /**
   * 获取所有用户（管理员功能）
   */
  async getAllUsers(): Promise<{ success: boolean; data?: User[]; message?: string }> {
    try {
      const response = await request.get('/api/auth/users');
      return response;
    } catch (error: any) {
      throw new Error(error.message || '获取用户列表失败');
    }
  }
}

export const authService = new AuthService();