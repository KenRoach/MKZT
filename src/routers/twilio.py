from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.services.twilio_service import twilio_service
from src.utils.auth import get_current_user

router = APIRouter(prefix="/twilio", tags=["twilio"])

class SMSRequest(BaseModel):
    """Request model for sending SMS."""
    to: str
    body: str
    media_urls: Optional[List[str]] = None

class CallRequest(BaseModel):
    """Request model for making calls."""
    to: str
    twiml_url: str
    status_callback: Optional[str] = None

class VerificationRequest(BaseModel):
    """Request model for phone verification."""
    phone_number: str

class VerificationCheckRequest(BaseModel):
    """Request model for checking verification."""
    phone_number: str
    code: str

class TokenRequest(BaseModel):
    """Request model for generating access token."""
    identity: str
    grants: Optional[List[str]] = ['voice', 'chat']

@router.post("/sms")
async def send_sms(
    request: SMSRequest,
    current_user = Depends(get_current_user)
):
    """
    Send an SMS message.
    
    Args:
        request: SMS request details
        current_user: Current authenticated user
        
    Returns:
        Message details
    """
    try:
        result = await twilio_service.send_sms(
            to=request.to,
            body=request.body,
            media_urls=request.media_urls
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending SMS: {str(e)}"
        )

@router.post("/call")
async def make_call(
    request: CallRequest,
    current_user = Depends(get_current_user)
):
    """
    Make a voice call.
    
    Args:
        request: Call request details
        current_user: Current authenticated user
        
    Returns:
        Call details
    """
    try:
        result = await twilio_service.make_call(
            to=request.to,
            twiml_url=request.twiml_url,
            status_callback=request.status_callback
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error making call: {str(e)}"
        )

@router.post("/verify")
async def verify_number(
    request: VerificationRequest,
    current_user = Depends(get_current_user)
):
    """
    Send verification code to phone number.
    
    Args:
        request: Verification request details
        current_user: Current authenticated user
        
    Returns:
        Verification details
    """
    try:
        result = await twilio_service.verify_number(request.phone_number)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending verification: {str(e)}"
        )

@router.post("/verify/check")
async def check_verification(
    request: VerificationCheckRequest,
    current_user = Depends(get_current_user)
):
    """
    Check verification code.
    
    Args:
        request: Verification check request details
        current_user: Current authenticated user
        
    Returns:
        Verification check details
    """
    try:
        result = await twilio_service.check_verification(
            request.phone_number,
            request.code
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking verification: {str(e)}"
        )

@router.post("/token")
async def generate_token(
    request: TokenRequest,
    current_user = Depends(get_current_user)
):
    """
    Generate access token for client.
    
    Args:
        request: Token request details
        current_user: Current authenticated user
        
    Returns:
        Access token
    """
    try:
        token = twilio_service.generate_access_token(
            request.identity,
            request.grants
        )
        
        return {"token": token}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating token: {str(e)}"
        )

@router.post("/webhook/voice")
async def voice_webhook(request: Request):
    """
    Handle voice webhook.
    
    Args:
        request: Webhook request
        
    Returns:
        TwiML response
    """
    try:
        # Get form data
        form_data = await request.form()
        
        # Generate TwiML response
        twiml = twilio_service.generate_voice_twiml()
        
        return twiml
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error handling voice webhook: {str(e)}"
        )

@router.post("/webhook/messaging")
async def messaging_webhook(request: Request):
    """
    Handle messaging webhook.
    
    Args:
        request: Webhook request
        
    Returns:
        TwiML response
    """
    try:
        # Get form data
        form_data = await request.form()
        
        # Generate TwiML response
        twiml = twilio_service.generate_messaging_twiml(
            message="Thank you for your message!"
        )
        
        return twiml
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error handling messaging webhook: {str(e)}"
        )

@router.post("/webhook/status")
async def status_webhook(request: Request):
    """
    Handle status webhook.
    
    Args:
        request: Webhook request
        
    Returns:
        Success response
    """
    try:
        # Get form data
        form_data = await request.form()
        
        # Process status update
        # TODO: Implement status update processing
        
        return {"success": True}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error handling status webhook: {str(e)}"
        ) 