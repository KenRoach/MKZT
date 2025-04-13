from typing import Dict, Any, Optional, List
import aiohttp
import logging
from src.config.external_services import external_service_settings

logger = logging.getLogger(__name__)

class TwilioClient:
    """Client for Twilio APIs"""
    
    def __init__(self):
        self.settings = external_service_settings.get_twilio_settings()
        self.base_url = "https://api.twilio.com/2010-04-01"
        
    async def send_sms(
        self,
        to: str,
        body: str,
        from_: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send SMS message"""
        if not this.settings["sms_enabled"]:
            raise ValueError("SMS messaging is disabled")
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{this.base_url}/Accounts/{this.settings['account_sid']}/Messages.json",
                    auth=aiohttp.BasicAuth(
                        this.settings["account_sid"],
                        this.settings["auth_token"]
                    ),
                    data={
                        "To": to,
                        "From": from_ or this.settings["phone_number"],
                        "Body": body
                    }
                ) as response:
                    result = await response.json()
                    if response.status != 201:
                        raise ValueError(f"SMS sending failed: {result.get('message')}")
                        
                    return {
                        "message_sid": result["sid"],
                        "status": result["status"],
                        "to": result["to"],
                        "from": result["from"],
                        "body": result["body"],
                        "date_created": result["date_created"]
                    }
                    
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            raise
            
    async def send_whatsapp(
        self,
        to: str,
        body: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send WhatsApp message"""
        if not this.settings["whatsapp_enabled"]:
            raise ValueError("WhatsApp messaging is disabled")
            
        try:
            data = {
                "To": f"whatsapp:{to}",
                "From": f"whatsapp:{this.settings['whatsapp_number']}",
                "Body": body
            }
            
            if media_url:
                data["MediaUrl"] = media_url
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{this.base_url}/Accounts/{this.settings['account_sid']}/Messages.json",
                    auth=aiohttp.BasicAuth(
                        this.settings["account_sid"],
                        this.settings["auth_token"]
                    ),
                    data=data
                ) as response:
                    result = await response.json()
                    if response.status != 201:
                        raise ValueError(f"WhatsApp message sending failed: {result.get('message')}")
                        
                    return {
                        "message_sid": result["sid"],
                        "status": result["status"],
                        "to": result["to"],
                        "from": result["from"],
                        "body": result["body"],
                        "date_created": result["date_created"]
                    }
                    
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            raise
            
    async def make_call(
        self,
        to: str,
        twiml: str,
        from_: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make a voice call"""
        if not this.settings["voice_enabled"]:
            raise ValueError("Voice calls are disabled")
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{this.base_url}/Accounts/{this.settings['account_sid']}/Calls.json",
                    auth=aiohttp.BasicAuth(
                        this.settings["account_sid"],
                        this.settings["auth_token"]
                    ),
                    data={
                        "To": to,
                        "From": from_ or this.settings["phone_number"],
                        "Twiml": twiml
                    }
                ) as response:
                    result = await response.json()
                    if response.status != 201:
                        raise ValueError(f"Call failed: {result.get('message')}")
                        
                    return {
                        "call_sid": result["sid"],
                        "status": result["status"],
                        "to": result["to"],
                        "from": result["from"],
                        "date_created": result["date_created"]
                    }
                    
        except Exception as e:
            logger.error(f"Error making call: {str(e)}")
            raise
            
    async def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """Get status of a message"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{this.base_url}/Accounts/{this.settings['account_sid']}/Messages/{message_sid}.json",
                    auth=aiohttp.BasicAuth(
                        this.settings["account_sid"],
                        this.settings["auth_token"]
                    )
                ) as response:
                    result = await response.json()
                    if response.status != 200:
                        raise ValueError(f"Failed to get message status: {result.get('message')}")
                        
                    return {
                        "message_sid": result["sid"],
                        "status": result["status"],
                        "to": result["to"],
                        "from": result["from"],
                        "body": result["body"],
                        "date_created": result["date_created"],
                        "date_sent": result.get("date_sent"),
                        "date_updated": result["date_updated"],
                        "error_code": result.get("error_code"),
                        "error_message": result.get("error_message")
                    }
                    
        except Exception as e:
            logger.error(f"Error getting message status: {str(e)}")
            raise
            
    async def get_call_status(self, call_sid: str) -> Dict[str, Any]:
        """Get status of a call"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{this.base_url}/Accounts/{this.settings['account_sid']}/Calls/{call_sid}.json",
                    auth=aiohttp.BasicAuth(
                        this.settings["account_sid"],
                        this.settings["auth_token"]
                    )
                ) as response:
                    result = await response.json()
                    if response.status != 200:
                        raise ValueError(f"Failed to get call status: {result.get('message')}")
                        
                    return {
                        "call_sid": result["sid"],
                        "status": result["status"],
                        "to": result["to"],
                        "from": result["from"],
                        "date_created": result["date_created"],
                        "date_updated": result["date_updated"],
                        "duration": result.get("duration"),
                        "error_code": result.get("error_code"),
                        "error_message": result.get("error_message")
                    }
                    
        except Exception as e:
            logger.error(f"Error getting call status: {str(e)}")
            raise
            
    def verify_webhook_signature(
        self,
        body: str,
        headers: Dict[str, str]
    ) -> bool:
        """Verify Twilio webhook signature"""
        try:
            # Implementation depends on Twilio's webhook verification method
            # This is a placeholder for the actual implementation
            return True
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False
            
# Create singleton instance
twilio_client = TwilioClient() 