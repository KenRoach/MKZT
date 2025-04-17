import os
from fastapi import FastAPI, Request, Response, HTTPException, Depends, BackgroundTasks, WebSocket
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
from src.config.security import security_settings, get_security_settings, apply_security_headers
from src.handlers.order_manager import OrderManager
from src.routers import order, customer, driver, merchant, merchant_dashboard
from src.config.settings import settings
from src.middleware.auth import AuthMiddleware
from src.monitoring.security_metrics import metrics_collector
from src.monitoring.alert_manager import alert_manager
import time
from src.services.conversation_manager import conversation_manager
from src.handlers.conversation_handler import ActorType

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
settings = get_security_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
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
app.add_middleware(AuthMiddleware)
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

# Add request validation middleware
@app.middleware("http")
async def validate_request_middleware(request: Request, call_next):
    # Validate content type
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            raise HTTPException(
                status_code=415,
                detail="Unsupported media type. Only application/json is supported."
            )
    
    response = await call_next(request)
    return response

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request.state.request_id
        }
    )

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    return apply_security_headers(response.headers)

# Add middleware for security monitoring
@app.middleware("http")
async def security_monitoring_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Check if IP is blocked
    client_ip = request.client.host
    if metrics_collector.is_ip_blocked(client_ip):
        await alert_manager.alert(
            "blocked_ip_attempt",
            f"Blocked IP {client_ip} attempted to access {request.url.path}",
            "warning"
        )
        raise HTTPException(status_code=403, detail="IP address blocked")
    
    try:
        response = await call_next(request)
        
        # Track rate limits
        if response.status_code == 429:
            if metrics_collector.track_rate_limit(client_ip, request.url.path):
                await alert_manager.alert(
                    "rate_limit",
                    f"Rate limit threshold exceeded for IP {client_ip} on {request.url.path}",
                    "warning"
                )
                metrics_collector.block_ip(client_ip)
        
        return response
        
    except Exception as e:
        # Track suspicious activities
        if metrics_collector.track_suspicious_activity(client_ip, str(e)):
            await alert_manager.alert(
                "suspicious_activity",
                f"Suspicious activity detected from IP {client_ip}: {str(e)}",
                "critical"
            )
            metrics_collector.block_ip(client_ip)
        raise
    finally:
        # Record authentication latency if applicable
        if request.url.path.startswith("/auth"):
            auth_latency.observe(time.time() - start_time)

@app.websocket("/ws/{actor_type}/{actor_id}")
async def websocket_endpoint(websocket: WebSocket, actor_type: str, actor_id: str):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            order_id = data.get("order_id")
            message = data.get("message")
            
            if not order_id or not message:
                await websocket.send_json({"error": "Invalid message format"})
                continue
            
            if actor_type == "customer":
                response = await conversation_manager.handle_customer_message(
                    order_id, actor_id, message
                )
            elif actor_type == "kitchen":
                response = await conversation_manager.handle_kitchen_message(
                    order_id, actor_id, message
                )
            elif actor_type == "driver":
                response = await conversation_manager.handle_driver_message(
                    order_id, actor_id, message
                )
            else:
                await websocket.send_json({"error": "Invalid actor type"})
                continue
            
            await websocket.send_json({"response": response})
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()

@app.post("/api/v1/conversation/{order_id}/message")
async def send_message(
    order_id: str,
    actor_type: ActorType,
    actor_id: str,
    message: str
):
    """Send message through REST API"""
    try:
        if actor_type == ActorType.CUSTOMER:
            response = await conversation_manager.handle_customer_message(
                order_id, actor_id, message
            )
        elif actor_type == ActorType.KITCHEN:
            response = await conversation_manager.handle_kitchen_message(
                order_id, actor_id, message
            )
        elif actor_type == ActorType.DRIVER:
            response = await conversation_manager.handle_driver_message(
                order_id, actor_id, message
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid actor type")
            
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    ) 