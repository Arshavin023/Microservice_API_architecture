"""
notification-service worker

Runs as a fully async program using aio-pika instead of pika.
This avoids the event loop conflict between pika's blocking connection
and SQLAlchemy's asyncpg driver — everything runs in one async context.
"""

import os
import json
import logging
import asyncio
import httpx
import aio_pika

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification-service")

DATABASE_URL = os.getenv("DATABASE_URL")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
QUEUE_NAME = "notification_service.events"


def get_session_factory():
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_user_email(user_id: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{USER_SERVICE_URL}/users/internal/{user_id}")
        if resp.status_code == 200:
            return resp.json().get("email")
        logger.warning(f"user-service returned {resp.status_code} for user {user_id}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Could not reach user-service for user {user_id}: {e}")
        return None


async def already_sent(session_factory, order_id: str, notification_type: str) -> bool:
    from app.models.notification import Notification, NotificationType
    from uuid import UUID

    async with session_factory() as db:
        result = await db.execute(
            select(Notification).where(
                Notification.order_id == UUID(order_id),
                Notification.notification_type == NotificationType(notification_type),
                Notification.sent == True,
            )
        )
        return result.scalar_one_or_none() is not None


async def log_notification(
    session_factory,
    order_id,
    user_id,
    to_email,
    notification_type,
    subject,
    sent,
    error_message=None,
):
    from app.models.notification import Notification, NotificationType
    from uuid import UUID

    async with session_factory() as db:
        notif = Notification(
            order_id=UUID(order_id),
            user_id=UUID(user_id),
            to_email=to_email,
            notification_type=NotificationType(notification_type),
            subject=subject,
            sent=sent,
            error_message=error_message,
        )
        db.add(notif)
        await db.commit()


async def handle_payment_succeeded(data: dict, session_factory) -> None:
    from app.utils.templates import payment_succeeded
    from app.utils.ses import send_email

    order_id = data.get("order_id", "")
    user_id = data.get("user_id", "")
    amount = data.get("amount", "0")
    notif_type = "payment_succeeded"
    if await already_sent(session_factory, order_id, notif_type):
        logger.info(f"Already sent {notif_type} for {order_id}")
        return
    email = await get_user_email(user_id)
    if not email:
        logger.error(f"No email for user {user_id}")
        return
    subject, html, text = payment_succeeded(order_id, amount)
    sent = send_email(email, subject, html, text)
    await log_notification(
        session_factory, order_id, user_id, email, notif_type, subject, sent
    )


async def handle_payment_failed(data: dict, session_factory) -> None:
    from app.utils.templates import payment_failed
    from app.utils.ses import send_email

    order_id = data.get("order_id", "")
    user_id = data.get("user_id", "")
    notif_type = "payment_failed"
    if await already_sent(session_factory, order_id, notif_type):
        logger.info(f"Already sent {notif_type} for {order_id}")
        return
    email = await get_user_email(user_id)
    if not email:
        logger.error(f"No email for user {user_id}")
        return
    subject, html, text = payment_failed(order_id)
    sent = send_email(email, subject, html, text)
    await log_notification(
        session_factory, order_id, user_id, email, notif_type, subject, sent
    )


async def handle_shipment_dispatched(data: dict, session_factory) -> None:
    from app.utils.templates import shipment_dispatched
    from app.utils.ses import send_email

    order_id = data.get("order_id", "")
    user_id = data.get("user_id", "")
    driver_name = data.get("driver_name")
    driver_phone = data.get("driver_phone")
    delivery_address = data.get("delivery_address", "")
    notif_type = "shipment_dispatched"
    if await already_sent(session_factory, order_id, notif_type):
        logger.info(f"Already sent {notif_type} for {order_id}")
        return
    email = await get_user_email(user_id)
    if not email:
        logger.error(f"No email for user {user_id}")
        return
    subject, html, text = shipment_dispatched(
        order_id, driver_name, driver_phone, delivery_address
    )
    sent = send_email(email, subject, html, text)
    await log_notification(
        session_factory, order_id, user_id, email, notif_type, subject, sent
    )


async def handle_shipment_delivered(data: dict, session_factory) -> None:
    from app.utils.templates import shipment_delivered
    from app.utils.ses import send_email

    order_id = data.get("order_id", "")
    user_id = data.get("user_id", "")
    notif_type = "shipment_delivered"
    if await already_sent(session_factory, order_id, notif_type):
        logger.info(f"Already sent {notif_type} for {order_id}")
        return
    email = await get_user_email(user_id)
    if not email:
        logger.error(f"No email for user {user_id}")
        return
    subject, html, text = shipment_delivered(order_id)
    sent = send_email(email, subject, html, text)
    await log_notification(
        session_factory, order_id, user_id, email, notif_type, subject, sent
    )


async def handle_delivery_pending(data: dict, session_factory) -> None:
    from app.utils.templates import delivery_pending_confirmation
    from app.utils.ses import send_email

    order_id = data.get("order_id", "")
    user_id = data.get("user_id", "")
    notif_type = "shipment_delivered"  # reuse — customer confirmation request

    if await already_sent(session_factory, order_id, notif_type):
        logger.info(f"Already sent delivery confirmation request for {order_id}")
        return
    email = await get_user_email(user_id)
    if not email:
        logger.error(f"No email for user {user_id}")
        return
    subject, html, text = delivery_pending_confirmation(order_id)
    sent = send_email(email, subject, html, text)
    await log_notification(
        session_factory, order_id, user_id, email, notif_type, subject, sent
    )


HANDLERS = {
    "payment.succeeded": handle_payment_succeeded,
    "payment.failed": handle_payment_failed,
    "shipment.dispatched": handle_shipment_dispatched,
    "shipment.delivery_pending": handle_delivery_pending,
    "shipment.delivered": handle_shipment_delivered,
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

                for exchange_name in ("payment_events", "shipping_events"):
                    await channel.declare_exchange(
                        exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
                    )

                queue = await channel.declare_queue(QUEUE_NAME, durable=True)

                payment_exchange = await channel.get_exchange("payment_events")
                shipping_exchange = await channel.get_exchange("shipping_events")

                await queue.bind(payment_exchange, routing_key="payment.succeeded")
                await queue.bind(payment_exchange, routing_key="payment.failed")
                await queue.bind(shipping_exchange, routing_key="shipment.dispatched")
                await queue.bind(
                    shipping_exchange, routing_key="shipment.delivery_pending"
                )
                await queue.bind(shipping_exchange, routing_key="shipment.delivered")

                logger.info(
                    f"notification-service started — "
                    f"listening on '{QUEUE_NAME}' for payment + shipping events"
                )

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process(requeue=False):
                            try:
                                data = json.loads(message.body)
                                event = data.get("event")
                                logger.info(f"Received event: {event}")
                                handler = HANDLERS.get(event)
                                if handler:
                                    await handler(data, session_factory)
                                else:
                                    logger.info(f"No handler for '{event}' — skipping")
                            except Exception as e:
                                logger.error(f"Error processing {event}: {e}")

        except Exception as e:
            logger.error(f"Connection error: {e}. Retrying in 5s...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
