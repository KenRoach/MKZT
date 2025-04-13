import os
import sys
import subprocess
from pathlib import Path

# Database connection details
DB_HOST = "db.btnjormbowjzcnzathpt.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "mifjyg-mimky7-ficriD"

def run_seed_data():
    """Run the seed data SQL file against the database"""
    try:
        # Get the path to the seed data SQL file
        seed_file = Path(__file__).parent / "supabase" / "seed_data.sql"
        
        if not seed_file.exists():
            print(f"Error: Seed data file not found at {seed_file}")
            sys.exit(1)
        
        # Construct the connection string
        conn_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
        # Try to connect using psql
        print(f"Running seed data script: {seed_file}")
        result = subprocess.run(
            ["psql", conn_string, "-f", str(seed_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Successfully seeded the database with dummy data!")
            print(f"Output: {result.stdout}")
        else:
            print(f"Error seeding the database: {result.stderr}")
            
    except FileNotFoundError:
        print("psql command not found. Please install PostgreSQL client tools.")
        print("You can download them from: https://www.postgresql.org/download/")
        print("\nAlternatively, you can run the SQL file directly in the Supabase SQL Editor:")
        print("1. Log in to your Supabase dashboard at https://app.supabase.io")
        print("2. Select your project (btnjormbowjzcnzathpt)")
        print("3. Go to the SQL Editor tab")
        print("4. Copy the contents of the seed_data.sql file")
        print("5. Paste it into the SQL Editor and click Run")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_seed_data() 