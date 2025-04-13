#!/usr/bin/env python3
import os
import sys
import subprocess
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()

    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("Error: DATABASE_URL environment variable is not set")
        sys.exit(1)

    try:
        # Create migrations directory if it doesn't exist
        if not os.path.exists("migrations"):
            os.makedirs("migrations")
            os.makedirs("migrations/versions")

        # Run database migrations
        print("Running database migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Database migrations completed successfully")

    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 