import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from src.services.messaging_service import MessagingService
from src.data.crm_repository import CRMRepository

@pytest.fixture
def mock_crm_repository():
    return Mock(spec=CRMRepository)

@pytest.fixture
def mock_yappy_client():
    return Mock()

@pytest.fixture
def messaging_service(mock_crm_repository, mock_yappy_client):
    with patch("src.services.messaging_service.CRMRepository", return_value=mock_crm_repository), \
         patch("src.services.messaging_service.YappyClient", return_value=mock_yappy_client):
        service = MessagingService()
        return service

@pytest.fixture
def sample_order():
    return {
        "id": "order123",
        "customer_id": "customer123",
        "total_amount": 100.00,
        "status": "pending",
        "items": [
            {"name": "Item 1", "quantity": 2, "price": 30.00},
            {"name": "Item 2", "quantity": 1, "price": 40.00}
        ]
    }

@pytest.fixture
def sample_customer():
    return {
        "id": "customer123",
        "name": "John Doe",
        "email": "john@example.com",
        "phone_number": "+1234567890"
    }

@pytest.mark.asyncio
async def test_send_order_confirmation_success(messaging_service, mock_crm_repository, sample_order, sample_customer):
    # Setup mocks
    mock_crm_repository.get_order_by_id.return_value = sample_order
    mock_crm_repository.get_customer_by_id.return_value = sample_customer
    mock_crm_repository.send_message = AsyncMock(return_value={"status": "success"})
    
    # Execute
    result = await messaging_service.send_order_confirmation("order123", "whatsapp")
    
    # Verify
    assert result["status"] == "success"
    assert "Order confirmation sent to all stakeholders" in result["message"]
    mock_crm_repository.get_order_by_id.assert_called_once_with("order123")
    mock_crm_repository.get_customer_by_id.assert_called_once_with("customer123")
    mock_crm_repository.send_message.assert_called()

@pytest.mark.asyncio
async def test_send_order_confirmation_order_not_found(messaging_service, mock_crm_repository):
    # Setup mocks
    mock_crm_repository.get_order_by_id.return_value = None
    
    # Execute and verify
    with pytest.raises(ValueError, match="Order not found: order123"):
        await messaging_service.send_order_confirmation("order123", "whatsapp")
    
    # Verify
    mock_crm_repository.get_order_by_id.assert_called_once_with("order123")
    mock_crm_repository.get_customer_by_id.assert_not_called()
    mock_crm_repository.send_message.assert_not_called()

@pytest.mark.asyncio
async def test_send_payment_request_success(messaging_service, mock_crm_repository, mock_yappy_client, sample_order, sample_customer):
    # Setup mocks
    mock_crm_repository.get_order_by_id.return_value = sample_order
    mock_crm_repository.get_customer_by_id.return_value = sample_customer
    mock_yappy_client.create_payment_link.return_value = "https://payment.example.com/pay123"
    mock_crm_repository.send_message = AsyncMock(return_value={"status": "success"})
    
    # Execute
    result = await messaging_service.send_payment_request("order123", 100.00, "whatsapp")
    
    # Verify
    assert result["status"] == "success"
    mock_crm_repository.get_order_by_id.assert_called_once_with("order123")
    mock_crm_repository.get_customer_by_id.assert_called_once_with("customer123")
    mock_yappy_client.create_payment_link.assert_called_once_with(
        amount=100.00,
        description="Order #order123",
        customer_name="John Doe",
        customer_email="john@example.com",
        customer_phone="+1234567890"
    )
    mock_crm_repository.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_send_payment_request_order_not_found(messaging_service, mock_crm_repository):
    # Setup mocks
    mock_crm_repository.get_order_by_id.return_value = None
    
    # Execute and verify
    with pytest.raises(ValueError, match="Order not found: order123"):
        await messaging_service.send_payment_request("order123", 100.00, "whatsapp")
    
    # Verify
    mock_crm_repository.get_order_by_id.assert_called_once_with("order123")
    mock_crm_repository.get_customer_by_id.assert_not_called()
    mock_yappy_client.create_payment_link.assert_not_called()
    mock_crm_repository.send_message.assert_not_called()

@pytest.mark.asyncio
async def test_send_message_success(messaging_service, mock_crm_repository):
    # Setup mocks
    mock_crm_repository.send_message = AsyncMock(return_value={"status": "success"})
    
    # Execute
    result = await messaging_service.send_message(
        recipient_id="customer123",
        recipient_type="customer",
        message="Test message",
        channel="whatsapp"
    )
    
    # Verify
    assert result["status"] == "success"
    mock_crm_repository.send_message.assert_called_once_with(
        recipient_id="customer123",
        recipient_type="customer",
        message="Test message",
        channel="whatsapp",
        buttons=None,
        payment_link=None
    )

@pytest.mark.asyncio
async def test_format_message_with_payment_link(messaging_service):
    # Execute
    formatted_message = messaging_service._format_message(
        message="Please pay for your order",
        channel="whatsapp",
        payment_link="https://payment.example.com/pay123"
    )
    
    # Verify
    assert "Please pay for your order" in formatted_message
    assert "https://payment.example.com/pay123" in formatted_message

@pytest.mark.asyncio
async def test_format_message_with_buttons(messaging_service):
    # Execute
    formatted_message = messaging_service._format_message(
        message="Please select an option",
        channel="whatsapp",
        buttons=[
            {"text": "Option 1"},
            {"text": "Option 2"}
        ]
    )
    
    # Verify
    assert "Please select an option" in formatted_message
    assert "1. Option 1" in formatted_message
    assert "2. Option 2" in formatted_message

@pytest.mark.asyncio
async def test_generate_order_confirmation_message_customer(messaging_service, sample_order):
    # Execute
    message = messaging_service._generate_order_confirmation_message(sample_order, "customer")
    
    # Verify
    assert "Order Confirmed!" in message
    assert "order123" in message
    assert "100.00" in message

@pytest.mark.asyncio
async def test_generate_order_confirmation_message_merchant(messaging_service, sample_order):
    # Execute
    message = messaging_service._generate_order_confirmation_message(sample_order, "merchant")
    
    # Verify
    assert "New Order Received!" in message
    assert "order123" in message
    assert "100.00" in message

@pytest.mark.asyncio
async def test_generate_order_confirmation_message_driver(messaging_service, sample_order):
    # Add delivery information to order
    order_with_delivery = {
        **sample_order,
        "merchant_address": "123 Merchant St",
        "delivery_address": "456 Customer Ave"
    }
    
    # Execute
    message = messaging_service._generate_order_confirmation_message(order_with_delivery, "driver")
    
    # Verify
    assert "New Delivery Assignment!" in message
    assert "order123" in message
    assert "123 Merchant St" in message
    assert "456 Customer Ave" in message

@pytest.mark.asyncio
async def test_generate_payment_request_message(messaging_service, sample_order):
    # Execute
    message = messaging_service._generate_payment_request_message(
        sample_order,
        100.00,
        "https://payment.example.com/pay123"
    )
    
    # Verify
    assert "Payment Request for Order" in message
    assert "order123" in message
    assert "100.00" in message
    assert "https://payment.example.com/pay123" in message 