"""Merge migration heads

Revision ID: 8b3e52d9ccbb
Revises: 685ba377cd47, a1b2c3d4e5f6
Create Date: 2025-11-13 13:53:27.213315

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b3e52d9ccbb'
down_revision = ('685ba377cd47', 'a1b2c3d4e5f6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
