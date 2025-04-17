from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum
import os

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class SecurityConfig:
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiry: int = 3600  # 1 hour
    rate_limit: int = 100  # requests per minute
    cors_origins: list = None
    allowed_hosts: list = None
    
@dataclass
class MonitoringConfig:
    prometheus_port: int = 9090
    grafana_port: int = 3000
    log_level: str = "INFO"
    trace_sampling_rate: float = 0.1

@dataclass
class CacheConfig:
    redis_url: str
    default_ttl: int = 300  # 5 minutes
    max_connections: int = 10

@dataclass
class QueueConfig:
    rabbitmq_url: str
    max_retries: int = 3
    retry_delay: int = 60  # seconds

class InfrastructureConfig:
    def __init__(self, env: Environment):
        self.env = env
        self.security = self._load_security_config()
        self.monitoring = self._load_monitoring_config()
        self.cache = self._load_cache_config()
        self.queue = self._load_queue_config()
        
    def _load_security_config(self) -> SecurityConfig:
        return SecurityConfig(
            jwt_secret=os.getenv("JWT_SECRET"),
            cors_origins=os.getenv("CORS_ORIGINS", "").split(","),
            allowed_hosts=os.getenv("ALLOWED_HOSTS", "").split(",")
        )
        
    def _load_monitoring_config(self) -> MonitoringConfig:
        return MonitoringConfig(
            prometheus_port=int(os.getenv("PROMETHEUS_PORT", 9090)),
            grafana_port=int(os.getenv("GRAFANA_PORT", 3000)),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
        
    def _load_cache_config(self) -> CacheConfig:
        return CacheConfig(
            redis_url=os.getenv("REDIS_URL"),
            default_ttl=int(os.getenv("CACHE_TTL", 300))
        )
        
    def _load_queue_config(self) -> QueueConfig:
        return QueueConfig(
            rabbitmq_url=os.getenv("RABBITMQ_URL"),
            max_retries=int(os.getenv("QUEUE_MAX_RETRIES", 3))
        ) 