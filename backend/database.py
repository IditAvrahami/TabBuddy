import logging
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

# PostgreSQL connection string - required environment variable
DATABASE_URL: str
_env_database_url = os.getenv("DATABASE_URL")
if not _env_database_url:
    raise ValueError(
        "DATABASE_URL environment variable is required for PostgreSQL connection"
    )
DATABASE_URL = _env_database_url

logger.info(
    "Connecting to PostgreSQL database: %s",
    DATABASE_URL.replace(DATABASE_URL.split("@")[0].split("//")[1], "***"),
)

# Create PostgreSQL engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use DeclarativeBase for proper type checking
# Import after other setup to avoid circular dependencies
from sqlalchemy.orm import DeclarativeBase  # noqa: E402


# Define Base class directly - this works at runtime
# The type checking issue in pre-commit is handled via pyproject.toml overrides
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    logger.info("Opening PostgreSQL session")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.info("Closed PostgreSQL session")
