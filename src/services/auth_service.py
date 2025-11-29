"""
Authentication service for Enhanced User Management System
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import bcrypt
import jwt
import structlog

from src.config.settings import settings
from src.database.connection import get_database_session
from src.database.redis import create_session, delete_session, get_session, delete_all_user_sessions
from src.utils.exceptions import AuthenticationError, AuthorizationError, ValidationError
from src.models.user import User

logger = structlog.get_logger()


class AuthService:
    """Service for handling authentication operations"""
    
    def __init__(self):
        self.logger = structlog.get_logger(self.__class__.__name__)
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password
        """
        async with get_database_session() as session:
            try:
                # Find user by email
                user = await User.find_by_email(session, email)
                
                if not user:
                    self.logger.warning("Authentication failed - user not found", email=email)
                    return {
                        "success": False,
                        "message": "Invalid credentials"
                    }
                
                # Check if user is active
                if user.status != "ACTIVE":
                    self.logger.warning("Authentication failed - user inactive", email=email, status=user.status)
                    return {
                        "success": False,
                        "message": "Account is not active"
                    }
                
                # Verify password
                if not self._verify_password(password, user.password_hash):
                    self.logger.warning("Authentication failed - invalid password", email=email)
                    return {
                        "success": False,
                        "message": "Invalid credentials"
                    }
                
                # Generate JWT token
                token = self._generate_token(user)
                
                # Create session
                session_id = await create_session(
                    user_id=user.id,
                    session_data={
                        "email": user.email,
                        "login_time": datetime.utcnow().isoformat(),
                        "ip_address": None  # Will be set by API layer
                    },
                    expire_hours=settings.JWT_EXPIRATION_HOURS
                )
                
                # Update last login
                user.last_login = datetime.utcnow()
                await session.commit()
                
                # Get user roles
                roles = await user.get_roles(session)
                
                self.logger.info("User authenticated successfully", 
                              user_id=user.id, 
                              email=email)
                
                return {
                    "success": True,
                    "user_id": user.id,
                    "email": user.email,
                    "token": token,
                    "session_id": session_id,
                    "roles": [role.name for role in roles],
                    "expires_in": settings.JWT_EXPIRATION_HOURS * 3600,
                    "message": "Authentication successful"
                }
                
            except Exception as e:
                self.logger.error("Authentication error", error=str(e))
                raise AuthenticationError("Authentication failed")
    
    async def logout_user(self, token: str) -> Dict[str, Any]:
        """
        Logout user and invalidate token
        """
        try:
            # Validate token and get user info
            user_info = self.validate_token(token)
            if not user_info:
                return {
                    "success": False,
                    "message": "Invalid token"
                }
            
            # Delete session from Redis
            session_id = user_info.get("session_id")
            if session_id:
                await delete_session(session_id)
            
            self.logger.info("User logged out", 
                          user_id=user_info.get("user_id"))
            
            return {
                "success": True,
                "message": "Logout successful"
            }
            
        except Exception as e:
            self.logger.error("Logout error", error=str(e))
            raise AuthenticationError("Logout failed")
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token and return user info
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                self.logger.warning("Token expired", user_id=payload.get("user_id"))
                return None
            
            # Get session from Redis
            session_id = payload.get("session_id")
            if session_id:
                session_data = await get_session(session_id)
                if not session_data:
                    self.logger.warning("Session not found", session_id=session_id)
                    return None
            
            return {
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "session_id": session_id,
                "roles": payload.get("roles", [])
            }
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token signature expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning("Invalid token", error=str(e))
            return None
        except Exception as e:
            self.logger.error("Token validation error", error=str(e))
            return None
    
    async def refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Refresh JWT token
        """
        try:
            # Validate current token
            user_info = self.validate_token(token)
            if not user_info:
                return {
                    "success": False,
                    "message": "Invalid token"
                }
            
            # Get user from database
            async with get_database_session() as session:
                user = await User.find_by_id(session, user_info["user_id"])
                
                if not user or user.status != "ACTIVE":
                    return {
                        "success": False,
                        "message": "User not found or inactive"
                    }
            
            # Generate new token
            new_token = self._generate_token(user)
            
            # Create new session
            session_id = await create_session(
                user_id=user.id,
                session_data={
                    "email": user.email,
                    "refresh_time": datetime.utcnow().isoformat(),
                    "ip_address": None
                },
                expire_hours=settings.JWT_EXPIRATION_HOURS
            )
            
            # Delete old session
            old_session_id = user_info.get("session_id")
            if old_session_id:
                await delete_session(old_session_id)
            
            self.logger.info("Token refreshed", 
                          user_id=user.id)
            
            return {
                "success": True,
                "user_id": user.id,
                "email": user.email,
                "token": new_token,
                "session_id": session_id,
                "roles": user_info.get("roles", []),
                "expires_in": settings.JWT_EXPIRATION_HOURS * 3600,
                "message": "Token refreshed successfully"
            }
            
        except Exception as e:
            self.logger.error("Token refresh error", error=str(e))
            raise AuthenticationError("Token refresh failed")
    
    async def invalidate_all_sessions(self, user_id: int) -> Dict[str, Any]:
        """
        Invalidate all sessions for a user
        """
        try:
            deleted_count = await delete_all_user_sessions(user_id)
            
            self.logger.info("All sessions invalidated", 
                          user_id=user_id, 
                          deleted_count=deleted_count)
            
            return {
                "success": True,
                "deleted_sessions": deleted_count,
                "message": "All sessions invalidated successfully"
            }
            
        except Exception as e:
            self.logger.error("Session invalidation error", error=str(e))
            raise AuthenticationError("Failed to invalidate sessions")
    
    def _generate_token(self, user: 'User') -> str:
        """
        Generate JWT token for user
        """
        now = datetime.utcnow()
        exp = now + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        
        # Get user roles (this should be passed from caller for efficiency)
        # For now, use empty list
        roles = []
        
        payload = {
            "user_id": user.id,
            "email": user.email,
            "roles": roles,
            "iat": now,
            "exp": exp,
            "session_id": None  # Will be set after session creation
        }
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            self.logger.error("Password verification error", error=str(e))
            return False
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt
        """
        try:
            # Generate salt and hash
            salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            return password_hash.decode('utf-8')
        except Exception as e:
            logger.error("Password hashing error", error=str(e))
            raise ValidationError("Password hashing failed")
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        Validate password strength
        """
        errors = []
        
        # Check minimum length
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long")
        
        # Check for uppercase letter
        if settings.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase letter
        if settings.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check for numbers
        if settings.PASSWORD_REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        # Check for special characters
        if settings.PASSWORD_REQUIRE_SPECIAL and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    async def generate_password_reset_token(self, user_id: int, email: str) -> str:
        """
        Generate password reset token
        """
        try:
            # Generate secure token
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Store token in database (this would be implemented in the user model)
            # For now, return the token
            return token
            
        except Exception as e:
            self.logger.error("Password reset token generation error", error=str(e))
            raise AuthenticationError("Failed to generate reset token")
    
    async def verify_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify password reset token
        """
        try:
            # Hash the token to compare with stored hash
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # This would check the database for the token
            # For now, return None
            return None
            
        except Exception as e:
            self.logger.error("Password reset token verification error", error=str(e))
            return None