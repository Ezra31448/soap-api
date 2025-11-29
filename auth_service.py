from spyne import ServiceBase, rpc, Unicode, Boolean, Fault
from models import (
    Session, User, UserRole, RefreshToken, PasswordResetToken, TokenBlacklist,
    hash_password, verify_password, generate_token, validate_email
)
from rate_limiter import check_rate_limit, record_login_attempt, reset_rate_limit
import jwt
import os
from datetime import datetime, timedelta
import hashlib

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '15'))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '7'))

class AuthService(ServiceBase):
    """Enhanced authentication service with refresh tokens, password reset, and logout"""
    
    @rpc(Unicode, Unicode, Unicode, Unicode, _returns=Unicode)
    def register(ctx, username, password, email, role='user'):
        """
        Register a new user with role-based access
        Args:
            username: Unique username (min 3 chars)
            password: User password (min 6 chars, will be hashed)
            email: User email address
            role: User role (admin, user, viewer) - defaults to 'user'
        Returns:
            Success message
        """
        session = Session()
        try:
            # Validate input
            if not username or len(username) < 3:
                raise Fault(faultcode='Client', faultstring='Username must be at least 3 characters')
            if not password or len(password) < 6:
                raise Fault(faultcode='Client', faultstring='Password must be at least 6 characters')
            if not email or not validate_email(email):
                raise Fault(faultcode='Client', faultstring='Valid email address is required')
            
            # Check if username already exists
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                raise Fault(faultcode='Client', faultstring='Username already exists')
            
            # Check if email already exists
            existing_email = session.query(User).filter_by(email=email).first()
            if existing_email:
                raise Fault(faultcode='Client', faultstring='Email already registered')
            
            # Validate and set role
            try:
                user_role = UserRole[role.upper()]
            except KeyError:
                raise Fault(faultcode='Client', faultstring=f'Invalid role. Must be one of: admin, user, viewer')
            
            # Create new user with hashed password
            password_hash = hash_password(password)
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                role=user_role
            )
            session.add(new_user)
            session.commit()
            
            return f"SUCCESS: User '{username}' registered successfully with role '{user_role.value}'"
        except Fault:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise Fault(faultcode='Server', faultstring=f'Registration failed: {str(e)}')
        finally:
            session.close()
    
    @rpc(Unicode, Unicode, _returns=Unicode)
    def login(ctx, username, password):
        """
        Authenticate user and return access + refresh tokens
        Implements rate limiting to prevent brute force attacks
        
        Args:
            username: Username
            password: Password
        Returns:
            JSON string with access_token and refresh_token
        """
        session = Session()
        try:
            # Check rate limit BEFORE attempting authentication
            check_rate_limit(username)
            
            # Find user
            user = session.query(User).filter_by(username=username).first()
            if not user:
                # Record failed attempt
                record_login_attempt(username, success=False)
                raise Fault(faultcode='Client', faultstring='Invalid username or password')
            
            # Verify password
            if not verify_password(password, user.password_hash):
                # Record failed attempt
                record_login_attempt(username, success=False, user_id=user.id)
                raise Fault(faultcode='Client', faultstring='Invalid username or password')
            
            # Generate access token (short-lived)
            access_payload = {
                'user_id': user.id,
                'username': user.username,
                'role': user.role.value,
                'type': 'access',
                'exp': datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
                'iat': datetime.utcnow()
            }
            access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            # Generate refresh token (long-lived)
            refresh_token_string = generate_token()
            refresh_token_expires = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
            
            # Store refresh token in database
            refresh_token_db = RefreshToken(
                token=refresh_token_string,
                user_id=user.id,
                expires_at=refresh_token_expires
            )
            session.add(refresh_token_db)
            session.commit()
            
            # Record successful login and reset rate limit
            record_login_attempt(username, success=True, user_id=user.id)
            reset_rate_limit(username)
            
            # Return both tokens in a formatted string (JSON-like)
            return f'{{"access_token": "{access_token}", "refresh_token": "{refresh_token_string}", "expires_in": {JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60}}}'
            
        except Fault:
            raise
        except Exception as e:
            raise Fault(faultcode='Server', faultstring=f'Login failed: {str(e)}')
        finally:
            session.close()
    
    @rpc(Unicode, _returns=Unicode)
    def refresh_token(ctx, refresh_token):
        """
        Exchange refresh token for a new access token
        Implements token rotation for security
        
        Args:
            refresh_token: Valid refresh token string
        Returns:
            JSON string with new access_token and refresh_token
        """
        session = Session()
        try:
            # Find refresh token in database
            token_db = session.query(RefreshToken).filter_by(token=refresh_token).first()
            
            if not token_db:
                raise Fault(faultcode='Client', faultstring='Invalid refresh token')
            
            # Check if token is revoked
            if token_db.revoked:
                raise Fault(faultcode='Client', faultstring='Refresh token has been revoked')
            
            # Check if token is expired
            if token_db.expires_at < datetime.utcnow():
                raise Fault(faultcode='Client', faultstring='Refresh token has expired')
            
            # Get user
            user = session.query(User).filter_by(id=token_db.user_id).first()
            if not user:
                raise Fault(faultcode='Server', faultstring='User not found')
            
            # Generate new access token
            access_payload = {
                'user_id': user.id,
                'username': user.username,
                'role': user.role.value,
                'type': 'access',
                'exp': datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
                'iat': datetime.utcnow()
            }
            new_access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            # Token rotation: revoke old refresh token and issue new one
            token_db.revoked = True
            
            new_refresh_token_string = generate_token()
            new_refresh_token_expires = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
            
            new_refresh_token_db = RefreshToken(
                token=new_refresh_token_string,
                user_id=user.id,
                expires_at=new_refresh_token_expires
            )
            session.add(new_refresh_token_db)
            session.commit()
            
            return f'{{"access_token": "{new_access_token}", "refresh_token": "{new_refresh_token_string}", "expires_in": {JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60}}}'
            
        except Fault:
            raise
        except Exception as e:
            raise Fault(faultcode='Server', faultstring=f'Token refresh failed: {str(e)}')
        finally:
            session.close()
    
    @rpc(Unicode, _returns=Unicode)
    def logout(ctx, access_token):
        """
        Logout user by blacklisting their access token
        
        Args:
            access_token: Current access token to blacklist
        Returns:
            Success message
        """
        session = Session()
        try:
            # Decode token to get expiration
            try:
                payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                # Token already expired, no need to blacklist
                return "SUCCESS: Logged out"
            except jwt.InvalidTokenError as e:
                raise Fault(faultcode='Client', faultstring=f'Invalid token: {str(e)}')
            
            # Generate JTI (JWT ID) from token hash
            jti = hashlib.sha256(access_token.encode()).hexdigest()
            
            # Check if already blacklisted
            existing = session.query(TokenBlacklist).filter_by(jti=jti).first()
            if existing:
                return "SUCCESS: Already logged out"
            
            # Add to blacklist
            blacklist_entry = TokenBlacklist(
                jti=jti,
                token=access_token,
                expires_at=datetime.fromtimestamp(payload['exp'])
            )
            session.add(blacklist_entry)
            
            # Also revoke all refresh tokens for this user
            session.query(RefreshToken).filter_by(
                user_id=payload['user_id'],
                revoked=False
            ).update({'revoked': True})
            
            session.commit()
            
            return "SUCCESS: Logged out successfully"
            
        except Fault:
            raise
        except Exception as e:
            session.rollback()
            raise Fault(faultcode='Server', faultstring=f'Logout failed: {str(e)}')
        finally:
            session.close()
    
    @rpc(Unicode, _returns=Unicode)
    def request_password_reset(ctx, email):
        """
        Request password reset token for email
        
        Args:
            email: User's email address
        Returns:
            Success message (token logged to console in dev)
        """
        session = Session()
        try:
            # Find user by email
            user = session.query(User).filter_by(email=email).first()
            
            # Always return success to prevent email enumeration
            if not user:
                return "SUCCESS: If email exists, password reset instructions have been sent"
            
            # Generate reset token
            reset_token = generate_token()
            reset_expires = datetime.utcnow() + timedelta(hours=1)
            
            # Store reset token
            password_reset = PasswordResetToken(
                token=reset_token,
                user_id=user.id,
                expires_at=reset_expires
            )
            session.add(password_reset)
            session.commit()
            
            # In production, send email here
            # For now, log to console
            print("="*60)
            print("PASSWORD RESET REQUESTED")
            print(f"User: {user.username} ({email})")
            print(f"Reset Token: {reset_token}")
            print(f"Expires: {reset_expires}")
            print(f"Use this token with the reset_password method")
            print("="*60)
            
            return "SUCCESS: If email exists, password reset instructions have been sent"
            
        except Exception as e:
            session.rollback()
            raise Fault(faultcode='Server', faultstring=f'Password reset request failed: {str(e)}')
        finally:
            session.close()
    
    @rpc(Unicode, Unicode, _returns=Unicode)
    def reset_password(ctx, reset_token, new_password):
        """
        Reset password using reset token
        
        Args:
            reset_token: Password reset token from request_password_reset
            new_password: New password (min 6 chars)
        Returns:
            Success message
        """
        session = Session()
        try:
            # Validate new password
            if not new_password or len(new_password) < 6:
                raise Fault(faultcode='Client', faultstring='Password must be at least 6 characters')
            
            # Find reset token
            token_db = session.query(PasswordResetToken).filter_by(token=reset_token).first()
            
            if not token_db:
                raise Fault(faultcode='Client', faultstring='Invalid reset token')
            
            # Check if already used
            if token_db.used:
                raise Fault(faultcode='Client', faultstring='Reset token has already been used')
            
            # Check if expired
            if token_db.expires_at < datetime.utcnow():
                raise Fault(faultcode='Client', faultstring='Reset token has expired')
            
            # Get user and update password
            user = session.query(User).filter_by(id=token_db.user_id).first()
            if not user:
                raise Fault(faultcode='Server', faultstring='User not found')
            
            user.password_hash = hash_password(new_password)
            token_db.used = True
            
            # Revoke all refresh tokens for security
            session.query(RefreshToken).filter_by(
                user_id=user.id,
                revoked=False
            ).update({'revoked': True})
            
            session.commit()
            
            return f"SUCCESS: Password reset successfully for user '{user.username}'"
            
        except Fault:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise Fault(faultcode='Server', faultstring=f'Password reset failed: {str(e)}')
        finally:
            session.close()
    
    @rpc(Unicode, _returns=Unicode)
    def verify_token(ctx, token):
        """
        Verify a JWT token and return user info
        Args:
            token: JWT token string
        Returns:
            User information as string
        """
        session = Session()
        try:
            # Check if token is blacklisted
            jti = hashlib.sha256(token.encode()).hexdigest()
            blacklisted = session.query(TokenBlacklist).filter_by(jti=jti).first()
            if blacklisted:
                raise Fault(faultcode='Client', faultstring='Token has been revoked')
            
            # Decode and verify token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Return user info
            return f"Valid token for user: {payload['username']} (ID: {payload['user_id']}, Role: {payload.get('role', 'user')})"
        except jwt.ExpiredSignatureError:
            raise Fault(faultcode='Client', faultstring='Token has expired')
        except jwt.InvalidTokenError:
            raise Fault(faultcode='Client', faultstring='Invalid token')
        except Fault:
            raise
        except Exception as e:
            raise Fault(faultcode='Server', faultstring=f'Token verification failed: {str(e)}')
        finally:
            session.close()

def decode_token(token: str) -> dict:
    """
    Utility function to decode and validate JWT token
    Checks blacklist and returns payload dict or raises exception
    """
    session = Session()
    try:
        # Check if token is blacklisted
        jti = hashlib.sha256(token.encode()).hexdigest()
        blacklisted = session.query(TokenBlacklist).filter_by(jti=jti).first()
        if blacklisted:
            raise Fault(faultcode='Client', faultstring='Token has been revoked')
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Fault(faultcode='Client', faultstring='Token has expired')
    except jwt.InvalidTokenError:
        raise Fault(faultcode='Client', faultstring='Invalid token')
    finally:
        session.close()

