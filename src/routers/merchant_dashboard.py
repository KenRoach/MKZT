from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from src.services.merchant_dashboard_service import merchant_dashboard
from src.utils.auth import get_current_merchant

router = APIRouter(prefix="/merchant/dashboard", tags=["merchant_dashboard"])

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