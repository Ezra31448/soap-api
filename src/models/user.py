"""
User model for Enhanced User Management System
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import select, func, and_, or_

from src.database.connection import Base
from src.models.role import Role
from src.models.permission import Permission


class User(Base):
    """User model"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default='ACTIVE', index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_expires = Column(DateTime, nullable=True)
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, status={self.status})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == "ACTIVE"
    
    @property
    def is_suspended(self) -> bool:
        """Check if user is suspended"""
        return self.status == "SUSPENDED"
    
    @classmethod
    async def find_by_id(cls, session: Session, user_id: int) -> Optional['User']:
        """Find user by ID"""
        result = await session.execute(
            select(cls).where(cls.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def find_by_email(cls, session: Session, email: str) -> Optional['User']:
        """Find user by email"""
        result = await session.execute(
            select(cls).where(func.lower(cls.email) == func.lower(email))
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def find_all_with_pagination(cls, session: Session, offset: int = 0, 
                                   limit: int = 20, status: str = None) -> tuple[List['User'], int]:
        """Find all users with pagination"""
        query = select(cls)
        
        # Apply status filter if provided
        if status:
            query = query.where(cls.status == status.upper())
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await session.scalar(count_query)
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        query = query.order_by(cls.created_at.desc())
        
        result = await session.execute(query)
        users = result.scalars().all()
        
        return list(users), total_count
    
    @classmethod
    async def search_users(cls, session: Session, search_term: str, 
                         offset: int = 0, limit: int = 20) -> List['User']:
        """Search users by name or email"""
        search_pattern = f"%{search_term.lower()}%"
        
        query = select(cls).where(
            or_(
                func.lower(cls.first_name).like(search_pattern),
                func.lower(cls.last_name).like(search_pattern),
                func.lower(cls.email).like(search_pattern)
            )
        )
        
        query = query.offset(offset).limit(limit)
        query = query.order_by(cls.first_name, cls.last_name)
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    async def get_roles(self, session: Session) -> List[Role]:
        """Get user's roles"""
        result = await session.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == self.id)
            .order_by(Role.name)
        )
        return list(result.scalars().all())
    
    async def get_permissions(self, session: Session) -> List[Permission]:
        """Get user's permissions through roles"""
        result = await session.execute(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, RolePermission.role_id == Role.id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == self.id)
            .distinct()
            .order_by(Permission.module, Permission.action)
        )
        return list(result.scalars().all())
    
    async def has_permission(self, session: Session, permission_name: str) -> bool:
        """Check if user has a specific permission"""
        result = await session.execute(
            select(func.count())
            .select_from(
                select(Permission)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .join(Role, RolePermission.role_id == Role.id)
                .join(UserRole, UserRole.role_id == Role.id)
                .where(
                    and_(
                        UserRole.user_id == self.id,
                        Permission.name == permission_name
                    )
                )
                .subquery()
            )
        )
        return result.scalar() > 0
    
    async def has_role(self, session: Session, role_name: str) -> bool:
        """Check if user has a specific role"""
        result = await session.execute(
            select(func.count())
            .select_from(
                select(Role)
                .join(UserRole, UserRole.role_id == Role.id)
                .where(
                    and_(
                        UserRole.user_id == self.id,
                        Role.name == role_name
                    )
                )
                .subquery()
            )
        )
        return result.scalar() > 0
    
    async def assign_role(self, session: Session, role_name: str, assigned_by: int = None) -> bool:
        """Assign a role to user"""
        # Find role
        role = await session.execute(
            select(Role).where(Role.name == role_name.upper())
        )
        role = role.scalar_one_or_none()
        
        if not role:
            return False
        
        # Check if user already has this role
        existing_assignment = await session.execute(
            select(UserRole).where(
                and_(
                    UserRole.user_id == self.id,
                    UserRole.role_id == role.id
                )
            )
        )
        existing_assignment = existing_assignment.scalar_one_or_none()
        
        if existing_assignment:
            return False  # Already assigned
        
        # Create new assignment
        user_role = UserRole(
            user_id=self.id,
            role_id=role.id,
            assigned_by=assigned_by or self.id
        )
        
        session.add(user_role)
        return True
    
    async def remove_role(self, session: Session, role_name: str) -> bool:
        """Remove a role from user"""
        # Find role
        role = await session.execute(
            select(Role).where(Role.name == role_name.upper())
        )
        role = role.scalar_one_or_none()
        
        if not role:
            return False
        
        # Find and delete assignment
        assignment = await session.execute(
            select(UserRole).where(
                and_(
                    UserRole.user_id == self.id,
                    UserRole.role_id == role.id
                )
            )
        )
        assignment = assignment.scalar_one_or_none()
        
        if assignment:
            await session.delete(assignment)
            return True
        
        return False
    
    async def update_last_login(self, session: Session) -> None:
        """Update user's last login time"""
        self.last_login = datetime.utcnow()
        await session.commit()
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "profile_picture_url": self.profile_picture_url,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_suspended": self.is_suspended
        }
        
        if include_sensitive:
            data["password_hash"] = self.password_hash
            data["reset_token"] = self.reset_token
            data["reset_expires"] = self.reset_expires.isoformat() if self.reset_expires else None
        
        return data
    
    @classmethod
    async def get_statistics(cls, session: Session) -> Dict[str, Any]:
        """Get user statistics"""
        # Total users
        total_users = await session.scalar(
            select(func.count()).select_from(cls)
        )
        
        # Users by status
        users_by_status = await session.execute(
            select(cls.status, func.count())
            .select_from(cls)
            .group_by(cls.status)
        )
        status_counts = dict(users_by_status.all())
        
        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = await session.scalar(
            select(func.count())
            .select_from(cls)
            .where(cls.created_at >= thirty_days_ago)
        )
        
        # Active users (logged in last 30 days)
        active_users = await session.scalar(
            select(func.count())
            .select_from(cls)
            .where(
                and_(
                    cls.last_login >= thirty_days_ago,
                    cls.status == 'ACTIVE'
                )
            )
        )
        
        return {
            "total_users": total_users,
            "users_by_status": status_counts,
            "recent_registrations": recent_registrations,
            "active_users": active_users
        }


# Import related models to avoid circular imports
from src.models.user_role import UserRole