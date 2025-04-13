#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from src.utils.supabase_client import supabase
from src.utils.logger import logger

def test_supabase_connection():
    """Test Supabase connection and basic operations"""
    try:
        # Test 1: Basic connection
        logger.info("Testing Supabase connection...")
        
        # Test 2: Try to fetch merchants
        logger.info("Fetching merchants...")
        merchants = supabase.table("merchants").select("*").limit(1).execute()
        logger.info(f"Successfully fetched {len(merchants.data)} merchants")
        
        # Test 3: Try to fetch customers
        logger.info("Fetching customers...")
        customers = supabase.table("customers").select("*").limit(1).execute()
        logger.info(f"Successfully fetched {len(customers.data)} customers")
        
        # Test 4: Try to fetch orders
        logger.info("Fetching orders...")
        orders = supabase.table("orders").select("*").limit(1).execute()
        logger.info(f"Successfully fetched {len(orders.data)} orders")
        
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