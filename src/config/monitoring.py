from pydantic import BaseSettings
from typing import Dict, List, Optional
import os

class MonitoringSettings(BaseSettings):
    # Alert thresholds
    FAILED_LOGIN_THRESHOLD: int = 5  # Number of failed logins before alert
    FAILED_LOGIN_WINDOW: int = 300   # Time window in seconds (5 minutes)
    
    RATE_LIMIT_THRESHOLD: int = 10   # Number of rate limit hits before alert
    RATE_LIMIT_WINDOW: int = 60      # Time window in seconds
    
    SUSPICIOUS_IP_THRESHOLD: int = 3  # Number of suspicious activities before alert
    SUSPICIOUS_IP_WINDOW: int = 3600  # Time window in seconds (1 hour)
    
    # Alert channels
    SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
    EMAIL_ALERTS_ENABLED: bool = True
    ALERT_EMAIL_ADDRESSES: List[str] = ["security@yourdomain.com"]
    
    # Prometheus metrics
    PROMETHEUS_PUSH_GATEWAY: Optional[str] = os.getenv("PROMETHEUS_PUSH_GATEWAY")
    
    # Logging
    SECURITY_LOG_LEVEL: str = "INFO"
    SECURITY_LOG_FILE: str = "logs/security.log"
    
    class Config:
        env_prefix = "MONITORING_"

monitoring_settings = MonitoringSettings() 