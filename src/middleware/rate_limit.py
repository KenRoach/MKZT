from fastapi import Request, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from redis import Redis
from datetime import datetime, timedelta
from src.config.security import security_settings
import json
import asyncio
from typing import Dict, Optional
from src.config.security import get_security_settings
from src.utils.logger import logger
import redis.asyncio as redis

class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        settings = get_security_settings()
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        self.rate_limits = settings.RATE_LIMIT_CONFIG

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        path = request.url.path
        
        # Determine rate limit type based on path
        limit_type = "default"
        if path.startswith("/api/auth"):
            limit_type = "auth"
        elif path.startswith("/api"):
            limit_type = "api"
        elif path.startswith("/webhook"):
            limit_type = "webhook"
            
        key = f"rate_limit:{client_ip}:{path}"
        
        if await self.is_rate_limited(key, limit_type):
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={"Retry-After": "60"}
            )
            
        response = await call_next(request)
        return response

    async def is_rate_limited(self, key: str, limit_type: str = "default") -> bool:
        try:
            rate_limit = self.rate_limits.get(limit_type, self.rate_limits["default"])
            max_requests, window = self._parse_rate_limit(rate_limit)
            
            current = await self.redis.get(key)
            if not current:
                await self.redis.setex(key, window, 1)
                return False
                
            count = int(current)
            if count >= max_requests:
                return True
                
            await self.redis.incr(key)
            return False
            
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            return False

    def _parse_rate_limit(self, rate_limit: str) -> tuple:
        requests, period = rate_limit.split("/")
        seconds = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}
        return int(requests), seconds[period]

class RateLimitExceeded(Exception):
    pass 