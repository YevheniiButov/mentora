"""Add profile redesign fields simplified

Revision ID: df528c6ddffd
Revises: 99423f8b195c
Create Date: 2026-03-16 22:05:42.067023

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df528c6ddffd'
down_revision = '99423f8b195c'
branch_labels = None
depends_on = None


def upgrade():
    # Only add columns to 'user' table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('city', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('num_children', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('housing_needed', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('work_as_assistant', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('big_commitment', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('diploma_status', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('transcript_status', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('vog_status', sa.String(length=50), nullable=True))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('vog_status')
        batch_op.drop_column('transcript_status')
        batch_op.drop_column('diploma_status')
        batch_op.drop_column('big_commitment')
        batch_op.drop_column('work_as_assistant')
        batch_op.drop_column('housing_needed')
        batch_op.drop_column('num_children')
        batch_op.drop_column('city')
