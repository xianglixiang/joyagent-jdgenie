import api from './index';

// 知识库相关的类型定义
export interface Dataset {
  id: string;
  name: string;
  avatar?: string;
  description: string;
  embedding_model: string;
  permission: string;
  chunk_method: string;
  create_time?: string;
  update_time?: string;
  document_count: number;
  chunk_count: number;
}

export interface Document {
  id: string;
  name: string;
  dataset_id: string;
  type: string;
  size: string;
  status: string;
  create_time?: string;
  update_time?: string;
  meta_fields?: Record<string, any>;
  chunk_method: string;
  parser_config?: Record<string, any>;
  chunk_count: number;
}

export interface Chunk {
  id: string;
  document_id: string;
  content: string;
  important_keywords?: string[];
  create_time?: string;
  update_time?: string;
  token_count: number;
  similarity?: number;
}

export interface SearchResult {
  query: string;
  chunks: Chunk[];
  total: number;
  dataset_ids?: string[];
  top_k: number;
  similarity_threshold: number;
}

export interface KnowledgeApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
}

// 数据集相关API
export const datasetApi = {
  // 创建数据集
  create: (data: {
    name: string;
    description?: string;
    embedding_model?: string;
  }) => api.post<KnowledgeApiResponse<Dataset>>('/api/knowledge/datasets', data),

  // 获取数据集列表
  list: (params?: {
    page?: number;
    page_size?: number;
    name?: string;
  }) => api.get<KnowledgeApiResponse<{
    datasets: Dataset[];
    total: number;
    page: number;
    page_size: number;
  }>>('/api/knowledge/datasets', params),

  // 获取单个数据集
  get: (id: string) => api.get<KnowledgeApiResponse<Dataset>>(`/api/knowledge/datasets/${id}`),

  // 删除数据集
  delete: (id: string) => api.delete<KnowledgeApiResponse>(`/api/knowledge/datasets/${id}`),

  // 获取数据集统计信息
  stats: (id: string) => api.get<KnowledgeApiResponse<{
    dataset_id: string;
    dataset_name: string;
    document_count: number;
    total_chunks: number;
  }>>(`/api/knowledge/stats/${id}`),
};

// 文档相关API
export const documentApi = {
  // 上传文档
  upload: (datasetId: string, data: {
    file_path: string;
    name?: string;
  }) => api.post<KnowledgeApiResponse<Document>>(`/api/knowledge/datasets/${datasetId}/documents`, data),

  // 获取文档列表
  list: (datasetId: string, params?: {
    page?: number;
    page_size?: number;
    keywords?: string;
  }) => api.get<KnowledgeApiResponse<{
    documents: Document[];
    total: number;
    page: number;
    page_size: number;
  }>>(`/api/knowledge/datasets/${datasetId}/documents`, params),

  // 获取单个文档
  get: (datasetId: string, documentId: string) => 
    api.get<KnowledgeApiResponse<Document>>(`/api/knowledge/datasets/${datasetId}/documents/${documentId}`),

  // 删除文档
  delete: (datasetId: string, documentId: string) => 
    api.delete<KnowledgeApiResponse>(`/api/knowledge/datasets/${datasetId}/documents/${documentId}`),
};

// 知识检索API
export const searchApi = {
  // 知识检索
  search: (data: {
    query: string;
    dataset_id?: string;
    top_k?: number;
    similarity_threshold?: number;
  }) => api.post<KnowledgeApiResponse<SearchResult>>('/api/knowledge/search', data),
};

// 批量操作API
export const batchApi = {
  // 批量操作
  execute: (operations: Array<{
    type: string;
    [key: string]: any;
  }>) => api.post<KnowledgeApiResponse<{
    results: any[];
    total: number;
    successful: number;
    failed: number;
  }>>('/api/knowledge/batch', { operations }),
};

// 配置和工具API
export const configApi = {
  // 获取配置
  getConfig: () => api.get<KnowledgeApiResponse<{
    ragflow_base_url: string;
    ragflow_timeout: number;
    ragflow_retry_attempts: number;
    ragflow_api_key_configured: boolean;
  }>>('/api/knowledge/config'),

  // 验证配置
  validateConfig: () => api.post<KnowledgeApiResponse<{
    config_valid: boolean;
  }>>('/api/knowledge/tools/validate-config'),

  // 健康检查
  health: () => api.get<KnowledgeApiResponse<{
    ragflow_configured: boolean;
    ragflow_base_url: string;
    service_status: string;
  }>>('/api/knowledge/health'),
};