import os
import logging
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

logger = logging.getLogger(__name__)

# PostgreSQL connection string - required environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required for PostgreSQL connection")

logger.info("Connecting to PostgreSQL database: %s", DATABASE_URL.replace(DATABASE_URL.split('@')[0].split('//')[1], '***'))

# Create PostgreSQL engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    logger.info("Opening PostgreSQL session")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.info("Closed PostgreSQL session")