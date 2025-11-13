"""Add SystemEvent model for monitoring

Revision ID: 99423f8b195c
Revises: 8b3e52d9ccbb
Create Date: 2025-11-13 13:54:03.955767

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99423f8b195c'
down_revision = '8b3e52d9ccbb'
branch_labels = None
depends_on = None


def upgrade():
    # Create system_events table for monitoring
    op.create_table('system_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_email', sa.String(length=120), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('request_url', sa.String(length=500), nullable=True),
        sa.Column('request_method', sa.String(length=10), nullable=True),
        sa.Column('error_traceback', sa.Text(), nullable=True),
        sa.Column('event_metadata', sa.Text(), nullable=True),
        sa.Column('email_sent', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('email_sent_at', sa.DateTime(), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['resolved_by'], ['user.id'], name='fk_system_events_resolved_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_system_events_user_id', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_events_created_at'), 'system_events', ['created_at'], unique=False)
    op.create_index(op.f('ix_system_events_event_type'), 'system_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_system_events_severity'), 'system_events', ['severity'], unique=False)
    op.create_index(op.f('ix_system_events_user_email'), 'system_events', ['user_email'], unique=False)
    op.create_index(op.f('ix_system_events_user_id'), 'system_events', ['user_id'], unique=False)


def downgrade():
    # Drop system_events table
    op.drop_index(op.f('ix_system_events_user_id'), table_name='system_events')
    op.drop_index(op.f('ix_system_events_user_email'), table_name='system_events')
    op.drop_index(op.f('ix_system_events_severity'), table_name='system_events')
    op.drop_index(op.f('ix_system_events_event_type'), table_name='system_events')
    op.drop_index(op.f('ix_system_events_created_at'), table_name='system_events')
    op.drop_table('system_events')
