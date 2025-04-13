import time
import asyncio
import functools
import logging
from datetime import datetime
from typing import Dict, Any, Callable, Optional
from functools import wraps

# Get logger
logger = logging.getLogger("monitoring")

class MetricsTracker:
    def __init__(self):
        self.metrics = {
            "requests": {},
            "errors": {},
            "processing_times": {},
            "custom": {}
        }
    
    def track_request(self, endpoint: str, method: str, status_code: int, processing_time: float):
        """Track API request metrics"""
        key = f"{method}:{endpoint}"
        
        # Initialize if not exists
        if key not in self.metrics["requests"]:
            self.metrics["requests"][key] = {
                "count": 0,
                "status_codes": {},
                "total_time": 0,
                "avg_time": 0
            }
        
        # Update metrics
        self.metrics["requests"][key]["count"] += 1
        self.metrics["requests"][key]["total_time"] += processing_time
        self.metrics["requests"][key]["avg_time"] = (
            self.metrics["requests"][key]["total_time"] / 
            self.metrics["requests"][key]["count"]
        )
        
        # Track status codes
        if status_code not in self.metrics["requests"][key]["status_codes"]:
            self.metrics["requests"][key]["status_codes"][status_code] = 0
        self.metrics["requests"][key]["status_codes"][status_code] += 1
        
        # Log request
        logger.info(f"Request: {method} {endpoint} - Status: {status_code} - Time: {processing_time:.2f}s")
    
    def track_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """Track error metrics"""
        # Initialize if not exists
        if error_type not in self.metrics["errors"]:
            self.metrics["errors"][error_type] = {
                "count": 0,
                "last_occurrence": None,
                "contexts": []
            }
        
        # Update metrics
        self.metrics["errors"][error_type]["count"] += 1
        self.metrics["errors"][error_type]["last_occurrence"] = datetime.now().isoformat()
        
        # Store context if provided
        if context:
            self.metrics["errors"][error_type]["contexts"].append({
                "timestamp": datetime.now().isoformat(),
                "message": error_message,
                "context": context
            })
        
        # Log error
        logger.error(f"Error: {error_type} - {error_message}")
    
    def track_processing_time(self, operation: str, processing_time: float):
        """Track processing time for operations"""
        # Initialize if not exists
        if operation not in self.metrics["processing_times"]:
            self.metrics["processing_times"][operation] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "min_time": float('inf'),
                "max_time": 0
            }
        
        # Update metrics
        self.metrics["processing_times"][operation]["count"] += 1
# Metrics storage
metrics = {
    "requests": {},
    "errors": {},
    "processing_times": {},
    "custom": {}
}

def track_request(endpoint: str, method: str, status_code: int, processing_time: float):
    """Track API request metrics"""
    key = f"{method}:{endpoint}"
    
    # Initialize if not exists
    if key not in metrics["requests"]:
        metrics["requests"][key] = {
            "count": 0,
            "status_codes": {},
            "total_time": 0,
            "avg_time": 0
        }
    
    # Update metrics
    metrics["requests"][key]["count"] += 1
    metrics["requests"][key]["total_time"] += processing_time
    metrics["requests"][key]["avg_time"] = metrics["requests"][key]["total_time"] / metrics["requests"][key]["count"]
    
    # Track status codes
    if status_code not in metrics["requests"][key]["status_codes"]:
        metrics["requests"][key]["status_codes"][status_code] = 0
    metrics["requests"][key]["status_codes"][status_code] += 1
    
    # Log request
    logger.info(f"Request: {method} {endpoint} - Status: {status_code} - Time: {processing_time:.2f}s")

def track_error(error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
    """Track error metrics"""
    # Initialize if not exists
    if error_type not in metrics["errors"]:
        metrics["errors"][error_type] = {
            "count": 0,
            "last_occurrence": None,
            "contexts": []
        }
    
    # Update metrics
    metrics["errors"][error_type]["count"] += 1
    metrics["errors"][error_type]["last_occurrence"] = datetime.now().isoformat()
    
    # Store context if provided
    if context:
        metrics["errors"][error_type]["contexts"].append({
            "timestamp": datetime.now().isoformat(),
            "message": error_message,
            "context": context
        })
    
    # Log error
    logger.error(f"Error: {error_type} - {error_message}")

def track_processing_time(operation: str, processing_time: float):
    """Track processing time for operations"""
    # Initialize if not exists
    if operation not in metrics["processing_times"]:
        metrics["processing_times"][operation] = {
            "count": 0,
            "total_time": 0,
            "avg_time": 0,
            "min_time": float('inf'),
            "max_time": 0
        }
    
    # Update metrics
    metrics["processing_times"][operation]["count"] += 1
    metrics["processing_times"][operation]["total_time"] += processing_time
    metrics["processing_times"][operation]["avg_time"] = metrics["processing_times"][operation]["total_time"] / metrics["processing_times"][operation]["count"]
    metrics["processing_times"][operation]["min_time"] = min(metrics["processing_times"][operation]["min_time"], processing_time)
    metrics["processing_times"][operation]["max_time"] = max(metrics["processing_times"][operation]["max_time"], processing_time)
    
    # Log processing time
    logger.info(f"Processing time for {operation}: {processing_time:.2f}s")

def track_custom_metric(name: str, value: Any, tags: Optional[Dict[str, str]] = None):
    """Track custom metrics"""
    # Initialize if not exists
    if name not in metrics["custom"]:
        metrics["custom"][name] = {
            "values": [],
            "tags": {}
        }
    
    # Update metrics
    metrics["custom"][name]["values"].append({
        "timestamp": datetime.now().isoformat(),
        "value": value
    })
    
    # Update tags if provided
    if tags:
        metrics["custom"][name]["tags"].update(tags)
    
    # Log custom metric
    logger.info(f"Custom metric: {name} = {value}")

def get_metrics() -> Dict[str, Any]:
    """Get all metrics"""
    return metrics

def reset_metrics():
    """Reset all metrics"""
    global metrics
    metrics = {
        "requests": {},
        "errors": {},
        "processing_times": {},
        "custom": {}
    }
    logger.info("Metrics reset")

# Decorator to track function execution time
def track_time(operation_name: Optional[str] = None):
    """Decorator to track function execution time"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Use function name if operation_name is not provided
                op_name = operation_name or func.__name__
                track_processing_time(op_name, processing_time)
                
                return result
            except Exception as e:
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Track error
                op_name = operation_name or func.__name__
                track_error(
                    type(e).__name__,
                    str(e),
                    {"operation": op_name, "processing_time": processing_time}
                )
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Use function name if operation_name is not provided
                op_name = operation_name or func.__name__
                track_processing_time(op_name, processing_time)
                
                return result
            except Exception as e:
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Track error
                op_name = operation_name or func.__name__
                track_error(
                    type(e).__name__,
                    str(e),
                    {"operation": op_name, "processing_time": processing_time}
                )
                
                raise
        
        # Return the appropriate wrapper based on whether the function is async or not
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator 