from typing import Dict, Any, Optional, List
from src.handlers.input_channels.whatsapp import WhatsAppInputHandler
from src.handlers.input_channels.web import WebInputHandler
from src.handlers.input_channels.mobile import MobileInputHandler
from src.handlers.input_channels.third_party import ThirdPartyInputHandler
from src.handlers.input_channels.instagram import InstagramInputHandler
from src.handlers.input_channels.sms import SMSInputHandler
from src.engine.decision_engine import DecisionEngine
from src.engine.driver_coordinator import DriverCoordinator
from src.engine.consumer_notifier import ConsumerNotifier
from src.engine.merchant_dashboard import MerchantDashboard
from src.utils.logger import logger
from src.utils.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime

class OrderManager:
    def __init__(self, api_key: str):
        # Initialize input handlers
        self.input_handlers = {
            "whatsapp": WhatsAppInputHandler(api_key),
            "web": WebInputHandler(api_key),
            "mobile": MobileInputHandler(api_key),
            "third_party": ThirdPartyInputHandler(api_key),
            "instagram": InstagramInputHandler(api_key),
            "sms": SMSInputHandler(api_key)
        }
        
        # Initialize core components
        self.decision_engine = DecisionEngine()
        self.driver_coordinator = DriverCoordinator()
        self.consumer_notifier = ConsumerNotifier()
        self.merchant_dashboard = MerchantDashboard()
    
    async def process_order(self, data: Dict[str, Any], channel: str) -> Dict[str, Any]:
        """Process an order from any channel"""
        try:
            # Get the appropriate input handler
            handler = self.input_handlers.get(channel)
            if not handler:
                raise ValueError(f"Unsupported channel: {channel}")
            
            # Validate input
            if not await handler.validate_input(data):
                raise ValueError("Invalid input data")
            
            # Process input
            order = await handler.process_input(data)
            
            # Enrich customer data
            order = await handler.enrich_customer_data(order)
            
            # Apply business logic
            order = await self._apply_business_logic(order)
            
            # Process through decision engine
            order = await self.decision_engine.process_order(order)
            
            # Assign to driver
            order = await self.driver_coordinator.assign_order(order)
            
            # Send confirmation to consumer
            await self.consumer_notifier.send_order_confirmation(order)
            
            # Save to database
            await self._save_order(order)
            
            # Update merchant dashboard
            await self._update_merchant_dashboard(order)
            
            return order
            
        except Exception as e:
            logger.error(f"Error processing order: {str(e)}")
            raise
    
    async def _apply_business_logic(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business logic to order"""
        try:
            # Implement business logic
            # This is a placeholder for the actual implementation
            return order
        except Exception as e:
            logger.error(f"Error applying business logic: {str(e)}")
            raise
    
    async def _save_order(self, order: Dict[str, Any]) -> None:
        """Save order to database"""
        try:
            # Implement database save
            # This is a placeholder for the actual implementation
            pass
        except Exception as e:
            logger.error(f"Error saving order: {str(e)}")
            raise
    
    async def _update_merchant_dashboard(self, order: Dict[str, Any]) -> None:
        """Update merchant dashboard with new order"""
        try:
            # Update performance metrics
            await self.merchant_dashboard.update_performance_metrics(order)
            
            # Check for inventory alerts
            await self.merchant_dashboard.check_inventory_alerts(order)
            
        except Exception as e:
            logger.error(f"Error updating merchant dashboard: {str(e)}")
            raise
    
    async def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """Update order status"""
        try:
            # Update order status
            order = await self._get_order(order_id)
            order["status"] = status
            
            # Notify consumer
            await self.consumer_notifier.send_order_update(order)
            
            # Update driver status if needed
            if status in ["delivered", "cancelled"]:
                await self.driver_coordinator.update_driver_status(order["driver_id"], "available")
            
            # Save updated order
            await self._save_order(order)
            
            # Update merchant dashboard
            await self._update_merchant_dashboard(order)
            
            return order
            
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            raise
    
    async def get_order_tracking(self, order_id: str) -> Dict[str, Any]:
        """Get order tracking information"""
        try:
            order = await self._get_order(order_id)
            
            # Get driver location
            driver_location = await self.driver_coordinator.get_driver_location(order["driver_id"])
            
            return {
                "order_id": order_id,
                "status": order["status"],
                "driver_location": driver_location,
                "estimated_delivery": order.get("estimated_delivery"),
                "last_update": order.get("last_update")
            }
            
        except Exception as e:
            logger.error(f"Error getting order tracking: {str(e)}")
            raise
    
    async def _get_order(self, order_id: str) -> Dict[str, Any]:
        """Get order from database"""
        try:
            # Implement database get
            # This is a placeholder for the actual implementation
            return {
                "order_id": order_id,
                "status": "pending",
                "driver_id": "driver123",
                "estimated_delivery": "2024-03-20T15:00:00Z",
                "last_update": "2024-03-20T14:00:00Z"
            }
        except Exception as e:
            logger.error(f"Error getting order: {str(e)}")
            raise
    
    async def get_merchant_metrics(self, merchant_id: str, time_range: str = "today") -> Dict[str, Any]:
        """Get merchant performance metrics"""
        try:
            return await self.merchant_dashboard.get_performance_metrics(merchant_id, time_range)
        except Exception as e:
            logger.error(f"Error getting merchant metrics: {str(e)}")
            raise
    
    async def get_merchant_analytics(self, merchant_id: str, time_range: str = "today") -> Dict[str, Any]:
        """Get merchant order analytics"""
        try:
            return await self.merchant_dashboard.get_order_analytics(merchant_id, time_range)
        except Exception as e:
            logger.error(f"Error getting merchant analytics: {str(e)}")
            raise
    
    async def get_merchant_insights(self, merchant_id: str) -> Dict[str, Any]:
        """Get merchant customer insights"""
        try:
            return await self.merchant_dashboard.get_customer_insights(merchant_id)
        except Exception as e:
            logger.error(f"Error getting merchant insights: {str(e)}")
            raise
    
    async def get_merchant_alerts(self, merchant_id: str) -> Dict[str, Any]:
        """Get merchant alerts"""
        try:
            return await self.merchant_dashboard.get_inventory_alerts(merchant_id)
        except Exception as e:
            logger.error(f"Error getting merchant alerts: {str(e)}")
            raise 