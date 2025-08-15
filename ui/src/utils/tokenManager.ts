/**
 * Token管理器 - 处理JWT Token的存储、获取和验证
 */

const TOKEN_KEY = 'genie_auth_token';
const USER_KEY = 'genie_user_info';
const REFRESH_TOKEN_KEY = 'genie_refresh_token';

export class TokenManager {
  /**
   * 存储Token
   */
  static setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  }

  /**
   * 获取Token
   */
  static getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  /**
   * 移除Token
   */
  static removeToken(): void {
    localStorage.removeItem(TOKEN_KEY);
  }

  /**
   * 存储用户信息
   */
  static setUser(user: any): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  /**
   * 获取用户信息
   */
  static getUser(): any | null {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * 移除用户信息
   */
  static removeUser(): void {
    localStorage.removeItem(USER_KEY);
  }

  /**
   * 存储刷新Token
   */
  static setRefreshToken(token: string): void {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  }

  /**
   * 获取刷新Token
   */
  static getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  /**
   * 移除刷新Token
   */
  static removeRefreshToken(): void {
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  /**
   * 清除所有认证信息
   */
  static clearAll(): void {
    this.removeToken();
    this.removeUser();
    this.removeRefreshToken();
  }

  /**
   * 检查Token是否存在
   */
  static hasToken(): boolean {
    return !!this.getToken();
  }

  /**
   * 检查Token是否过期（基于JWT的exp字段）
   */
  static isTokenExpired(): boolean {
    const token = this.getToken();
    if (!token) return true;

    try {
      const payload = this.parseJWT(token);
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp < currentTime;
    } catch (error) {
      console.error('解析Token失败:', error);
      return true;
    }
  }

  /**
   * 解析JWT Token
   */
  static parseJWT(token: string): any {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) {
        throw new Error('Invalid JWT format');
      }

      const payload = parts[1];
      const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
      return JSON.parse(decoded);
    } catch (error) {
      throw new Error('Failed to parse JWT token');
    }
  }

  /**
   * 获取Token中的用户信息
   */
  static getUserFromToken(): any | null {
    const token = this.getToken();
    if (!token) return null;

    try {
      const payload = this.parseJWT(token);
      return {
        userId: parseInt(payload.sub),
        username: payload.username,
        role: payload.role,
        exp: payload.exp,
        iat: payload.iat
      };
    } catch (error) {
      console.error('从Token获取用户信息失败:', error);
      return null;
    }
  }

  /**
   * 检查用户是否有指定角色
   */
  static hasRole(role: string): boolean {
    const userInfo = this.getUserFromToken();
    return userInfo?.role === role;
  }

  /**
   * 检查用户是否为管理员
   */
  static isAdmin(): boolean {
    return this.hasRole('ADMIN');
  }

  /**
   * 检查用户是否为普通用户
   */
  static isUser(): boolean {
    return this.hasRole('USER');
  }

  /**
   * 获取Token过期时间
   */
  static getTokenExpiration(): Date | null {
    const token = this.getToken();
    if (!token) return null;

    try {
      const payload = this.parseJWT(token);
      return new Date(payload.exp * 1000);
    } catch (error) {
      return null;
    }
  }

  /**
   * 计算Token剩余有效时间（秒）
   */
  static getTokenRemainingTime(): number {
    const expiration = this.getTokenExpiration();
    if (!expiration) return 0;

    const now = new Date();
    const remaining = Math.floor((expiration.getTime() - now.getTime()) / 1000);
    return Math.max(0, remaining);
  }

  /**
   * 检查Token是否即将过期（默认5分钟内过期）
   */
  static isTokenNearExpiry(thresholdMinutes: number = 5): boolean {
    const remaining = this.getTokenRemainingTime();
    return remaining > 0 && remaining < (thresholdMinutes * 60);
  }
}