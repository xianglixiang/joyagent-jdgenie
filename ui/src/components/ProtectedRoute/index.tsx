import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'ADMIN' | 'USER' | 'GUEST';
  fallback?: React.ReactNode;
}

/**
 * 受保护的路由组件
 * 用于需要认证的页面，自动重定向未登录用户到登录页面
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole,
  fallback 
}) => {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  // 如果正在加载，显示加载状态
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <Spin size="large" />
      </div>
    );
  }

  // 如果未认证，重定向到登录页面
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 如果需要特定角色权限
  if (requiredRole && user?.role !== requiredRole) {
    // 如果是管理员要求但用户不是管理员
    if (requiredRole === 'ADMIN' && user?.role !== 'ADMIN') {
      return fallback || (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '200px',
          flexDirection: 'column' 
        }}>
          <h3>权限不足</h3>
          <p>您没有访问此页面的权限</p>
        </div>
      );
    }
  }

  // 认证通过，渲染子组件
  return <>{children}</>;
};

export default ProtectedRoute;