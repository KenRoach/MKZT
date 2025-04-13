from typing import Dict, Any
from .base import InputChannelHandler
from src.utils.logger import logger

class ThirdPartyInputHandler(InputChannelHandler):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def process_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process third-party app input and convert to standard format"""
        try:
            # Extract order information from third-party data
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
                    "partner_id": data.get("partner_id"),
                    "integration_id": data.get("integration_id"),
                    "original_format": data.get("original_format"),
                    "partner_specific_data": data.get("partner_data", {})
                }
            }
            
            return self.standardize_order_format(order)
            
        except Exception as e:
            logger.error(f"Error processing third-party input: {str(e)}")
            raise
    
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate third-party input data"""
        required_fields = ["order", "customer_id", "partner_id"]
        return all(field in data for field in required_fields)
    
    async def enrich_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Enrich order with customer data from CRM"""
        # Implement CRM integration here
        return {
            "customer_id": customer_id,
            "channel": "third_party",
            "preferences": {},
            "history": {}
        } 