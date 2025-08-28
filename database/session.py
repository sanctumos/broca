"""Database session management."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Get database path from environment or use default
DB_PATH = os.getenv('DB_PATH', 'broca.db')
ENGINE = create_engine(f'sqlite:///{DB_PATH}')
SessionLocal = sessionmaker(bind=ENGINE)

def get_session() -> Session:
    """Get a database session.
    
    Returns:
        A SQLAlchemy Session object
    """
    return SessionLocal() 