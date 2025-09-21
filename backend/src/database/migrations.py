"""
Database migration management utilities.
"""

import os
import logging
from pathlib import Path
from typing import List
from sqlalchemy import text
from . import engine


logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations and schema updates."""
    
    def __init__(self, migrations_dir: str = None):
        if migrations_dir is None:
            migrations_dir = Path(__file__).parent / "migrations"
        self.migrations_dir = Path(migrations_dir)
        
    def get_migration_files(self) -> List[Path]:
        """Get all migration files sorted by filename."""
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory {self.migrations_dir} does not exist")
            return []
            
        migration_files = list(self.migrations_dir.glob("*.sql"))
        return sorted(migration_files)
    
    def run_migration_file(self, file_path: Path) -> bool:
        """
        Execute a single migration file.
        Returns True if successful, False otherwise.
        """
        try:
            logger.info(f"Running migration: {file_path.name}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            with engine.connect() as conn:
                trans = conn.begin()
                try:
                    for statement in statements:
                        if statement:
                            conn.execute(text(statement))
                    trans.commit()
                    logger.info(f"Successfully applied migration: {file_path.name}")
                    return True
                except Exception as e:
                    trans.rollback()
                    logger.error(f"Error applying migration {file_path.name}: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"Failed to run migration {file_path.name}: {e}")
            return False
    
    def run_all_migrations(self) -> bool:
        """
        Run all migration files in order.
        Returns True if all migrations successful, False otherwise.
        """
        migration_files = self.get_migration_files()
        
        if not migration_files:
            logger.info("No migration files found")
            return True
            
        logger.info(f"Found {len(migration_files)} migration files")
        
        for migration_file in migration_files:
            if not self.run_migration_file(migration_file):
                logger.error(f"Migration failed at: {migration_file.name}")
                return False
                
        logger.info("All migrations completed successfully")
        return True
    
    def create_migration_table(self):
        """Create a table to track applied migrations (future enhancement)."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            with engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
            logger.info("Created schema_migrations table")
        except Exception as e:
            logger.error(f"Failed to create schema_migrations table: {e}")
    
    def check_database_status(self) -> dict:
        """
        Check database connection and basic table status.
        Returns dictionary with status information.
        """
        status = {
            'connection': False,
            'tables_exist': False,
            'sample_data': False,
            'error': None
        }
        
        try:
            with engine.connect() as conn:
                # Test connection
                conn.execute(text("SELECT 1"))
                status['connection'] = True
                
                # Check if main tables exist
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('ai_agents', 'performance_metrics', 'user_sessions', 'monitoring_configuration')
                """))
                table_count = result.scalar()
                status['tables_exist'] = table_count == 4
                
                # Check if sample data exists
                if status['tables_exist']:
                    result = conn.execute(text("SELECT COUNT(*) FROM ai_agents"))
                    agent_count = result.scalar()
                    status['sample_data'] = agent_count > 0
                    
        except Exception as e:
            status['error'] = str(e)
            logger.error(f"Database status check failed: {e}")
            
        return status


def run_migrations():
    """Convenience function to run all migrations."""
    manager = MigrationManager()
    return manager.run_all_migrations()


def check_db_status():
    """Convenience function to check database status."""
    manager = MigrationManager()
    return manager.check_database_status()