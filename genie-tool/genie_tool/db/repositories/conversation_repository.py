# -*- coding: utf-8 -*-
# =====================
# 对话Repository
# Author: AI Assistant
# Date: 2025/8/12
# =====================
from typing import Optional, List
from datetime import datetime, timedelta
from sqlmodel import select, func, desc
from genie_tool.db.models.conversation import Conversation, MessageType, AgentType, ConversationStatus, ConversationHistory, ConversationStats
from genie_tool.db.repositories.base_repository import BaseRepository
from genie_tool.db.db_engine import async_session_local


class ConversationRepository(BaseRepository[Conversation]):
    """对话数据访问层"""
    
    def __init__(self):
        super().__init__(Conversation)
    
    async def get_by_request_id(self, request_id: str) -> Optional[Conversation]:
        """根据请求ID获取对话"""
        return await self.get_by_field("request_id", request_id)
    
    async def get_by_session_id(self, session_id: str, skip: int = 0, limit: int = 100) -> List[Conversation]:
        """根据会话ID获取对话列表"""
        return await self.get_by_fields({"session_id": session_id}, skip, limit)
    
    async def get_conversation_history(self, session_id: str, limit: int = 50) -> List[ConversationHistory]:
        """获取会话对话历史"""
        async with async_session_local() as session:
            stmt = (select(Conversation)
                   .where(Conversation.session_id == session_id)
                   .order_by(Conversation.created_at.asc())
                   .limit(limit))
            
            result = await session.execute(stmt)
            conversations = result.scalars().all()
            
            return [
                ConversationHistory(
                    id=c.id,
                    session_id=c.session_id,
                    request_id=c.request_id,
                    message_type=c.message_type,
                    user_query=c.user_query,
                    agent_response=c.agent_response,
                    agent_type=c.agent_type,
                    execution_time=c.execution_time,
                    status=c.status,
                    created_at=c.created_at
                ) for c in conversations
            ]
    
    async def get_conversation_stats(self, session_id: str) -> Optional[ConversationStats]:
        """获取会话对话统计"""
        async with async_session_local() as session:
            # 总消息数
            total_stmt = select(func.count()).select_from(Conversation).where(Conversation.session_id == session_id)
            total_result = await session.execute(total_stmt)
            total_messages = total_result.scalar()
            
            if total_messages == 0:
                return None
            
            # 总Token数
            token_stmt = select(func.sum(Conversation.token_usage)).where(Conversation.session_id == session_id)
            token_result = await session.execute(token_stmt)
            total_tokens = token_result.scalar() or 0
            
            # 总成本
            cost_stmt = select(func.sum(Conversation.cost)).where(Conversation.session_id == session_id)
            cost_result = await session.execute(cost_stmt)
            total_cost = cost_result.scalar() or 0.0
            
            # 平均执行时间
            avg_time_stmt = select(func.avg(Conversation.execution_time)).where(
                (Conversation.session_id == session_id) & 
                (Conversation.execution_time.isnot(None))
            )
            avg_time_result = await session.execute(avg_time_stmt)
            avg_execution_time = avg_time_result.scalar() or 0.0
            
            # 成功率
            success_stmt = select(func.count()).select_from(Conversation).where(
                (Conversation.session_id == session_id) &
                (Conversation.status == ConversationStatus.SUCCESS)
            )
            success_result = await session.execute(success_stmt)
            success_count = success_result.scalar()
            success_rate = (success_count / total_messages) * 100 if total_messages > 0 else 0
            
            # 工具使用次数
            tool_stmt = select(func.sum(Conversation.tool_calls_count)).where(Conversation.session_id == session_id)
            tool_result = await session.execute(tool_stmt)
            tool_usage_count = tool_result.scalar() or 0
            
            return ConversationStats(
                session_id=session_id,
                total_messages=total_messages,
                total_tokens=total_tokens,
                total_cost=total_cost,
                avg_execution_time=avg_execution_time,
                success_rate=success_rate,
                tool_usage_count=tool_usage_count
            )