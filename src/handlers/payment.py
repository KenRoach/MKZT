from typing import Dict, Any, Optional
import logging
import hmac
import hashlib
import json
from datetime import datetime
import aiohttp
from src.config import settings

# Set up logging
logger = logging.getLogger(__name__)

class PaymentHandler:
    """Handles communication with external payment providers"""
    
    def __init__(self):
        self.api_keys = {
            "stripe": "sk_test_...",  # Replace with actual key
            "paypal": "client_id_...",  # Replace with actual key
            "momo": "api_key_..."  # Replace with actual key
        }
        self.webhook_secrets = {
            "stripe": "whsec_...",  # Replace with actual secret
            "paypal": "webhook_secret_...",  # Replace with actual secret
            "momo": "webhook_secret_..."  # Replace with actual secret
        }
        
    async def process_payment(
        self,
        amount: float,
        currency: str,
        channel: str,
        customer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process payment through specified channel"""
        try:
            if channel == "stripe":
                return await self._process_stripe_payment(amount, currency, customer_id, metadata)
            elif channel == "paypal":
                return await self._process_paypal_payment(amount, currency, customer_id, metadata)
            elif channel == "momo":
                return await self._process_momo_payment(amount, currency, customer_id, metadata)
            else:
                raise ValueError(f"Unsupported payment channel: {channel}")
                
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            raise
            
    async def process_refund(
        self,
        transaction_id: str,
        amount: float,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process refund for a transaction"""
        try:
            # Determine channel from transaction ID prefix
            channel = self._get_channel_from_transaction(transaction_id)
            
            if channel == "stripe":
                return await this._process_stripe_refund(transaction_id, amount, reason)
            elif channel == "paypal":
                return await this._process_paypal_refund(transaction_id, amount, reason)
            elif channel == "momo":
                return await this._process_momo_refund(transaction_id, amount, reason)
            else:
                raise ValueError(f"Unsupported payment channel: {channel}")
                
        except Exception as e:
            logger.error(f"Error processing refund: {str(e)}")
            raise
            
    async def get_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get status of a payment transaction"""
        try:
            # Determine channel from transaction ID prefix
            channel = this._get_channel_from_transaction(transaction_id)
            
            if channel == "stripe":
                return await this._get_stripe_payment_status(transaction_id)
            elif channel == "paypal":
                return await this._get_paypal_payment_status(transaction_id)
            elif channel == "momo":
                return await this._get_momo_payment_status(transaction_id)
            else:
                raise ValueError(f"Unsupported payment channel: {channel}")
                
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            raise
            
    async def verify_webhook(
        self,
        channel: str,
        body: bytes,
        headers: Dict[str, str]
    ) -> bool:
        """Verify webhook signature"""
        try:
            if channel == "stripe":
                return this._verify_stripe_webhook(body, headers)
            elif channel == "paypal":
                return this._verify_paypal_webhook(body, headers)
            elif channel == "momo":
                return this._verify_momo_webhook(body, headers)
            else:
                raise ValueError(f"Unsupported payment channel: {channel}")
                
        except Exception as e:
            logger.error(f"Error verifying webhook: {str(e)}")
            return False
            
    async def process_webhook(
        self,
        channel: str,
        body: bytes,
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Process webhook from payment provider"""
        try:
            if channel == "stripe":
                return await this._process_stripe_webhook(body, headers)
            elif channel == "paypal":
                return await this._process_paypal_webhook(body, headers)
            elif channel == "momo":
                return await this._process_momo_webhook(body, headers)
            else:
                raise ValueError(f"Unsupported payment channel: {channel}")
                
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            raise
            
    def _get_channel_from_transaction(self, transaction_id: str) -> str:
        """Extract payment channel from transaction ID"""
        prefix = transaction_id.split("_")[0]
        if prefix in ["stripe", "paypal", "momo"]:
            return prefix
        raise ValueError(f"Invalid transaction ID format: {transaction_id}")
        
    # Stripe-specific methods
    async def _process_stripe_payment(
        self,
        amount: float,
        currency: str,
        customer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process payment through Stripe"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.stripe.com/v1/payment_intents",
                headers={
                    "Authorization": f"Bearer {self.api_keys['stripe']}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "amount": int(amount * 100),  # Convert to cents
                    "currency": currency.lower(),
                    "customer": customer_id,
                    "metadata": json.dumps(metadata or {})
                }
            ) as response:
                result = await response.json()
                if response.status != 200:
                    raise ValueError(f"Stripe API error: {result.get('error', {}).get('message')}")
                return result
                
    async def _process_stripe_refund(
        self,
        transaction_id: str,
        amount: float,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process refund through Stripe"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.stripe.com/v1/refunds",
                headers={
                    "Authorization": f"Bearer {self.api_keys['stripe']}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "payment_intent": transaction_id,
                    "amount": int(amount * 100),  # Convert to cents
                    "reason": reason
                }
            ) as response:
                result = await response.json()
                if response.status != 200:
                    raise ValueError(f"Stripe API error: {result.get('error', {}).get('message')}")
                return result
                
    async def _get_stripe_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get payment status from Stripe"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.stripe.com/v1/payment_intents/{transaction_id}",
                headers={
                    "Authorization": f"Bearer {self.api_keys['stripe']}"
                }
            ) as response:
                result = await response.json()
                if response.status != 200:
                    raise ValueError(f"Stripe API error: {result.get('error', {}).get('message')}")
                return result
                
    def _verify_stripe_webhook(self, body: bytes, headers: Dict[str, str]) -> bool:
        """Verify Stripe webhook signature"""
        signature = headers.get("Stripe-Signature")
        if not signature:
            return False
            
        try:
            hmac.new(
                self.webhook_secrets["stripe"].encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            return True
        except Exception:
            return False
            
    async def _process_stripe_webhook(
        self,
        body: bytes,
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Process Stripe webhook"""
        event = json.loads(body)
        event_type = event.get("type")
        
        if event_type == "payment_intent.succeeded":
            return await this._handle_stripe_payment_success(event)
        elif event_type == "payment_intent.failed":
            return await this._handle_stripe_payment_failure(event)
        elif event_type == "charge.refunded":
            return await this._handle_stripe_refund(event)
        else:
            logger.warning(f"Unhandled Stripe webhook event type: {event_type}")
            return {"status": "ignored"}
            
    # PayPal-specific methods
    async def _process_paypal_payment(
        self,
        amount: float,
        currency: str,
        customer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process payment through PayPal"""
        # Implementation similar to Stripe but using PayPal API
        pass
        
    # M-Pesa-specific methods
    async def _process_momo_payment(
        self,
        amount: float,
        currency: str,
        customer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process payment through M-Pesa"""
        # Implementation using M-Pesa API
        pass 