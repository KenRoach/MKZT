from typing import Dict, Any, Optional
import logging
from datetime import datetime
from src.handlers.payment import PaymentHandler
from src.data.crm_repository import CRMRepository

# Set up logging
logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, payment_handler: PaymentHandler, crm_repository: CRMRepository):
        """Initialize payment service"""
        self.payment_handler = payment_handler
        self.crm_repository = crm_repository
        
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
            order = await self.crm_repository.get_order(order_id)
            if not order:
                raise ValueError(f"Order {order_id} not found")
                
            # Validate amount
            if abs(order["total_amount"] - amount) > 0.01:  # Allow small floating point differences
                raise ValueError(f"Payment amount {amount} does not match order total {order['total_amount']}")
                
            # Process payment
            payment_result = await self.payment_handler.process_payment(
                amount=amount,
                currency=currency,
                channel=channel,
                customer_id=customer_id,
                metadata={
                    "order_id": order_id,
                    **(metadata or {})
                }
            )
            
            # Update order payment status
            await self.crm_repository.update_order_payment(
                order_id=order_id,
                payment_id=payment_result["transaction_id"],
                status=payment_result["status"],
                amount=payment_result["amount"],
                currency=payment_result["currency"],
                payment_method=payment_result["payment_method"],
                metadata=payment_result["metadata"]
            )
            
            return payment_result
            
        except Exception as e:
            logger.error(f"Error processing order payment: {str(e)}")
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
            payment = await self.crm_repository.get_payment(transaction_id)
            if not payment:
                raise ValueError(f"Payment {transaction_id} not found")
                
            # Validate refund amount
            if amount > payment["amount"]:
                raise ValueError(f"Refund amount {amount} cannot exceed payment amount {payment['amount']}")
                
            # Process refund
            refund_result = await self.payment_handler.process_refund(
                transaction_id=transaction_id,
                amount=amount,
                reason=reason
            )
            
            # Update payment status
            await self.crm_repository.update_payment_status(
                payment_id=transaction_id,
                status="refunded",
                refund_id=refund_result["refund_id"],
                refund_amount=refund_result["amount"],
                refund_reason=refund_result["reason"]
            )
            
            return refund_result
            
        except Exception as e:
            logger.error(f"Error processing refund: {str(e)}")
            raise
            
    async def get_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get payment status"""
        try:
            # Get payment status from provider
            status = await self.payment_handler.get_payment_status(transaction_id)
            
            # Update local payment status if different
            payment = await self.crm_repository.get_payment(transaction_id)
            if payment and payment["status"] != status["status"]:
                await self.crm_repository.update_payment_status(
                    payment_id=transaction_id,
                    status=status["status"]
                )
                
            return status
            
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            raise
            
    async def handle_webhook(
        self,
        channel: str,
        body: bytes,
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Handle payment webhook"""
        try:
            # Process webhook
            webhook_data = await self.payment_handler.process_webhook(channel, body, headers)
            
            # Update payment status if needed
            if webhook_data["transaction_id"]:
                await self.get_payment_status(webhook_data["transaction_id"])
                
            return webhook_data
            
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            raise
            
    async def handle_payment_success(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Handle successful payment redirect"""
        try:
            # Get payment details
            payment_id = params.get("payment_id")
            if not payment_id:
                raise ValueError("Missing payment ID")
                
            # Execute payment
            result = await this.payment_handler.execute_payment(payment_id)
            
            # Update payment status
            await this.crm_repository.update_payment_status(
                transaction_id=result["transaction_id"],
                status=result["status"],
                payment_details=result
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error handling payment success: {str(e)}")
            raise
            
    async def handle_payment_cancel(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Handle cancelled payment redirect"""
        try:
            # Get payment details
            payment_id = params.get("payment_id")
            if not payment_id:
                raise ValueError("Missing payment ID")
                
            # Cancel payment
            result = await this.payment_handler.cancel_payment(payment_id)
            
            # Update payment status
            await this.crm_repository.update_payment_status(
                transaction_id=result["transaction_id"],
                status="cancelled",
                payment_details=result
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error handling payment cancellation: {str(e)}")
            raise 