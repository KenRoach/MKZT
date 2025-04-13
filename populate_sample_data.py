#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import logging
from src.core.logger import setup_logging
from src.data.crm_repository import CRMRepository
from datetime import datetime, timedelta
import random

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def generate_sample_data():
    """Generate sample data for testing and development."""
    # Sample customers
    customers = [
        {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "address": "123 Main St, City, Country",
            "preferences": {"language": "en", "notifications": ["email", "sms"]}
        },
        {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "+0987654321",
            "address": "456 Oak Ave, Town, Country",
            "preferences": {"language": "es", "notifications": ["whatsapp"]}
        }
    ]
    
    # Sample merchants
    merchants = [
        {
            "name": "Restaurant A",
            "email": "restaurant.a@example.com",
            "phone": "+1122334455",
            "address": "789 Food St, City, Country",
            "cuisine": "Italian",
            "rating": 4.5
        },
        {
            "name": "Cafe B",
            "email": "cafe.b@example.com",
            "phone": "+5544332211",
            "address": "321 Coffee Rd, Town, Country",
            "cuisine": "International",
            "rating": 4.2
        }
    ]
    
    # Sample drivers
    drivers = [
        {
            "name": "Mike Johnson",
            "email": "mike@example.com",
            "phone": "+6677889900",
            "vehicle_type": "motorcycle",
            "status": "available"
        },
        {
            "name": "Sarah Wilson",
            "email": "sarah@example.com",
            "phone": "+9988776655",
            "vehicle_type": "car",
            "status": "available"
        }
    ]
    
    return customers, merchants, drivers

def main():
    try:
        logger.info("Starting to populate sample data")
        
        # Initialize repository
        repo = CRMRepository()
        
        # Generate sample data
        customers, merchants, drivers = generate_sample_data()
        
        # Create customers
        created_customers = []
        for customer in customers:
            created_customer = repo.create_customer(customer)
            created_customers.append(created_customer)
            logger.info(f"Created customer: {created_customer['name']}")
        
        # Create merchants
        created_merchants = []
        for merchant in merchants:
            created_merchant = repo.create_merchant(merchant)
            created_merchants.append(created_merchant)
            logger.info(f"Created merchant: {created_merchant['name']}")
        
        # Create drivers
        created_drivers = []
        for driver in drivers:
            created_driver = repo.create_driver(driver)
            created_drivers.append(created_driver)
            logger.info(f"Created driver: {created_driver['name']}")
        
        # Create sample orders
        for customer in created_customers:
            for merchant in created_merchants:
                # Create order
                order = {
                    "customer_id": customer["id"],
                    "merchant_id": merchant["id"],
                    "driver_id": random.choice(created_drivers)["id"],
                    "status": random.choice(["pending", "confirmed", "preparing", "ready", "delivered"]),
                    "total_amount": random.uniform(10.0, 100.0),
                    "created_at": datetime.now() - timedelta(days=random.randint(0, 30))
                }
                
                created_order = repo.create_order(order)
                logger.info(f"Created order for customer {customer['name']} at {merchant['name']}")
                
                # Create order items
                num_items = random.randint(1, 5)
                for _ in range(num_items):
                    item = {
                        "order_id": created_order["id"],
                        "name": f"Item {random.randint(1, 10)}",
                        "quantity": random.randint(1, 3),
                        "price": random.uniform(5.0, 20.0)
                    }
                    repo.create_order_item(item)
        
        logger.info("Sample data population completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to populate sample data: {str(e)}")
        raise

if __name__ == "__main__":
    main() 