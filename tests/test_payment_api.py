import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from src.main import app
from src.services.payment import PaymentService
from src.handlers.payment import PaymentHandler
from src.data.crm_repository import CRMRepository

# Create test client
client = TestClient(app)

# Mock authentication
@pytest.fixture
def mock_auth():
    with patch("src.routers.payment.get_current_user") as mock:
        mock.return_value = {"id": "user123", "role": "customer"}
        yield mock

# Mock services
@pytest.fixture
def mock_payment_service():
    with patch("src.routers.payment.payment_service") as mock:
        yield mock

# Sample test data
@pytest.fixture
def sample_order():
    return {
        "id": "order123",
        "customer_id": "user123",
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

# Test process payment endpoint
def test_process_payment_success(mock_auth, mock_payment_service, sample_order, sample_payment):
    # Setup mocks
    mock_payment_service.process_order_payment.return_value = sample_payment
    
    # Make request
    response = client.post(
        "/payment/process",
        json={
            "order_id": "order123",
            "amount": 100.00,
            "currency": "USD",
            "channel": "card",
            "customer_id": "user123",
            "metadata": {"source": "web"}
        }
    )
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == sample_payment
    
    # Verify service was called correctly
    mock_payment_service.process_order_payment.assert_called_once_with(
        order_id="order123",
        amount=100.00,
        currency="USD",
        channel="card",
        customer_id="user123",
        metadata={"source": "web"}
    )

def test_process_payment_unauthorized(mock_auth, mock_payment_service):
    # Setup mocks to simulate unauthorized access
    mock_auth.return_value = {"id": "other_user", "role": "customer"}
    mock_payment_service.process_order_payment.side_effect = ValueError("Not authorized")
    
    # Make request
    response = client.post(
        "/payment/process",
        json={
            "order_id": "order123",
            "amount": 100.00,
            "currency": "USD",
            "channel": "card",
            "customer_id": "user123"
        }
    )
    
    # Verify response
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]

def test_process_payment_invalid_data(mock_auth, mock_payment_service):
    # Setup mocks
    mock_payment_service.process_order_payment.side_effect = ValueError("Invalid payment data")
    
    # Make request with invalid data
    response = client.post(
        "/payment/process",
        json={
            "order_id": "order123",
            "amount": -100.00,  # Invalid amount
            "currency": "USD",
            "channel": "card",
            "customer_id": "user123"
        }
    )
    
    # Verify response
    assert response.status_code == 400
    assert "Invalid payment data" in response.json()["detail"]

# Test webhook endpoint
def test_payment_webhook_success(mock_payment_service):
    # Setup mocks
    webhook_data = {"transaction_id": "txn123", "status": "completed"}
    mock_payment_service.handle_webhook.return_value = webhook_data
    
    # Make request
    response = client.post(
        "/payment/webhook/stripe",
        json={"type": "payment_intent.succeeded", "data": {"object": {"id": "pi_123"}}},
        headers={"stripe-signature": "test_signature"}
    )
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == webhook_data
    
    # Verify service was called correctly
    mock_payment_service.handle_webhook.assert_called_once()

def test_payment_webhook_invalid_signature(mock_payment_service):
    # Setup mocks
    mock_payment_service.handle_webhook.side_effect = ValueError("Invalid webhook signature")
    
    # Make request with invalid signature
    response = client.post(
        "/payment/webhook/stripe",
        json={"type": "payment_intent.succeeded", "data": {"object": {"id": "pi_123"}}},
        headers={"stripe-signature": "invalid_signature"}
    )
    
    # Verify response
    assert response.status_code == 400
    assert "Invalid webhook signature" in response.json()["detail"]

# Test refund endpoint
def test_process_refund_success(mock_auth, mock_payment_service):
    # Setup mocks
    refund_result = {
        "refund_id": "refund123",
        "amount": 100.00,
        "reason": "Customer request"
    }
    mock_payment_service.process_refund.return_value = refund_result
    
    # Make request
    response = client.post(
        "/payment/refund",
        json={
            "transaction_id": "txn123",
            "amount": 100.00,
            "reason": "Customer request"
        }
    )
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == refund_result
    
    # Verify service was called correctly
    mock_payment_service.process_refund.assert_called_once_with(
        transaction_id="txn123",
        amount=100.00,
        reason="Customer request"
    )

def test_process_refund_payment_not_found(mock_auth, mock_payment_service):
    # Setup mocks
    mock_payment_service.process_refund.side_effect = ValueError("Payment txn123 not found")
    
    # Make request
    response = client.post(
        "/payment/refund",
        json={
            "transaction_id": "txn123",
            "amount": 100.00,
            "reason": "Customer request"
        }
    )
    
    # Verify response
    assert response.status_code == 400
    assert "Payment txn123 not found" in response.json()["detail"]

# Test payment status endpoint
def test_get_payment_status_success(mock_auth, mock_payment_service, sample_payment):
    # Setup mocks
    mock_payment_service.get_payment_status.return_value = sample_payment
    
    # Make request
    response = client.get("/payment/status/txn123")
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == sample_payment
    
    # Verify service was called correctly
    mock_payment_service.get_payment_status.assert_called_once_with("txn123")

def test_get_payment_status_not_found(mock_auth, mock_payment_service):
    # Setup mocks
    mock_payment_service.get_payment_status.side_effect = ValueError("Payment txn123 not found")
    
    # Make request
    response = client.get("/payment/status/txn123")
    
    # Verify response
    assert response.status_code == 404
    assert "Payment txn123 not found" in response.json()["detail"]

# Test payment success callback endpoint
def test_payment_success_callback(mock_payment_service, sample_payment):
    # Setup mocks
    mock_payment_service.handle_payment_success.return_value = sample_payment
    
    # Make request
    response = client.get("/payment/success?payment_id=pay123")
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == sample_payment
    
    # Verify service was called correctly
    mock_payment_service.handle_payment_success.assert_called_once_with({"payment_id": "pay123"})

# Test payment cancel callback endpoint
def test_payment_cancel_callback(mock_payment_service):
    # Setup mocks
    cancel_result = {
        "transaction_id": "txn123",
        "status": "cancelled"
    }
    mock_payment_service.handle_payment_cancel.return_value = cancel_result
    
    # Make request
    response = client.get("/payment/cancel?payment_id=pay123")
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == cancel_result
    
    # Verify service was called correctly
    mock_payment_service.handle_payment_cancel.assert_called_once_with({"payment_id": "pay123"}) 