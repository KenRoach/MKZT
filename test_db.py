import os
import sys

# Database connection details
DB_HOST = "db.btnjormbowjzcnzathpt.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "mifjyg-mimky7-ficriD"

def test_connection():
    """Test the database connection using the subprocess module"""
    try:
        # Try to connect using psql command if available
        import subprocess
        
        # Construct the connection string
        conn_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
        # Try to connect using psql
        result = subprocess.run(
            ["psql", conn_string, "-c", "SELECT version();"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Successfully connected to PostgreSQL database!")
            print(f"Output: {result.stdout}")
        else:
            print(f"Error connecting to database: {result.stderr}")
            
    except FileNotFoundError:
        print("psql command not found. Please install PostgreSQL client tools.")
        print("You can download them from: https://www.postgresql.org/download/")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_connection() 