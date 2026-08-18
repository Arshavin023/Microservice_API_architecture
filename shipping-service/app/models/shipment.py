import uuid6
import enum
from sqlalchemy import Column, String, DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class ShipmentStatus(str, enum.Enum):
    pending = "pending"  # created, not yet picked up
    dispatched = "dispatched"  # driver left with order
    delivered = "delivered"  # customer received


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid6.uuid7())

    # Cross-service references — no FK constraints (separate DBs)
    order_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    status = Column(
        Enum(ShipmentStatus),
        nullable=False,
        default=ShipmentStatus.pending,
    )

    # Delivery details
    delivery_address = Column(String(500), nullable=False)
    driver_name = Column(String(200), nullable=True)
    driver_phone = Column(String(50), nullable=True)
    tracking_note = Column(Text, nullable=True)

    # Timestamps for each state transition
    dispatched_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
