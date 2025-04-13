from typing import Dict, Any, List
import time
from datetime import datetime, timedelta
import logging
from collections import deque
import psutil
from src.utils.logger import get_logger
import os

logger = get_logger(__name__)

class MetricsTracker:
    def __init__(self, max_history: int = 1000):
        """Initialize metrics tracker with a maximum history size"""
        self.max_history = max_history
        self.request_times: deque = deque(maxlen=max_history)
        self.error_count = 0
        self.total_requests = 0
        self.start_time = datetime.utcnow()
        self.consecutive_errors = 0
        self.last_error_time = None
        self.request_types = {
            "order": 0,
            "status": 0,
            "help": 0,
            "other": 0
        }
        self.memory_usage = deque(maxlen=max_history)
        self.cpu_usage = deque(maxlen=max_history)

    def track_request(self, duration: float, request_type: str = "other") -> None:
        """Track a request's duration and type"""
        self.request_times.append(duration)
        self.total_requests += 1
        self.request_types[request_type] = self.request_types.get(request_type, 0) + 1
        self._track_system_metrics()

    def _track_system_metrics(self) -> None:
        """Track system metrics"""
        try:
            process = psutil.Process()
            self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
            self.cpu_usage.append(process.cpu_percent())
        except Exception as e:
            logger.error(f"Error tracking system metrics: {str(e)}")

    def track_error(self) -> None:
        """Track an error occurrence"""
        self.error_count += 1
        self.consecutive_errors += 1
        self.last_error_time = datetime.utcnow()

    def track_success(self) -> None:
        """Track a successful request"""
        self.consecutive_errors = 0

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        if not self.request_times:
            avg_response_time = 0
            avg_memory_usage = 0
            avg_cpu_usage = 0
        else:
            avg_response_time = sum(self.request_times) / len(self.request_times)
            avg_memory_usage = sum(self.memory_usage) / len(self.memory_usage)
            avg_cpu_usage = sum(self.cpu_usage) / len(self.cpu_usage)

        error_rate = self.error_count / max(self.total_requests, 1)
        uptime = (datetime.utcnow() - self.start_time).total_seconds()

        return {
            "total_requests": self.total_requests,
            "error_count": self.error_count,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "uptime_seconds": uptime,
            "consecutive_errors": self.consecutive_errors,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "request_types": self.request_types,
            "system_metrics": {
                "avg_memory_usage_mb": avg_memory_usage,
                "avg_cpu_usage_percent": avg_cpu_usage,
                "current_memory_usage_mb": self.memory_usage[-1] if self.memory_usage else 0,
                "current_cpu_usage_percent": self.cpu_usage[-1] if self.cpu_usage else 0
            }
        }

    def check_health(self, thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Check health based on thresholds"""
        metrics = self.get_metrics()
        health_status = {
            "status": "healthy",
            "checks": {},
            "details": {
                "timestamp": datetime.utcnow().isoformat(),
                "environment": os.getenv("ENVIRONMENT", "development"),
                "version": os.getenv("APP_VERSION", "1.0.0")
            }
        }

        # Check error rate
        if metrics["error_rate"] > thresholds.get("error_rate", 0.1):
            health_status["checks"]["error_rate"] = {
                "status": "unhealthy",
                "value": metrics["error_rate"],
                "threshold": thresholds.get("error_rate", 0.1),
                "severity": "high",
                "description": "Error rate exceeds threshold"
            }
            health_status["status"] = "unhealthy"

        # Check response time
        if metrics["avg_response_time"] > thresholds.get("response_time", 2.0):
            health_status["checks"]["response_time"] = {
                "status": "unhealthy",
                "value": metrics["avg_response_time"],
                "threshold": thresholds.get("response_time", 2.0),
                "severity": "medium",
                "description": "Average response time exceeds threshold"
            }
            health_status["status"] = "unhealthy"

        # Check consecutive errors
        if metrics["consecutive_errors"] > thresholds.get("consecutive_errors", 3):
            health_status["checks"]["consecutive_errors"] = {
                "status": "unhealthy",
                "value": metrics["consecutive_errors"],
                "threshold": thresholds.get("consecutive_errors", 3),
                "severity": "high",
                "description": "Too many consecutive errors"
            }
            health_status["status"] = "unhealthy"

        # Check memory usage
        if metrics["system_metrics"]["current_memory_usage_mb"] > thresholds.get("memory_usage_mb", 1000):
            health_status["checks"]["memory_usage"] = {
                "status": "unhealthy",
                "value": metrics["system_metrics"]["current_memory_usage_mb"],
                "threshold": thresholds.get("memory_usage_mb", 1000),
                "severity": "high",
                "description": "Memory usage exceeds threshold"
            }
            health_status["status"] = "unhealthy"

        # Check CPU usage
        if metrics["system_metrics"]["current_cpu_usage_percent"] > thresholds.get("cpu_usage_percent", 80):
            health_status["checks"]["cpu_usage"] = {
                "status": "unhealthy",
                "value": metrics["system_metrics"]["current_cpu_usage_percent"],
                "threshold": thresholds.get("cpu_usage_percent", 80),
                "severity": "medium",
                "description": "CPU usage exceeds threshold"
            }
            health_status["status"] = "unhealthy"

        # Check request distribution
        total_requests = sum(metrics["request_types"].values())
        if total_requests > 0:
            for req_type, count in metrics["request_types"].items():
                percentage = count / total_requests
                if percentage > thresholds.get(f"{req_type}_percentage", 0.8):
                    health_status["checks"][f"{req_type}_distribution"] = {
                        "status": "warning",
                        "value": percentage,
                        "threshold": thresholds.get(f"{req_type}_percentage", 0.8),
                        "severity": "low",
                        "description": f"High percentage of {req_type} requests"
                    }

        # Add trend analysis
        if len(self.request_times) > 1:
            recent_times = list(self.request_times)[-10:]
            avg_recent = sum(recent_times) / len(recent_times)
            if avg_recent > metrics["avg_response_time"] * 1.5:
                health_status["checks"]["response_time_trend"] = {
                    "status": "warning",
                    "value": avg_recent,
                    "baseline": metrics["avg_response_time"],
                    "severity": "medium",
                    "description": "Recent response times are significantly higher than average"
                }

        return health_status 