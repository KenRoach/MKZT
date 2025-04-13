import pytest
import os
from unittest.mock import patch, MagicMock, Mock
from src.utils.notification_handler import NotificationHandler
from datetime import datetime, timedelta

@pytest.fixture
def notification_handler():
    """Fixture to create a notification handler instance"""
    os.environ["SMTP_SERVER"] = "smtp.test.com"
    os.environ["SMTP_PORT"] = "587"
    os.environ["SMTP_USERNAME"] = "test@example.com"
    os.environ["SMTP_PASSWORD"] = "test_password"
    os.environ["SLACK_WEBHOOK_URL"] = "https://hooks.slack.com/services/test"
    return NotificationHandler()

@pytest.fixture
def mock_env_vars():
    """Set up environment variables for testing"""
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['SLACK_WEBHOOK_URL'] = 'https://hooks.slack.com/test'
    os.environ['ADMIN_EMAILS'] = 'admin1@test.com,admin2@test.com'
    os.environ['ADMIN_PHONE_NUMBERS'] = '+1234567890,+0987654321'
    os.environ['TWILIO_ACCOUNT_SID'] = 'test_sid'
    os.environ['TWILIO_AUTH_TOKEN'] = 'test_token'
    os.environ['TWILIO_FROM_NUMBER'] = '+1122334455'
    os.environ['ADMIN1_NOTIFICATION_PREFERENCES'] = 'slack,email,sms'
    os.environ['ADMIN2_NOTIFICATION_PREFERENCES'] = 'slack,email'
    yield
    # Clean up
    for key in ['ENVIRONMENT', 'SLACK_WEBHOOK_URL', 'ADMIN_EMAILS', 
                'ADMIN_PHONE_NUMBERS', 'TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN',
                'TWILIO_FROM_NUMBER', 'ADMIN1_NOTIFICATION_PREFERENCES',
                'ADMIN2_NOTIFICATION_PREFERENCES']:
        os.environ.pop(key, None)

@pytest.mark.asyncio
async def test_send_email_notification(notification_handler):
    """Test sending email notification"""
    with patch("smtplib.SMTP") as mock_smtp:
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        result = await notification_handler.send_email_notification(
            subject="Test Subject",
            message="Test Message"
        )
        
        assert result["status"] == "success"
        mock_smtp_instance.sendmail.assert_called_once()

@pytest.mark.asyncio
async def test_send_slack_notification_success(notification_handler):
    """Test successful Slack notification"""
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await notification_handler.send_slack_notification("Test message")
        assert result is True
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_send_slack_notification_failure(notification_handler):
    """Test failed Slack notification"""
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status = 500
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await notification_handler.send_slack_notification("Test message")
        assert result is False
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_notify_health_status(notification_handler):
    """Test health status notification"""
    health_status = {
        "status": "unhealthy",
        "checks": {
            "error_rate": {
                "status": "unhealthy",
                "value": 0.15,
                "threshold": 0.1
            },
            "response_time": {
                "status": "healthy",
                "value": 0.5,
                "threshold": 1.0
            }
        }
    }

    with patch.object(notification_handler, "send_slack_notification") as mock_send:
        await notification_handler.notify_health_status(health_status)
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        assert "Unhealthy Status Detected" in call_args[0]
        assert "error_rate" in call_args[0]
        assert "0.15" in call_args[0]
        assert call_args[1] == "error"

@pytest.mark.asyncio
async def test_notify_error(notification_handler):
    """Test error notification"""
    error = ValueError("Test error")
    context = {"path": "/api/test", "method": "GET"}

    with patch.object(notification_handler, "send_slack_notification") as mock_send:
        await notification_handler.notify_error(error, context)
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        assert "Error Occurred" in call_args[0]
        assert "ValueError" in call_args[0]
        assert "Test error" in call_args[0]
        assert "/api/test" in call_args[0]
        assert call_args[1] == "error"

@pytest.mark.asyncio
async def test_notify_metrics(notification_handler):
    """Test metrics notification"""
    metrics = {
        "total_requests": 100,
        "error_rate": 0.05,
        "avg_response_time": 0.3,
        "uptime_seconds": 3600,
        "consecutive_errors": 2
    }

    with patch.object(notification_handler, "send_slack_notification") as mock_send:
        await notification_handler.notify_metrics(metrics)
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        assert "Metrics Update" in call_args[0]
        assert "100" in call_args[0]
        assert "5.00%" in call_args[0]
        assert "0.30s" in call_args[0]
        assert "1.0h" in call_args[0]
        assert "2" in call_args[0]
        assert call_args[1] == "info"

@pytest.mark.asyncio
async def test_check_metrics_no_alerts(notification_handler):
    """Test checking metrics with no alerts"""
    metrics = {
        "error_rate": 0.01,
        "response_time": 0.5,
        "consecutive_errors": 0
    }
    
    with patch("src.utils.notification_handler.NotificationHandler.send_slack_notification") as mock_slack:
        await notification_handler.check_metrics(metrics)
        mock_slack.assert_not_called()

@pytest.mark.asyncio
async def test_check_metrics_high_error_rate(notification_handler):
    """Test checking metrics with high error rate"""
    metrics = {
        "error_rate": 0.15,
        "response_time": 0.5,
        "consecutive_errors": 0
    }
    
    with patch("src.utils.notification_handler.NotificationHandler.send_slack_notification") as mock_slack:
        await notification_handler.check_metrics(metrics)
        mock_slack.assert_called_once()

@pytest.mark.asyncio
async def test_check_metrics_high_response_time(notification_handler):
    """Test checking metrics with high response time"""
    metrics = {
        "error_rate": 0.01,
        "response_time": 2.0,
        "consecutive_errors": 0
    }
    
    with patch("src.utils.notification_handler.NotificationHandler.send_slack_notification") as mock_slack:
        await notification_handler.check_metrics(metrics)
        mock_slack.assert_called_once()

@pytest.mark.asyncio
async def test_check_metrics_consecutive_errors(notification_handler):
    """Test checking metrics with consecutive errors"""
    metrics = {
        "error_rate": 0.01,
        "response_time": 0.5,
        "consecutive_errors": 5
    }
    
    with patch("src.utils.notification_handler.NotificationHandler.send_slack_notification") as mock_slack:
        await notification_handler.check_metrics(metrics)
        mock_slack.assert_called_once()

@pytest.mark.asyncio
async def test_reset_error_counts(notification_handler):
    """Test resetting error counts"""
    notification_handler.error_counts = {"TestError": 5}
    notification_handler.reset_error_counts()
    assert notification_handler.error_counts == {}

@pytest.mark.asyncio
async def test_send_sms_notification_basic(notification_handler, mock_env_vars):
    """Test basic SMS notification sending"""
    message = "Test message"
    result = await notification_handler.send_sms_notification(message)
    
    assert result is True
    notification_handler.twilio_client.messages.create.assert_called_once()
    call_args = notification_handler.twilio_client.messages.create.call_args[1]
    assert call_args['body'].startswith('[TEST]')
    assert message in call_args['body']
    assert call_args['from_'] == '+1122334455'
    assert call_args['to'] == '+1234567890'

@pytest.mark.asyncio
async def test_send_sms_notification_rate_limiting(notification_handler, mock_env_vars):
    """Test SMS rate limiting"""
    message = "Test message"
    
    # Send first message
    await notification_handler.send_sms_notification(message, notification_type="test")
    
    # Try to send another message immediately
    result = await notification_handler.send_sms_notification(message, notification_type="test")
    
    assert result is False  # Should be rate limited
    assert notification_handler.twilio_client.messages.create.call_count == 1

@pytest.mark.asyncio
async def test_send_sms_notification_preferences(notification_handler, mock_env_vars):
    """Test SMS notifications respect user preferences"""
    message = "Test message"
    
    # Send to all recipients
    await notification_handler.send_sms_notification(message)
    
    # Should only send to admin1 who has SMS in preferences
    assert notification_handler.twilio_client.messages.create.call_count == 1
    call_args = notification_handler.twilio_client.messages.create.call_args[1]
    assert call_args['to'] == '+1234567890'  # admin1's number

@pytest.mark.asyncio
async def test_send_sms_notification_formatting(notification_handler, mock_env_vars):
    """Test SMS message formatting"""
    message = "Test message"
    
    # Test high priority
    await notification_handler.send_sms_notification(
        message,
        notification_type="error_alert",
        priority="high",
        include_link=True,
        link_url="http://test.com"
    )
    
    call_args = notification_handler.twilio_client.messages.create.call_args[1]
    formatted_message = call_args['body']
    
    assert '[TEST]' in formatted_message
    assert '🚨' in formatted_message
    assert 'ERROR:' in formatted_message
    assert message in formatted_message
    assert 'View details: http://test.com' in formatted_message
    assert 'Time:' in formatted_message

@pytest.mark.asyncio
async def test_notify_health_status_sms(notification_handler, mock_env_vars):
    """Test health status SMS notifications"""
    health_status = {
        "status": "unhealthy",
        "checks": {
            "database": {
                "status": "unhealthy",
                "value": "connection failed",
                "threshold": "connected",
                "severity": "high"
            },
            "api": {
                "status": "unhealthy",
                "value": "timeout",
                "threshold": "responsive",
                "severity": "medium"
            }
        }
    }
    
    await notification_handler.notify_health_status(health_status)
    
    # Should send SMS for high severity issues
    call_args = notification_handler.twilio_client.messages.create.call_args[1]
    formatted_message = call_args['body']
    
    assert '[TEST]' in formatted_message
    assert '🚨' in formatted_message
    assert 'HEALTH:' in formatted_message
    assert 'database' in formatted_message.lower()
    assert 'connection failed' in formatted_message.lower()
    assert 'api' not in formatted_message.lower()  # Should not include medium severity

@pytest.mark.asyncio
async def test_notify_error_sms(notification_handler, mock_env_vars):
    """Test error SMS notifications"""
    error = ValueError("Test error")
    context = {"path": "/test", "method": "GET"}
    
    await notification_handler.notify_error(error, context)
    
    call_args = notification_handler.twilio_client.messages.create.call_args[1]
    formatted_message = call_args['body']
    
    assert '[TEST]' in formatted_message
    assert '🚨' in formatted_message
    assert 'ERROR:' in formatted_message
    assert 'ValueError' in formatted_message
    assert 'Test error' in formatted_message
    assert 'View details:' in formatted_message

@pytest.mark.asyncio
async def test_notify_metrics_sms(notification_handler, mock_env_vars):
    """Test metrics SMS notifications"""
    metrics = {
        "total_requests": 1000,
        "error_rate": 0.15,
        "avg_response_time": 0.5,
        "uptime_seconds": 3600,
        "consecutive_errors": 3,
        "system_metrics": {
            "current_memory_usage_mb": 512,
            "current_cpu_usage_percent": 85
        }
    }
    
    await notification_handler.notify_metrics(metrics)
    
    call_args = notification_handler.twilio_client.messages.create.call_args[1]
    formatted_message = call_args['body']
    
    assert '[TEST]' in formatted_message
    assert '⚠️' in formatted_message  # Medium priority
    assert 'METRICS:' in formatted_message
    assert '15.0%' in formatted_message
    assert '85.0%' in formatted_message
    assert 'View details:' in formatted_message

@pytest.mark.asyncio
async def test_notify_metrics_sms_high_priority(notification_handler, mock_env_vars):
    """Test metrics SMS notifications with high priority"""
    metrics = {
        "total_requests": 1000,
        "error_rate": 0.25,  # High error rate
        "avg_response_time": 0.5,
        "uptime_seconds": 3600,
        "consecutive_errors": 6,  # High consecutive errors
        "system_metrics": {
            "current_memory_usage_mb": 512,
            "current_cpu_usage_percent": 85
        }
    }
    
    await notification_handler.notify_metrics(metrics)
    
    call_args = notification_handler.twilio_client.messages.create.call_args[1]
    formatted_message = call_args['body']
    
    assert '[TEST]' in formatted_message
    assert '🚨' in formatted_message  # High priority
    assert 'METRICS:' in formatted_message
    assert '25.0%' in formatted_message
    assert '85.0%' in formatted_message
    assert 'View details:' in formatted_message 