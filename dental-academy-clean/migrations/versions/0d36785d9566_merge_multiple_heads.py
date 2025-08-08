"""Merge multiple heads

Revision ID: 0d36785d9566
Revises: 5a4e86d1603e, add_diagnostic_reassessment_fields, add_difficulty_to_lesson
Create Date: 2025-08-05 01:32:17.606425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d36785d9566'
down_revision = ('5a4e86d1603e', 'add_diagnostic_reassessment_fields', 'add_difficulty_to_lesson')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
