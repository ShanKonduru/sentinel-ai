"""
Base SQLAlchemy model and database setup for Sentinel AI.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func


# SQLAlchemy base configuration
Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields and utilities."""
    __abstract__ = True
    
    # Common timestamp fields
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    
    @classmethod
    def generate_uuid(cls):
        """Generate a new UUID for primary keys."""
        return str(uuid.uuid4())
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self):
        """String representation of the model."""
        class_name = self.__class__.__name__
        return f"<{class_name}({self.to_dict()})>"