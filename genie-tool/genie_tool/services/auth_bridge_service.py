# -*- coding: utf-8 -*-
# =====================
# 认证桥接服务 - 连接Java后端和Python服务
# Author: AI Assistant
# Date: 2025/8/14
# =====================
from typing import Optional, Dict, Any
import httpx
import asyncio
from loguru import logger

from genie_tool.db.models.user import User, UserRole, UserStatus
from genie_tool.services.user_service import UserService


class AuthBridgeService:
    """认证桥接服务 - 同步Java后端用户数据到Python数据库"""
    
    def __init__(self, backend_url: str = "http://localhost:8080"):
        self.backend_url = backend_url
        self.user_service = UserService()
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def sync_user_from_backend(self, user_id: int, token: str) -> Optional[User]:
        """从Java后端同步用户信息到Python数据库"""
        try:
            # 从后端获取用户信息
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{self.backend_url}/api/auth/me", headers=headers)
            
            if response.status_code != 200:
                logger.error(f"获取用户信息失败: {response.status_code}")
                return None
            
            user_data = response.json().get("data")
            if not user_data:
                logger.error("后端返回的用户数据为空")
                return None
            
            # 检查Python数据库中是否存在该用户
            existing_user = await self.user_service.get_user_by_id(user_id)
            
            if existing_user:
                # 更新现有用户信息
                update_data = {
                    "username": user_data.get("username"),
                    "email": user_data.get("email"),
                    "full_name": user_data.get("fullName"),
                    "role": self._convert_role(user_data.get("role")),
                    "status": self._convert_status(user_data.get("status")),
                    "api_quota_daily": user_data.get("apiQuotaDaily", 100),
                    "api_quota_used": user_data.get("apiQuotaUsed", 0)
                }
                return await self.user_service.update_user_profile(user_id, update_data)
            else:
                # 创建新用户（密码哈希暂时设为空，因为认证在Java端处理）
                user = await self.user_service.create_user(
                    username=user_data.get("username"),
                    email=user_data.get("email"),
                    password="__backend_managed__",  # 标记密码由后端管理
                    full_name=user_data.get("fullName"),
                    role=self._convert_role(user_data.get("role"))
                )
                
                if user:
                    # 更新用户ID以匹配后端
                    await self.user_service.user_repo.update(user.id, {"id": user_id})
                
                return user
                
        except Exception as e:
            logger.error(f"同步用户信息失败: {e}")
            return None
    
    async def validate_token_with_backend(self, token: str) -> Optional[Dict[str, Any]]:
        """向Java后端验证Token"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post(f"{self.backend_url}/api/auth/validate", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("valid"):
                    return {
                        "user_id": result.get("userId"),
                        "username": result.get("username"),
                        "role": result.get("role"),
                        "valid": True
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Token验证失败: {e}")
            return None
    
    async def get_or_sync_user(self, user_id: int, token: str) -> Optional[User]:
        """获取用户信息，如果不存在则从后端同步"""
        # 先从本地数据库查找
        user = await self.user_service.get_user_by_id(user_id)
        
        if not user:
            # 本地不存在，从后端同步
            logger.info(f"用户 {user_id} 不存在，从后端同步")
            user = await self.sync_user_from_backend(user_id, token)
        
        return user
    
    async def update_user_activity(self, user_id: int) -> bool:
        """更新用户活动时间"""
        try:
            user = await self.user_service.get_user_by_id(user_id)
            if user:
                await self.user_service.user_repo.update_last_login(user_id)
                return True
            return False
        except Exception as e:
            logger.error(f"更新用户活动时间失败: {e}")
            return False
    
    def _convert_role(self, backend_role: str) -> UserRole:
        """转换后端角色到Python枚举"""
        role_mapping = {
            "ADMIN": UserRole.ADMIN,
            "USER": UserRole.USER,
            "GUEST": UserRole.GUEST
        }
        return role_mapping.get(backend_role, UserRole.USER)
    
    def _convert_status(self, backend_status: str) -> UserStatus:
        """转换后端状态到Python枚举"""
        status_mapping = {
            "ACTIVE": UserStatus.ACTIVE,
            "INACTIVE": UserStatus.INACTIVE,
            "SUSPENDED": UserStatus.SUSPENDED
        }
        return status_mapping.get(backend_status, UserStatus.ACTIVE)
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()


# 全局桥接服务实例
auth_bridge = AuthBridgeService()


async def get_user_from_request_context(request_headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """从请求上下文获取用户信息"""
    auth_header = request_headers.get("Authorization") or request_headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    # 验证Token并获取用户信息
    token_info = await auth_bridge.validate_token_with_backend(token)
    if not token_info or not token_info.get("valid"):
        return None
    
    user_id = token_info.get("user_id")
    if not user_id:
        return None
    
    # 获取或同步用户信息
    user = await auth_bridge.get_or_sync_user(user_id, token)
    if not user:
        return None
    
    return {
        "user_id": user.id,
        "username": user.username,
        "role": user.role.value,
        "user": user
    }