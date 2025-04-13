import os
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import aiohttp
from src.utils.twilio_client import twilio_client
from src.utils.instagram_client import instagram_client
from src.utils.yappy_client import yappy_client
from src.data.crm_repository import CRMRepository

logger = logging.getLogger(__name__)

class MessagingService:
    """Unified messaging service for handling communications across multiple channels"""
    
    def __init__(self):
        self.crm_repository = CRMRepository()
        self.twilio_client = twilio_client
        self.instagram_client = instagram_client
        self.yappy_client = yappy_client
        
    async def send_message(
        self,
        recipient_id: str,
        recipient_type: str,
        message: str,
        channel: str = "whatsapp",
        media_url: Optional[str] = None,
        buttons: Optional[List[Dict[str, str]]] = None,
        payment_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a message to a recipient through the specified channel"""
        try:
            # Get recipient contact info
            recipient = await self._get_recipient(recipient_id, recipient_type)
            if not recipient:
                raise ValueError(f"Recipient not found: {recipient_id} ({recipient_type})")
                
            # Format message based on channel
            formatted_message = self._format_message(message, channel, buttons, payment_link)
            
            # Send message through appropriate channel
            if channel == "whatsapp":
                return await self._send_whatsapp(recipient["phone_number"], formatted_message, media_url)
            elif channel == "sms":
                return await this._send_sms(recipient["phone_number"], formatted_message)
            elif channel == "instagram":
                return await this._send_instagram(recipient["instagram_id"], formatted_message, media_url)
            else:
                raise ValueError(f"Unsupported channel: {channel}")
                
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise
            
    async def send_order_confirmation(
        self,
        order_id: str,
        channel: str = "whatsapp"
    ) -> Dict[str, Any]:
        """Send order confirmation to all stakeholders"""
        try:
            # Get order details
            order = await this.crm_repository.get_order_by_id(order_id)
            if not order:
                raise ValueError(f"Order not found: {order_id}")
                
            # Get stakeholder details
            customer = await this.crm_repository.get_customer_by_id(order["customer_id"])
            merchant = await this.crm_repository.get_merchant_by_id(order["merchant_id"])
            driver = await this.crm_repository.get_driver_by_id(order["driver_id"]) if order.get("driver_id") else None
            
            # Generate order confirmation message
            customer_message = this._generate_order_confirmation_message(order, "customer")
            merchant_message = this._generate_order_confirmation_message(order, "merchant")
            driver_message = this._generate_order_confirmation_message(order, "driver") if driver else None
            
            # Send messages to all stakeholders
            results = {
                "customer": await this.send_message(
                    customer["id"],
                    "customer",
                    customer_message,
                    channel
                ),
                "merchant": await this.send_message(
                    merchant["id"],
                    "merchant",
                    merchant_message,
                    channel
                )
            }
            
            if driver:
                results["driver"] = await this.send_message(
                    driver["id"],
                    "driver",
                    driver_message,
                    channel
                )
                
            return {
                "status": "success",
                "message": "Order confirmation sent to all stakeholders",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error sending order confirmation: {str(e)}")
            raise
            
    async def send_payment_request(
        self,
        order_id: str,
        amount: float,
        channel: str = "whatsapp"
    ) -> Dict[str, Any]:
        """Send payment request to customer"""
        try:
            # Get order details
            order = await this.crm_repository.get_order_by_id(order_id)
            if not order:
                raise ValueError(f"Order not found: {order_id}")
                
            # Get customer details
            customer = await this.crm_repository.get_customer_by_id(order["customer_id"])
            
            # Generate payment link
            payment_link = await this.yappy_client.create_payment_link(
                amount=amount,
                description=f"Order #{order_id}",
                customer_name=customer.get("name", "Customer"),
                customer_email=customer.get("email"),
                customer_phone=customer.get("phone_number")
            )
            
            # Generate payment request message
            payment_message = this._generate_payment_request_message(order, amount, payment_link)
            
            # Send payment request
            return await this.send_message(
                customer["id"],
                "customer",
                payment_message,
                channel,
                payment_link=payment_link
            )
            
        except Exception as e:
            logger.error(f"Error sending payment request: {str(e)}")
            raise
            
    async def send_order_status_update(
        self,
        order_id: str,
        status: str,
        channel: str = "whatsapp"
    ) -> Dict[str, Any]:
        """Send order status update to all stakeholders"""
        try:
            # Get order details
            order = await this.crm_repository.get_order_by_id(order_id)
            if not order:
                raise ValueError(f"Order not found: {order_id}")
                
            # Get stakeholder details
            customer = await this.crm_repository.get_customer_by_id(order["customer_id"])
            merchant = await this.crm_repository.get_merchant_by_id(order["merchant_id"])
            driver = await this.crm_repository.get_driver_by_id(order["driver_id"]) if order.get("driver_id") else None
            
            # Generate status update message
            customer_message = this._generate_status_update_message(order, status, "customer")
            merchant_message = this._generate_status_update_message(order, status, "merchant")
            driver_message = this._generate_status_update_message(order, status, "driver") if driver else None
            
            # Send messages to all stakeholders
            results = {
                "customer": await this.send_message(
                    customer["id"],
                    "customer",
                    customer_message,
                    channel
                ),
                "merchant": await this.send_message(
                    merchant["id"],
                    "merchant",
                    merchant_message,
                    channel
                )
            }
            
            if driver:
                results["driver"] = await this.send_message(
                    driver["id"],
                    "driver",
                    driver_message,
                    channel
                )
                
            return {
                "status": "success",
                "message": f"Order status update ({status}) sent to all stakeholders",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error sending order status update: {str(e)}")
            raise
            
    async def send_driver_assignment(
        self,
        order_id: str,
        driver_id: str,
        channel: str = "whatsapp"
    ) -> Dict[str, Any]:
        """Send driver assignment notification"""
        try:
            # Get order and driver details
            order = await this.crm_repository.get_order_by_id(order_id)
            driver = await this.crm_repository.get_driver_by_id(driver_id)
            merchant = await this.crm_repository.get_merchant_by_id(order["merchant_id"])
            
            if not order or not driver:
                raise ValueError(f"Order or driver not found: {order_id}, {driver_id}")
                
            # Generate driver assignment message
            driver_message = this._generate_driver_assignment_message(order, driver)
            merchant_message = this._generate_merchant_driver_notification(order, driver)
            
            # Send messages
            results = {
                "driver": await this.send_message(
                    driver["id"],
                    "driver",
                    driver_message,
                    channel
                ),
                "merchant": await this.send_message(
                    merchant["id"],
                    "merchant",
                    merchant_message,
                    channel
                )
            }
            
            return {
                "status": "success",
                "message": "Driver assignment notification sent",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error sending driver assignment: {str(e)}")
            raise
            
    async def send_delivery_confirmation(
        self,
        order_id: str,
        channel: str = "whatsapp"
    ) -> Dict[str, Any]:
        """Send delivery confirmation to customer and merchant"""
        try:
            # Get order details
            order = await this.crm_repository.get_order_by_id(order_id)
            if not order:
                raise ValueError(f"Order not found: {order_id}")
                
            # Get stakeholder details
            customer = await this.crm_repository.get_customer_by_id(order["customer_id"])
            merchant = await this.crm_repository.get_merchant_by_id(order["merchant_id"])
            
            # Generate delivery confirmation message
            customer_message = this._generate_delivery_confirmation_message(order, "customer")
            merchant_message = this._generate_delivery_confirmation_message(order, "merchant")
            
            # Send messages
            results = {
                "customer": await this.send_message(
                    customer["id"],
                    "customer",
                    customer_message,
                    channel
                ),
                "merchant": await this.send_message(
                    merchant["id"],
                    "merchant",
                    merchant_message,
                    channel
                )
            }
            
            return {
                "status": "success",
                "message": "Delivery confirmation sent",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error sending delivery confirmation: {str(e)}")
            raise
            
    async def send_rating_request(
        self,
        order_id: str,
        channel: str = "whatsapp"
    ) -> Dict[str, Any]:
        """Send rating request to customer"""
        try:
            # Get order details
            order = await this.crm_repository.get_order_by_id(order_id)
            if not order:
                raise ValueError(f"Order not found: {order_id}")
                
            # Get customer details
            customer = await this.crm_repository.get_customer_by_id(order["customer_id"])
            
            # Generate rating request message
            rating_message = this._generate_rating_request_message(order)
            
            # Create rating buttons
            rating_buttons = [
                {"text": "⭐", "value": "1"},
                {"text": "⭐⭐", "value": "2"},
                {"text": "⭐⭐⭐", "value": "3"},
                {"text": "⭐⭐⭐⭐", "value": "4"},
                {"text": "⭐⭐⭐⭐⭐", "value": "5"}
            ]
            
            # Send rating request
            return await this.send_message(
                customer["id"],
                "customer",
                rating_message,
                channel,
                buttons=rating_buttons
            )
            
        except Exception as e:
            logger.error(f"Error sending rating request: {str(e)}")
            raise
            
    # Helper methods
    async def _get_recipient(self, recipient_id: str, recipient_type: str) -> Dict[str, Any]:
        """Get recipient details based on type and ID"""
        if recipient_type == "customer":
            return await this.crm_repository.get_customer_by_id(recipient_id)
        elif recipient_type == "merchant":
            return await this.crm_repository.get_merchant_by_id(recipient_id)
        elif recipient_type == "driver":
            return await this.crm_repository.get_driver_by_id(recipient_id)
        else:
            raise ValueError(f"Unsupported recipient type: {recipient_type}")
            
    async def _send_whatsapp(self, phone_number: str, message: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        """Send WhatsApp message"""
        return await this.twilio_client.send_whatsapp_message(
            to=phone_number,
            message=message,
            media_url=media_url
        )
        
    async def _send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS message"""
        return await this.twilio_client.send_sms(
            to=phone_number,
            message=message
        )
        
    async def _send_instagram(self, instagram_id: str, message: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        """Send Instagram message"""
        return await this.instagram_client.send_direct_message(
            to=instagram_id,
            message=message,
            media_url=media_url
        )
        
    def _format_message(self, message: str, channel: str, buttons: Optional[List[Dict[str, str]]] = None, payment_link: Optional[str] = None) -> str:
        """Format message based on channel and content"""
        formatted_message = message
        
        # Add payment link if provided
        if payment_link:
            formatted_message += f"\n\nPayment Link: {payment_link}"
            
        # Add button instructions for WhatsApp
        if channel == "whatsapp" and buttons:
            formatted_message += "\n\nPlease select an option:"
            for i, button in enumerate(buttons, 1):
                formatted_message += f"\n{i}. {button['text']}"
                
        return formatted_message
        
    def _generate_order_confirmation_message(self, order: Dict[str, Any], recipient_type: str) -> str:
        """Generate order confirmation message based on recipient type"""
        order_id = order["id"]
        total_amount = order.get("total_amount", 0)
        
        if recipient_type == "customer":
            return (
                f"✅ Order Confirmed! #{order_id}\n\n"
                f"Thank you for your order. We've received your order and it's being prepared.\n\n"
                f"Order Total: ${total_amount:.2f}\n\n"
                f"You'll receive updates as your order progresses."
            )
        elif recipient_type == "merchant":
            return (
                f"🆕 New Order Received! #{order_id}\n\n"
                f"A new order has been placed and is ready for preparation.\n\n"
                f"Order Total: ${total_amount:.2f}\n\n"
                f"Please confirm when the order is ready for pickup."
            )
        elif recipient_type == "driver":
            return (
                f"🚚 New Delivery Assignment! #{order_id}\n\n"
                f"You've been assigned to deliver this order.\n\n"
                f"Pickup Location: {order.get('merchant_address', 'Merchant Location')}\n"
                f"Delivery Location: {order.get('delivery_address', 'Customer Location')}\n\n"
                f"Please confirm when you've picked up the order."
            )
        else:
            return f"Order #{order_id} has been confirmed. Total: ${total_amount:.2f}"
            
    def _generate_payment_request_message(self, order: Dict[str, Any], amount: float, payment_link: str) -> str:
        """Generate payment request message"""
        order_id = order["id"]
        
        return (
            f"💰 Payment Request for Order #{order_id}\n\n"
            f"Your order total is ${amount:.2f}\n\n"
            f"Please complete your payment using the link below:\n"
            f"{payment_link}\n\n"
            f"Once payment is confirmed, your order will be processed."
        )
        
    def _generate_status_update_message(self, order: Dict[str, Any], status: str, recipient_type: str) -> str:
        """Generate order status update message"""
        order_id = order["id"]
        
        status_emoji = {
            "pending": "⏳",
            "confirmed": "✅",
            "preparing": "👨‍🍳",
            "ready": "🔄",
            "picked_up": "🚚",
            "delivered": "🎉",
            "cancelled": "❌"
        }
        
        emoji = status_emoji.get(status.lower(), "📝")
        status_text = status.capitalize()
        
        if recipient_type == "customer":
            return (
                f"{emoji} Order #{order_id} Update: {status_text}\n\n"
                f"Your order status has been updated to: {status_text}\n\n"
                f"You'll receive another update when your order status changes again."
            )
        elif recipient_type == "merchant":
            return (
                f"{emoji} Order #{order_id} Update: {status_text}\n\n"
                f"The order status has been updated to: {status_text}\n\n"
                f"Please take appropriate action if needed."
            )
        elif recipient_type == "driver":
            return (
                f"{emoji} Order #{order_id} Update: {status_text}\n\n"
                f"The order status has been updated to: {status_text}\n\n"
                f"Please update your delivery status accordingly."
            )
        else:
            return f"Order #{order_id} status updated to: {status_text}"
            
    def _generate_driver_assignment_message(self, order: Dict[str, Any], driver: Dict[str, Any]) -> str:
        """Generate driver assignment message"""
        order_id = order["id"]
        driver_name = driver.get("name", "Driver")
        
        return (
            f"🚚 New Delivery Assignment! #{order_id}\n\n"
            f"Hello {driver_name},\n\n"
            f"You've been assigned to deliver this order.\n\n"
            f"Pickup Location: {order.get('merchant_address', 'Merchant Location')}\n"
            f"Delivery Location: {order.get('delivery_address', 'Customer Location')}\n\n"
            f"Please confirm when you've picked up the order by replying 'PICKUP #{order_id}'."
        )
        
    def _generate_merchant_driver_notification(self, order: Dict[str, Any], driver: Dict[str, Any]) -> str:
        """Generate merchant notification about driver assignment"""
        order_id = order["id"]
        driver_name = driver.get("name", "Driver")
        driver_phone = driver.get("phone_number", "N/A")
        
        return (
            f"🚚 Driver Assigned to Order #{order_id}\n\n"
            f"A driver has been assigned to deliver this order:\n\n"
            f"Driver: {driver_name}\n"
            f"Phone: {driver_phone}\n\n"
            f"The driver will arrive shortly to pick up the order."
        )
        
    def _generate_delivery_confirmation_message(self, order: Dict[str, Any], recipient_type: str) -> str:
        """Generate delivery confirmation message"""
        order_id = order["id"]
        
        if recipient_type == "customer":
            return (
                f"🎉 Order Delivered! #{order_id}\n\n"
                f"Your order has been successfully delivered.\n\n"
                f"Thank you for choosing our service! We hope you enjoy your order.\n\n"
                f"You'll receive a rating request shortly."
            )
        elif recipient_type == "merchant":
            return (
                f"✅ Order Delivered! #{order_id}\n\n"
                f"The order has been successfully delivered to the customer.\n\n"
                f"Thank you for partnering with us!"
            )
        else:
            return f"Order #{order_id} has been delivered."
            
    def _generate_rating_request_message(self, order: Dict[str, Any]) -> str:
        """Generate rating request message"""
        order_id = order["id"]
        
        return (
            f"⭐ Rate Your Order #{order_id}\n\n"
            f"How was your experience with this order?\n\n"
            f"Please rate from 1 to 5 stars by selecting an option below."
        )

# Create singleton instance
messaging_service = MessagingService() 