"""
Permission model for Enhanced User Management System
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.sql import select, func, and_, or_

from src.database.connection import Base


class Permission(Base):
    """Permission model"""
    
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    module = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name={self.name}, module={self.module}, action={self.action})>"
    
    @property
    def full_name(self) -> str:
        """Get full permission name (module:action)"""
        return f"{self.module}:{self.action}"
    
    @classmethod
    async def find_by_id(cls, session: Session, permission_id: int) -> Optional['Permission']:
        """Find permission by ID"""
        result = await session.execute(
            select(cls).where(cls.id == permission_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def find_by_name(cls, session: Session, name: str) -> Optional['Permission']:
        """Find permission by name"""
        result = await session.execute(
            select(cls).where(func.upper(cls.name) == func.upper(name))
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def find_by_module_and_action(cls, session: Session, module: str, action: str) -> Optional['Permission']:
        """Find permission by module and action"""
        result = await session.execute(
            select(cls).where(
                and_(
                    func.upper(cls.module) == func.upper(module),
                    func.upper(cls.action) == func.upper(action)
                )
            )
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def find_all(cls, session: Session) -> List['Permission']:
        """Find all permissions"""
        result = await session.execute(
            select(cls).order_by(cls.module, cls.action)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def find_all_with_pagination(cls, session: Session, offset: int = 0, 
                                   limit: int = 20) -> tuple[List['Permission'], int]:
        """Find all permissions with pagination"""
        # Get total count
        count_query = select(func.count()).select_from(cls)
        total_count = await session.scalar(count_query)
        
        # Get permissions with pagination
        query = select(cls).offset(offset).limit(limit).order_by(cls.module, cls.action)
        result = await session.execute(query)
        permissions = list(result.scalars().all())
        
        return permissions, total_count
    
    @classmethod
    async def find_by_module(cls, session: Session, module: str) -> List['Permission']:
        """Find all permissions for a specific module"""
        result = await session.execute(
            select(cls).where(func.upper(cls.module) == func.upper(module))
                         .order_by(cls.action)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def search_permissions(cls, session: Session, search_term: str, 
                             offset: int = 0, limit: int = 20) -> List['Permission']:
        """Search permissions by name, module, or action"""
        search_pattern = f"%{search_term.lower()}%"
        
        query = select(cls).where(
            or_(
                func.lower(cls.name).like(search_pattern),
                func.lower(cls.module).like(search_pattern),
                func.lower(cls.action).like(search_pattern),
                func.lower(cls.description).like(search_pattern)
            )
        )
        
        query = query.offset(offset).limit(limit)
        query = query.order_by(cls.module, cls.action)
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    @classmethod
    async def get_modules(cls, session: Session) -> List[str]:
        """Get all distinct permission modules"""
        result = await session.execute(
            select(func.distinct(cls.module)).order_by(cls.module)
        )
        return [row[0] for row in result.all()]
    
    @classmethod
    async def get_actions_by_module(cls, session: Session, module: str) -> List[str]:
        """Get all distinct actions for a module"""
        result = await session.execute(
            select(func.distinct(cls.action))
            .where(func.upper(cls.module) == func.upper(module))
            .order_by(cls.action)
        )
        return [row[0] for row in result.all()]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert permission to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "module": self.module,
            "action": self.action,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    async def get_statistics(cls, session: Session) -> Dict[str, Any]:
        """Get permission statistics"""
        # Total permissions
        total_permissions = await session.scalar(
            select(func.count()).select_from(cls)
        )
        
        # Permissions by module
        permissions_by_module = await session.execute(
            select(cls.module, func.count())
            .select_from(cls)
            .group_by(cls.module)
            .order_by(func.count().desc())
        )
        module_counts = [
            {
                "module": row.module,
                "count": row.count
            }
            for row in permissions_by_module.all()
        ]
        
        # Permissions by action
        permissions_by_action = await session.execute(
            select(cls.action, func.count())
            .select_from(cls)
            .group_by(cls.action)
            .order_by(func.count().desc())
            .limit(10)
        )
        action_counts = [
            {
                "action": row.action,
                "count": row.count
            }
            for row in permissions_by_action.all()
        ]
        
        return {
            "total_permissions": total_permissions,
            "permissions_by_module": module_counts,
            "top_actions": action_counts
        }