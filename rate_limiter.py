from models import Session, LoginAttempt, User
from datetime import datetime, timedelta
from spyne import Fault
import os

# Configuration from environment
MAX_ATTEMPTS = int(os.getenv('RATE_LIMIT_MAX_ATTEMPTS', '5'))
WINDOW_MINUTES = int(os.getenv('RATE_LIMIT_WINDOW_MINUTES', '15'))

def check_rate_limit(username: str) -> None:
    """
    Check if user has exceeded login attempt rate limit
    Raises Fault if rate limit exceeded
    
    Args:
        username: Username to check
    """
    session = Session()
    try:
        # Calculate time window
        window_start = datetime.utcnow() - timedelta(minutes=WINDOW_MINUTES)
        
        # Count failed attempts in window
        failed_attempts = session.query(LoginAttempt).filter(
            LoginAttempt.username == username,
            LoginAttempt.success == False,
            LoginAttempt.attempted_at >= window_start
        ).count()
        
        if failed_attempts >= MAX_ATTEMPTS:
            raise Fault(
                faultcode='Client.RateLimitExceeded',
                faultstring=f'Too many failed login attempts. Please try again in {WINDOW_MINUTES} minutes.'
            )
        
        # Clean up old attempts (older than 24 hours)
        cleanup_old_attempts(session)
        
    finally:
        session.close()

def record_login_attempt(username: str, success: bool, user_id: int = None, ip_address: str = None) -> None:
    """
    Record a login attempt
    
    Args:
        username: Username that attempted login
        success: Whether login was successful
        user_id: User ID if login was successful
        ip_address: IP address of the attempt
    """
    session = Session()
    try:
        attempt = LoginAttempt(
            username=username,
            user_id=user_id,
            success=success,
            ip_address=ip_address,
            attempted_at=datetime.utcnow()
        )
        session.add(attempt)
        session.commit()
    except Exception as e:
        session.rollback()
        # Log error but don't fail login flow
        print(f"Failed to record login attempt: {e}")
    finally:
        session.close()

def cleanup_old_attempts(session) -> None:
    """
    Remove login attempts older than 24 hours
    
    Args:
        session: Database session
    """
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        session.query(LoginAttempt).filter(
            LoginAttempt.attempted_at < cutoff_time
        ).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Failed to cleanup old login attempts: {e}")

def reset_rate_limit(username: str) -> None:
    """
    Reset rate limit for a user (e.g., after successful login)
    
    Args:
        username: Username to reset
    """
    session = Session()
    try:
        # Delete failed attempts for this user
        session.query(LoginAttempt).filter(
            LoginAttempt.username == username,
            LoginAttempt.success == False
        ).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Failed to reset rate limit: {e}")
    finally:
        session.close()
