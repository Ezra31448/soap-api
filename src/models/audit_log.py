"""
Audit Log model for Enhanced User Management System
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import select, func, and_, or_

from src.database.connection import Base


class AuditLog(Base):
    """Audit Log model"""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action})>"
    
    @property
    def is_user_action(self) -> bool:
        """Check if this is a user-related action"""
        return self.resource_type == "USER"
    
    @property
    def is_role_action(self) -> bool:
        """Check if this is a role-related action"""
        return self.resource_type == "ROLE"
    
    @property
    def is_permission_action(self) -> bool:
        """Check if this is a permission-related action"""
        return self.resource_type == "PERMISSION"
    
    @property
    def is_profile_action(self) -> bool:
        """Check if this is a profile-related action"""
        return self.resource_type == "PROFILE"
    
    @classmethod
    async def find_by_id(cls, session: Session, audit_id: int) -> Optional['AuditLog']:
        """Find audit log by ID"""
        result = await session.execute(
            select(cls).where(cls.id == audit_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def find_by_user_id(cls, session: Session, user_id: int, 
                            limit: int = 100) -> list['AuditLog']:
        """Find audit logs by user ID"""
        result = await session.execute(
            select(cls)
            .where(cls.user_id == user_id)
            .order_by(cls.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def find_by_action(cls, session: Session, action: str, 
                          limit: int = 100) -> list['AuditLog']:
        """Find audit logs by action"""
        result = await session.execute(
            select(cls)
            .where(cls.action == action)
            .order_by(cls.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def find_by_resource(cls, session: Session, resource_type: str, 
                            resource_id: int = None, limit: int = 100) -> list['AuditLog']:
        """Find audit logs by resource"""
        query = select(cls).where(cls.resource_type == resource_type)
        
        if resource_id:
            query = query.where(cls.resource_id == resource_id)
        
        result = await session.execute(
            query.order_by(cls.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def find_by_date_range(cls, session: Session, start_date: datetime, 
                               end_date: datetime, limit: int = 100) -> list['AuditLog']:
        """Find audit logs by date range"""
        result = await session.execute(
            select(cls)
            .where(
                and_(
                    cls.created_at >= start_date,
                    cls.created_at <= end_date
                )
            )
            .order_by(cls.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @classmethod
    def build_query(cls, user_id: int = None, action: str = None,
                   resource_type: str = None, start_date: datetime = None,
                   end_date: datetime = None):
        """Build a query with optional filters"""
        query = select(cls)
        
        # Apply filters
        if user_id:
            query = query.where(cls.user_id == user_id)
        
        if action:
            query = query.where(cls.action == action)
        
        if resource_type:
            query = query.where(cls.resource_type == resource_type)
        
        if start_date:
            query = query.where(cls.created_at >= start_date)
        
        if end_date:
            query = query.where(cls.created_at <= end_date)
        
        return query
    
    @classmethod
    def build_count_query(cls, user_id: int = None, action: str = None,
                        resource_type: str = None, start_date: datetime = None,
                        end_date: datetime = None):
        """Build a count query with optional filters"""
        query = select(func.count()).select_from(
            cls.build_query(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                start_date=start_date,
                end_date=end_date
            ).subquery()
        )
        return query
    
    @classmethod
    async def get_recent_events(cls, session: Session, hours: int = 24, 
                            limit: int = 50) -> list['AuditLog']:
        """Get recent audit events within specified hours"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        result = await session.execute(
            select(cls)
            .where(cls.created_at >= time_threshold)
            .order_by(cls.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def get_failed_logins(cls, session: Session, hours: int = 24, 
                               limit: int = 50) -> list['AuditLog']:
        """Get failed login attempts within specified hours"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        result = await session.execute(
            select(cls)
            .where(
                and_(
                    cls.action == 'USER_LOGIN_FAILED',
                    cls.created_at >= time_threshold
                )
            )
            .order_by(cls.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def get_user_activity_summary(cls, session: Session, user_id: int, 
                                   days: int = 30) -> Dict[str, Any]:
        """Get user activity summary for specified days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total actions
        total_actions = await session.scalar(
            select(func.count())
            .select_from(
                select(cls).where(
                    and_(
                        cls.user_id == user_id,
                        cls.created_at >= start_date
                    )
                )
            )
        )
        
        # Actions by type
        actions_by_type = await session.execute(
            select(cls.resource_type, func.count())
            .select_from(
                select(cls).where(
                    and_(
                        cls.user_id == user_id,
                        cls.created_at >= start_date
                    )
                )
            )
            .group_by(cls.resource_type)
        )
        type_counts = dict(actions_by_type.all())
        
        # Most recent action
        most_recent = await session.execute(
            select(cls)
            .where(cls.user_id == user_id)
            .order_by(cls.created_at.desc())
            .limit(1)
        )
        recent_action = most_recent.scalar_one_or_none()
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_actions": total_actions,
            "actions_by_type": type_counts,
            "most_recent_action": {
                "action": recent_action.action if recent_action else None,
                "resource_type": recent_action.resource_type if recent_action else None,
                "created_at": recent_action.created_at.isoformat() if recent_action else None
            }
        }
    
    @classmethod
    async def get_security_events(cls, session: Session, hours: int = 24, 
                              limit: int = 100) -> list['AuditLog']:
        """Get security-related events"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Security-related actions
        security_actions = [
            'USER_LOGIN_FAILED',
            'USER_LOGIN_SUCCESS',
            'USER_LOGOUT',
            'PASSWORD_RESET_REQUEST',
            'PASSWORD_RESET_SUCCESS',
            'UNAUTHORIZED_ACCESS_ATTEMPT'
        ]
        
        result = await session.execute(
            select(cls)
            .where(
                and_(
                    cls.action.in_(security_actions),
                    cls.created_at >= time_threshold
                )
            )
            .order_by(cls.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary"""
        return {
            "audit_id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_user_action": self.is_user_action,
            "is_role_action": self.is_role_action,
            "is_permission_action": self.is_permission_action,
            "is_profile_action": self.is_profile_action
        }
    
    @classmethod
    async def get_statistics(cls, session: Session, days: int = 30) -> Dict[str, Any]:
        """Get audit statistics for specified days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total events
        total_events = await session.scalar(
            select(func.count())
            .select_from(
                select(cls).where(cls.created_at >= start_date)
            )
        )
        
        # Events by action
        events_by_action = await session.execute(
            select(cls.action, func.count())
            .select_from(
                select(cls).where(cls.created_at >= start_date)
            )
            .group_by(cls.action)
            .order_by(func.count().desc())
            .limit(10)
        )
        action_counts = [
            {
                "action": row.action,
                "count": row.count
            }
            for row in events_by_action.all()
        ]
        
        # Events by resource type
        events_by_resource = await session.execute(
            select(cls.resource_type, func.count())
            .select_from(
                select(cls).where(cls.created_at >= start_date)
            )
            .group_by(cls.resource_type)
            .order_by(func.count().desc())
        )
        resource_counts = [
            {
                "resource_type": row.resource_type,
                "count": row.count
            }
            for row in events_by_resource.all()
        ]
        
        # Unique users
        unique_users = await session.scalar(
            select(func.count(func.distinct(cls.user_id)))
            .select_from(
                select(cls).where(
                    and_(
                        cls.created_at >= start_date,
                        cls.user_id.isnot(None)
                    )
                )
            )
        )
        
        return {
            "period_days": days,
            "total_events": total_events,
            "events_by_action": action_counts,
            "events_by_resource_type": resource_counts,
            "unique_active_users": unique_users
        }