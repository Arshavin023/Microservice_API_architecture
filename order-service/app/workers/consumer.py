"""
order-service-worker

Consumes shipping events and drives the order state machine:
    shipment.dispatched → order: paid → shipped
    shipment.delivered  → order: shipped → delivered

Uses aio-pika (fully async) to avoid event loop conflicts with
SQLAlchemy's asyncpg driver.
"""
import os
import json
import logging
import asyncio
import aio_pika
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("order-service-worker")

DATABASE_URL  = os.getenv("DATABASE_URL")
RABBITMQ_URL  = os.getenv("RABBITMQ_URL")
EXCHANGE_NAME = "shipping_events"
QUEUE_NAME    = "order_service.shipping_events"


def get_session_factory():
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def handle_shipment_dispatched(data: dict, session_factory) -> None:
    order_id = data.get("order_id")
    if not order_id:
        logger.warning("shipment.dispatched missing order_id"); return

    async with session_factory() as db:
        result = await db.execute(
            text("UPDATE orders SET status='shipped', updated_at=now() "
                 "WHERE id=:oid AND status='paid' RETURNING id"),
            {"oid": order_id},
        )
        await db.commit()

    if result.fetchone():
        logger.info(f"Order {order_id} → shipped")
    else:
        logger.warning(f"Order {order_id} not updated — not in 'paid' state (idempotent)")


async def handle_shipment_delivered(data: dict, session_factory) -> None:
    order_id = data.get("order_id")
    if not order_id:
        logger.warning("shipment.delivered missing order_id"); return

    async with session_factory() as db:
        result = await db.execute(
            text("UPDATE orders SET status='delivered', updated_at=now() "
                 "WHERE id=:oid AND status IN ('awaiting_confirmation','shipped') RETURNING id"),
            {"oid": order_id},
        )
        await db.commit()

    if result.fetchone():
        logger.info(f"Order {order_id} → delivered")
    else:
        logger.warning(f"Order {order_id} not updated — not in expected state (idempotent)")


async def handle_delivery_pending(data: dict, session_factory) -> None:
    """Order: shipped → awaiting_confirmation (customer must confirm or auto-confirms in 2hrs)."""
    order_id = data.get("order_id")
    if not order_id:
        logger.warning("shipment.delivery_pending missing order_id"); return

    async with session_factory() as db:
        result = await db.execute(
            text("UPDATE orders SET status='awaiting_confirmation', updated_at=now() "
                 "WHERE id=:oid AND status='shipped' RETURNING id"),
            {"oid": order_id},
        )
        await db.commit()

    if result.fetchone():
        logger.info(f"Order {order_id} → awaiting_confirmation")
    else:
        logger.warning(f"Order {order_id} not updated to awaiting_confirmation (idempotent)")


HANDLERS = {
    "shipment.dispatched":       handle_shipment_dispatched,
    "shipment.delivery_pending": handle_delivery_pending,
    "shipment.delivered":        handle_shipment_delivered,
}


async def main():
    session_factory = get_session_factory()

    while True:
        try:
            logger.info("Connecting to RabbitMQ...")
            connection = await aio_pika.connect_robust(RABBITMQ_URL)

            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=1)

                exchange = await channel.declare_exchange(
                    EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
                )

                queue = await channel.declare_queue(QUEUE_NAME, durable=True)
                await queue.bind(exchange, routing_key="shipment.dispatched")
                await queue.bind(exchange, routing_key="shipment.delivery_pending")
                await queue.bind(exchange, routing_key="shipment.delivered")

                logger.info(
                    f"order-service-worker started — "
                    f"listening on '{QUEUE_NAME}' for shipment events"
                )

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process(requeue=False):
                            try:
                                data    = json.loads(message.body)
                                event   = data.get("event")
                                logger.info(f"Received event: {event}")
                                handler = HANDLERS.get(event)
                                if handler:
                                    await handler(data, session_factory)
                                else:
                                    logger.info(f"No handler for '{event}' — skipping")
                            except Exception as e:
                                logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Connection error: {e}. Retrying in 5s...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
