from pydantic import BaseSettings
from functools import lru_cache
from typing import List, Optional

class Settings(BaseSettings):
    # ... existing code ...
    
    # DeepSeek Configuration
    DEEPSEEK_API_KEY: str
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_MAX_TOKENS: int = 500
    DEEPSEEK_TEMPERATURE: float = 0.1
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# ... existing code ... 