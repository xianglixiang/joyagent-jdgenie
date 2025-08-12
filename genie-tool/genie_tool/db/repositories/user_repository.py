# -*- coding: utf-8 -*-
# =====================
# 用户Repository
# Author: AI Assistant
# Date: 2025/8/12
# =====================
from typing import Optional, List
from datetime import datetime
from sqlmodel import select
from genie_tool.db.models.user import User, UserRole, UserStatus, UserProfile
from genie_tool.db.repositories.base_repository import BaseRepository
from genie_tool.db.db_engine import async_session_local


class UserRepository(BaseRepository[User]):
    """用户数据访问层"""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return await self.get_by_field("username", username)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return await self.get_by_field("email", email)
    
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取活跃用户列表"""
        return await self.get_by_fields({"status": UserStatus.ACTIVE}, skip, limit)
    
    async def get_users_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """根据角色获取用户列表"""
        return await self.get_by_fields({"role": role}, skip, limit)
    
    async def update_last_login(self, user_id: int) -> Optional[User]:
        """更新用户最后登录时间"""
        return await self.update(user_id, {"last_login": datetime.utcnow()})
    
    async def update_api_quota_used(self, user_id: int, used_count: int) -> Optional[User]:
        """更新用户API配额使用量"""
        async with async_session_local() as session:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().one_or_none()
            
            if not user:
                return None
            
            user.api_quota_used = min(user.api_quota_used + used_count, user.api_quota_daily)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    async def reset_daily_quota(self, user_id: int) -> Optional[User]:
        """重置用户每日配额"""
        return await self.update(user_id, {"api_quota_used": 0})
    
    async def reset_all_daily_quotas(self) -> int:
        """重置所有用户每日配额"""
        async with async_session_local() as session:
            stmt = select(User).where(User.status == UserStatus.ACTIVE)
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            count = 0
            for user in users:
                user.api_quota_used = 0
                session.add(user)
                count += 1
            
            await session.commit()
            return count
    
    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """获取用户资料（不包含敏感信息）"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
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
    
    async def search_users(self, 
                          keyword: str, 
                          role: Optional[UserRole] = None,
                          status: Optional[UserStatus] = None,
                          skip: int = 0, 
                          limit: int = 100) -> List[User]:
        """搜索用户"""
        async with async_session_local() as session:
            stmt = select(User)
            
            # 关键词搜索
            if keyword:
                stmt = stmt.where(
                    (User.username.contains(keyword)) |
                    (User.email.contains(keyword)) |
                    (User.full_name.contains(keyword))
                )
            
            # 角色过滤
            if role:
                stmt = stmt.where(User.role == role)
            
            # 状态过滤
            if status:
                stmt = stmt.where(User.status == status)
            
            stmt = stmt.offset(skip).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def get_user_stats(self) -> dict:
        """获取用户统计信息"""
        async with async_session_local() as session:
            total_users = await self.count()
            active_users = await self.count({"status": UserStatus.ACTIVE})
            admin_users = await self.count({"role": UserRole.ADMIN})
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "admin_users": admin_users,
                "regular_users": total_users - admin_users
            }