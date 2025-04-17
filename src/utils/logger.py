import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Any, Dict, Optional, Callable
import uuid
import time
from functools import wraps

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class StructuredLogger:
    """
    A structured logger that adds context to log messages and outputs them in JSON format.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._request_id = None
        self._user_id = None
        self._service = name
    
    @property
    def request_id(self) -> str:
        """Get the current request ID or generate a new one if not set."""
        if not self._request_id:
            self._request_id = str(uuid.uuid4())
        return self._request_id
    
    @request_id.setter
    def request_id(self, value: str):
        """Set the request ID for the current context."""
        self._request_id = value
    
    @property
    def user_id(self) -> Optional[str]:
        """Get the current user ID if set."""
        return self._user_id
    
    @user_id.setter
    def user_id(self, value: str):
        """Set the user ID for the current context."""
        self._user_id = value
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal method to log with context."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": logging.getLevelName(level),
            "service": self._service,
            "message": message,
            "request_id": self.request_id,
        }
        
        if self._user_id:
            log_data["user_id"] = self._user_id
        
        # Add any additional context
        log_data.update(kwargs)
        
        # Output as JSON for structured logging
        self.logger.log(level, json.dumps(log_data))
    
    def debug(self, message: str, **kwargs):
        """Log a debug message."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log an info message."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log a warning message."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log an error message."""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log a critical message."""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, exc_info=True, **kwargs):
        """Log an exception with traceback."""
        self._log(logging.ERROR, message, exc_info=exc_info, **kwargs)


# Create a context manager for request context
class RequestContext:
    """
    Context manager to set request context for logging.
    """
    
    def __init__(self, logger: StructuredLogger, request_id: Optional[str] = None, user_id: Optional[str] = None):
        self.logger = logger
        self.request_id = request_id
        self.user_id = user_id
        self._previous_request_id = None
        self._previous_user_id = None
    
    def __enter__(self):
        # Store previous values
        self._previous_request_id = self.logger.request_id
        self._previous_user_id = self.logger.user_id
        
        # Set new values
        if self.request_id:
            self.logger.request_id = self.request_id
        if self.user_id:
            self.logger.user_id = self.user_id
        
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore previous values
        self.logger.request_id = self._previous_request_id
        self.logger.user_id = self._previous_user_id


# Decorator for timing function execution
def log_execution_time(logger: StructuredLogger):
    """
    Decorator to log the execution time of a function.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f"Function {func.__name__} executed successfully",
                    function=func.__name__,
                    execution_time_ms=round(execution_time * 1000, 2)
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.exception(
                    f"Function {func.__name__} failed",
                    function=func.__name__,
                    execution_time_ms=round(execution_time * 1000, 2),
                    error=str(e)
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f"Function {func.__name__} executed successfully",
                    function=func.__name__,
                    execution_time_ms=round(execution_time * 1000, 2)
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.exception(
                    f"Function {func.__name__} failed",
                    function=func.__name__,
                    execution_time_ms=round(execution_time * 1000, 2),
                    error=str(e)
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Create a singleton logger instance
logger = StructuredLogger("mkzt")

def setup_logger(name: str = "whatsapp_bot") -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/whatsapp_bot.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create default logger
logger = setup_logger()

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)

class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter for adding context to log messages"""
    
    def __init__(self, logger: logging.Logger, extra: Dict[str, Any]):
        super().__init__(logger, extra)
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process the log message and kwargs"""
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"].update(self.extra)
        return msg, kwargs

def get_context_logger(name: str, context: Dict[str, Any]) -> LoggerAdapter:
    """Get a logger instance with context"""
    logger = get_logger(name)
    return LoggerAdapter(logger, context) 