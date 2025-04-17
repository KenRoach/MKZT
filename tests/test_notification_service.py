import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from src.services.notifications import NotificationService
from src.services.database import DatabaseService
from src.services.voice_notes import VoiceNoteService

@pytest.fixture
def mock_db():
    return Mock(spec=DatabaseService)

@pytest.fixture
def mock_voice_service():
    return Mock(spec=VoiceNoteService)

@pytest.fixture
def notification_service(mock_db, mock_voice_service):
    with patch("src.services.notifications.DatabaseService", return_value=mock_db), \
         patch("src.services.notifications.VoiceNoteService", return_value=mock_voice_service):
        service = NotificationService()
        return service

@pytest.fixture
def sample_order():
    return {
        "order_id": "order123",
        "customer_id": "customer123",
        "customer_phone": "+1234567890",
        "customer_email": "customer@example.com",
        "customer_instagram": "customer_instagram",
        "total_amount": 100.00,
        "status": "pending"
    }

@pytest.mark.asyncio
async def test_send_whatsapp_notification_success(notification_service, sample_order, mock_db):
    # Setup mocks
    mock_db.log_notification = AsyncMock()
    mock_db.update_notification_status = AsyncMock()
    
    # Execute
    result = await notification_service.send_whatsapp_notification(
        sample_order,
        "Your order has been confirmed!"
    )
    
    # Verify
    assert result is True
    mock_db.log_notification.assert_called_once()
    mock_db.update_notification_status.assert_called_once_with(
        mock_db.log_notification.call_args[0][0]["id"],
        "delivered",
        None
    )

@pytest.mark.asyncio
async def test_send_whatsapp_notification_failure(notification_service, sample_order, mock_db):
    # Setup mocks
    mock_db.log_notification = AsyncMock()
    mock_db.update_notification_status = AsyncMock()
    
    # Mock the internal method to simulate failure
    with patch.object(notification_service, "_send_whatsapp_message", return_value=False):
        # Execute
        result = await notification_service.send_whatsapp_notification(
            sample_order,
            "Your order has been confirmed!"
        )
        
        # Verify
        assert result is False
        mock_db.log_notification.assert_called_once()
        mock_db.update_notification_status.assert_called_once_with(
            mock_db.log_notification.call_args[0][0]["id"],
            "failed",
            None
        )

@pytest.mark.asyncio
async def test_send_email_notification_success(notification_service, sample_order, mock_db):
    # Setup mocks
    mock_db.log_notification = AsyncMock()
    mock_db.update_notification_status = AsyncMock()
    
    # Execute
    result = await notification_service.send_email_notification(
        sample_order,
        "Your order has been confirmed!"
    )
    
    # Verify
    assert result is True
    mock_db.log_notification.assert_called_once()
    mock_db.update_notification_status.assert_called_once_with(
        mock_db.log_notification.call_args[0][0]["id"],
        "delivered",
        None
    )

@pytest.mark.asyncio
async def test_send_sms_notification_success(notification_service, sample_order, mock_db):
    # Setup mocks
    mock_db.log_notification = AsyncMock()
    mock_db.update_notification_status = AsyncMock()
    
    # Execute
    result = await notification_service.send_sms_notification(
        sample_order,
        "Your order has been confirmed!"
    )
    
    # Verify
    assert result is True
    mock_db.log_notification.assert_called_once()
    mock_db.update_notification_status.assert_called_once_with(
        mock_db.log_notification.call_args[0][0]["id"],
        "delivered",
        None
    )

@pytest.mark.asyncio
async def test_send_instagram_notification_success(notification_service, sample_order, mock_db):
    # Setup mocks
    mock_db.log_notification = AsyncMock()
    mock_db.update_notification_status = AsyncMock()
    
    # Execute
    result = await notification_service.send_instagram_notification(
        sample_order,
        "Your order has been confirmed!"
    )
    
    # Verify
    assert result is True
    mock_db.log_notification.assert_called_once()
    mock_db.update_notification_status.assert_called_once_with(
        mock_db.log_notification.call_args[0][0]["id"],
        "delivered",
        None
    )

@pytest.mark.asyncio
async def test_send_voice_notification_success(notification_service, sample_order, mock_db, mock_voice_service):
    # Setup mocks
    mock_db.log_notification = AsyncMock()
    mock_db.update_notification_status = AsyncMock()
    mock_voice_service.send_voice_notification = AsyncMock(return_value=True)
    
    # Execute
    result = await notification_service.send_voice_notification(
        sample_order,
        "Your order has been confirmed!"
    )
    
    # Verify
    assert result is True
    mock_voice_service.send_voice_notification.assert_called_once_with(
        sample_order,
        "Your order has been confirmed!"
    )

@pytest.mark.asyncio
async def test_notification_retry_mechanism(notification_service, sample_order, mock_db):
    # Setup mocks
    mock_db.log_notification = AsyncMock()
    mock_db.update_notification_status = AsyncMock()
    
    # Mock the internal method to fail twice then succeed
    with patch.object(notification_service, "_send_whatsapp_message") as mock_send:
        mock_send.side_effect = [False, False, True]
        
        # Execute
        result = await notification_service.send_whatsapp_notification(
            sample_order,
            "Your order has been confirmed!"
        )
        
        # Verify
        assert result is True
        assert mock_send.call_count == 3
        mock_db.log_notification.assert_called_once()
        mock_db.update_notification_status.assert_called_once_with(
            mock_db.log_notification.call_args[0][0]["id"],
            "delivered",
            None
        )

@pytest.mark.asyncio
async def test_notification_max_retries_exceeded(notification_service, sample_order, mock_db):
    # Setup mocks
    mock_db.log_notification = AsyncMock()
    mock_db.update_notification_status = AsyncMock()
    
    # Mock the internal method to always fail
    with patch.object(notification_service, "_send_whatsapp_message", return_value=False):
        # Execute
        result = await notification_service.send_whatsapp_notification(
            sample_order,
            "Your order has been confirmed!"
        )
        
        # Verify
        assert result is False
        mock_db.log_notification.assert_called_once()
        mock_db.update_notification_status.assert_called_once_with(
            mock_db.log_notification.call_args[0][0]["id"],
            "failed",
            None
        )

@pytest.mark.asyncio
async def test_notification_exception_handling(notification_service, sample_order, mock_db):
    # Setup mocks
    mock_db.log_notification = AsyncMock()
    mock_db.update_notification_status = AsyncMock()
    
    # Mock the internal method to raise an exception
    with patch.object(notification_service, "_send_whatsapp_message", side_effect=Exception("API Error")):
        # Execute
        result = await notification_service.send_whatsapp_notification(
            sample_order,
            "Your order has been confirmed!"
        )
        
        # Verify
        assert result is False
        mock_db.log_notification.assert_called_once()
        mock_db.update_notification_status.assert_called_once_with(
            mock_db.log_notification.call_args[0][0]["id"],
            "failed",
            "API Error"
        ) 