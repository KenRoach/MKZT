from typing import Dict, Any
from pydantic import BaseSettings, SecretStr

class PaymentSettings(BaseSettings):
    """Payment provider settings"""
    
    # Stripe settings
    STRIPE_SECRET_KEY: SecretStr
    STRIPE_WEBHOOK_SECRET: SecretStr
    STRIPE_PUBLISHABLE_KEY: str
    
    # PayPal settings
    PAYPAL_CLIENT_ID: str
    PAYPAL_SECRET_KEY: SecretStr
    PAYPAL_WEBHOOK_ID: str
    PAYPAL_MODE: str = "sandbox"  # or "live"
    
    # M-Pesa settings
    MPESA_CONSUMER_KEY: str
    MPESA_CONSUMER_SECRET: SecretStr
    MPESA_PASSKEY: SecretStr
    MPESA_SHORTCODE: str
    MPESA_ENV: str = "sandbox"  # or "production"
    
    # General settings
    DEFAULT_CURRENCY: str = "USD"
    SUPPORTED_CURRENCIES: Dict[str, Any] = {
        "USD": {"symbol": "$", "decimals": 2},
        "EUR": {"symbol": "€", "decimals": 2},
        "GBP": {"symbol": "£", "decimals": 2},
        "KES": {"symbol": "KSh", "decimals": 0}
    }
    
    # Webhook settings
    WEBHOOK_TIMEOUT: int = 30  # seconds
    WEBHOOK_MAX_RETRIES: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    def get_provider_settings(self, provider: str) -> Dict[str, Any]:
        """Get settings for a specific provider"""
        if provider == "stripe":
            return {
                "secret_key": self.STRIPE_SECRET_KEY.get_secret_value(),
                "webhook_secret": self.STRIPE_WEBHOOK_SECRET.get_secret_value(),
                "publishable_key": self.STRIPE_PUBLISHABLE_KEY
            }
        elif provider == "paypal":
            return {
                "client_id": self.PAYPAL_CLIENT_ID,
                "secret_key": self.PAYPAL_SECRET_KEY.get_secret_value(),
                "webhook_id": self.PAYPAL_WEBHOOK_ID,
                "mode": self.PAYPAL_MODE
            }
        elif provider == "momo":
            return {
                "consumer_key": self.MPESA_CONSUMER_KEY,
                "consumer_secret": self.MPESA_CONSUMER_SECRET.get_secret_value(),
                "passkey": self.MPESA_PASSKEY.get_secret_value(),
                "shortcode": self.MPESA_SHORTCODE,
                "env": self.MPESA_ENV
            }
        else:
            raise ValueError(f"Unsupported payment provider: {provider}")
            
    def get_currency_settings(self, currency: str) -> Dict[str, Any]:
        """Get settings for a specific currency"""
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")
        return self.SUPPORTED_CURRENCIES[currency]
        
# Create settings instance
payment_settings = PaymentSettings() 