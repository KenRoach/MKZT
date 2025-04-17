import os
from typing import List, Dict, Any, Optional
from pydantic import BaseSettings, SecretStr
import secrets
import json
from functools import lru_cache

class SecuritySettings(BaseSettings):
    # API Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEY_LENGTH: int = 32
    API_KEY_PREFIX: str = "mkzt_"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("SECURITY_RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("SECURITY_RATE_LIMIT_WINDOW", "3600"))
    
    # CORS Settings
    CORS_ORIGINS: List[str] = json.loads(os.getenv("SECURITY_CORS_ORIGINS", '["https://your-production-domain.com"]'))
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    CORS_ALLOW_HEADERS: List[str] = [
        "Authorization",
        "Content-Type",
        "X-API-Key",
        "X-Request-ID"
    ]
    
    # JWT Settings
    JWT_SECRET_KEY: SecretStr = SecretStr(os.getenv("SECURITY_JWT_SECRET_KEY", secrets.token_urlsafe(32)))
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password Security
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPER: bool = True
    PASSWORD_REQUIRE_LOWER: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_SALT_ROUNDS: int = int(os.getenv("SECURITY_PASSWORD_SALT_ROUNDS", "12"))
    
    # Session Security
    SESSION_LIFETIME: int = int(os.getenv("SECURITY_SESSION_LIFETIME", "3600"))
    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    
    # Content Security Policy
    CSP_DIRECTIVES: Dict[str, str] = {
        "default-src": "'self'",
        "script-src": "'self'",
        "style-src": "'self'",
        "img-src": "'self' data: https:",
        "font-src": "'self'",
        "connect-src": "'self'",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "base-uri": "'self'",
        "object-src": "'none'"
    }
    
    # Security Headers
    SECURITY_HEADERS: Dict[str, str] = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Embedder-Policy": "require-corp"
    }
    
    # Redis settings for rate limiting
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = int(os.getenv("SECURITY_MAX_UPLOAD_SIZE", "5242880"))  # 5MB in bytes
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf", "doc", "docx"]
    
    # Authentication Settings
    AUTH_REQUIRED_ROUTES: List[str] = [
        "/api/v1/users/me",
        "/api/v1/orders/*",
        "/api/v1/payments/*"
    ]
    
    # IP Blocking Settings
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_ATTEMPT_WINDOW: int = 900  # 15 minutes in seconds
    IP_BLOCK_DURATION: int = 3600  # 1 hour in seconds
    
    # Enhanced Rate Limiting
    RATE_LIMIT_CONFIG: Dict[str, str] = {
        "default": "100/hour",
        "auth": "5/minute",
        "api": "1000/day",
        "webhook": "500/hour"
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_prefix = "SECURITY_"

@lru_cache()
def get_security_settings() -> SecuritySettings:
    """Returns a cached instance of SecuritySettings."""
    return SecuritySettings()

# Middleware functions for implementing security measures
def apply_security_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Apply security headers to the response."""
    settings = get_security_settings()
    headers.update(settings.SECURITY_HEADERS)
    
    # Build CSP header
    csp_header = "; ".join(f"{key} {value}" for key, value in settings.CSP_DIRECTIVES.items())
    headers["Content-Security-Policy"] = csp_header
    
    return headers

def validate_file_upload(filename: str, filesize: int) -> bool:
    """Validate file upload against security settings."""
    settings = get_security_settings()
    
    if filesize > settings.MAX_UPLOAD_SIZE:
        return False
    
    extension = filename.split(".")[-1].lower() if "." in filename else ""
    return extension in settings.ALLOWED_EXTENSIONS

# Create settings instance
security_settings = SecuritySettings() 