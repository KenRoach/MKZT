import os
from google.cloud import speech_v1
from google.cloud import storage
from openai import OpenAI
import logging
from typing import Dict, Optional
import json
import tempfile

from src.config.logger import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

class VoiceOrderHandler:
    def __init__(self):
        self.speech_client = speech_v1.SpeechClient()
        self.storage_client = storage.Client()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def process_voice_message(self, audio_url: str, source: str = "whatsapp") -> Optional[Dict]:
        """
        Process a voice message from WhatsApp or phone call.
        
        Args:
            audio_url: URL of the audio file
            source: Source of the voice message ("whatsapp" or "phone")
            
        Returns:
            Dictionary containing the processed order details
        """
        try:
            # Download and convert audio to proper format
            audio_content = await self._download_and_convert_audio(audio_url)
            
            # Transcribe audio using Google Speech-to-Text
            transcript = await self._transcribe_audio(audio_content)
            logger.info(f"Transcribed text: {transcript}")
            
            # Extract order details using OpenAI
            order_details = await self._extract_order_details(transcript)
            logger.info(f"Extracted order details: {order_details}")
            
            return order_details
            
        except Exception as e:
            logger.error(f"Error processing voice message: {str(e)}")
            return None
            
    async def _download_and_convert_audio(self, audio_url: str) -> bytes:
        """Download and convert audio to proper format for Speech-to-Text."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Download audio file
            # For WhatsApp, you'll need to use their Media API
            # For phone calls, you'll need to handle the streaming differently
            # This is a placeholder for the actual implementation
            pass
            
        try:
            # Convert audio to proper format (16-bit PCM WAV)
            # You'll need to use a library like pydub for this
            # This is a placeholder for the actual implementation
            audio_content = b""  # Placeholder
            return audio_content
        finally:
            os.unlink(temp_file.name)
            
    async def _transcribe_audio(self, audio_content: bytes) -> str:
        """Transcribe audio using Google Speech-to-Text."""
        audio = speech_v1.RecognitionAudio(content=audio_content)
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
            model="phone_call",  # Use phone_call model for better accuracy
            use_enhanced=True,
            enable_automatic_punctuation=True
        )
        
        response = self.speech_client.recognize(config=config, audio=audio)
        transcript = ""
        
        for result in response.results:
            transcript += result.alternatives[0].transcript + " "
            
        return transcript.strip()
        
    async def _extract_order_details(self, transcript: str) -> Dict:
        """Extract order details from transcript using OpenAI."""
        prompt = f"""
        Extract order details from the following voice transcript. 
        Format the response as a JSON object with the following fields:
        - items: list of items ordered (name, quantity, special instructions)
        - delivery_address: delivery location
        - special_instructions: any special instructions for the entire order
        - customer_name: name of the customer if mentioned
        
        Transcript: {transcript}
        """
        
        response = self.openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts order details from voice transcripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        try:
            order_details = json.loads(response.choices[0].message.content)
            return order_details
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing OpenAI response: {str(e)}")
            return None

    async def validate_order(self, order_details: Dict) -> bool:
        """Validate the extracted order details."""
        required_fields = ["items", "delivery_address"]
        
        if not all(field in order_details for field in required_fields):
            return False
            
        if not order_details["items"]:
            return False
            
        return True 