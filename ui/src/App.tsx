import React from 'react';
import { ConfigProvider } from 'antd';
import { RouterProvider } from 'react-router-dom';
import zhCN from 'antd/locale/zh_CN';
import router from './router';
import { AuthProvider } from './contexts/AuthContext';

// App 组件：应用的根组件，设置全局配置和路由
const App: GenieType.FC = React.memo(() => {
  return (
    <ConfigProvider locale={zhCN}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </ConfigProvider>
  );
});

export default App;
