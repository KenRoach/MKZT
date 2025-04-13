import os
from typing import Dict, Any
from dotenv import load_dotenv

class Config:
    """Configuration management class"""
    
    def __init__(self):
        """Initialize configuration with environment variables"""
        load_dotenv()
        
        # Database configuration
        self.DATABASE_URL = self._get_required_env("DATABASE_URL")
        
        # OpenAI configuration
        self.OPENAI_API_KEY = self._get_required_env("OPENAI_API_KEY")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        self.OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        # WhatsApp configuration
        self.WHATSAPP_API_TOKEN = self._get_required_env("WHATSAPP_API_TOKEN")
        self.WHATSAPP_PHONE_NUMBER_ID = self._get_required_env("WHATSAPP_PHONE_NUMBER_ID")
        self.WHATSAPP_VERIFY_TOKEN = self._get_required_env("WHATSAPP_VERIFY_TOKEN")
        
        # CRM configuration
        self.CRM_API_KEY = self._get_required_env("CRM_API_KEY")
        self.CRM_BASE_URL = self._get_required_env("CRM_BASE_URL")
        
        # Email configuration
        self.SMTP_SERVER = self._get_required_env("SMTP_SERVER")
        self.SMTP_PORT = int(self._get_required_env("SMTP_PORT"))
        self.SMTP_USERNAME = self._get_required_env("SMTP_USERNAME")
        self.SMTP_PASSWORD = self._get_required_env("SMTP_PASSWORD")
        self.FROM_EMAIL = self._get_required_env("FROM_EMAIL")
        self.ADMIN_EMAILS = self._get_required_env("ADMIN_EMAILS").split(",")
        
        # Monitoring configuration
        self.ERROR_RATE_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", "0.1"))
        self.RESPONSE_TIME_THRESHOLD = float(os.getenv("RESPONSE_TIME_THRESHOLD", "2.0"))
        self.CONSECUTIVE_ERRORS_THRESHOLD = int(os.getenv("CONSECUTIVE_ERRORS_THRESHOLD", "3"))
        
        # Slack configuration
        self.SLACK_WEBHOOK_URL = self._get_required_env("SLACK_WEBHOOK_URL")
        
        # Environment
        self.ENV = os.getenv("ENV", "development")
        self.DEBUG = self.ENV == "development"
    
    def _get_required_env(self, key: str) -> str:
        """Get a required environment variable"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith("_")
        }
    
    def validate(self) -> None:
        """Validate configuration values"""
        # Validate database URL
        if not self.DATABASE_URL.startswith(("postgresql://", "sqlite://")):
            raise ValueError("Invalid DATABASE_URL format")
        
        # Validate email configuration
        if not all([self.SMTP_SERVER, self.SMTP_PORT, self.SMTP_USERNAME, self.SMTP_PASSWORD]):
            raise ValueError("Missing required email configuration")
        
        # Validate WhatsApp configuration
        if not all([self.WHATSAPP_API_TOKEN, self.WHATSAPP_PHONE_NUMBER_ID, self.WHATSAPP_VERIFY_TOKEN]):
            raise ValueError("Missing required WhatsApp configuration")
        
        # Validate CRM configuration
        if not all([self.CRM_API_KEY, self.CRM_BASE_URL]):
            raise ValueError("Missing required CRM configuration")
        
        # Validate monitoring thresholds
        if not (0 <= self.ERROR_RATE_THRESHOLD <= 1):
            raise ValueError("ERROR_RATE_THRESHOLD must be between 0 and 1")
        if self.RESPONSE_TIME_THRESHOLD <= 0:
            raise ValueError("RESPONSE_TIME_THRESHOLD must be positive")
        if self.CONSECUTIVE_ERRORS_THRESHOLD <= 0:
            raise ValueError("CONSECUTIVE_ERRORS_THRESHOLD must be positive")

# Create a global configuration instance
config = Config()

# API Keys
WHATSAPP_API_KEY = config.WHATSAPP_API_TOKEN
OPENAI_API_KEY = config.OPENAI_API_KEY
CRM_API_KEY = config.CRM_API_KEY

# Database
DATABASE_URL = config.DATABASE_URL

# AI Settings
AI_MODEL = config.OPENAI_MODEL
MAX_TOKENS = config.OPENAI_MAX_TOKENS
TEMPERATURE = config.OPENAI_TEMPERATURE

# WhatsApp Settings
WHATSAPP_WEBHOOK_URL = "/webhook/whatsapp"
WHATSAPP_BASE_URL = "https://graph.facebook.com/v17.0"  # WhatsApp Business API base URL

# CRM Settings
CRM_BASE_URL = config.CRM_BASE_URL
CRM_TIMEOUT = 30  # seconds

# Website Settings
WEBSITE_BASE_URL = os.getenv("WEBSITE_BASE_URL")
WEBSITE_SEARCH_ENDPOINT = "/search"

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 