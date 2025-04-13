from typing import Dict, Any
from .base import InputChannelHandler
from src.utils.logger import logger

class WebAppInputHandler(InputChannelHandler):
    async def process_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process web app input and convert to standard format"""
        try:
            # Extract order information from web app data
            order_data = data.get("order", {})
            customer_id = data.get("customer_id")
            
            # Create standard order format
            order = {
                "order_id": order_data.get("order_id"),
                "customer_id": customer_id,
                "items": order_data.get("items", []),
                "total_amount": order_data.get("total_amount"),
                "status": order_data.get("status", "pending"),
                "metadata": {
                    "session_id": data.get("session_id"),
                    "browser_info": data.get("browser_info", {}),
                    "device_info": data.get("device_info", {})
                }
            }
            
            return self.standardize_order_format(order)
            
        except Exception as e:
            logger.error(f"Error processing web app input: {str(e)}")
            raise
    
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate web app input data"""
        required_fields = ["order", "customer_id"]
        return all(field in data for field in required_fields)
    
    async def enrich_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Enrich order with customer data from CRM"""
        # Implement CRM integration here
        return {
            "customer_id": customer_id,
            "channel": "web_app",
            "preferences": {},
            "history": {}
        } 