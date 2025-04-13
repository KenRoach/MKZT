#!/usr/bin/env python3

import uvicorn
import os
from dotenv import load_dotenv
import logging
from src.core.config import settings
from src.core.logger import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def main():
    try:
        # Get port from environment or use default
        port = int(os.getenv("PORT", 8000))
        
        # Get host from environment or use default
        host = os.getenv("HOST", "0.0.0.0")
        
        # Get reload flag from environment or use default
        reload = os.getenv("DEBUG", "False").lower() == "true"
        
        logger.info(f"Starting server on {host}:{port}")
        logger.info(f"Debug mode: {reload}")
        
        # Run the application
        uvicorn.run(
            "src.app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise

if __name__ == "__main__":
    main() 