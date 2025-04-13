from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from datetime import datetime, timedelta
from src.utils.metrics_tracker import MetricsTracker
from src.utils.notification_handler import NotificationHandler

app = FastAPI(title="WhatsApp Bot Dashboard")
metrics_tracker = MetricsTracker()
notification_handler = NotificationHandler()

# Mount static files
app.mount("/static", StaticFiles(directory="src/dashboard/static"), name="static")
templates = Jinja2Templates(directory="src/dashboard/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the dashboard page"""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

@app.get("/api/metrics")
async def get_metrics():
    """Get current metrics"""
    return metrics_tracker.get_metrics()

@app.get("/api/health")
async def get_health():
    """Get health status"""
    thresholds = {
        "error_rate": 0.1,
        "response_time": 2.0,
        "consecutive_errors": 3,
        "memory_usage_mb": 1000,
        "cpu_usage_percent": 80
    }
    return metrics_tracker.check_health(thresholds)

@app.get("/api/history")
async def get_history():
    """Get historical metrics"""
    # This would typically come from a database
    # For now, we'll return some sample data
    now = datetime.utcnow()
    history = []
    for i in range(24):
        timestamp = now - timedelta(hours=i)
        history.append({
            "timestamp": timestamp.isoformat(),
            "requests": 100 + i * 10,
            "errors": i * 2,
            "response_time": 0.5 + (i % 5) * 0.1
        })
    return history 