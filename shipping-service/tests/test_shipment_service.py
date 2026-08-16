"""
Unit tests for ShipmentService.

Event publishers are mocked — no real RabbitMQ needed.
"""
import uuid
import pytest
from unittest.mock import patch

from app.models.shipment import Shipment, ShipmentStatus
from app.services.shipment_service import ShipmentService, ShipmentError


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _str_uuid() -> str:
    return str(uuid.uuid4())


async def _create_shipment(db, order_id=None, user_id=None) -> Shipment:
    return await ShipmentService.create(
        db=db,
        order_id=order_id or _str_uuid(),
        user_id=user_id or _str_uuid(),
        delivery_address="12 Wuse Zone 4, Abuja",
        driver_name="Emeka Obi",
        driver_phone="+2348012345678",
    )


# ── create ────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestShipmentServiceCreate:

    async def test_creates_shipment_with_pending_status(self, db):
        shipment = await _create_shipment(db)
        assert shipment.status == ShipmentStatus.pending

    async def test_stores_all_fields(self, db):
        order_id = _str_uuid()
        user_id  = _str_uuid()
        shipment = await ShipmentService.create(
            db=db,
            order_id=order_id,
            user_id=user_id,
            delivery_address="12 Wuse Zone 4, Abuja",
            driver_name="Emeka Obi",
            driver_phone="+2348012345678",
            tracking_note="Handle with care",
        )
        assert str(shipment.order_id)       == order_id
        assert str(shipment.user_id)        == user_id
        assert shipment.delivery_address    == "12 Wuse Zone 4, Abuja"
        assert shipment.driver_name         == "Emeka Obi"
        assert shipment.driver_phone        == "+2348012345678"
        assert shipment.tracking_note       == "Handle with care"
        assert shipment.dispatched_at is None
        assert shipment.delivered_at  is None

    async def test_duplicate_order_raises_shipment_error(self, db):
        order_id = _str_uuid()
        await _create_shipment(db, order_id=order_id)
        with pytest.raises(ShipmentError, match="already exists"):
            await _create_shipment(db, order_id=order_id)

    async def test_different_orders_create_separate_shipments(self, db):
        s1 = await _create_shipment(db)
        s2 = await _create_shipment(db)
        assert s1.id != s2.id


# ── dispatch ──────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestShipmentServiceDispatch:

    async def test_dispatch_updates_status_to_dispatched(self, db):
        with patch("app.services.shipment_service.publish_shipment_dispatched"):
            shipment = await _create_shipment(db)
            result = await ShipmentService.dispatch(db, str(shipment.id))
        assert result.status == ShipmentStatus.dispatched

    async def test_dispatch_sets_dispatched_at_timestamp(self, db):
        with patch("app.services.shipment_service.publish_shipment_dispatched"):
            shipment = await _create_shipment(db)
            result = await ShipmentService.dispatch(db, str(shipment.id))
        assert result.dispatched_at is not None

    async def test_dispatch_updates_driver_info(self, db):
        with patch("app.services.shipment_service.publish_shipment_dispatched"):
            shipment = await _create_shipment(db)
            result = await ShipmentService.dispatch(
                db, str(shipment.id),
                driver_name="Chidi Nwosu",
                driver_phone="+2348099999999",
                tracking_note="On the way",
            )
        assert result.driver_name   == "Chidi Nwosu"
        assert result.driver_phone  == "+2348099999999"
        assert result.tracking_note == "On the way"

    async def test_dispatch_publishes_event(self, db):
        with patch("app.services.shipment_service.publish_shipment_dispatched") as mock_pub:
            shipment = await _create_shipment(db)
            await ShipmentService.dispatch(db, str(shipment.id))
        mock_pub.assert_called_once()

    async def test_dispatch_nonexistent_shipment_raises_error(self, db):
        with pytest.raises(ShipmentError, match="not found"):
            await ShipmentService.dispatch(db, str(_uuid()))

    async def test_cannot_dispatch_already_dispatched_shipment(self, db):
        with patch("app.services.shipment_service.publish_shipment_dispatched"):
            shipment = await _create_shipment(db)
            await ShipmentService.dispatch(db, str(shipment.id))
            with pytest.raises(ShipmentError, match="only 'pending'"):
                await ShipmentService.dispatch(db, str(shipment.id))

    async def test_cannot_dispatch_delivered_shipment(self, db):
        with patch("app.services.shipment_service.publish_shipment_dispatched"), \
             patch("app.services.shipment_service.publish_shipment_delivered"):
            shipment = await _create_shipment(db)
            await ShipmentService.dispatch(db, str(shipment.id))
            await ShipmentService.deliver(db, str(shipment.id))
            with pytest.raises(ShipmentError, match="only 'pending'"):
                await ShipmentService.dispatch(db, str(shipment.id))


# ── deliver ───────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestShipmentServiceDeliver:

    async def _dispatch(self, db, shipment):
        with patch("app.services.shipment_service.publish_shipment_dispatched"):
            return await ShipmentService.dispatch(db, str(shipment.id))

    async def test_deliver_updates_status_to_delivered(self, db):
        with patch("app.services.shipment_service.publish_shipment_dispatched"), \
             patch("app.services.shipment_service.publish_shipment_delivered"):
            shipment = await _create_shipment(db)
            await ShipmentService.dispatch(db, str(shipment.id))
            result = await ShipmentService.deliver(db, str(shipment.id))
        assert result.status == ShipmentStatus.delivered

    async def test_deliver_sets_delivered_at_timestamp(self, db):
        with patch("app.services.shipment_service.publish_shipment_dispatched"), \
             patch("app.services.shipment_service.publish_shipment_delivered"):
            shipment = await _create_shipment(db)
            await ShipmentService.dispatch(db, str(shipment.id))
            result = await ShipmentService.deliver(db, str(shipment.id))
        assert result.delivered_at is not None

    async def test_deliver_publishes_event(self, db):
        with patch("app.services.shipment_service.publish_shipment_dispatched"), \
             patch("app.services.shipment_service.publish_shipment_delivered") as mock_pub:
            shipment = await _create_shipment(db)
            await ShipmentService.dispatch(db, str(shipment.id))
            await ShipmentService.deliver(db, str(shipment.id))
        mock_pub.assert_called_once()

    async def test_cannot_deliver_pending_shipment(self, db):
        shipment = await _create_shipment(db)
        with pytest.raises(ShipmentError, match="only 'dispatched'"):
            await ShipmentService.deliver(db, str(shipment.id))

    async def test_deliver_nonexistent_shipment_raises_error(self, db):
        with pytest.raises(ShipmentError, match="not found"):
            await ShipmentService.deliver(db, str(_uuid()))

    async def test_cannot_deliver_twice(self, db):
        with patch("app.services.shipment_service.publish_shipment_dispatched"), \
             patch("app.services.shipment_service.publish_shipment_delivered"):
            shipment = await _create_shipment(db)
            await ShipmentService.dispatch(db, str(shipment.id))
            await ShipmentService.deliver(db, str(shipment.id))
            with pytest.raises(ShipmentError, match="only 'dispatched'"):
                await ShipmentService.deliver(db, str(shipment.id))


# ── get_by_order / get_by_id ──────────────────────────────────────

@pytest.mark.asyncio
class TestShipmentServiceGet:

    async def test_get_by_order_returns_shipment(self, db):
        order_id = _str_uuid()
        shipment = await _create_shipment(db, order_id=order_id)
        result = await ShipmentService.get_by_order(db, order_id)
        assert result is not None
        assert result.id == shipment.id

    async def test_get_by_order_returns_none_for_unknown_order(self, db):
        result = await ShipmentService.get_by_order(db, _str_uuid())
        assert result is None

    async def test_get_by_id_returns_shipment(self, db):
        shipment = await _create_shipment(db)
        result = await ShipmentService.get_by_id(db, str(shipment.id))
        assert result is not None
        assert result.id == shipment.id

    async def test_get_by_id_returns_none_for_unknown_id(self, db):
        result = await ShipmentService.get_by_id(db, str(_uuid()))
        assert result is None
