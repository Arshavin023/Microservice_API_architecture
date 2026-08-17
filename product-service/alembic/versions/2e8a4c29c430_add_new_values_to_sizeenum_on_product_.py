"""add new values to sizeenum on product_variants and add description column to categories

Revision ID: 2e8a4c29c430
Revises: 'p1q2r3s4t5u6'
Create Date: 2026-08-17 00:27:12.726740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e8a4c29c430'
down_revision: Union[str, None] = 'p1q2r3s4t5u6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE sizeenum ADD VALUE IF NOT EXISTS 'portion'")
    op.execute("ALTER TYPE sizeenum ADD VALUE IF NOT EXISTS 'regular'")
    op.execute("ALTER TYPE sizeenum ADD VALUE IF NOT EXISTS 'half'")
    op.execute("ALTER TYPE sizeenum ADD VALUE IF NOT EXISTS 'full'")
    op.add_column('categories', sa.Column('description', sa.String(length=500), nullable=True))


def downgrade() -> None:
    pass