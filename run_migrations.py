#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import logging
from src.core.logger import setup_logging
from src.data.database import run_migrations

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting database migrations")
        
        # Run migrations
        run_migrations()
        
        logger.info("Database migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to run migrations: {str(e)}")
        raise

if __name__ == "__main__":
    main() 