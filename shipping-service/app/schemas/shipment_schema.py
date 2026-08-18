from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class ShipmentStatusEnum(str, Enum):
    pending = "pending"
    dispatched = "dispatched"
    delivered = "delivered"


class CreateShipmentRequest(BaseModel):
    """Staff creates a shipment for a paid order."""

    order_id: UUID
    user_id: UUID
    delivery_address: str
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    tracking_note: Optional[str] = None


class DispatchShipmentRequest(BaseModel):
    """Staff marks a shipment as dispatched (driver left with order)."""

    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    tracking_note: Optional[str] = None


class DeliverShipmentRequest(BaseModel):
    """Staff marks a shipment as delivered."""

    tracking_note: Optional[str] = None


class ShipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    user_id: UUID
    status: ShipmentStatusEnum
    delivery_address: str
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    tracking_note: Optional[str] = None
    dispatched_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
