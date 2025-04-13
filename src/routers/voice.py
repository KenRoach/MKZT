from fastapi import APIRouter, Request, Response, HTTPException
from typing import Dict, Optional
import logging
from src.config.logger import setup_logging
from src.handlers.input_channels.phone import PhoneInputHandler
from src.handlers.order_manager import OrderManager

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])
phone_handler = PhoneInputHandler()
order_manager = OrderManager()

@router.post("/incoming")
async def handle_incoming_call() -> Response:
    """Handle incoming phone calls."""
    try:
        # Get initial TwiML response
        response = phone_handler.get_initial_response()
        return Response(content=response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {str(e)}")
        raise HTTPException(status_code=500, detail="Error handling incoming call")

@router.post("/process")
async def process_recording(request: Request) -> Response:
    """Process the voice recording."""
    try:
        # Get recording details from Twilio request
        form_data = await request.form()
        recording_url = form_data.get("RecordingUrl")
        transcription = form_data.get("TranscriptionText")
        
        if not recording_url:
            raise HTTPException(status_code=400, detail="Recording URL not found")
            
        # Process the recording
        order_details = await phone_handler.process_recording(recording_url, transcription)
        
        if not order_details:
            # If processing failed, ask the customer to try again
            response = VoiceResponse()
            response.say("I'm sorry, I couldn't understand your order. Please try again.")
            response.redirect("/voice/incoming")
            return Response(content=str(response), media_type="application/xml")
            
        # Store order details in session or temporary storage
        # This is a placeholder - implement your storage solution
        
        # Get confirmation response
        response = phone_handler.get_confirmation_response(order_details)
        return Response(content=response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing recording: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing recording")

@router.post("/confirm")
async def confirm_order(request: Request) -> Response:
    """Handle order confirmation."""
    try:
        # Get confirmation input from Twilio request
        form_data = await request.form()
        digits = form_data.get("Digits")
        
        response = VoiceResponse()
        
        if digits == "1":
            # Retrieve order details from session or temporary storage
            # This is a placeholder - implement your storage solution
            order_details = {}  # Placeholder
            
            # Process the order
            processed_order = await order_manager.process_order(order_details)
            
            if processed_order:
                response.say("Thank you! Your order has been confirmed and will be processed shortly.")
            else:
                response.say("I'm sorry, there was an error processing your order. Please try again later.")
                
        elif digits == "2":
            response.say("Order cancelled. Let's try again.")
            response.redirect("/voice/incoming")
            
        else:
            response.say("Invalid input. Please try again.")
            response.redirect("/voice/incoming")
            
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error confirming order: {str(e)}")
        raise HTTPException(status_code=500, detail="Error confirming order")

@router.post("/transcription")
async def handle_transcription(request: Request) -> Dict:
    """Handle transcription webhook from Twilio."""
    try:
        # Get transcription details from Twilio request
        form_data = await request.form()
        transcription_text = form_data.get("TranscriptionText")
        recording_url = form_data.get("RecordingUrl")
        
        if not transcription_text or not recording_url:
            raise HTTPException(status_code=400, detail="Missing transcription data")
            
        # Store transcription for later use
        # This is a placeholder - implement your storage solution
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error handling transcription: {str(e)}")
        raise HTTPException(status_code=500, detail="Error handling transcription") 