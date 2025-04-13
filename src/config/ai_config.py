from typing import Dict, Any
from pydantic import BaseSettings, SecretStr

class AIConfig(BaseSettings):
    """AI Configuration Settings"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: SecretStr
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.7
    
    # Google Cloud AI Configuration
    GOOGLE_CLOUD_PROJECT_ID: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    GOOGLE_SPEECH_TO_TEXT_API_KEY: SecretStr
    GOOGLE_LANGUAGE_API_KEY: SecretStr
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: SecretStr
    
    # AI Service Settings
    AI_RATE_LIMIT: int = 60  # requests per minute
    AI_CACHE_TTL: int = 3600  # cache time in seconds
    AI_ERROR_THRESHOLD: int = 3  # consecutive errors before alerting
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def get_openai_settings(self) -> Dict[str, Any]:
        """Get OpenAI settings"""
        return {
            "api_key": self.OPENAI_API_KEY.get_secret_value(),
            "model": self.OPENAI_MODEL,
            "max_tokens": self.OPENAI_MAX_TOKENS,
            "temperature": self.OPENAI_TEMPERATURE
        }
    
    def get_google_ai_settings(self) -> Dict[str, Any]:
        """Get Google AI settings"""
        return {
            "project_id": self.GOOGLE_CLOUD_PROJECT_ID,
            "credentials_path": self.GOOGLE_APPLICATION_CREDENTIALS,
            "speech_to_text_key": self.GOOGLE_SPEECH_TO_TEXT_API_KEY.get_secret_value(),
            "language_key": self.GOOGLE_LANGUAGE_API_KEY.get_secret_value()
        }
    
    def get_supabase_settings(self) -> Dict[str, Any]:
        """Get Supabase settings"""
        return {
            "url": self.SUPABASE_URL,
            "key": self.SUPABASE_KEY.get_secret_value()
        }

# Create global instance
ai_config = AIConfig() 