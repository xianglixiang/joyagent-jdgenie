#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================
# SQLite到MySQL数据迁移脚本
# Author: AI Assistant
# Date: 2025/8/12
# =====================
import os
import asyncio
import sqlite3
from typing import List, Dict, Any
from loguru import logger
from sqlalchemy import create_engine, text
from sqlmodel import Session

from genie_tool.db.models.user import User
from genie_tool.db.models.session import Session as ChatSession
from genie_tool.db.models.conversation import Conversation
from genie_tool.db.models.report import Report
from genie_tool.db.models.task_execution import TaskExecution
from genie_tool.db.file_table import FileInfo


class SQLiteToMySQLMigrator:
    """SQLite到MySQL数据迁移器"""
    
    def __init__(self, sqlite_path: str, mysql_url: str):
        self.sqlite_path = sqlite_path
        self.mysql_url = mysql_url
        self.sqlite_conn = None
        self.mysql_engine = None
    
    def connect(self):
        """建立数据库连接"""
        # SQLite连接
        if os.path.exists(self.sqlite_path):
            self.sqlite_conn = sqlite3.connect(self.sqlite_path)
            self.sqlite_conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
            logger.info(f"Connected to SQLite database: {self.sqlite_path}")
        else:
            logger.warning(f"SQLite database not found: {self.sqlite_path}")
            return False
        
        # MySQL连接
        try:
            self.mysql_engine = create_engine(self.mysql_url)
            logger.info("Connected to MySQL database")
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {e}")
            return False
        
        return True
    
    def close(self):
        """关闭数据库连接"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        if self.mysql_engine:
            self.mysql_engine.dispose()
    
    def get_sqlite_tables(self) -> List[str]:
        """获取SQLite数据库中的表列表"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        return tables
    
    def migrate_file_info(self):
        """迁移文件信息表"""
        logger.info("Migrating FileInfo table...")
        
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT * FROM fileinfo")
        rows = cursor.fetchall()
        
        if not rows:
            logger.info("No FileInfo records to migrate")
            return
        
        with Session(self.mysql_engine) as session:
            for row in rows:
                file_info = FileInfo(
                    id=row['id'],
                    file_id=row['file_id'],
                    filename=row['filename'],
                    file_path=row['file_path'],
                    description=row['description'],
                    file_size=row['file_size'],
                    status=row['status'],
                    request_id=row['request_id'],
                    create_time=row['create_time']
                )
                session.add(file_info)
            
            session.commit()
            logger.info(f"Migrated {len(rows)} FileInfo records")
    
    def create_sample_data(self):
        """创建示例数据（如果SQLite中没有相关表）"""
        logger.info("Creating sample data for new tables...")
        
        with Session(self.mysql_engine) as session:
            # 创建示例用户（如果不存在）
            existing_user = session.query(User).filter(User.username == "admin").first()
            if not existing_user:
                import hashlib
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                
                admin_user = User(
                    username="admin",
                    email="admin@genie.local",
                    password_hash=password_hash,
                    full_name="系统管理员",
                    role="admin",
                    status="active",
                    api_quota_daily=10000
                )
                session.add(admin_user)
                session.commit()
                logger.info("Created admin user")
    
    def verify_migration(self):
        """验证迁移结果"""
        logger.info("Verifying migration...")
        
        with Session(self.mysql_engine) as session:
            # 检查FileInfo表
            file_count = session.query(FileInfo).count()
            logger.info(f"FileInfo records in MySQL: {file_count}")
            
            # 检查User表
            user_count = session.query(User).count()
            logger.info(f"User records in MySQL: {user_count}")
    
    def migrate(self):
        """执行完整迁移"""
        if not self.connect():
            return False
        
        try:
            # 获取SQLite表列表
            tables = self.get_sqlite_tables()
            logger.info(f"Found SQLite tables: {tables}")
            
            # 迁移现有表
            if 'fileinfo' in tables:
                self.migrate_file_info()
            
            # 创建示例数据
            self.create_sample_data()
            
            # 验证迁移
            self.verify_migration()
            
            logger.info("Migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
        
        finally:
            self.close()


async def main():
    """主函数"""
    # 获取数据库配置
    from genie_tool.db.db_engine import get_database_config
    
    db_type, sync_url, async_url = get_database_config()
    
    if db_type != "mysql":
        logger.info("Current database is not MySQL, migration not needed")
        return
    
    # 获取SQLite数据库路径
    sqlite_path = os.environ.get("SQLITE_DB_PATH", "autobots.db")
    
    # 创建迁移器
    migrator = SQLiteToMySQLMigrator(sqlite_path, sync_url)
    
    # 执行迁移
    success = migrator.migrate()
    
    if success:
        logger.info("Data migration completed successfully!")
    else:
        logger.error("Data migration failed!")


if __name__ == "__main__":
    asyncio.run(main())