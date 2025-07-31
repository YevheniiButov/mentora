"""Create BI-toets diagnostic testing models

Revision ID: big_diagnostic_001
Revises: 047438f72808
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'big_diagnostic_001'
down_revision = '047438f72808'
branch_labels = None
depends_on = None

def upgrade():
    # Create big_domain table
    op.create_table('big_domain',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('weight_percentage', sa.Float(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name')
    )
    
    # Create irt_parameters table
    op.create_table('irt_parameters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('difficulty', sa.Float(), nullable=False),
        sa.Column('discrimination', sa.Float(), nullable=False),
        sa.Column('guessing', sa.Float(), nullable=True),
        sa.Column('calibration_date', sa.DateTime(), nullable=True),
        sa.Column('calibration_sample_size', sa.Integer(), nullable=True),
        sa.Column('reliability', sa.Float(), nullable=True),
        sa.Column('se_difficulty', sa.Float(), nullable=True),
        sa.Column('se_discrimination', sa.Float(), nullable=True),
        sa.Column('se_guessing', sa.Float(), nullable=True),
        sa.Column('infit', sa.Float(), nullable=True),
        sa.Column('outfit', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['question.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('question_id')
    )
    
    # Create diagnostic_session table
    op.create_table('diagnostic_session',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_type', sa.String(length=50), nullable=False),
        sa.Column('test_length', sa.Integer(), nullable=True),
        sa.Column('time_limit', sa.Integer(), nullable=True),
        sa.Column('current_ability', sa.Float(), nullable=True),
        sa.Column('ability_se', sa.Float(), nullable=True),
        sa.Column('questions_answered', sa.Integer(), nullable=True),
        sa.Column('correct_answers', sa.Integer(), nullable=True),
        sa.Column('session_data', sa.Text(), nullable=True),
        sa.Column('ability_history', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('termination_reason', sa.String(length=50), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create diagnostic_response table
    op.create_table('diagnostic_response',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('selected_answer', sa.String(length=255), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('ability_before', sa.Float(), nullable=True),
        sa.Column('ability_after', sa.Float(), nullable=True),
        sa.Column('se_before', sa.Float(), nullable=True),
        sa.Column('se_after', sa.Float(), nullable=True),
        sa.Column('item_information', sa.Float(), nullable=True),
        sa.Column('expected_response', sa.Float(), nullable=True),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['question.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['diagnostic_session.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create personal_learning_plan table
    op.create_table('personal_learning_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('exam_date', sa.Date(), nullable=True),
        sa.Column('target_ability', sa.Float(), nullable=True),
        sa.Column('study_hours_per_week', sa.Float(), nullable=True),
        sa.Column('current_ability', sa.Float(), nullable=True),
        sa.Column('overall_progress', sa.Float(), nullable=True),
        sa.Column('estimated_readiness', sa.Float(), nullable=True),
        sa.Column('domain_analysis', sa.Text(), nullable=True),
        sa.Column('weak_domains', sa.Text(), nullable=True),
        sa.Column('strong_domains', sa.Text(), nullable=True),
        sa.Column('study_schedule', sa.Text(), nullable=True),
        sa.Column('milestones', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create study_session table
    op.create_table('study_session',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('learning_plan_id', sa.Integer(), nullable=False),
        sa.Column('session_type', sa.String(length=50), nullable=False),
        sa.Column('domain_id', sa.Integer(), nullable=True),
        sa.Column('content_ids', sa.Text(), nullable=True),
        sa.Column('questions_answered', sa.Integer(), nullable=True),
        sa.Column('correct_answers', sa.Integer(), nullable=True),
        sa.Column('planned_duration', sa.Integer(), nullable=True),
        sa.Column('actual_duration', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('progress_percent', sa.Float(), nullable=True),
        sa.Column('difficulty_level', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['domain_id'], ['big_domain.id'], ),
        sa.ForeignKeyConstraint(['learning_plan_id'], ['personal_learning_plan.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add new columns to existing question table
    op.add_column('question', sa.Column('big_domain_id', sa.Integer(), nullable=True))
    op.add_column('question', sa.Column('difficulty_level', sa.Integer(), nullable=True))
    op.add_column('question', sa.Column('question_type', sa.String(length=50), nullable=True))
    op.add_column('question', sa.Column('clinical_context', sa.Text(), nullable=True))
    op.add_column('question', sa.Column('learning_objectives', sa.Text(), nullable=True))
    op.add_column('question', sa.Column('tags', sa.Text(), nullable=True))
    
    # Add new columns to existing test table
    op.add_column('test', sa.Column('test_format', sa.String(length=50), nullable=True))
    op.add_column('test', sa.Column('irt_enabled', sa.Boolean(), nullable=True))
    op.add_column('test', sa.Column('min_questions', sa.Integer(), nullable=True))
    op.add_column('test', sa.Column('max_questions', sa.Integer(), nullable=True))
    op.add_column('test', sa.Column('precision_threshold', sa.Float(), nullable=True))
    op.add_column('test', sa.Column('passing_score', sa.Float(), nullable=True))
    
    # Add new columns to existing test_attempt table
    op.add_column('test_attempt', sa.Column('ability_estimate', sa.Float(), nullable=True))
    op.add_column('test_attempt', sa.Column('ability_se', sa.Float(), nullable=True))
    op.add_column('test_attempt', sa.Column('response_time', sa.Float(), nullable=True))
    op.add_column('test_attempt', sa.Column('difficulty_rating', sa.Integer(), nullable=True))
    
    # Create indexes
    op.create_index(op.f('ix_question_big_domain_id'), 'question', ['big_domain_id'], unique=False)
    op.create_index(op.f('ix_diagnostic_session_user_id'), 'diagnostic_session', ['user_id'], unique=False)
    op.create_index(op.f('ix_diagnostic_response_session_id'), 'diagnostic_response', ['session_id'], unique=False)
    op.create_index(op.f('ix_personal_learning_plan_user_id'), 'personal_learning_plan', ['user_id'], unique=False)
    op.create_index(op.f('ix_study_session_learning_plan_id'), 'study_session', ['learning_plan_id'], unique=False)

def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_study_session_learning_plan_id'), table_name='study_session')
    op.drop_index(op.f('ix_personal_learning_plan_user_id'), table_name='personal_learning_plan')
    op.drop_index(op.f('ix_diagnostic_response_session_id'), table_name='diagnostic_response')
    op.drop_index(op.f('ix_diagnostic_session_user_id'), table_name='diagnostic_session')
    op.drop_index(op.f('ix_question_big_domain_id'), table_name='question')
    
    # Drop new columns from existing tables
    op.drop_column('test_attempt', 'difficulty_rating')
    op.drop_column('test_attempt', 'response_time')
    op.drop_column('test_attempt', 'ability_se')
    op.drop_column('test_attempt', 'ability_estimate')
    
    op.drop_column('test', 'passing_score')
    op.drop_column('test', 'precision_threshold')
    op.drop_column('test', 'max_questions')
    op.drop_column('test', 'min_questions')
    op.drop_column('test', 'irt_enabled')
    op.drop_column('test', 'test_format')
    
    op.drop_column('question', 'tags')
    op.drop_column('question', 'learning_objectives')
    op.drop_column('question', 'clinical_context')
    op.drop_column('question', 'question_type')
    op.drop_column('question', 'difficulty_level')
    op.drop_column('question', 'big_domain_id')
    
    # Drop new tables
    op.drop_table('study_session')
    op.drop_table('personal_learning_plan')
    op.drop_table('diagnostic_response')
    op.drop_table('diagnostic_session')
    op.drop_table('irt_parameters')
    op.drop_table('big_domain') 