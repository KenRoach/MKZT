import os
from typing import Dict, Any, Optional
import logging
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from src.config.logger import setup_logging
from src.handlers.voice_order_handler import VoiceOrderHandler

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

class PhoneInputHandler:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_client = Client(self.account_sid, self.auth_token)
        self.voice_handler = VoiceOrderHandler()
        
    def get_initial_response(self) -> str:
        """Get the initial TwiML response for incoming calls."""
        response = VoiceResponse()
        
        # Add initial greeting
        response.say("Welcome to our voice ordering system. Please state your order clearly after the beep.")
        
        # Add a pause
        response.pause(length=1)
        
        # Start recording
        response.record(
            maxLength="120",  # 2 minutes max
            action="/voice/process",  # Webhook to process the recording
            transcribe=True,  # Enable Twilio transcription
            transcribeCallback="/voice/transcription"  # Webhook for transcription
        )
        
        return str(response)
        
    async def process_recording(self, recording_url: str, transcription: Optional[str] = None) -> Optional[Dict]:
        """Process a voice recording and convert it to an order."""
        try:
            if transcription:
                # Use the Twilio transcription if available
                order_details = await self.voice_handler._extract_order_details(transcription)
            else:
                # Use Google Speech-to-Text if no transcription is available
                order_details = await self.voice_handler.process_voice_message(recording_url, "phone")
                
            if order_details and await self.voice_handler.validate_order(order_details):
                return self._format_order(order_details, recording_url)
                
            return None
            
        except Exception as e:
            logger.error(f"Error processing phone recording: {str(e)}")
            return None
            
    def get_confirmation_response(self, order_details: Dict) -> str:
        """Get TwiML response to confirm the order details."""
        response = VoiceResponse()
        
        # Read back the order details
        confirmation_text = self._generate_confirmation_text(order_details)
        response.say(confirmation_text)
        
        # Gather confirmation input
        gather = Gather(num_digits=1, action="/voice/confirm")
        gather.say("Press 1 to confirm your order, or 2 to cancel and try again.")
        response.append(gather)
        
        return str(response)
        
    def _generate_confirmation_text(self, order_details: Dict) -> str:
        """Generate confirmation text from order details."""
        text = "I've received your order. Here's what I understood: "
        
        # Add items
        if order_details.get("items"):
            text += "You ordered "
            for item in order_details["items"]:
                text += f"{item.get('quantity', 1)} {item.get('name', '')}. "
                
        # Add delivery address
        if order_details.get("delivery_address"):
            text += f"To be delivered to {order_details['delivery_address']}. "
            
        # Add special instructions
        if order_details.get("special_instructions"):
            text += f"With special instructions: {order_details['special_instructions']}. "
            
        return text
        
    def _format_order(self, order_details: Dict, recording_url: str) -> Dict:
        """Format the order details into a standardized structure."""
        return {
            "customer_id": order_details.get("customer_name", "phone_customer"),
            "order_source": "phone",
            "recording_url": recording_url,
            "items": order_details.get("items", []),
            "delivery_address": order_details.get("delivery_address", ""),
            "special_instructions": order_details.get("special_instructions", ""),
            "customer_name": order_details.get("customer_name", ""),
            "phone_number": order_details.get("phone_number", ""),
            "status": "pending_confirmation"
        }
        
    async def enrich_customer_data(self, order: Dict) -> Dict:
        """Enrich the order with additional customer data from phone records."""
        try:
            phone_number = order.get("phone_number")
            if phone_number:
                # Look up previous orders or customer profile
                customer_data = await self._get_customer_data(phone_number)
                if customer_data:
                    order["customer_profile"] = customer_data
                    
            return order
            
        except Exception as e:
            logger.error(f"Error enriching customer data: {str(e)}")
            return order
            
    async def _get_customer_data(self, phone_number: str) -> Optional[Dict]:
        """Get customer data from phone number."""
        # This is a placeholder - implement your customer lookup logic here
        return None 