import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://...")

# 1. Define arguments that are perfectly safe for BOTH SQLite and PostgreSQL
engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# 2. Append pooling parameters ONLY if we are connecting to a PostgreSQL instance
if DATABASE_URL.startswith("postgresql"):
    engine_kwargs.update({"pool_size": 10, "max_overflow": 20})

# 3. Unpack all appropriate arguments into the factory function
engine = create_async_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) # type: ignore[call-overload]


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
