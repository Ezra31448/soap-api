"""
User-Role junction model for Enhanced User Management System
"""
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.database.connection import Base


class UserRole(Base):
    """User-Role junction model"""
    
    __tablename__ = "user_roles"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])
    
    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id}, assigned_at={self.assigned_at})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user role to dictionary"""
        return {
            "user_id": self.user_id,
            "role_id": self.role_id,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "assigned_by": self.assigned_by
        }