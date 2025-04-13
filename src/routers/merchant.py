from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from src.utils.database import get_db
from src.handlers.order_manager import OrderManager
from src.services.merchant_app_integration import merchant_app_integration
from src.services.merchant_registry import merchant_registry
from src.utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/merchant", tags=["merchant"])
order_manager = OrderManager()

@router.get("/merchants/{merchant_id}/metrics")
async def get_merchant_metrics(
    merchant_id: str,
    time_range: str = "today",
    db: Session = Depends(get_db)
):
    """Get merchant performance metrics"""
    try:
        metrics = await order_manager.get_merchant_metrics(merchant_id, time_range)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/merchants/{merchant_id}/analytics")
async def get_merchant_analytics(
    merchant_id: str,
    time_range: str = "today",
    db: Session = Depends(get_db)
):
    """Get merchant order analytics"""
    try:
        analytics = await order_manager.get_merchant_analytics(merchant_id, time_range)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/merchants/{merchant_id}/insights")
async def get_merchant_insights(
    merchant_id: str,
    db: Session = Depends(get_db)
):
    """Get merchant customer insights"""
    try:
        insights = await order_manager.get_merchant_insights(merchant_id)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/merchants/{merchant_id}/alerts")
async def get_merchant_alerts(
    merchant_id: str,
    db: Session = Depends(get_db)
):
    """Get merchant alerts"""
    try:
        alerts = await order_manager.get_merchant_alerts(merchant_id)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/merchants/{merchant_id}/orders")
async def get_merchant_orders(
    merchant_id: str,
    status: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get merchant orders"""
    try:
        # Implement order retrieval logic
        return {
            "orders": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/merchants/{merchant_id}/drivers")
async def get_merchant_drivers(
    merchant_id: str,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get merchant drivers"""
    try:
        # Implement driver retrieval logic
        return {
            "drivers": [],
            "total": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{merchant_id}/order")
async def send_order_to_merchant(
    merchant_id: str,
    order_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send an order to a merchant's app
    
    Args:
        merchant_id: Merchant ID
        order_data: Order details
        
    Returns:
        Response from merchant's app
    """
    try:
        # Check if merchant exists and is active
        merchant = await merchant_registry.get_merchant_by_id(merchant_id)
        if not merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        
        if not merchant.get("is_active"):
            raise HTTPException(status_code=400, detail="Merchant is not active")
        
        if not merchant.get("is_accepting_orders"):
            raise HTTPException(status_code=400, detail="Merchant is not accepting orders")
        
        # Send order to merchant's app
        response = await merchant_app_integration.send_order_to_merchant(merchant_id, order_data)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending order to merchant: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{merchant_id}/order/{order_id}")
async def get_order_status(
    merchant_id: str,
    order_id: str
) -> Dict[str, Any]:
    """
    Get order status from merchant's app
    
    Args:
        merchant_id: Merchant ID
        order_id: Order ID
        
    Returns:
        Order status from merchant's app
    """
    try:
        # Check if merchant exists
        merchant = await merchant_registry.get_merchant_by_id(merchant_id)
        if not merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        
        # Get order status from merchant's app
        status = await merchant_app_integration.get_order_status(merchant_id, order_id)
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{merchant_id}/order/{order_id}")
async def update_order_status(
    merchant_id: str,
    order_id: str,
    status_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update order status in merchant's app
    
    Args:
        merchant_id: Merchant ID
        order_id: Order ID
        status_data: New status details
        
    Returns:
        Response from merchant's app
    """
    try:
        # Check if merchant exists
        merchant = await merchant_registry.get_merchant_by_id(merchant_id)
        if not merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        
        # Update order status in merchant's app
        response = await merchant_app_integration.update_order_status(
            merchant_id, order_id, status_data
        )
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{merchant_id}/menu")
async def get_merchant_menu(
    merchant_id: str
) -> List[Dict[str, Any]]:
    """
    Get merchant's menu
    
    Args:
        merchant_id: Merchant ID
        
    Returns:
        List of menu items
    """
    try:
        # Check if merchant exists
        merchant = await merchant_registry.get_merchant_by_id(merchant_id)
        if not merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        
        # Get merchant's menu
        menu = await merchant_registry.get_merchant_menu(merchant_id)
        return menu
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting merchant menu: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{merchant_id}/menu")
async def update_merchant_menu(
    merchant_id: str,
    menu: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Update merchant's menu
    
    Args:
        merchant_id: Merchant ID
        menu: New menu items
        
    Returns:
        Update results
    """
    try:
        # Check if merchant exists
        merchant = await merchant_registry.get_merchant_by_id(merchant_id)
        if not merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        
        # Update merchant's menu
        success = await merchant_registry.update_merchant_menu(merchant_id, menu)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update menu")
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating merchant menu: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{merchant_id}/status")
async def get_merchant_status(
    merchant_id: str
) -> Dict[str, Any]:
    """
    Get merchant's operational status
    
    Args:
        merchant_id: Merchant ID
        
    Returns:
        Merchant status
    """
    try:
        status = await merchant_registry.get_merchant_status(merchant_id)
        if not status["success"]:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting merchant status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{merchant_id}/status")
async def update_merchant_status(
    merchant_id: str,
    is_active: Optional[bool] = None,
    is_accepting_orders: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update merchant's operational status
    
    Args:
        merchant_id: Merchant ID
        is_active: Whether merchant is active
        is_accepting_orders: Whether merchant is accepting orders
        
    Returns:
        Update results
    """
    try:
        status = await merchant_registry.update_merchant_status(
            merchant_id, is_active, is_accepting_orders
        )
        if not status["success"]:
            raise HTTPException(status_code=400, detail=status["error"])
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating merchant status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 