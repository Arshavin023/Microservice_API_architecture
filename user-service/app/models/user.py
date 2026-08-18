import uuid6
from sqlalchemy import Column, String, Boolean, DateTime, func, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid6.uuid7())

    # The auth-service user this profile belongs to. UNIQUE is what
    # makes the RabbitMQ consumer idempotent — a duplicate
    # user.registered event for the same user_id hits this constraint
    # and fails cleanly, instead of creating a second profile row.
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)

    email = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False)

    full_name = Column(String(150), nullable=True)
    phone = Column(String(20), nullable=True)
    delivery_address = Column(String(255), nullable=True)

    dietary_preferences = Column(JSON, nullable=True)
    favorite_order = Column(JSON, nullable=True)
    notification_settings = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
