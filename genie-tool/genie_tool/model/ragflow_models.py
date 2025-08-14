"""
RAGFlow数据模型
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class Dataset:
    """数据集模型"""
    id: str
    name: str
    avatar: str = ""
    description: str = ""
    embedding_model: str = "text-embedding-3-small"
    permission: str = "me"
    chunk_method: str = "manual"
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    document_count: int = 0
    chunk_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> 'Dataset':
        """从字典创建Dataset对象"""
        return cls(**data)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "avatar": self.avatar,
            "description": self.description,
            "embedding_model": self.embedding_model,
            "permission": self.permission,
            "chunk_method": self.chunk_method,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "document_count": self.document_count,
            "chunk_count": self.chunk_count
        }


@dataclass
class Document:
    """文档模型"""
    id: str
    name: str
    dataset_id: str
    type: str = ""
    size: str = ""
    status: str = ""
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    meta_fields: Optional[Dict[str, Any]] = None
    chunk_method: str = "manual"
    parser_config: Optional[Dict[str, Any]] = None
    chunk_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> 'Document':
        """从字典创建Document对象"""
        return cls(**data)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "dataset_id": self.dataset_id,
            "type": self.type,
            "size": self.size,
            "status": self.status,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "meta_fields": self.meta_fields or {},
            "chunk_method": self.chunk_method,
            "parser_config": self.parser_config or {},
            "chunk_count": self.chunk_count
        }


@dataclass
class Chunk:
    """文档块模型"""
    id: str
    document_id: str
    content: str
    important_keywords: Optional[List[str]] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    token_count: int = 0
    similarity: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> 'Chunk':
        """从字典创建Chunk对象"""
        return cls(**data)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "important_keywords": self.important_keywords or [],
            "create_time": self.create_time,
            "update_time": self.update_time,
            "token_count": self.token_count,
            "similarity": self.similarity
        }


@dataclass
class SearchResult:
    """搜索结果模型"""
    chunks: List[Chunk]
    total: int
    query: str
    dataset_ids: Optional[List[str]] = None
    similarity_threshold: float = 0.1
    top_k: int = 10

    @classmethod
    def from_dict(cls, data: dict) -> 'SearchResult':
        """从字典创建SearchResult对象"""
        chunks_data = data.get("chunks", [])
        chunks = [Chunk.from_dict(chunk_data) for chunk_data in chunks_data]
        
        return cls(
            chunks=chunks,
            total=data.get("total", 0),
            query=data.get("query", ""),
            dataset_ids=data.get("dataset_ids", []),
            similarity_threshold=data.get("similarity_threshold", 0.1),
            top_k=data.get("top_k", 10)
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "total": self.total,
            "query": self.query,
            "dataset_ids": self.dataset_ids or [],
            "similarity_threshold": self.similarity_threshold,
            "top_k": self.top_k
        }


@dataclass
class RAGFlowResponse:
    """RAGFlow API响应模型"""
    code: int
    message: str
    data: Any = None
    success: bool = False

    def is_success(self) -> bool:
        """判断响应是否成功"""
        return self.code == 200

    @classmethod
    def from_dict(cls, data: dict) -> 'RAGFlowResponse':
        """从字典创建RAGFlowResponse对象"""
        return cls(
            code=data.get("code", 500),
            message=data.get("message", ""),
            data=data.get("data"),
            success=data.get("success", False)
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data,
            "success": self.success
        }