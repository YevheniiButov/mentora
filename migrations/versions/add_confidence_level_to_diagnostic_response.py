"""add_confidence_level_to_diagnostic_response

Revision ID: add_confidence_level_001
Revises: 047438f72808
Create Date: 2025-07-30 15:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_confidence_level_001'
down_revision = '047438f72808'
branch_labels = None
depends_on = None


def upgrade():
    # Add confidence_level column to diagnostic_response table
    op.add_column('diagnostic_response', sa.Column('confidence_level', sa.Integer(), nullable=True))


def downgrade():
    # Remove confidence_level column from diagnostic_response table
    op.drop_column('diagnostic_response', 'confidence_level') 