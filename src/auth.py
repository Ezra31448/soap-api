"""
Authentication module for SOAP API
"""
import os
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from model import Base

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship with wallet
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}')>"

class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String(500), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TokenBlacklist(id='{self.id}', token='{token[:20]}...')>"

# Add relationship to Wallet model
from model import Wallet
Wallet.user_id = Column(String(36), ForeignKey('users.id'), nullable=True)
Wallet.user = relationship("User", back_populates="wallet")

class AuthService:
    def __init__(self, db_session):
        self.db = db_session
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_user(self, username: str, email: str, password: str):
        """Create a new user with hashed password"""
        try:
            # Check if username or email already exists
            existing_user = self.db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return None, "Username or email already exists"
            
            # Create new user
            password_hash = self.hash_password(password)
            user = User(
                username=username,
                email=email,
                password_hash=password_hash
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            return user, None
            
        except SQLAlchemyError as e:
            self.db.rollback()
            return None, f"Database error: {str(e)}"
    
    def authenticate_user(self, username: str, password: str):
        """Authenticate user and return user object if valid"""
        try:
            user = self.db.query(User).filter(User.username == username).first()
            if not user:
                return None, "User not found"
            
            if not user.is_active:
                return None, "User account is disabled"
            
            if not self.verify_password(password, user.password_hash):
                return None, "Invalid password"
            
            return user, None
            
        except SQLAlchemyError as e:
            return None, f"Database error: {str(e)}"
    
    def generate_token(self, user: User) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    
    def verify_token(self, token: str):
        """Verify JWT token and return user if valid"""
        try:
            # Check if token is blacklisted
            blacklisted = self.db.query(TokenBlacklist).filter(
                TokenBlacklist.token == token
            ).first()
            
            if blacklisted:
                return None, "Token has been revoked"
            
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get('user_id')
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return None, "Invalid token or user not found"
            
            return user, None
            
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
        except SQLAlchemyError as e:
            return None, f"Database error: {str(e)}"
    
    def revoke_token(self, token: str):
        """Add token to blacklist"""
        try:
            # Decode token to get expiration
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
            expires_at = datetime.fromtimestamp(payload['exp'])
            
            blacklisted_token = TokenBlacklist(
                token=token,
                expires_at=expires_at
            )
            
            self.db.add(blacklisted_token)
            self.db.commit()
            return True, None
            
        except jwt.InvalidTokenError:
            return False, "Invalid token"
        except SQLAlchemyError as e:
            self.db.rollback()
            return False, f"Database error: {str(e)}"
