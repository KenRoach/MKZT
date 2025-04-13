import os
import pytest
from dotenv import load_dotenv
from src.utils.order_handler import OrderHandler
from src.utils.database import SessionLocal, Customer, Order

# Load environment variables
load_dotenv()

@pytest.fixture
def order_handler():
    """Create an order handler for testing"""
    return OrderHandler()

@pytest.fixture
def db_session():
    """Create a database session for testing"""
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture
def test_customer(db_session):
    """Create a test customer"""
    customer = Customer(
        phone_number="+1234567890",
        name="Test Customer",
        email="test@example.com"
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer

@pytest.mark.asyncio
async def test_create_order(order_handler, test_customer):
    """Test creating an order"""
    # Test order data
    items = [
        {"product_id": 1, "quantity": 2, "price": 1000},  # $10.00 each
        {"product_id": 2, "quantity": 1, "price": 2000}   # $20.00 each
    ]
    shipping_address = {
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "zip": "12345",
        "country": "USA"
    }
    
    # Create order
    result = await order_handler.create_order(test_customer.id, items, shipping_address)
    
    # Check result
    assert result["status"] == "success"
    assert "order_id" in result
    assert "order_number" in result
    assert result["total_amount"] == 4000  # $40.00 total

@pytest.mark.asyncio
async def test_get_order(order_handler, test_customer, db_session):
    """Test getting order details"""
    # Create a test order
    order = Order(
        customer_id=test_customer.id,
        order_number="TEST-123",
        status="pending",
        items=[{"product_id": 1, "quantity": 1, "price": 1000}],
        total_amount=1000,
        shipping_address={"street": "123 Main St"}
    )
    db_session.add(order)
    db_session.commit()
    
    # Get order details
    result = await order_handler.get_order(order.id)
    
    # Check result
    assert result["status"] == "success"
    assert result["order"]["order_number"] == "TEST-123"
    assert result["order"]["status"] == "pending"
    assert result["order"]["total_amount"] == 1000
    assert result["order"]["customer"]["phone_number"] == test_customer.phone_number

@pytest.mark.asyncio
async def test_update_order_status(order_handler, test_customer, db_session):
    """Test updating order status"""
    # Create a test order
    order = Order(
        customer_id=test_customer.id,
        order_number="TEST-123",
        status="pending",
        items=[{"product_id": 1, "quantity": 1, "price": 1000}],
        total_amount=1000,
        shipping_address={"street": "123 Main St"}
    )
    db_session.add(order)
    db_session.commit()
    
    # Update order status
    result = await order_handler.update_order_status(order.id, "completed")
    
    # Check result
    assert result["status"] == "success"
    assert result["order_number"] == "TEST-123"
    assert result["status"] == "completed"

@pytest.mark.asyncio
async def test_get_customer_orders(order_handler, test_customer, db_session):
    """Test getting customer orders"""
    # Create test orders
    orders = [
        Order(
            customer_id=test_customer.id,
            order_number=f"TEST-{i}",
            status="pending",
            items=[{"product_id": 1, "quantity": 1, "price": 1000}],
            total_amount=1000,
            shipping_address={"street": "123 Main St"}
        )
        for i in range(3)
    ]
    for order in orders:
        db_session.add(order)
    db_session.commit()
    
    # Get customer orders
    result = await order_handler.get_customer_orders(test_customer.id)
    
    # Check result
    assert result["status"] == "success"
    assert len(result["orders"]) == 3
    assert all(order["status"] == "pending" for order in result["orders"])

@pytest.mark.asyncio
async def test_extract_order_from_message(order_handler):
    """Test extracting order from message"""
    # Test message
    message = "I want to order 2 blue shirts and 1 red shirt"
    
    # Extract order
    result = await order_handler.extract_order_from_message(message)
    
    # Check result
    assert "items" in result
    assert "shipping_address" in result
    assert len(result["items"]) > 0
    assert all(key in result["shipping_address"] for key in ["street", "city", "state", "zip", "country"]) 