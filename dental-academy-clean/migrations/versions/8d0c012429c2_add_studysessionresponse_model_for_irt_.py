"""Add StudySessionResponse model for IRT feedback

Revision ID: 8d0c012429c2
Revises: a712e229aab8
Create Date: 2025-08-06 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d0c012429c2'
down_revision = 'a712e229aab8'
branch_labels = None
depends_on = None


def upgrade():
    # Create study_session_response table
    op.create_table('study_session_response',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('response_time', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['study_session.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop study_session_response table
    op.drop_table('study_session_response')
