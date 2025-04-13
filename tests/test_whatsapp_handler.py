import os
import pytest
import json
from dotenv import load_dotenv
from src.whatsapp.handler import WhatsAppHandler
from unittest.mock import patch, MagicMock, AsyncMock, Mock
from src.utils.message_handler import MessageHandler

# Load environment variables
load_dotenv()

@pytest.fixture
def whatsapp_handler():
    """Fixture to create a WhatsApp handler instance"""
    os.environ["WHATSAPP_API_TOKEN"] = "test_token"
    os.environ["WHATSAPP_PHONE_NUMBER_ID"] = "test_phone_number_id"
    os.environ["WHATSAPP_VERIFY_TOKEN"] = "test_verify_token"
    return WhatsAppHandler()

@pytest.mark.asyncio
async def test_verify_webhook_valid(whatsapp_handler):
    """Test webhook verification with valid parameters"""
    # Test data
    mode = "subscribe"
    verify_token = "test_verify_token"
    challenge = "1234567890"
    
    # Verify webhook
    result = await whatsapp_handler.verify_webhook(mode, verify_token, challenge)
    
    # Check result
    assert result["status"] == "success"
    assert result["challenge"] == challenge

@pytest.mark.asyncio
async def test_verify_webhook_invalid_mode(whatsapp_handler):
    """Test webhook verification with invalid mode"""
    # Test data
    mode = "invalid"
    verify_token = "test_verify_token"
    challenge = "1234567890"
    
    # Verify webhook
    result = await whatsapp_handler.verify_webhook(mode, verify_token, challenge)
    
    # Check result
    assert result["status"] == "error"
    assert "mode" in result["message"].lower()

@pytest.mark.asyncio
async def test_verify_webhook_invalid_token(whatsapp_handler):
    """Test webhook verification with invalid token"""
    # Test data
    mode = "subscribe"
    verify_token = "wrong_token"
    challenge = "1234567890"
    
    # Verify webhook
    result = await whatsapp_handler.verify_webhook(mode, verify_token, challenge)
    
    # Check result
    assert result["status"] == "error"
    assert "token" in result["message"].lower()

@pytest.mark.asyncio
async def test_process_webhook_text_message(whatsapp_handler):
    """Test processing a text message webhook"""
    # Test data
    webhook_data = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "1234567890",
                        "text": {"body": "Hello"},
                        "id": "test-message-id"
                    }]
                }
            }]
        }]
    }
    
    # Mock message handler
    with patch.object(MessageHandler, 'process_message', new_callable=AsyncMock) as mock_process_message, \
         patch.object(WhatsAppHandler, 'send_message', new_callable=AsyncMock) as mock_send_message:
        
        # Setup mocks
        mock_process_message.return_value = "Hello! How can I help you?"
        mock_send_message.return_value = {"status": "success"}
        
        # Process webhook
        result = await whatsapp_handler.process_webhook(webhook_data)
        
        # Check result
        assert result["status"] == "success"
        mock_process_message.assert_called_once_with("Hello", "1234567890")
        mock_send_message.assert_called_once_with("1234567890", "Hello! How can I help you?")

@pytest.mark.asyncio
async def test_process_webhook_no_messages(whatsapp_handler):
    """Test processing a webhook with no messages"""
    # Test data
    webhook_data = {
        "entry": [{
            "changes": [{
                "value": {}
            }]
        }]
    }
    
    # Process webhook
    result = await whatsapp_handler.process_webhook(webhook_data)
    
    # Check result
    assert result["status"] == "error"
    assert "no messages" in result["message"].lower()

@pytest.mark.asyncio
async def test_send_message(whatsapp_handler):
    """Test sending a message"""
    # Test data
    to_number = "1234567890"
    message = "Test message"
    
    # Mock requests
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = Mock()
        mock_response.status = 200
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Send message
        result = await whatsapp_handler.send_message(to_number, message)
        
        # Check result
        assert result["status"] == "success"
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_send_template_message(whatsapp_handler):
    """Test sending a template message"""
    # Test data
    to_number = "1234567890"
    template_name = "test_template"
    language_code = "en"
    components = [{"type": "body", "parameters": [{"type": "text", "text": "test"}]}]
    
    # Mock requests
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = Mock()
        mock_response.status = 200
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Send template message
        result = await whatsapp_handler.send_template_message(
            to_number,
            template_name,
            language_code,
            components
        )
        
        # Check result
        assert result["status"] == "success"
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_send_message_error(whatsapp_handler):
    """Test sending a message with error"""
    # Test data
    to_number = "1234567890"
    message = "Test message"
    
    # Mock requests with error
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.side_effect = Exception("API Error")
        
        # Send message
        result = await whatsapp_handler.send_message(to_number, message)
        
        # Check result
        assert result["status"] == "error"
        assert "error" in result["message"].lower() 