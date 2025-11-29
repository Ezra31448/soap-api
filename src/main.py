"""
Main application entry point for the Enhanced User Management System SOAP API
"""
import asyncio
import logging
import logging.config
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn

from src.config.settings import settings
from src.api.soap_v2 import create_soap_app
from src.api.health import router as health_router
from src.utils.logging import setup_logging
from src.utils.exceptions import setup_exception_handlers
from src.database.connection import init_database, close_database
from src.database.redis import init_redis, close_redis
from src.middleware.permission_middleware import setup_permission_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger = structlog.get_logger()
    logger.info("Starting Enhanced User Management System")
    
    # Initialize database connections
    await init_database()
    await init_redis()
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Enhanced User Management System")
    
    # Close database connections
    await close_database()
    await close_redis()
    
    logger.info("Application shutdown completed")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Setup logging
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Enhanced User Management System with SOAP API support",
        docs_url=settings.DOCS_URL if settings.DOCS_ENABLED else None,
        redoc_url=settings.REDOC_URL if settings.DOCS_ENABLED else None,
        lifespan=lifespan
    )
    
    # Setup middleware
    setup_middleware(app)
    setup_permission_middleware(app)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Include routers
    app.include_router(health_router, tags=["Health"])
    
    # Setup SOAP endpoint
    soap_app = create_soap_app()
    app.mount(settings.SOAP_ENDPOINT, soap_app)
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """Setup application middleware"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # Trusted host middleware
    if settings.APP_ENV == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure based on your deployment
        )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log HTTP requests"""
        logger = structlog.get_logger()
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code
        )
        
        return response


def main() -> None:
    """Main entry point"""
    
    # Create application
    app = create_application()
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        use_colors=True
    )


if __name__ == "__main__":
    main()