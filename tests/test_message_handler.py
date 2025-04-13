import os
import pytest
from dotenv import load_dotenv
from src.utils.message_handler import MessageHandler
from src.utils.database import SessionLocal, Customer, Message
from unittest.mock import patch, MagicMock, Mock, AsyncMock
from src.utils.customer_handler import CustomerHandler
from src.utils.order_handler import OrderHandler
from src.ai.handler import AIHandler
from src.models.database import Order, OrderStatus

# Load environment variables
load_dotenv()

@pytest.fixture
def message_handler():
    """Fixture to create a message handler instance"""
    return MessageHandler()

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

@pytest.fixture
def mock_customer():
    """Fixture to create a mock customer"""
    return Customer(
        id=1,
        phone_number="+1234567890",
        name="Test Customer",
        email="test@example.com"
    )

@pytest.fixture
def mock_order():
    """Fixture to create a mock order"""
    return Order(
        id=1,
        order_number="ORD-001",
        customer_id=1,
        status=OrderStatus.PENDING,
        total_amount=100.0,
        items=[{"name": "Test Item", "quantity": 1, "price": 100.0}],
        shipping_address={
            "street": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "country": "Test Country"
        }
    )

@pytest.mark.asyncio
async def test_process_message_greeting(message_handler, test_customer):
    """Test processing a greeting message"""
    with patch.object(CustomerHandler, 'get_or_create_customer', new_callable=AsyncMock) as mock_get_customer, \
         patch.object(AIHandler, 'analyze_intent', new_callable=AsyncMock) as mock_analyze_intent, \
         patch.object(AIHandler, 'generate_response', new_callable=AsyncMock) as mock_generate_response:
        
        # Setup mocks
        mock_get_customer.return_value = test_customer
        mock_analyze_intent.return_value = {
            "intent": "greeting",
            "confidence": 0.9,
            "entities": {}
        }
        mock_generate_response.return_value = "Hello! How can I help you today?"
        
        # Process message
        response = await message_handler.process_message(
            "Hi there!",
            test_customer.phone_number
        )
        
        # Verify response
        assert "Hello" in response
        mock_get_customer.assert_called_once_with(test_customer.phone_number)
        mock_analyze_intent.assert_called_once_with("Hi there!")
        mock_generate_response.assert_called_once()

@pytest.mark.asyncio
async def test_process_message_order(message_handler, test_customer):
    """Test processing an order message"""
    with patch.object(CustomerHandler, 'get_or_create_customer', new_callable=AsyncMock) as mock_get_customer, \
         patch.object(AIHandler, 'analyze_intent', new_callable=AsyncMock) as mock_analyze_intent, \
         patch.object(AIHandler, 'extract_order_details', new_callable=AsyncMock) as mock_extract_order, \
         patch.object(OrderHandler, 'create_order', new_callable=AsyncMock) as mock_create_order, \
         patch.object(AIHandler, 'generate_response', new_callable=AsyncMock) as mock_generate_response:
        
        # Setup mocks
        mock_get_customer.return_value = test_customer
        mock_analyze_intent.return_value = {
            "intent": "order",
            "confidence": 0.9,
            "entities": {}
        }
        mock_extract_order.return_value = {
            "items": [{"name": "Test Item", "quantity": 1, "price": 100.0}],
            "shipping_address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "zip_code": "12345",
                "country": "Test Country"
            },
            "total_amount": 100.0
        }
        mock_create_order.return_value = {"order_id": 1, "status": "pending"}
        mock_generate_response.return_value = "Order received! Please provide your shipping address."
        
        # Process message
        response = await message_handler.process_message(
            "I want to order a test item",
            test_customer.phone_number
        )
        
        # Verify response
        assert "shipping address" in response.lower()
        mock_get_customer.assert_called_once_with(test_customer.phone_number)
        mock_analyze_intent.assert_called_once()
        mock_extract_order.assert_called_once()
        mock_create_order.assert_called_once()
        mock_generate_response.assert_called_once()

@pytest.mark.asyncio
async def test_process_message_order_status(message_handler, test_customer, mock_order):
    """Test processing an order status message"""
    with patch.object(CustomerHandler, 'get_or_create_customer', new_callable=AsyncMock) as mock_get_customer, \
         patch.object(AIHandler, 'analyze_intent', new_callable=AsyncMock) as mock_analyze_intent, \
         patch.object(OrderHandler, 'get_customer_orders', new_callable=AsyncMock) as mock_get_orders, \
         patch.object(AIHandler, 'generate_response', new_callable=AsyncMock) as mock_generate_response:
        
        # Setup mocks
        mock_get_customer.return_value = test_customer
        mock_analyze_intent.return_value = {
            "intent": "order_status",
            "confidence": 0.9,
            "entities": {"order_number": "ORD-001"}
        }
        mock_get_orders.return_value = [mock_order]
        mock_generate_response.return_value = "Your order ORD-001 is pending."
        
        # Process message
        response = await message_handler.process_message(
            "What's the status of my order ORD-001?",
            test_customer.phone_number
        )
        
        # Verify response
        assert "ORD-001" in response
        assert "pending" in response.lower()
        mock_get_customer.assert_called_once_with(test_customer.phone_number)
        mock_analyze_intent.assert_called_once()
        mock_get_orders.assert_called_once_with(test_customer.id)
        mock_generate_response.assert_called_once()

@pytest.mark.asyncio
async def test_process_message_help(message_handler, test_customer):
    """Test processing a help message"""
    with patch.object(CustomerHandler, 'get_or_create_customer', new_callable=AsyncMock) as mock_get_customer, \
         patch.object(AIHandler, 'analyze_intent', new_callable=AsyncMock) as mock_analyze_intent, \
         patch.object(AIHandler, 'generate_response', new_callable=AsyncMock) as mock_generate_response:
        
        # Setup mocks
        mock_get_customer.return_value = test_customer
        mock_analyze_intent.return_value = {
            "intent": "help",
            "confidence": 0.9,
            "entities": {}
        }
        mock_generate_response.return_value = "Here's how I can help you..."
        
        # Process message
        response = await message_handler.process_message(
            "Help me please",
            test_customer.phone_number
        )
        
        # Verify response
        assert "help" in response.lower()
        mock_get_customer.assert_called_once_with(test_customer.phone_number)
        mock_analyze_intent.assert_called_once()
        mock_generate_response.assert_called_once()

@pytest.mark.asyncio
async def test_process_message_unknown_intent(message_handler, test_customer):
    """Test processing a message with unknown intent"""
    with patch.object(CustomerHandler, 'get_or_create_customer', new_callable=AsyncMock) as mock_get_customer, \
         patch.object(AIHandler, 'analyze_intent', new_callable=AsyncMock) as mock_analyze_intent, \
         patch.object(AIHandler, 'generate_response', new_callable=AsyncMock) as mock_generate_response:
        
        # Setup mocks
        mock_get_customer.return_value = test_customer
        mock_analyze_intent.return_value = {
            "intent": "unknown",
            "confidence": 0.3,
            "entities": {}
        }
        mock_generate_response.return_value = "I'm not sure I understand. Can you please rephrase?"
        
        # Process message
        response = await message_handler.process_message(
            "xyz123",
            test_customer.phone_number
        )
        
        # Verify response
        assert "not sure" in response.lower()
        mock_get_customer.assert_called_once_with(test_customer.phone_number)
        mock_analyze_intent.assert_called_once()
        mock_generate_response.assert_called_once()

@pytest.mark.asyncio
async def test_save_response(message_handler, test_customer, db_session):
    """Test saving a response message"""
    with patch.object(CustomerHandler, 'get_or_create_customer', new_callable=AsyncMock) as mock_get_customer, \
         patch('src.utils.message_handler.SessionLocal') as mock_session:
        
        # Setup mocks
        mock_get_customer.return_value = test_customer
        mock_session_instance = Mock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
        # Save response
        await message_handler.save_response(
            customer_id=test_customer.id,
            content="Test response",
            intent="test"
        )
        
        # Verify database interaction
        mock_session_instance.add.assert_called_once()
        mock_session_instance.commit.assert_called_once()

        # Check if response was saved
        saved_message = db_session.query(Message).filter(Message.customer_id == test_customer.id).first()
        assert saved_message is not None
        assert saved_message.content == "Test response"
        assert saved_message.direction == "outgoing"
        assert saved_message.customer_id == test_customer.id 