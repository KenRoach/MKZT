# Order Parser API Specification

## Overview
The Order Parser API standardizes order processing across multiple input channels (WhatsApp, Instagram, Website, Voice). It handles natural language processing, structured data parsing, and order validation.

## Base URL
```
/api/v1/order-parser
```

## Endpoints

### 1. Parse Text Order
```http
POST /parse/text
Content-Type: application/json
Authorization: Bearer {token}

{
    "text": "string",
    "source": "whatsapp|instagram|web|voice",
    "customer_id": "uuid",
    "language": "string",
    "location": {
        "latitude": "float",
        "longitude": "float"
    },
    "context": {
        "previous_orders": "boolean",
        "saved_preferences": "boolean"
    }
}

Response (200):
{
    "parsed_order": {
        "items": [{
            "product_id": "uuid",
            "quantity": "integer",
            "special_instructions": "string",
            "variations": ["string"],
            "confidence_score": "float"
        }],
        "delivery_address": {
            "street": "string",
            "city": "string",
            "state": "string",
            "postal_code": "string",
            "coordinates": {
                "latitude": "float",
                "longitude": "float"
            }
        },
        "requested_delivery_time": "datetime",
        "special_requirements": ["string"],
        "payment_method": "string"
    },
    "requires_clarification": "boolean",
    "clarification_points": [{
        "type": "item|address|time|payment",
        "message": "string",
        "options": ["string"]
    }]
}
```

### 2. Parse Structured Order
```http
POST /parse/structured
Content-Type: application/json
Authorization: Bearer {token}

{
    "order_data": {
        "items": [{
            "name": "string",
            "quantity": "integer",
            "notes": "string"
        }],
        "delivery_info": {
            "address": "string",
            "time": "string"
        },
        "customer_info": {
            "id": "uuid",
            "preferences": {}
        }
    },
    "source": "web|app",
    "merchant_id": "uuid"
}

Response (200):
{
    "validated_order": {
        "items": [{
            "product_id": "uuid",
            "quantity": "integer",
            "price": "float",
            "special_instructions": "string"
        }],
        "total_amount": "float",
        "estimated_preparation_time": "integer",
        "delivery_details": {
            "address": {},
            "estimated_delivery_time": "datetime"
        }
    }
}
```

### 3. Validate Order
```http
POST /validate
Content-Type: application/json
Authorization: Bearer {token}

{
    "order": {
        "items": [],
        "delivery_details": {},
        "payment_info": {}
    },
    "merchant_id": "uuid",
    "validation_level": "basic|complete"
}

Response (200):
{
    "is_valid": "boolean",
    "validation_results": [{
        "field": "string",
        "status": "valid|invalid|warning",
        "message": "string"
    }],
    "suggested_corrections": [{
        "field": "string",
        "current_value": "string",
        "suggested_value": "string",
        "confidence": "float"
    }]
}
```

### 4. Get Order Template
```http
GET /template/{merchant_id}
Authorization: Bearer {token}

Response (200):
{
    "required_fields": ["string"],
    "optional_fields": ["string"],
    "validation_rules": {},
    "special_instructions_template": {},
    "delivery_zones": [{
        "zone_id": "string",
        "coordinates": []
    }]
}
```

## Error Responses

### Standard Error Format
```json
{
    "error": {
        "code": "string",
        "message": "string",
        "details": {}
    }
}
```

### Common Error Codes
- 400: Invalid order format
- 422: Validation failed
- 404: Product/merchant not found
- 429: Rate limit exceeded
- 500: Processing error

## Rate Limits
- Text parsing: 30 requests/minute
- Structured parsing: 60 requests/minute
- Validation: 100 requests/minute
- Template retrieval: 300 requests/minute

## Webhook Support
```http
POST /webhook/order-updates
Content-Type: application/json

{
    "event_type": "order_parsed|validation_failed|clarification_needed",
    "order_id": "uuid",
    "timestamp": "datetime",
    "data": {}
}
```

## Integration Examples

### WhatsApp Order
```python
import requests

order_text = "I want 2 pepperoni pizzas and a large coke for delivery"
response = requests.post(
    "api/v1/order-parser/parse/text",
    json={
        "text": order_text,
        "source": "whatsapp",
        "customer_id": "customer_123",
        "language": "en"
    }
)
```

### Web Order
```python
import requests

structured_order = {
    "items": [
        {"name": "Pepperoni Pizza", "quantity": 2},
        {"name": "Large Coke", "quantity": 1}
    ],
    "delivery_info": {
        "address": "123 Main St",
        "time": "ASAP"
    }
}
response = requests.post(
    "api/v1/order-parser/parse/structured",
    json={"order_data": structured_order}
)
```

## Dependencies
- NLP Service
- Menu Database
- Customer Profile Service
- Location Service
- Pricing Service

## Performance Requirements
- Text parsing response time: < 2s
- Structured parsing response time: < 1s
- Validation response time: < 500ms
- 99.9% uptime
- Maximum 1% error rate 