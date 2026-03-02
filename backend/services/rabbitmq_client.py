import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aio_pika
from aio_pika.abc import (
    AbstractChannel,
    AbstractExchange,
    AbstractQueue,
    AbstractQueueIterator,
    AbstractRobustConnection,
)

logger = logging.getLogger(__name__)

# Global connection (will be initialized on startup)
_connection: AbstractRobustConnection | None = None
_channel: AbstractChannel | None = None
_exchange: AbstractExchange | None = None
_queue: AbstractQueue | None = None


async def get_rabbitmq_connection() -> AbstractRobustConnection:
    """Get or create RabbitMQ connection"""
    global _connection
    if _connection is None or _connection.is_closed:
        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        _connection = await aio_pika.connect_robust(rabbitmq_url)
        logger.info("Connected to RabbitMQ")
    assert _connection is not None
    return _connection


async def get_rabbitmq_channel() -> AbstractChannel:
    """Get or create RabbitMQ channel"""
    global _channel
    if _channel is None or _channel.is_closed:
        connection = await get_rabbitmq_connection()
        _channel = await connection.channel()
        logger.info("Created RabbitMQ channel")
    assert _channel is not None
    return _channel


async def get_notifications_exchange() -> AbstractExchange:
    """Get or create notifications exchange"""
    global _exchange
    if _exchange is None:
        channel = await get_rabbitmq_channel()
        _exchange = await channel.declare_exchange(
            "notifications", aio_pika.ExchangeType.DIRECT, durable=True
        )
        logger.info("Declared notifications exchange")
    assert _exchange is not None
    return _exchange


async def get_notifications_queue() -> AbstractQueue:
    """Get or create notifications queue"""
    global _queue
    if _queue is None:
        channel = await get_rabbitmq_channel()
        exchange = await get_notifications_exchange()
        queue = await channel.declare_queue("notifications", durable=True)
        await queue.bind(exchange, routing_key="notification.ready")
        _queue = queue
        logger.info("Declared and bound notifications queue")
    assert _queue is not None
    return _queue


@asynccontextmanager
async def get_rabbitmq_consumer() -> AsyncIterator[AbstractQueueIterator]:
    """Context manager for consuming from RabbitMQ queue"""
    queue = await get_notifications_queue()
    async with queue.iterator() as queue_iter:
        yield queue_iter


async def close_rabbitmq_connection() -> None:
    """Close RabbitMQ connection"""
    global _connection, _channel, _exchange, _queue
    if _channel and not _channel.is_closed:
        await _channel.close()
    if _connection and not _connection.is_closed:
        await _connection.close()
    _connection = None
    _channel = None
    _exchange = None
    _queue = None
    logger.info("Closed RabbitMQ connection")
