#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from src.utils.supabase_client import supabase
from src.data.crm_repository import CRMRepository
from src.utils.logger import logger

def test_supabase_connection():
    """Test Supabase connection and basic operations"""
    try:
        # Initialize repository
        crm_repo = CRMRepository()
        
        # Test 1: Basic connection
        logger.info("Testing Supabase connection...")
        
        # Test 2: Try to fetch customers
        logger.info("Fetching customers...")
        customers = crm_repo.get_customers(limit=5)
        logger.info(f"Successfully fetched {len(customers)} customers")
        for customer in customers:
            logger.info(f"Customer: {customer.get('name')} ({customer.get('email')})")
        
        # Test 3: Try to fetch merchants
        logger.info("Fetching merchants...")
        merchants = crm_repo.get_merchants(limit=5)
        logger.info(f"Successfully fetched {len(merchants)} merchants")
        for merchant in merchants:
            logger.info(f"Merchant: {merchant.get('name')} ({merchant.get('email')})")
        
        # Test 4: Try to fetch drivers
        logger.info("Fetching drivers...")
        drivers = crm_repo.get_drivers(limit=5)
        logger.info(f"Successfully fetched {len(drivers)} drivers")
        for driver in drivers:
            logger.info(f"Driver: {driver.get('name')} ({driver.get('email')})")
        
        # Test 5: Try to fetch orders
        logger.info("Fetching orders...")
        orders = crm_repo.get_orders(limit=5)
        logger.info(f"Successfully fetched {len(orders)} orders")
        for order in orders:
            logger.info(f"Order: ID {order.get('id')}, Status: {order.get('status')}")
        
        logger.info("All Supabase connection tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing Supabase connection: {str(e)}")
        return False

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run tests
    success = test_supabase_connection()
    
    if success:
        print("\n✅ Supabase connection test successful!")
    else:
        print("\n❌ Supabase connection test failed!") 