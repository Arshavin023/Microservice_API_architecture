import uuid
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.shipment import Shipment, ShipmentStatus
from app.utils.events import publish_shipment_dispatched, publish_delivery_pending, publish_shipment_delivered

logger = logging.getLogger(__name__)


class ShipmentError(Exception):
    pass


class ShipmentService:

    @staticmethod
    async def create(
        db: AsyncSession,
        order_id: str,
        user_id: str,
        delivery_address: str,
        driver_name: str | None = None,
        driver_phone: str | None = None,
        tracking_note: str | None = None,
    ) -> Shipment:
        """
        Staff creates a shipment for a paid order.
        One shipment per order — enforced by the unique constraint on order_id.
        """
        # Guard against duplicate shipments for the same order
        existing = await db.execute(
            select(Shipment).where(Shipment.order_id == uuid.UUID(order_id))
        )
        if existing.scalar_one_or_none():
            raise ShipmentError(f"Shipment already exists for order {order_id}")

        shipment = Shipment(
            order_id=uuid.UUID(order_id),
            user_id=uuid.UUID(user_id),
            delivery_address=delivery_address,
            driver_name=driver_name,
            driver_phone=driver_phone,
            tracking_note=tracking_note,
            status=ShipmentStatus.pending,
        )
        db.add(shipment)
        await db.commit()
        await db.refresh(shipment)
        logger.info(f"Shipment created for order {order_id}")
        return shipment

    @staticmethod
    async def dispatch(
        db: AsyncSession,
        shipment_id: str,
        driver_name: str | None = None,
        driver_phone: str | None = None,
        tracking_note: str | None = None,
    ) -> Shipment:
        """
        Staff marks shipment as dispatched — driver left with the order.
        Publishes shipment.dispatched so order-service-worker can update
        the order status to 'shipped', and notification-service can email
        the customer.
        """
        result = await db.execute(
            select(Shipment).where(Shipment.id == uuid.UUID(shipment_id))
        )
        shipment = result.scalar_one_or_none()

        if not shipment:
            raise ShipmentError(f"Shipment {shipment_id} not found")

        if shipment.status != ShipmentStatus.pending:
            raise ShipmentError(
                f"Cannot dispatch shipment in status '{shipment.status}' "
                f"— only 'pending' shipments can be dispatched"
            )

        shipment.status        = ShipmentStatus.dispatched
        shipment.dispatched_at = datetime.utcnow()
        if driver_name:   shipment.driver_name  = driver_name
        if driver_phone:  shipment.driver_phone = driver_phone
        if tracking_note: shipment.tracking_note = tracking_note

        await db.commit()
        await db.refresh(shipment)

        publish_shipment_dispatched(
            shipment_id=str(shipment.id),
            order_id=str(shipment.order_id),
            user_id=str(shipment.user_id),
            delivery_address=shipment.delivery_address,
            driver_name=shipment.driver_name,
            driver_phone=shipment.driver_phone,
        )
        return shipment

    @staticmethod
    async def notify_customer(
        db: AsyncSession,
        shipment_id: str,
        tracking_note: str | None = None,
    ) -> Shipment:
        """
        Staff notifies customer that the rider has delivered the order.
        Sets shipment to 'delivered' internally but publishes
        shipment.delivery_pending so order-service sets the order to
        'awaiting_confirmation' and notification-service emails the customer
        to confirm receipt. A cron job auto-confirms after 2 hours if the
        customer doesn't respond.
        """
        result = await db.execute(
            select(Shipment).where(Shipment.id == uuid.UUID(shipment_id))
        )
        shipment = result.scalar_one_or_none()

        if not shipment:
            raise ShipmentError(f"Shipment {shipment_id} not found")

        if shipment.status != ShipmentStatus.dispatched:
            raise ShipmentError(
                f"Cannot notify delivery for shipment in status '{shipment.status}' "
                f"— only 'dispatched' shipments can be marked as delivery pending"
            )

        shipment.status       = ShipmentStatus.delivered
        shipment.delivered_at = datetime.utcnow()
        if tracking_note:
            shipment.tracking_note = tracking_note

        await db.commit()
        await db.refresh(shipment)

        publish_delivery_pending(
            shipment_id=str(shipment.id),
            order_id=str(shipment.order_id),
            user_id=str(shipment.user_id),
        )
        return shipment

    @staticmethod
    async def deliver(
        db: AsyncSession,
        shipment_id: str,
        tracking_note: str | None = None,
    ) -> Shipment:
        """
        Internal/cron use — directly marks shipment delivered and
        publishes shipment.delivered (used by auto-confirm after 2hrs).
        """
        result = await db.execute(
            select(Shipment).where(Shipment.id == uuid.UUID(shipment_id))
        )
        shipment = result.scalar_one_or_none()

        if not shipment:
            raise ShipmentError(f"Shipment {shipment_id} not found")

        if shipment.status != ShipmentStatus.dispatched:
            raise ShipmentError(
                f"Cannot deliver shipment in status '{shipment.status}'"
            )

        shipment.status       = ShipmentStatus.delivered
        shipment.delivered_at = datetime.utcnow()
        if tracking_note:
            shipment.tracking_note = tracking_note

        await db.commit()
        await db.refresh(shipment)

        publish_shipment_delivered(
            shipment_id=str(shipment.id),
            order_id=str(shipment.order_id),
            user_id=str(shipment.user_id),
        )
        return shipment

    @staticmethod
    async def get_by_order(
        db: AsyncSession,
        order_id: str,
    ) -> Shipment | None:
        result = await db.execute(
            select(Shipment).where(Shipment.order_id == uuid.UUID(order_id))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        shipment_id: str,
    ) -> Shipment | None:
        result = await db.execute(
            select(Shipment).where(Shipment.id == uuid.UUID(shipment_id))
        )
        return result.scalar_one_or_none()
