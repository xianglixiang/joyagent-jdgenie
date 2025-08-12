# -*- coding: utf-8 -*-
# =====================
# 会话Repository
# Author: AI Assistant
# Date: 2025/8/12
# =====================
from typing import Optional, List
from datetime import datetime, timedelta
from sqlmodel import select, func
from genie_tool.db.models.session import Session, SessionStatus, SessionSummary, SessionDetail
from genie_tool.db.repositories.base_repository import BaseRepository
from genie_tool.db.db_engine import async_session_local


class SessionRepository(BaseRepository[Session]):
    """会话数据访问层"""
    
    def __init__(self):
        super().__init__(Session)
    
    async def get_by_session_id(self, session_id: str) -> Optional[Session]:
        """根据会话ID获取会话"""
        return await self.get_by_field("session_id", session_id)
    
    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Session]:
        """根据用户ID获取会话列表"""
        return await self.get_by_fields({"user_id": user_id}, skip, limit)
    
    async def get_active_sessions(self, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Session]:
        """获取活跃会话列表"""
        filters = {"status": SessionStatus.ACTIVE}
        if user_id:
            filters["user_id"] = user_id
        return await self.get_by_fields(filters, skip, limit)
    
    async def get_recent_sessions(self, user_id: int, days: int = 7, limit: int = 50) -> List[Session]:
        """获取用户最近的会话"""
        async with async_session_local() as session:
            since_date = datetime.utcnow() - timedelta(days=days)
            stmt = (select(Session)
                   .where(Session.user_id == user_id)
                   .where(Session.created_at >= since_date)
                   .order_by(Session.created_at.desc())
                   .limit(limit))
            
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def update_last_activity(self, session_id: str) -> Optional[Session]:
        """更新会话最后活动时间"""
        async with async_session_local() as session:
            stmt = select(Session).where(Session.session_id == session_id)
            result = await session.execute(stmt)
            session_obj = result.scalars().one_or_none()
            
            if not session_obj:
                return None
            
            session_obj.last_activity = datetime.utcnow()
            session.add(session_obj)
            await session.commit()
            await session.refresh(session_obj)
            return session_obj
    
    async def increment_message_count(self, session_id: str) -> Optional[Session]:
        """增加会话消息计数"""
        async with async_session_local() as session:
            stmt = select(Session).where(Session.session_id == session_id)
            result = await session.execute(stmt)
            session_obj = result.scalars().one_or_none()
            
            if not session_obj:
                return None
            
            session_obj.message_count += 1
            session_obj.last_activity = datetime.utcnow()
            session.add(session_obj)
            await session.commit()
            await session.refresh(session_obj)
            return session_obj
    
    async def update_token_usage(self, session_id: str, tokens_used: int) -> Optional[Session]:
        """更新会话Token使用量"""
        async with async_session_local() as session:
            stmt = select(Session).where(Session.session_id == session_id)
            result = await session.execute(stmt)
            session_obj = result.scalars().one_or_none()
            
            if not session_obj:
                return None
            
            session_obj.total_tokens_used += tokens_used
            session.add(session_obj)
            await session.commit()
            await session.refresh(session_obj)
            return session_obj
    
    async def archive_session(self, session_id: str) -> Optional[Session]:
        """归档会话"""
        async with async_session_local() as session:
            stmt = select(Session).where(Session.session_id == session_id)
            result = await session.execute(stmt)
            session_obj = result.scalars().one_or_none()
            
            if not session_obj:
                return None
            
            session_obj.status = SessionStatus.ARCHIVED
            session.add(session_obj)
            await session.commit()
            await session.refresh(session_obj)
            return session_obj
    
    async def get_session_summaries(self, user_id: int, skip: int = 0, limit: int = 100) -> List[SessionSummary]:
        """获取会话摘要列表"""
        async with async_session_local() as session:
            stmt = (select(Session)
                   .where(Session.user_id == user_id)
                   .order_by(Session.last_activity.desc())
                   .offset(skip)
                   .limit(limit))
            
            result = await session.execute(stmt)
            sessions = result.scalars().all()
            
            return [
                SessionSummary(
                    id=s.id,
                    session_id=s.session_id,
                    title=s.title,
                    status=s.status,
                    message_count=s.message_count,
                    last_activity=s.last_activity,
                    created_at=s.created_at,
                    agent_type=s.agent_type
                ) for s in sessions
            ]
    
    async def get_session_detail(self, session_id: str) -> Optional[SessionDetail]:
        """获取会话详情"""
        session_obj = await self.get_by_session_id(session_id)
        if not session_obj:
            return None
        
        return SessionDetail(
            id=session_obj.id,
            session_id=session_obj.session_id,
            user_id=session_obj.user_id,
            title=session_obj.title,
            description=session_obj.description,
            status=session_obj.status,
            message_count=session_obj.message_count,
            total_tokens_used=session_obj.total_tokens_used,
            last_activity=session_obj.last_activity,
            agent_type=session_obj.agent_type,
            output_style=session_obj.output_style,
            created_at=session_obj.created_at,
            updated_at=session_obj.updated_at
        )
    
    async def search_sessions(self, 
                             user_id: int,
                             keyword: str,
                             agent_type: Optional[str] = None,
                             status: Optional[SessionStatus] = None,
                             skip: int = 0,
                             limit: int = 100) -> List[Session]:
        """搜索会话"""
        async with async_session_local() as session:
            stmt = select(Session).where(Session.user_id == user_id)
            
            # 关键词搜索
            if keyword:
                stmt = stmt.where(
                    (Session.title.contains(keyword)) |
                    (Session.description.contains(keyword))
                )
            
            # 代理类型过滤
            if agent_type:
                stmt = stmt.where(Session.agent_type == agent_type)
            
            # 状态过滤
            if status:
                stmt = stmt.where(Session.status == status)
            
            stmt = stmt.order_by(Session.last_activity.desc()).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def cleanup_old_sessions(self, days: int = 30) -> int:
        """清理旧会话（删除状态且超过指定天数的会话）"""
        async with async_session_local() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stmt = (select(Session)
                   .where(Session.status == SessionStatus.DELETED)
                   .where(Session.updated_at < cutoff_date))
            
            result = await session.execute(stmt)
            sessions_to_delete = result.scalars().all()
            
            for session_obj in sessions_to_delete:
                await session.delete(session_obj)
            
            await session.commit()
            return len(sessions_to_delete)
    
    async def get_session_stats(self, user_id: Optional[int] = None) -> dict:
        """获取会话统计信息"""
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        
        total_sessions = await self.count(filters)
        
        active_filters = {**filters, "status": SessionStatus.ACTIVE}
        active_sessions = await self.count(active_filters)
        
        archived_filters = {**filters, "status": SessionStatus.ARCHIVED}
        archived_sessions = await self.count(archived_filters)
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "archived_sessions": archived_sessions,
            "deleted_sessions": total_sessions - active_sessions - archived_sessions
        }