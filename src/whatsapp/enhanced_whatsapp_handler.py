from typing import Dict, Any, List
from src.handlers.enhanced_multilingual_handler import EnhancedMultilingualHandler, AdvancedOrderTracking
from twilio.rest import Client
import asyncio
import json
import os

class EnhancedWhatsAppHandler:
    def __init__(self):
        self.multilingual_handler = EnhancedMultilingualHandler()
        self.order_tracking = AdvancedOrderTracking()
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
    async def process_message(self, message_data: Dict[str, Any]) -> None:
        """Process incoming WhatsApp message with enhanced features"""
        try:
            # Detect message language
            message_text = message_data.get("text", "")
            language = await self.multilingual_handler.detect_language(message_text)
            
            # Process based on message type
            if message_data.get("type") == "order_new":
                await self._handle_new_order(message_data, language)
            elif message_data.get("type") == "order_confirmation":
                await self._handle_order_confirmation(message_data, language)
            elif message_data.get("type") == "driver_update":
                await self._handle_driver_update(message_data, language)
            elif message_data.get("type") == "delivery_confirmation":
                await self._handle_delivery_confirmation(message_data, language)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            error_messages = {
                "en": "Sorry, there was an error processing your message. Please try again.",
                "es": "Lo sentimos, hubo un error procesando tu mensaje. Por favor intenta nuevamente.",
                "pt": "Desculpe, houve um erro ao processar sua mensagem. Por favor, tente novamente."
            }
            await self._send_message(
                message_data["phone_number"],
                error_messages.get(language, error_messages["en"])
            )

    async def _handle_new_order(self, data: Dict[str, Any], language: str) -> None:
        """Handle new order with enhanced features"""
        # Generate rich message for new order
        message = await self.multilingual_handler.generate_rich_message(
            "new_order",
            {
                "restaurant": data["restaurant"],
                "order_id": data["order_id"],
                "items": self._format_items(data["items"], language),
                "payment_method": data["payment_method"],
                "address": data["delivery_address"]
            },
            language
        )
        
        # Update tracking
        await self.order_tracking.update_order_status(
            data["order_id"],
            "received",
            {"restaurant": data["restaurant"]}
        )
        
        # Send message
        await self._send_rich_message(data["phone_number"], message)

    async def _handle_driver_update(self, data: Dict[str, Any], language: str) -> None:
        """Handle driver updates with location tracking"""
        message = await self.multilingual_handler.generate_rich_message(
            "driver_assigned",
            {
                "driver_name": data["driver_name"],
                "order_id": data["order_id"],
                "restaurant": data["restaurant"],
                "driver_id": data["driver_id"],
                "location": {
                    "lat": data["location"]["lat"],
                    "lng": data["location"]["lng"],
                    "name": data["location"]["name"],
                    "address": data["location"]["address"]
                }
            },
            language
        )
        
        # Update tracking
        await self.order_tracking.update_order_status(
            data["order_id"],
            "in_delivery",
            {
                "driver": data["driver_name"],
                "location": data["location"]
            }
        )
        
        await self._send_rich_message(data["phone_number"], message)

    async def _send_rich_message(self, to_number: str, message: Dict[str, Any]) -> None:
        """Send rich WhatsApp message with media and interactive elements"""
        try:
            message_params = {
                "from_": f"whatsapp:{self.whatsapp_number}",
                "to": f"whatsapp:{to_number}",
                "body": message["text"]
            }
            
            # Add media if present
            if "media" in message:
                message_params["media_url"] = [message["media"]["url"]]
            
            # Add location if present
            if any(comp["type"] == "location" for comp in message.get("components", [])):
                location = next(
                    comp["location"] for comp in message["components"] 
                    if comp["type"] == "location"
                )
                message_params["persistent_action"] = [
                    f"geo:{location['latitude']},{location['longitude']}"
                ]
            
            self.twilio_client.messages.create(**message_params)
            
        except Exception as e:
            logger.error(f"Error sending rich message: {str(e)}")

    def _format_items(self, items: List[Dict[str, Any]], language: str) -> str:
        """Format order items in the appropriate language"""
        item_templates = {
            "en": "• {quantity}x {name} ({restaurant})",
            "es": "• {quantity}x {name} ({restaurant})",
            "pt": "• {quantity}x {name} ({restaurant})"
        }
        
        template = item_templates.get(language, item_templates["en"])
        return "\n".join([
            template.format(**item) for item in items
        ]) 