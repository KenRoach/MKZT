from typing import Dict, Any
from src.handlers.multilingual_order_handler import MultilingualOrderHandler
from twilio.rest import Client
import os

class MultilingualWhatsAppHandler:
    def __init__(self):
        self.order_handler = MultilingualOrderHandler()
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
    async def process_order_message(self, message_data: Dict[str, Any]) -> None:
        """Process incoming WhatsApp order message"""
        try:
            # Detect language ( 