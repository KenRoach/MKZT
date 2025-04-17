from typing import Dict, Any
from fastapi import Request
from src.handlers.restaurant_dashboard import RestaurantDashboardHandler
from src.handlers.driver_coordination import DriverCoordinationHandler
from src.ai.enhanced_chatbot import EnhancedChatbot
from src.utils.logger import logger

class EnhancedWhatsAppHandler:
    def __init__(self):
        self.customer_chatbot = EnhancedChatbot()
        self.restaurant_handler = RestaurantDashboardHandler()
        self.driver_handler = DriverCoordinationHandler()
        
    async def process_webhook(self, request: Request) -> Dict[str, Any]:
        """Process incoming webhook from WhatsApp"""
        try:
            data = await request.json()
            
            # Process messages
            if "entry" in data and data["entry"]:
                for entry in data["entry"]:
                    if "changes" in entry and entry["changes"]:
                        for change in entry["changes"]:
                            if "value" in change and "messages" in change["value"]:
                                for message in change["value"]["messages"]:
                                    await self._route_message(message)
            
            return {"status": "success"}
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _route_message(self, message: Dict[str, Any]) -> None:
        """Route message to appropriate handler"""
        try:
            phone_number = message.get("from")
            message_text = message.get("text", {}).get("body", "")
            
            if not phone_number or not message_text:
                return
            
            # Determine user type
            user_type = await self._identify_user_type(phone_number)
            
            # Route to appropriate handler
            if user_type == "restaurant":
                response = await self.restaurant_handler.process_message(
                    restaurant_id=phone_number,
                    message=message_text
                )
            elif user_type == "driver":
                response = await self.driver_handler.process_driver_message(
                    driver_id=phone_number,
                    message=message_text
                )
            else:
                response = await self.customer_chatbot.process_message(
                    user_id=phone_number,
                    message=message_text
                )
            
            # Send response
            await self.send_message(
                to_number=phone_number,
                message=response["message"],
                quick_replies=response.get("quick_replies", [])
            )
            
        except Exception as e:
            logger.error(f"Error routing message: {str(e)}")
    
    async def _identify_user_type(self, phone_number: str) -> str:
        """Identify user type based on phone number"""
        # This would typically check against your database
        # Simplified version for demonstration
        if phone_number.startswith("+507"):
            return "restaurant"
        elif phone_number.startswith("+508"):
            return "driver"
        return "customer" 