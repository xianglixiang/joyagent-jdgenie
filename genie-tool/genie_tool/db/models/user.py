# -*- coding: utf-8 -*-
# =====================
# 用户管理数据模型
# Author: AI Assistant
# Date: 2025/8/12
# =====================
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import DateTime, text, String
from sqlmodel import SQLModel, Field


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(SQLModel, table=True):
    """用户表"""
    __tablename__ = "users"
    
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    password_hash: str = Field(max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    role: UserRole = Field(default=UserRole.USER)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    last_login: Optional[datetime] = Field(default=None, sa_type=DateTime)
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
    
    # 业务字段
    api_quota_daily: Optional[int] = Field(default=100)  # 每日API调用配额
    api_quota_used: Optional[int] = Field(default=0)    # 已使用配额
    preferences: Optional[str] = Field(default=None)     # 用户偏好设置 (JSON字符串)


class UserProfile(SQLModel):
    """用户资料（非表模型，用于API响应）"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    status: UserStatus
    last_login: Optional[datetime]
    created_at: datetime
    api_quota_daily: int
    api_quota_used: int