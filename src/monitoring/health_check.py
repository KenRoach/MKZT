from fastapi import APIRouter, HTTPException
from src.utils.logger import logger
from src.services.health_monitor import HealthMonitor

router = APIRouter()
health_monitor = HealthMonitor()

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    status = await health_monitor.check_all_systems()
    
    return {
        "status": "healthy" if all(status.values()) else "degraded",
        "services": {
            "database": status["database"],
            "redis": status["redis"],
            "whatsapp_api": status["whatsapp"],
            "conversation_service": status["conversation"]
        },
        "metrics": await health_monitor.get_system_metrics()
    } 