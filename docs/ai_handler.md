# AI Handler

The AI Handler is a component that leverages OpenAI's language models to analyze messages, extract information, and determine intent. It provides the intelligence behind the WhatsApp AI Ordering Bot's ability to understand and process customer messages.

## Features

- **Intent Analysis**: Determines the purpose of incoming messages
- **Order Extraction**: Extracts order details from customer messages
- **Entity Recognition**: Identifies key entities in messages (products, quantities, etc.)
- **Response Generation**: Creates natural language responses
- **Error Handling**: Robust error handling with detailed logging
- **Rate Limiting**: Implements rate limiting for API calls

## Configuration

The AI Handler uses the following environment variables:

```
# OpenAI Configuration
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=150
OPENAI_TEMPERATURE=0.2
```

## Usage

### Basic Usage

```python
from src.ai.handler import AIHandler

# Initialize the AI handler
ai_handler = AIHandler()

# Analyze message intent
message = "I'd like to order 2 pizzas and a soda"
intent_result = await ai_handler.analyze_intent(message)

# Extract order details
order_result = await ai_handler.extract_order(message)

# Generate a response
context = {"intent": "order", "items": [{"name": "Pizza", "quantity": 2}]}
response = await ai_handler.generate_response(context)
```

## Methods

### `analyze_intent(message)`

Analyzes a message to determine its intent.

Parameters:
- `message`: The message text

Returns:
- Dictionary with intent and confidence

### `extract_order(message)`

Extracts order details from a message.

Parameters:
- `message`: The message text

Returns:
- Dictionary with extracted order details

### `generate_response(context)`

Generates a response based on the context.

Parameters:
- `context`: Dictionary with context information

Returns:
- Generated response text

### `_call_openai(prompt, max_tokens=None, temperature=None)`

Makes a call to the OpenAI API.

Parameters:
- `prompt`: The prompt to send to OpenAI
- `max_tokens`: Maximum number of tokens to generate
- `temperature`: Temperature for response generation

Returns:
- OpenAI API response

## Intent Analysis

The AI Handler uses OpenAI to analyze message intent. It works as follows:

1. Sends the message to OpenAI with a prompt requesting intent analysis
2. Receives the intent classification from OpenAI
3. Returns the intent and confidence level

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

## Order Extraction

The AI Handler extracts order details from messages using OpenAI. It works as follows:

1. Sends the message to OpenAI with a prompt requesting order extraction
2. Receives the extracted order details from OpenAI
3. Returns the structured order information

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

## Response Generation

The AI Handler generates responses based on context using OpenAI. It works as follows:

1. Sends the context to OpenAI with a prompt requesting response generation
2. Receives the generated response from OpenAI
3. Returns the response text

Example AI prompt:
```
Generate a response for the following context.
The response should be friendly, concise, and helpful.

Context: {
  "intent": "order",
  "items": [
    {
      "name": "Pizza",
      "quantity": 2
    },
    {
      "name": "Soda",
      "quantity": 1
    }
  ]
}
```

## Error Handling

The AI Handler includes comprehensive error handling:

- API authentication errors
- Rate limiting errors
- Invalid response format errors
- Timeout errors

All errors are logged with detailed context for debugging.

## Testing

The AI Handler includes comprehensive tests in `tests/test_ai_handler.py`. Run the tests with:

```
pytest tests/test_ai_handler.py
```

## Integration with Other Components

The AI Handler integrates with several other components:

- **Message Handler**: Provides intent analysis for message processing
- **Order Handler**: Provides order extraction for order processing
- **Notification Handler**: May use AI for generating notification content

## Troubleshooting

### Common Issues

1. **API authentication failures**
   - Check OpenAI API key
   - Verify API key permissions
   - Ensure API key is correctly set in environment variables

2. **Rate limiting issues**
   - Check OpenAI rate limits
   - Implement caching for frequently used prompts
   - Adjust request frequency

3. **Response format issues**
   - Check prompt structure
   - Verify JSON parsing logic
   - Review error handling for malformed responses

## Best Practices

1. **Keep prompts clear and specific** for better results
2. **Use structured output formats** (JSON) for easier parsing
3. **Implement caching** for frequently used prompts
4. **Handle errors gracefully** with appropriate logging
5. **Monitor API usage** to stay within limits
6. **Fine-tune temperature** based on the task (lower for extraction, higher for generation) 