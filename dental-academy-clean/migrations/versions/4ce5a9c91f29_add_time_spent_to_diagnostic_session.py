"""add_time_spent_to_diagnostic_session

Revision ID: 4ce5a9c91f29
Revises: dffdc5ac1334
Create Date: 2025-11-07 20:49:11.346558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ce5a9c91f29'
down_revision = 'dffdc5ac1334'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем колонку time_spent в таблицу diagnostic_session
    op.add_column('diagnostic_session', sa.Column('time_spent', sa.Float(), nullable=True, server_default='0.0'))


def downgrade():
    # Удаляем колонку time_spent
    op.drop_column('diagnostic_session', 'time_spent')
