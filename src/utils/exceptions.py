"""
Custom exceptions and exception handlers for the Enhanced User Management System
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Dict, Any, Union
import structlog

from src.utils.logging import log_error


# Custom exception classes
class BaseCustomException(Exception):
    """Base class for custom exceptions"""
    
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(BaseCustomException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed", details: Dict[str, Any] = None):
        super().__init__(message, "AUTH_ERROR", details)


class AuthorizationError(BaseCustomException):
    """Authorization related errors"""
    
    def __init__(self, message: str = "Access denied", details: Dict[str, Any] = None):
        super().__init__(message, "AUTHZ_ERROR", details)


class ValidationError(BaseCustomException):
    """Validation related errors"""
    
    def __init__(self, message: str = "Validation failed", details: Dict[str, Any] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class NotFoundError(BaseCustomException):
    """Resource not found errors"""
    
    def __init__(self, message: str = "Resource not found", details: Dict[str, Any] = None):
        super().__init__(message, "NOT_FOUND", details)


class ConflictError(BaseCustomException):
    """Resource conflict errors"""
    
    def __init__(self, message: str = "Resource conflict", details: Dict[str, Any] = None):
        super().__init__(message, "CONFLICT", details)


class DatabaseError(BaseCustomException):
    """Database related errors"""
    
    def __init__(self, message: str = "Database error", details: Dict[str, Any] = None):
        super().__init__(message, "DATABASE_ERROR", details)


class ExternalServiceError(BaseCustomException):
    """External service related errors"""
    
    def __init__(self, message: str = "External service error", details: Dict[str, Any] = None):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)


class RateLimitError(BaseCustomException):
    """Rate limiting errors"""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Dict[str, Any] = None):
        super().__init__(message, "RATE_LIMIT_ERROR", details)


class BusinessLogicError(BaseCustomException):
    """Business logic related errors"""
    
    def __init__(self, message: str = "Business logic error", details: Dict[str, Any] = None):
        super().__init__(message, "BUSINESS_LOGIC_ERROR", details)


# SOAP specific exceptions
class SOAPError(BaseCustomException):
    """SOAP specific errors"""
    
    def __init__(self, message: str, fault_code: str = "SOAP-ENV:Server", details: Dict[str, Any] = None):
        super().__init__(message, "SOAP_ERROR", details)
        self.fault_code = fault_code


class SOAPFaultError(SOAPError):
    """SOAP fault errors"""
    
    def __init__(self, message: str, fault_code: str = "SOAP-ENV:Server", actor: str = None, details: Dict[str, Any] = None):
        super().__init__(message, fault_code, details)
        self.actor = actor


# Error code mappings
ERROR_CODE_MAPPINGS = {
    # Authentication errors
    "AUTH_ERROR": 401,
    "AUTHZ_ERROR": 403,
    
    # Validation errors
    "VALIDATION_ERROR": 422,
    
    # Not found errors
    "NOT_FOUND": 404,
    
    # Conflict errors
    "CONFLICT": 409,
    
    # Rate limiting
    "RATE_LIMIT_ERROR": 429,
    
    # Server errors
    "DATABASE_ERROR": 500,
    "EXTERNAL_SERVICE_ERROR": 502,
    "BUSINESS_LOGIC_ERROR": 422,
    "SOAP_ERROR": 500,
    
    # Default
    "INTERNAL_SERVER_ERROR": 500
}


def get_http_status_code(error_code: str) -> int:
    """Get HTTP status code for error code"""
    return ERROR_CODE_MAPPINGS.get(error_code, 500)


def format_error_response(
    error: Union[BaseCustomException, Exception],
    include_details: bool = True
) -> Dict[str, Any]:
    """Format error response"""
    
    if isinstance(error, BaseCustomException):
        response = {
            "success": False,
            "error": {
                "code": error.code,
                "message": error.message
            }
        }
        
        if include_details and error.details:
            response["error"]["details"] = error.details
            
    elif isinstance(error, HTTPException):
        response = {
            "success": False,
            "error": {
                "code": f"HTTP_{error.status_code}",
                "message": error.detail
            }
        }
        
    else:
        response = {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    
    return response


def format_soap_error_response(error: Union[SOAPError, Exception]) -> str:
    """Format SOAP error response"""
    
    if isinstance(error, SOAPError):
        fault_code = getattr(error, 'fault_code', 'SOAP-ENV:Server')
        actor = getattr(error, 'actor', None)
        
        soap_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <soap:Fault>
            <faultcode>{fault_code}</faultcode>
            <faultstring>{error.message}</faultstring>'''
        
        if actor:
            soap_response += f'\n            <faultactor>{actor}</faultactor>'
        
        if error.details:
            soap_response += f'\n            <detail>{error.details}</detail>'
        
        soap_response += '''
        </soap:Fault>
    </soap:Body>
</soap:Envelope>'''
        
        return soap_response
    
    else:
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <soap:Fault>
            <faultcode>SOAP-ENV:Server</faultcode>
            <faultstring>Internal server error: {str(error)}</faultstring>
        </soap:Fault>
    </soap:Body>
</soap:Envelope>'''


# Exception handlers
async def custom_exception_handler(request: Request, exc: BaseCustomException) -> JSONResponse:
    """Handler for custom exceptions"""
    
    logger = structlog.get_logger()
    
    # Log error
    log_error(
        error=exc,
        context={
            "request_method": request.method,
            "request_url": str(request.url),
            "client_ip": request.client.host if request.client else None
        }
    )
    
    # Format response
    status_code = get_http_status_code(exc.code)
    response_data = format_error_response(exc)
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for HTTP exceptions"""
    
    logger = structlog.get_logger()
    
    # Log error
    logger.warning(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        request_method=request.method,
        request_url=str(request.url),
        client_ip=request.client.host if request.client else None
    )
    
    # Format response
    response_data = format_error_response(exc)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for validation exceptions"""
    
    logger = structlog.get_logger()
    
    # Format validation errors
    validation_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        validation_errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"]
        })
    
    # Log error
    logger.warning(
        "Validation error occurred",
        validation_errors=validation_errors,
        request_method=request.method,
        request_url=str(request.url),
        client_ip=request.client.host if request.client else None
    )
    
    # Format response
    response_data = {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {
                "validation_errors": validation_errors
            }
        }
    }
    
    return JSONResponse(
        status_code=422,
        content=response_data
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for general exceptions"""
    
    logger = structlog.get_logger()
    
    # Log error
    log_error(
        error=exc,
        context={
            "request_method": request.method,
            "request_url": str(request.url),
            "client_ip": request.client.host if request.client else None
        }
    )
    
    # Format response
    response_data = format_error_response(exc, include_details=False)
    
    return JSONResponse(
        status_code=500,
        content=response_data
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers for FastAPI application"""
    
    # Custom exception handlers
    app.add_exception_handler(BaseCustomException, custom_exception_handler)
    
    # Built-in exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)


# Utility functions for raising exceptions
def raise_auth_error(message: str = "Authentication failed", details: Dict[str, Any] = None):
    """Raise authentication error"""
    raise AuthenticationError(message, details)


def raise_authz_error(message: str = "Access denied", details: Dict[str, Any] = None):
    """Raise authorization error"""
    raise AuthorizationError(message, details)


def raise_validation_error(message: str = "Validation failed", details: Dict[str, Any] = None):
    """Raise validation error"""
    raise ValidationError(message, details)


def raise_not_found_error(message: str = "Resource not found", details: Dict[str, Any] = None):
    """Raise not found error"""
    raise NotFoundError(message, details)


def raise_conflict_error(message: str = "Resource conflict", details: Dict[str, Any] = None):
    """Raise conflict error"""
    raise ConflictError(message, details)


def raise_database_error(message: str = "Database error", details: Dict[str, Any] = None):
    """Raise database error"""
    raise DatabaseError(message, details)


def raise_business_logic_error(message: str = "Business logic error", details: Dict[str, Any] = None):
    """Raise business logic error"""
    raise BusinessLogicError(message, details)


def raise_rate_limit_error(message: str = "Rate limit exceeded", details: Dict[str, Any] = None):
    """Raise rate limit error"""
    raise RateLimitError(message, details)


def raise_soap_error(message: str, fault_code: str = "SOAP-ENV:Server", details: Dict[str, Any] = None):
    """Raise SOAP error"""
    raise SOAPError(message, fault_code, details)