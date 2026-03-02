from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator

from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.connection import Connection as RedisConnection

logger = logging.getLogger(__name__)

# Redis connection pool (initialized in lifespan)
_redis_pool: ConnectionPool[RedisConnection] | None = None


async def get_redis_client() -> AsyncGenerator[Redis, None]:  # type: ignore[type-arg]
    """Dependency to get Redis client - creates client from pool per request"""
    if _redis_pool is None:
        raise RuntimeError(
            "Redis connection pool not initialized. Call init_redis() first."
        )

    # Create client from pool for this request
    client = Redis(connection_pool=_redis_pool, decode_responses=True)
    try:
        yield client
    finally:
        # Client will return connection to pool automatically
        await client.aclose()  # type: ignore[attr-defined]
        logger.debug("Redis client connection returned to pool")


def init_redis() -> ConnectionPool[RedisConnection]:
    """Initialize Redis connection pool (called in lifespan startup)"""
    global _redis_pool
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    _redis_pool = ConnectionPool.from_url(
        redis_url,
        decode_responses=True,
        max_connections=50,
    )
    logger.info("Redis connection pool initialized")
    return _redis_pool


async def close_redis() -> None:
    """Close Redis connection pool (called in lifespan shutdown)"""
    global _redis_pool
    if _redis_pool is not None:
        # adisconnect is the async version; disconnect is sync
        await _redis_pool.aclose()  # type: ignore[attr-defined]
        _redis_pool = None
        logger.info("Redis connection pool closed")
