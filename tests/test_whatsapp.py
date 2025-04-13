import os
import pytest
from dotenv import load_dotenv
from src.whatsapp.handler import WhatsAppHandler

# Load environment variables
load_dotenv()

@pytest.fixture
def whatsapp_handler():
    """Create a WhatsApp handler for testing"""
    return WhatsAppHandler()

def test_verify_webhook(whatsapp_handler):
    """Test webhook verification"""
    # Get the API key from environment
    api_key = os.getenv("WHATSAPP_API_KEY")
    
    # Test with correct token
    result = whatsapp_handler.verify_webhook("subscribe", api_key, "1234567890")
    assert result["status"] == "success"
    assert result["challenge"] == "1234567890"
    
    # Test with incorrect token
    result = whatsapp_handler.verify_webhook("subscribe", "incorrect_token", "1234567890")
    assert result["status"] == "error"
    assert "Invalid verification" in result["message"]

@pytest.mark.asyncio
async def test_process_webhook(whatsapp_handler):
    """Test processing webhook data"""
    # Sample webhook data
    webhook_data = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "test_message_id",
                                    "from": "+1234567890",
                                    "text": {
                                        "body": "Hello, I want to order a product"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    
    # Process the webhook
    result = await whatsapp_handler.process_webhook(webhook_data)
    
    # Check the result
    assert result["status"] == "success"
    assert result["message_id"] == "test_message_id"
    assert "response" in result

@pytest.mark.asyncio
async def test_send_message(whatsapp_handler):
    """Test sending a message"""
    # Send a test message
    result = await whatsapp_handler.send_message("+1234567890", "This is a test message")
    
    # Check the result
    assert "status" in result
    # Note: In a real test, we would mock the API call to avoid actually sending messages 