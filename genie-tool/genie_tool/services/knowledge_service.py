"""
知识管理服务
提供RAGFlow知识库操作的业务逻辑层
"""

from typing import Dict, List, Optional, Any
from genie_tool.api.ragflow_client import RAGFlowClient
from genie_tool.model.ragflow_models import Dataset, Document, Chunk, SearchResult, RAGFlowResponse
from genie_tool.util.log_util import setup_logger
import os

logger = setup_logger(__name__)


class KnowledgeService:
    """知识管理服务类"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.ragflow_client = RAGFlowClient(base_url, api_key)
    
    def close(self):
        """关闭服务连接"""
        self.ragflow_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # 数据集管理服务
    
    def create_dataset(self, name: str, description: str = "", embedding_model: str = "text-embedding-3-small") -> Dict:
        """创建知识库数据集"""
        try:
            result = self.ragflow_client.create_dataset(
                name=name,
                description=description,
                embedding_model=embedding_model
            )
            
            if result.get("code") == 200:
                logger.info(f"成功创建数据集: {name}")
                return {
                    "success": True,
                    "message": "数据集创建成功",
                    "data": result.get("data")
                }
            else:
                logger.error(f"创建数据集失败: {result.get('message')}")
                return {
                    "success": False,
                    "message": f"创建数据集失败: {result.get('message')}",
                    "data": None
                }
        except Exception as e:
            logger.error(f"创建数据集异常: {e}")
            return {
                "success": False,
                "message": f"创建数据集异常: {str(e)}",
                "data": None
            }
    
    def list_datasets(self, page: int = 1, page_size: int = 20, name: str = None) -> Dict:
        """获取数据集列表"""
        try:
            result = self.ragflow_client.list_datasets(page=page, page_size=page_size, name=name)
            
            if result.get("code") == 200:
                data = result.get("data", {})
                datasets = []
                
                # 转换数据格式
                for item in data.get("data", []):
                    try:
                        dataset = Dataset.from_dict(item)
                        datasets.append(dataset.to_dict())
                    except Exception as e:
                        logger.warning(f"转换数据集数据失败: {e}")
                        datasets.append(item)
                
                return {
                    "success": True,
                    "message": "获取数据集列表成功",
                    "data": {
                        "datasets": datasets,
                        "total": data.get("total", 0),
                        "page": page,
                        "page_size": page_size
                    }
                }
            else:
                logger.error(f"获取数据集列表失败: {result.get('message')}")
                return {
                    "success": False,
                    "message": f"获取数据集列表失败: {result.get('message')}",
                    "data": None
                }
        except Exception as e:
            logger.error(f"获取数据集列表异常: {e}")
            return {
                "success": False,
                "message": f"获取数据集列表异常: {str(e)}",
                "data": None
            }
    
    def delete_dataset(self, dataset_id: str) -> Dict:
        """删除数据集"""
        try:
            result = self.ragflow_client.delete_datasets([dataset_id])
            
            if result.get("code") == 200:
                logger.info(f"成功删除数据集: {dataset_id}")
                return {
                    "success": True,
                    "message": "数据集删除成功",
                    "data": None
                }
            else:
                logger.error(f"删除数据集失败: {result.get('message')}")
                return {
                    "success": False,
                    "message": f"删除数据集失败: {result.get('message')}",
                    "data": None
                }
        except Exception as e:
            logger.error(f"删除数据集异常: {e}")
            return {
                "success": False,
                "message": f"删除数据集异常: {str(e)}",
                "data": None
            }
    
    # 文档管理服务
    
    def upload_document(self, dataset_id: str, file_paths: List[str]) -> Dict:
        """上传文档到数据集"""
        try:
            result = self.ragflow_client.upload_documents(dataset_id, file_paths)
            
            if result.get("code") == 200:
                logger.info(f"成功上传文档到数据集 {dataset_id}: {file_paths}")
                return {
                    "success": True,
                    "message": "文档上传成功",
                    "data": result.get("data")
                }
            else:
                logger.error(f"上传文档失败: {result.get('message')}")
                return {
                    "success": False,
                    "message": f"上传文档失败: {result.get('message')}",
                    "data": None
                }
        except Exception as e:
            logger.error(f"上传文档异常: {e}")
            return {
                "success": False,
                "message": f"上传文档异常: {str(e)}",
                "data": None
            }
    
    def list_documents(self, dataset_id: str, page: int = 1, page_size: int = 20, keywords: str = None) -> Dict:
        """获取文档列表"""
        try:
            result = self.ragflow_client.list_documents(
                dataset_id=dataset_id,
                page=page,
                page_size=page_size,
                keywords=keywords
            )
            
            if result.get("code") == 200:
                data = result.get("data", {})
                documents = []
                
                # 转换数据格式
                for item in data.get("data", []):
                    try:
                        document = Document.from_dict(item)
                        documents.append(document.to_dict())
                    except Exception as e:
                        logger.warning(f"转换文档数据失败: {e}")
                        documents.append(item)
                
                return {
                    "success": True,
                    "message": "获取文档列表成功",
                    "data": {
                        "documents": documents,
                        "total": data.get("total", 0),
                        "page": page,
                        "page_size": page_size
                    }
                }
            else:
                logger.error(f"获取文档列表失败: {result.get('message')}")
                return {
                    "success": False,
                    "message": f"获取文档列表失败: {result.get('message')}",
                    "data": None
                }
        except Exception as e:
            logger.error(f"获取文档列表异常: {e}")
            return {
                "success": False,
                "message": f"获取文档列表异常: {str(e)}",
                "data": None
            }
    
    def delete_document(self, dataset_id: str, document_id: str) -> Dict:
        """删除文档"""
        try:
            result = self.ragflow_client.delete_documents(dataset_id, [document_id])
            
            if result.get("code") == 200:
                logger.info(f"成功删除文档: {document_id}")
                return {
                    "success": True,
                    "message": "文档删除成功",
                    "data": None
                }
            else:
                logger.error(f"删除文档失败: {result.get('message')}")
                return {
                    "success": False,
                    "message": f"删除文档失败: {result.get('message')}",
                    "data": None
                }
        except Exception as e:
            logger.error(f"删除文档异常: {e}")
            return {
                "success": False,
                "message": f"删除文档异常: {str(e)}",
                "data": None
            }
    
    # 知识检索服务
    
    def search_knowledge(self, query: str, dataset_ids: List[str] = None, top_k: int = 10, similarity_threshold: float = 0.1) -> Dict:
        """知识检索"""
        try:
            result = self.ragflow_client.search_knowledge(
                query=query,
                dataset_ids=dataset_ids,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            if result.get("code") == 200:
                data = result.get("data", {})
                
                # 转换搜索结果
                chunks = []
                for chunk_data in data.get("chunks", []):
                    try:
                        chunk = Chunk.from_dict(chunk_data)
                        chunks.append(chunk.to_dict())
                    except Exception as e:
                        logger.warning(f"转换搜索结果数据失败: {e}")
                        chunks.append(chunk_data)
                
                search_result = {
                    "query": query,
                    "chunks": chunks,
                    "total": len(chunks),
                    "dataset_ids": dataset_ids or [],
                    "top_k": top_k,
                    "similarity_threshold": similarity_threshold
                }
                
                logger.info(f"知识检索成功，查询: {query}, 结果数量: {len(chunks)}")
                return {
                    "success": True,
                    "message": "知识检索成功",
                    "data": search_result
                }
            else:
                logger.error(f"知识检索失败: {result.get('message')}")
                return {
                    "success": False,
                    "message": f"知识检索失败: {result.get('message')}",
                    "data": None
                }
        except Exception as e:
            logger.error(f"知识检索异常: {e}")
            return {
                "success": False,
                "message": f"知识检索异常: {str(e)}",
                "data": None
            }
    
    # 辅助方法
    
    def get_dataset_info(self, dataset_id: str) -> Dict:
        """获取数据集详细信息"""
        try:
            result = self.ragflow_client.get_dataset(dataset_id)
            
            if result.get("code") == 200:
                data = result.get("data", {})
                try:
                    dataset = Dataset.from_dict(data)
                    return {
                        "success": True,
                        "message": "获取数据集信息成功",
                        "data": dataset.to_dict()
                    }
                except Exception as e:
                    logger.warning(f"转换数据集信息失败: {e}")
                    return {
                        "success": True,
                        "message": "获取数据集信息成功",
                        "data": data
                    }
            else:
                logger.error(f"获取数据集信息失败: {result.get('message')}")
                return {
                    "success": False,
                    "message": f"获取数据集信息失败: {result.get('message')}",
                    "data": None
                }
        except Exception as e:
            logger.error(f"获取数据集信息异常: {e}")
            return {
                "success": False,
                "message": f"获取数据集信息异常: {str(e)}",
                "data": None
            }
    
    def batch_process_documents(self, dataset_id: str, operations: List[Dict]) -> Dict:
        """批量处理文档操作"""
        results = []
        
        for operation in operations:
            op_type = operation.get("type")
            
            try:
                if op_type == "upload":
                    result = self.upload_document(dataset_id, operation.get("files", []))
                elif op_type == "delete":
                    result = self.delete_document(dataset_id, operation.get("document_id"))
                else:
                    result = {
                        "success": False,
                        "message": f"不支持的操作类型: {op_type}",
                        "data": None
                    }
                
                results.append({
                    "operation": operation,
                    "result": result
                })
            except Exception as e:
                logger.error(f"批量操作异常: {e}")
                results.append({
                    "operation": operation,
                    "result": {
                        "success": False,
                        "message": f"操作异常: {str(e)}",
                        "data": None
                    }
                })
        
        successful_count = sum(1 for r in results if r["result"]["success"])
        
        return {
            "success": True,
            "message": f"批量操作完成，成功: {successful_count}/{len(results)}",
            "data": {
                "results": results,
                "total": len(results),
                "successful": successful_count,
                "failed": len(results) - successful_count
            }
        }