from supabase import create_client, Client
from src.config.supabase_config import get_supabase_settings
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        settings = get_supabase_settings()
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    async def store_ai_result(self, task: str, input_text: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Store AI processing result in the database."""
        try:
            data = {
                "task": task,
                "input_text": input_text,
                "result": result
            }
            response = self.client.table("ai_results").insert(data).execute()
            logger.info(f"Stored AI result for task: {task}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Error storing AI result: {str(e)}")
            raise
    
    async def store_transcript(self, transcript: str, language: str) -> Dict[str, Any]:
        """Store speech-to-text transcript in the database."""
        try:
            data = {
                "transcript": transcript,
                "language": language
            }
            response = self.client.table("transcripts").insert(data).execute()
            logger.info(f"Stored transcript in language: {language}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Error storing transcript: {str(e)}")
            raise
    
    async def store_sentiment(self, text: str, score: float, magnitude: float) -> Dict[str, Any]:
        """Store sentiment analysis result in the database."""
        try:
            data = {
                "text": text,
                "score": score,
                "magnitude": magnitude
            }
            response = self.client.table("sentiments").insert(data).execute()
            logger.info(f"Stored sentiment analysis with score: {score}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Error storing sentiment: {str(e)}")
            raise
    
    async def get_ai_results(self, task: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve AI results with optional task filter."""
        try:
            query = self.client.table("ai_results").select("*")
            if task:
                query = query.eq("task", task)
            response = query.order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error retrieving AI results: {str(e)}")
            raise
    
    async def get_transcripts(self, language: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve transcripts with optional language filter."""
        try:
            query = self.client.table("transcripts").select("*")
            if language:
                query = query.eq("language", language)
            response = query.order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error retrieving transcripts: {str(e)}")
            raise
    
    async def get_sentiments(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve sentiment analysis results."""
        try:
            response = self.client.table("sentiments").select("*").order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error retrieving sentiments: {str(e)}")
            raise

# Create singleton instance
supabase_service = SupabaseService() 