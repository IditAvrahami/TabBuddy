import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.drug import router as drug_router
from backend.api.meal import router as meal_router
from backend.api.notifications import router as notifications_router
from backend.database import Base, engine
from backend.services.rabbitmq_client import (
    close_rabbitmq_connection,
    get_notifications_exchange,
    get_notifications_queue,
)
from backend.services.redis_client import close_redis, init_redis

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    try:
        # Create PostgreSQL tables
        Base.metadata.create_all(bind=engine)
        logger.info("PostgreSQL tables created successfully")
    except Exception as e:
        logger.error("Failed to create PostgreSQL tables: %s", e)
        raise

    try:
        # Initialize Redis
        init_redis()
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}", exc_info=True)
        raise

    try:
        # Initialize RabbitMQ queue and exchange
        await get_notifications_queue()
        await get_notifications_exchange()
        logger.info("RabbitMQ initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RabbitMQ: {e}", exc_info=True)

    yield

    # Shutdown
    try:
        await close_redis()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}", exc_info=True)

    try:
        await close_rabbitmq_connection()
        logger.info("RabbitMQ connections closed")
    except Exception as e:
        logger.error(f"Error closing RabbitMQ connections: {e}", exc_info=True)


app = FastAPI(title="TabBuddy API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drug_router)
app.include_router(meal_router)
app.include_router(notifications_router)

logger.info("TabBuddy API started successfully")
