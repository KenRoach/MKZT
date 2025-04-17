import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from src.services.payment import PaymentService
from src.handlers.payment import PaymentHandler
from src.data.crm_repository import CRMRepository

@pytest.fixture
def mock_payment_handler():
    return Mock(spec=PaymentHandler)

@pytest.fixture
def mock_crm_repository():
    return Mock(spec=CRMRepository)

@pytest.fixture
def payment_service(mock_payment_handler, mock_crm_repository):
    return PaymentService(mock_payment_handler, mock_crm_repository)

@pytest.fixture
def sample_order():
    return {
        "id": "order123",
        "customer_id": "customer123",
        "total_amount": 100.00,
        "status": "pending"
    }

@pytest.fixture
def sample_payment():
    return {
        "transaction_id": "txn123",
        "amount": 100.00,
        "currency": "USD",
        "status": "completed",
        "payment_method": "card",
        "metadata": {"order_id": "order123"}
    }

@pytest.mark.asyncio
async def test_process_order_payment_success(payment_service, mock_payment_handler, mock_crm_repository, sample_order, sample_payment):
    # Setup mocks
    mock_crm_repository.get_order.return_value = sample_order
    mock_payment_handler.process_payment.return_value = sample_payment
    
    # Execute
    result = await payment_service.process_order_payment(
        order_id="order123",
        amount=100.00,
        currency="USD",
        channel="card",
        customer_id="customer123"
    )
    
    # Verify
    assert result == sample_payment
    mock_crm_repository.get_order.assert_called_once_with("order123")
    mock_payment_handler.process_payment.assert_called_once()
    mock_crm_repository.update_order_payment.assert_called_once()

@pytest.mark.asyncio
async def test_process_order_payment_order_not_found(payment_service, mock_crm_repository):
    # Setup mocks
    mock_crm_repository.get_order.return_value = None
    
    # Execute and verify
    with pytest.raises(ValueError, match="Order order123 not found"):
        await payment_service.process_order_payment(
            order_id="order123",
            amount=100.00,
            currency="USD",
            channel="card",
            customer_id="customer123"
        )

@pytest.mark.asyncio
async def test_process_order_payment_amount_mismatch(payment_service, mock_crm_repository, sample_order):
    # Setup mocks
    mock_crm_repository.get_order.return_value = sample_order
    
    # Execute and verify
    with pytest.raises(ValueError, match="Payment amount 150.00 does not match order total 100.00"):
        await payment_service.process_order_payment(
            order_id="order123",
            amount=150.00,
            currency="USD",
            channel="card",
            customer_id="customer123"
        )

@pytest.mark.asyncio
async def test_process_refund_success(payment_service, mock_payment_handler, mock_crm_repository, sample_payment):
    # Setup mocks
    mock_crm_repository.get_payment.return_value = sample_payment
    mock_payment_handler.process_refund.return_value = {
        "refund_id": "refund123",
        "amount": 100.00,
        "reason": "Customer request"
    }
    
    # Execute
    result = await payment_service.process_refund(
        transaction_id="txn123",
        amount=100.00,
        reason="Customer request"
    )
    
    # Verify
    assert result["refund_id"] == "refund123"
    mock_crm_repository.get_payment.assert_called_once_with("txn123")
    mock_payment_handler.process_refund.assert_called_once()
    mock_crm_repository.update_payment_status.assert_called_once()

@pytest.mark.asyncio
async def test_process_refund_payment_not_found(payment_service, mock_crm_repository):
    # Setup mocks
    mock_crm_repository.get_payment.return_value = None
    
    # Execute and verify
    with pytest.raises(ValueError, match="Payment txn123 not found"):
        await payment_service.process_refund(
            transaction_id="txn123",
            amount=100.00,
            reason="Customer request"
        )

@pytest.mark.asyncio
async def test_process_refund_amount_exceeds_payment(payment_service, mock_crm_repository, sample_payment):
    # Setup mocks
    mock_crm_repository.get_payment.return_value = sample_payment
    
    # Execute and verify
    with pytest.raises(ValueError, match="Refund amount 150.00 cannot exceed payment amount 100.00"):
        await payment_service.process_refund(
            transaction_id="txn123",
            amount=150.00,
            reason="Customer request"
        )

@pytest.mark.asyncio
async def test_get_payment_status_success(payment_service, mock_payment_handler, mock_crm_repository, sample_payment):
    # Setup mocks
    mock_payment_handler.get_payment_status.return_value = {"status": "completed"}
    mock_crm_repository.get_payment.return_value = sample_payment
    
    # Execute
    result = await payment_service.get_payment_status("txn123")
    
    # Verify
    assert result["status"] == "completed"
    mock_payment_handler.get_payment_status.assert_called_once_with("txn123")
    mock_crm_repository.get_payment.assert_called_once_with("txn123")

@pytest.mark.asyncio
async def test_handle_webhook_success(payment_service, mock_payment_handler):
    # Setup mocks
    webhook_data = {"transaction_id": "txn123", "status": "completed"}
    mock_payment_handler.process_webhook.return_value = webhook_data
    
    # Execute
    result = await payment_service.handle_webhook(
        channel="stripe",
        body=b"{}",
        headers={"stripe-signature": "test"}
    )
    
    # Verify
    assert result == webhook_data
    mock_payment_handler.process_webhook.assert_called_once()

@pytest.mark.asyncio
async def test_handle_payment_success(payment_service, mock_payment_handler, mock_crm_repository, sample_payment):
    # Setup mocks
    mock_payment_handler.execute_payment.return_value = sample_payment
    
    # Execute
    result = await payment_service.handle_payment_success({"payment_id": "pay123"})
    
    # Verify
    assert result == sample_payment
    mock_payment_handler.execute_payment.assert_called_once_with("pay123")
    mock_crm_repository.update_payment_status.assert_called_once()

@pytest.mark.asyncio
async def test_handle_payment_cancel(payment_service, mock_payment_handler, mock_crm_repository):
    # Setup mocks
    mock_payment_handler.cancel_payment.return_value = {
        "transaction_id": "txn123",
        "status": "cancelled"
    }
    
    # Execute
    result = await payment_service.handle_payment_cancel({"payment_id": "pay123"})
    
    # Verify
    assert result["status"] == "cancelled"
    mock_payment_handler.cancel_payment.assert_called_once_with("pay123")
    mock_crm_repository.update_payment_status.assert_called_once() 