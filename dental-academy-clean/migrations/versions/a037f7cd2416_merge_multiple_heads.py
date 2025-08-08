"""merge multiple heads

Revision ID: a037f7cd2416
Revises: add_confidence_level_001, add_requires_diagnostic_field, spaced_repetition_001
Create Date: 2025-08-04 12:48:36.837073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a037f7cd2416'
down_revision = ('add_confidence_level_001', 'add_requires_diagnostic_field', 'spaced_repetition_001')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
