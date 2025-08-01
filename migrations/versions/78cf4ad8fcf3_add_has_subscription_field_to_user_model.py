"""Add has_subscription field to User model

Revision ID: 78cf4ad8fcf3
Revises: 246641da327c
Create Date: 2025-07-07 21:51:55.628814

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78cf4ad8fcf3'
down_revision = '246641da327c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('has_subscription', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('has_subscription')

    # ### end Alembic commands ###
