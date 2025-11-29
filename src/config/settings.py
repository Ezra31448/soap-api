"""
Application configuration settings for the Enhanced User Management System
"""
from functools import lru_cache
from typing import Optional, List
from pydantic import field_validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application Configuration
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_NAME: str = "Enhanced User Management System"
    APP_VERSION: str = "1.0.0"
    
    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "user_management_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 10
    
    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL from components"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Security Configuration
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 7
    
    # Password Configuration
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # Email Configuration
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    EMAIL_FROM: str = "noreply@example.com"
    EMAIL_FROM_NAME: str = "User Management System"
    
    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES: List[str] = ["jpg", "jpeg", "png", "gif"]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = None
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    
    # API Configuration
    API_PREFIX: str = "/api"
    SOAP_ENDPOINT: str = "/soap"
    WSDL_ENDPOINT: str = "/wsdl"
    
    # Health Check Configuration
    HEALTH_CHECK_ENABLED: bool = True
    HEALTH_CHECK_ENDPOINT: str = "/health"
    
    # Documentation Configuration
    DOCS_ENABLED: bool = True
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # Testing Configuration
    TESTING: bool = False
    TEST_DATABASE_URL: Optional[str] = None
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @field_validator("CORS_ALLOW_METHODS", mode="before")
    @classmethod
    def assemble_cors_methods(cls, v):
        """Parse CORS methods from string or list"""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @field_validator("CORS_ALLOW_HEADERS", mode="before")
    @classmethod
    def assemble_cors_headers(cls, v):
        """Parse CORS headers from string or list"""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @field_validator("ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def assemble_file_types(cls, v):
        """Parse allowed file types from string or list"""
        if isinstance(v, str):
            return [i.strip().lower() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()