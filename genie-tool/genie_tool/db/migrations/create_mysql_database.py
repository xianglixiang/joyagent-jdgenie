#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================
# MySQL数据库创建脚本
# Author: AI Assistant
# Date: 2025/8/12
# =====================
import os
import asyncio
from typing import Optional
from loguru import logger
import pymysql
from genie_tool.db.db_engine import get_database_config, init_db


async def create_mysql_database():
    """创建MySQL数据库（如果不存在）"""
    db_type, sync_url, async_url = get_database_config()
    
    if db_type != "mysql":
        logger.info("当前配置不是MySQL，跳过数据库创建")
        return True
    
    # 从环境变量获取MySQL连接信息
    mysql_host = os.environ.get("MYSQL_HOST", "localhost")
    mysql_port = int(os.environ.get("MYSQL_PORT", "3306"))
    mysql_user = os.environ.get("MYSQL_USER", "root")
    mysql_password = os.environ.get("MYSQL_PASSWORD", "")
    mysql_database = os.environ.get("MYSQL_DATABASE", "genie_db")
    
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 检查数据库是否存在
            cursor.execute(f"SHOW DATABASES LIKE '{mysql_database}'")
            result = cursor.fetchone()
            
            if not result:
                # 创建数据库
                cursor.execute(f"""
                    CREATE DATABASE {mysql_database} 
                    CHARACTER SET utf8mb4 
                    COLLATE utf8mb4_unicode_ci
                """)
                logger.info(f"Created MySQL database: {mysql_database}")
            else:
                logger.info(f"MySQL database already exists: {mysql_database}")
        
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to create MySQL database: {e}")
        return False


def create_admin_user():
    """创建默认管理员用户"""
    from genie_tool.db.models.user import User, UserRole, UserStatus
    from genie_tool.db.repositories.user_repository import UserRepository
    import hashlib
    
    async def _create_admin():
        user_repo = UserRepository()
        
        # 检查是否已存在管理员用户
        admin_user = await user_repo.get_by_username("admin")
        if admin_user:
            logger.info("Admin user already exists")
            return
        
        # 创建默认管理员用户
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        
        admin = User(
            username="admin",
            email="admin@genie.local",
            password_hash=password_hash,
            full_name="系统管理员",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            api_quota_daily=10000
        )
        
        await user_repo.create(admin)
        logger.info("Created default admin user (username: admin, password: admin123)")
    
    return asyncio.run(_create_admin())


async def main():
    """主函数"""
    logger.info("Starting database setup...")
    
    # 1. 创建MySQL数据库（如果需要）
    if not await create_mysql_database():
        logger.error("Failed to create MySQL database")
        return False
    
    # 2. 初始化数据库表结构
    try:
        init_db()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        return False
    
    # 3. 创建默认管理员用户
    try:
        create_admin_user()
        logger.info("Default admin user setup completed")
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        return False
    
    logger.info("Database setup completed successfully!")
    return True


if __name__ == "__main__":
    asyncio.run(main())