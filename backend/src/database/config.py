"""
Database configuration and connection management for Sentinel AI.
"""
import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from ..models import Base


class DatabaseConfig:
    """Database configuration class."""
    
    def __init__(self):
        """Initialize database configuration from environment variables."""
        self.database_url = self._build_database_url()
        self.echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        self.pool_size = int(os.getenv("DATABASE_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
        self.pool_timeout = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))
    
    def _build_database_url(self) -> str:
        """Build database URL from environment variables."""
        # Check for full DATABASE_URL first
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return database_url
        
        # Build from individual components
        db_host = os.getenv("DATABASE_HOST", "localhost")
        db_port = os.getenv("DATABASE_PORT", "5432")
        db_name = os.getenv("DATABASE_NAME", "sentinel_ai")
        db_user = os.getenv("DATABASE_USER", "postgres")
        db_password = os.getenv("DATABASE_PASSWORD", "")
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class DatabaseManager:
    """Database connection and session manager."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """Initialize database manager with configuration."""
        self.config = config or DatabaseConfig()
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
    
    @property
    def engine(self) -> Engine:
        """Get or create database engine."""
        if self._engine is None:
            self._engine = create_engine(
                self.config.database_url,
                echo=self.config.echo,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                # PostgreSQL specific optimizations
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "sentinel_ai_backend",
                }
            )
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
        return self._session_factory
    
    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self) -> None:
        """Drop all database tables (use with caution!)."""
        Base.metadata.drop_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup."""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session_sync(self) -> Session:
        """Get a database session for manual management."""
        return self.session_factory()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def close(self) -> None:
        """Close database engine and all connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db_session() -> Generator[Session, None, None]:
    """Get a database session - convenience function for dependency injection."""
    db_manager = get_database_manager()
    with db_manager.get_session() as session:
        yield session


def init_database() -> None:
    """Initialize database with tables."""
    db_manager = get_database_manager()
    db_manager.create_tables()


def close_database() -> None:
    """Close database connections."""
    global _db_manager
    if _db_manager:
        _db_manager.close()
        _db_manager = None