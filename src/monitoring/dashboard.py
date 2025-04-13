from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.utils.metrics_tracker import MetricsTracker
from src.utils.notification_handler import NotificationHandler

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    metrics_tracker = MetricsTracker(db)
    notification_handler = NotificationHandler()
    
    # Get metrics for the last 24 hours
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    
    metrics = metrics_tracker.get_metrics(start_time, end_time)
    
    # Calculate statistics
    total_requests = sum(m.total_requests for m in metrics)
    total_errors = sum(m.error_count for m in metrics)
    avg_response_time = sum(m.average_response_time for m in metrics) / len(metrics) if metrics else 0
    
    # Get recent notifications
    recent_notifications = notification_handler.get_recent_notifications()
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "metrics": metrics,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "avg_response_time": avg_response_time,
            "recent_notifications": recent_notifications,
            "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0
        }
    )

@router.get("/api/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    metrics_tracker = MetricsTracker(db)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    return metrics_tracker.get_metrics(start_time, end_time) 