"""add specialty columns to user and virtual_patient_scenario

Revision ID: e7a1c2a6b1a8
Revises: f22ecb06fc04
Create Date: 2025-10-30
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7a1c2a6b1a8'
down_revision = 'f22ecb06fc04'
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    # user.specialty
    if not _has_column('user', 'specialty'):
        op.add_column('user', sa.Column('specialty', sa.String(length=255), nullable=True))

    # virtual_patient_scenario.specialty
    if not _has_column('virtual_patient_scenario', 'specialty'):
        op.add_column(
            'virtual_patient_scenario',
            sa.Column('specialty', sa.String(length=255), nullable=True),
        )


def downgrade() -> None:
    # virtual_patient_scenario.specialty
    if _has_column('virtual_patient_scenario', 'specialty'):
        op.drop_column('virtual_patient_scenario', 'specialty')

    # user.specialty
    if _has_column('user', 'specialty'):
        op.drop_column('user', 'specialty')


