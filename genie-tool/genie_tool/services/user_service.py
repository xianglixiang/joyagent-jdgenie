# -*- coding: utf-8 -*-
# =====================
# 用户服务
# Author: AI Assistant
# Date: 2025/8/14
# =====================
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib
import secrets
from loguru import logger

from genie_tool.db.models.user import User, UserRole, UserStatus, UserProfile
from genie_tool.db.repositories.user_repository import UserRepository


class UserService:
    """用户服务 - 与Java后端的UserService同步"""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户凭证"""
        try:
            user = await self.user_repo.get_by_username(username)
            if not user:
                return None
            
            if user.status != UserStatus.ACTIVE:
                logger.warning(f"用户 {username} 状态不是活跃状态: {user.status}")
                return None
            
            # 验证密码
            if self._verify_password(password, user.password_hash):
                # 更新最后登录时间
                await self.user_repo.update_last_login(user.id)
                logger.info(f"用户 {username} 登录成功")
                return user
            else:
                logger.warning(f"用户 {username} 密码验证失败")
                return None
                
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return None
    
    async def create_user(self, 
                         username: str, 
                         email: str, 
                         password: str,
                         full_name: Optional[str] = None,
                         role: UserRole = UserRole.USER) -> Optional[User]:
        """创建新用户"""
        try:
            # 检查用户名是否已存在
            existing_user = await self.user_repo.get_by_username(username)
            if existing_user:
                logger.warning(f"用户名 {username} 已存在")
                return None
            
            # 检查邮箱是否已存在
            existing_email = await self.user_repo.get_by_email(email)
            if existing_email:
                logger.warning(f"邮箱 {email} 已存在")
                return None
            
            # 创建用户
            user_data = {
                "username": username,
                "email": email,
                "password_hash": self._hash_password(password),
                "full_name": full_name,
                "role": role,
                "status": UserStatus.ACTIVE,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "api_quota_daily": 100,
                "api_quota_used": 0
            }
            
            user = await self.user_repo.create(user_data)
            logger.info(f"用户 {username} 创建成功")
            return user
            
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return await self.user_repo.get_by_id(user_id)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return await self.user_repo.get_by_username(username)
    
    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """获取用户资料（不包含敏感信息）"""
        return await self.user_repo.get_user_profile(user_id)
    
    async def update_user_profile(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """更新用户资料"""
        try:
            # 过滤允许更新的字段
            allowed_fields = ["full_name", "email", "preferences"]
            filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
            
            if not filtered_data:
                logger.warning("没有可更新的字段")
                return None
            
            # 如果更新邮箱，检查是否已存在
            if "email" in filtered_data:
                existing_email = await self.user_repo.get_by_email(filtered_data["email"])
                if existing_email and existing_email.id != user_id:
                    logger.warning(f"邮箱 {filtered_data['email']} 已被其他用户使用")
                    return None
            
            filtered_data["updated_at"] = datetime.utcnow()
            user = await self.user_repo.update(user_id, filtered_data)
            
            if user:
                logger.info(f"用户 {user_id} 资料更新成功")
            
            return user
            
        except Exception as e:
            logger.error(f"更新用户资料失败: {e}")
            return None
    
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改用户密码"""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                logger.warning(f"用户 {user_id} 不存在")
                return False
            
            # 验证旧密码
            if not self._verify_password(old_password, user.password_hash):
                logger.warning(f"用户 {user_id} 旧密码验证失败")
                return False
            
            # 更新密码
            new_hash = self._hash_password(new_password)
            updated_user = await self.user_repo.update(user_id, {
                "password_hash": new_hash,
                "updated_at": datetime.utcnow()
            })
            
            if updated_user:
                logger.info(f"用户 {user_id} 密码修改成功")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            return False
    
    async def update_api_quota_used(self, user_id: int, tokens_used: int) -> bool:
        """更新用户API配额使用量"""
        try:
            user = await self.user_repo.update_api_quota_used(user_id, tokens_used)
            return user is not None
        except Exception as e:
            logger.error(f"更新API配额失败: {e}")
            return False
    
    async def check_api_quota(self, user_id: int) -> bool:
        """检查用户API配额是否足够"""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return False
            
            return user.api_quota_used < user.api_quota_daily
            
        except Exception as e:
            logger.error(f"检查API配额失败: {e}")
            return False
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户（管理员功能）"""
        try:
            return await self.user_repo.get_all(skip, limit)
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return []
    
    async def search_users(self, keyword: str, role: Optional[UserRole] = None, 
                          status: Optional[UserStatus] = None, 
                          skip: int = 0, limit: int = 100) -> List[User]:
        """搜索用户"""
        try:
            return await self.user_repo.search_users(keyword, role, status, skip, limit)
        except Exception as e:
            logger.error(f"搜索用户失败: {e}")
            return []
    
    async def update_user_status(self, user_id: int, status: UserStatus) -> Optional[User]:
        """更新用户状态（管理员功能）"""
        try:
            user = await self.user_repo.update(user_id, {
                "status": status,
                "updated_at": datetime.utcnow()
            })
            
            if user:
                logger.info(f"用户 {user_id} 状态更新为 {status}")
            
            return user
            
        except Exception as e:
            logger.error(f"更新用户状态失败: {e}")
            return None
    
    async def update_user_role(self, user_id: int, role: UserRole) -> Optional[User]:
        """更新用户角色（管理员功能）"""
        try:
            user = await self.user_repo.update(user_id, {
                "role": role,
                "updated_at": datetime.utcnow()
            })
            
            if user:
                logger.info(f"用户 {user_id} 角色更新为 {role}")
            
            return user
            
        except Exception as e:
            logger.error(f"更新用户角色失败: {e}")
            return None
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            return await self.user_repo.get_user_stats()
        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            return {}
    
    def _hash_password(self, password: str) -> str:
        """密码哈希 - 与Java后端保持一致"""
        # 使用与Java后端相同的盐值和算法
        salt = "genie-salt"
        return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        return self._hash_password(password) == hashed
    
    def convert_to_profile(self, user: User) -> UserProfile:
        """转换为用户资料对象"""
        return UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            last_login=user.last_login,
            created_at=user.created_at,
            api_quota_daily=user.api_quota_daily,
            api_quota_used=user.api_quota_used
        )