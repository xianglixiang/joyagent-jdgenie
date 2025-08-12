import React, { memo, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button, Tooltip } from 'antd';
import { Home, Database, Plus, MessageSquare, Trash2 } from 'lucide-react';
import classNames from 'classnames';
import { useSession } from '@/hooks';
import { formatTimestamp } from '@/utils';
import logo from '@/assets/logo.png';

interface SidebarProps {
  className?: string;
}

const Sidebar: React.FC<SidebarProps> = memo(({ className }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { 
    sessions, 
    currentSessionId, 
    createSession, 
    setCurrentSession, 
    deleteSession 
  } = useSession();

  // 导航菜单项
  const navigationItems = useMemo(() => [
    {
      key: 'home',
      label: '首页',
      icon: Home,
      path: '/',
    },
    {
      key: 'knowledge',
      label: '知识库',
      icon: Database,
      path: '/knowledge',
    }
  ], []);

  // 处理导航点击
  const handleNavClick = (path: string) => {
    navigate(path);
  };

  // 创建新会话
  const handleCreateSession = () => {
    const sessionId = createSession();
    navigate(`/${sessionId}`);
  };

  // 选择会话
  const handleSessionClick = (sessionId: string) => {
    setCurrentSession(sessionId);
    navigate(`/${sessionId}`);
  };

  // 删除会话
  const handleDeleteSession = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    deleteSession(sessionId);
    
    // 如果删除的是当前会话，导航到首页
    if (sessionId === currentSessionId) {
      navigate('/');
    }
  };

  // 判断是否为当前路径
  const isCurrentPath = (path: string) => {
    if (path === '/') {
      return location.pathname === '/' || (!location.pathname.includes('/knowledge'));
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className={classNames('w-280 bg-white border-r border-gray-200 flex flex-col h-full', className)}>
      {/* Logo 区域 */}
      <div className="flex items-center p-24 border-b border-gray-100">
        <div className="w-1/2 flex justify-center">
          <img src={logo} alt="logo" className="w-132 h-32" />
        </div>
        <div className="w-1/2 flex justify-center">
          <span className="font-bold text-transparent bg-clip-text" 
                style={{
                  fontSize: '30px',
                  backgroundImage: 'linear-gradient(270deg, rgba(130,45,255,1) 0%,rgba(62,69,255,1) 20.88266611099243%,rgba(60,196,250,1) 100%)'
                }}>
            海小睿
          </span>
        </div>
      </div>

      {/* 导航菜单 */}
      <div className="p-16">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = isCurrentPath(item.path);
          
          return (
            <div
              key={item.key}
              onClick={() => handleNavClick(item.path)}
              className={classNames(
                'flex items-center px-12 py-8 rounded-8 cursor-pointer transition-all duration-200 mb-4',
                {
                  'bg-blue-50 text-blue-600 border border-blue-200': isActive,
                  'text-gray-600 hover:bg-gray-50 hover:text-gray-900': !isActive,
                }
              )}
            >
              <Icon className="w-16 h-16 mr-8" />
              <span className="text-14 font-medium">{item.label}</span>
            </div>
          );
        })}
      </div>

      {/* 分割线 */}
      <div className="mx-16 border-t border-gray-200"></div>

      {/* 新建会话按钮 */}
      <div className="p-16">
        <Button
          type="primary"
          icon={<Plus className="w-16 h-16" />}
          onClick={handleCreateSession}
          className="w-full flex items-center justify-center"
          size="large"
        >
          新建会话
        </Button>
      </div>

      {/* 会话历史列表 */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="px-16 pb-8">
          <h3 className="text-12 font-medium text-gray-500 uppercase tracking-wide">
            历史会话
          </h3>
        </div>
        
        <div className="flex-1 overflow-y-auto px-16">
          {sessions.length === 0 ? (
            <div className="text-center py-24 text-gray-400">
              <MessageSquare className="w-32 h-32 mx-auto mb-8 opacity-50" />
              <p className="text-12">暂无会话历史</p>
            </div>
          ) : (
            <div className="space-y-4">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => handleSessionClick(session.id)}
                  className={classNames(
                    'group relative p-12 rounded-8 cursor-pointer transition-all duration-200 border',
                    {
                      'bg-blue-50 border-blue-200 text-blue-600': session.id === currentSessionId,
                      'bg-white border-gray-100 hover:bg-gray-50 hover:border-gray-200 text-gray-700': session.id !== currentSessionId,
                    }
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-14 font-medium truncate mb-4">
                        {session.title}
                      </h4>
                      {session.lastMessage && (
                        <p className="text-12 text-gray-500 line-clamp-2 mb-4">
                          {session.lastMessage}
                        </p>
                      )}
                      <p className="text-10 text-gray-400">
                        {formatTimestamp(session.lastActiveTime)}
                      </p>
                    </div>
                    
                    <Tooltip title="删除会话">
                      <button
                        onClick={(e) => handleDeleteSession(e, session.id)}
                        className="opacity-0 group-hover:opacity-100 p-4 text-gray-400 hover:text-red-500 transition-all duration-200"
                      >
                        <Trash2 className="w-12 h-12" />
                      </button>
                    </Tooltip>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

Sidebar.displayName = 'Sidebar';

export default Sidebar;