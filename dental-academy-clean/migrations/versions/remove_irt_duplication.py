"""Remove IRT parameter duplication

Revision ID: remove_irt_duplication
Revises: 047438f72808
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'remove_irt_duplication'
down_revision = '047438f72808'
branch_labels = None
depends_on = None

def upgrade():
    """Upgrade: Remove IRT parameters from Question model"""
    
    # Step 1: Create IRTParameters records for all questions that don't have them
    op.execute("""
        INSERT INTO irt_parameters (question_id, difficulty, discrimination, guessing, calibration_date)
        SELECT 
            q.id as question_id,
            q.irt_difficulty as difficulty,
            q.irt_discrimination as discrimination,
            q.irt_guessing as guessing,
            datetime('now') as calibration_date
        FROM questions q
        LEFT JOIN irt_parameters irt ON q.id = irt.question_id
        WHERE irt.question_id IS NULL
    """)
    
    # Step 2: Remove IRT columns from questions table
    op.drop_column('questions', 'irt_difficulty')
    op.drop_column('questions', 'irt_discrimination')
    op.drop_column('questions', 'irt_guessing')

def downgrade():
    """Downgrade: Restore IRT parameters to Question model"""
    
    # Step 1: Add IRT columns back to questions table
    op.add_column('questions', sa.Column('irt_difficulty', sa.Float(), nullable=True))
    op.add_column('questions', sa.Column('irt_discrimination', sa.Float(), nullable=True))
    op.add_column('questions', sa.Column('irt_guessing', sa.Float(), nullable=True))
    
    # Step 2: Copy data back from irt_parameters
    op.execute("""
        UPDATE questions q
        JOIN irt_parameters irt ON q.id = irt.question_id
        SET 
            q.irt_difficulty = irt.difficulty,
            q.irt_discrimination = irt.discrimination,
            q.irt_guessing = irt.guessing
    """)
    
    # Step 3: Make columns not nullable
    op.alter_column('questions', 'irt_difficulty', nullable=False)
    op.alter_column('questions', 'irt_discrimination', nullable=False)
    op.alter_column('questions', 'irt_guessing', nullable=False) 