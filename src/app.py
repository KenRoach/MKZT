from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.middleware.api_key import APIKeyMiddleware
from src.middleware.rate_limit import RateLimitMiddleware
from src.config.security import security_settings
from src.analytics.restaurant_analytics import RestaurantAnalytics
from src.routing.enhanced_routing import EnhancedRouting
from src.ratings.rating_system import RatingSystem
from src.inventory.inventory_management import InventoryManagement
from src.analytics.advanced_realtime_analytics import AdvancedRealtimeAnalytics
from src.testing.ab_testing_engine import ABTestingEngine
from src.whatsapp.enhanced_whatsapp_handler import EnhancedWhatsAppHandler
from src.merchant.merchant_dashboard_handler import MerchantDashboardHandler
from src.whatsapp.merchant_whatsapp_handler import MerchantWhatsAppHandler
from src.whatsapp.enhanced_merchant_handler import EnhancedMerchantHandler
from src.whatsapp.nutrition_whatsapp_handler import NutritionWhatsAppHandler
import asyncio
from typing import Dict, Any
from datetime import datetime
import os
import json

app = FastAPI(
    title="Order Management System",
    description="A comprehensive order management system with multi-channel support",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API key validation middleware
app.add_middleware(APIKeyMiddleware)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Import and include routers
from src.routers import merchant, order, driver, customer

app.include_router(merchant.router, prefix="/api/v1/merchants", tags=["merchants"])
app.include_router(order.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(driver.router, prefix="/api/v1/drivers", tags=["drivers"])
app.include_router(customer.router, prefix="/api/v1/customers", tags=["customers"])

# Initialize components
realtime_analytics = AdvancedRealtimeAnalytics()
ab_testing = ABTestingEngine()
whatsapp_handler = EnhancedWhatsAppHandler()
merchant_handler = EnhancedMerchantHandler()
nutrition_handler = NutritionWhatsAppHandler()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint."""
    return {
        "status": "operational",
        "version": "1.0.0"
    }

# Advanced Analytics Endpoints
@app.get("/analytics/realtime")
async def get_realtime_analytics():
    """Get current real-time analytics"""
    data = await realtime_analytics.process_realtime_metrics({
        "timestamp": datetime.now(),
        "active_sessions": await get_active_sessions(),
        "current_metrics": await get_current_metrics()
    })
    return data

@app.get("/analytics/trends")
async def get_trend_analysis():
    """Get trend analysis"""
    return await realtime_analytics._analyze_trends()

@app.get("/analytics/anomalies")
async def get_anomalies():
    """Get detected anomalies"""
    return await realtime_analytics._detect_anomalies()

# A/B Testing Endpoints
@app.post("/ab-testing/create")
async def create_ab_test(test_config: Dict[str, Any]):
    """Create a new A/B test"""
    return await ab_testing.create_test(test_config)

@app.get("/ab-testing/{test_id}/assign/{user_id}")
async def assign_to_test(test_id: str, user_id: str):
    """Assign a user to an A/B test variant"""
    return await ab_testing.assign_user_to_variant(user_id, test_id)

@app.post("/ab-testing/{test_id}/record")
async def record_test_event(test_id: str, event_data: Dict[str, Any]):
    """Record an event for A/B testing"""
    return await ab_testing.record_event(
        test_id,
        event_data.get("user_id"),
        event_data
    )

@app.get("/ab-testing/{test_id}/results")
async def get_test_results(test_id: str):
    """Get A/B test results"""
    return await ab_testing.analyze_test(test_id)

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(message_data: Dict[str, Any]):
    """Handle incoming WhatsApp messages"""
    try:
        await whatsapp_handler.process_message(message_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook/whatsapp/verify")
async def verify_webhook(mode: str, token: str, challenge: str):
    """Verify WhatsApp webhook"""
    if mode == "subscribe" and token == os.getenv("WEBHOOK_VERIFY_TOKEN"):
        return int(challenge)
    raise HTTPException(status_code=403, detail="Invalid verification token")

@app.post("/webhook/merchant")
async def merchant_webhook(message_data: Dict[str, Any]):
    """Handle merchant WhatsApp messages"""
    try:
        await merchant_handler.process_merchant_message(message_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/merchant/enhanced")
async def enhanced_merchant_webhook(request_data: Dict[str, Any]):
    """Handle enhanced merchant requests"""
    try:
        await merchant_handler.process_merchant_request(request_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/merchant/{merchant_id}")
async def merchant_dashboard_websocket(websocket: WebSocket, merchant_id: str):
    """Real-time merchant dashboard updates"""
    await websocket.accept()
    try:
        while True:
            # Send real-time updates about sales, orders, etc.
            dashboard_data = await merchant_handler.merchant_dashboard._fetch_sales_data(
                merchant_id
            )
            await websocket.send_json(dashboard_data)
            await asyncio.sleep(5)  # Update every 5 seconds
    except WebSocketDisconnect:
        pass

@app.websocket("/ws/merchant/{merchant_id}/inventory")
async def inventory_websocket(websocket: WebSocket, merchant_id: str):
    """Real-time inventory updates"""
    await websocket.accept()
    try:
        while True:
            inventory_data = await merchant_handler.inventory_manager.get_inventory_summary(
                merchant_id
            )
            await websocket.send_json(inventory_data)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass

@app.websocket("/ws/merchant/{merchant_id}/promotions")
async def promotions_websocket(websocket: WebSocket, merchant_id: str):
    """Real-time promotion updates"""
    await websocket.accept()
    try:
        while True:
            promotions_data = await merchant_handler.promotion_manager.get_active_promotions(
                merchant_id
            )
            await websocket.send_json(promotions_data)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass

@app.websocket("/ws/merchant/{merchant_id}/customers")
async def customers_websocket(websocket: WebSocket, merchant_id: str):
    """Real-time customer insights"""
    await websocket.accept()
    try:
        while True:
            customer_data = await merchant_handler.customer_manager.get_customer_insights(
                merchant_id
            )
            await websocket.send_json(customer_data)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass

# Example merchant login
message_data = {
    "phone_number": "+1234567890",
    "credentials": "ROLLINGSUSHI2024",
    "merchant_id": "rolling_sushi_01"
}

# Process the login
await merchant_handler.process_merchant_message(message_data)

# Example menu selection
message_data = {
    "phone_number": "+1234567890",
    "merchant_id": "rolling_sushi_01",
    "text": "1"  # View sales
}

# Process the selection
await merchant_handler.process_merchant_message(message_data)

@app.post("/webhook/nutrition")
async def nutrition_webhook(message_data: Dict[str, Any]):
    """Handle nutrition tracking WhatsApp messages"""
    try:
        await nutrition_handler.process_nutrition_message(message_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 