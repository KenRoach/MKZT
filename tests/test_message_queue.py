import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from src.services.queue import MessageQueue
from src.services.notifications import NotificationService

@pytest.fixture
def mock_notification_service():
    return Mock(spec=NotificationService)

@pytest.fixture
def message_queue(mock_notification_service):
    with patch("src.services.queue.NotificationService", return_value=mock_notification_service):
        queue = MessageQueue()
        return queue

@pytest.fixture
def sample_notification():
    return {
        "id": "notification123",
        "order_id": "order123",
        "customer_id": "customer123",
        "channel": "whatsapp",
        "message": "Your order has been confirmed!",
        "order": {
            "order_id": "order123",
            "customer_id": "customer123",
            "customer_phone": "+1234567890"
        }
    }

@pytest.mark.asyncio
async def test_enqueue_notification(message_queue, sample_notification):
    # Execute
    await message_queue.enqueue_notification(sample_notification)
    
    # Verify
    assert message_queue.queue.qsize() == 1
    queued_item = await message_queue.queue.get()
    assert queued_item["id"] == sample_notification["id"]
    assert queued_item["channel"] == sample_notification["channel"]
    assert "timestamp" in queued_item
    assert queued_item["attempts"] == 0

@pytest.mark.asyncio
async def test_process_notification_success(message_queue, mock_notification_service, sample_notification):
    # Setup mocks
    mock_notification_service.send_whatsapp_notification = AsyncMock(return_value=True)
    
    # Add notification to queue
    await message_queue.enqueue_notification(sample_notification)
    
    # Execute
    await message_queue._process_notification(await message_queue.queue.get())
    
    # Verify
    mock_notification_service.send_whatsapp_notification.assert_called_once_with(
        sample_notification["order"],
        sample_notification["message"]
    )

@pytest.mark.asyncio
async def test_process_notification_failure_with_retry(message_queue, mock_notification_service, sample_notification):
    # Setup mocks
    mock_notification_service.send_whatsapp_notification = AsyncMock(return_value=False)
    
    # Add notification to queue
    await message_queue.enqueue_notification(sample_notification)
    
    # Execute
    await message_queue._process_notification(await message_queue.queue.get())
    
    # Verify
    assert message_queue.queue.qsize() == 1
    retried_item = await message_queue.queue.get()
    assert retried_item["id"] == sample_notification["id"]
    assert retried_item["attempts"] == 1
    mock_notification_service.send_whatsapp_notification.assert_called_once()

@pytest.mark.asyncio
async def test_process_notification_max_retries_exceeded(message_queue, mock_notification_service, sample_notification):
    # Setup mocks
    mock_notification_service.send_whatsapp_notification = AsyncMock(return_value=False)
    
    # Add notification to queue with max retries already attempted
    notification_with_max_retries = {**sample_notification, "attempts": 3}
    await message_queue.enqueue_notification(notification_with_max_retries)
    
    # Execute
    await message_queue._process_notification(await message_queue.queue.get())
    
    # Verify
    assert message_queue.queue.qsize() == 0  # Should not be requeued
    mock_notification_service.send_whatsapp_notification.assert_called_once()

@pytest.mark.asyncio
async def test_process_notification_exception_with_retry(message_queue, mock_notification_service, sample_notification):
    # Setup mocks
    mock_notification_service.send_whatsapp_notification = AsyncMock(side_effect=Exception("API Error"))
    
    # Add notification to queue
    await message_queue.enqueue_notification(sample_notification)
    
    # Execute
    await message_queue._process_notification(await message_queue.queue.get())
    
    # Verify
    assert message_queue.queue.qsize() == 1
    retried_item = await message_queue.queue.get()
    assert retried_item["id"] == sample_notification["id"]
    assert retried_item["attempts"] == 1
    mock_notification_service.send_whatsapp_notification.assert_called_once()

@pytest.mark.asyncio
async def test_start_and_stop_queue(message_queue):
    # Start queue
    message_queue.start()
    assert message_queue.is_processing is True
    
    # Stop queue
    message_queue.stop()
    assert message_queue.is_processing is False

@pytest.mark.asyncio
async def test_get_queue_stats(message_queue, sample_notification):
    # Add notification to queue
    await message_queue.enqueue_notification(sample_notification)
    
    # Execute
    stats = await message_queue.get_queue_stats()
    
    # Verify
    assert stats["queue_size"] == 1
    assert stats["is_processing"] == message_queue.is_processing
    assert stats["max_concurrent"] == message_queue.max_concurrent
    assert stats["rate_limit"] == message_queue.rate_limit

@pytest.mark.asyncio
async def test_process_queue_multiple_notifications(message_queue, mock_notification_service):
    # Setup mocks
    mock_notification_service.send_whatsapp_notification = AsyncMock(return_value=True)
    
    # Add multiple notifications to queue
    notifications = [
        {
            "id": f"notification{i}",
            "order_id": f"order{i}",
            "customer_id": f"customer{i}",
            "channel": "whatsapp",
            "message": f"Message {i}",
            "order": {"order_id": f"order{i}", "customer_id": f"customer{i}"}
        }
        for i in range(3)
    ]
    
    for notification in notifications:
        await message_queue.enqueue_notification(notification)
    
    # Start queue processing
    message_queue.start()
    
    # Wait for processing to complete
    await asyncio.sleep(0.1)
    
    # Stop queue
    message_queue.stop()
    
    # Verify
    assert message_queue.queue.qsize() == 0
    assert mock_notification_service.send_whatsapp_notification.call_count == 3 