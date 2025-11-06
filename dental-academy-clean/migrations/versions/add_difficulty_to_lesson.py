"""Add difficulty field to Lesson model

Revision ID: add_difficulty_to_lesson
Revises: 047438f72808
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_difficulty_to_lesson'
down_revision = '047438f72808'
branch_labels = None
depends_on = None

def upgrade():
    # Add difficulty column to lessons table
    op.add_column('lessons', sa.Column('difficulty', sa.Float(), nullable=True, default=0.0))
    
    # Create index for better performance
    op.create_index(op.f('ix_lessons_difficulty'), 'lessons', ['difficulty'], unique=False)

def downgrade():
    # Remove index
    op.drop_index(op.f('ix_lessons_difficulty'), table_name='lessons')
    
    # Remove difficulty column
    op.drop_column('lessons', 'difficulty') 