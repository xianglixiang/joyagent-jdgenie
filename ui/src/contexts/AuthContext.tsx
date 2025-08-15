import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { authService } from '../services/auth';
import { TokenManager } from '../utils/tokenManager';
import type { 
  AuthState, 
  AuthContextType, 
  User, 
  LoginRequest, 
  RegisterRequest 
} from '../types/auth';

// 认证状态的操作类型
type AuthAction = 
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'CLEAR_ERROR' };

// 初始状态
const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
  loading: false,
  error: null
};

// reducer函数
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        token: action.payload.token,
        loading: false,
        error: null
      };
    
    case 'LOGOUT':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        token: null,
        loading: false,
        error: null
      };
    
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload
      };
    
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    
    default:
      return state;
  }
}

// 创建Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider组件
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // 初始化认证状态
  useEffect(() => {
    initializeAuth();
  }, []);

  // 自动刷新Token
  useEffect(() => {
    if (state.isAuthenticated) {
      const interval = setInterval(() => {
        if (TokenManager.isTokenNearExpiry(10)) {
          refreshToken();
        }
      }, 60000); // 每分钟检查一次

      return () => clearInterval(interval);
    }
  }, [state.isAuthenticated]);

  const initializeAuth = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      const token = TokenManager.getToken();
      const user = TokenManager.getUser();

      if (token && user && !TokenManager.isTokenExpired()) {
        // Token有效，验证用户信息
        try {
          const currentUserResponse = await authService.getCurrentUser();
          // 处理新的统一响应格式，数据在 response.data 中
          const userData = currentUserResponse.data || currentUserResponse; // 兼容旧格式
          if (currentUserResponse.success && userData) {
            dispatch({ 
              type: 'LOGIN_SUCCESS', 
              payload: { 
                user: userData, 
                token 
              } 
            });
            TokenManager.setUser(userData);
          } else {
            // 验证失败，清除本地数据
            TokenManager.clearAll();
            dispatch({ type: 'LOGOUT' });
          }
        } catch (error) {
          // 网络错误等，使用本地缓存的用户信息
          dispatch({ 
            type: 'LOGIN_SUCCESS', 
            payload: { user, token } 
          });
        }
      } else {
        // Token无效或不存在，清除本地数据
        TokenManager.clearAll();
        dispatch({ type: 'LOGOUT' });
      }
    } catch (error) {
      console.error('初始化认证状态失败:', error);
      TokenManager.clearAll();
      dispatch({ type: 'LOGOUT' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const login = async (credentials: LoginRequest): Promise<boolean> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'CLEAR_ERROR' });

    try {
      const response = await authService.login(credentials);
      
      // 处理新的统一响应格式 {success: true, data: AuthResponse, message: string}
      const authData = response.data || response; // 兼容旧格式
      
      if (authData.token && authData.user) {
        // 保存Token和用户信息
        TokenManager.setToken(authData.token);
        TokenManager.setUser(authData.user);
        
        dispatch({ 
          type: 'LOGIN_SUCCESS', 
          payload: { 
            user: authData.user, 
            token: authData.token 
          } 
        });
        
        return true;
      } else {
        dispatch({ type: 'SET_ERROR', payload: authData.message || response.message || '登录失败' });
        return false;
      }
    } catch (error: any) {
      dispatch({ type: 'SET_ERROR', payload: error.message || '登录失败' });
      return false;
    }
  };

  const register = async (userData: RegisterRequest): Promise<boolean> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'CLEAR_ERROR' });

    try {
      const response = await authService.register(userData);
      
      // 处理新的统一响应格式 {success: true, data: AuthResponse, message: string}
      const authData = response.data || response; // 兼容旧格式
      
      if (authData.token && authData.user) {
        // 注册成功后自动登录
        TokenManager.setToken(authData.token);
        TokenManager.setUser(authData.user);
        
        dispatch({ 
          type: 'LOGIN_SUCCESS', 
          payload: { 
            user: authData.user, 
            token: authData.token 
          } 
        });
        
        return true;
      } else {
        dispatch({ type: 'SET_ERROR', payload: authData.message || response.message || '注册失败' });
        return false;
      }
    } catch (error: any) {
      dispatch({ type: 'SET_ERROR', payload: error.message || '注册失败' });
      return false;
    }
  };

  const logout = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      await authService.logout();
    } catch (error) {
      console.error('登出请求失败:', error);
    } finally {
      // 无论请求是否成功，都清除本地数据
      TokenManager.clearAll();
      dispatch({ type: 'LOGOUT' });
    }
  };

  const refreshToken = async (): Promise<boolean> => {
    try {
      const response = await authService.refreshToken();
      
      // 处理新的统一响应格式 {success: true, data: AuthResponse, message: string}
      const authData = response.data || response; // 兼容旧格式
      
      if (authData.token && authData.user) {
        TokenManager.setToken(authData.token);
        TokenManager.setUser(authData.user);
        
        dispatch({ 
          type: 'LOGIN_SUCCESS', 
          payload: { 
            user: authData.user, 
            token: authData.token 
          } 
        });
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('刷新Token失败:', error);
      // 刷新失败，执行登出
      logout();
      return false;
    }
  };

  const getCurrentUser = async () => {
    if (!state.isAuthenticated) return;

    try {
      const response = await authService.getCurrentUser();
      // 处理新的统一响应格式，数据在 response.data 中
      const userData = response.data || response; // 兼容旧格式
      if (response.success && userData) {
        dispatch({ type: 'UPDATE_USER', payload: userData });
        TokenManager.setUser(userData);
      }
    } catch (error) {
      console.error('获取用户信息失败:', error);
    }
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const contextValue: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshToken,
    clearError,
    getCurrentUser
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook for using auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};