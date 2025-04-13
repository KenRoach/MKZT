import os
import sys
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

def test_connection():
    """Test the database connection"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("Error: Missing DATABASE_URL in .env file")
        sys.exit(1)
    
    try:
        print(f"Connecting to database: {database_url.split('@')[1]}")
        conn = psycopg2.connect(database_url)
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"Successfully connected to PostgreSQL database!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Close the connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_connection() 