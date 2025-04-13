from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AppError(Exception):
    """Base exception class for application errors"""
    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(AppError):
    """Exception for validation errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status_code=400, details=details)

class AuthenticationError(AppError):
    """Exception for authentication errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status_code=401, details=details)

class NotFoundError(AppError):
    """Exception for not found errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status_code=404, details=details)

class DatabaseError(AppError):
    """Exception for database errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status_code=500, details=details)

class ExternalServiceError(AppError):
    """Exception for external service errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status_code=502, details=details)

async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global error handler for the application"""
    # Get request details
    path = request.url.path
    method = request.method
    client_host = request.client.host if request.client else None
    
    # Create error context
    error_context = {
        "path": path,
        "method": method,
        "client_host": client_host
    }
    
    # Handle known application errors
    if isinstance(exc, AppError):
        logger.error(
            f"Application error: {exc.message}",
            extra={"error_context": error_context, "details": exc.details}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.message,
                "details": exc.details
            }
        )
    
    # Handle validation errors
    if isinstance(exc, ValueError):
        logger.error(
            f"Validation error: {str(exc)}",
            extra={"error_context": error_context}
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "Validation error",
                "details": {"error": str(exc)}
            }
        )
    
    # Handle database errors
    if isinstance(exc, Exception) and "database" in str(exc).lower():
        logger.error(
            f"Database error: {str(exc)}",
            extra={"error_context": error_context}
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Database error",
                "details": {"error": str(exc)}
            }
        )
    
    # Handle external service errors
    if isinstance(exc, Exception) and any(
        service in str(exc).lower()
        for service in ["api", "http", "connection", "timeout"]
    ):
        logger.error(
            f"External service error: {str(exc)}",
            extra={"error_context": error_context}
        )
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "status": "error",
                "message": "External service error",
                "details": {"error": str(exc)}
            }
        )
    
    # Handle unknown errors
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={"error_context": error_context},
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "details": {"error": str(exc)}
        }
    ) 