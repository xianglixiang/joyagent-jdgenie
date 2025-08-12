# -*- coding: utf-8 -*-
# =====================
# 任务执行记录数据模型
# Author: AI Assistant
# Date: 2025/8/12
# =====================
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import DateTime, text, Text
from sqlmodel import SQLModel, Field


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(str, Enum):
    """任务优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskExecution(SQLModel, table=True):
    """任务执行记录表"""
    __tablename__ = "task_executions"
    
    id: int | None = Field(default=None, primary_key=True)
    task_id: str = Field(unique=True, index=True, max_length=255)
    session_id: str = Field(index=True, max_length=255)
    request_id: Optional[str] = Field(default=None, index=True, max_length=255)
    parent_task_id: Optional[str] = Field(default=None, index=True, max_length=255)  # 父任务ID
    
    # 任务基本信息
    task_name: str = Field(max_length=255)
    task_description: Optional[str] = Field(default=None, max_length=1000)
    task_type: str = Field(max_length=50)  # 任务类型
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    
    # 执行状态
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    progress: float = Field(default=0.0)  # 进度百分比 (0-100)
    current_step: Optional[str] = Field(default=None, max_length=255)  # 当前执行步骤
    
    # 代理信息
    agent_type: Optional[str] = Field(default=None, max_length=50)
    agent_version: Optional[str] = Field(default=None, max_length=20)
    
    # 时间信息
    start_time: Optional[datetime] = Field(default=None, sa_type=DateTime)
    end_time: Optional[datetime] = Field(default=None, sa_type=DateTime)
    estimated_duration: Optional[int] = Field(default=None)  # 预估执行时间（秒）
    actual_duration: Optional[int] = Field(default=None)     # 实际执行时间（秒）
    
    # 结果信息
    result_summary: Optional[str] = Field(default=None, sa_type=Text)
    output_files: Optional[str] = Field(default=None, sa_type=Text)  # JSON字符串，输出文件列表
    error_message: Optional[str] = Field(default=None, sa_type=Text)
    error_code: Optional[str] = Field(default=None, max_length=20)
    
    # 资源使用情况
    cpu_usage: Optional[float] = Field(default=None)     # CPU使用率
    memory_usage: Optional[float] = Field(default=None)  # 内存使用量（MB）
    tokens_used: Optional[int] = Field(default=None)     # Token使用量
    api_calls_count: Optional[int] = Field(default=None) # API调用次数
    
    # 依赖关系
    dependencies: Optional[str] = Field(default=None, sa_type=Text)  # JSON字符串，依赖任务列表
    
    # 配置信息
    config: Optional[str] = Field(default=None, sa_type=Text)  # JSON字符串，任务配置
    
    # 日志和调试信息
    execution_log: Optional[str] = Field(default=None, sa_type=Text)
    debug_info: Optional[str] = Field(default=None, sa_type=Text)
    
    # 重试信息
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    
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


class TaskSummary(SQLModel):
    """任务摘要（用于列表显示）"""
    id: int
    task_id: str
    session_id: str
    task_name: str
    task_type: str
    status: TaskStatus
    priority: TaskPriority
    progress: float
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    actual_duration: Optional[int]
    created_at: datetime


class TaskDetail(SQLModel):
    """任务详情"""
    id: int
    task_id: str
    session_id: str
    request_id: Optional[str]
    parent_task_id: Optional[str]
    task_name: str
    task_description: Optional[str]
    task_type: str
    priority: TaskPriority
    status: TaskStatus
    progress: float
    current_step: Optional[str]
    agent_type: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    actual_duration: Optional[int]
    result_summary: Optional[str]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime


class TaskStats(SQLModel):
    """任务统计信息"""
    total_tasks: int
    pending_tasks: int
    running_tasks: int
    completed_tasks: int
    failed_tasks: int
    avg_execution_time: Optional[float]
    success_rate: float