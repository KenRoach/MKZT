from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any, Optional
import logging
from src.handlers.whatsapp_auth import whatsapp_auth
from src.handlers.whatsapp_inventory import whatsapp_inventory
from src.auth.auth_handler import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

@router.post("/webhook")
async def handle_webhook(request: Request) -> Dict[str, Any]:
    """Handle incoming WhatsApp webhook"""
    try:
        # Parse webhook data
        data = await request.json()
        
        # Extract message details
        message = data.get("message", {})
        from_number = message.get("from")
        body = message.get("body", "")
        media_url = message.get("mediaUrl")
        
        if not from_number:
            raise HTTPException(status_code=400, detail="Missing phone number")
            
        # Check if this is an authentication message
        if body.startswith("AUTH"):
            auth_code = body.split(" ")[1]
            return await whatsapp_auth.verify_auth_code(from_number, auth_code)
            
        # For inventory management, verify the merchant
        merchant = await whatsapp_auth.get_merchant_by_phone(from_number)
        if not merchant:
            # Initiate authentication if not a merchant
            return await whatsapp_auth.initiate_auth(from_number)
            
        # Process inventory management message
        return await whatsapp_inventory.process_message(
            merchant_id=merchant["id"],
            message=body,
            media_url=media_url
        )
        
    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/initiate")
async def initiate_auth(phone_number: str) -> Dict[str, Any]:
    """Initiate WhatsApp authentication"""
    try:
        return await whatsapp_auth.initiate_auth(phone_number)
    except Exception as e:
        logger.error(f"Error initiating auth: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/verify")
async def verify_auth(phone_number: str, auth_code: str) -> Dict[str, Any]:
    """Verify authentication code"""
    try:
        return await whatsapp_auth.verify_auth_code(phone_number, auth_code)
    except Exception as e:
        logger.error(f"Error verifying auth: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/inventory/message")
async def send_inventory_message(
    merchant_id: str,
    message: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Send inventory management message via WhatsApp"""
    try:
        # Verify user is a merchant
        if current_user.get("role") != "merchant":
            raise HTTPException(status_code=403, detail="Access denied. Only merchants can access this endpoint.")
            
        return await whatsapp_inventory.process_message(
            merchant_id=merchant_id,
            message=message
        )
    except Exception as e:
        logger.error(f"Error sending inventory message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/inventory/update")
async def send_inventory_update(
    merchant_id: str,
    update_type: str,
    data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Send inventory update notification via WhatsApp"""
    try:
        # Verify user is a merchant
        if current_user.get("role") != "merchant":
            raise HTTPException(status_code=403, detail="Access denied. Only merchants can access this endpoint.")
            
        await whatsapp_inventory.send_inventory_update(
            merchant_id=merchant_id,
            update_type=update_type,
            data=data
        )
        
        return {
            "status": "success",
            "message": "Inventory update sent successfully"
        }
    except Exception as e:
        logger.error(f"Error sending inventory update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 