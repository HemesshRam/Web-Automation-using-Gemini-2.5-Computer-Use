"""
Database Configuration
SQLAlchemy setup with SQLite backend
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from config.settings import settings


# Database URL
DATABASE_URL = settings.database_url

# Create engine
if "sqlite" in DATABASE_URL:
    # SQLite-specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def init_db():
    """Initialize database tables - creates all tables if they don't exist"""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Get a new database session"""
    return SessionLocal()