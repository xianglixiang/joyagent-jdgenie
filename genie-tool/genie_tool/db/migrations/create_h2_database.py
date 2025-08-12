#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================
# H2数据库创建脚本
# Author: AI Assistant
# Date: 2025/8/12
# =====================
import os
import asyncio
from loguru import logger
from genie_tool.db.db_engine import get_database_config, init_db


async def create_h2_database():
    """创建H2数据库（实际使用SQLite）"""
    db_type, sync_url, async_url = get_database_config()
    
    if db_type != "h2":
        logger.info("当前配置不是H2，跳过数据库创建")
        return True
    
    h2_mode = os.environ.get("H2_MODE", "file")
    h2_db_path = os.environ.get("H2_DB_PATH", "./genie_h2_db.db")
    
    try:
        if h2_mode == "memory":
            logger.info("H2内存模式已配置，数据库将在应用启动时自动创建")
        else:
            logger.info(f"H2文件模式配置完成，数据库文件: {h2_db_path}")
            
            # 确保数据库目录存在
            db_dir = os.path.dirname(h2_db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                logger.info(f"创建数据库目录: {db_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"H2数据库配置失败: {e}")
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
    logger.info("Starting H2 database setup...")
    
    # 1. 配置H2数据库
    if not await create_h2_database():
        logger.error("Failed to configure H2 database")
        return False
    
    # 2. 初始化数据库表结构
    try:
        init_db()
        logger.info("H2 database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize H2 database tables: {e}")
        return False
    
    # 3. 创建默认管理员用户
    try:
        create_admin_user()
        logger.info("Default admin user setup completed")
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        return False
    
    logger.info("H2 database setup completed successfully!")
    logger.info("H2数据库特点:")
    logger.info("- 零配置，无需安装额外数据库服务")
    logger.info("- 支持内存模式和文件模式")
    logger.info("- 完全兼容现有SQLite代码")
    logger.info("- 适合本地开发和测试环境")
    return True


if __name__ == "__main__":
    asyncio.run(main())