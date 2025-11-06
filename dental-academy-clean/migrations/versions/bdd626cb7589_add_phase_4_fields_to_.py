"""Add Phase 4 fields to PersonalLearningPlan

Revision ID: bdd626cb7589
Revises: 6f9d1b7e7392
Create Date: 2025-10-25 00:29:23.965230

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdd626cb7589'
down_revision = '6f9d1b7e7392'
branch_labels = None
depends_on = None


def upgrade():
    # === NEW FIELDS FOR PHASE 4 ===
    
    # Spaced Repetition Integration
    op.add_column('personal_learning_plan', sa.Column('spaced_repetition_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('personal_learning_plan', sa.Column('sr_algorithm', sa.String(length=20), nullable=True, default='sm2'))
    op.add_column('personal_learning_plan', sa.Column('next_review_date', sa.Date(), nullable=True))
    op.add_column('personal_learning_plan', sa.Column('sr_streak', sa.Integer(), nullable=True, default=0))
    op.add_column('personal_learning_plan', sa.Column('total_sr_reviews', sa.Integer(), nullable=True, default=0))
    
    # Domain Category Integration (from Phase 3)
    op.add_column('personal_learning_plan', sa.Column('category_progress', sa.Text(), nullable=True))
    op.add_column('personal_learning_plan', sa.Column('weak_categories', sa.Text(), nullable=True))
    op.add_column('personal_learning_plan', sa.Column('strong_categories', sa.Text(), nullable=True))
    op.add_column('personal_learning_plan', sa.Column('current_category_focus', sa.Integer(), nullable=True))
    
    # Daily Tasks and Goals
    op.add_column('personal_learning_plan', sa.Column('daily_question_goal', sa.Integer(), nullable=True, default=20))
    op.add_column('personal_learning_plan', sa.Column('daily_time_goal', sa.Integer(), nullable=True, default=30))
    op.add_column('personal_learning_plan', sa.Column('daily_streak', sa.Integer(), nullable=True, default=0))
    op.add_column('personal_learning_plan', sa.Column('longest_daily_streak', sa.Integer(), nullable=True, default=0))
    op.add_column('personal_learning_plan', sa.Column('last_activity_date', sa.Date(), nullable=True))
    op.add_column('personal_learning_plan', sa.Column('daily_goal_met_count', sa.Integer(), nullable=True, default=0))
    
    # Enhanced Progress Tracking
    op.add_column('personal_learning_plan', sa.Column('category_abilities', sa.Text(), nullable=True))
    op.add_column('personal_learning_plan', sa.Column('learning_velocity', sa.Float(), nullable=True))
    op.add_column('personal_learning_plan', sa.Column('retention_rate', sa.Float(), nullable=True))
    op.add_column('personal_learning_plan', sa.Column('time_invested', sa.Integer(), nullable=True, default=0))


def downgrade():
    # Remove Phase 4 fields
    op.drop_column('personal_learning_plan', 'time_invested')
    op.drop_column('personal_learning_plan', 'retention_rate')
    op.drop_column('personal_learning_plan', 'learning_velocity')
    op.drop_column('personal_learning_plan', 'category_abilities')
    op.drop_column('personal_learning_plan', 'daily_goal_met_count')
    op.drop_column('personal_learning_plan', 'last_activity_date')
    op.drop_column('personal_learning_plan', 'longest_daily_streak')
    op.drop_column('personal_learning_plan', 'daily_streak')
    op.drop_column('personal_learning_plan', 'daily_time_goal')
    op.drop_column('personal_learning_plan', 'daily_question_goal')
    op.drop_column('personal_learning_plan', 'current_category_focus')
    op.drop_column('personal_learning_plan', 'strong_categories')
    op.drop_column('personal_learning_plan', 'weak_categories')
    op.drop_column('personal_learning_plan', 'category_progress')
    op.drop_column('personal_learning_plan', 'total_sr_reviews')
    op.drop_column('personal_learning_plan', 'sr_streak')
    op.drop_column('personal_learning_plan', 'next_review_date')
    op.drop_column('personal_learning_plan', 'sr_algorithm')
    op.drop_column('personal_learning_plan', 'spaced_repetition_enabled')
