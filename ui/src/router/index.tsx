import React, { Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import Layout from '@/layout/index';
import { Loading } from '@/components';
import ProtectedRoute from '@/components/ProtectedRoute';

// 使用常量存储路由路径
const ROUTES = {
  HOME: '/',
  SESSION: '/:sessionId',
  KNOWLEDGE: '/knowledge',
  LOGIN: '/login',
  API_TEST: '/api-test',
  NOT_FOUND: '*',
};

// 使用 React.lazy 懒加载组件
const Home = React.lazy(() => import('@/pages/Home'));
const NotFound = React.lazy(() => import('@/components/NotFound'));
const Knowledge = React.lazy(() => import('@/pages/Knowledge'));
const Login = React.lazy(() => import('@/pages/Login'));
const ApiTest = React.lazy(() => import('@/pages/ApiTest'));

// 创建路由配置
const router = createBrowserRouter([
  // 登录页面（不需要认证）
  {
    path: ROUTES.LOGIN,
    element: (
      <Suspense fallback={<Loading loading={true} className="h-full"/>}>
        <Login />
      </Suspense>
    ),
  },
  // API测试页面（不需要认证）
  {
    path: ROUTES.API_TEST,
    element: (
      <Suspense fallback={<Loading loading={true} className="h-full"/>}>
        <ApiTest />
      </Suspense>
    ),
  },
  // 需要认证的主要应用路由
  {
    path: ROUTES.HOME,
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<Loading loading={true} className="h-full"/>}>
            <Home />
          </Suspense>
        ),
      },
      {
        path: ROUTES.SESSION,
        element: (
          <Suspense fallback={<Loading loading={true} className="h-full"/>}>
            <Home />
          </Suspense>
        ),
      },
      {
        path: ROUTES.KNOWLEDGE,
        element: (
          <Suspense fallback={<Loading loading={true} className="h-full"/>}>
            <Knowledge />
          </Suspense>
        ),
      },
      {
        path: ROUTES.NOT_FOUND,
        element: (
          <Suspense fallback={<Loading loading={true} className="h-full"/>}>
            <NotFound />
          </Suspense>
        ),
      },
    ],
  },
  // 重定向所有未匹配的路由到 404 页面
  {
    path: '*',
    element: <Navigate to={ROUTES.NOT_FOUND} replace />,
  },
]);

export default router;
