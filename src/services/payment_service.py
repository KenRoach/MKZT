import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.data.crm_repository import crm_repository
from src.handlers.payment_handler import payment_handler

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.crm_repository = crm_repository
        self.payment_handler = payment_handler
        
    async def process_order_payment(
        self,
        order_id: str,
        amount: float,
        currency: str,
        channel: str,
        customer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a payment for an order"""
        try:
            # Get order details
            order = await self.crm_repository.get_order_by_id(order_id)
            if not order:
                raise ValueError(f"Order {order_id} not found")
                
            # Verify order amount matches payment amount
            if float(order["total_amount"]) != amount:
                raise ValueError("Payment amount does not match order amount")
                
            # Process payment through handler
            payment_result = await self.payment_handler.process_payment(
                order_id=order_id,
                amount=amount,
                currency=currency,
                channel=channel,
                customer_id=customer_id,
                metadata=metadata
            )
            
            # Update order payment status
            await self.crm_repository.update_order_payment_status(
                order_id=order_id,
                status=payment_result["status"],
                transaction_id=payment_result["transaction_id"],
                payment_method=channel,
                payment_details=payment_result
            )
            
            return payment_result
            
        except Exception as e:
            logger.error(f"Error processing order payment: {str(e)}")
            raise
            
    async def handle_payment_webhook(
        self,
        channel: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle payment webhook"""
        try:
            # Verify webhook signature
            if not await self.payment_handler.verify_payment_webhook(channel, payload, signature):
                raise ValueError("Invalid webhook signature")
                
            # Handle webhook through handler
            webhook_result = await self.payment_handler.handle_payment_webhook(channel, payload)
            
            # Update payment status in CRM if transaction ID is provided
            if transaction_id := webhook_result.get("transaction_id"):
                payment = await self.crm_repository.get_payment_by_transaction_id(transaction_id)
                if payment:
                    await self.crm_repository.update_order_payment(
                        payment_id=payment["id"],
                        status=webhook_result.get("status", "pending"),
                        metadata={
                            "webhook_response": webhook_result,
                            **(payment.get("metadata") or {})
                        }
                    )
                    
                    # Update order status if payment is completed
                    if webhook_result.get("status") == "completed":
                        await self.crm_repository.update_order_status(
                            order_id=payment["order_id"],
                            status="paid",
                            metadata={"payment_completed_at": datetime.utcnow().isoformat()}
                        )
                        
            return webhook_result
            
        except Exception as e:
            logger.error(f"Error handling payment webhook: {str(e)}")
            raise
            
    async def get_payment_status(self, order_id: str) -> Dict[str, Any]:
        """Get payment status for an order"""
        try:
            # Get payment details from CRM
            payment = await self.crm_repository.get_order_payment_details(order_id)
            if not payment:
                raise ValueError(f"Payment not found for order {order_id}")
                
            return payment
            
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            raise
            
    async def process_refund(
        self,
        transaction_id: str,
        amount: float,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a refund"""
        try:
            # Get payment details
            payment = await self.crm_repository.get_payment_by_transaction_id(transaction_id)
            if not payment:
                raise ValueError(f"Payment {transaction_id} not found")
                
            # Process refund through handler
            refund_result = await self.payment_handler.process_refund(
                transaction_id=transaction_id,
                amount=amount,
                reason=reason
            )
            
            # Update payment status
            await self.crm_repository.update_payment_status(
                transaction_id=transaction_id,
                status="refunded",
                refund_details=refund_result
            )
            
            return refund_result
            
        except Exception as e:
            logger.error(f"Error processing refund: {str(e)}")
            raise

# Create singleton instance
payment_service = PaymentService() 