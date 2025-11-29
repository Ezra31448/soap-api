"""
Permission validation middleware for Enhanced User Management System
"""
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Optional
import structlog

from src.database.connection import get_database_session
from src.services.auth_service import AuthService
from src.models.user import User

logger = structlog.get_logger()


async def permission_required(permission: str):
    """
    Decorator to require specific permission for API endpoints
    """
    def decorator(func: Callable):
        async def wrapper(request: Request, *args, **kwargs):
            try:
                # Get token from request
                token = _extract_token_from_request(request)
                if not token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication token required"
                    )
                
                # Validate token
                auth_service = AuthService()
                user_info = await auth_service.validate_token(token)
                if not user_info:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token"
                    )
                
                # Check permission
                async with get_database_session() as session:
                    user = await User.find_by_id(session, user_info.get('user_id'))
                    if not user or not await user.has_permission(session, permission):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Insufficient permissions. Required: {permission}"
                        )
                
                # Add user info to request state for downstream use
                request.state.user = user_info
                request.state.user_id = user_info.get('user_id')
                
                return await func(request, *args, **kwargs)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error("Permission validation failed", error=str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error during permission validation"
                )
        
        return wrapper
    return decorator


async def role_required(role: str):
    """
    Decorator to require specific role for API endpoints
    """
    def decorator(func: Callable):
        async def wrapper(request: Request, *args, **kwargs):
            try:
                # Get token from request
                token = _extract_token_from_request(request)
                if not token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication token required"
                    )
                
                # Validate token
                auth_service = AuthService()
                user_info = await auth_service.validate_token(token)
                if not user_info:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token"
                    )
                
                # Check role
                async with get_database_session() as session:
                    user = await User.find_by_id(session, user_info.get('user_id'))
                    if not user or not await user.has_role(session, role):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Insufficient permissions. Required role: {role}"
                        )
                
                # Add user info to request state for downstream use
                request.state.user = user_info
                request.state.user_id = user_info.get('user_id')
                
                return await func(request, *args, **kwargs)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error("Role validation failed", error=str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error during role validation"
                )
        
        return wrapper
    return decorator


async def authentication_required(func: Callable):
    """
    Decorator to require authentication for API endpoints
    """
    async def wrapper(request: Request, *args, **kwargs):
        try:
            # Get token from request
            token = _extract_token_from_request(request)
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication token required"
                )
            
            # Validate token
            auth_service = AuthService()
            user_info = await auth_service.validate_token(token)
            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            
            # Add user info to request state for downstream use
            request.state.user = user_info
            request.state.user_id = user_info.get('user_id')
            
            return await func(request, *args, **kwargs)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Authentication validation failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during authentication validation"
            )
    
    return wrapper


def _extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extract authentication token from request
    """
    # Try to get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]  # Remove "Bearer " prefix
    
    # Try to get token from query parameter
    token = request.query_params.get("token")
    if token:
        return token
    
    # Try to get token from SOAP header
    soap_header = request.headers.get("SOAPAction")
    if soap_header:
        # Extract token from SOAP action if available
        # This is a fallback method for SOAP clients
        pass
    
    return None


async def permission_middleware(request: Request, call_next: Callable):
    """
    Middleware to add user information to request state if token is present
    """
    try:
        # Get token from request
        token = _extract_token_from_request(request)
        if token:
            # Validate token
            auth_service = AuthService()
            user_info = await auth_service.validate_token(token)
            if user_info:
                # Add user info to request state
                request.state.user = user_info
                request.state.user_id = user_info.get('user_id')
                
                # Get user permissions
                async with get_database_session() as session:
                    user = await User.find_by_id(session, user_info.get('user_id'))
                    if user:
                        permissions = await user.get_permissions(session)
                        request.state.user_permissions = [perm.name for perm in permissions]
                        request.state.user_roles = [role.name for role in await user.get_roles(session)]
        
        # Continue to next middleware
        response = await call_next(request)
        return response
        
    except Exception as e:
        logger.error("Permission middleware error", error=str(e))
        # Continue to next middleware even if there's an error
        response = await call_next(request)
        return response


def setup_permission_middleware(app: FastAPI) -> None:
    """
    Setup permission middleware for FastAPI application
    """
    app.middleware("http")(permission_middleware)