# Mealkitz AI

Advanced AI-powered food delivery and nutrition management system.

## Features

- 👤 Consumer Features
  - Order management
  - Nutrition tracking
  - Recipe suggestions
  - Personalized recommendations

- 🧑‍🍳 Merchant Features
  - Sales analytics
  - Inventory management
  - Customer insights
  - Promotion management

- 🛵 Driver Features
  - Route optimization
  - Earnings tracking
  - Performance metrics
  - Document management

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mealkitz/mealkitz-ai.git
cd mealkitz-ai
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
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

5. Initialize database:
```bash
python manage.py db upgrade
```

### Running the Application

#### Development
```bash
uvicorn src.app:app --reload
```

#### Production
```bash
docker-compose up -d
```

## Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=src
```

## Documentation

API documentation is available at `/docs` when running the application.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 

# Example interactions for different actors
async def test_multi_actor_conversation():
    # Customer order
    customer_response = await conversation_manager.handle_customer_message(
        order_id="TEST123",
        customer_id="CUST123",
        message="Hola, quiero un California Roll y un té frío"
    )
    print(f"Customer Response: {customer_response}")

    # Kitchen acknowledgment
    kitchen_response = await conversation_manager.handle_kitchen_message(
        order_id="TEST123",
        staff_id="STAFF123",
        message="15 minutos"
    )
    print(f"Kitchen Response: {kitchen_response}")

    # Driver confirmation
    driver_response = await conversation_manager.handle_driver_message(
        order_id="TEST123",
        driver_id="DRIVER123",
        message="Confirmo disponibilidad"
    )
    print(f"Driver Response: {driver_response}")

# 1. Build the production images
docker compose -f docker-compose.prod.yml build

# 2. Start the entire stack
docker compose -f docker-compose.prod.yml up -d

# 3. Verify all services are running
docker compose -f docker-compose.prod.yml ps

# 4. Check application logs
docker compose -f docker-compose.prod.yml logs -f app 