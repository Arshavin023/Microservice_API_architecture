"""init shipments table

Revision ID: ship001
Revises:
Create Date: 2026-07-02 10:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'ship001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    shipment_status = postgresql.ENUM(
        'pending', 'dispatched', 'delivered',
        name='shipmentstatus'
    )
    shipment_status.create(op.get_bind())

    op.create_table(
        'shipments',
        sa.Column('id',               postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id',         postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id',          postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status',           postgresql.ENUM(
                                        'pending', 'dispatched', 'delivered',
                                        name='shipmentstatus', create_type=False),
                                      nullable=False),
        sa.Column('delivery_address', sa.String(500),  nullable=False),
        sa.Column('driver_name',      sa.String(200),  nullable=True),
        sa.Column('driver_phone',     sa.String(50),   nullable=True),
        sa.Column('tracking_note',    sa.Text(),        nullable=True),
        sa.Column('dispatched_at',    sa.DateTime(),    nullable=True),
        sa.Column('delivered_at',     sa.DateTime(),    nullable=True),
        sa.Column('created_at',       sa.DateTime(),    nullable=True),
        sa.Column('updated_at',       sa.DateTime(),    nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id'),
    )
    op.create_index('ix_shipments_order_id', 'shipments', ['order_id'])
    op.create_index('ix_shipments_user_id',  'shipments', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_shipments_user_id',  'shipments')
    op.drop_index('ix_shipments_order_id', 'shipments')
    op.drop_table('shipments')
    op.execute('DROP TYPE shipmentstatus')
