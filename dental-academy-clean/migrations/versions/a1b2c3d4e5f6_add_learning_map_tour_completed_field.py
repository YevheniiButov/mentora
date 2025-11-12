"""Add learning_map_tour_completed field to User model

Revision ID: a1b2c3d4e5f6
Revises: dffdc5ac1334
Create Date: 2025-11-12 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'dffdc5ac1334'  # Last migration in chain after merge
branch_labels = None
depends_on = None

def upgrade():
    # Add learning_map_tour_completed field to user table
    # Default is False - tour will be shown on first visit
    op.add_column('user', sa.Column('learning_map_tour_completed', sa.Boolean(), nullable=False, server_default='false'))

def downgrade():
    # Remove learning_map_tour_completed field from user table
    op.drop_column('user', 'learning_map_tour_completed')

