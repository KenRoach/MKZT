# Order Handler

The Order Handler is a component that manages the creation, retrieval, and updating of orders in the WhatsApp AI Ordering Bot system. It integrates with both the database and CRM systems to ensure consistent order management.

## Features

- **Order Creation**: Creates new orders with unique IDs and timestamps
- **Order Retrieval**: Retrieves order details by ID or customer
- **Order Status Updates**: Updates order status in both database and CRM
- **AI-Powered Order Extraction**: Extracts order details from customer messages using AI
- **CRM Integration**: Syncs order data with external CRM systems
- **Error Handling**: Robust error handling with detailed logging

## Usage

### Basic Usage

```python
from src.utils.order_handler import OrderHandler
from src.utils.database import get_db_session

# Initialize the handler with a database session
db_session = get_db_session()
order_handler = OrderHandler(db_session)

# Create a new order
order_items = [
    {"name": "Pizza", "quantity": 2, "price": 10.99},
    {"name": "Soda", "quantity": 1, "price": 2.99}
]
customer_id = "customer123"
order_id, status = await order_handler.create_order(customer_id, order_items)

# Get order details
order = await order_handler.get_order(order_id)

# Update order status
await order_handler.update_order_status(order_id, "shipped")

# Get all orders for a customer
customer_orders = await order_handler.get_customer_orders(customer_id)

# Extract order from a message
message = "I'd like to order 2 pizzas and a soda"
order_details = await order_handler.extract_order_from_message(message)
```

## Order Structure

Orders in the system have the following structure:

```python
{
    "id": "order123",
    "customer_id": "customer123",
    "items": [
        {
            "name": "Pizza",
            "quantity": 2,
            "price": 10.99
        },
        {
            "name": "Soda",
            "quantity": 1,
            "price": 2.99
        }
    ],
    "total_amount": 24.97,
    "status": "pending",
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
}
```

## Methods

### `create_order(customer_id, items)`

Creates a new order in the database and CRM.

Parameters:
- `customer_id`: ID of the customer placing the order
- `items`: List of items in the order, each with name, quantity, and price

Returns:
- Tuple of (order_id, status)

### `get_order(order_id)`

Retrieves order details from the database.

Parameters:
- `order_id`: ID of the order to retrieve

Returns:
- Order details as a dictionary

### `update_order_status(order_id, status)`

Updates the status of an order in both the database and CRM.

Parameters:
- `order_id`: ID of the order to update
- `status`: New status for the order

Returns:
- Boolean indicating success

### `get_customer_orders(customer_id)`

Retrieves all orders for a specific customer.

Parameters:
- `customer_id`: ID of the customer

Returns:
- List of order details

### `extract_order_from_message(message)`

Extracts order information from a customer message using AI.

Parameters:
- `message`: Customer message text

Returns:
- Dictionary containing extracted order details

## AI Order Extraction

The `extract_order_from_message` method uses OpenAI to analyze customer messages and extract order details. It works as follows:

1. Sends the message to OpenAI with a prompt requesting order extraction
2. Parses the JSON response from OpenAI
3. Validates the extracted order details
4. Returns the structured order information

Example AI prompt:
```
Extract order information from the following message. 
Return a JSON object with the following structure:
{
  "items": [
    {
      "name": "item name",
      "quantity": number,
      "price": number (optional)
    }
  ],
  "special_instructions": "string (optional)"
}

Message: "I'd like to order 2 pizzas and a soda"
```

## Error Handling

The Order Handler includes comprehensive error handling:

- Database connection errors
- CRM API errors
- AI service errors
- Invalid input validation

All errors are logged with detailed context for debugging.

## Testing

The Order Handler includes comprehensive tests in `tests/test_order_handler.py`. Run the tests with:

```
pytest tests/test_order_handler.py
```

## Integration with Other Components

The Order Handler integrates with several other components:

- **Database**: Stores order information
- **CRM Handler**: Syncs order data with external CRM systems
- **AI Handler**: Extracts order details from messages
- **Message Handler**: Processes incoming messages and routes order-related intents

## Troubleshooting

### Common Issues

1. **Order creation failures**
   - Check database connection
   - Verify CRM API credentials
   - Ensure customer ID exists

2. **AI extraction issues**
   - Verify OpenAI API key
   - Check message format
   - Review AI prompt effectiveness

3. **Status update failures**
   - Check order ID validity
   - Verify CRM API status
   - Ensure status value is valid

## Best Practices

1. **Always use transactions** for database operations to ensure data consistency
2. **Validate input data** before processing
3. **Handle errors gracefully** with appropriate logging
4. **Use async/await** for all database and API operations
5. **Keep CRM and database in sync** by updating both systems 