"""Merge multiple heads

Revision ID: 616149fd23c7
Revises: add_new_big_domains_complete, cf4b399693db
Create Date: 2025-07-22 22:18:22.314327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '616149fd23c7'
down_revision = ('add_new_big_domains_complete', 'cf4b399693db')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
