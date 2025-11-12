"""Add learning_map_tour_completed field to User model

Revision ID: add_learning_map_tour_completed
Revises: 
Create Date: 2025-11-12 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_learning_map_tour_completed'
down_revision = 'bdd626cb7589'  # Latest migration
branch_labels = None
depends_on = None

def upgrade():
    # Add learning_map_tour_completed field to user table
    # Default is False - tour will be shown on first visit
    op.add_column('user', sa.Column('learning_map_tour_completed', sa.Boolean(), nullable=False, server_default='false'))

def downgrade():
    # Remove learning_map_tour_completed field from user table
    op.drop_column('user', 'learning_map_tour_completed')

