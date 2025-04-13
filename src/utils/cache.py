from typing import Any, Optional
from datetime import datetime, timedelta
import json
import redis
from src.config.ai_config import ai_config

class Cache:
    """Simple cache implementation using Redis"""
    
    def __init__(self, ttl: int = 3600):
        """Initialize cache with TTL in seconds"""
        self.ttl = ttl
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any) -> bool:
        """Set value in cache"""
        try:
            return self.redis.setex(
                key,
                self.ttl,
                json.dumps(value)
            )
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return bool(self.redis.delete(key))
        except Exception:
            return False
    
    async def clear(self) -> bool:
        """Clear all cached values"""
        try:
            return self.redis.flushdb()
        except Exception:
            return False 