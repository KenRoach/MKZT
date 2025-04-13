from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from src.services.supabase_service import supabase_service
from src.auth.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/ai-data", tags=["AI Data"])

class AIResult(BaseModel):
    task: str
    input_text: str
    result: dict

class Transcript(BaseModel):
    transcript: str
    language: str

class Sentiment(BaseModel):
    text: str
    score: float
    magnitude: float

@router.post("/ai-results")
async def store_ai_result(
    result: AIResult,
    current_user = Depends(get_current_user)
):
    """Store an AI processing result."""
    try:
        return await supabase_service.store_ai_result(
            task=result.task,
            input_text=result.input_text,
            result=result.result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai-results")
async def get_ai_results(
    task: Optional[str] = None,
    limit: int = 100,
    current_user = Depends(get_current_user)
):
    """Retrieve AI processing results."""
    try:
        return await supabase_service.get_ai_results(task=task, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transcripts")
async def store_transcript(
    transcript: Transcript,
    current_user = Depends(get_current_user)
):
    """Store a speech-to-text transcript."""
    try:
        return await supabase_service.store_transcript(
            transcript=transcript.transcript,
            language=transcript.language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transcripts")
async def get_transcripts(
    language: Optional[str] = None,
    limit: int = 100,
    current_user = Depends(get_current_user)
):
    """Retrieve speech-to-text transcripts."""
    try:
        return await supabase_service.get_transcripts(language=language, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sentiments")
async def store_sentiment(
    sentiment: Sentiment,
    current_user = Depends(get_current_user)
):
    """Store a sentiment analysis result."""
    try:
        return await supabase_service.store_sentiment(
            text=sentiment.text,
            score=sentiment.score,
            magnitude=sentiment.magnitude
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiments")
async def get_sentiments(
    limit: int = 100,
    current_user = Depends(get_current_user)
):
    """Retrieve sentiment analysis results."""
    try:
        return await supabase_service.get_sentiments(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 