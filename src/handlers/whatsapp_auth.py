import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
from src.data.crm_repository import CRMRepository
from src.utils.twilio_client import twilio_client

logger = logging.getLogger(__name__)

class WhatsAppAuthHandler:
    """Handler for WhatsApp-based merchant authentication"""
    
    def __init__(self):
        self.crm_repository = CRMRepository()
        self.twilio_client = twilio_client
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
        self.auth_code_expiry = timedelta(minutes=10)
        
    async def initiate_auth(self, phone_number: str) -> Dict[str, Any]:
        """Initiate WhatsApp authentication for a merchant"""
        try:
            # Generate a 6-digit auth code
            auth_code = "".join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Store the auth code with expiry
            await self.crm_repository.store_auth_code(
                phone_number=phone_number,
                auth_code=auth_code,
                expiry=datetime.now() + self.auth_code_expiry
            )
            
            # Send auth code via WhatsApp
            message = (
                f"Welcome to MKZT Merchant Portal!\n\n"
                f"Your authentication code is: {auth_code}\n\n"
                f"This code will expire in 10 minutes.\n\n"
                f"If you didn't request this code, please ignore this message."
            )
            
            await self.twilio_client.send_whatsapp_message(
                to=phone_number,
                message=message
            )
            
            return {
                "status": "success",
                "message": "Authentication code sent via WhatsApp",
                "phone_number": phone_number
            }
            
        except Exception as e:
            logger.error(f"Error initiating WhatsApp auth: {str(e)}")
            raise
            
    async def verify_auth_code(self, phone_number: str, auth_code: str) -> Dict[str, Any]:
        """Verify the authentication code and generate JWT token"""
        try:
            # Get stored auth code
            stored_auth = await self.crm_repository.get_auth_code(phone_number)
            
            if not stored_auth:
                raise ValueError("No authentication code found for this phone number")
                
            if stored_auth["expiry"] < datetime.now():
                raise ValueError("Authentication code has expired")
                
            if stored_auth["auth_code"] != auth_code:
                raise ValueError("Invalid authentication code")
                
            # Get or create merchant profile
            merchant = await self.crm_repository.get_merchant_by_phone(phone_number)
            
            if not merchant:
                # Create new merchant profile
                merchant = await self.crm_repository.create_merchant({
                    "phone_number": phone_number,
                    "status": "pending_verification",
                    "created_at": datetime.now().isoformat()
                })
                
            # Generate JWT token
            token = jwt.encode(
                {
                    "merchant_id": merchant["id"],
                    "phone_number": phone_number,
                    "role": "merchant",
                    "exp": datetime.now() + timedelta(days=30)
                },
                self.jwt_secret,
                algorithm="HS256"
            )
            
            # Clear used auth code
            await self.crm_repository.delete_auth_code(phone_number)
            
            return {
                "status": "success",
                "message": "Authentication successful",
                "token": token,
                "merchant": merchant
            }
            
        except Exception as e:
            logger.error(f"Error verifying auth code: {str(e)}")
            raise
            
    async def send_welcome_message(self, phone_number: str, merchant: Dict[str, Any]) -> None:
        """Send welcome message with instructions"""
        try:
            message = (
                f"Welcome to MKZT Merchant Portal, {merchant.get('name', 'Merchant')}!\n\n"
                f"You can now manage your inventory and menu through WhatsApp.\n\n"
                f"Available commands:\n"
                f"- 'Add item': Add a new inventory item\n"
                f"- 'Update price': Update item prices\n"
                f"- 'View menu': View your current menu\n"
                f"- 'Add photo': Add photos to your items\n"
                f"- 'Help': View all available commands\n\n"
                f"Start by sending 'Add item' to add your first inventory item."
            )
            
            await self.twilio_client.send_whatsapp_message(
                to=phone_number,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Error sending welcome message: {str(e)}")
            raise

# Create singleton instance
whatsapp_auth = WhatsAppAuthHandler() 