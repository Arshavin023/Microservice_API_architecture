"""init notifications table

Revision ID: notif001
Revises:
Create Date: 2026-07-02 11:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'notif001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    notif_type = postgresql.ENUM(
        'payment_succeeded', 'payment_failed',
        'shipment_dispatched', 'shipment_delivered',
        name='notificationtype'
    )
    notif_type.create(op.get_bind())

    op.create_table(
        'notifications',
        sa.Column('id',                postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id',          postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id',           postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('to_email',          sa.String(255), nullable=False),
        sa.Column('notification_type', postgresql.ENUM(
            'payment_succeeded', 'payment_failed',
            'shipment_dispatched', 'shipment_delivered',
            name='notificationtype', create_type=False), nullable=False),
        sa.Column('subject',           sa.String(500), nullable=False),
        sa.Column('sent',              sa.Boolean(),   nullable=False),
        sa.Column('error_message',     sa.Text(),      nullable=True),
        sa.Column('created_at',        sa.DateTime(),  nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_notifications_order_id', 'notifications', ['order_id'])
    op.create_index('ix_notifications_user_id',  'notifications', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_notifications_user_id',  'notifications')
    op.drop_index('ix_notifications_order_id', 'notifications')
    op.drop_table('notifications')
    op.execute('DROP TYPE notificationtype')
