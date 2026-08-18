import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth2 import AuthJWT
from fastapi_jwt_auth2.exceptions import AuthJWTException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.auth import require_staff, get_current_user_id
from app.schemas.shipment_schema import (
    CreateShipmentRequest,
    DispatchShipmentRequest,
    DeliverShipmentRequest,
    ShipmentResponse,
)
from app.services.shipment_service import ShipmentService, ShipmentError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/shipments", tags=["Shipments"])


def _parse_uuid(value: str, field: str = "id") -> UUID:
    try:
        return UUID(value)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid {field} format")


# ── Staff write endpoints ─────────────────────────────────────────


@router.post("", response_model=ShipmentResponse, status_code=201)
async def create_shipment(
    data: CreateShipmentRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_staff),
):
    """
    Staff creates a shipment for a paid order.
    Call this after payment.succeeded has been confirmed and the kitchen
    has prepared the order for pickup.
    """
    try:
        shipment = await ShipmentService.create(
            db=db,
            order_id=str(data.order_id),
            user_id=str(data.user_id),
            delivery_address=data.delivery_address,
            driver_name=data.driver_name,
            driver_phone=data.driver_phone,
            tracking_note=data.tracking_note,
        )
    except ShipmentError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return shipment


@router.patch("/{shipment_id}/dispatch", response_model=ShipmentResponse)
async def dispatch_shipment(
    shipment_id: str,
    data: DispatchShipmentRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_staff),
):
    """
    Staff marks a shipment as dispatched — driver has picked up the order
    and is on the way to the customer.
    Publishes shipment.dispatched → order becomes 'shipped'.
    """
    uid = _parse_uuid(shipment_id, "shipment_id")
    try:
        shipment = await ShipmentService.dispatch(
            db=db,
            shipment_id=str(uid),
            driver_name=data.driver_name,
            driver_phone=data.driver_phone,
            tracking_note=data.tracking_note,
        )
    except ShipmentError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return shipment


@router.patch("/{shipment_id}/notify-customer", response_model=ShipmentResponse)
async def notify_customer(
    shipment_id: str,
    data: DeliverShipmentRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_staff),
):
    """
    Staff notifies customer that rider has delivered the order.
    Sets shipment to 'delivered', publishes shipment.delivery_pending
    so order moves to 'awaiting_confirmation' and customer gets an email
    asking them to confirm receipt. Auto-confirmed by cron after 2 hours.
    """
    uid = _parse_uuid(shipment_id, "shipment_id")
    try:
        shipment = await ShipmentService.notify_customer(
            db=db,
            shipment_id=str(uid),
            tracking_note=data.tracking_note,
        )
    except ShipmentError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return shipment


# ── Customer read endpoints ───────────────────────────────────────


@router.get("/order/{order_id}", response_model=ShipmentResponse)
async def get_shipment_by_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Customer tracks their shipment by order ID.
    Returns 404 if no shipment exists yet (order still being prepared).
    """
    uid = _parse_uuid(order_id, "order_id")
    shipment = await ShipmentService.get_by_order(db, str(uid))
    if not shipment:
        raise HTTPException(
            status_code=404,
            detail="No shipment found for this order yet",
        )
    # Customers can only view their own shipment
    if shipment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return shipment


@router.get("/order/{order_id}/staff", response_model=ShipmentResponse)
async def get_shipment_by_order_staff(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_staff),
):
    """Staff can look up any shipment by order ID."""
    uid = _parse_uuid(order_id, "order_id")
    shipment = await ShipmentService.get_by_order(db, str(uid))
    if not shipment:
        raise HTTPException(
            status_code=404,
            detail="No shipment found for this order yet",
        )
    return shipment


@router.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(
    shipment_id: str,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_staff),
):
    """Staff can look up any shipment directly by ID."""
    uid = _parse_uuid(shipment_id, "shipment_id")
    shipment = await ShipmentService.get_by_id(db, str(uid))
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment
