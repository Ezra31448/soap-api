"""
Role service for Enhanced User Management System
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
import structlog

from src.database.connection import get_database_session
from src.utils.exceptions import ValidationError, NotFoundError, ConflictError, AuthorizationError
from src.models.role import Role
from src.models.permission import Permission

logger = structlog.get_logger()


class RoleService:
    """Service for handling role operations"""
    
    def __init__(self):
        self.logger = structlog.get_logger(self.__class__.__name__)
    
    async def create_role(self, name: str, description: str = None) -> Dict[str, Any]:
        """
        Create a new role
        """
        async with get_database_session() as session:
            try:
                # Check if role already exists
                existing_role = await Role.find_by_name(session, name)
                if existing_role:
                    raise ConflictError("Role with this name already exists")
                
                # Create role
                role = Role(
                    name=name.upper(),
                    description=description
                )
                
                session.add(role)
                await session.commit()
                
                self.logger.info("Role created successfully", 
                              role_id=role.id, 
                              name=name)
                
                return {
                    "role_id": role.id,
                    "name": role.name,
                    "description": role.description,
                    "created_at": role.created_at.isoformat()
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Role creation failed", error=str(e))
                raise
    
    async def get_role(self, role_id: int) -> Dict[str, Any]:
        """
        Get role information by ID
        """
        async with get_database_session() as session:
            try:
                # Get role
                role = await Role.find_by_id(session, role_id)
                if not role:
                    raise NotFoundError("Role not found")
                
                # Get role permissions
                permissions = await role.get_permissions(session)
                
                self.logger.info("Role retrieved", role_id=role_id)
                
                return {
                    "role_id": role.id,
                    "name": role.name,
                    "description": role.description,
                    "permissions": [perm.to_dict() for perm in permissions],
                    "created_at": role.created_at.isoformat(),
                    "updated_at": role.updated_at.isoformat()
                }
                
            except Exception as e:
                self.logger.error("Get role failed", error=str(e))
                raise
    
    async def get_all_roles(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Get all roles with pagination
        """
        async with get_database_session() as session:
            try:
                # Get roles with pagination
                offset = (page - 1) * page_size
                roles, total_count = await Role.find_all_with_pagination(
                    session, offset, page_size
                )
                
                # Format role data
                role_list = []
                for role in roles:
                    role_data = {
                        "role_id": role.id,
                        "name": role.name,
                        "description": role.description,
                        "created_at": role.created_at.isoformat(),
                        "updated_at": role.updated_at.isoformat()
                    }
                    role_list.append(role_data)
                
                self.logger.info("Roles retrieved", 
                              page=page,
                              page_size=page_size,
                              total_count=total_count)
                
                return {
                    "roles": role_list,
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
                
            except Exception as e:
                self.logger.error("Get all roles failed", error=str(e))
                raise
    
    async def update_role(self, role_id: int, name: str = None, 
                       description: str = None) -> Dict[str, Any]:
        """
        Update role information
        """
        async with get_database_session() as session:
            try:
                # Get role
                role = await Role.find_by_id(session, role_id)
                if not role:
                    raise NotFoundError("Role not found")
                
                # Check if new name conflicts with existing role
                if name and name.upper() != role.name:
                    existing_role = await Role.find_by_name(session, name)
                    if existing_role:
                        raise ConflictError("Role with this name already exists")
                
                # Update role data
                if name:
                    role.name = name.upper()
                if description is not None:
                    role.description = description
                
                await session.commit()
                
                self.logger.info("Role updated", 
                              role_id=role_id,
                              update_data={"name": name, "description": description})
                
                return {
                    "role_id": role.id,
                    "name": role.name,
                    "description": role.description,
                    "updated_at": role.updated_at.isoformat()
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Update role failed", error=str(e))
                raise
    
    async def delete_role(self, role_id: int) -> Dict[str, Any]:
        """
        Delete a role
        """
        async with get_database_session() as session:
            try:
                # Get role
                role = await Role.find_by_id(session, role_id)
                if not role:
                    raise NotFoundError("Role not found")
                
                # Cannot delete ADMIN role
                if role.is_admin:
                    raise ValidationError("Cannot delete ADMIN role")
                
                # Store role info for response
                role_info = {
                    "role_id": role.id,
                    "name": role.name,
                    "description": role.description
                }
                
                # Delete role (cascade will handle related records)
                await session.delete(role)
                await session.commit()
                
                self.logger.info("Role deleted", role_id=role_id)
                
                return {
                    **role_info,
                    "message": "Role deleted successfully"
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Delete role failed", error=str(e))
                raise
    
    async def assign_permission_to_role(self, role_id: int, permission_id: int, 
                                     assigned_by: int) -> Dict[str, Any]:
        """
        Assign a permission to a role
        """
        async with get_database_session() as session:
            try:
                # Get role
                role = await Role.find_by_id(session, role_id)
                if not role:
                    raise NotFoundError("Role not found")
                
                # Get permission
                permission = await Permission.find_by_id(session, permission_id)
                if not permission:
                    raise NotFoundError("Permission not found")
                
                # Assign permission to role
                success = await role.assign_permission(
                    session, permission.name, assigned_by
                )
                
                if not success:
                    raise ConflictError("Permission already assigned to role")
                
                await session.commit()
                
                self.logger.info("Permission assigned to role", 
                              role_id=role_id,
                              permission_id=permission_id,
                              assigned_by=assigned_by)
                
                return {
                    "role_id": role.id,
                    "permission_id": permission.id,
                    "permission_name": permission.name,
                    "message": "Permission assigned to role successfully"
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Assign permission to role failed", error=str(e))
                raise
    
    async def remove_permission_from_role(self, role_id: int, permission_id: int) -> Dict[str, Any]:
        """
        Remove a permission from a role
        """
        async with get_database_session() as session:
            try:
                # Get role
                role = await Role.find_by_id(session, role_id)
                if not role:
                    raise NotFoundError("Role not found")
                
                # Get permission
                permission = await Permission.find_by_id(session, permission_id)
                if not permission:
                    raise NotFoundError("Permission not found")
                
                # Remove permission from role
                success = await role.remove_permission(session, permission.name)
                
                if not success:
                    raise NotFoundError("Permission not assigned to role")
                
                await session.commit()
                
                self.logger.info("Permission removed from role", 
                              role_id=role_id,
                              permission_id=permission_id)
                
                return {
                    "role_id": role.id,
                    "permission_id": permission.id,
                    "permission_name": permission.name,
                    "message": "Permission removed from role successfully"
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Remove permission from role failed", error=str(e))
                raise
    
    async def create_permission(self, name: str, description: str = None,
                           module: str = None, action: str = None) -> Dict[str, Any]:
        """
        Create a new permission
        """
        async with get_database_session() as session:
            try:
                # Check if permission already exists
                existing_permission = await Permission.find_by_name(session, name)
                if existing_permission:
                    raise ConflictError("Permission with this name already exists")
                
                # Create permission
                permission = Permission(
                    name=name,
                    description=description,
                    module=module or "CUSTOM",
                    action=action or "CUSTOM"
                )
                
                session.add(permission)
                await session.commit()
                
                self.logger.info("Permission created successfully",
                              permission_id=permission.id,
                              name=name)
                
                return {
                    "permission_id": permission.id,
                    "name": permission.name,
                    "description": permission.description,
                    "module": permission.module,
                    "action": permission.action,
                    "created_at": permission.created_at.isoformat()
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Permission creation failed", error=str(e))
                raise
    
    async def get_all_permissions(self, page: int = 1,
                               page_size: int = 20) -> Dict[str, Any]:
        """
        Get all permissions with pagination
        """
        async with get_database_session() as session:
            try:
                # Get permissions with pagination
                offset = (page - 1) * page_size
                permissions, total_count = await Permission.find_all_with_pagination(
                    session, offset, page_size
                )
                
                # Format permission data
                permission_list = []
                for permission in permissions:
                    permission_data = {
                        "permission_id": permission.id,
                        "name": permission.name,
                        "description": permission.description,
                        "module": permission.module,
                        "action": permission.action,
                        "created_at": permission.created_at.isoformat()
                    }
                    permission_list.append(permission_data)
                
                self.logger.info("Permissions retrieved",
                              page=page,
                              page_size=page_size,
                              total_count=total_count)
                
                return {
                    "permissions": permission_list,
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
                
            except Exception as e:
                self.logger.error("Get all permissions failed", error=str(e))
                raise