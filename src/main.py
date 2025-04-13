import os
from fastapi import FastAPI, Request, Response, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from src.whatsapp.handler import WhatsAppHandler
from src.utils.database import get_db, init_db
from src.utils.order_handler import OrderHandler
from src.utils.customer_handler import CustomerHandler
from src.utils.logging import setup_logging, get_logger
from src.middleware.monitoring import MonitoringMiddleware
from src.api.metrics import router as metrics_router
from src.utils.monitoring import MetricsTracker
from src.utils.notification_handler import NotificationHandler
import asyncio
import logging
from fastapi.responses import JSONResponse
from datetime import datetime
from src.middleware.rate_limit import RateLimiter
from src.middleware.security import APIKeyMiddleware, setup_cors
from src.middleware.security_headers import SecurityHeadersMiddleware, InputSanitizationMiddleware
from src.utils.logger import logger
from src.utils.security_audit import log_api_access
from src.monitoring.dashboard import router as dashboard_router
from src.config.security import security_settings
from src.handlers.order_manager import OrderManager
from src.routers import order, customer, driver, merchant, merchant_dashboard
from src.config.settings import settings

# Load environment variables
load_dotenv()

# Set up logging
loggers = setup_logging()
logger = get_logger("api")

# Initialize WhatsApp handler
whatsapp_handler = WhatsAppHandler()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Set up templates
templates = Jinja2Templates(directory="src/templates")

# Include routers
app.include_router(metrics_router)
app.include_router(dashboard_router, prefix="/monitoring", tags=["monitoring"])
app.include_router(order.router)
app.include_router(customer.router)
app.include_router(driver.router)
app.include_router(merchant.router)
app.include_router(merchant_dashboard.router)

# Initialize handlers
order_handler = OrderHandler()
customer_handler = CustomerHandler()

# Initialize metrics tracker
metrics_tracker = MetricsTracker()

# Initialize notification handler
notification_handler = NotificationHandler()

# Initialize order manager
order_manager = OrderManager()

# Add monitoring middleware with metrics tracker
app.add_middleware(MonitoringMiddleware, metrics_tracker=metrics_tracker)

# Add middleware
app.add_middleware(RateLimiter)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputSanitizationMiddleware)
setup_cors(app)

# Background task to check metrics periodically
async def check_metrics_periodically():
    while True:
        try:
            metrics = metrics_tracker.get_metrics()
            await notification_handler.notify_metrics(metrics)
        except Exception as e:
            logger.error(f"Error checking metrics: {str(e)}")
        await asyncio.sleep(60)  # Check every minute

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("Starting WhatsApp AI Ordering Bot")
    # Initialize database
    init_db()
    logger.info("Database initialized")
    # Start background tasks
    background_tasks = BackgroundTasks()
    background_tasks.add_task(check_metrics_periodically)

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("Shutting down WhatsApp AI Ordering Bot")

@app.get("/")
async def root():
    return {"message": "Welcome to the Order Management System API"}

@app.get("/dashboard")
async def dashboard(request: Request):
    """Dashboard endpoint"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verify WhatsApp webhook"""
    logger.info("Webhook verification requested")
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == os.getenv("WHATSAPP_VERIFY_TOKEN"):
            logger.info("Webhook verified successfully")
            return int(challenge)
        else:
            logger.warning("Webhook verification failed")
            raise HTTPException(status_code=403, detail="Verification failed")
    else:
        logger.warning("Invalid webhook verification request")
        raise HTTPException(status_code=400, detail="Invalid request")

@app.post("/webhook")
async def process_webhook(request: Request, db: Session = Depends(get_db)):
    """Process incoming WhatsApp webhook"""
    logger.info("Webhook received")
    try:
        # Process webhook
        response = await whatsapp_handler.process_webhook(request, db)
        logger.info("Webhook processed successfully")
        return response
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/{customer_id}")
async def get_customer_orders(customer_id: int):
    """Get all orders for a customer"""
    result = await order_handler.get_customer_orders(customer_id)
    
    if result["status"] == "success":
        return result
    else:
        raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))

@app.get("/customers/{phone_number}")
async def get_customer(phone_number: str):
    """Get customer by phone number"""
    result = await customer_handler.get_customer_by_phone(phone_number)
    
    if result["status"] == "success":
        return result
    else:
        raise HTTPException(status_code=404, detail="Customer not found")

# Order endpoints
@app.post("/orders/{channel}")
async def create_order(
    channel: str,
    data: dict,
    db: Session = Depends(get_db)
):
    """Create order from any input channel"""
    try:
        order = await order_manager.process_order(channel, data, db)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Get order by ID"""
    order = await order_manager.get_order(order_id, db)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """Update order status"""
    try:
        order = await order_manager.update_order_status(order_id, status, db)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()
    
    # Process request
    try:
        response = await call_next(request)
        success = response.status_code < 400
    except Exception as e:
        success = False
        raise e
    finally:
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000  # ms
        
        # Log API access
        db = next(get_db())
        log_api_access(
            db=db,
            endpoint=request.url.path,
            method=request.method,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            user_id=request.headers.get("X-User-ID"),
            success=success,
            error=str(e) if not success else None
        )
        
        # Update metrics
        metrics_tracker.record_request(
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code if success else 500,
            processing_time=processing_time
        )
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_details = {
        "timestamp": datetime.utcnow().isoformat(),
        "path": request.url.path,
        "method": request.method,
        "error": str(exc),
        "client_host": request.client.host
    }
    
    logger.error("Global exception", extra=error_details)
    await notification_handler.notify_error(
        error_type=type(exc).__name__,
        error_message=str(exc),
        context=error_details
    )
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    ) 