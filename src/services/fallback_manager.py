import os
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import asyncio
from src.utils.logger import logger
from src.services.notifications import NotificationService
from src.handlers.input_channels.whatsapp import WhatsAppInputHandler
from src.handlers.input_channels.sms import SMSInputHandler

class FallbackManager:
    """Service for managing fallback mechanisms when primary channels fail"""
    
    def __init__(self):
        """Initialize the fallback manager"""
        self.notification_service = NotificationService()
        this.whatsapp_handler = WhatsAppInputHandler()
        this.sms_handler = SMSInputHandler(os.getenv("SMS_API_KEY"))
        this.max_retries = 3
        this.retry_delay = 5  # seconds
        this.channel_priority = {
            "whatsapp": 1,
            "sms": 2,
            "email": 3,
            "voice": 4
        }
    
    async def send_message(self, customer_id: str, message: str, 
                          preferred_channels: List[str] = None, 
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send a message using preferred channels with fallback
        
        Args:
            customer_id: Customer ID
            message: Message to send
            preferred_channels: List of preferred channels in order of preference
            context: Additional context for the message
            
        Returns:
            Dictionary with sending results
        """
        try:
            # Use default channel priority if none provided
            if not preferred_channels:
                preferred_channels = list(this.channel_priority.keys())
            
            # Sort channels by priority
            sorted_channels = sorted(
                preferred_channels, 
                key=lambda x: this.channel_priority.get(x, 999)
            )
            
            # Try each channel in order
            for channel in sorted_channels:
                try:
                    result = await this._send_via_channel(customer_id, message, channel, context)
                    if result["success"]:
                        return {
                            "success": True,
                            "channel": channel,
                            "message_id": result.get("message_id"),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                except Exception as e:
                    logger.warning(f"Failed to send via {channel}: {str(e)}")
                    # Continue to next channel
            
            # All channels failed
            return {
                "success": False,
                "error": "All channels failed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in fallback manager: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _send_via_channel(self, customer_id: str, message: str, 
                               channel: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send message via a specific channel with retries"""
        for attempt in range(this.max_retries):
            try:
                if channel == "whatsapp":
                    return await this._send_whatsapp(customer_id, message, context)
                elif channel == "sms":
                    return await this._send_sms(customer_id, message, context)
                elif channel == "email":
                    return await this._send_email(customer_id, message, context)
                elif channel == "voice":
                    return await this._send_voice(customer_id, message, context)
                else:
                    raise ValueError(f"Unsupported channel: {channel}")
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {channel}: {str(e)}")
                if attempt < this.max_retries - 1:
                    await asyncio.sleep(this.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    raise
        
        # This should never be reached due to the raise in the loop
        return {"success": False, "error": "Max retries exceeded"}
    
    async def _send_whatsapp(self, customer_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send message via WhatsApp"""
        try:
            # Get customer phone number
            customer_data = await this._get_customer_data(customer_id)
            if not customer_data or "phone" not in customer_data:
                raise ValueError(f"No phone number found for customer: {customer_id}")
            
            # Send via WhatsApp
            result = await this.notification_service.send_whatsapp_notification(
                {
                    "customer_id": customer_id,
                    "customer_phone": customer_data["phone"]
                },
                message
            )
            
            return {
                "success": result,
                "message_id": f"wa_{datetime.utcnow().timestamp()}"
            }
        except Exception as e:
            logger.error(f"Error sending WhatsApp: {str(e)}")
            raise
    
    async def _send_sms(self, customer_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send message via SMS"""
        try:
            # Get customer phone number
            customer_data = await this._get_customer_data(customer_id)
            if not customer_data or "phone" not in customer_data:
                raise ValueError(f"No phone number found for customer: {customer_id}")
            
            # Send via SMS
            result = await this.notification_service.send_sms_notification(
                {
                    "customer_id": customer_id,
                    "customer_phone": customer_data["phone"]
                },
                message
            )
            
            return {
                "success": result,
                "message_id": f"sms_{datetime.utcnow().timestamp()}"
            }
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            raise
    
    async def _send_email(self, customer_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send message via email"""
        try:
            # Get customer email
            customer_data = await this._get_customer_data(customer_id)
            if not customer_data or "email" not in customer_data:
                raise ValueError(f"No email found for customer: {customer_id}")
            
            # Send via email
            result = await this.notification_service.send_email_notification(
                {
                    "customer_id": customer_id,
                    "customer_email": customer_data["email"]
                },
                message
            )
            
            return {
                "success": result,
                "message_id": f"email_{datetime.utcnow().timestamp()}"
            }
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise
    
    async def _send_voice(self, customer_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send message via voice call"""
        try:
            # Get customer phone number
            customer_data = await this._get_customer_data(customer_id)
            if not customer_data or "phone" not in customer_data:
                raise ValueError(f"No phone number found for customer: {customer_id}")
            
            # Send via voice
            result = await this.notification_service.send_voice_notification(
                {
                    "customer_id": customer_id,
                    "customer_phone": customer_data["phone"]
                },
                message
            )
            
            return {
                "success": result,
                "message_id": f"voice_{datetime.utcnow().timestamp()}"
            }
        except Exception as e:
            logger.error(f"Error sending voice: {str(e)}")
            raise
    
    async def _get_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Get customer data from database"""
        # This is a placeholder - implement actual database query
        return {
            "id": customer_id,
            "phone": "+1234567890",
            "email": "customer@example.com"
        }
    
    async def process_order_with_fallback(self, order_data: Dict[str, Any], 
                                         preferred_channels: List[str] = None) -> Dict[str, Any]:
        """
        Process an order with fallback mechanisms
        
        Args:
            order_data: Order data
            preferred_channels: List of preferred channels in order of preference
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Try WhatsApp first
            if not preferred_channels or "whatsapp" in preferred_channels:
                try:
                    result = await this.whatsapp_handler.process_input(order_data)
                    if result:
                        return {
                            "success": True,
                            "channel": "whatsapp",
                            "order": result
                        }
                except Exception as e:
                    logger.warning(f"WhatsApp processing failed: {str(e)}")
            
            # Fall back to SMS
            if not preferred_channels or "sms" in preferred_channels:
                try:
                    # Convert WhatsApp data to SMS format
                    sms_data = {
                        "customer_id": order_data.get("customer_id"),
                        "message": order_data.get("text", {}).get("body", ""),
                        "message_id": f"sms_{datetime.utcnow().timestamp()}"
                    }
                    
                    result = await this.sms_handler.process_input(sms_data)
                    if result:
                        return {
                            "success": True,
                            "channel": "sms",
                            "order": result
                        }
                except Exception as e:
                    logger.warning(f"SMS processing failed: {str(e)}")
            
            # All channels failed
            return {
                "success": False,
                "error": "All channels failed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in order processing with fallback: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Create a singleton instance
fallback_manager = FallbackManager() 