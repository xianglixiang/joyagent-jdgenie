import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Checkbox, Typography, Space, Divider, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import type { LoginRequest, RegisterRequest } from '../../types/auth';
import './style.css';

const { Title, Text, Link } = Typography;

const LoginPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const { login, register, isAuthenticated, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // 如果已登录，重定向到主页
  useEffect(() => {
    if (isAuthenticated) {
      const from = (location.state as any)?.from?.pathname || '/';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  // 清除错误信息
  useEffect(() => {
    clearError();
  }, [isLogin]);

  const handleLogin = async (values: LoginRequest) => {
    setLoading(true);
    try {
      const success = await login(values);
      if (success) {
        message.success('登录成功！');
        const from = (location.state as any)?.from?.pathname || '/';
        navigate(from, { replace: true });
      }
    } catch (error) {
      // 错误已在AuthContext中处理
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values: RegisterRequest) => {
    if (values.password !== values.confirmPassword) {
      message.error('两次输入的密码不一致');
      return;
    }

    setLoading(true);
    try {
      const success = await register(values);
      if (success) {
        message.success('注册成功！');
        const from = (location.state as any)?.from?.pathname || '/';
        navigate(from, { replace: true });
      }
    } catch (error) {
      // 错误已在AuthContext中处理
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    clearError();
  };

  return (
    <div className="login-container">
      <div className="login-background"></div>
      <Card className="login-card" bordered={false}>
        <div className="login-header">
          <div className="logo">
            <img src="/src/assets/logo.png" alt="Genie" className="logo-image" />
          </div>
          <Title level={2} className="login-title">
            {isLogin ? '欢迎回来' : '创建账户'}
          </Title>
          <Text type="secondary" className="login-subtitle">
            {isLogin ? '登录您的账户以继续使用 JoyAgent-JDGenie' : '注册新账户开始您的智能助手之旅'}
          </Text>
        </div>

        <Divider />

        {error && (
          <div className="error-message">
            <Text type="danger">{error}</Text>
          </div>
        )}

        {isLogin ? (
          <Form
            name="login"
            size="large"
            onFinish={handleLogin}
            autoComplete="off"
            layout="vertical"
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: '请输入用户名' }]}
            >
              <Input 
                prefix={<UserOutlined />} 
                placeholder="用户名" 
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password 
                prefix={<LockOutlined />} 
                placeholder="密码"
                autoComplete="current-password"
              />
            </Form.Item>

            <Form.Item>
              <div className="login-options">
                <Form.Item name="rememberMe" valuePropName="checked" noStyle>
                  <Checkbox>记住我</Checkbox>
                </Form.Item>
                <Link className="forgot-password">忘记密码？</Link>
              </div>
            </Form.Item>

            <Form.Item>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading}
                block
                size="large"
              >
                登录
              </Button>
            </Form.Item>
          </Form>
        ) : (
          <Form
            name="register"
            size="large"
            onFinish={handleRegister}
            autoComplete="off"
            layout="vertical"
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, message: '用户名至少3个字符' }
              ]}
            >
              <Input 
                prefix={<UserOutlined />} 
                placeholder="用户名" 
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '请输入有效的邮箱地址' }
              ]}
            >
              <Input 
                prefix={<MailOutlined />} 
                placeholder="邮箱" 
                autoComplete="email"
              />
            </Form.Item>

            <Form.Item
              name="fullName"
              rules={[{ required: false }]}
            >
              <Input 
                placeholder="姓名（可选）" 
                autoComplete="name"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' }
              ]}
            >
              <Input.Password 
                prefix={<LockOutlined />} 
                placeholder="密码"
                autoComplete="new-password"
              />
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              rules={[
                { required: true, message: '请确认密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'));
                  },
                }),
              ]}
            >
              <Input.Password 
                prefix={<LockOutlined />} 
                placeholder="确认密码"
                autoComplete="new-password"
              />
            </Form.Item>

            <Form.Item>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading}
                block
                size="large"
              >
                注册
              </Button>
            </Form.Item>
          </Form>
        )}

        <div className="login-footer">
          <Space>
            <Text type="secondary">
              {isLogin ? '还没有账户？' : '已有账户？'}
            </Text>
            <Link onClick={toggleMode}>
              {isLogin ? '立即注册' : '立即登录'}
            </Link>
          </Space>
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;