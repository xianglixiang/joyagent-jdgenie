"""
知识管理API路由
提供RAGFlow集成的FastAPI路由
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from genie_tool.services.knowledge_service import KnowledgeService
from loguru import logger
import os

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# 请求模型定义

class DatasetCreateRequest(BaseModel):
    name: str
    description: str = ""
    embedding_model: str = "text-embedding-3-small"

class DocumentUploadRequest(BaseModel):
    files: List[str]

class SearchRequest(BaseModel):
    query: str
    dataset_ids: Optional[List[str]] = None
    top_k: int = 10
    similarity_threshold: float = 0.1

class BatchOperationRequest(BaseModel):
    operations: List[Dict[str, Any]]

# 知识库路由实现

@router.post("/datasets")
async def create_dataset(request: DatasetCreateRequest):
    """创建知识库数据集"""
    try:
        with KnowledgeService() as service:
            result = service.create_dataset(
                name=request.name,
                description=request.description,
                embedding_model=request.embedding_model
            )
            return result
    except Exception as e:
        logger.error(f"创建数据集失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建数据集失败: {str(e)}")

@router.get("/datasets")
async def list_datasets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: Optional[str] = None
):
    """获取数据集列表"""
    try:
        with KnowledgeService() as service:
            result = service.list_datasets(page=page, page_size=page_size, name=name)
            return result
    except Exception as e:
        logger.error(f"获取数据集列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据集列表失败: {str(e)}")

@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    """获取单个数据集详情"""
    try:
        with KnowledgeService() as service:
            result = service.get_dataset_info(dataset_id)
            return result
    except Exception as e:
        logger.error(f"获取数据集详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据集详情失败: {str(e)}")

@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """删除数据集"""
    try:
        with KnowledgeService() as service:
            result = service.delete_dataset(dataset_id)
            return result
    except Exception as e:
        logger.error(f"删除数据集失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除数据集失败: {str(e)}")

@router.post("/datasets/{dataset_id}/documents")
async def upload_documents(dataset_id: str, request: DocumentUploadRequest):
    """上传文档到数据集"""
    try:
        with KnowledgeService() as service:
            result = service.upload_document(dataset_id, request.files)
            return result
    except Exception as e:
        logger.error(f"上传文档失败: {e}")
        raise HTTPException(status_code=500, detail=f"上传文档失败: {str(e)}")

@router.get("/datasets/{dataset_id}/documents")
async def list_documents(
    dataset_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keywords: Optional[str] = None
):
    """获取数据集中的文档列表"""
    try:
        with KnowledgeService() as service:
            result = service.list_documents(
                dataset_id=dataset_id,
                page=page,
                page_size=page_size,
                keywords=keywords
            )
            return result
    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")

@router.delete("/datasets/{dataset_id}/documents/{document_id}")
async def delete_document(dataset_id: str, document_id: str):
    """删除文档"""
    try:
        with KnowledgeService() as service:
            result = service.delete_document(dataset_id, document_id)
            return result
    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")

@router.post("/search")
async def search_knowledge(request: SearchRequest):
    """知识检索"""
    try:
        with KnowledgeService() as service:
            result = service.search_knowledge(
                query=request.query,
                dataset_ids=request.dataset_ids,
                top_k=request.top_k,
                similarity_threshold=request.similarity_threshold
            )
            return result
    except Exception as e:
        logger.error(f"知识检索失败: {e}")
        raise HTTPException(status_code=500, detail=f"知识检索失败: {str(e)}")

@router.post("/batch")
async def batch_operations(request: BatchOperationRequest):
    """批量处理操作"""
    try:
        with KnowledgeService() as service:
            # 提取数据集ID（假设所有操作都针对同一数据集）
            dataset_id = None
            for operation in request.operations:
                if "dataset_id" in operation:
                    dataset_id = operation["dataset_id"]
                    break
            
            if not dataset_id:
                raise ValueError("批量操作需要指定数据集ID")
            
            result = service.batch_process_documents(dataset_id, request.operations)
            return result
    except Exception as e:
        logger.error(f"批量操作失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量操作失败: {str(e)}")

@router.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 简单的健康检查，可以扩展为检查RAGFlow连接状态
        ragflow_base_url = os.getenv("RAGFLOW_BASE_URL", "http://127.0.0.1:9380")
        ragflow_api_key = os.getenv("RAGFLOW_API_KEY", "")
        
        return {
            "success": True,
            "message": "Knowledge management service is running",
            "data": {
                "ragflow_configured": bool(ragflow_api_key),
                "ragflow_base_url": ragflow_base_url,
                "service_status": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")

@router.get("/stats/{dataset_id}")
async def get_dataset_stats(dataset_id: str):
    """获取数据集统计信息"""
    try:
        with KnowledgeService() as service:
            # 获取数据集基本信息
            dataset_info = service.get_dataset_info(dataset_id)
            
            if not dataset_info["success"]:
                return dataset_info
            
            # 获取文档列表来计算统计信息
            documents_result = service.list_documents(dataset_id, page=1, page_size=1000)
            
            stats = {
                "dataset_id": dataset_id,
                "dataset_name": dataset_info["data"].get("name", ""),
                "document_count": 0,
                "total_chunks": 0
            }
            
            if documents_result["success"]:
                documents = documents_result["data"].get("documents", [])
                stats["document_count"] = len(documents)
                stats["total_chunks"] = sum(doc.get("chunk_count", 0) for doc in documents)
            
            return {
                "success": True,
                "message": "获取数据集统计信息成功",
                "data": stats
            }
    except Exception as e:
        logger.error(f"获取数据集统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据集统计信息失败: {str(e)}")

# 辅助工具接口

@router.post("/tools/validate-config")
async def validate_ragflow_config():
    """验证RAGFlow配置"""
    try:
        with KnowledgeService() as service:
            # 尝试获取数据集列表来验证配置
            result = service.list_datasets(page=1, page_size=1)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "RAGFlow配置有效",
                    "data": {"config_valid": True}
                }
            else:
                return {
                    "success": False,
                    "message": f"RAGFlow配置无效: {result['message']}",
                    "data": {"config_valid": False}
                }
    except Exception as e:
        logger.error(f"验证RAGFlow配置失败: {e}")
        return {
            "success": False,
            "message": f"验证RAGFlow配置失败: {str(e)}",
            "data": {"config_valid": False}
        }