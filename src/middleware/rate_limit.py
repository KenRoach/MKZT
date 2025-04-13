from fastapi import Request, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from redis import Redis
from datetime import datetime, timedelta
from src.config.security import security_settings
import json

class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, redis_client: Redis):
        super().__init__(app)
        self.redis = redis_client
        self.requests_limit = security_settings.RATE_LIMIT_REQUESTS
        self.window = security_settings.RATE_LIMIT_WINDOW

    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP or API key)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self._check_rate_limit(client_id):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        # Process request
        response = await call_next(request)
        return response

    def _get_client_id(self, request: Request) -> str:
        """Get unique identifier for the client (IP or API key)"""
        api_key = request.headers.get(security_settings.API_KEY_HEADER)
        if api_key:
            return f"api_key:{api_key}"
        return f"ip:{request.client.host}"

    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if the client has exceeded the rate limit"""
        current = datetime.utcnow()
        key = f"rate_limit:{client_id}"
        
        # Get current window data
        window_data = self.redis.get(key)
        if not window_data:
            # Initialize new window
            window_data = {
                "count": 1,
                "window_start": current.timestamp()
            }
            self.redis.setex(
                key,
                self.window,
                json.dumps(window_data)
            )
            return True
        
        # Parse existing window data
        window_data = json.loads(window_data)
        window_start = datetime.fromtimestamp(window_data["window_start"])
        
        # Check if window has expired
        if current - window_start > timedelta(seconds=self.window):
            # Reset window
            window_data = {
                "count": 1,
                "window_start": current.timestamp()
            }
            self.redis.setex(
                key,
                self.window,
                json.dumps(window_data)
            )
            return True
        
        # Check if limit exceeded
        if window_data["count"] >= self.requests_limit:
            return False
        
        # Increment counter
        window_data["count"] += 1
        self.redis.setex(
            key,
            self.window,
            json.dumps(window_data)
        )
        return True

class RateLimitExceeded(Exception):
    pass 