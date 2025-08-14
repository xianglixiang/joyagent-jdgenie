"""
RAGFlow HTTP客户端
封装RAGFlow API调用
"""

import httpx
import json
from typing import Dict, List, Optional, Any
from loguru import logger
import os


class RAGFlowClient:
    """RAGFlow API客户端"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv("RAGFLOW_BASE_URL", "http://127.0.0.1:9380")
        self.api_key = api_key or os.getenv("RAGFLOW_API_KEY", "")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.client = httpx.Client(timeout=30.0)
    
    def close(self):
        """关闭客户端连接"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """发送HTTP请求的通用方法"""
        try:
            url = f"{self.base_url}/api/v1/{endpoint}"
            response = self.client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params
            )
            
            result = response.json()
            if response.status_code != 200:
                logger.error(f"RAGFlow API错误: {response.status_code} - {result}")
            
            return result
        except Exception as e:
            logger.error(f"RAGFlow请求失败: {e}")
            return {"code": 500, "message": f"请求失败: {str(e)}"}
    
    # 数据集管理API
    
    def create_dataset(self, name: str, description: str = "", embedding_model: str = "text-embedding-3-small",
                      permission: str = "me", chunk_method: str = "manual") -> Dict:
        """创建数据集"""
        data = {
            "name": name,
            "description": description,
            "embedding_model": embedding_model,
            "permission": permission,
            "chunk_method": chunk_method
        }
        return self._make_request("POST", "datasets", data)
    
    def list_datasets(self, page: int = 1, page_size: int = 20, name: str = None) -> Dict:
        """列出数据集"""
        params = {"page": page, "page_size": page_size}
        if name:
            params["name"] = name
        return self._make_request("GET", "datasets", params=params)
    
    def get_dataset(self, dataset_id: str) -> Dict:
        """获取单个数据集"""
        return self._make_request("GET", f"datasets/{dataset_id}")
    
    def update_dataset(self, dataset_id: str, name: str = None, description: str = None,
                      embedding_model: str = None, permission: str = None, chunk_method: str = None) -> Dict:
        """更新数据集"""
        data = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if embedding_model:
            data["embedding_model"] = embedding_model
        if permission:
            data["permission"] = permission
        if chunk_method:
            data["chunk_method"] = chunk_method
        
        return self._make_request("PUT", f"datasets/{dataset_id}", data)
    
    def delete_datasets(self, dataset_ids: List[str]) -> Dict:
        """删除数据集"""
        data = {"ids": dataset_ids}
        return self._make_request("DELETE", "datasets", data)
    
    # 文档管理API
    
    def upload_documents(self, dataset_id: str, files: List[str]) -> Dict:
        """上传文档到数据集（简化实现）"""
        # 这里简化处理，实际应该使用multipart/form-data上传文件
        data = {"files": files}
        return self._make_request("POST", f"datasets/{dataset_id}/documents", data)
    
    def list_documents(self, dataset_id: str, page: int = 1, page_size: int = 20, 
                      keywords: str = None, name: str = None) -> Dict:
        """列出文档"""
        params = {"page": page, "page_size": page_size}
        if keywords:
            params["keywords"] = keywords
        if name:
            params["name"] = name
        
        return self._make_request("GET", f"datasets/{dataset_id}/documents", params=params)
    
    def get_document(self, dataset_id: str, document_id: str) -> Dict:
        """获取单个文档"""
        return self._make_request("GET", f"datasets/{dataset_id}/documents/{document_id}")
    
    def update_document(self, dataset_id: str, document_id: str, name: str = None, 
                       meta_fields: Dict = None, chunk_method: str = None, parser_config: Dict = None) -> Dict:
        """更新文档"""
        data = {}
        if name:
            data["name"] = name
        if meta_fields:
            data["meta_fields"] = meta_fields
        if chunk_method:
            data["chunk_method"] = chunk_method
        if parser_config:
            data["parser_config"] = parser_config
        
        return self._make_request("PUT", f"datasets/{dataset_id}/documents/{document_id}", data)
    
    def delete_documents(self, dataset_id: str, document_ids: List[str]) -> Dict:
        """删除文档"""
        data = {"ids": document_ids}
        return self._make_request("DELETE", f"datasets/{dataset_id}/documents", data)
    
    # 块管理API
    
    def add_chunk(self, dataset_id: str, document_id: str, content: str, important_keywords: List[str] = None) -> Dict:
        """添加文档块"""
        data = {"content": content}
        if important_keywords:
            data["important_keywords"] = important_keywords
        
        return self._make_request("POST", f"datasets/{dataset_id}/documents/{document_id}/chunks", data)
    
    def list_chunks(self, dataset_id: str, document_id: str, page: int = 1, page_size: int = 20, keywords: str = None) -> Dict:
        """列出文档块"""
        params = {"page": page, "page_size": page_size}
        if keywords:
            params["keywords"] = keywords
        
        return self._make_request("GET", f"datasets/{dataset_id}/documents/{document_id}/chunks", params=params)
    
    def get_chunk(self, dataset_id: str, document_id: str, chunk_id: str) -> Dict:
        """获取单个文档块"""
        return self._make_request("GET", f"datasets/{dataset_id}/documents/{document_id}/chunks/{chunk_id}")
    
    def update_chunk(self, dataset_id: str, document_id: str, chunk_id: str, content: str = None, important_keywords: List[str] = None) -> Dict:
        """更新文档块"""
        data = {}
        if content:
            data["content"] = content
        if important_keywords:
            data["important_keywords"] = important_keywords
        
        return self._make_request("PUT", f"datasets/{dataset_id}/documents/{document_id}/chunks/{chunk_id}", data)
    
    def delete_chunks(self, dataset_id: str, document_id: str, chunk_ids: List[str]) -> Dict:
        """删除文档块"""
        data = {"ids": chunk_ids}
        return self._make_request("DELETE", f"datasets/{dataset_id}/documents/{document_id}/chunks", data)
    
    # 知识检索API
    
    def search_knowledge(self, query: str, dataset_ids: List[str] = None, top_k: int = 10, similarity_threshold: float = 0.1) -> Dict:
        """知识检索"""
        data = {
            "query": query,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold
        }
        if dataset_ids:
            data["dataset_ids"] = dataset_ids
        
        return self._make_request("POST", "search", data)