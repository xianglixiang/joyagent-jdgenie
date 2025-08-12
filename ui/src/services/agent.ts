import api from './index';

export const agentApi = {
  loginIn: () =>
    api.get(`/web/api/login`),
  getWhiteList: () => api.get(`/web/api/getWhiteList`),
  apply: (data:string) => api.get(`/web/api/genie/apply`, {"email": data}),
  
  // LLM模型管理相关API (这些API直接返回数据，不包装在统一格式中)
  getAllModels: () => 
    fetch(`${process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:8080' : ''}/api/llm/models`)
      .then(res => res.json()),
  getCurrentModel: () => 
    fetch(`${process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:8080' : ''}/api/llm/current`)
      .then(res => res.json()),
  switchModel: (modelName: string) => 
    fetch(`${process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:8080' : ''}/api/llm/switch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ modelName }),
    }).then(res => res.json()),
};
