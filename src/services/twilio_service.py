from typing import List, Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant, ChatGrant
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.twiml.messaging_response import MessagingResponse

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class TwilioService:
    """Service for handling Twilio operations."""
    
    def __init__(self):
        """Initialize Twilio client."""
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        self.messaging_service_sid = settings.TWILIO_MESSAGING_SERVICE_SID
        self.verify_service_sid = settings.TWILIO_VERIFY_SERVICE_SID
        self.api_key = settings.TWILIO_API_KEY
        self.api_secret = settings.TWILIO_API_SECRET
        self.webhook_url = settings.TWILIO_WEBHOOK_URL
        self.status_callback_url = settings.TWILIO_STATUS_CALLBACK_URL
        
        logger.info("Initialized Twilio service")
    
    async def send_sms(
        self,
        to: str,
        body: str,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send an SMS message.
        
        Args:
            to: Recipient phone number
            body: Message content
            media_urls: Optional list of media URLs to attach
            
        Returns:
            Message details
        """
        try:
            message = self.client.messages.create(
                messaging_service_sid=self.messaging_service_sid,
                to=to,
                body=body,
                media_url=media_urls
            )
            
            logger.info(f"Sent SMS to {to}: {message.sid}")
            return {
                "sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "body": message.body,
                "date_created": message.date_created,
                "date_sent": message.date_sent,
                "error_code": message.error_code,
                "error_message": message.error_message
            }
            
        except TwilioRestException as e:
            logger.error(f"Error sending SMS: {str(e)}")
            raise
    
    async def make_call(
        self,
        to: str,
        twiml_url: str,
        status_callback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make a voice call.
        
        Args:
            to: Recipient phone number
            twiml_url: URL to TwiML instructions
            status_callback: Optional callback URL for call status
            
        Returns:
            Call details
        """
        try:
            call = self.client.calls.create(
                to=to,
                from_=self.phone_number,
                url=twiml_url,
                status_callback=status_callback or self.status_callback_url,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method='POST'
            )
            
            logger.info(f"Initiated call to {to}: {call.sid}")
            return {
                "sid": call.sid,
                "status": call.status,
                "to": call.to,
                "from": call.from_,
                "direction": call.direction,
                "duration": call.duration,
                "start_time": call.start_time,
                "end_time": call.end_time,
                "price": call.price,
                "price_unit": call.price_unit
            }
            
        except TwilioRestException as e:
            logger.error(f"Error making call: {str(e)}")
            raise
    
    async def verify_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Send verification code to phone number.
        
        Args:
            phone_number: Phone number to verify
            
        Returns:
            Verification details
        """
        try:
            verification = self.client.verify.v2.services(
                self.verify_service_sid
            ).verifications.create(
                to=phone_number,
                channel='sms'
            )
            
            logger.info(f"Sent verification to {phone_number}: {verification.sid}")
            return {
                "sid": verification.sid,
                "status": verification.status,
                "to": verification.to,
                "channel": verification.channel,
                "valid": verification.valid
            }
            
        except TwilioRestException as e:
            logger.error(f"Error sending verification: {str(e)}")
            raise
    
    async def check_verification(
        self,
        phone_number: str,
        code: str
    ) -> Dict[str, Any]:
        """
        Check verification code.
        
        Args:
            phone_number: Phone number to verify
            code: Verification code
            
        Returns:
            Verification check details
        """
        try:
            check = self.client.verify.v2.services(
                self.verify_service_sid
            ).verification_checks.create(
                to=phone_number,
                code=code
            )
            
            logger.info(f"Checked verification for {phone_number}: {check.sid}")
            return {
                "sid": check.sid,
                "status": check.status,
                "to": check.to,
                "valid": check.valid
            }
            
        except TwilioRestException as e:
            logger.error(f"Error checking verification: {str(e)}")
            raise
    
    def generate_access_token(
        self,
        identity: str,
        grants: List[str] = ['voice', 'chat']
    ) -> str:
        """
        Generate access token for client.
        
        Args:
            identity: User identity
            grants: List of grants to include
            
        Returns:
            Access token
        """
        try:
            token = AccessToken(
                self.client.account_sid,
                self.api_key,
                self.api_secret,
                identity=identity
            )
            
            if 'voice' in grants:
                voice_grant = VoiceGrant(
                    outgoing_application_sid=self.messaging_service_sid,
                    incoming_allow=True
                )
                token.add_grant(voice_grant)
            
            if 'chat' in grants:
                chat_grant = ChatGrant(
                    service_sid=self.messaging_service_sid
                )
                token.add_grant(chat_grant)
            
            logger.info(f"Generated access token for {identity}")
            return token.to_jwt().decode()
            
        except Exception as e:
            logger.error(f"Error generating access token: {str(e)}")
            raise
    
    def generate_voice_twiml(
        self,
        gather_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate TwiML for voice response.
        
        Args:
            gather_params: Parameters for Gather verb
            
        Returns:
            TwiML string
        """
        try:
            response = VoiceResponse()
            
            if gather_params:
                gather = Gather(**gather_params)
                response.append(gather)
            else:
                response.say("Hello from Twilio!")
            
            logger.info("Generated voice TwiML")
            return str(response)
            
        except Exception as e:
            logger.error(f"Error generating voice TwiML: {str(e)}")
            raise
    
    def generate_messaging_twiml(
        self,
        message: str,
        media_urls: Optional[List[str]] = None
    ) -> str:
        """
        Generate TwiML for messaging response.
        
        Args:
            message: Message content
            media_urls: Optional list of media URLs
            
        Returns:
            TwiML string
        """
        try:
            response = MessagingResponse()
            response.message(message, media_url=media_urls)
            
            logger.info("Generated messaging TwiML")
            return str(response)
            
        except Exception as e:
            logger.error(f"Error generating messaging TwiML: {str(e)}")
            raise

# Create singleton instance
twilio_service = TwilioService() 