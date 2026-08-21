"""add disputed to orderstatus enum

Revision ID: ord003
Revises: ord002
Create Date: 2026-08-21
"""
from typing import Sequence, Union
from alembic import op

revision: str = 'ord003'
down_revision: Union[str, None] = 'ord002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'disputed'")

def downgrade() -> None:
    pass
