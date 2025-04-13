# Message Handler

The Message Handler is a core component of the WhatsApp AI Ordering Bot that processes incoming messages, determines their intent, and routes them to the appropriate handlers for further processing.

## Features

- **Intent Analysis**: Determines the purpose of incoming messages using AI
- **Customer Management**: Creates or retrieves customer information
- **Order Processing**: Routes order-related messages to the Order Handler
- **Response Generation**: Creates appropriate responses based on message intent
- **Message History**: Tracks conversation history for context
- **Error Handling**: Robust error handling with detailed logging

## Usage

### Basic Usage

```python
from src.utils.message_handler import MessageHandler
from src.utils.database import get_db_session
from src.utils.customer_handler import CustomerHandler
from src.utils.order_handler import OrderHandler
from src.ai.handler import AIHandler

# Initialize dependencies
db_session = get_db_session()
customer_handler = CustomerHandler(db_session)
order_handler = OrderHandler(db_session)
ai_handler = AIHandler()

# Initialize the message handler
message_handler = MessageHandler(
    db_session=db_session,
    customer_handler=customer_handler,
    order_handler=order_handler,
    ai_handler=ai_handler
)

# Process a message
message = "I'd like to order 2 pizzas and a soda"
phone_number = "+1234567890"
response = await message_handler.process_message(message, phone_number)
```

## Message Processing Flow

The Message Handler processes messages through the following steps:

1. **Customer Identification**: Identifies or creates a customer based on the phone number
2. **Intent Analysis**: Determines the intent of the message using AI
3. **Intent Handling**: Routes the message to the appropriate handler based on intent
4. **Response Generation**: Creates a response based on the processing results
5. **Message History**: Records the message and response in the database

## Supported Intents

The Message Handler supports the following intents:

1. **Greeting**: Initial greetings or hellos
2. **Order**: Placing a new order
3. **Order Status**: Checking the status of an existing order
4. **Help**: Requesting assistance or information
5. **Unknown**: Messages that don't match any known intent

## Methods

### `process_message(message, phone_number)`

Processes an incoming message and returns a response.

Parameters:
- `message`: The message text
- `phone_number`: The sender's phone number

Returns:
- Response text

### `_handle_greeting(customer)`

Handles greeting messages.

Parameters:
- `customer`: Customer information

Returns:
- Greeting response

### `_handle_order(customer, message)`

Handles order messages.

Parameters:
- `customer`: Customer information
- `message`: The message text

Returns:
- Order confirmation or request for more information

### `_handle_order_status(customer, message)`

Handles order status requests.

Parameters:
- `customer`: Customer information
- `message`: The message text

Returns:
- Order status information

### `_handle_help(customer)`

Handles help requests.

Parameters:
- `customer`: Customer information

Returns:
- Help information

### `_handle_unknown(customer, message)`

Handles messages with unknown intent.

Parameters:
- `customer`: Customer information
- `message`: The message text

Returns:
- Response indicating inability to understand the message

### `_save_message(customer_id, message, response, intent)`

Saves a message and its response to the database.

Parameters:
- `customer_id`: ID of the customer
- `message`: The message text
- `response`: The response text
- `intent`: The detected intent

Returns:
- Boolean indicating success

## Intent Analysis

The Message Handler uses the AI Handler to analyze message intent. It works as follows:

1. Sends the message to the AI Handler with a prompt requesting intent analysis
2. Receives the intent classification from the AI Handler
3. Routes the message to the appropriate handler based on the intent

Example AI prompt:
```
Analyze the following message and determine its intent.
Return a JSON object with the following structure:
{
  "intent": "greeting|order|order_status|help|unknown",
  "confidence": number between 0 and 1
}

Message: "I'd like to order 2 pizzas and a soda"
```

## Response Templates

The Message Handler uses templates for generating responses:

### Greeting Response
```
Hello! Welcome to our WhatsApp ordering service. How can I help you today?
```

### Order Response
```
I've received your order for:
{order_details}

Your order number is: {order_id}
Total amount: ${total_amount}

Is there anything else you'd like to add to your order?
```

### Order Status Response
```
Order #{order_id} is currently {status}.
{additional_details}
```

### Help Response
```
I can help you with the following:
- Placing a new order
- Checking the status of an existing order
- Getting assistance with your order

Just let me know what you need!
```

### Unknown Intent Response
```
I'm not sure I understand. Could you please rephrase your message or type 'help' for assistance?
```

## Error Handling

The Message Handler includes comprehensive error handling:

- AI service errors
- Database errors
- Customer handler errors
- Order handler errors

All errors are logged with detailed context for debugging.

## Testing

The Message Handler includes comprehensive tests in `tests/test_message_handler.py`. Run the tests with:

```
pytest tests/test_message_handler.py
```

## Integration with Other Components

The Message Handler integrates with several other components:

- **Customer Handler**: Manages customer information
- **Order Handler**: Processes orders
- **AI Handler**: Analyzes message intent
- **Database**: Stores message history

## Troubleshooting

### Common Issues

1. **Intent analysis failures**
   - Check AI Handler configuration
   - Verify OpenAI API key
   - Review intent analysis prompt

2. **Customer identification issues**
   - Check database connection
   - Verify phone number format
   - Review customer handler configuration

3. **Order processing errors**
   - Check order handler configuration
   - Verify product information
   - Review order extraction logic

## Best Practices

1. **Keep responses concise** for WhatsApp's character limits
2. **Use clear language** that's easy to understand
3. **Provide options** when asking for information
4. **Handle edge cases** gracefully
5. **Maintain conversation context** for a better user experience 