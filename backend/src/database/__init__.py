"""
Database connection and configuration module.
"""

import os
from typing import Optional
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Database configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'postgresql://sentinel:sentinel_password@localhost:5432/sentinel_ai'
)

# SQLAlchemy engine configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=os.getenv('SQLALCHEMY_ECHO', 'false').lower() == 'true'
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Metadata for reflection
metadata = MetaData()


def get_db():
    """
    Database dependency for FastAPI/Flask applications.
    Yields a database session and ensures proper cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables in the database.
    This is typically handled by migrations, but useful for testing.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all tables in the database.
    WARNING: This will delete all data!
    """
    Base.metadata.drop_all(bind=engine)


def get_database_url() -> str:
    """Get the current database URL."""
    return DATABASE_URL


def test_connection() -> bool:
    """
    Test the database connection.
    Returns True if connection is successful, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False