import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiohttp
from src.utils.logger import logger
from src.services.merchant_registry import merchant_registry

class MerchantAppIntegration:
    """Service for integrating with food entrepreneurs' apps"""
    
    def __init__(self):
        """Initialize the merchant app integration service"""
        self.api_key = os.getenv("MERCHANT_APP_API_KEY")
        self.base_url = os.getenv("MERCHANT_APP_BASE_URL")
        self.timeout = 30  # seconds
        self.max_retries = 3
    
    async def send_order_to_merchant(self, merchant_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send order to merchant's app
        
        Args:
            merchant_id: Merchant ID
            order_data: Order data
            
        Returns:
            Dictionary with sending results
        """
        try:
            # Get merchant details
            merchant = await merchant_registry.get_merchant_by_id(merchant_id)
            if not merchant:
                raise ValueError(f"Merchant not found: {merchant_id}")
            
            # Prepare order data
            formatted_order = await self._format_order_for_merchant(order_data, merchant)
            
            # Send to merchant's app
            async with aiohttp.ClientSession() as session:
                for attempt in range(self.max_retries):
                    try:
                        async with session.post(
                            f"{self.base_url}/merchants/{merchant_id}/orders",
                            json=formatted_order,
                            headers={
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json"
                            },
                            timeout=self.timeout
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                return {
                                    "success": True,
                                    "merchant_order_id": result.get("merchant_order_id"),
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            else:
                                error_text = await response.text()
                                logger.warning(
                                    f"Failed to send order to merchant (attempt {attempt + 1}): "
                                    f"Status {response.status}, Error: {error_text}"
                                )
                                if attempt < self.max_retries - 1:
                                    continue
                                else:
                                    raise Exception(f"Failed to send order: {error_text}")
                    except Exception as e:
                        if attempt < self.max_retries - 1:
                            continue
                        else:
                            raise
            
            # This should never be reached due to the raise in the loop
            return {"success": False, "error": "Max retries exceeded"}
            
        except Exception as e:
            logger.error(f"Error sending order to merchant: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_order_status(self, merchant_id: str, order_id: str) -> Dict[str, Any]:
        """
        Get order status from merchant's app
        
        Args:
            merchant_id: Merchant ID
            order_id: Order ID
            
        Returns:
            Dictionary with order status
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/merchants/{merchant_id}/orders/{order_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "status": result.get("status"),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"Failed to get order status: {error_text}")
                        
        except Exception as e:
            logger.error(f"Error getting order status: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def update_order_status(self, merchant_id: str, order_id: str, 
                                 status_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update order status in merchant's app
        
        Args:
            merchant_id: Merchant ID
            order_id: Order ID
            status_data: New status details
            
        Returns:
            Dictionary with update results
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    f"{self.base_url}/merchants/{merchant_id}/orders/{order_id}",
                    json=status_data,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "status": result.get("status"),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"Failed to update order status: {error_text}")
                        
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _format_order_for_merchant(self, order_data: Dict[str, Any], 
                                        merchant: Dict[str, Any]) -> Dict[str, Any]:
        """Format order data according to merchant's requirements"""
        try:
            # Get merchant's menu for item validation
            menu = await merchant_registry.get_merchant_menu(merchant["id"])
            
            # Format order items
            formatted_items = []
            for item in order_data.get("items", []):
                menu_item = next(
                    (m for m in menu if m["id"] == item["id"]), 
                    None
                )
                if menu_item:
                    formatted_items.append({
                        "id": item["id"],
                        "name": menu_item["name"],
                        "quantity": item["quantity"],
                        "price": menu_item["price"],
                        "special_instructions": item.get("special_instructions", "")
                    })
            
            # Format order
            return {
                "order_id": order_data["id"],
                "customer": {
                    "id": order_data["customer_id"],
                    "name": order_data.get("customer_name", ""),
                    "phone": order_data.get("customer_phone", ""),
                    "address": order_data.get("delivery_address", {})
                },
                "items": formatted_items,
                "total_amount": order_data.get("total_amount", 0),
                "payment_method": order_data.get("payment_method", ""),
                "delivery_time": order_data.get("delivery_time", ""),
                "notes": order_data.get("notes", "")
            }
            
        except Exception as e:
            logger.error(f"Error formatting order: {str(e)}")
            raise

# Create a singleton instance
merchant_app_integration = MerchantAppIntegration() 