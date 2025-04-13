# Notification Handler

The Notification Handler is a component that manages sending alerts and notifications through multiple channels (Slack, email, and SMS) when important events occur in the system.

## Features

- **Multi-Channel Notifications**: Send alerts via Slack, email, and SMS
- **Priority Levels**: Support for high, medium, and low priority notifications
- **Rate Limiting**: Prevents notification spam with configurable rate limits
- **User Preferences**: Respects user notification channel preferences
- **Rich Formatting**: Supports formatted messages with links and emojis
- **Environment Awareness**: Includes environment context in all notifications

## Configuration

The Notification Handler uses the following environment variables:

```
# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz

# Email Configuration
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=notifications@example.com
SMTP_PASSWORD=your_password
FROM_EMAIL=notifications@example.com
ADMIN_EMAILS=admin1@example.com,admin2@example.com

# SMS Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
ADMIN_PHONE_NUMBERS=+1234567890,+0987654321

# Notification Preferences
ADMIN1_NOTIFICATION_PREFERENCES=slack,email,sms
ADMIN2_NOTIFICATION_PREFERENCES=slack,email

# Rate Limiting
SMS_RATE_LIMIT=10
SMS_COOLDOWN_MINUTES=30

# Environment
ENVIRONMENT=development
```

## Usage

### Basic Usage

```python
from src.utils.notification_handler import NotificationHandler

# Initialize the handler
notification_handler = NotificationHandler()

# Send a notification
await notification_handler.send_slack_notification("Test message")
await notification_handler.send_email_notification("Test Subject", "Test message")
await notification_handler.send_sms_notification("Test message")
```

### Notification Types

The handler supports several notification types:

1. **Health Status Notifications**
   ```python
   health_status = {
       "status": "unhealthy",
       "checks": {
           "database": {
               "status": "unhealthy",
               "value": "connection failed",
               "threshold": "connected",
               "severity": "high"
           }
       }
   }
   await notification_handler.notify_health_status(health_status)
   ```

2. **Error Notifications**
   ```python
   error = ValueError("Test error")
   context = {"path": "/test", "method": "GET"}
   await notification_handler.notify_error(error, context)
   ```

3. **Metrics Notifications**
   ```python
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
   ```

### SMS Notifications

SMS notifications support additional parameters:

```python
await notification_handler.send_sms_notification(
    message="Test message",
    notification_type="error_alert",
    priority="high",
    include_link=True,
    link_url="http://example.com"
)
```

Parameters:
- `message`: The message to send
- `notification_type`: Type of notification (e.g., "error_alert", "health_alert", "metrics_alert")
- `priority`: Priority level ("high", "medium", "low")
- `include_link`: Whether to include a link in the message
- `link_url`: URL to include in the message

### Rate Limiting

The handler implements rate limiting for SMS notifications:

- Maximum number of SMS per hour (configurable via `SMS_RATE_LIMIT`)
- Cooldown period between SMS to the same recipient (configurable via `SMS_COOLDOWN_MINUTES`)

### User Preferences

Users can specify their preferred notification channels:

```
ADMIN1_NOTIFICATION_PREFERENCES=slack,email,sms
ADMIN2_NOTIFICATION_PREFERENCES=slack,email
```

The handler will only send notifications to users through their preferred channels.

## Message Formatting

### Slack Messages

Slack messages include:
- Environment prefix (e.g., "[PROD]")
- Priority indicator (🚨 for high, ⚠️ for medium, ℹ️ for low)
- Notification type header
- Formatted message content
- Links (if applicable)
- Timestamp

### Email Messages

Email messages include:
- Environment prefix in subject
- Priority indicator in subject
- Formatted HTML content
- Links (if applicable)
- Timestamp

### SMS Messages

SMS messages include:
- Environment prefix
- Priority indicator (🚨 for high, ⚠️ for medium, ℹ️ for low)
- Notification type indicator
- Concise message content
- Link (if requested)
- Timestamp

## Testing

The notification handler includes comprehensive tests in `tests/test_notification_handler.py`. Run the tests with:

```
pytest tests/test_notification_handler.py
```

## Troubleshooting

### Common Issues

1. **Notifications not being sent**
   - Check that the environment variables are correctly set
   - Verify that the notification channels (Slack, email, SMS) are properly configured
   - Check user preferences to ensure notifications are enabled for the desired channels

2. **Rate limiting issues**
   - If SMS notifications are not being sent, check if rate limits are being hit
   - Adjust the `SMS_RATE_LIMIT` and `SMS_COOLDOWN_MINUTES` settings if needed

3. **Formatting issues**
   - Ensure that message content is properly formatted
   - Check that links are correctly formatted and included when requested

## API Reference

### Methods

#### `__init__()`

Initializes the notification handler with configuration from environment variables.

#### `send_slack_notification(message, level="info")`

Sends a notification to Slack.

Parameters:
- `message`: The message to send
- `level`: The notification level ("info", "warning", "error")

Returns:
- `bool`: True if the notification was sent successfully, False otherwise

#### `send_email_notification(subject, message, recipients=None)`

Sends an email notification.

Parameters:
- `subject`: The email subject
- `message`: The email message
- `recipients`: List of recipients (defaults to admin emails)

Returns:
- `bool`: True if the notification was sent successfully, False otherwise

#### `send_sms_notification(message, recipients=None, notification_type="general", priority="normal", include_link=False, link_url=None)`

Sends an SMS notification.

Parameters:
- `message`: The message to send
- `recipients`: List of recipients (defaults to admin phone numbers)
- `notification_type`: Type of notification
- `priority`: Priority level
- `include_link`: Whether to include a link
- `link_url`: URL to include

Returns:
- `bool`: True if the notification was sent successfully, False otherwise

#### `notify_health_status(health_status)`

Sends notifications about system health status.

Parameters:
- `health_status`: Dictionary containing health status information

#### `notify_error(error, context=None)`

Sends notifications about errors.

Parameters:
- `error`: The error that occurred
- `context`: Additional context about the error

#### `notify_metrics(metrics)`

Sends notifications about system metrics.

Parameters:
- `metrics`: Dictionary containing system metrics

#### `check_metrics(metrics)`

Checks metrics and sends notifications if thresholds are exceeded.

Parameters:
- `metrics`: Dictionary containing system metrics

Returns:
- Dictionary with status and notification information

#### `reset_error_counts()`

Resets error counts used for tracking consecutive errors. 