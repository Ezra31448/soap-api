"""
Session model for Enhanced User Management System
"""
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.database.connection import Base


class Session(Base):
    """Session model for user authentication sessions"""
    
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if session is valid (not expired)"""
        return not self.is_expired
    
    @property
    def time_remaining(self) -> int:
        """Get remaining time in seconds"""
        if self.is_expired:
            return 0
        
        delta = self.expires_at - datetime.utcnow()
        return int(delta.total_seconds())
    
    @classmethod
    async def find_by_id(cls, session, session_id: int):
        """Find session by ID"""
        result = await session.execute(
            select(cls).where(cls.id == session_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def find_by_token_hash(cls, session, token_hash: str):
        """Find session by token hash"""
        result = await session.execute(
            select(cls).where(cls.token_hash == token_hash)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def find_by_user_id(cls, session, user_id: int, limit: int = 10):
        """Find sessions for a user"""
        result = await session.execute(
            select(cls)
            .where(cls.user_id == user_id)
            .order_by(cls.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def find_active_by_user_id(cls, session, user_id: int, limit: int = 10):
        """Find active sessions for a user"""
        result = await session.execute(
            select(cls)
            .where(
                and_(
                    cls.user_id == user_id,
                    cls.expires_at > datetime.utcnow()
                )
            )
            .order_by(cls.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def find_expired(cls, session, limit: int = 100):
        """Find expired sessions"""
        result = await session.execute(
            select(cls)
            .where(cls.expires_at <= datetime.utcnow())
            .order_by(cls.expires_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def cleanup_expired_sessions(cls, session) -> int:
        """Delete expired sessions and return count"""
        from sqlalchemy import delete
        
        delete_stmt = delete(cls).where(cls.expires_at <= datetime.utcnow())
        result = await session.execute(delete_stmt)
        await session.commit()
        
        return result.rowcount
    
    @classmethod
    async def get_session_statistics(cls, session) -> Dict[str, Any]:
        """Get session statistics"""
        # Total sessions
        total_sessions = await session.scalar(
            select(func.count()).select_from(cls)
        )
        
        # Active sessions
        active_sessions = await session.scalar(
            select(func.count()).select_from(
                select(cls).where(cls.expires_at > datetime.utcnow())
            )
        )
        
        # Expired sessions
        expired_sessions = total_sessions - active_sessions
        
        # Sessions by user (top 10 users with most sessions)
        sessions_by_user = await session.execute(
            select(cls.user_id, func.count().label('session_count'))
            .group_by(cls.user_id)
            .order_by(func.count().desc())
            .limit(10)
        )
        user_session_counts = [
            {
                "user_id": row.user_id,
                "session_count": row.session_count
            }
            for row in sessions_by_user.all()
        ]
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions,
            "top_users_by_sessions": user_session_counts
        }
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert session to dictionary"""
        data = {
            "session_id": self.id,
            "user_id": self.user_id,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "is_expired": self.is_expired,
            "is_valid": self.is_valid,
            "time_remaining": self.time_remaining
        }
        
        if include_sensitive:
            data["token_hash"] = self.token_hash
        
        return data