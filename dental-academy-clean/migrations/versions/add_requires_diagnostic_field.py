"""Add requires_diagnostic field to User model

Revision ID: add_requires_diagnostic_field
Revises: 047438f72808
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_requires_diagnostic_field'
down_revision = '047438f72808'
branch_labels = None
depends_on = None

def upgrade():
    # Add requires_diagnostic field to user table
    op.add_column('user', sa.Column('requires_diagnostic', sa.Boolean(), nullable=False, server_default='true'))

def downgrade():
    # Remove requires_diagnostic field from user table
    op.drop_column('user', 'requires_diagnostic') 