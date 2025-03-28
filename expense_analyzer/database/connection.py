"""Database connection management"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://expense_analyzer_user:secure_password_123@localhost:5432/expense_analyzer_db"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Get database session"""
    return SessionLocal()


def close_db(db):
    """Close database session"""
    if db:
        db.close()
