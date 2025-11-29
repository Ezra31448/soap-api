"""
Database connection management for the Enhanced User Management System
"""
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
import structlog

from src.config.settings import settings

logger = structlog.get_logger()

# SQLAlchemy base class
Base = declarative_base()

# Global database engine and session factory
engine: Optional[asyncpg.Pool] = None
async_session_factory: Optional[async_sessionmaker] = None


async def init_database() -> None:
    """
    Initialize database connection pool
    """
    global engine, async_session_factory
    
    try:
        logger.info("Initializing database connection", 
                  host=settings.DB_HOST, 
                  port=settings.DB_PORT,
                  database=settings.DB_NAME)
        
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            echo=settings.APP_DEBUG
        )
        
        # Create session factory
        async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Test connection
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            await session.commit()
        
        logger.info("Database connection initialized successfully")
        
    except Exception as e:
        logger.error("Failed to initialize database connection", error=str(e))
        raise


async def close_database() -> None:
    """
    Close database connection pool
    """
    global engine
    
    try:
        if engine:
            await engine.dispose()
            logger.info("Database connection closed")
    except Exception as e:
        logger.error("Error closing database connection", error=str(e))


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection
    """
    if not async_session_factory:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error("Database session error", error=str(e))
            raise
        finally:
            await session.close()


async def get_database_status() -> Dict[str, Any]:
    """
    Get database connection status
    """
    try:
        if not async_session_factory:
            return {
                "status": "unhealthy",
                "error": "Database not initialized"
            }
        
        async with async_session_factory() as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            
            # Get connection pool info
            pool_status = engine.pool.status() if hasattr(engine, 'pool') else {}
            
            return {
                "status": "healthy",
                "version": version,
                "pool_size": settings.DB_POOL_SIZE,
                "pool_status": pool_status
            }
            
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def execute_query(query: str, params: Optional[Dict] = None) -> Any:
    """
    Execute a raw SQL query
    """
    if not async_session_factory:
        raise RuntimeError("Database not initialized")
    
    async with async_session_factory() as session:
        try:
            result = await session.execute(text(query), params or {})
            await session.commit()
            return result
        except Exception as e:
            await session.rollback()
            logger.error("Query execution failed", query=query, error=str(e))
            raise


async def execute_transaction(queries: list) -> Any:
    """
    Execute multiple queries in a transaction
    """
    if not async_session_factory:
        raise RuntimeError("Database not initialized")
    
    async with async_session_factory() as session:
        try:
            results = []
            for query, params in queries:
                result = await session.execute(text(query), params or {})
                results.append(result)
            
            await session.commit()
            return results
        except Exception as e:
            await session.rollback()
            logger.error("Transaction execution failed", error=str(e))
            raise


# Database dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session
    """
    async for session in get_database_session():
        yield session


# Context manager for database operations
class DatabaseManager:
    """
    Context manager for database operations
    """
    
    def __init__(self):
        self.session: Optional[AsyncSession] = None
        self.transaction = None
    
    async def __aenter__(self) -> AsyncSession:
        if not async_session_factory:
            raise RuntimeError("Database not initialized")
        
        self.session = async_session_factory()
        self.transaction = await self.session.begin()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type:
                await self.transaction.rollback()
                logger.error("Transaction rolled back", error=str(exc_val))
            else:
                await self.transaction.commit()
            
            await self.session.close()


# Utility functions for common database operations
async def check_table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database
    """
    query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = :table_name
        )
    """
    result = await execute_query(query, {"table_name": table_name})
    return result.scalar()


async def get_table_count(table_name: str) -> int:
    """
    Get the number of rows in a table
    """
    query = f"SELECT COUNT(*) FROM {table_name}"
    result = await execute_query(query)
    return result.scalar()


async def get_database_info() -> Dict[str, Any]:
    """
    Get general database information
    """
    queries = [
        ("SELECT version()", {}),
        ("SELECT current_database()", {}),
        ("SELECT current_user()", {}),
        ("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'", {})
    ]
    
    results = await execute_transaction(queries)
    
    return {
        "version": results[0].scalar(),
        "database": results[1].scalar(),
        "user": results[2].scalar(),
        "table_count": results[3].scalar()
    }