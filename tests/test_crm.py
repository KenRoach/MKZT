import os
import pytest
from dotenv import load_dotenv
from src.crm.handler import CRMHandler

# Load environment variables
load_dotenv()

@pytest.fixture
def crm_handler():
    """Create a CRM handler for testing"""
    return CRMHandler()

@pytest.mark.asyncio
async def test_get_customer_info(crm_handler):
    """Test getting customer information"""
    # Get customer info
    result = await crm_handler.get_customer_info("12345")
    
    # Check the result
    assert "status" in result
    # Note: In a real test, we would mock the API call to avoid actually calling the CRM

@pytest.mark.asyncio
async def test_get_order_history(crm_handler):
    """Test getting order history"""
    # Get order history
    result = await crm_handler.get_order_history("12345")
    
    # Check the result
    assert "status" in result
    # Note: In a real test, we would mock the API call to avoid actually calling the CRM

@pytest.mark.asyncio
async def test_create_order(crm_handler):
    """Test creating an order"""
    # Create an order
    order_data = {
        "items": [
            {"product_id": 1, "quantity": 2}
        ],
        "shipping_address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "12345"
        }
    }
    
    result = await crm_handler.create_order("12345", order_data)
    
    # Check the result
    assert "status" in result
    # Note: In a real test, we would mock the API call to avoid actually calling the CRM

@pytest.mark.asyncio
async def test_search_customers(crm_handler):
    """Test searching customers"""
    # Search for customers
    result = await crm_handler.search_customers("John Doe")
    
    # Check the result
    assert "status" in result
    # Note: In a real test, we would mock the API call to avoid actually calling the CRM 