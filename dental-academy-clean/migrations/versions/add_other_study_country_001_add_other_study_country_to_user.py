"""Add other_study_country field to User model

Revision ID: add_other_study_country_001
Revises: ab7d2a4f0c1d
Create Date: 2025-10-31
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_other_study_country_001'
down_revision = 'ab7d2a4f0c1d'
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    """Check if column exists in table"""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    # Add other_study_country column if it doesn't exist
    if not _has_column('user', 'other_study_country'):
        op.add_column('user', sa.Column('other_study_country', sa.String(length=100), nullable=True))


def downgrade():
    # Remove other_study_country column if it exists
    if _has_column('user', 'other_study_country'):
        op.drop_column('user', 'other_study_country')

