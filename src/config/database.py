import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    _engine = None
    _SessionLocal = None
    
    @classmethod
    def get_engine(cls):
        """Get or create SQLAlchemy engine"""
        if cls._engine is None:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("Missing DATABASE_URL in .env file")
            
            cls._engine = create_engine(
                database_url,
                pool_size=int(os.getenv("DATABASE_POOL_SIZE", "20")),
                max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
            )
        return cls._engine
    
    @classmethod
    def get_session(cls) -> Session:
        """Get a new database session"""
        if cls._SessionLocal is None:
            cls._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=cls.get_engine()
            )
        return cls._SessionLocal()
    
    @classmethod
    def get_db(cls):
        """Get a database session with automatic cleanup"""
        db = cls.get_session()
        try:
            yield db
        finally:
            db.close()

# Create a singleton instance
db = DatabaseConfig() 