import os
from typing import Dict, Any
from pydantic import BaseSettings

class DevelopmentSettings(BaseSettings):
    # Debug mode
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://localhost:5432/mkzt_dev"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # WhatsApp API (using sandbox in development)
    WHATSAPP_API_KEY: str = "your_test_api_key"
    WHATSAPP_SANDBOX_NUMBER: str = "+1234567890"
    
    # Security
    JWT_SECRET_KEY: str = "dev_secret_key"
    API_KEY_HEADER: str = "X-API-Key"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "logs/development.log"
    
    class Config:
        env_file = ".env.development"

dev_settings = DevelopmentSettings() 