from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any
import logging
from src.services.ai_bot import ai_bot
from src.auth.auth_handler import get_current_user
from src.data.crm_repository import CRMRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-bot", tags=["ai-bot"])
crm_repository = CRMRepository()

async def verify_merchant_access(merchant_id: str, current_user: Dict[str, Any]) -> bool:
    """Verify that the current user has access to the specified merchant"""
    try:
        # Check if user is a merchant
        if current_user.get("role") != "merchant":
            return False
            
        # Check if user is the owner of the merchant account
        if current_user.get("merchant_id") != merchant_id:
            return False
            
        # Verify merchant exists
        merchant = await crm_repository.get_merchant_by_id(merchant_id)
        if not merchant:
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error verifying merchant access: {str(e)}")
        return False

@router.post("/inventory/query")
async def process_inventory_query(
    merchant_id: str,
    query: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Process natural language queries about inventory"""
    try:
        # Verify merchant access
        if not await verify_merchant_access(merchant_id, current_user):
            raise HTTPException(status_code=403, detail="Access denied. You can only access your own inventory.")
            
        return await ai_bot.process_inventory_query(merchant_id, query)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing inventory query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inventory/check-levels")
async def check_inventory_levels(
    merchant_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Check inventory levels and generate alerts"""
    try:
        # Verify merchant access
        if not await verify_merchant_access(merchant_id, current_user):
            raise HTTPException(status_code=403, detail="Access denied. You can only access your own inventory.")
            
        return await ai_bot.check_inventory_levels(merchant_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking inventory levels: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inventory/suggest-reorder")
async def suggest_reorder_quantities(
    merchant_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Suggest reorder quantities based on historical data"""
    try:
        # Verify merchant access
        if not await verify_merchant_access(merchant_id, current_user):
            raise HTTPException(status_code=403, detail="Access denied. You can only access your own inventory.")
            
        return await ai_bot.suggest_reorder_quantities(merchant_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suggesting reorder quantities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inventory/trends")
async def analyze_inventory_trends(
    merchant_id: str,
    days: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Analyze inventory trends and patterns"""
    try:
        # Verify merchant access
        if not await verify_merchant_access(merchant_id, current_user):
            raise HTTPException(status_code=403, detail="Access denied. You can only access your own inventory.")
            
        return await ai_bot.analyze_inventory_trends(merchant_id, days)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing inventory trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inventory/report")
async def generate_inventory_report(
    merchant_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate a comprehensive inventory report"""
    try:
        # Verify merchant access
        if not await verify_merchant_access(merchant_id, current_user):
            raise HTTPException(status_code=403, detail="Access denied. You can only access your own inventory.")
            
        return await ai_bot.generate_inventory_report(merchant_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating inventory report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 