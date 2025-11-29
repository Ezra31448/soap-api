from spyne import Fault
from auth_service import decode_token

def check_authentication(ctx):
    """
    Check authentication from SOAP context
    Checks token blacklist and validates JWT
    Raises Fault if authentication fails
    Returns user_id, username, and role if successful
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
    
    # Validate token and extract payload (includes blacklist check)
    try:
        payload = decode_token(token)
        return payload.get('user_id'), payload.get('username'), payload.get('role', 'user')
    except Fault:
        raise
    except Exception as e:
        raise Fault(
            faultcode='Client.Unauthorized',
            faultstring=f'Authentication failed: {str(e)}'
        )

def require_role(ctx, *allowed_roles):
    """
    Check if authenticated user has required role
    
    Args:
        ctx: SOAP context
        *allowed_roles: List of allowed role strings ('admin', 'user', 'viewer')
    
    Raises:
        Fault if user doesn't have required role
    """
    user_id, username, user_role = check_authentication(ctx)
    
    if user_role not in allowed_roles:
        raise Fault(
            faultcode='Client.Forbidden',
            faultstring=f'Access denied. Required role: {", ".join(allowed_roles)}. Your role: {user_role}'
        )
    
    return user_id, username, user_role

