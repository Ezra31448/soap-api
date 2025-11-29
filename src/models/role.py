"""
Role model for Enhanced User Management System
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import select, func, and_

from src.database.connection import Base
from src.models.permission import Permission


class Role(Base):
    """Role model"""
    
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"
    
    @property
    def is_admin(self) -> bool:
        """Check if role is admin"""
        return self.name.upper() == "ADMIN"
    
    @property
    def is_manager(self) -> bool:
        """Check if role is manager"""
        return self.name.upper() == "MANAGER"
    
    @property
    def is_user(self) -> bool:
        """Check if role is user"""
        return self.name.upper() == "USER"
    
    @classmethod
    async def find_by_id(cls, session: Session, role_id: int) -> Optional['Role']:
        """Find role by ID"""
        result = await session.execute(
            select(cls).where(cls.id == role_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def find_by_name(cls, session: Session, name: str) -> Optional['Role']:
        """Find role by name"""
        result = await session.execute(
            select(cls).where(func.upper(cls.name) == func.upper(name))
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def find_all(cls, session: Session) -> List['Role']:
        """Find all roles"""
        result = await session.execute(
            select(cls).order_by(cls.name)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def find_all_with_pagination(cls, session: Session, offset: int = 0, 
                                   limit: int = 20) -> tuple[List['Role'], int]:
        """Find all roles with pagination"""
        # Get total count
        count_query = select(func.count()).select_from(cls)
        total_count = await session.scalar(count_query)
        
        # Get roles with pagination
        query = select(cls).offset(offset).limit(limit).order_by(cls.name)
        result = await session.execute(query)
        roles = list(result.scalars().all())
        
        return roles, total_count
    
    @classmethod
    async def search_roles(cls, session: Session, search_term: str, 
                         offset: int = 0, limit: int = 20) -> List['Role']:
        """Search roles by name or description"""
        search_pattern = f"%{search_term.lower()}%"
        
        query = select(cls).where(
            or_(
                func.lower(cls.name).like(search_pattern),
                func.lower(cls.description).like(search_pattern)
            )
        )
        
        query = query.offset(offset).limit(limit)
        query = query.order_by(cls.name)
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    async def get_permissions(self, session: Session) -> List[Permission]:
        """Get role's permissions"""
        result = await session.execute(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == self.id)
            .order_by(Permission.module, Permission.action)
        )
        return list(result.scalars().all())
    
    async def has_permission(self, session: Session, permission_name: str) -> bool:
        """Check if role has a specific permission"""
        result = await session.execute(
            select(func.count())
            .select_from(
                select(Permission)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .where(
                    and_(
                        RolePermission.role_id == self.id,
                        Permission.name == permission_name
                    )
                )
                .subquery()
            )
        )
        return result.scalar() > 0
    
    async def assign_permission(self, session: Session, permission_name: str, 
                           granted_by: int = None) -> bool:
        """Assign a permission to role"""
        # Find permission
        permission = await session.execute(
            select(Permission).where(Permission.name == permission_name)
        )
        permission = permission.scalar_one_or_none()
        
        if not permission:
            return False
        
        # Check if role already has this permission
        existing_assignment = await session.execute(
            select(RolePermission).where(
                and_(
                    RolePermission.role_id == self.id,
                    RolePermission.permission_id == permission.id
                )
            )
        )
        existing_assignment = existing_assignment.scalar_one_or_none()
        
        if existing_assignment:
            return False  # Already assigned
        
        # Create new assignment
        role_permission = RolePermission(
            role_id=self.id,
            permission_id=permission.id,
            granted_by=granted_by
        )
        
        session.add(role_permission)
        return True
    
    async def remove_permission(self, session: Session, permission_name: str) -> bool:
        """Remove a permission from role"""
        # Find permission
        permission = await session.execute(
            select(Permission).where(Permission.name == permission_name)
        )
        permission = permission.scalar_one_or_none()
        
        if not permission:
            return False
        
        # Find and delete assignment
        assignment = await session.execute(
            select(RolePermission).where(
                and_(
                    RolePermission.role_id == self.id,
                    RolePermission.permission_id == permission.id
                )
            )
        )
        assignment = assignment.scalar_one_or_none()
        
        if assignment:
            await session.delete(assignment)
            return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert role to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_admin": self.is_admin,
            "is_manager": self.is_manager,
            "is_user": self.is_user
        }
    
    @classmethod
    async def get_statistics(cls, session: Session) -> Dict[str, Any]:
        """Get role statistics"""
        # Total roles
        total_roles = await session.scalar(
            select(func.count()).select_from(cls)
        )
        
        # Roles with most users
        roles_with_user_counts = await session.execute(
            select(
                cls.name,
                func.count(UserRole.user_id).label('user_count')
            )
            .join(UserRole, UserRole.role_id == cls.id)
            .group_by(cls.id, cls.name)
            .order_by(func.count(UserRole.user_id).desc())
            .limit(5)
        )
        
        return {
            "total_roles": total_roles,
            "roles_with_most_users": [
                {
                    "role_name": row.name,
                    "user_count": row.user_count
                }
                for row in roles_with_user_counts.all()
            ]
        }


# Import related models to avoid circular imports
from src.models.user_role import UserRole
from src.models.role_permission import RolePermission