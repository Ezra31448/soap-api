"""
Logging configuration for the Enhanced User Management System
"""
import logging
import logging.config
import sys
import time
from typing import Dict, Any
import structlog
from pythonjsonlogger import jsonlogger

from src.config.settings import settings


def setup_logging() -> None:
    """
    Configure structured logging for the application
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" 
            else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    log_config = get_logging_config()
    logging.config.dictConfig(log_config)
    
    # Set log level for specific modules
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.APP_DEBUG else logging.WARNING
    )


def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration dictionary
    """
    log_level = settings.LOG_LEVEL.upper()
    
    # JSON formatter for production
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    # Console formatter for development
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            },
            "console": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "console",
                "stream": sys.stdout
            }
        },
        "loggers": {
            "": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy": {
                "level": "INFO" if settings.APP_DEBUG else "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "INFO" if settings.APP_DEBUG else "WARNING",
                "handlers": ["console"],
                "propagate": False
            }
        }
    }
    
    # Add file handler if log file is specified
    if settings.LOG_FILE:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "json",
            "filename": settings.LOG_FILE,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
        
        # Add file handler to all loggers
        for logger_config in config["loggers"].values():
            if "handlers" in logger_config:
                logger_config["handlers"].append("file")
    
    return config


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a structured logger instance
    """
    return structlog.get_logger(name)


# Request logging middleware
class RequestLoggingMiddleware:
    """
    Middleware for logging HTTP requests and responses
    """
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger("request")
    
    async def __call__(self, scope, receive, send):
        """
        ASGI application wrapper for request logging
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Get request details
        method = scope["method"]
        path = scope["path"]
        query_string = scope.get("query_string", b"").decode()
        client = scope.get("client", ("unknown", 0))
        user_agent = ""
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        if b"user-agent" in headers:
            user_agent = headers[b"user-agent"].decode()
        
        # Log request
        request_id = self._generate_request_id()
        self.logger.info(
            "Request started",
            request_id=request_id,
            method=method,
            path=path,
            query_string=query_string,
            client_ip=client[0],
            user_agent=user_agent
        )
        
        # Wrap send to capture response
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time
                
                # Log response
                self.logger.info(
                    "Request completed",
                    request_id=request_id,
                    method=method,
                    path=path,
                    status_code=status_code,
                    duration_ms=round(duration * 1000, 2)
                )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID"""
        import uuid
        return str(uuid.uuid4())[:8]


# Audit logging
def log_audit_event(
    user_id: int = None,
    action: str = "",
    resource_type: str = "",
    resource_id: int = None,
    old_values: Dict[str, Any] = None,
    new_values: Dict[str, Any] = None,
    ip_address: str = None,
    user_agent: str = None
) -> None:
    """
    Log an audit event
    """
    logger = get_logger("audit")
    
    audit_data = {
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "old_values": old_values,
        "new_values": new_values,
        "ip_address": ip_address,
        "user_agent": user_agent
    }
    
    logger.info("Audit event", **audit_data)


# Error logging
def log_error(
    error: Exception,
    context: Dict[str, Any] = None,
    user_id: int = None
) -> None:
    """
    Log an error with context
    """
    logger = get_logger("error")
    
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
        "user_id": user_id
    }
    
    logger.error("Application error", **error_data, exc_info=True)


# Performance logging
def log_performance(
    operation: str,
    duration_ms: float,
    context: Dict[str, Any] = None
) -> None:
    """
    Log performance metrics
    """
    logger = get_logger("performance")
    
    perf_data = {
        "operation": operation,
        "duration_ms": duration_ms,
        "context": context or {}
    }
    
    logger.info("Performance metric", **perf_data)


# Security logging
def log_security_event(
    event_type: str,
    severity: str = "INFO",
    user_id: int = None,
    ip_address: str = None,
    details: Dict[str, Any] = None
) -> None:
    """
    Log security-related events
    """
    logger = get_logger("security")
    
    security_data = {
        "event_type": event_type,
        "severity": severity,
        "user_id": user_id,
        "ip_address": ip_address,
        "details": details or {}
    }
    
    if severity.upper() == "CRITICAL":
        logger.critical("Security event", **security_data)
    elif severity.upper() == "HIGH":
        logger.error("Security event", **security_data)
    elif severity.upper() == "MEDIUM":
        logger.warning("Security event", **security_data)
    else:
        logger.info("Security event", **security_data)