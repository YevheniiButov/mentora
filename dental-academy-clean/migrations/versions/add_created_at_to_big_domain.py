"""Add created_at column to big_domain table

Revision ID: add_created_at_big_domain
Revises: fb47982ff101
Create Date: 2025-01-20 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'add_created_at_big_domain'
down_revision = 'fb47982ff101'
branch_labels = None
depends_on = None

def upgrade():
    """Add created_at column to big_domain table"""
    
    # Add created_at column
    op.add_column('big_domain', sa.Column('created_at', sa.DateTime(), nullable=True))
    
    # Set default value for existing records
    op.execute("UPDATE big_domain SET created_at = datetime('now') WHERE created_at IS NULL")
    
    # Note: SQLite doesn't support ALTER COLUMN, so we'll leave it nullable
    # The model will handle the default value

def downgrade():
    """Remove created_at column from big_domain table"""
    op.drop_column('big_domain', 'created_at') 