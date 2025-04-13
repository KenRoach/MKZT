# Order Management System

A comprehensive order management system with multi-channel support, intelligent routing, and real-time tracking.

## Features

- **Multi-Channel Order Processing**
  - WhatsApp integration
  - Web App support
  - Mobile App support
  - Instagram integration
  - SMS support
  - Third-party API integration

- **Intelligent Order Management**
  - Agentic decision engine for order routing
  - Real-time order tracking
  - Automated issue detection
  - Performance monitoring

- **Merchant Dashboard**
  - Real-time performance metrics
  - Order analytics
  - Customer insights
  - Inventory alerts

- **Driver Coordination**
  - Real-time location tracking
  - Automated driver assignment
  - Delivery status updates

- **Consumer Notifications**
  - Multi-language support (English, Spanish, Portuguese)
  - Multi-channel notifications
  - Order confirmations
  - Status updates
  - Tracking information

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL (Supabase)
- **Caching**: Redis
- **Authentication**: JWT
- **API Documentation**: OpenAPI (Swagger)

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Supabase account

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd order-management-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run database migrations:
   ```bash
   python src/scripts/run_migrations.py
   ```

## Running the Application

1. Start the development server:
   ```bash
   uvicorn src.app:app --reload
   ```

2. Access the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /health` - Check system health

### Metrics
- `GET /metrics` - Get system metrics

### Merchants
- `GET /api/v1/merchants` - List merchants
- `GET /api/v1/merchants/{merchant_id}` - Get merchant details
- `POST /api/v1/merchants` - Create merchant
- `PUT /api/v1/merchants/{merchant_id}` - Update merchant

### Orders
- `GET /api/v1/orders` - List orders
- `GET /api/v1/orders/{order_id}` - Get order details
- `POST /api/v1/orders` - Create order
- `PUT /api/v1/orders/{order_id}` - Update order
- `GET /api/v1/orders/{order_id}/tracking` - Get order tracking

### Drivers
- `GET /api/v1/drivers` - List drivers
- `GET /api/v1/drivers/{driver_id}` - Get driver details
- `POST /api/v1/drivers` - Create driver
- `PUT /api/v1/drivers/{driver_id}` - Update driver
- `PUT /api/v1/drivers/{driver_id}/location` - Update driver location

### Customers
- `GET /api/v1/customers` - List customers
- `GET /api/v1/customers/{customer_id}` - Get customer details
- `POST /api/v1/customers` - Create customer
- `PUT /api/v1/customers/{customer_id}` - Update customer

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 