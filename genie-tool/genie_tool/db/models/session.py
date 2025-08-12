# -*- coding: utf-8 -*-
# =====================
# 会话管理数据模型
# Author: AI Assistant
# Date: 2025/8/12
# =====================
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import DateTime, text, ForeignKey
from sqlmodel import SQLModel, Field, Relationship


class SessionStatus(str, Enum):
    """会话状态枚举"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Session(SQLModel, table=True):
    """会话表"""
    __tablename__ = "sessions"
    
    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(unique=True, index=True, max_length=255)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: SessionStatus = Field(default=SessionStatus.ACTIVE)
    
    # 会话统计信息
    message_count: int = Field(default=0)
    total_tokens_used: int = Field(default=0)
    last_activity: Optional[datetime] = Field(default=None, sa_type=DateTime)
    
    # 会话配置信息
    agent_type: Optional[str] = Field(default=None, max_length=50)  # 使用的代理类型
    output_style: Optional[str] = Field(default=None, max_length=20)  # 输出格式偏好
    
    # 元数据
    metadata: Optional[str] = Field(default=None)  # JSON字符串，存储额外信息
    
    # 时间戳
    created_at: Optional[datetime] = Field(
        sa_type=DateTime,
        default=None,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")}
    )
    updated_at: Optional[datetime] = Field(
        sa_type=DateTime,
        default=None,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": text("CURRENT_TIMESTAMP")
        }
    )


class SessionSummary(SQLModel):
    """会话摘要（用于列表显示）"""
    id: int
    session_id: str
    title: str
    status: SessionStatus
    message_count: int
    last_activity: Optional[datetime]
    created_at: datetime
    agent_type: Optional[str]


class SessionDetail(SQLModel):
    """会话详情（用于详细信息显示）"""
    id: int
    session_id: str
    user_id: Optional[int]
    title: str
    description: Optional[str]
    status: SessionStatus
    message_count: int
    total_tokens_used: int
    last_activity: Optional[datetime]
    agent_type: Optional[str]
    output_style: Optional[str]
    created_at: datetime
    updated_at: datetime