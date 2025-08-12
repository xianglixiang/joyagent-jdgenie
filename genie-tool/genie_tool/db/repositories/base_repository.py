# -*- coding: utf-8 -*-
# =====================
# 基础Repository类
# Author: AI Assistant
# Date: 2025/8/12
# =====================
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy import func, desc, asc
from sqlmodel import select, Session as SQLSession
from genie_tool.db.db_engine import async_session_local

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """基础Repository类，提供通用的CRUD操作"""
    
    def __init__(self, model_class: type[T]):
        self.model_class = model_class
    
    async def create(self, obj: T) -> T:
        """创建对象"""
        async with async_session_local() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj
    
    async def get_by_id(self, obj_id: int) -> Optional[T]:
        """根据ID获取对象"""
        async with async_session_local() as session:
            stmt = select(self.model_class).where(self.model_class.id == obj_id)
            result = await session.execute(stmt)
            return result.scalars().one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """获取所有对象（分页）"""
        async with async_session_local() as session:
            stmt = select(self.model_class).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[T]:
        """更新对象"""
        async with async_session_local() as session:
            stmt = select(self.model_class).where(self.model_class.id == obj_id)
            result = await session.execute(stmt)
            obj = result.scalars().one_or_none()
            
            if not obj:
                return None
            
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj
    
    async def delete(self, obj_id: int) -> bool:
        """删除对象"""
        async with async_session_local() as session:
            stmt = select(self.model_class).where(self.model_class.id == obj_id)
            result = await session.execute(stmt)
            obj = result.scalars().one_or_none()
            
            if not obj:
                return False
            
            await session.delete(obj)
            await session.commit()
            return True
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """计算记录数量"""
        async with async_session_local() as session:
            stmt = select(func.count()).select_from(self.model_class)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model_class, key):
                        stmt = stmt.where(getattr(self.model_class, key) == value)
            
            result = await session.execute(stmt)
            return result.scalar()
    
    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[T]:
        """根据字段获取对象"""
        async with async_session_local() as session:
            if not hasattr(self.model_class, field_name):
                return None
            
            stmt = select(self.model_class).where(getattr(self.model_class, field_name) == field_value)
            result = await session.execute(stmt)
            return result.scalars().one_or_none()
    
    async def get_by_fields(self, filters: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[T]:
        """根据多个字段获取对象列表"""
        async with async_session_local() as session:
            stmt = select(self.model_class)
            
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    stmt = stmt.where(getattr(self.model_class, key) == value)
            
            stmt = stmt.offset(skip).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def get_sorted(self, 
                        sort_field: str, 
                        sort_order: str = "asc", 
                        skip: int = 0, 
                        limit: int = 100) -> List[T]:
        """获取排序后的对象列表"""
        async with async_session_local() as session:
            if not hasattr(self.model_class, sort_field):
                return await self.get_all(skip, limit)
            
            sort_column = getattr(self.model_class, sort_field)
            if sort_order.lower() == "desc":
                sort_column = desc(sort_column)
            else:
                sort_column = asc(sort_column)
            
            stmt = select(self.model_class).order_by(sort_column).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def batch_create(self, objects: List[T]) -> List[T]:
        """批量创建对象"""
        async with async_session_local() as session:
            session.add_all(objects)
            await session.commit()
            for obj in objects:
                await session.refresh(obj)
            return objects