import os
import json
import requests
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from src.utils.message_handler import MessageHandler
from fastapi import Request
from sqlalchemy.orm import Session

from src.utils.logging import get_logger
from src.utils.monitoring import track_time, track_error

# Load environment variables
load_dotenv()

# Get logger
logger = get_logger("whatsapp")

class WhatsAppHandler:
    def __init__(self):
        """Initialize WhatsApp handler"""
        self.api_token = os.getenv("WHATSAPP_API_TOKEN")
        self.verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
        self.api_url = "https://graph.facebook.com/v17.0"
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.message_handler = MessageHandler()
        
        logger.info("WhatsApp handler initialized")
    
    @track_time("process_webhook")
    async def process_webhook(self, request: Request, db: Session) -> Dict[str, Any]:
        """Process incoming webhook from WhatsApp"""
        try:
            # Parse webhook data
            data = await request.json()
            logger.info(f"Webhook data received: {json.dumps(data)}")
            
            # Extract message data
            if "entry" in data and data["entry"]:
                for entry in data["entry"]:
                    if "changes" in entry and entry["changes"]:
                        for change in entry["changes"]:
                            if "value" in change and "messages" in change["value"]:
                                for message in change["value"]["messages"]:
                                    # Process message
                                    await self._process_message(message, db)
            
            return {"status": "success"}
        except Exception as e:
            error_msg = f"Error processing webhook: {str(e)}"
            logger.error(error_msg)
            track_error("webhook_processing", error_msg, {"data": str(data)})
            return {"status": "error", "message": error_msg}
    
    @track_time("process_message")
    async def _process_message(self, message: Dict[str, Any], db: Session) -> None:
        """Process a single message"""
        try:
            # Extract message details
            from_number = message.get("from")
            message_id = message.get("id")
            timestamp = message.get("timestamp")
            
            # Extract message content
            if "text" in message and "body" in message["text"]:
                content = message["text"]["body"]
            else:
                content = "Unsupported message type"
            
            logger.info(f"Processing message from {from_number}: {content}")
            
            # Process message with message handler
            response = await self.message_handler.process_message(
                phone_number=from_number,
                message=content,
                db=db
            )
            
            # Send response
            await self.send_message(from_number, response)
            
            logger.info(f"Message processed successfully: {message_id}")
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            track_error("message_processing", error_msg, {"message": str(message)})
    
    @track_time("send_message")
    async def send_message(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send a message to a WhatsApp number"""
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text",
                "text": {"body": message}
            }
            
            logger.info(f"Sending message to {to_number}: {message}")
            
            response = requests.post(url, headers=headers, json=data)
            response_data = response.json()
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully: {response_data.get('messages', [{}])[0].get('id')}")
                return {"status": "success", "message_id": response_data.get("messages", [{}])[0].get("id")}
            else:
                error_msg = f"Error sending message: {response_data.get('error', {}).get('message', 'Unknown error')}"
                logger.error(error_msg)
                track_error("message_sending", error_msg, {"to": to_number, "status_code": response.status_code})
                return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Error sending message: {str(e)}"
            logger.error(error_msg)
            track_error("message_sending", error_msg, {"to": to_number})
            return {"status": "error", "message": error_msg}
    
    @track_time("send_template_message")
    async def send_template_message(self, to_number: str, template_name: str, language_code: str = "en", components: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a template message to a WhatsApp number"""
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    }
                }
            }
            
            # Add components if provided
            if components:
                data["template"]["components"] = components
            
            logger.info(f"Sending template message to {to_number}: {template_name}")
            
            response = requests.post(url, headers=headers, json=data)
            response_data = response.json()
            
            if response.status_code == 200:
                logger.info(f"Template message sent successfully: {response_data.get('messages', [{}])[0].get('id')}")
                return {"status": "success", "message_id": response_data.get("messages", [{}])[0].get("id")}
            else:
                error_msg = f"Error sending template message: {response_data.get('error', {}).get('message', 'Unknown error')}"
                logger.error(error_msg)
                track_error("template_message_sending", error_msg, {"to": to_number, "template": template_name, "status_code": response.status_code})
                return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Error sending template message: {str(e)}"
            logger.error(error_msg)
            track_error("template_message_sending", error_msg, {"to": to_number, "template": template_name})
            return {"status": "error", "message": error_msg}
    
    def verify_webhook(self, mode: str, verify_token: str, challenge: str) -> Optional[str]:
        """Verify webhook subscription"""
        if mode == "subscribe" and verify_token == os.getenv("WHATSAPP_VERIFY_TOKEN"):
            return challenge
        return None 