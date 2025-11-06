"""add fill_in fields to virtual_patient_attempt

Revision ID: ab7d2a4f0c1d
Revises: fe12c7bb9c3a
Create Date: 2025-10-30
"""

from alembic import op
import sqlalchemy as sa


revision = 'ab7d2a4f0c1d'
down_revision = 'fe12c7bb9c3a'
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    if not _has_column('virtual_patient_attempt', 'fill_in_answers'):
        op.add_column('virtual_patient_attempt', sa.Column('fill_in_answers', sa.Text(), nullable=True))
    if not _has_column('virtual_patient_attempt', 'fill_in_score'):
        op.add_column('virtual_patient_attempt', sa.Column('fill_in_score', sa.Integer(), nullable=True))


def downgrade() -> None:
    if _has_column('virtual_patient_attempt', 'fill_in_score'):
        op.drop_column('virtual_patient_attempt', 'fill_in_score')
    if _has_column('virtual_patient_attempt', 'fill_in_answers'):
        op.drop_column('virtual_patient_attempt', 'fill_in_answers')


