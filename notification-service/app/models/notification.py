import uuid6
import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class NotificationType(str, enum.Enum):
    payment_succeeded  = "payment_succeeded"
    payment_failed     = "payment_failed"
    shipment_dispatched = "shipment_dispatched"
    shipment_delivered = "shipment_delivered"


class Notification(Base):
    """
    Audit log of every email notification sent (or attempted).
    Useful for debugging, customer service ("did they get the email?"),
    and idempotency checks (don't send the same notification twice).
    """
    __tablename__ = "notifications"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid6.uuid7())
    order_id         = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id          = Column(UUID(as_uuid=True), nullable=False, index=True)
    to_email         = Column(String(255), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    subject          = Column(String(500), nullable=False)
    sent             = Column(Boolean, nullable=False, default=False)
    error_message    = Column(Text, nullable=True)
    created_at       = Column(DateTime, default=func.now())
