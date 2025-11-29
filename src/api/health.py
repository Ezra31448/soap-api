"""
Health check endpoints for the Enhanced User Management System
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import asyncio

from src.database.connection import get_database_status
from src.database.redis import get_redis_status
from src.config.settings import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> JSONResponse:
    """
    Comprehensive health check endpoint
    Returns the overall health status of the application and its dependencies
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "checks": {}
    }
    
    # Check database connection
    try:
        db_status = await get_database_status()
        health_status["checks"]["database"] = db_status
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check Redis connection
    try:
        redis_status = await get_redis_status()
        health_status["checks"]["redis"] = redis_status
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Determine HTTP status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return JSONResponse(
        status_code=status_code,
        content=health_status
    )


@router.get("/health/ready")
async def readiness_check() -> JSONResponse:
    """
    Readiness probe endpoint
    Checks if the application is ready to serve traffic
    """
    # Check critical dependencies
    try:
        # Database must be ready
        db_status = await get_database_status()
        if db_status["status"] != "healthy":
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not ready",
                    "reason": "database not ready"
                }
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "ready",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not ready",
                "reason": str(e)
            }
        )


@router.get("/health/live")
async def liveness_check() -> JSONResponse:
    """
    Liveness probe endpoint
    Checks if the application is still running
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@router.get("/health/detailed")
async def detailed_health_check() -> JSONResponse:
    """
    Detailed health check with system information
    """
    import psutil
    import platform
    
    # Get system information
    system_info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "disk_usage": psutil.disk_usage('/').percent
    }
    
    # Get application status
    health_status = await health_check()
    health_data = health_status.body.decode() if hasattr(health_status.body, 'decode') else health_status.body
    
    # Import json to parse health_data if it's a string
    import json
    if isinstance(health_data, str):
        health_data = json.loads(health_data)
    
    # Combine system info with health status
    detailed_status = {
        **health_data,
        "system": system_info
    }
    
    return JSONResponse(
        status_code=health_status.status_code,
        content=detailed_status
    )