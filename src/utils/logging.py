import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
def setup_logging():
    """Set up logging configuration for the application"""
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create a file handler for all logs
    log_file = logs_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Create a file handler for error logs
    error_log_file = logs_dir / f"error_{datetime.now().strftime('%Y%m%d')}.log"
    error_file_handler = logging.handlers.RotatingFileHandler(
        error_log_file, maxBytes=10485760, backupCount=10
    )
    error_file_handler.setFormatter(formatter)
    error_file_handler.setLevel(logging.ERROR)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add the handlers to the root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_file_handler)
    root_logger.addHandler(console_handler)
    
    # Set up loggers for specific components
    loggers = {
        "whatsapp": logging.getLogger("whatsapp"),
        "ai": logging.getLogger("ai"),
        "crm": logging.getLogger("crm"),
        "database": logging.getLogger("database"),
        "api": logging.getLogger("api")
    }
    
    # Configure each logger
    for logger in loggers.values():
        logger.setLevel(logging.INFO)
    
    return loggers

# Create a function to get a logger
def get_logger(name):
    """Get a logger with the specified name"""
    return logging.getLogger(name) 