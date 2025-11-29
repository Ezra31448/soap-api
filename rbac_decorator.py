from functools import wraps
from spyne import Fault
from auth_service import decode_token
from models import UserRole

def require_roles(*allowed_roles):
    """
    Decorator to enforce role-based access control on SOAP endpoints
    
    Args:
        *allowed_roles: Variable number of UserRole enum values or strings
    
    Usage:
        @require_roles(UserRole.ADMIN)
        @rpc(...)
        def admin_only_method(ctx):
            pass
            
        @require_roles(UserRole.ADMIN, UserRole.USER)
        @rpc(...)
        def user_and_admin_method(ctx):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(ctx, *args, **kwargs):
            # Get user role from context
            user_role = get_user_role(ctx)
            
            # Convert allowed_roles to strings for comparison
            allowed_role_strings = []
            for role in allowed_roles:
                if isinstance(role, UserRole):
                    allowed_role_strings.append(role.value)
                else:
                    allowed_role_strings.append(str(role))
            
            # Check if user's role is in allowed roles
            if user_role not in allowed_role_strings:
                raise Fault(
                    faultcode='Client.Forbidden',
                    faultstring=f'Access denied. Required role: {", ".join(allowed_role_strings)}'
                )
            
            return func(ctx, *args, **kwargs)
        return wrapper
    return decorator

def get_user_role(ctx) -> str:
    """
    Extract user role from context (requires authentication)
    
    Args:
        ctx: SOAP context
        
    Returns:
        User role as string
    """
    # Try to get token from HTTP headers
    token = None
    
    # Check transport headers
    if hasattr(ctx, 'transport') and hasattr(ctx.transport, 'req_env'):
        auth_header = ctx.transport.req_env.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
    
    if not token:
        raise Fault(
            faultcode='Client.Unauthorized',
            faultstring='Authentication required. Please provide a valid JWT token in the Authorization header.'
        )
    
    # Validate token and extract role
    try:
        payload = decode_token(token)
        return payload.get('role', 'user')
    except Fault:
        raise
    except Exception as e:
        raise Fault(
            faultcode='Client.Unauthorized',
            faultstring=f'Authentication failed: {str(e)}'
        )

def check_role(required_role: str, user_role: str) -> bool:
    """
    Check if user's role meets the minimum requirement
    Implements role hierarchy: admin > user > viewer
    
    Args:
        required_role: Minimum required role
        user_role: User's actual role
        
    Returns:
        True if user has sufficient permissions
    """
    role_hierarchy = {
        'admin': 3,
        'user': 2,
        'viewer': 1
    }
    
    required_level = role_hierarchy.get(required_role.lower(), 0)
    user_level = role_hierarchy.get(user_role.lower(), 0)
    
    return user_level >= required_level
