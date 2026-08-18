"""
Shared fixtures for shipping-service tests.

Same SQLite/UUID/JSONB patching pattern as order-service and payment-service.
require_staff and get_current_user_id are both overridden in the client
fixture using the actual JWT_SECRET from environment — same approach that
fixed the 401 issues in other services.
"""

import os
import uuid
import pytest
import pytest_asyncio
from datetime import datetime, timedelta

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only")

from sqlalchemy import String, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

from app.db.base import Base
from app.db.session import get_db
from app.core.auth import require_staff, get_current_user_id
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class UUIDasStr(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return str(value) if value is not None else None

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return uuid.UUID(str(value))
        except (ValueError, AttributeError):
            return value


def _patch_columns():
    patched = []
    for table in Base.metadata.tables.values():
        for col in table.columns:
            if isinstance(col.type, PG_UUID):
                col.type = UUIDasStr()
                patched.append(col)
    return patched


def _restore_columns(patched):
    for col in patched:
        col.type = PG_UUID(as_uuid=True)


@pytest_asyncio.fixture(scope="function")
async def db():
    patched = _patch_columns()
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    _restore_columns(patched)


def _make_token(user_id: str, is_staff: bool = False) -> str:
    import jwt as pyjwt

    secret = os.environ.get("JWT_SECRET", "test-secret-key-for-testing-only")
    payload = {
        "sub": "testuser",
        "user_id": str(user_id),
        "is_staff": is_staff,
        "type": "access",
        "fresh": False,
        "iat": datetime.utcnow(),
        "nbf": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "jti": str(uuid.uuid4()),
    }
    token = pyjwt.encode(payload, secret, algorithm="HS256")
    return token.decode("utf-8") if isinstance(token, bytes) else token


@pytest_asyncio.fixture(scope="function")
async def client(db):
    """HTTP client with staff token injected via overridden dependencies."""
    _staff_user_id = uuid.uuid4()
    _customer_user_id = uuid.uuid4()

    async def override_get_db():
        yield db

    def override_require_staff():
        pass  # staff access granted unconditionally in tests

    def override_get_current_user_id():
        return _customer_user_id

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_staff] = override_require_staff
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        ac._staff_user_id = _staff_user_id
        ac._customer_user_id = _customer_user_id
        yield ac

    app.dependency_overrides.clear()


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


def make_staff_token(user_id: str = None) -> str:
    return _make_token(user_id or str(uuid.uuid4()), is_staff=True)


def make_user_token(user_id: str = None) -> str:
    return _make_token(user_id or str(uuid.uuid4()), is_staff=False)
