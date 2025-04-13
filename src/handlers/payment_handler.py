import os
import hmac
import hashlib
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential
import stripe
import paypalrestsdk

from src.config import settings

logger = logging.getLogger(__name__)

class PaymentHandler:
    """Handler for managing payments across different channels"""
    
    def __init__(self):
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        self.paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.paypal_secret = os.getenv("PAYPAL_SECRET")
        self.paypal_webhook_id = os.getenv("PAYPAL_WEBHOOK_ID")
        
        # Initialize Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Initialize PayPal
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_MODE,
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET
        })
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_payment(
        self,
        order_id: str,
        amount: float,
        currency: str,
        channel: str,
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process payment through specified channel"""
        try:
            if channel == "stripe":
                return await self._process_stripe_payment(
                    order_id=order_id,
                    amount=amount,
                    currency=currency,
                    customer_id=customer_id,
                    metadata=metadata
                )
            elif channel == "paypal":
                return await self._process_paypal_payment(
                    order_id=order_id,
                    amount=amount,
                    currency=currency,
                    customer_id=customer_id,
                    metadata=metadata
                )
            else:
                raise ValueError(f"Unsupported payment channel: {channel}")
                
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            raise
            
    async def verify_payment_webhook(
        self,
        channel: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> bool:
        """Verify webhook signature"""
        try:
            if channel == "stripe":
                return self._verify_stripe_webhook(payload, signature)
            elif channel == "paypal":
                return self._verify_paypal_webhook(payload, signature)
            else:
                raise ValueError(f"Unsupported payment channel: {channel}")
                
        except Exception as e:
            logger.error(f"Error verifying webhook: {str(e)}")
            return False
            
    async def handle_payment_webhook(
        self,
        channel: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle payment webhook"""
        try:
            if channel == "stripe":
                return await self._handle_stripe_webhook(payload)
            elif channel == "paypal":
                return await self._handle_paypal_webhook(payload)
            else:
                raise ValueError(f"Unsupported payment channel: {channel}")
                
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            raise
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_refund(
        self,
        transaction_id: str,
        amount: float,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process refund for a transaction"""
        try:
            # Determine channel from transaction ID prefix
            if transaction_id.startswith("pi_"):
                return await self._process_stripe_refund(transaction_id, amount, reason)
            elif transaction_id.startswith("PAY-"):
                return await self._process_paypal_refund(transaction_id, amount, reason)
            else:
                raise ValueError(f"Invalid transaction ID format: {transaction_id}")
                
        except Exception as e:
            logger.error(f"Error processing refund: {str(e)}")
            raise
            
    async def _process_stripe_payment(
        self,
        order_id: str,
        amount: float,
        currency: str,
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process payment through Stripe"""
        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                customer=customer_id,
                metadata={
                    "order_id": order_id,
                    **(metadata or {})
                }
            )
            
            return {
                "transaction_id": intent.id,
                "status": intent.status,
                "client_secret": intent.client_secret,
                "amount": amount,
                "currency": currency,
                "payment_method": "stripe",
                "created_at": datetime.fromtimestamp(intent.created).isoformat()
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment error: {str(e)}")
            raise ValueError(f"Payment processing failed: {str(e)}")
            
    def _verify_stripe_webhook(
        self,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> bool:
        """Verify Stripe webhook signature"""
        try:
            if not signature:
                return False
                
            stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature,
                secret=self.stripe_webhook_secret
            )
            return True
            
        except Exception as e:
            logger.error(f"Error verifying Stripe webhook: {str(e)}")
            return False
            
    async def _handle_stripe_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Stripe webhook"""
        try:
            event_type = payload.get("type")
            data = payload.get("data", {}).get("object", {})
            
            if event_type == "payment_intent.succeeded":
                return {
                    "status": "completed",
                    "transaction_id": data.get("id"),
                    "amount": data.get("amount", 0) / 100,  # Convert from cents
                    "currency": data.get("currency"),
                    "payment_method": "stripe",
                    "metadata": data
                }
            elif event_type == "payment_intent.payment_failed":
                return {
                    "status": "failed",
                    "transaction_id": data.get("id"),
                    "error": data.get("last_payment_error", {}).get("message"),
                    "payment_method": "stripe",
                    "metadata": data
                }
            else:
                return {
                    "status": "unknown",
                    "event_type": event_type,
                    "metadata": payload
                }
                
        except Exception as e:
            logger.error(f"Error handling Stripe webhook: {str(e)}")
            raise
            
    async def _process_stripe_refund(
        self,
        transaction_id: str,
        amount: float,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process refund through Stripe"""
        try:
            # Create refund
            refund = stripe.Refund.create(
                payment_intent=transaction_id,
                amount=int(amount * 100),  # Convert to cents
                reason=reason
            )
            
            return {
                "refund_id": refund.id,
                "status": refund.status,
                "amount": amount,
                "reason": reason,
                "created_at": datetime.fromtimestamp(int(refund.created)).isoformat()
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe refund error: {str(e)}")
            raise ValueError(f"Refund processing failed: {str(e)}")
            
    async def _process_paypal_payment(
        self,
        order_id: str,
        amount: float,
        currency: str,
        customer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process payment through PayPal"""
        try:
            # Create PayPal payment
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": currency
                    },
                    "description": f"Order {order_id}"
                }],
                "redirect_urls": {
                    "return_url": f"{settings.API_BASE_URL}/payment/success",
                    "cancel_url": f"{settings.API_BASE_URL}/payment/cancel"
                }
            })
            
            if payment.create():
                return {
                    "transaction_id": payment.id,
                    "status": "pending",
                    "approval_url": next(link.href for link in payment.links if link.rel == "approval_url"),
                    "amount": amount,
                    "currency": currency,
                    "payment_method": "paypal",
                    "created_at": datetime.utcnow().isoformat()
                }
            else:
                raise ValueError(f"PayPal payment creation failed: {payment.error}")
                
        except Exception as e:
            logger.error(f"PayPal payment error: {str(e)}")
            raise ValueError(f"Payment processing failed: {str(e)}")
            
    def _verify_paypal_webhook(
        self,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> bool:
        """Verify PayPal webhook signature"""
        try:
            # PayPal webhook verification logic here
            # This would depend on PayPal's webhook verification method
            return True
        except Exception:
            return False
            
    async def _handle_paypal_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PayPal webhook"""
        try:
            event_type = payload.get("event_type")
            resource = payload.get("resource", {})
            
            if event_type == "PAYMENT.CAPTURE.COMPLETED":
                return {
                    "status": "completed",
                    "transaction_id": resource.get("id"),
                    "amount": float(resource.get("amount", {}).get("total", 0)),
                    "currency": resource.get("amount", {}).get("currency"),
                    "payment_method": "paypal",
                    "metadata": {
                        "order_id": resource.get("custom_id")
                    }
                }
            elif event_type == "PAYMENT.CAPTURE.DENIED":
                return {
                    "status": "failed",
                    "transaction_id": resource.get("id"),
                    "error": resource.get("status_details", {}).get("reason"),
                    "payment_method": "paypal",
                    "metadata": resource
                }
            else:
                return {
                    "status": "unknown",
                    "event_type": event_type,
                    "metadata": payload
                }
                
        except Exception as e:
            logger.error(f"Error handling PayPal webhook: {str(e)}")
            raise
            
    async def _process_paypal_refund(
        self,
        transaction_id: str,
        amount: float,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process refund through PayPal"""
        try:
            # Get sale ID from payment
            payment = paypalrestsdk.Payment.find(transaction_id)
            sale_id = payment.transactions[0].related_resources[0].sale.id
            
            # Create refund
            sale = paypalrestsdk.Sale.find(sale_id)
            refund = sale.refund({
                "amount": {
                    "total": str(amount),
                    "currency": payment.transactions[0].amount.currency
                }
            })
            
            if refund.success():
                return {
                    "refund_id": refund.id,
                    "status": "completed",
                    "amount": amount,
                    "reason": reason,
                    "created_at": datetime.utcnow().isoformat()
                }
            else:
                raise ValueError(f"PayPal refund failed: {refund.error}")
                
        except Exception as e:
            logger.error(f"PayPal refund error: {str(e)}")
            raise ValueError(f"Refund processing failed: {str(e)}")

# Create singleton instance
payment_handler = PaymentHandler() 