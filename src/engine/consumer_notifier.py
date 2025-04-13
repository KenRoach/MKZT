from typing import Dict, Any, List, Optional
from datetime import datetime
from src.utils.logger import logger
from src.config.languages import LanguageConfig
from src.services.database import DatabaseService
from src.services.notifications import NotificationService
from src.services.queue import MessageQueue

class ConsumerNotifier:
    def __init__(self):
        this.db = DatabaseService()
        this.notification_service = NotificationService()
        this.message_queue = MessageQueue()
        this.notification_channels = {
            "whatsapp": this.notification_service.send_whatsapp_notification,
            "email": this.notification_service.send_email_notification,
            "sms": this.notification_service.send_sms_notification,
            "instagram": this.notification_service.send_instagram_notification,
            "voice": this.notification_service.send_voice_notification
        }
    
    async def start(self):
        """Start the notification system"""
        await this.message_queue.start()
    
    async def stop(self):
        """Stop the notification system"""
        await this.message_queue.stop()
    
    async def send_order_confirmation(self, order: Dict[str, Any]):
        """Send order confirmation to consumer"""
        try:
            # Get consumer's preferred notification channels and language
            preferences = await this._get_notification_preferences(order["customer_id"])
            channels = preferences.get("channels", ["whatsapp", "email"])
            language = preferences.get("language", LanguageConfig.DEFAULT_LANGUAGE)
            
            # Create confirmation message
            message = await this._create_confirmation_message(order, language)
            
            # Queue notifications for each preferred channel
            for channel in channels:
                if channel in this.notification_channels:
                    await this.message_queue.enqueue_notification({
                        "id": f"confirmation_{order['order_id']}_{channel}",
                        "order": order,
                        "message": message,
                        "channel": channel
                    })
            
        except Exception as e:
            logger.error(f"Error sending order confirmation: {str(e)}")
            raise
    
    async def send_order_update(self, order_id: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Send order status update to consumer"""
        try:
            # Get order details
            order = await this._get_order_details(order_id)
            if not order:
                raise ValueError(f"Order not found: {order_id}")
            
            # Get consumer's preferred notification channels and language
            preferences = await this._get_notification_preferences(order["customer_id"])
            channels = preferences.get("channels", ["whatsapp", "email"])
            language = preferences.get("language", LanguageConfig.DEFAULT_LANGUAGE)
            
            # Create update message
            message = await this._create_update_message(order, status, details, language)
            
            # Queue notifications for each preferred channel
            for channel in channels:
                if channel in this.notification_channels:
                    await this.message_queue.enqueue_notification({
                        "id": f"update_{order_id}_{channel}",
                        "order": order,
                        "message": message,
                        "channel": channel
                    })
            
        except Exception as e:
            logger.error(f"Error sending order update: {str(e)}")
            raise
    
    async def send_tracking_update(self, order_id: str, tracking_info: Dict[str, Any]):
        """Send tracking information to consumer"""
        try:
            # Get order details
            order = await this._get_order_details(order_id)
            if not order:
                raise ValueError(f"Order not found: {order_id}")
            
            # Get consumer's preferred notification channels and language
            preferences = await this._get_notification_preferences(order["customer_id"])
            channels = preferences.get("channels", ["whatsapp", "email"])
            language = preferences.get("language", LanguageConfig.DEFAULT_LANGUAGE)
            
            # Create tracking message
            message = await this._create_tracking_message(order, tracking_info, language)
            
            # Queue notifications for each preferred channel
            for channel in channels:
                if channel in this.notification_channels:
                    await this.message_queue.enqueue_notification({
                        "id": f"tracking_{order_id}_{channel}",
                        "order": order,
                        "message": message,
                        "channel": channel
                    })
            
        except Exception as e:
            logger.error(f"Error sending tracking update: {str(e)}")
            raise
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get notification queue statistics"""
        return await this.message_queue.get_queue_stats()
    
    async def _get_notification_preferences(self, customer_id: str) -> Dict[str, Any]:
        """Get consumer's notification preferences"""
        return await this.db.get_customer_preferences(customer_id)
    
    async def _get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get order details from database"""
        return await this.db.get_order_details(order_id)
    
    async def _create_confirmation_message(self, order: Dict[str, Any], language: str) -> str:
        """Create order confirmation message"""
        messages = LanguageConfig.MESSAGES[language]["order_confirmation"]
        currency = LanguageConfig.format_currency(order.get("total_amount", 0), language)
        
        return f"""
{messages['title']}
------------------
{messages['order_id']}: {order.get("order_id")}
{messages['items']}: {", ".join(item["name"] for item in order.get("items", []))}
{messages['total_amount']}: {currency}
{messages['delivery_address']}: {order.get("delivery_address", "Pickup")}
{messages['estimated_delivery']}: {order.get("estimated_delivery_time", "To be determined")}

{messages['thank_you']}
"""
    
    async def _create_update_message(self, order: Dict[str, Any], status: str, details: Optional[Dict[str, Any]] = None, language: str = "en") -> str:
        """Create order update message"""
        messages = LanguageConfig.MESSAGES[language]["order_update"]
        
        message = f"""
{messages['title']}
-----------
{messages['order_id']}: {order.get("order_id")}
{messages['status']}: {status}
"""
        if details:
            message += f"{messages['details']}: {details}\n"
        
        return message
    
    async def _create_tracking_message(self, order: Dict[str, Any], tracking_info: Dict[str, Any], language: str = "en") -> str:
        """Create tracking information message"""
        messages = LanguageConfig.MESSAGES[language]["tracking_update"]
        
        return f"""
{messages['title']}
-------------------
{messages['order_id']}: {order.get("order_id")}
{messages['status']}: {tracking_info.get("status")}
{messages['driver_location']}: {tracking_info.get("driver_location")}
{messages['estimated_delivery']}: {tracking_info.get("estimated_delivery_time")}
""" 