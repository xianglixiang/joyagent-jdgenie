# -*- coding: utf-8 -*-
# =====================
# 会话管理服务
# Author: AI Assistant
# Date: 2025/8/12
# =====================
import uuid
from typing import Optional, List
from datetime import datetime

from genie_tool.db.models.session import Session, SessionStatus, SessionSummary, SessionDetail
from genie_tool.db.repositories.session_repository import SessionRepository
from genie_tool.util.log_util import timer
from loguru import logger


class SessionService:
    """会话管理服务"""
    
    def __init__(self):
        self.session_repo = SessionRepository()
    
    @timer()
    async def create_session(self, 
                           user_id: Optional[int] = None,
                           title: str = "新对话",
                           description: Optional[str] = None,
                           agent_type: Optional[str] = None,
                           output_style: Optional[str] = None) -> Session:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            title=title,
            description=description,
            agent_type=agent_type,
            output_style=output_style,
            last_activity=datetime.utcnow()
        )
        
        created_session = await self.session_repo.create(session)
        logger.info(f"Created new session: {session_id} for user: {user_id}")
        return created_session
    
    @timer()
    async def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话信息"""
        return await self.session_repo.get_by_session_id(session_id)
    
    @timer()
    async def get_session_detail(self, session_id: str) -> Optional[SessionDetail]:
        """获取会话详细信息"""
        return await self.session_repo.get_session_detail(session_id)
    
    @timer()
    async def get_user_sessions(self, 
                              user_id: int, 
                              status: Optional[SessionStatus] = None,
                              skip: int = 0, 
                              limit: int = 20) -> List[SessionSummary]:
        """获取用户会话列表"""
        if status:
            filters = {"user_id": user_id, "status": status}
            sessions = await self.session_repo.get_by_fields(filters, skip, limit)
        else:
            sessions = await self.session_repo.get_by_user_id(user_id, skip, limit)
        
        # 转换为摘要格式
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
    
    @timer()
    async def update_session(self, 
                           session_id: str, 
                           title: Optional[str] = None,
                           description: Optional[str] = None,
                           agent_type: Optional[str] = None,
                           output_style: Optional[str] = None) -> Optional[Session]:
        """更新会话信息"""
        session = await self.session_repo.get_by_session_id(session_id)
        if not session:
            return None
        
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if agent_type is not None:
            update_data["agent_type"] = agent_type
        if output_style is not None:
            update_data["output_style"] = output_style
        
        if update_data:
            updated_session = await self.session_repo.update(session.id, update_data)
            logger.info(f"Updated session: {session_id}")
            return updated_session
        
        return session
    
    @timer()
    async def record_activity(self, session_id: str, tokens_used: int = 0) -> Optional[Session]:
        """记录会话活动"""
        # 更新最后活动时间
        session = await self.session_repo.update_last_activity(session_id)
        if not session:
            return None
        
        # 增加消息计数
        session = await self.session_repo.increment_message_count(session_id)
        
        # 更新Token使用量
        if tokens_used > 0:
            session = await self.session_repo.update_token_usage(session_id, tokens_used)
        
        return session
    
    @timer()
    async def archive_session(self, session_id: str) -> Optional[Session]:
        """归档会话"""
        session = await self.session_repo.archive_session(session_id)
        if session:
            logger.info(f"Archived session: {session_id}")
        return session
    
    @timer()
    async def delete_session(self, session_id: str) -> bool:
        """删除会话（软删除）"""
        session = await self.session_repo.get_by_session_id(session_id)
        if not session:
            return False
        
        update_data = {"status": SessionStatus.DELETED}
        updated_session = await self.session_repo.update(session.id, update_data)
        
        if updated_session:
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    @timer()
    async def search_sessions(self, 
                            user_id: int,
                            keyword: str,
                            agent_type: Optional[str] = None,
                            status: Optional[SessionStatus] = None,
                            skip: int = 0,
                            limit: int = 20) -> List[SessionSummary]:
        """搜索会话"""
        sessions = await self.session_repo.search_sessions(
            user_id=user_id,
            keyword=keyword,
            agent_type=agent_type,
            status=status,
            skip=skip,
            limit=limit
        )
        
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
    
    @timer()
    async def get_session_stats(self, user_id: Optional[int] = None) -> dict:
        """获取会话统计信息"""
        return await self.session_repo.get_session_stats(user_id)
    
    @timer()
    async def cleanup_old_sessions(self, days: int = 30) -> int:
        """清理旧会话"""
        count = await self.session_repo.cleanup_old_sessions(days)
        logger.info(f"Cleaned up {count} old sessions")
        return count