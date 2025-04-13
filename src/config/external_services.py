from typing import Dict, Any
from pydantic import BaseSettings, SecretStr

class ExternalServiceSettings(BaseSettings):
    """External service settings"""
    
    # Google Maps settings
    GOOGLE_MAPS_API_KEY: SecretStr
    GOOGLE_MAPS_GEOCODING_API_KEY: SecretStr
    GOOGLE_MAPS_DISTANCE_MATRIX_API_KEY: SecretStr
    
    # Twilio settings
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: SecretStr
    TWILIO_PHONE_NUMBER: str
    TWILIO_WHATSAPP_NUMBER: str
    TWILIO_WEBHOOK_SECRET: SecretStr
    
    # Firebase settings
    FIREBASE_PROJECT_ID: str
    FIREBASE_PRIVATE_KEY: SecretStr
    FIREBASE_CLIENT_EMAIL: str
    FIREBASE_DATABASE_URL: str
    
    # Service-specific settings
    GOOGLE_MAPS_REGION: str = "ke"  # Default region
    GOOGLE_MAPS_LANGUAGE: str = "en"  # Default language
    TWILIO_SMS_ENABLED: bool = True
    TWILIO_VOICE_ENABLED: bool = True
    TWILIO_WHATSAPP_ENABLED: bool = True
    FIREBASE_NOTIFICATIONS_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    def get_google_maps_settings(self) -> Dict[str, Any]:
        """Get Google Maps settings"""
        return {
            "api_key": self.GOOGLE_MAPS_API_KEY.get_secret_value(),
            "geocoding_api_key": self.GOOGLE_MAPS_GEOCODING_API_KEY.get_secret_value(),
            "distance_matrix_api_key": self.GOOGLE_MAPS_DISTANCE_MATRIX_API_KEY.get_secret_value(),
            "region": self.GOOGLE_MAPS_REGION,
            "language": self.GOOGLE_MAPS_LANGUAGE
        }
        
    def get_twilio_settings(self) -> Dict[str, Any]:
        """Get Twilio settings"""
        return {
            "account_sid": self.TWILIO_ACCOUNT_SID,
            "auth_token": self.TWILIO_AUTH_TOKEN.get_secret_value(),
            "phone_number": self.TWILIO_PHONE_NUMBER,
            "whatsapp_number": self.TWILIO_WHATSAPP_NUMBER,
            "webhook_secret": self.TWILIO_WEBHOOK_SECRET.get_secret_value(),
            "sms_enabled": self.TWILIO_SMS_ENABLED,
            "voice_enabled": self.TWILIO_VOICE_ENABLED,
            "whatsapp_enabled": self.TWILIO_WHATSAPP_ENABLED
        }
        
    def get_firebase_settings(self) -> Dict[str, Any]:
        """Get Firebase settings"""
        return {
            "project_id": self.FIREBASE_PROJECT_ID,
            "private_key": self.FIREBASE_PRIVATE_KEY.get_secret_value(),
            "client_email": self.FIREBASE_CLIENT_EMAIL,
            "database_url": self.FIREBASE_DATABASE_URL,
            "notifications_enabled": self.FIREBASE_NOTIFICATIONS_ENABLED
        }
        
# Create settings instance
external_service_settings = ExternalServiceSettings() 