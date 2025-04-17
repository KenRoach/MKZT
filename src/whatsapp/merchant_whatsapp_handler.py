from typing import Dict, Any
from src.merchant.merchant_dashboard_handler import MerchantDashboardHandler
from twilio.rest import Client
import os
from src.merchant.advanced_analytics_system import AnalyticsType

class MerchantWhatsAppHandler:
    def __init__(self):
        self.merchant_dashboard = MerchantDashboardHandler()
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
    async def process_merchant_message(self, message_data: Dict[str, Any]) -> None:
        """Process merchant WhatsApp messages"""
        try:
            if "credentials" in message_data:
                # Handle login
                response = await self.merchant_dashboard.authenticate_merchant(
                    message_data["credentials"]
                )
            else:
                # Process merchant input
                response = await self.merchant_dashboard.process_merchant_input(
                    message_data["merchant_id"],
                    message_data["text"]
                )
                
            await self._send_message(
                message_data["phone_number"],
                response["message"]
            )
            
        except Exception as e:
            logger.error(f"Error processing merchant message: {str(e)}")
            await self._send_error_message(message_data["phone_number"])

    async def _send_message(self, to_number: str, message: str) -> None:
        """Send WhatsApp message to merchant"""
        try:
            self.twilio_client.messages.create(
                body=message,
                from_=f"whatsapp:{self.whatsapp_number}",
                to=f"whatsapp:{to_number}"
            )
        except Exception as e:
            logger.error(f"Error sending merchant message: {str(e)}")

    async def _send_error_message(self, to_number: str) -> None:
        """Send error message to merchant"""
        try:
            self.twilio_client.messages.create(
                body="Sorry, there was an error processing your request. Please try again later.",
                from_=f"whatsapp:{self.whatsapp_number}",
                to=f"whatsapp:{to_number}"
            )
        except Exception as e:
            logger.error(f"Error sending error message: {str(e)}")

# Example advanced analytics
analytics_result = await analytics_system.generate_advanced_analytics(
    merchant_id="rolling_sushi_01",
    analysis_type=AnalyticsType.SALES
)

# Example price optimization
pricing_result = await analytics_system.optimize_pricing(
    merchant_id="rolling_sushi_01",
    product_id="california_roll"
)

# Example customer segmentation
segmentation_result = await analytics_system.segment_customers(
    merchant_id="rolling_sushi_01"
)

# Example inventory prediction
inventory_result = await analytics_system.predict_inventory_needs(
    merchant_id="rolling_sushi_01",
    forecast_period=14  # 2 weeks forecast
) 