"""merge_multiple_heads_before_restructure

Revision ID: 63cc688d32c8
Revises: 34a1e08591b4, 616149fd23c7, remove_irt_duplication
Create Date: 2025-07-28 22:31:57.817082

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63cc688d32c8'
down_revision = ('34a1e08591b4', '616149fd23c7', 'remove_irt_duplication')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
