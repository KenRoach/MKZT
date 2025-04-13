from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
import json
import openai
from google.cloud import speech_v1, language_v1
from supabase import create_client, Client
from src.config.ai_config import ai_config
from src.utils.cache import Cache

logger = logging.getLogger(__name__)

class AIService:
    """Unified AI Service for all AI operations"""
    
    def __init__(self):
        """Initialize AI service with OpenAI, Google Cloud, and Supabase clients"""
        # Initialize OpenAI
        openai.api_key = ai_config.OPENAI_API_KEY.get_secret_value()
        self.model = ai_config.OPENAI_MODEL
        self.max_tokens = ai_config.OPENAI_MAX_TOKENS
        self.temperature = ai_config.OPENAI_TEMPERATURE
        
        # Initialize Google Cloud clients
        self.speech_client = speech_v1.SpeechClient()
        self.language_client = language_v1.LanguageServiceClient()
        
        # Initialize Supabase client
        supabase_settings = ai_config.get_supabase_settings()
        self.supabase: Client = create_client(
            supabase_settings["url"],
            supabase_settings["key"]
        )
        
        # Initialize cache
        self.cache = Cache(ttl=ai_config.AI_CACHE_TTL)
        
        # Error tracking
        self.error_count = 0
        self.last_error_time = None
    
    async def process_text(self, text: str, task: str = "general") -> Dict[str, Any]:
        """
        Process text using OpenAI for various tasks
        
        Args:
            text: Input text to process
            task: Type of task (general, order, sentiment, etc.)
            
        Returns:
            Processed results
        """
        try:
            # Check cache
            cache_key = f"{task}:{text}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Prepare prompt based on task
            prompt = self._get_task_prompt(task, text)
            
            # Call OpenAI
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Process response
            result = self._process_response(response, task)
            
            # Store in Supabase
            await self._store_ai_result(task, text, result)
            
            # Cache result
            await self.cache.set(cache_key, result)
            
            return result
            
        except Exception as e:
            self._handle_error(e)
            raise
    
    async def process_audio(self, audio_content: bytes, language: str = "en") -> Dict[str, Any]:
        """
        Process audio using Google Speech-to-Text
        
        Args:
            audio_content: Audio data
            language: Language code
            
        Returns:
            Transcription and analysis
        """
        try:
            # Transcribe audio
            audio = speech_v1.RecognitionAudio(content=audio_content)
            config = speech_v1.RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code=language
            )
            
            response = await self.speech_client.recognize(config=config, audio=audio)
            transcript = " ".join([result.alternatives[0].transcript 
                                 for result in response.results])
            
            # Store transcript in Supabase
            await self._store_transcript(transcript, language)
            
            # Process transcript with OpenAI
            return await self.process_text(transcript, "audio")
            
        except Exception as e:
            self._handle_error(e)
            raise
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using Google Cloud Language API
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        try:
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            
            sentiment = await self.language_client.analyze_sentiment(
                request={"document": document}
            )
            
            result = {
                "score": sentiment.document_sentiment.score,
                "magnitude": sentiment.document_sentiment.magnitude
            }
            
            # Store sentiment in Supabase
            await self._store_sentiment(text, result)
            
            return result
            
        except Exception as e:
            self._handle_error(e)
            raise
    
    async def _store_ai_result(self, task: str, text: str, result: Dict[str, Any]) -> None:
        """Store AI processing result in Supabase"""
        try:
            data = {
                "task": task,
                "input_text": text,
                "result": result,
                "created_at": datetime.now().isoformat()
            }
            await self.supabase.table("ai_results").insert(data).execute()
        except Exception as e:
            logger.error(f"Error storing AI result: {str(e)}")
    
    async def _store_transcript(self, transcript: str, language: str) -> None:
        """Store transcript in Supabase"""
        try:
            data = {
                "transcript": transcript,
                "language": language,
                "created_at": datetime.now().isoformat()
            }
            await this.supabase.table("transcripts").insert(data).execute()
        except Exception as e:
            logger.error(f"Error storing transcript: {str(e)}")
    
    async def _store_sentiment(self, text: str, sentiment: Dict[str, Any]) -> None:
        """Store sentiment analysis in Supabase"""
        try:
            data = {
                "text": text,
                "score": sentiment["score"],
                "magnitude": sentiment["magnitude"],
                "created_at": datetime.now().isoformat()
            }
            await this.supabase.table("sentiments").insert(data).execute()
        except Exception as e:
            logger.error(f"Error storing sentiment: {str(e)}")
    
    def _get_task_prompt(self, task: str, text: str) -> Dict[str, str]:
        """Get appropriate prompt for the task"""
        prompts = {
            "general": {
                "system": "You are a helpful assistant.",
                "user": text
            },
            "order": {
                "system": "You are an order processing assistant. Extract order details from the text.",
                "user": f"Extract order information from: {text}"
            },
            "sentiment": {
                "system": "You are a sentiment analysis assistant. Analyze the sentiment of the text.",
                "user": f"Analyze sentiment of: {text}"
            },
            "audio": {
                "system": "You are an audio processing assistant. Process the transcribed text.",
                "user": f"Process transcribed text: {text}"
            }
        }
        return prompts.get(task, prompts["general"])
    
    def _process_response(self, response: Any, task: str) -> Dict[str, Any]:
        """Process OpenAI response based on task"""
        content = response.choices[0].message.content
        
        if task == "order":
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"error": "Failed to parse order details"}
        
        return {"response": content}
    
    def _handle_error(self, error: Exception) -> None:
        """Handle and track errors"""
        self.error_count += 1
        self.last_error_time = datetime.now()
        
        if self.error_count >= ai_config.AI_ERROR_THRESHOLD:
            logger.error(f"AI service error threshold reached: {str(error)}")
            # TODO: Implement alerting system
        
        logger.error(f"AI service error: {str(error)}")

# Create global instance
ai_service = AIService() 