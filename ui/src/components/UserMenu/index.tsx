import React from 'react';
import { Dropdown, Avatar, Space, Typography, Divider, Button } from 'antd';
import { 
  UserOutlined, 
  SettingOutlined, 
  LogoutOutlined,
  CrownOutlined,
  ApiOutlined
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './style.css';

const { Text } = Typography;

/**
 * 用户菜单组件 - 显示在Header右侧
 */
const UserMenu: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  if (!isAuthenticated || !user) {
    return (
      <Button type="primary" onClick={() => navigate('/login')}>
        登录
      </Button>
    );
  }

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    switch (key) {
      case 'profile':
        // TODO: 导航到用户设置页面
        console.log('打开用户设置');
        break;
      case 'settings':
        // TODO: 导航到系统设置页面
        console.log('打开系统设置');
        break;
      case 'logout':
        handleLogout();
        break;
      default:
        break;
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'ADMIN':
        return <CrownOutlined style={{ color: '#f39c12' }} />;
      case 'USER':
        return <UserOutlined style={{ color: '#3498db' }} />;
      default:
        return <UserOutlined style={{ color: '#95a5a6' }} />;
    }
  };

  const getRoleText = (role: string) => {
    switch (role) {
      case 'ADMIN':
        return '管理员';
      case 'USER':
        return '用户';
      case 'GUEST':
        return '访客';
      default:
        return '未知';
    }
  };

  const getQuotaColor = (used: number, total: number) => {
    const percentage = (used / total) * 100;
    if (percentage >= 90) return '#e74c3c';
    if (percentage >= 70) return '#f39c12';
    return '#27ae60';
  };

  const menuItems: MenuProps['items'] = [
    {
      key: 'user-info',
      label: (
        <div className="user-menu-header">
          <div className="user-avatar-large">
            <Avatar 
              size={40} 
              src={user.avatar} 
              icon={<UserOutlined />}
              style={{ backgroundColor: '#1890ff' }}
            />
          </div>
          <div className="user-info">
            <div className="user-name">
              <Text strong>{user.fullName || user.username}</Text>
            </div>
            <div className="user-role">
              <Space size={4}>
                {getRoleIcon(user.role)}
                <Text type="secondary" className="role-text">
                  {getRoleText(user.role)}
                </Text>
              </Space>
            </div>
            <div className="user-email">
              <Text type="secondary" className="email-text">
                {user.email}
              </Text>
            </div>
          </div>
        </div>
      ),
      disabled: true
    },
    {
      type: 'divider'
    },
    {
      key: 'quota-info',
      label: (
        <div className="quota-info">
          <Space>
            <ApiOutlined />
            <Text type="secondary">今日配额:</Text>
            <Text 
              style={{ 
                color: getQuotaColor(user.apiQuotaUsed || 0, user.apiQuotaDaily || 100) 
              }}
            >
              {user.apiQuotaUsed || 0} / {user.apiQuotaDaily || 100}
            </Text>
          </Space>
        </div>
      ),
      disabled: true
    },
    {
      type: 'divider'
    },
    {
      key: 'profile',
      label: (
        <Space>
          <UserOutlined />
          个人设置
        </Space>
      )
    },
    {
      key: 'settings',
      label: (
        <Space>
          <SettingOutlined />
          系统设置
        </Space>
      )
    },
    {
      type: 'divider'
    },
    {
      key: 'logout',
      label: (
        <Space>
          <LogoutOutlined />
          <Text type="danger">退出登录</Text>
        </Space>
      )
    }
  ];

  return (
    <Dropdown
      menu={{ 
        items: menuItems, 
        onClick: handleMenuClick,
        className: 'user-dropdown-menu'
      }}
      placement="bottomRight"
      arrow
      trigger={['click']}
    >
      <div className="user-menu-trigger">
        <Space size={8}>
          <Avatar 
            size={32} 
            src={user.avatar} 
            icon={<UserOutlined />}
            style={{ backgroundColor: '#1890ff', cursor: 'pointer' }}
          />
          <div className="user-greeting">
            <Text className="greeting-text">
              Hi, {user.fullName || user.username}
            </Text>
          </div>
        </Space>
      </div>
    </Dropdown>
  );
};

export default UserMenu;