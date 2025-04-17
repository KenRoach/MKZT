from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.utils.metrics_tracker import MetricsTracker
from src.utils.notification_handler import NotificationHandler
from src.utils.security_audit import get_audit_logs
from src.monitoring.security_metrics import metrics_collector
from prometheus_client import generate_latest
import json

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

@router.get("/security/metrics")
async def security_metrics():
    """Get security metrics in Prometheus format"""
    return generate_latest()

@router.get("/security/dashboard")
async def security_dashboard():
    """Get security dashboard data"""
    now = datetime.utcnow()
    hour_ago = now - timedelta(hours=1)
    
    # Get recent audit logs
    audit_logs = await get_audit_logs(
        start_time=hour_ago,
        end_time=now,
        limit=1000
    )
    
    # Aggregate metrics
    metrics = {
        "failed_logins": {
            "total": len([log for log in audit_logs if log.event_type == "failed_login"]),
            "by_ip": {}
        },
        "rate_limit_hits": {
            "total": len([log for log in audit_logs if log.event_type == "rate_limit"]),
            "by_endpoint": {}
        },
        "suspicious_activities": {
            "total": len([log for log in audit_logs if log.event_type == "suspicious"]),
            "by_type": {}
        },
        "blocked_ips": list(metrics_collector._blocked_ips),
        "active_sessions": metrics_collector.active_sessions._value.get(),
    }
    
    return metrics

@router.get("/security/alerts")
async def security_alerts():
    """Get recent security alerts"""
    return list(alert_manager.alert_history.items())

@router.get("/security/blocked-ips")
async def blocked_ips():
    """Get currently blocked IPs"""
    return list(metrics_collector._blocked_ips) 