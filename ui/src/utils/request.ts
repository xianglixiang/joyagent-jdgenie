import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { showMessage } from './utils';
import { TokenManager } from './tokenManager';

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: SERVICE_BASE_URL,
  timeout: 10000,
  headers: {'Content-Type': 'application/json',},
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加JWT Token到请求头
    const token = TokenManager.getToken();
    const isExpired = TokenManager.isTokenExpired();
    
    console.log('请求拦截器 - 检查Token状态:', {
      url: config.url,
      hasToken: !!token,
      tokenLength: token ? token.length : 0,
      isExpired: isExpired,
      tokenPreview: token ? token.substring(0, 20) + '...' : null
    });
    
    if (token && !isExpired) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('请求拦截器 - 已添加Authorization header');
    } else {
      console.log('请求拦截器 - 未添加Authorization header, 原因:', 
        !token ? '无Token' : 'Token已过期');
    }
    
    return config;
  },
  (error) => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

const noAuth = (url?: string) => {
  // 清除认证信息
  TokenManager.clearAll();
  showMessage()?.error('登录已过期，请重新登录');
  
  // 重定向到登录页面或指定URL
  if (url) {
    location.href = url;
  } else {
    // 重定向到登录页面
    window.location.hash = '#/login';
  }
};

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const { data, status } = response;

    if (status === 200) {
      // 处理新的后端数据结构
      if (data.success !== undefined) {
        // 新的统一响应格式
        if (data.success) {
          return data;
        } else {
          showMessage()?.error(data.message || '请求失败');
          return Promise.reject(new Error(data.message || '请求失败'));
        }
      }
      // 兼容旧的响应格式
      else if (data.code === 200) {
        return data.data;
      } else if (data.code === 401) {
        noAuth(data.redirectUrl);
      } else {
        showMessage()?.error(data.msg || '请求失败');
        return Promise.reject(new Error(data.msg || '请求失败'));
      }
    }

    return response;
  },
  (error) => {
    console.error('响应错误:', error);

    const message = showMessage();
    if (error.response) {
      const { status, data: resData } = error.response;

      switch (status) {
        case 401:
          // 未授权，清除token并跳转登录
          noAuth(resData.redirectUrl);
          break;
        case 403:
          message?.error(error.message || '没有权限访问');
          break;
        case 404:
          message?.error(error.message || '请求的资源不存在');
          break;
        case 500:
          message?.error(error.message || '服务器内部错误');
          break;
        default:
          message?.error(error.message || `请求失败，状态码: ${status}`);
      }
    } else if (error.request) {
      message?.error(error.message || '网络错误，请检查网络连接');
    } else {
      message?.error('请求配置错误');
    }

    return Promise.reject(error);
  }
);

export default request;