import os
import json
import logging
import pika

logger = logging.getLogger(__name__)

RABBITMQ_URL   = os.getenv("RABBITMQ_URL")
EXCHANGE_NAME  = "shipping_events"
EXCHANGE_TYPE  = "topic"


def _publish(routing_key: str, message: dict) -> None:
    try:
        params     = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel    = connection.channel()

        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            durable=True,
        )

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(message, default=str),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )

        connection.close()
        logger.info(
            f"Published {routing_key} for order_id={message.get('order_id')}"
        )

    except Exception as e:
        # Event publish failure must not abort the shipment DB write.
        # Log loudly — a reconciliation or retry mechanism can pick this up.
        logger.error(f"Failed to publish {routing_key}: {e}")


def publish_shipment_dispatched(
    shipment_id: str,
    order_id: str,
    user_id: str,
    delivery_address: str,
    driver_name: str | None,
    driver_phone: str | None,
) -> None:
    _publish("shipment.dispatched", {
        "event":            "shipment.dispatched",
        "shipment_id":      shipment_id,
        "order_id":         order_id,
        "user_id":          user_id,
        "delivery_address": delivery_address,
        "driver_name":      driver_name,
        "driver_phone":     driver_phone,
    })


def publish_shipment_delivered(
    shipment_id: str,
    order_id: str,
    user_id: str,
) -> None:
    _publish("shipment.delivered", {
        "event":       "shipment.delivered",
        "shipment_id": shipment_id,
        "order_id":    order_id,
        "user_id":     user_id,
    })
