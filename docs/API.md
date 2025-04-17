# Mealkitz AI - API Documentation

## Authentication

### Get Access Token
```http
POST /api/v1/auth/token
Content-Type: application/json

{
    "access_code": "XXXX2024"
}
```

### Refresh Token
```http
POST /api/v1/auth/refresh
Authorization: Bearer {refresh_token}
```

## Consumer API

### Orders

#### Create Order
```http
POST /api/v1/consumer/orders
Authorization: Bearer {token}
Content-Type: application/json

{
    "items": [
        {
            "product_id": "prod_123",
            "quantity": 2
        }
    ],
    "delivery_address_id": "addr_123"
}
```

#### Get Order Status
```http
GET /api/v1/consumer/orders/{order_id}
Authorization: Bearer {token}
```

## Merchant API

### Analytics

#### Get Sales Report
```http
GET /api/v1/merchant/analytics/sales
Authorization: Bearer {token}
Query Parameters:
- start_date: YYYY-MM-DD
- end_date: YYYY-MM-DD
```

### Inventory

#### Update Stock
```http
PATCH /api/v1/merchant/inventory/{product_id}
Authorization: Bearer {token}
Content-Type: application/json

{
    "quantity": 50,
    "status": "in_stock"
}
```

## Driver API

### Deliveries

#### Update Delivery Status
```http
PATCH /api/v1/driver/deliveries/{delivery_id}
Authorization: Bearer {token}
Content-Type: application/json

{
    "status": "delivered",
    "location": {
        "lat": 8.9898,
        "lng": -79.5199
    }
}
```

4. Let's set up branch protection rules:

```yaml:src/.github/branch-protection.yml
# Branch protection rules for main branch
protection:
  main:
    required_status_checks:
      strict: true
      contexts:
        - "test"
        - "lint"
        - "security-scan"
        - "type-check"
        - "integration-tests"
    enforce_admins: true
    required_pull_request_reviews:
      required_approving_review_count: 2
      dismiss_stale_reviews: true
      require_code_owner_reviews: true
    restrictions:
      apps: []
      users: []
      teams:
        - "mealkitz-maintainers"

# Branch protection rules for develop branch
protection:
  develop:
    required_status_checks:
      strict: true
      contexts:
        - "test"
        - "lint"
        - "security-scan"
    enforce_admins: false
    required_pull_request_reviews:
      required_approving_review_count: 1
      dismiss_stale_reviews: true
    restrictions:
      apps: []
      users: []
      teams:
        - "mealkitz-developers"
```

And create a CODEOWNERS file:

```text:src/.github/CODEOWNERS
# Default owners for everything in the repo
*       @mealkitz/maintainers

# Backend code
/src/backend/     @mealkitz/backend-team

# Frontend code
/src/frontend/    @mealkitz/frontend-team

# Infrastructure code
/k 