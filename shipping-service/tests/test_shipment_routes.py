"""
Route-level tests for shipping-service HTTP endpoints.

Events are mocked — no real RabbitMQ needed.
Auth dependencies (require_staff, get_current_user_id) are overridden
in conftest.py so tests don't need fastapi_jwt_auth2 running.
"""
import uuid
import pytest
from unittest.mock import patch

from app.models.shipment import Shipment, ShipmentStatus

SHIPMENTS_URL = "/shipments"


def _new_uuid() -> str:
    return str(uuid.uuid4())


def _shipment_payload(**overrides):
    base = {
        "order_id":         _new_uuid(),
        "user_id":          _new_uuid(),
        "delivery_address": "12 Wuse Zone 4, Abuja",
        "driver_name":      "Emeka Obi",
        "driver_phone":     "+2348012345678",
    }
    return {**base, **overrides}


# ── POST /shipments ───────────────────────────────────────────────

@pytest.mark.asyncio
class TestCreateShipment:

    async def test_create_returns_201(self, client, db):
        resp = await client.post(SHIPMENTS_URL, json=_shipment_payload())
        assert resp.status_code == 201

    async def test_create_returns_pending_status(self, client, db):
        resp = await client.post(SHIPMENTS_URL, json=_shipment_payload())
        assert resp.json()["status"] == "pending"

    async def test_create_stores_all_fields(self, client, db):
        payload = _shipment_payload(
            tracking_note="Handle with care"
        )
        resp = await client.post(SHIPMENTS_URL, json=payload)
        data = resp.json()
        assert data["delivery_address"] == payload["delivery_address"]
        assert data["driver_name"]      == payload["driver_name"]
        assert data["driver_phone"]     == payload["driver_phone"]
        assert data["tracking_note"]    == "Handle with care"

    async def test_create_missing_delivery_address_422(self, client, db):
        payload = _shipment_payload()
        del payload["delivery_address"]
        resp = await client.post(SHIPMENTS_URL, json=payload)
        assert resp.status_code == 422

    async def test_create_missing_order_id_422(self, client, db):
        payload = _shipment_payload()
        del payload["order_id"]
        resp = await client.post(SHIPMENTS_URL, json=payload)
        assert resp.status_code == 422

    async def test_duplicate_order_returns_409(self, client, db):
        payload = _shipment_payload()
        await client.post(SHIPMENTS_URL, json=payload)
        resp = await client.post(SHIPMENTS_URL, json=payload)
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]


# ── PATCH /shipments/{id}/dispatch ───────────────────────────────

@pytest.mark.asyncio
class TestDispatchShipment:

    async def _create(self, client):
        resp = await client.post(SHIPMENTS_URL, json=_shipment_payload())
        return resp.json()["id"]

    async def test_dispatch_returns_200(self, client, db):
        shipment_id = await self._create(client)
        with patch("app.services.shipment_service.publish_shipment_dispatched"):
            resp = await client.patch(
                f"{SHIPMENTS_URL}/{shipment_id}/dispatch",
                json={"tracking_note": "Driver left"},
            )
        assert resp.status_code == 200

    async def test_dispatch_changes_status_to_dispatched(self, client, db):
        shipment_id = await self._create(client)
        with patch("app.services.shipment_service.publish_shipment_dispatched"):
            resp = await client.patch(
                f"{SHIPMENTS_URL}/{shipment_id}/dispatch",
                json={},
            )
        assert resp.json()["status"] == "dispatched"

    async def test_dispatch_sets_dispatched_at(self, client, db):
        shipment_id = await self._create(client)
        with patch("app.services.shipment_service.publish_shipment_dispatched"):
            resp = await client.patch(
                f"{SHIPMENTS_URL}/{shipment_id}/dispatch",
                json={},
            )
        assert resp.json()["dispatched_at"] is not None

    async def test_dispatch_nonexistent_shipment_409(self, client, db):
        with patch("app.services.shipment_service.publish_shipment_dispatched"):
            resp = await client.patch(
                f"{SHIPMENTS_URL}/{_new_uuid()}/dispatch",
                json={},
            )
        assert resp.status_code == 409

    async def test_dispatch_twice_returns_409(self, client, db):
        shipment_id = await self._create(client)
        with patch("app.services.shipment_service.publish_shipment_dispatched"):
            await client.patch(f"{SHIPMENTS_URL}/{shipment_id}/dispatch", json={})
            resp = await client.patch(f"{SHIPMENTS_URL}/{shipment_id}/dispatch", json={})
        assert resp.status_code == 409

    async def test_dispatch_invalid_uuid_422(self, client, db):
        resp = await client.patch(
            f"{SHIPMENTS_URL}/not-a-uuid/dispatch",
            json={},
        )
        assert resp.status_code == 422


# ── PATCH /shipments/{id}/deliver ────────────────────────────────

@pytest.mark.asyncio
class TestDeliverShipment:

    async def _create_and_dispatch(self, client):
        resp = await client.post(SHIPMENTS_URL, json=_shipment_payload())
        shipment_id = resp.json()["id"]
        with patch("app.services.shipment_service.publish_shipment_dispatched"):
            await client.patch(f"{SHIPMENTS_URL}/{shipment_id}/dispatch", json={})
        return shipment_id

    async def test_deliver_returns_200(self, client, db):
        shipment_id = await self._create_and_dispatch(client)
        with patch("app.services.shipment_service.publish_shipment_delivered"):
            resp = await client.patch(
                f"{SHIPMENTS_URL}/{shipment_id}/deliver",
                json={"tracking_note": "Customer received"},
            )
        assert resp.status_code == 200

    async def test_deliver_changes_status_to_delivered(self, client, db):
        shipment_id = await self._create_and_dispatch(client)
        with patch("app.services.shipment_service.publish_shipment_delivered"):
            resp = await client.patch(
                f"{SHIPMENTS_URL}/{shipment_id}/deliver",
                json={},
            )
        assert resp.json()["status"] == "delivered"

    async def test_deliver_sets_delivered_at(self, client, db):
        shipment_id = await self._create_and_dispatch(client)
        with patch("app.services.shipment_service.publish_shipment_delivered"):
            resp = await client.patch(
                f"{SHIPMENTS_URL}/{shipment_id}/deliver",
                json={},
            )
        assert resp.json()["delivered_at"] is not None

    async def test_deliver_pending_shipment_returns_409(self, client, db):
        resp = await client.post(SHIPMENTS_URL, json=_shipment_payload())
        shipment_id = resp.json()["id"]
        with patch("app.services.shipment_service.publish_shipment_delivered"):
            resp = await client.patch(
                f"{SHIPMENTS_URL}/{shipment_id}/deliver",
                json={},
            )
        assert resp.status_code == 409

    async def test_deliver_nonexistent_shipment_409(self, client, db):
        with patch("app.services.shipment_service.publish_shipment_delivered"):
            resp = await client.patch(
                f"{SHIPMENTS_URL}/{_new_uuid()}/deliver",
                json={},
            )
        assert resp.status_code == 409

    async def test_deliver_twice_returns_409(self, client, db):
        shipment_id = await self._create_and_dispatch(client)
        with patch("app.services.shipment_service.publish_shipment_delivered"):
            await client.patch(f"{SHIPMENTS_URL}/{shipment_id}/deliver", json={})
            resp = await client.patch(f"{SHIPMENTS_URL}/{shipment_id}/deliver", json={})
        assert resp.status_code == 409


# ── GET /shipments/{id} (staff) ───────────────────────────────────

@pytest.mark.asyncio
class TestGetShipment:

    async def test_staff_can_get_shipment_by_id(self, client, db):
        resp = await client.post(SHIPMENTS_URL, json=_shipment_payload())
        shipment_id = resp.json()["id"]
        resp = await client.get(f"{SHIPMENTS_URL}/{shipment_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == shipment_id

    async def test_nonexistent_shipment_returns_404(self, client, db):
        resp = await client.get(f"{SHIPMENTS_URL}/{_new_uuid()}")
        assert resp.status_code == 404

    async def test_invalid_uuid_returns_422(self, client, db):
        resp = await client.get(f"{SHIPMENTS_URL}/not-a-uuid")
        assert resp.status_code == 422


# ── GET /shipments/order/{order_id} (customer) ───────────────────

@pytest.mark.asyncio
class TestGetShipmentByOrder:

    async def test_customer_can_track_own_shipment(self, client, db):
        # The conftest override makes get_current_user_id return _customer_user_id
        # We create the shipment with that same user_id so ownership check passes
        customer_user_id = str(client._customer_user_id)
        order_id = _new_uuid()
        payload = _shipment_payload(order_id=order_id, user_id=customer_user_id)
        await client.post(SHIPMENTS_URL, json=payload)

        resp = await client.get(f"{SHIPMENTS_URL}/order/{order_id}")
        assert resp.status_code == 200
        assert resp.json()["order_id"] == order_id

    async def test_returns_404_when_no_shipment_for_order(self, client, db):
        resp = await client.get(f"{SHIPMENTS_URL}/order/{_new_uuid()}")
        assert resp.status_code == 404

    async def test_customer_cannot_view_other_users_shipment(self, client, db):
        # Create shipment with a different user_id than the authenticated customer
        order_id       = _new_uuid()
        other_user_id  = _new_uuid()
        payload = _shipment_payload(order_id=order_id, user_id=str(other_user_id))
        await client.post(SHIPMENTS_URL, json=payload)

        resp = await client.get(f"{SHIPMENTS_URL}/order/{order_id}")
        assert resp.status_code == 403


# ── GET /health ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
