import os
import pytest
from dotenv import load_dotenv
from src.ai.handler import AIHandler

# Load environment variables
load_dotenv()

@pytest.fixture
def ai_handler():
    """Create an AI handler for testing"""
    return AIHandler()

@pytest.mark.asyncio
async def test_process_message(ai_handler):
    """Test processing a message"""
    # Process a test message
    response = await ai_handler.process_message("Hello, I want to order a product", "+1234567890")
    
    # Check the response
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_search_website(ai_handler):
    """Test searching the website"""
    # Search for a product
    response = await ai_handler.search_website("blue shirt")
    
    # Check the response
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_search_crm(ai_handler):
    """Test searching the CRM"""
    # Search for a customer
    response = await ai_handler.search_crm("John Doe")
    
    # Check the response
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0

def test_is_order_related(ai_handler):
    """Test order-related message detection"""
    # Test order-related messages
    assert ai_handler._is_order_related("I want to order a product") is True
    assert ai_handler._is_order_related("What's the price of this item?") is True
    assert ai_handler._is_order_related("When will my order be delivered?") is True
    
    # Test non-order-related messages
    assert ai_handler._is_order_related("Hello, how are you?") is False
    assert ai_handler._is_order_related("Thank you for your help") is False 