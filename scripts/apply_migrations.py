import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create and return a PostgreSQL connection"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        raise ValueError("Missing DATABASE_URL in .env file")
    
    try:
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        sys.exit(1)

def read_migration_file(file_path: Path) -> str:
    """Read and return the contents of a migration file"""
    with open(file_path, 'r') as f:
        return f.read()

def apply_migration(conn, migration_file: Path) -> None:
    """Apply a single migration file to the database"""
    try:
        print(f"Applying migration: {migration_file.name}")
        sql = read_migration_file(migration_file)
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Execute the SQL migration
        cursor.execute(sql)
        
        # Commit the transaction
        conn.commit()
        
        print(f"Successfully applied migration: {migration_file.name}")
    except Exception as e:
        print(f"Error applying migration {migration_file.name}: {str(e)}")
        conn.rollback()
        sys.exit(1)

def main():
    """Main function to apply all migrations"""
    try:
        # Get database connection
        conn = get_db_connection()
        
        # Get migrations directory
        migrations_dir = Path(__file__).parent.parent / 'supabase' / 'migrations'
        
        # Get all SQL migration files
        migration_files = sorted(migrations_dir.glob('*.sql'))
        
        if not migration_files:
            print("No migration files found")
            return
        
        # Apply each migration
        for migration_file in migration_files:
            apply_migration(conn, migration_file)
        
        print("All migrations applied successfully")
        
        # Close the connection
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 