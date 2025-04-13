import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from src.utils.database import Base

# Load environment variables
load_dotenv()

def init_db():
    """Initialize the database and create all tables"""
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("Database initialized successfully!")
        print("Created tables:")
        for table in Base.metadata.tables:
            print(f"- {table}")
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 