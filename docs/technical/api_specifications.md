# API Specifications

## Overview
Complete API documentation for all services in the Mealkitz platform.

## Authentication
```json
POST /api/v1/auth/login
{
  "email": "string",
  "password": "string"
}

Response:
{
  "access_token": "string",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## Order Service

### Create Order
```json
POST /api/v1/orders
{
  "customer_id": "uuid",
  "merchant_id": "uuid",
  "items": [
    {
      "product_id": "uuid",
      "quantity": "integer",
      "special_instructions": "string"
    }
  ],
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
  "payment_method": "string"
}

Response (201):
{
  "order_id": "uuid",
  "status": "pending",
  "estimated_delivery_time": "datetime",
  "total_amount": "decimal"
}
```

### Update Order Status
```json
PUT /api/v1/orders/{order_id}/status
{
  "status": "enum(pending, confirmed, preparing, ready, picked_up, delivered, cancelled)",
  "reason": "string"  // Optional, required for cancellation
}

Response (200):
{
  "order_id": "uuid",
  "status": "string",
  "updated_at": "datetime"
}
```

## Driver Service

### Driver Location Update
```json
POST /api/v1/driver/location
{
  "driver_id": "uuid",
  "location": {
    "latitude": "float",
    "longitude": "float"
  },
  "status": "enum(online, offline, on_delivery)",
  "battery_level": "integer"  // Optional
}

Response (200):
{
  "acknowledged": true,
  "timestamp": "datetime"
}
```

### Get Driver Orders
```json
GET /api/v1/driver/orders?status=active

Response (200):
{
  "orders": [
    {
      "order_id": "uuid",
      "pickup": {
        "merchant_name": "string",
        "address": "string",
        "coordinates": {
          "latitude": "float",
          "longitude": "float"
        }
      },
      "dropoff": {
        "customer_name": "string",
        "address": "string",
        "coordinates": {
          "latitude": "float",
          "longitude": "float"
        }
      },
      "status": "string",
      "estimated_pickup_time": "datetime",
      "estimated_delivery_time": "datetime"
    }
  ]
}
```

## Merchant Service

### Update Menu Item
```json
PUT /api/v1/merchant/products/{product_id}
{
  "name": "string",
  "description": "string",
  "price": "decimal",
  "availability": "boolean",
  "preparation_time": "integer",
  "categories": ["string"]
}

Response (200):
{
  "product_id": "uuid",
  "updated_at": "datetime"
}
```

### Get Orders Dashboard
```json
GET /api/v1/merchant/dashboard?date=YYYY-MM-DD

Response (200):
{
  "summary": {
    "total_orders": "integer",
    "completed_orders": "integer",
    "active_orders": "integer",
    "total_revenue": "decimal"
  },
  "orders": [
    {
      "order_id": "uuid",
      "status": "string",
      "items": [
        {
          "name": "string",
          "quantity": "integer",
          "special_instructions": "string"
        }
      ],
      "created_at": "datetime",
      "estimated_pickup_time": "datetime"
    }
  ]
}
```

## AI Service

### Predict Order Volume
```json
POST /api/v1/ai/predict/orders
{
  "merchant_id": "uuid",
  "timestamp": "datetime",
  "location": {
    "latitude": "float",
    "longitude": "float"
  }
}

Response (200):
{
  "predicted_volume": "integer",
  "confidence_score": "float",
  "factors": [
    {
      "name": "string",
      "impact": "float"
    }
  ]
}
```

### Optimize Routes
```json
POST /api/v1/ai/optimize/routes
{
  "driver_id": "uuid",
  "current_location": {
    "latitude": "float",
    "longitude": "float"
  },
  "deliveries": [
    {
      "order_id": "uuid",
      "pickup": {
        "latitude": "float",
        "longitude": "float"
      },
      "dropoff": {
        "latitude": "float",
        "longitude": "float"
      },
      "time_window": {
        "start": "datetime",
        "end": "datetime"
      }
    }
  ]
}

Response (200):
{
  "route": [
    {
      "order_id": "uuid",
      "type": "enum(pickup, dropoff)",
      "estimated_time": "datetime",
      "location": {
        "latitude": "float",
        "longitude": "float"
      }
    }
  ],
  "total_distance": "float",
  "total_time": "integer"
}
```

## WebSocket Events

### Order Updates
```json
{
  "type": "order_update",
  "data": {
    "order_id": "uuid",
    "status": "string",
    "timestamp": "datetime",
    "metadata": {}
  }
}
```

### Driver Location
```json
{
  "type": "driver_location",
  "data": {
    "driver_id": "uuid",
    "location": {
      "latitude": "float",
      "longitude": "float"
    },
    "timestamp": "datetime"
  }
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
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 422: Unprocessable Entity
- 429: Too Many Requests
- 500: Internal Server Error

## Rate Limits
- Authentication: 5 requests/minute
- Orders: 60 requests/minute
- Location Updates: 30 requests/minute
- Menu Updates: 100 requests/hour
- AI Predictions: 1000 requests/day

## Versioning
- API version included in URL path (/api/v1/)
- Deprecation notices via response headers
- Minimum 6 months support for deprecated versions 