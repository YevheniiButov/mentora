"""Add profile_public field to user table

Revision ID: add_profile_public
Revises: ab7d2a4f0c1d
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_profile_public'
down_revision = 'add_other_study_country_001'
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    """Check if column exists in table"""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    """Add profile_public column to user table"""
    # Add profile_public column if it doesn't exist
    if not _has_column('user', 'profile_public'):
        op.add_column('user', sa.Column('profile_public', sa.Boolean(), server_default='1', nullable=False))
        print("✅ Added profile_public column to user table")
    else:
        print("⚠️ Column profile_public already exists, skipping")


def downgrade():
    """Remove profile_public column from user table"""
    # Remove profile_public column if it exists
    if _has_column('user', 'profile_public'):
        op.drop_column('user', 'profile_public')
        print("✅ Removed profile_public column from user table")
    else:
        print("⚠️ Column profile_public doesn't exist, skipping")

