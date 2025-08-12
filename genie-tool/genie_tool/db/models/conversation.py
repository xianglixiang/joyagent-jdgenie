# -*- coding: utf-8 -*-
# =====================
# 对话历史数据模型
# Author: AI Assistant
# Date: 2025/8/12
# =====================
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import DateTime, text, Text
from sqlmodel import SQLModel, Field


class MessageType(str, Enum):
    """消息类型枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class AgentType(str, Enum):
    """代理类型枚举"""
    PLANNING = "planning"
    REACT = "react"
    EXECUTOR = "executor"
    SUMMARY = "summary"


class ConversationStatus(str, Enum):
    """对话状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class Conversation(SQLModel, table=True):
    """对话历史表"""
    __tablename__ = "conversations"
    
    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, max_length=255)
    request_id: str = Field(unique=True, index=True, max_length=255)
    
    # 消息内容
    message_type: MessageType = Field(default=MessageType.USER)
    user_query: Optional[str] = Field(default=None, sa_type=Text)
    agent_response: Optional[str] = Field(default=None, sa_type=Text)
    
    # 代理信息
    agent_type: Optional[AgentType] = Field(default=None)
    agent_step: Optional[int] = Field(default=0)  # 代理执行步骤
    
    # 性能指标
    execution_time: Optional[float] = Field(default=None)  # 执行时间（秒）
    token_usage: Optional[int] = Field(default=None)       # Token使用量
    cost: Optional[float] = Field(default=None)            # 成本
    
    # 状态信息
    status: ConversationStatus = Field(default=ConversationStatus.SUCCESS)
    error_message: Optional[str] = Field(default=None, max_length=1000)
    
    # 工具调用信息
    tools_used: Optional[str] = Field(default=None)        # JSON字符串，记录使用的工具
    tool_calls_count: Optional[int] = Field(default=0)     # 工具调用次数
    
    # 输出格式
    output_style: Optional[str] = Field(default=None, max_length=20)
    
    # 元数据
    metadata: Optional[str] = Field(default=None, sa_type=Text)  # JSON字符串
    
    # 时间戳
    created_at: Optional[datetime] = Field(
        sa_type=DateTime,
        default=None,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")}
    )


class ConversationHistory(SQLModel):
    """对话历史摘要（用于会话历史展示）"""
    id: int
    session_id: str
    request_id: str
    message_type: MessageType
    user_query: Optional[str]
    agent_response: Optional[str]
    agent_type: Optional[AgentType]
    execution_time: Optional[float]
    status: ConversationStatus
    created_at: datetime


class ConversationStats(SQLModel):
    """对话统计信息"""
    session_id: str
    total_messages: int
    total_tokens: int
    total_cost: float
    avg_execution_time: float
    success_rate: float
    tool_usage_count: int