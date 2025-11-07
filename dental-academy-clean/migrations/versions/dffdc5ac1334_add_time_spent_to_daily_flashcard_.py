"""add_time_spent_to_daily_flashcard_progress

Revision ID: dffdc5ac1334
Revises: 1762253286
Create Date: 2025-11-07 15:43:35.808367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dffdc5ac1334'
down_revision = '1762253286'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем поле time_spent в таблицу daily_flashcard_progress
    op.add_column('daily_flashcard_progress', sa.Column('time_spent', sa.Float(), nullable=True, server_default='0.0'))


def downgrade():
    # Удаляем поле time_spent
    op.drop_column('daily_flashcard_progress', 'time_spent')
