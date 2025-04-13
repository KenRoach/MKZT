from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from src.utils.monitoring import metrics_tracker
from src.utils.logging import get_logger

# Get logger
logger = get_logger("api")

# Create router
router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=Dict[str, Any])
async def get_application_metrics():
    """Get all application metrics"""
    logger.info("Metrics requested")
    return metrics_tracker.get_metrics()

@router.post("/reset")
async def reset_application_metrics():
    """Reset all application metrics"""
    logger.info("Metrics reset requested")
    metrics_tracker.reset_metrics()
    return {"status": "success", "message": "Metrics reset successfully"} 