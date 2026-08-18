"""add awaiting_confirmation to orderstatus enum

Revision ID: ord002
Revises: ord001
Create Date: 2026-08-17 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'ord002'
down_revision: Union[str, None] = 'o2p3q4r5s6t7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL requires ALTER TYPE to add enum values
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'awaiting_confirmation'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values without recreating the type
    # Leave this as a no-op — removing enum values in production is risky
    pass
