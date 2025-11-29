"""
Redis connection management for the Enhanced User Management System
"""
import json
import pickle
from typing import Any, Optional, Dict, List
import redis.asyncio as redis
import structlog

from src.config.settings import settings

logger = structlog.get_logger()

# Global Redis client
redis_client: Optional[redis.Redis] = None


async def init_redis() -> None:
    """
    Initialize Redis connection
    """
    global redis_client
    
    try:
        logger.info("Initializing Redis connection", 
                  host=settings.REDIS_HOST, 
                  port=settings.REDIS_PORT)
        
        # Create Redis client
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=False  # We'll handle encoding/decoding manually
        )
        
        # Test connection
        await redis_client.ping()
        
        logger.info("Redis connection initialized successfully")
        
    except Exception as e:
        logger.error("Failed to initialize Redis connection", error=str(e))
        raise


async def close_redis() -> None:
    """
    Close Redis connection
    """
    global redis_client
    
    try:
        if redis_client:
            await redis_client.close()
            logger.info("Redis connection closed")
    except Exception as e:
        logger.error("Error closing Redis connection", error=str(e))


async def get_redis_status() -> Dict[str, Any]:
    """
    Get Redis connection status
    """
    try:
        if not redis_client:
            return {
                "status": "unhealthy",
                "error": "Redis not initialized"
            }
        
        # Test connection
        await redis_client.ping()
        
        # Get Redis info
        info = await redis_client.info()
        
        return {
            "status": "healthy",
            "version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
            "used_memory": info.get("used_memory_human"),
            "uptime": info.get("uptime_in_seconds")
        }
        
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Redis operations
async def set_key(key: str, value: Any, expire: Optional[int] = None) -> bool:
    """
    Set a key-value pair in Redis
    """
    try:
        if not redis_client:
            raise RuntimeError("Redis not initialized")
        
        # Serialize value
        serialized_value = pickle.dumps(value)
        
        # Set key with optional expiration
        if expire:
            await redis_client.setex(key, expire, serialized_value)
        else:
            await redis_client.set(key, serialized_value)
        
        return True
        
    except Exception as e:
        logger.error("Failed to set Redis key", key=key, error=str(e))
        return False


async def get_key(key: str) -> Any:
    """
    Get a value from Redis by key
    """
    try:
        if not redis_client:
            raise RuntimeError("Redis not initialized")
        
        # Get value
        value = await redis_client.get(key)
        
        if value is None:
            return None
        
        # Deserialize value
        return pickle.loads(value)
        
    except Exception as e:
        logger.error("Failed to get Redis key", key=key, error=str(e))
        return None


async def delete_key(key: str) -> bool:
    """
    Delete a key from Redis
    """
    try:
        if not redis_client:
            raise RuntimeError("Redis not initialized")
        
        result = await redis_client.delete(key)
        return result > 0
        
    except Exception as e:
        logger.error("Failed to delete Redis key", key=key, error=str(e))
        return False


async def key_exists(key: str) -> bool:
    """
    Check if a key exists in Redis
    """
    try:
        if not redis_client:
            raise RuntimeError("Redis not initialized")
        
        result = await redis_client.exists(key)
        return result > 0
        
    except Exception as e:
        logger.error("Failed to check Redis key existence", key=key, error=str(e))
        return False


async def set_json(key: str, value: Dict[str, Any], expire: Optional[int] = None) -> bool:
    """
    Set a JSON value in Redis
    """
    try:
        if not redis_client:
            raise RuntimeError("Redis not initialized")
        
        # Serialize JSON
        serialized_value = json.dumps(value)
        
        # Set key with optional expiration
        if expire:
            await redis_client.setex(key, expire, serialized_value)
        else:
            await redis_client.set(key, serialized_value)
        
        return True
        
    except Exception as e:
        logger.error("Failed to set JSON in Redis", key=key, error=str(e))
        return False


async def get_json(key: str) -> Optional[Dict[str, Any]]:
    """
    Get a JSON value from Redis
    """
    try:
        if not redis_client:
            raise RuntimeError("Redis not initialized")
        
        # Get value
        value = await redis_client.get(key)
        
        if value is None:
            return None
        
        # Deserialize JSON
        return json.loads(value)
        
    except Exception as e:
        logger.error("Failed to get JSON from Redis", key=key, error=str(e))
        return None


# Session management
async def create_session(user_id: int, session_data: Dict[str, Any], expire_hours: int = 24) -> str:
    """
    Create a user session in Redis
    """
    try:
        import uuid
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"
        
        # Add user_id to session data
        session_data["user_id"] = user_id
        session_data["session_id"] = session_id
        
        # Store session with expiration
        await set_json(session_key, session_data, expire_hours * 3600)
        
        # Add session to user's active sessions
        user_sessions_key = f"user_sessions:{user_id}"
        await redis_client.sadd(user_sessions_key, session_id)
        await redis_client.expire(user_sessions_key, expire_hours * 3600)
        
        return session_id
        
    except Exception as e:
        logger.error("Failed to create session", user_id=user_id, error=str(e))
        raise


async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get session data from Redis
    """
    try:
        session_key = f"session:{session_id}"
        return await get_json(session_key)
        
    except Exception as e:
        logger.error("Failed to get session", session_id=session_id, error=str(e))
        return None


async def delete_session(session_id: str) -> bool:
    """
    Delete a session from Redis
    """
    try:
        # Get session data to find user_id
        session_data = await get_session(session_id)
        if not session_data:
            return False
        
        user_id = session_data.get("user_id")
        
        # Delete session
        session_key = f"session:{session_id}"
        await delete_key(session_key)
        
        # Remove from user's active sessions
        if user_id:
            user_sessions_key = f"user_sessions:{user_id}"
            await redis_client.srem(user_sessions_key, session_id)
        
        return True
        
    except Exception as e:
        logger.error("Failed to delete session", session_id=session_id, error=str(e))
        return False


async def get_user_sessions(user_id: int) -> List[str]:
    """
    Get all active sessions for a user
    """
    try:
        user_sessions_key = f"user_sessions:{user_id}"
        sessions = await redis_client.smembers(user_sessions_key)
        return [session.decode() if isinstance(session, bytes) else session for session in sessions]
        
    except Exception as e:
        logger.error("Failed to get user sessions", user_id=user_id, error=str(e))
        return []


async def delete_all_user_sessions(user_id: int) -> int:
    """
    Delete all sessions for a user
    """
    try:
        sessions = await get_user_sessions(user_id)
        deleted_count = 0
        
        for session_id in sessions:
            if await delete_session(session_id):
                deleted_count += 1
        
        return deleted_count
        
    except Exception as e:
        logger.error("Failed to delete all user sessions", user_id=user_id, error=str(e))
        return 0


# Cache management
async def cache_get(cache_key: str) -> Optional[Any]:
    """
    Get value from cache
    """
    return await get_key(cache_key)


async def cache_set(cache_key: str, value: Any, expire: Optional[int] = None) -> bool:
    """
    Set value in cache
    """
    return await set_key(cache_key, value, expire)


async def cache_delete(cache_key: str) -> bool:
    """
    Delete value from cache
    """
    return await delete_key(cache_key)


async def cache_clear_pattern(pattern: str) -> int:
    """
    Clear cache keys matching a pattern
    """
    try:
        if not redis_client:
            raise RuntimeError("Redis not initialized")
        
        # Find keys matching pattern
        keys = await redis_client.keys(pattern)
        
        if not keys:
            return 0
        
        # Delete keys
        deleted_count = await redis_client.delete(*keys)
        return deleted_count
        
    except Exception as e:
        logger.error("Failed to clear cache pattern", pattern=pattern, error=str(e))
        return 0


# Rate limiting
async def rate_limit_check(key: str, limit: int, window_seconds: int) -> bool:
    """
    Check if rate limit is exceeded
    """
    try:
        if not redis_client:
            return True  # Allow if Redis is not available
        
        current_count = await redis_client.incr(key)
        
        if current_count == 1:
            # Set expiration for the key
            await redis_client.expire(key, window_seconds)
        
        return current_count <= limit
        
    except Exception as e:
        logger.error("Rate limit check failed", key=key, error=str(e))
        return True  # Allow if there's an error