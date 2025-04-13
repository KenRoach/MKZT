from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from src.services.merchant_dashboard_service import merchant_dashboard
from src.utils.auth import get_current_merchant
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging
import os
from src.auth.auth_handler import get_current_user
from src.services.ai_bot import ai_bot
from src.data.crm_repository import CRMRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/merchant", tags=["merchant"])
crm_repository = CRMRepository()

# Set up templates
templates = Jinja2Templates(directory="src/templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def get_merchant_dashboard(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Serve the merchant dashboard"""
    try:
        # Verify user is a merchant
        if current_user.get("role") != "merchant":
            raise HTTPException(status_code=403, detail="Access denied. Only merchants can access this page.")
            
        return templates.TemplateResponse(
            "merchant_dashboard.html",
            {"request": request, "merchant_id": current_user.get("merchant_id")}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving merchant dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders")
async def get_merchant_orders(
    merchant_id: str = Depends(get_current_merchant),
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Get orders for the current merchant
    """
    return await merchant_dashboard.get_merchant_orders(
        merchant_id=merchant_id,
        status=status,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/orders/{order_id}")
async def get_order_details(
    order_id: str,
    merchant_id: str = Depends(get_current_merchant)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific order
    """
    order = await merchant_dashboard.get_order_details(order_id)
    
    # Verify the order belongs to the merchant
    if not order or order.get("merchant_id") != merchant_id:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: str,
    notes: Optional[str] = None,
    merchant_id: str = Depends(get_current_merchant)
) -> Dict[str, Any]:
    """
    Update the status of an order
    """
    # Verify the order belongs to the merchant
    order = await merchant_dashboard.get_order_details(order_id)
    
    if not order or order.get("merchant_id") != merchant_id:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update the order status
    updated_order = await merchant_dashboard.update_order_status(
        order_id=order_id,
        status=status,
        notes=notes
    )
    
    return updated_order

@router.get("/metrics")
async def get_merchant_metrics(
    merchant_id: str = Depends(get_current_merchant),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Get performance metrics for the merchant
    """
    return await merchant_dashboard.get_merchant_metrics(
        merchant_id=merchant_id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/popular-items")
async def get_popular_items(
    merchant_id: str = Depends(get_current_merchant),
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Get popular items for the merchant
    """
    return await merchant_dashboard.get_popular_items(
        merchant_id=merchant_id,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )

# API endpoints for the frontend
@router.get("/api/inventory/items")
async def get_inventory_items(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get all inventory items for the merchant"""
    try:
        # Verify user is a merchant
        if current_user.get("role") != "merchant":
            raise HTTPException(status_code=403, detail="Access denied. Only merchants can access this endpoint.")
            
        merchant_id = current_user.get("merchant_id")
        return await crm_repository.get_inventory_items(merchant_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inventory items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/inventory/alerts")
async def get_inventory_alerts(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get all inventory alerts for the merchant"""
    try:
        # Verify user is a merchant
        if current_user.get("role") != "merchant":
            raise HTTPException(status_code=403, detail="Access denied. Only merchants can access this endpoint.")
            
        merchant_id = current_user.get("merchant_id")
        return await crm_repository.get_inventory_alerts(merchant_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inventory alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/inventory/suggest-reorder")
async def get_reorder_suggestions(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get reorder suggestions for the merchant"""
    try:
        # Verify user is a merchant
        if current_user.get("role") != "merchant":
            raise HTTPException(status_code=403, detail="Access denied. Only merchants can access this endpoint.")
            
        merchant_id = current_user.get("merchant_id")
        return await ai_bot.suggest_reorder_quantities(merchant_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reorder suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/ai-bot/inventory/query")
async def process_inventory_query(
    query_data: Dict[str, str],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Process a natural language query about inventory"""
    try:
        # Verify user is a merchant
        if current_user.get("role") != "merchant":
            raise HTTPException(status_code=403, detail="Access denied. Only merchants can access this endpoint.")
            
        merchant_id = current_user.get("merchant_id")
        query = query_data.get("query", "")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
            
        return await ai_bot.process_inventory_query(merchant_id, query)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing inventory query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai-bot/inventory/report")
async def generate_inventory_report(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate a comprehensive inventory report"""
    try:
        # Verify user is a merchant
        if current_user.get("role") != "merchant":
            raise HTTPException(status_code=403, detail="Access denied. Only merchants can access this endpoint.")
            
        merchant_id = current_user.get("merchant_id")
        return await ai_bot.generate_inventory_report(merchant_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating inventory report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/inventory/items")
async def create_inventory_item(
    item_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a new inventory item"""
    try:
        # Verify user is a merchant
        if current_user.get("role") != "merchant":
            raise HTTPException(status_code=403, detail="Access denied. Only merchants can access this endpoint.")
            
        merchant_id = current_user.get("merchant_id")
        return await crm_repository.create_inventory_item(merchant_id, item_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating inventory item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/inventory/items/{item_id}")
async def update_inventory_item(
    item_id: str,
    item_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update an inventory item"""
    try:
        # Verify user is a merchant
        if current_user.get("role") != "merchant":
            raise HTTPException(status_code=403, detail="Access denied. Only merchants can access this endpoint.")
            
        merchant_id = current_user.get("merchant_id")
        
        # Verify the item belongs to the merchant
        inventory_items = await crm_repository.get_inventory_items(merchant_id)
        if not any(item["id"] == item_id for item in inventory_items):
            raise HTTPException(status_code=403, detail="Access denied. You can only update your own inventory items.")
            
        # Update the item
        return await crm_repository.update_inventory_item(item_id, item_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating inventory item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/inventory/items/{item_id}")
async def delete_inventory_item(
    item_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete an inventory item"""
    try:
        # Verify user is a merchant
        if current_user.get("role") != "merchant":
            raise HTTPException(status_code=403, detail="Access denied. Only merchants can access this endpoint.")
            
        merchant_id = current_user.get("merchant_id")
        
        # Verify the item belongs to the merchant
        inventory_items = await crm_repository.get_inventory_items(merchant_id)
        if not any(item["id"] == item_id for item in inventory_items):
            raise HTTPException(status_code=403, detail="Access denied. You can only delete your own inventory items.")
            
        # Delete the item
        return await crm_repository.delete_inventory_item(item_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting inventory item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/inventory/alerts/{alert_id}")
async def update_inventory_alert(
    alert_id: str,
    alert_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update an inventory alert"""
    try:
        # Verify user is a merchant
        if current_user.get("role") != "merchant":
            raise HTTPException(status_code=403, detail="Access denied. Only merchants can access this endpoint.")
            
        merchant_id = current_user.get("merchant_id")
        
        # Verify the alert belongs to the merchant
        alerts = await crm_repository.get_inventory_alerts(merchant_id)
        if not any(alert["id"] == alert_id for alert in alerts):
            raise HTTPException(status_code=403, detail="Access denied. You can only update your own alerts.")
            
        # Update the alert
        return await crm_repository.update_inventory_alert(alert_id, alert_data.get("status", "resolved"))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating inventory alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 