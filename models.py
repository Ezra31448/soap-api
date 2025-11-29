from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timedelta
import os
import time
import bcrypt
import uuid
import enum

Base = declarative_base()

# Role Enum
class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    email = Column(String, unique=True)
    phone_number = Column(String)
    status = Column(String) # ACTIVE, INACTIVE

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    login_attempts = relationship("LoginAttempt", back_populates="user", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="refresh_tokens")

class LoginAttempt(Base):
    __tablename__ = 'login_attempts'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    success = Column(Boolean, default=False)
    ip_address = Column(String, nullable=True)
    attempted_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="login_attempts")

class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'
    id = Column(Integer, primary_key=True)
    jti = Column(String, unique=True, nullable=False, index=True)  # JWT ID
    token = Column(String, nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # When token naturally expires

# Password utility functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_token() -> str:
    """Generate a unique token string"""
    return str(uuid.uuid4())

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Cleanup functions
def cleanup_expired_tokens(session):
    """Remove expired tokens from database"""
    now = datetime.utcnow()
    
    # Remove expired refresh tokens
    session.query(RefreshToken).filter(RefreshToken.expires_at < now).delete()
    
    # Remove expired password reset tokens
    session.query(PasswordResetToken).filter(PasswordResetToken.expires_at < now).delete()
    
    # Remove expired blacklisted tokens
    session.query(TokenBlacklist).filter(TokenBlacklist.expires_at < now).delete()
    
    # Remove old login attempts (older than 24 hours)
    session.query(LoginAttempt).filter(
        LoginAttempt.attempted_at < now - timedelta(hours=24)
    ).delete()
    
    session.commit()

# Database connection
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
DB_NAME = os.getenv('POSTGRES_DB', 'soapdb')
DB_HOST = os.getenv('DB_HOST', 'db')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(engine)
            print("Database initialized successfully.")
            return
        except Exception as e:
            print(f"Database connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)
            retries -= 1
    print("Could not initialize database.")
