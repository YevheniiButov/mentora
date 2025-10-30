"""add target_keywords and last_played_date to virtual_patient_scenario

Revision ID: fe12c7bb9c3a
Revises: e7a1c2a6b1a8
Create Date: 2025-10-30
"""

from alembic import op
import sqlalchemy as sa


revision = 'fe12c7bb9c3a'
down_revision = 'e7a1c2a6b1a8'
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    # target_keywords TEXT NULL
    if not _has_column('virtual_patient_scenario', 'target_keywords'):
        op.add_column('virtual_patient_scenario', sa.Column('target_keywords', sa.Text(), nullable=True))

    # last_played_date DATETIME NULL
    if not _has_column('virtual_patient_scenario', 'last_played_date'):
        op.add_column('virtual_patient_scenario', sa.Column('last_played_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    if _has_column('virtual_patient_scenario', 'last_played_date'):
        op.drop_column('virtual_patient_scenario', 'last_played_date')
    if _has_column('virtual_patient_scenario', 'target_keywords'):
        op.drop_column('virtual_patient_scenario', 'target_keywords')


