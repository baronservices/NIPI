"""Database connection and session management."""

import os
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
from .models import Base


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, config_path: str = None):
        """Initialize database manager with configuration."""
        self.config = self._load_config(config_path)
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def _load_config(self, config_path: str = None) -> dict:
        """Load database configuration from YAML file."""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'config', 'config.yaml'
            )
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config['database']
    
    def _create_engine(self):
        """Create SQLAlchemy engine based on configuration."""
        db_type = self.config.get('type', 'sqlite')
        
        if db_type == 'sqlite':
            db_path = self.config.get('path', 'data/nipi.db')
            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            database_url = f"sqlite:///{db_path}"
            engine = create_engine(
                database_url,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
                echo=False
            )
        elif db_type == 'postgresql':
            host = self.config.get('host', 'localhost')
            port = self.config.get('port', 5432)
            database = self.config.get('name', 'nipi')
            username = self.config.get('username', '')
            password = self.config.get('password', '')
            
            database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            engine = create_engine(database_url, echo=False)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        return engine
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all database tables."""
        Base.metadata.drop_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session_direct(self) -> Session:
        """Get a database session (manual management required)."""
        return self.SessionLocal()
    
    def close(self):
        """Close the database engine."""
        self.engine.dispose()


# Global database manager instance
db_manager = None


def init_database(config_path: str = None) -> DatabaseManager:
    """Initialize the global database manager."""
    global db_manager
    db_manager = DatabaseManager(config_path)
    db_manager.create_tables()
    return db_manager


def get_db_session() -> Generator[Session, None, None]:
    """Get a database session (for dependency injection)."""
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    with db_manager.get_session() as session:
        yield session