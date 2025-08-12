# -*- coding: utf-8 -*-
# =====================
# 
# 
# Author: liumin.423
# Date:   2025/7/9
# =====================
import os
from typing import Callable, AsyncGenerator

from loguru import logger
from sqlalchemy import AsyncAdaptedQueuePool, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel


def get_database_config():
    """获取数据库配置"""
    db_type = os.environ.get("DATABASE_TYPE", "sqlite").lower()
    
    if db_type == "mysql":
        mysql_host = os.environ.get("MYSQL_HOST", "localhost")
        mysql_port = os.environ.get("MYSQL_PORT", "3306")
        mysql_user = os.environ.get("MYSQL_USER", "root")
        mysql_password = os.environ.get("MYSQL_PASSWORD", "")
        mysql_database = os.environ.get("MYSQL_DATABASE", "genie_db")
        
        # MySQL连接URL
        sync_url = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
        async_url = f"mysql+aiomysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
        
        return db_type, sync_url, async_url
    elif db_type == "h2":
        # H2数据库配置 - 使用增强的SQLite模式来模拟H2的功能
        h2_db_path = os.environ.get("H2_DB_PATH", "./genie_h2_db.db")
        h2_mode = os.environ.get("H2_MODE", "file")  # file 或 memory
        
        if h2_mode == "memory":
            # 内存模式，适合测试 - 使用SQLite内存数据库
            sync_url = "sqlite:///:memory:"
            async_url = "sqlite+aiosqlite:///:memory:"
        else:
            # 文件模式，数据持久化 - 使用SQLite文件数据库
            sync_url = f"sqlite:///{h2_db_path}"
            async_url = f"sqlite+aiosqlite:///{h2_db_path}"
        
        return db_type, sync_url, async_url
    else:
        # 默认使用SQLite
        sqlite_db_path = os.environ.get("SQLITE_DB_PATH", "autobots.db")
        sync_url = f"sqlite:///{sqlite_db_path}"
        async_url = f"sqlite+aiosqlite:///{sqlite_db_path}"
        
        return "sqlite", sync_url, async_url


# 获取数据库配置
db_type, sync_database_url, async_database_url = get_database_config()

# 创建同步引擎
if db_type == "mysql":
    engine = create_engine(
        sync_database_url,
        echo=True,
        pool_size=10,
        pool_recycle=3600,
        pool_pre_ping=True
    )
elif db_type == "h2":
    # H2数据库引擎配置 (使用SQLite作为底层)
    engine = create_engine(
        sync_database_url,
        echo=True,
        pool_size=5,
        pool_recycle=3600,
        connect_args={
            "check_same_thread": False,
            "timeout": 20,  # H2模式下的超时设置
            "isolation_level": None  # 自动提交模式
        }
    )
else:
    engine = create_engine(sync_database_url, echo=True)

# 创建异步引擎
if db_type == "mysql":
    async_engine = create_async_engine(
        async_database_url,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=20,
        max_overflow=30,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False,
    )
elif db_type == "h2":
    # H2使用SQLite异步引擎
    async_engine = create_async_engine(
        async_database_url,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=5,
        pool_recycle=3600,
        echo=False,
    )
else:
    async_engine = create_async_engine(
        async_database_url,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=10,
        pool_recycle=3600,
        echo=False,
    )

async_session_local: Callable[..., AsyncSession] = sessionmaker(bind=async_engine, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """session生成器 作为fast api的Depends选项"""
    async with async_session_local() as session:
        yield session


def init_db():
    """初始化数据库，创建所有表"""
    from genie_tool.db.file_table import FileInfo
    
    # Try to import additional models if they exist
    try:
        import importlib.util
        import os
        models_path = os.path.join(os.path.dirname(__file__), 'models')
        if os.path.exists(models_path):
            # Only import models if the directory exists
            from genie_tool.db.models.user import User
            from genie_tool.db.models.session import Session
            from genie_tool.db.models.conversation import Conversation
            from genie_tool.db.models.report import Report
            from genie_tool.db.models.task_execution import TaskExecution
            logger.info("Imported enterprise database models")
    except ImportError as e:
        logger.info(f"Using basic file table only: {e}")
    
    SQLModel.metadata.create_all(engine)
    db_type = os.environ.get("DATABASE_TYPE", "sqlite").lower()
    logger.info(f"Database initialized successfully using {db_type.upper()}")
    logger.info(f"Database URL: {str(engine.url)}")


if __name__ == "__main__":
    init_db()
