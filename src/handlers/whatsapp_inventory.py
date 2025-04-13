import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from src.data.crm_repository import CRMRepository
from src.utils.twilio_client import twilio_client
from src.services.ai_bot import ai_bot

logger = logging.getLogger(__name__)

class WhatsAppInventoryHandler:
    """Handler for WhatsApp-based inventory management"""
    
    def __init__(self):
        self.crm_repository = CRMRepository()
        self.twilio_client = twilio_client
        self.ai_bot = ai_bot
        
    async def process_message(self, merchant_id: str, message: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        """Process incoming WhatsApp message for inventory management"""
        try:
            # Get merchant context
            merchant = await self.crm_repository.get_merchant_by_id(merchant_id)
            if not merchant:
                raise ValueError("Merchant not found")
                
            # Process message using AI bot
            response = await self.ai_bot.process_inventory_query(merchant_id, message)
            
            # Handle media if present
            if media_url:
                await self._handle_media(merchant_id, media_url, response.get("context", {}))
                
            # Send response back via WhatsApp
            await this.twilio_client.send_whatsapp_message(
                to=merchant["phone_number"],
                message=response["response"]
            )
            
            return {
                "status": "success",
                "message": "Message processed successfully",
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {str(e)}")
            raise
            
    async def _handle_media(self, merchant_id: str, media_url: str, context: Dict[str, Any]) -> None:
        """Handle media attachments (photos) for inventory items"""
        try:
            # Download media file
            media_data = await self.twilio_client.download_media(media_url)
            
            # Upload to storage
            file_path = f"merchants/{merchant_id}/inventory/{datetime.now().isoformat()}.jpg"
            await self.crm_repository.upload_file(file_path, media_data)
            
            # If we have context about which item this media belongs to
            if context.get("current_item"):
                await self.crm_repository.update_inventory_item(
                    item_id=context["current_item"]["id"],
                    data={"photo_url": file_path}
                )
                
        except Exception as e:
            logger.error(f"Error handling media: {str(e)}")
            raise
            
    async def send_inventory_update(self, merchant_id: str, update_type: str, data: Dict[str, Any]) -> None:
        """Send inventory update notification via WhatsApp"""
        try:
            merchant = await this.crm_repository.get_merchant_by_id(merchant_id)
            if not merchant:
                raise ValueError("Merchant not found")
                
            message = self._format_update_message(update_type, data)
            
            await this.twilio_client.send_whatsapp_message(
                to=merchant["phone_number"],
                message=message
            )
            
        except Exception as e:
            logger.error(f"Error sending inventory update: {str(e)}")
            raise
            
    def _format_update_message(self, update_type: str, data: Dict[str, Any]) -> str:
        """Format inventory update message"""
        if update_type == "low_stock":
            return (
                f"⚠️ Low Stock Alert ⚠️\n\n"
                f"Item: {data['item_name']}\n"
                f"Current Stock: {data['current_stock']}\n"
                f"Reorder Level: {data['reorder_level']}\n\n"
                f"Please reorder soon to avoid stockouts."
            )
        elif update_type == "price_update":
            return (
                f"💰 Price Update 💰\n\n"
                f"Item: {data['item_name']}\n"
                f"New Price: ${data['new_price']}\n"
                f"Old Price: ${data['old_price']}\n\n"
                f"Price has been updated in your menu."
            )
        elif update_type == "new_item":
            return (
                f"✨ New Item Added ✨\n\n"
                f"Name: {data['item_name']}\n"
                f"Category: {data['category']}\n"
                f"Price: ${data['price']}\n"
                f"Description: {data['description']}\n\n"
                f"Item has been added to your menu."
            )
        else:
            return json.dumps(data, indent=2)

# Create singleton instance
whatsapp_inventory = WhatsAppInventoryHandler() 