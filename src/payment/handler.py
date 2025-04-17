import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.utils.logger import logger, RequestContext, log_execution_time

# Load environment variables
load_dotenv()

class PaymentHandler:
    def __init__(self):
        self.api_key = os.getenv("PAYMENT_API_KEY")
        self.api_url = os.getenv("PAYMENT_BASE_URL")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.logger = logger
    
    @log_execution_time(logger)
    async def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment"""
        try:
            url = f"{self.api_url}/payments"
            
            self.logger.info(
                "Creating payment",
                amount=payment_data.get("amount"),
                currency=payment_data.get("currency"),
                payment_method=payment_data.get("payment_method")
            )
            
            response = requests.post(url, headers=self.headers, json=payment_data)
            response.raise_for_status()
            
            payment_id = response.json().get("id")
            self.logger.info(
                "Payment created successfully",
                payment_id=payment_id
            )
            
            return {
                "status": "success",
                "payment_id": payment_id,
                "message": "Payment created successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error creating payment",
                error=str(e),
                amount=payment_data.get("amount"),
                currency=payment_data.get("currency")
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment status"""
        try:
            url = f"{self.api_url}/payments/{payment_id}"
            
            self.logger.info(
                "Fetching payment status",
                payment_id=payment_id
            )
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            status = response.json().get("status")
            self.logger.info(
                "Payment status fetched successfully",
                payment_id=payment_id,
                status=status
            )
            
            return {
                "status": "success",
                "payment_status": status
            }
            
        except Exception as e:
            self.logger.exception(
                "Error getting payment status",
                error=str(e),
                payment_id=payment_id
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def refund_payment(self, payment_id: str, refund_data: Dict[str, Any]) -> Dict[str, Any]:
        """Refund a payment"""
        try:
            url = f"{self.api_url}/payments/{payment_id}/refund"
            
            self.logger.info(
                "Processing refund",
                payment_id=payment_id,
                refund_amount=refund_data.get("amount")
            )
            
            response = requests.post(url, headers=self.headers, json=refund_data)
            response.raise_for_status()
            
            refund_id = response.json().get("id")
            self.logger.info(
                "Refund processed successfully",
                payment_id=payment_id,
                refund_id=refund_id
            )
            
            return {
                "status": "success",
                "refund_id": refund_id,
                "message": "Refund processed successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error processing refund",
                error=str(e),
                payment_id=payment_id
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Get payment details"""
        try:
            url = f"{self.api_url}/payments/{payment_id}"
            
            self.logger.info(
                "Fetching payment details",
                payment_id=payment_id
            )
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            payment = response.json()
            self.logger.info(
                "Payment details fetched successfully",
                payment_id=payment_id
            )
            
            return {
                "status": "success",
                "payment": payment
            }
            
        except Exception as e:
            self.logger.exception(
                "Error getting payment details",
                error=str(e),
                payment_id=payment_id
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def list_payments(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List payments with optional filters"""
        try:
            url = f"{self.api_url}/payments"
            
            self.logger.info(
                "Fetching payment list",
                filters=params
            )
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            payments = response.json().get("payments", [])
            self.logger.info(
                "Payment list fetched successfully",
                count=len(payments)
            )
            
            return {
                "status": "success",
                "payments": payments
            }
            
        except Exception as e:
            self.logger.exception(
                "Error listing payments",
                error=str(e)
            )
            return {
                "status": "error",
                "message": str(e),
                "payments": []
            }
    
    @log_execution_time(logger)
    async def cancel_payment(self, payment_id: str) -> Dict[str, Any]:
        """Cancel a payment"""
        try:
            url = f"{self.api_url}/payments/{payment_id}/cancel"
            
            self.logger.info(
                "Cancelling payment",
                payment_id=payment_id
            )
            
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            
            self.logger.info(
                "Payment cancelled successfully",
                payment_id=payment_id
            )
            
            return {
                "status": "success",
                "message": "Payment cancelled successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error cancelling payment",
                error=str(e),
                payment_id=payment_id
            )
            return {
                "status": "error",
                "message": str(e)
            } 