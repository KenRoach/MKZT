from fastapi import APIRouter, Request, Response, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
from src.services.payment import PaymentService
from src.handlers.payment import PaymentHandler
from src.data.crm_repository import CRMRepository
from src.auth.auth import get_current_user

# Set up logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/payment", tags=["payment"])

# Initialize services
payment_handler = PaymentHandler()
crm_repository = CRMRepository()
payment_service = PaymentService(payment_handler, crm_repository)

@router.post("/process")
async def process_payment(
    order_id: str,
    amount: float,
    currency: str,
    channel: str,
    customer_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Process a payment for an order"""
    try:
        # Verify user has access to this order
        order = await crm_repository.get_order(order_id)
        if not order or order["customer_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to process this payment")
            
        result = await payment_service.process_order_payment(
            order_id=order_id,
            amount=amount,
            currency=currency,
            channel=channel,
            customer_id=customer_id,
            metadata=metadata
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/refund")
async def process_refund(
    transaction_id: str,
    amount: float,
    reason: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Process a refund"""
    try:
        # Verify user has access to this payment
        payment = await crm_repository.get_payment(transaction_id)
        if not payment or payment["customer_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to process this refund")
            
        result = await payment_service.process_refund(
            transaction_id=transaction_id,
            amount=amount,
            reason=reason
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{transaction_id}")
async def get_payment_status(
    transaction_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get payment status"""
    try:
        # Verify user has access to this payment
        payment = await crm_repository.get_payment(transaction_id)
        if not payment or payment["customer_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to view this payment")
            
        result = await payment_service.get_payment_status(transaction_id)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhook/{channel}")
async def handle_webhook(
    channel: str,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Handle payment webhook"""
    try:
        # Get raw body and headers
        body = await request.body()
        headers = dict(request.headers)
        
        # Verify webhook signature
        if not await payment_handler.verify_webhook(channel, body, headers):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
            
        # Process webhook
        result = await payment_service.handle_webhook(channel, body, headers)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/execute/{payment_id}")
async def execute_payment(
    payment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Execute a pending payment"""
    try:
        # Execute payment
        result = await payment_handler.execute_payment(payment_id)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
@router.post("/cancel/{payment_id}")
async def cancel_payment(
    payment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Cancel a pending payment"""
    try:
        # Cancel payment
        result = await payment_handler.cancel_payment(payment_id)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error cancelling payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 