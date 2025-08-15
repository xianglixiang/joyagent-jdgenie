import { memo, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { ConfigProvider, message } from 'antd';
import { ConstantProvider, SessionProvider } from '@/hooks';
import { Sidebar, LLMSelector, UserMenu } from '@/components';
import * as constants from "@/utils/constants";
import { setMessage } from '@/utils';

// Layout 组件：应用的主要布局结构
const Layout: GenieType.FC = memo(() => {
  const [messageApi, messageContent] = message.useMessage();

  useEffect(() => {
    // 初始化全局 message
    setMessage(messageApi);
  }, [messageApi]);

  return (
    <ConfigProvider theme={{ token: { colorPrimary: '#4040FFB2' } }}>
      {messageContent}
      <ConstantProvider value={constants}>
        <SessionProvider>
          <div className="h-screen flex bg-gray-50 overflow-hidden">
            {/* 左侧边栏 */}
            <Sidebar />
            
            {/* 右侧主内容区域 */}
            <div className="flex-1 flex flex-col h-screen">
              {/* Header */}
              <header className="h-64 bg-white border-b border-gray-200 flex items-center justify-between px-24 flex-shrink-0">
                {/* Left side - LLM Selector */}
                <div className="flex items-center">
                  <LLMSelector />
                </div>
                
                {/* Right side - User Menu */}
                <div className="flex items-center">
                  <UserMenu />
                </div>
              </header>
              
              {/* Main Content */}
              <main 
                className="flex-1 overflow-y-auto bg-white" 
                style={{ 
                  height: 'calc(100vh - 256px - 160px)'
                }}
              >
                <Outlet />
              </main>
              
              {/* Footer */}
              <footer className="h-40 bg-white border-t border-gray-200 flex items-center justify-center px-24 flex-shrink-0">
                <span className="text-12 text-gray-500">
                  © 2025 上海银行. All rights reserved.
                </span>
              </footer>
            </div>
          </div>
        </SessionProvider>
      </ConstantProvider>
    </ConfigProvider>
  );
});

Layout.displayName = 'Layout';

export default Layout;
