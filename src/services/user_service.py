"""
User service for Enhanced User Management System
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
import structlog

from src.database.connection import get_database_session
from src.services.auth_service import AuthService
from src.utils.exceptions import ValidationError, NotFoundError, ConflictError, AuthorizationError
from src.models.user import User

logger = structlog.get_logger()


class UserService:
    """Service for handling user operations"""
    
    def __init__(self):
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.auth_service = AuthService()
    
    async def register_user(self, email: str, password: str, first_name: str, 
                          last_name: str, phone_number: str = None) -> Dict[str, Any]:
        """
        Register a new user
        """
        async with get_database_session() as session:
            try:
                # Check if user already exists
                existing_user = await User.find_by_email(session, email)
                if existing_user:
                    raise ConflictError("User with this email already exists")
                
                # Validate password strength
                password_validation = self.auth_service.validate_password_strength(password)
                if not password_validation["is_valid"]:
                    raise ValidationError("Password does not meet requirements", 
                                     {"errors": password_validation["errors"]})
                
                # Hash password
                password_hash = self.auth_service.hash_password(password)
                
                # Create user
                user = User(
                    email=email,
                    password_hash=password_hash,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    status="ACTIVE"
                )
                
                session.add(user)
                await session.flush()  # Get the user ID
                
                # Assign default USER role
                await user.assign_role(session, "USER")
                
                await session.commit()
                
                self.logger.info("User registered successfully", 
                              user_id=user.id, 
                              email=email)
                
                return {
                    "user_id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "status": user.status,
                    "created_at": user.created_at.isoformat()
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("User registration failed", error=str(e))
                raise
    
    async def get_user_profile(self, requesting_user_id: int, target_user_id: int) -> Dict[str, Any]:
        """
        Get user profile information
        """
        async with get_database_session() as session:
            try:
                # Get requesting user
                requesting_user = await User.find_by_id(session, requesting_user_id)
                if not requesting_user:
                    raise NotFoundError("Requesting user not found")
                
                # Get target user
                target_user = await User.find_by_id(session, target_user_id)
                if not target_user:
                    raise NotFoundError("User not found")
                
                # Check authorization
                if requesting_user_id != target_user_id:
                    # Check if requesting user has permission to view other profiles
                    if not await requesting_user.has_permission(session, "PROFILE_READ_ALL"):
                        raise AuthorizationError("You don't have permission to view this profile")
                
                # Get user roles
                roles = await target_user.get_roles(session)
                
                self.logger.info("User profile retrieved", 
                              requesting_user_id=requesting_user_id,
                              target_user_id=target_user_id)
                
                return {
                    "user_id": target_user.id,
                    "email": target_user.email,
                    "first_name": target_user.first_name,
                    "last_name": target_user.last_name,
                    "phone_number": target_user.phone_number,
                    "profile_picture_url": target_user.profile_picture_url,
                    "status": target_user.status,
                    "roles": [role.name for role in roles],
                    "created_at": target_user.created_at.isoformat(),
                    "updated_at": target_user.updated_at.isoformat(),
                    "last_login": target_user.last_login.isoformat() if target_user.last_login else None
                }
                
            except Exception as e:
                self.logger.error("Get user profile failed", error=str(e))
                raise
    
    async def update_user_profile(self, requesting_user_id: int, target_user_id: int, 
                               update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile information
        """
        async with get_database_session() as session:
            try:
                # Get requesting user
                requesting_user = await User.find_by_id(session, requesting_user_id)
                if not requesting_user:
                    raise NotFoundError("Requesting user not found")
                
                # Get target user
                target_user = await User.find_by_id(session, target_user_id)
                if not target_user:
                    raise NotFoundError("User not found")
                
                # Check authorization
                if requesting_user_id != target_user_id:
                    # Check if requesting user has permission to update other profiles
                    if not await requesting_user.has_permission(session, "PROFILE_UPDATE_ALL"):
                        raise AuthorizationError("You don't have permission to update this profile")
                else:
                    # Check if user can update own profile
                    if not await requesting_user.has_permission(session, "PROFILE_UPDATE_OWN"):
                        raise AuthorizationError("You don't have permission to update your profile")
                
                # Store old values for audit
                old_values = {
                    "first_name": target_user.first_name,
                    "last_name": target_user.last_name,
                    "phone_number": target_user.phone_number,
                    "profile_picture_url": target_user.profile_picture_url
                }
                
                # Update user data
                if "first_name" in update_data:
                    target_user.first_name = update_data["first_name"]
                if "last_name" in update_data:
                    target_user.last_name = update_data["last_name"]
                if "phone_number" in update_data:
                    target_user.phone_number = update_data["phone_number"]
                if "profile_picture_url" in update_data:
                    target_user.profile_picture_url = update_data["profile_picture_url"]
                
                await session.commit()
                
                # Get updated roles
                roles = await target_user.get_roles(session)
                
                self.logger.info("User profile updated", 
                              requesting_user_id=requesting_user_id,
                              target_user_id=target_user_id,
                              update_data=update_data)
                
                return {
                    "user_id": target_user.id,
                    "email": target_user.email,
                    "first_name": target_user.first_name,
                    "last_name": target_user.last_name,
                    "phone_number": target_user.phone_number,
                    "profile_picture_url": target_user.profile_picture_url,
                    "status": target_user.status,
                    "roles": [role.name for role in roles],
                    "updated_at": target_user.updated_at.isoformat()
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Update user profile failed", error=str(e))
                raise
    
    async def get_all_users(self, requesting_user_id: int, page: int = 1, 
                          page_size: int = 20, status: str = None) -> Dict[str, Any]:
        """
        Get all users with pagination
        """
        async with get_database_session() as session:
            try:
                # Get requesting user
                requesting_user = await User.find_by_id(session, requesting_user_id)
                if not requesting_user:
                    raise NotFoundError("Requesting user not found")
                
                # Check authorization
                if not await requesting_user.has_permission(session, "USER_LIST"):
                    raise AuthorizationError("You don't have permission to list users")
                
                # Get users with pagination
                offset = (page - 1) * page_size
                users, total_count = await User.find_all_with_pagination(
                    session, offset, page_size, status
                )
                
                # Format user data
                user_list = []
                for user in users:
                    roles = await user.get_roles(session)
                    user_data = {
                        "user_id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "phone_number": user.phone_number,
                        "status": user.status,
                        "roles": [role.name for role in roles],
                        "created_at": user.created_at.isoformat(),
                        "last_login": user.last_login.isoformat() if user.last_login else None
                    }
                    user_list.append(user_data)
                
                self.logger.info("Users retrieved", 
                              requesting_user_id=requesting_user_id,
                              page=page,
                              page_size=page_size,
                              total_count=total_count)
                
                return {
                    "users": user_list,
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
                
            except Exception as e:
                self.logger.error("Get all users failed", error=str(e))
                raise
    
    async def deactivate_user(self, requesting_user_id: int, target_user_id: int) -> Dict[str, Any]:
        """
        Deactivate a user
        """
        async with get_database_session() as session:
            try:
                # Get requesting user
                requesting_user = await User.find_by_id(session, requesting_user_id)
                if not requesting_user:
                    raise NotFoundError("Requesting user not found")
                
                # Get target user
                target_user = await User.find_by_id(session, target_user_id)
                if not target_user:
                    raise NotFoundError("User not found")
                
                # Check authorization
                if not await requesting_user.has_permission(session, "USER_DELETE"):
                    raise AuthorizationError("You don't have permission to deactivate users")
                
                # Cannot deactivate yourself
                if requesting_user_id == target_user_id:
                    raise ValidationError("You cannot deactivate your own account")
                
                # Update user status
                target_user.status = "INACTIVE"
                await session.commit()
                
                # Invalidate all sessions for the user
                await self.auth_service.invalidate_all_sessions(target_user_id)
                
                self.logger.info("User deactivated", 
                              requesting_user_id=requesting_user_id,
                              target_user_id=target_user_id)
                
                return {
                    "user_id": target_user.id,
                    "email": target_user.email,
                    "status": target_user.status,
                    "message": "User deactivated successfully"
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Deactivate user failed", error=str(e))
                raise
    
    async def activate_user(self, requesting_user_id: int, target_user_id: int) -> Dict[str, Any]:
        """
        Activate a user
        """
        async with get_database_session() as session:
            try:
                # Get requesting user
                requesting_user = await User.find_by_id(session, requesting_user_id)
                if not requesting_user:
                    raise NotFoundError("Requesting user not found")
                
                # Get target user
                target_user = await User.find_by_id(session, target_user_id)
                if not target_user:
                    raise NotFoundError("User not found")
                
                # Check authorization
                if not await requesting_user.has_permission(session, "USER_UPDATE"):
                    raise AuthorizationError("You don't have permission to activate users")
                
                # Update user status
                target_user.status = "ACTIVE"
                await session.commit()
                
                self.logger.info("User activated", 
                              requesting_user_id=requesting_user_id,
                              target_user_id=target_user_id)
                
                return {
                    "user_id": target_user.id,
                    "email": target_user.email,
                    "status": target_user.status,
                    "message": "User activated successfully"
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Activate user failed", error=str(e))
                raise
    
    async def change_password(self, user_id: int, current_password: str, 
                           new_password: str) -> Dict[str, Any]:
        """
        Change user password
        """
        async with get_database_session() as session:
            try:
                # Get user
                user = await User.find_by_id(session, user_id)
                if not user:
                    raise NotFoundError("User not found")
                
                # Verify current password
                if not self.auth_service._verify_password(current_password, user.password_hash):
                    raise ValidationError("Current password is incorrect")
                
                # Validate new password strength
                password_validation = self.auth_service.validate_password_strength(new_password)
                if not password_validation["is_valid"]:
                    raise ValidationError("New password does not meet requirements", 
                                     {"errors": password_validation["errors"]})
                
                # Hash new password
                new_password_hash = self.auth_service.hash_password(new_password)
                
                # Update password
                user.password_hash = new_password_hash
                await session.commit()
                
                # Invalidate all sessions for the user (force re-login)
                await self.auth_service.invalidate_all_sessions(user_id)
                
                self.logger.info("Password changed", user_id=user_id)
                
                return {
                    "user_id": user.id,
                    "message": "Password changed successfully"
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Change password failed", error=str(e))
                raise
    
    async def request_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Request password reset for user
        """
        async with get_database_session() as session:
            try:
                # Find user by email
                user = await User.find_by_email(session, email)
                if not user:
                    # Don't reveal if user exists or not for security
                    self.logger.info("Password reset requested for non-existent email", email=email)
                    return {
                        "success": True,
                        "message": "If the email exists, a reset link has been sent"
                    }
                
                # Generate reset token
                reset_token = await self.auth_service.generate_password_reset_token(user.id, email)
                reset_expires = datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry
                
                # Update user with reset token
                user.reset_token = reset_token
                user.reset_expires = reset_expires
                await session.commit()
                
                # TODO: Send email with reset link
                # This would integrate with an email service
                
                self.logger.info("Password reset requested",
                              user_id=user.id,
                              email=email)
                
                return {
                    "success": True,
                    "message": "If the email exists, a reset link has been sent"
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Password reset request failed", error=str(e))
                raise
    
    async def reset_password(self, reset_token: str, new_password: str) -> Dict[str, Any]:
        """
        Reset password using reset token
        """
        async with get_database_session() as session:
            try:
                # Verify reset token
                token_info = await self.auth_service.verify_password_reset_token(reset_token)
                if not token_info:
                    raise ValidationError("Invalid or expired reset token")
                
                # Find user
                user = await User.find_by_id(session, token_info["user_id"])
                if not user:
                    raise NotFoundError("User not found")
                
                # Check if token is expired
                if user.reset_expires and user.reset_expires < datetime.utcnow():
                    raise ValidationError("Reset token has expired")
                
                # Validate new password strength
                password_validation = self.auth_service.validate_password_strength(new_password)
                if not password_validation["is_valid"]:
                    raise ValidationError("Password does not meet requirements",
                                     {"errors": password_validation["errors"]})
                
                # Hash new password
                new_password_hash = self.auth_service.hash_password(new_password)
                
                # Update password and clear reset token
                user.password_hash = new_password_hash
                user.reset_token = None
                user.reset_expires = None
                await session.commit()
                
                # Invalidate all sessions for user (force re-login)
                await self.auth_service.invalidate_all_sessions(user.id)
                
                self.logger.info("Password reset completed",
                              user_id=user.id)
                
                return {
                    "success": True,
                    "message": "Password reset successfully"
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Password reset failed", error=str(e))
                raise
    
    async def assign_role(self, requesting_user_id: int, target_user_id: int,
                        role_id: int) -> Dict[str, Any]:
        """
        Assign a role to a user
        """
        async with get_database_session() as session:
            try:
                # Get requesting user
                requesting_user = await User.find_by_id(session, requesting_user_id)
                if not requesting_user:
                    raise NotFoundError("Requesting user not found")
                
                # Get target user
                target_user = await User.find_by_id(session, target_user_id)
                if not target_user:
                    raise NotFoundError("Target user not found")
                
                # Get role
                from src.models.role import Role
                role = await Role.find_by_id(session, role_id)
                if not role:
                    raise NotFoundError("Role not found")
                
                # Check authorization
                if not await requesting_user.has_permission(session, "ROLE_ASSIGN"):
                    raise AuthorizationError("You don't have permission to assign roles")
                
                # Assign role to user
                success = await target_user.assign_role(session, role.name, requesting_user_id)
                
                if not success:
                    raise ConflictError("User already has this role")
                
                await session.commit()
                
                self.logger.info("Role assigned to user",
                              requesting_user_id=requesting_user_id,
                              target_user_id=target_user_id,
                              role_id=role_id)
                
                return {
                    "success": True,
                    "message": "Role assigned successfully"
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Assign role failed", error=str(e))
                raise
    
    async def get_user_roles(self, requesting_user_id: int,
                           target_user_id: int = None) -> Dict[str, Any]:
        """
        Get user's roles
        """
        async with get_database_session() as session:
            try:
                # Get requesting user
                requesting_user = await User.find_by_id(session, requesting_user_id)
                if not requesting_user:
                    raise NotFoundError("Requesting user not found")
                
                # Determine target user
                target_id = target_user_id or requesting_user_id
                
                # Check authorization if viewing other user's roles
                if target_id != requesting_user_id:
                    if not await requesting_user.has_permission(session, "ROLE_READ"):
                        raise AuthorizationError("You don't have permission to view roles")
                
                # Get target user
                target_user = await User.find_by_id(session, target_id)
                if not target_user:
                    raise NotFoundError("Target user not found")
                
                # Get user's roles
                roles = await target_user.get_roles(session)
                
                self.logger.info("User roles retrieved",
                              requesting_user_id=requesting_user_id,
                              target_user_id=target_id)
                
                return {
                    "user_id": target_id,
                    "roles": [role.to_dict() for role in roles]
                }
                
            except Exception as e:
                self.logger.error("Get user roles failed", error=str(e))
                raise