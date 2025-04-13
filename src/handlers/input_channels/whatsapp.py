import os
from typing import Dict, Any, Optional
import logging
import json
import aiohttp
from src.config.logger import setup_logging
from src.handlers.voice_order_handler import VoiceOrderHandler

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

class WhatsAppInputHandler:
    def __init__(self):
        self.api_key = os.getenv("WHATSAPP_API_KEY")
        self.voice_handler = VoiceOrderHandler()
        
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate the incoming WhatsApp message."""
        required_fields = ["message_id", "from", "timestamp"]
        
        if not all(field in data for field in required_fields):
            return False
            
        # Check if it's a text message or voice message
        if "text" not in data and "voice" not in data:
            return False
            
        return True
        
    async def process_input(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Process the WhatsApp message and convert it to a standardized order format."""
        try:
            if not await self.validate_input(data):
                logger.error("Invalid WhatsApp message format")
                return None
                
            # Handle voice messages
            if "voice" in data:
                voice_url = await self._get_media_url(data["voice"]["id"])
                order_details = await self.voice_handler.process_voice_message(voice_url, "whatsapp")
                if order_details and await self.voice_handler.validate_order(order_details):
                    return self._format_order(order_details, data)
                return None
                
            # Handle text messages
            if "text" in data:
                # Existing text message processing logic
                order_details = self._parse_text_order(data["text"])
                return self._format_order(order_details, data)
                
            return None
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp input: {str(e)}")
            return None
            
    async def _get_media_url(self, media_id: str) -> str:
        """Get the URL for a media file from WhatsApp."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                url = f"https://graph.facebook.com/v12.0/{media_id}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["url"]
                    else:
                        logger.error(f"Failed to get media URL. Status: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting media URL: {str(e)}")
            return None
            
    def _parse_text_order(self, text: str) -> Dict:
        """Parse order details from text message."""
        # Existing text parsing logic
        # This is a placeholder - implement your text parsing logic here
        return {}
        
    def _format_order(self, order_details: Dict, raw_data: Dict) -> Dict:
        """Format the order details into a standardized structure."""
        return {
            "customer_id": raw_data["from"],
            "order_source": "whatsapp",
            "message_id": raw_data["message_id"],
            "timestamp": raw_data["timestamp"],
            "items": order_details.get("items", []),
            "delivery_address": order_details.get("delivery_address", ""),
            "special_instructions": order_details.get("special_instructions", ""),
            "customer_name": order_details.get("customer_name", ""),
            "raw_input": raw_data
        }
        
    async def enrich_customer_data(self, order: Dict) -> Dict:
        """Enrich the order with additional customer data from WhatsApp."""
        try:
            customer_id = order["customer_id"]
            # Get customer profile information from WhatsApp
            customer_data = await self._get_whatsapp_customer_data(customer_id)
            
            if customer_data:
                order["customer_profile"] = customer_data
                
            return order
            
        except Exception as e:
            logger.error(f"Error enriching customer data: {str(e)}")
            return order
            
    async def _get_whatsapp_customer_data(self, customer_id: str) -> Optional[Dict]:
        """Get customer data from WhatsApp API."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                url = f"https://graph.facebook.com/v12.0/{customer_id}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to get customer data. Status: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting customer data: {str(e)}")
            return None 