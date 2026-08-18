"""
shipping-service-worker

Consumes payment.succeeded from RabbitMQ and automatically creates a
pending shipment for the paid order.

This removes the need for staff to manually create shipments — the
shipment is created the moment payment is confirmed. Staff only need
to dispatch (driver picked up) and deliver (customer received).

Flow:
    payment.succeeded
        → create Shipment(status=pending)
        → staff sees it in dashboard
        → staff clicks Dispatch → shipment.dispatched published
        → order-service-worker: order → shipped
        → notification-service: "On the way" email
        → staff clicks Deliver → shipment.delivered published
        → order-service-worker: order → delivered
        → notification-service: "Delivered" email
"""
import os
import json
import uuid
import logging
import asyncio
import aio_pika

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from app.models.shipment import Shipment, ShipmentStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shipping-service-worker")

DATABASE_URL = os.getenv("DATABASE_URL")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
QUEUE_NAME   = "shipping_service.payment_events"


def get_session_factory():
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def handle_payment_succeeded(data: dict, session_factory) -> None:
    """
    Auto-create a pending shipment when payment is confirmed.
    Idempotent — if a shipment already exists for the order, skip.
    """
    import uuid6
    order_id = data.get("order_id")
    user_id  = data.get("user_id")

    if not order_id or not user_id:
        logger.warning(f"payment.succeeded missing order_id or user_id: {data}")
        return

    async with session_factory() as db:
        # Idempotency check — don't create duplicate shipments
        existing = await db.execute(
            select(Shipment).where(Shipment.order_id == uuid.UUID(order_id))
        )
        if existing.scalar_one_or_none():
            logger.info(f"Shipment already exists for order {order_id} — skipping")
            return

        shipment = Shipment(
            order_id=uuid.UUID(order_id),
            user_id=uuid.UUID(user_id),
            delivery_address="To be confirmed by staff",
            status=ShipmentStatus.pending,
        )
        db.add(shipment)
        await db.commit()
        logger.info(
            f"Auto-created pending shipment for order {order_id} "
            f"(payment.succeeded consumed)"
        )


async def main():
    session_factory = get_session_factory()

    while True:
        try:
            logger.info("Connecting to RabbitMQ...")
            connection = await aio_pika.connect_robust(RABBITMQ_URL)

            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=1)

                payment_exchange = await channel.declare_exchange(
                    "payment_events",
                    aio_pika.ExchangeType.TOPIC,
                    durable=True,
                )

                queue = await channel.declare_queue(QUEUE_NAME, durable=True)
                await queue.bind(payment_exchange, routing_key="payment.succeeded")

                logger.info(
                    f"shipping-service-worker started — "
                    f"listening on '{QUEUE_NAME}' for payment.succeeded"
                )

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process(requeue=False):
                            try:
                                data  = json.loads(message.body)
                                event = data.get("event")
                                logger.info(f"Received event: {event}")
                                if event == "payment.succeeded":
                                    await handle_payment_succeeded(data, session_factory)
                                else:
                                    logger.info(f"Ignoring event: {event}")
                            except Exception as e:
                                logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Connection error: {e}. Retrying in 5s...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())