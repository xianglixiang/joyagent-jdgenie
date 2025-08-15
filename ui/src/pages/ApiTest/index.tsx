import React, { useState } from 'react';
import { Button, Card, Space, Typography, Input, message } from 'antd';
import request from '../../utils/request';
import { TokenManager } from '../../utils/tokenManager';

const { Title, Text } = Typography;

const ApiTestPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [username, setUsername] = useState('testuser');
  const [password, setPassword] = useState('testpass123');
  const [email, setEmail] = useState('test@example.com');

  const testTokenStatus = async () => {
    setLoading(true);
    try {
      const token = TokenManager.getToken();
      const user = TokenManager.getUser();
      const isExpired = TokenManager.isTokenExpired();
      
      const tokenInfo = {
        hasToken: !!token,
        tokenLength: token ? token.length : 0,
        tokenExpired: isExpired,
        user: user,
        tokenPreview: token ? token.substring(0, 20) + '...' : null
      };
      
      console.log('Token状态检查:', tokenInfo);
      setResult(tokenInfo);
      message.success('Token状态检查完成');
    } catch (error: any) {
      console.error('Token状态检查错误:', error);
      setResult({ error: error.message });
      message.error('Token状态检查失败');
    } finally {
      setLoading(false);
    }
  };

  const testBasicAuth = async () => {
    setLoading(true);
    try {
      const response = await request.get('/api/auth/test');
      console.log('基础认证响应:', response);
      setResult(response);
      message.success('基础认证测试成功');
    } catch (error: any) {
      console.error('基础认证错误:', error);
      setResult({ error: error.message });
      message.error('基础认证测试失败');
    } finally {
      setLoading(false);
    }
  };

  const testHealthCheck = async () => {
    setLoading(true);
    try {
      const response = await request.get('/api/test/health');
      setResult(response);
      message.success('健康检查成功');
    } catch (error: any) {
      setResult({ error: error.message });
      message.error('健康检查失败');
    } finally {
      setLoading(false);
    }
  };

  const testLogin = async () => {
    setLoading(true);
    try {
      const response = await request.post('/api/auth/login', {
        username,
        password,
        rememberMe: false
      });
      console.log('登录响应:', response);
      setResult(response);
      message.success('登录测试成功');
    } catch (error: any) {
      console.error('登录错误:', error);
      setResult({ error: error.message, originalError: error });
      message.error('登录测试失败');
    } finally {
      setLoading(false);
    }
  };

  const testRegister = async () => {
    setLoading(true);
    try {
      const response = await request.post('/api/auth/register', {
        username,
        email,
        password,
        confirmPassword: password,
        fullName: '测试用户'
      });
      console.log('注册响应:', response);
      setResult(response);
      message.success('注册测试成功');
    } catch (error: any) {
      console.error('注册错误:', error);
      setResult({ error: error.message, originalError: error });
      message.error('注册测试失败');
    } finally {
      setLoading(false);
    }
  };

  const testTokenValidation = async () => {
    setLoading(true);
    try {
      console.log('开始测试Token验证...');
      
      // 先检查本地Token状态
      const token = TokenManager.getToken();
      const isExpired = TokenManager.isTokenExpired();
      console.log('本地Token检查:', {
        hasToken: !!token,
        tokenLength: token ? token.length : 0,
        isExpired: isExpired,
        tokenPreview: token ? token.substring(0, 30) + '...' : null
      });
      
      const response = await request.post('/api/auth/validate');
      console.log('Token验证响应:', response);
      setResult({
        localTokenInfo: {
          hasToken: !!token,
          tokenLength: token ? token.length : 0,
          isExpired: isExpired
        },
        serverResponse: response
      });
      message.success('Token验证测试成功');
    } catch (error: any) {
      console.error('Token验证错误:', error);
      setResult({ 
        error: error.message, 
        originalError: error,
        tokenStatus: {
          hasToken: !!TokenManager.getToken(),
          tokenExpired: TokenManager.isTokenExpired()
        }
      });
      message.error('Token验证测试失败');
    } finally {
      setLoading(false);
    }
  };

  const testKnowledgeAPI = async () => {
    setLoading(true);
    try {
      console.log('开始测试知识库API...');
      
      // 检查当前Token状态
      const token = TokenManager.getToken();
      console.log('当前Token:', token ? `存在(长度:${token.length})` : '不存在');
      
      const response = await request.get('/api/knowledge/datasets?page=1&page_size=10');
      console.log('知识库API响应:', response);
      setResult(response);
      message.success('知识库API测试成功');
    } catch (error: any) {
      console.error('知识库API错误:', error);
      setResult({ 
        error: error.message, 
        originalError: error,
        tokenStatus: {
          hasToken: !!TokenManager.getToken(),
          tokenExpired: TokenManager.isTokenExpired()
        }
      });
      message.error('知识库API测试失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto' }}>
      <Title level={2}>API 测试页面</Title>
      
      <Card title="测试参数" style={{ marginBottom: '16px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text>用户名:</Text>
            <Input 
              value={username} 
              onChange={(e) => setUsername(e.target.value)}
              style={{ marginLeft: '8px', width: '200px' }}
            />
          </div>
          <div>
            <Text>密码:</Text>
            <Input.Password 
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              style={{ marginLeft: '8px', width: '200px' }}
            />
          </div>
          <div>
            <Text>邮箱:</Text>
            <Input 
              value={email} 
              onChange={(e) => setEmail(e.target.value)}
              style={{ marginLeft: '8px', width: '200px' }}
            />
          </div>
        </Space>
      </Card>

      <Card title="API 测试" style={{ marginBottom: '16px' }}>
        <Space wrap>
          <Button onClick={testHealthCheck} loading={loading}>
            健康检查
          </Button>
          <Button onClick={testTokenStatus} loading={loading}>
            检查Token状态
          </Button>
          <Button onClick={testBasicAuth} loading={loading}>
            基础认证测试
          </Button>
          <Button onClick={testRegister} loading={loading} type="primary">
            测试注册
          </Button>
          <Button onClick={testLogin} loading={loading} type="primary">
            测试登录
          </Button>
          <Button onClick={testTokenValidation} loading={loading}>
            验证Token
          </Button>
          <Button onClick={testKnowledgeAPI} loading={loading} type="default">
            测试知识库API
          </Button>
        </Space>
      </Card>

      {result && (
        <Card title="响应结果">
          <pre style={{ 
            background: '#f5f5f5', 
            padding: '16px', 
            borderRadius: '4px',
            overflow: 'auto',
            maxHeight: '400px'
          }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  );
};

export default ApiTestPage;