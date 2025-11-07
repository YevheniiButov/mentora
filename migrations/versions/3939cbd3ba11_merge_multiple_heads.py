"""Merge multiple heads

Revision ID: 3939cbd3ba11
Revises: 2ff97374f815, 99228e12c0b3, big_diagnostic_001
Create Date: 2025-07-18 14:54:26.838179

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3939cbd3ba11'
down_revision = ('2ff97374f815', '99228e12c0b3', 'big_diagnostic_001')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
