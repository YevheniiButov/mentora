"""create_user_item_mastery_table

Revision ID: 685ba377cd47
Revises: 4ce5a9c91f29
Create Date: 2025-11-07 21:48:22.166290

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '685ba377cd47'
down_revision = '4ce5a9c91f29'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(sa.text("DROP TABLE IF EXISTS user_item_mastery"))
    op.create_table(
        'user_item_mastery',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('item_type', sa.String(length=32), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('total_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_correct', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('consecutive_correct_sessions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_result', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('last_session_reference', sa.String(length=64), nullable=True),
        sa.Column('last_session_date', sa.Date(), nullable=True),
        sa.Column('last_attempt_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_correct_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('mastered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'item_type', 'item_id', name='uq_user_item_mastery')
    )
    op.create_index('ix_user_item_mastery_user_id', 'user_item_mastery', ['user_id'])
    op.create_index('ix_user_item_mastery_item_type', 'user_item_mastery', ['item_type'])


def downgrade():
    op.drop_index('ix_user_item_mastery_item_type', table_name='user_item_mastery')
    op.drop_index('ix_user_item_mastery_user_id', table_name='user_item_mastery')
    op.drop_table('user_item_mastery')
