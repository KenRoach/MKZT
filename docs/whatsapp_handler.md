# WhatsApp Handler

The WhatsApp Handler is a component that manages the integration with the WhatsApp Business API. It handles incoming webhooks, verifies webhook requests, and sends messages back to customers.

## Features

- **Webhook Processing**: Processes incoming WhatsApp webhooks
- **Webhook Verification**: Verifies webhook requests from WhatsApp
- **Message Sending**: Sends text messages to customers
- **Template Messages**: Sends pre-approved template messages
- **Error Handling**: Robust error handling with detailed logging
- **Rate Limiting**: Implements rate limiting for API calls

## Configuration

The WhatsApp Handler uses the following environment variables:

```
# WhatsApp API Configuration
WHATSAPP_API_TOKEN=your_api_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id
WHATSAPP_API_VERSION=v17.0
WHATSAPP_API_URL=https://graph.facebook.com
```

## Usage

### Basic Usage

```python
from src.whatsapp.handler import WhatsAppHandler
from src.utils.message_handler import MessageHandler

# Initialize dependencies
message_handler = MessageHandler(...)

# Initialize the WhatsApp handler
whatsapp_handler = WhatsAppHandler(message_handler)

# Process a webhook
webhook_data = {...}  # Webhook data from WhatsApp
response = await whatsapp_handler.process_webhook(webhook_data)

# Send a message
phone_number = "+1234567890"
message = "Hello, this is a test message"
result = await whatsapp_handler.send_message(phone_number, message)

# Send a template message
template_name = "order_confirmation"
language_code = "en"
components = [
    {
        "type": "body",
        "parameters": [
            {"type": "text", "text": "12345"}
        ]
    }
]
result = await whatsapp_handler.send_template_message(
    phone_number, 
    template_name, 
    language_code, 
    components
)
```

## Webhook Processing

The WhatsApp Handler processes incoming webhooks through the following steps:

1. **Verification**: Verifies the webhook request from WhatsApp
2. **Message Extraction**: Extracts the message from the webhook data
3. **Message Processing**: Passes the message to the Message Handler
4. **Response Sending**: Sends the response back to the customer

### Webhook Data Structure

WhatsApp webhooks have the following structure:

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "PHONE_NUMBER",
              "phone_number_id": "PHONE_NUMBER_ID"
            },
            "messages": [
              {
                "from": "CUSTOMER_PHONE_NUMBER",
                "id": "MESSAGE_ID",
                "timestamp": "TIMESTAMP",
                "text": {
                  "body": "MESSAGE_TEXT"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

## Methods

### `process_webhook(webhook_data)`

Processes an incoming webhook from WhatsApp.

Parameters:
- `webhook_data`: The webhook data from WhatsApp

Returns:
- Response indicating success

### `verify_webhook(mode, verify_token, challenge)`

Verifies a webhook request from WhatsApp.

Parameters:
- `mode`: The mode parameter from WhatsApp
- `verify_token`: The verify token from WhatsApp
- `challenge`: The challenge parameter from WhatsApp

Returns:
- Challenge value if verification is successful, error response otherwise

### `send_message(phone_number, message)`

Sends a text message to a customer.

Parameters:
- `phone_number`: The recipient's phone number
- `message`: The message text

Returns:
- Boolean indicating success

### `send_template_message(phone_number, template_name, language_code, components)`

Sends a template message to a customer.

Parameters:
- `phone_number`: The recipient's phone number
- `template_name`: The name of the template to use
- `language_code`: The language code for the template
- `components`: The components to include in the template

Returns:
- Boolean indicating success

### `_process_message(message_data)`

Processes a message from the webhook data.

Parameters:
- `message_data`: The message data from the webhook

Returns:
- Response from the Message Handler

## Webhook Verification

WhatsApp requires webhook verification to ensure that the webhook is coming from a legitimate source. The verification process works as follows:

1. WhatsApp sends a GET request to the webhook URL with the following parameters:
   - `hub.mode`: Always "subscribe"
   - `hub.verify_token`: A token that you provide to WhatsApp
   - `hub.challenge`: A random string that you must return

2. The handler verifies the `hub.verify_token` against a configured value
3. If the token is valid, the handler returns the `hub.challenge` value
4. If the token is invalid, the handler returns an error response

## Message Templates

WhatsApp requires that businesses use pre-approved message templates for initiating conversations. The handler supports sending template messages with the following structure:

```json
{
  "messaging_product": "whatsapp",
  "to": "RECIPIENT_PHONE_NUMBER",
  "type": "template",
  "template": {
    "name": "TEMPLATE_NAME",
    "language": {
      "code": "LANGUAGE_CODE"
    },
    "components": [
      {
        "type": "COMPONENT_TYPE",
        "parameters": [
          {
            "type": "PARAMETER_TYPE",
            "text": "PARAMETER_VALUE"
          }
        ]
      }
    ]
  }
}
```

## Error Handling

The WhatsApp Handler includes comprehensive error handling:

- API authentication errors
- Rate limiting errors
- Invalid phone number errors
- Template message errors
- Webhook verification errors

All errors are logged with detailed context for debugging.

## Testing

The WhatsApp Handler includes comprehensive tests in `tests/test_whatsapp_handler.py`. Run the tests with:

```
pytest tests/test_whatsapp_handler.py
```

## Integration with Other Components

The WhatsApp Handler integrates with the Message Handler to process incoming messages and generate responses.

## Troubleshooting

### Common Issues

1. **Webhook verification failures**
   - Check the verify token configuration
   - Ensure the webhook URL is correctly configured in WhatsApp
   - Verify the webhook endpoint is accessible

2. **Message sending failures**
   - Check API token and phone number ID
   - Verify recipient phone number format
   - Check rate limiting status

3. **Template message failures**
   - Verify template name and language code
   - Check template component structure
   - Ensure template is approved by WhatsApp

## Best Practices

1. **Always verify webhooks** to ensure they're coming from WhatsApp
2. **Use template messages** for initiating conversations
3. **Implement rate limiting** to avoid API throttling
4. **Handle errors gracefully** with appropriate logging
5. **Validate phone numbers** before sending messages 