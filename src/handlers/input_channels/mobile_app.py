from typing import Dict, Any
from .base import InputChannelHandler
from src.utils.logger import logger

class MobileAppInputHandler(InputChannelHandler):
    async def process_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process mobile app input and convert to standard format"""
        try:
            # Extract order information from mobile app data
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
                    "app_version": data.get("app_version"),
                    "device_id": data.get("device_id"),
                    "platform": data.get("platform"),
                    "location": data.get("location", {})
                }
            }
            
            return self.standardize_order_format(order)
            
        except Exception as e:
            logger.error(f"Error processing mobile app input: {str(e)}")
            raise
    
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate mobile app input data"""
        required_fields = ["order", "customer_id", "device_id", "platform"]
        return all(field in data for field in required_fields)
    
    async def enrich_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Enrich order with customer data from CRM"""
        # Implement CRM integration here
        return {
            "customer_id": customer_id,
            "channel": "mobile_app",
            "preferences": {},
            "history": {}
        } 