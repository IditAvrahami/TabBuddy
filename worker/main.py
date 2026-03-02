import asyncio
import json
import logging
import os
import sys
from datetime import date

import aio_pika
import redis.asyncio as redis
from pydantic import ValidationError

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.api.notifications import NotificationDto

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def worker_loop():
    """Main worker loop that checks Redis ZSET and publishes to RabbitMQ"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

    # Connect to Redis
    redis_client = redis.from_url(redis_url, decode_responses=True)
    logger.info("Connected to Redis")

    # Connect to RabbitMQ
    connection = await aio_pika.connect_robust(rabbitmq_url)
    logger.info("Connected to RabbitMQ")

    try:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            "notifications", aio_pika.ExchangeType.DIRECT, durable=True
        )
        queue = await channel.declare_queue("notifications", durable=True)
        await queue.bind(exchange, routing_key="notification.ready")
        logger.info("RabbitMQ queue and exchange declared")

        while True:
            try:
                today = date.today()
                today_str = today.isoformat()
                index_key = f"notifications:{today_str}"

                # Get current timestamp
                import time
                now = time.time()

                # Check if index key exists
                exists = await redis_client.exists(index_key)
                if not exists:
                    await asyncio.sleep(2)
                    continue

                # Get all due notification data keys from index (sorted by time!)
                # The index ZSET contains data key references as values
                due_data_keys = await redis_client.zrangebyscore(
                    index_key, min=0, max=now, withscores=False
                )

                if due_data_keys:
                    logger.info(
                        f"Found {len(due_data_keys)} due notifications for {today_str}"
                    )

                for data_key in due_data_keys:
                    try:
                        # Get actual notification data from data key
                        notification_json = await redis_client.get(data_key)

                        if not notification_json:
                            # Data key expired or missing, clean up index
                            logger.warning(f"Data key {data_key} not found, removing from index")
                            await redis_client.zrem(index_key, data_key)
                            continue

                        # Deserialize JSON to Pydantic object
                        notification = NotificationDto.model_validate_json(notification_json)

                        # Serialize Pydantic object to JSON for RabbitMQ
                        message_body = notification.model_dump_json()

                        # Publish to RabbitMQ
                        await exchange.publish(
                            aio_pika.Message(
                                message_body.encode(),
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                            ),
                            routing_key="notification.ready",
                        )

                        logger.info(
                            f"Published notification for {notification.drug_name} (schedule_id={notification.schedule_id})"
                        )

                        # Remove from both index and data
                        await redis_client.zrem(index_key, data_key)
                        await redis_client.delete(data_key)

                    except ValidationError as e:
                        logger.error(
                            f"Invalid notification data in Redis: {e}. Skipping."
                        )
                        # Remove invalid entry from both index and data
                        await redis_client.zrem(index_key, data_key)
                        await redis_client.delete(data_key)
                    except Exception as e:
                        logger.error(
                            f"Error processing notification: {e}", exc_info=True
                        )

                # Sleep for 2 seconds before next check
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error in worker loop: {e}", exc_info=True)
                await asyncio.sleep(2)

    finally:
        await connection.close()
        await redis_client.close()
        logger.info("Worker shutdown complete")


if __name__ == "__main__":
    logger.info("Starting notification worker...")
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker crashed: {e}", exc_info=True)
        raise
