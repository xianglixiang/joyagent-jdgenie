# -*- coding: utf-8 -*-
# =====================
# 报告管理数据模型
# Author: AI Assistant
# Date: 2025/8/12
# =====================
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import DateTime, text, Text
from sqlmodel import SQLModel, Field


class ReportType(str, Enum):
    """报告类型枚举"""
    HTML = "html"
    MARKDOWN = "markdown"
    PDF = "pdf"
    PPT = "ppt"
    EXCEL = "excel"
    CSV = "csv"


class ReportStatus(str, Enum):
    """报告状态枚举"""
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Report(SQLModel, table=True):
    """报告表"""
    __tablename__ = "reports"
    
    id: int | None = Field(default=None, primary_key=True)
    report_id: str = Field(unique=True, index=True, max_length=255)
    session_id: str = Field(index=True, max_length=255)
    request_id: Optional[str] = Field(default=None, index=True, max_length=255)
    
    # 报告基本信息
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    report_type: ReportType = Field(default=ReportType.HTML)
    status: ReportStatus = Field(default=ReportStatus.GENERATING)
    
    # 文件信息
    file_path: Optional[str] = Field(default=None, max_length=500)
    file_size: Optional[int] = Field(default=None)  # 文件大小（字节）
    file_hash: Optional[str] = Field(default=None, max_length=64)  # 文件MD5哈希
    
    # 内容摘要
    content_summary: Optional[str] = Field(default=None, sa_type=Text)
    keywords: Optional[str] = Field(default=None, max_length=500)  # 关键词，逗号分隔
    
    # 生成信息
    generation_time: Optional[float] = Field(default=None)  # 生成耗时（秒）
    agent_type: Optional[str] = Field(default=None, max_length=50)
    template_used: Optional[str] = Field(default=None, max_length=100)
    
    # 访问统计
    view_count: int = Field(default=0)
    download_count: int = Field(default=0)
    last_accessed: Optional[datetime] = Field(default=None, sa_type=DateTime)
    
    # 元数据
    metadata: Optional[str] = Field(default=None, sa_type=Text)  # JSON字符串
    tags: Optional[str] = Field(default=None, max_length=500)   # 标签，逗号分隔
    
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


class ReportSummary(SQLModel):
    """报告摘要（用于列表显示）"""
    id: int
    report_id: str
    session_id: str
    title: str
    report_type: ReportType
    status: ReportStatus
    file_size: Optional[int]
    view_count: int
    download_count: int
    created_at: datetime


class ReportDetail(SQLModel):
    """报告详情"""
    id: int
    report_id: str
    session_id: str
    request_id: Optional[str]
    title: str
    description: Optional[str]
    report_type: ReportType
    status: ReportStatus
    file_path: Optional[str]
    file_size: Optional[int]
    content_summary: Optional[str]
    keywords: Optional[str]
    generation_time: Optional[float]
    agent_type: Optional[str]
    view_count: int
    download_count: int
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime