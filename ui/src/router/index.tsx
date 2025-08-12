import React, { Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import Layout from '@/layout/index';
import { Loading } from '@/components';

// 使用常量存储路由路径
const ROUTES = {
  HOME: '/',
  SESSION: '/:sessionId',
  KNOWLEDGE: '/knowledge',
  NOT_FOUND: '*',
};

// 使用 React.lazy 懒加载组件
const Home = React.lazy(() => import('@/pages/Home'));
const NotFound = React.lazy(() => import('@/components/NotFound'));

// 创建知识库页面的占位组件
const Knowledge = React.lazy(() => Promise.resolve({ 
  default: () => (
    <div className="h-full flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-24 font-bold mb-8">知识库</h2>
        <p className="text-gray-500">功能正在开发中...</p>
      </div>
    </div>
  )
}));

// 创建路由配置
const router = createBrowserRouter([
  {
    path: ROUTES.HOME,
    element: <Layout />,
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
