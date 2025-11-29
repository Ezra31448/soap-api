"""
Role-Permission junction model for Enhanced User Management System
"""
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.database.connection import Base


class RolePermission(Base):
    """Role-Permission junction model"""
    
    __tablename__ = "role_permissions"
    
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    granted_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission")
    granted_by_user = relationship("User", foreign_keys=[granted_by])
    
    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id}, granted_at={self.granted_at})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert role permission to dictionary"""
        return {
            "role_id": self.role_id,
            "permission_id": self.permission_id,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "granted_by": self.granted_by
        }