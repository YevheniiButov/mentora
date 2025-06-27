"""Add Dutch assessment fields and models

Revision ID: add_dutch_assessment_fields
Revises: initial_migration
Create Date: 2025-06-26 19:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_dutch_assessment_fields'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем новые поля в таблицу assessment_categories
    op.add_column('assessment_categories', sa.Column('is_dutch_specific', sa.Boolean(), nullable=True, default=False))
    op.add_column('assessment_categories', sa.Column('dutch_weight', sa.Float(), nullable=True, default=1.0))
    op.add_column('assessment_categories', sa.Column('critical_for_netherlands', sa.Boolean(), nullable=True, default=False))
    op.add_column('assessment_categories', sa.Column('name_en', sa.String(length=100), nullable=True))
    op.add_column('assessment_categories', sa.Column('name_ru', sa.String(length=100), nullable=True))
    
    # Создаем таблицу dutch_competency_levels
    op.create_table('dutch_competency_levels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('level_name', sa.String(length=20), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем таблицу dutch_assessment_results
    op.create_table('dutch_assessment_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('attempt_id', sa.Integer(), nullable=False),
        sa.Column('competency_level', sa.String(length=20), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('critical_areas_score', sa.Float(), nullable=False),
        sa.Column('can_work_supervised', sa.Boolean(), nullable=True, default=False),
        sa.Column('can_work_independently', sa.Boolean(), nullable=True, default=False),
        sa.Column('regional_focus', sa.String(length=20), nullable=True),
        sa.Column('certification_pathway', sa.Text(), nullable=True),
        sa.Column('next_steps', sa.Text(), nullable=True),
        sa.Column('category_scores', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['attempt_id'], ['pre_assessment_attempts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Удаляем таблицы
    op.drop_table('dutch_assessment_results')
    op.drop_table('dutch_competency_levels')
    
    # Удаляем колонки из assessment_categories
    op.drop_column('assessment_categories', 'name_ru')
    op.drop_column('assessment_categories', 'name_en')
    op.drop_column('assessment_categories', 'critical_for_netherlands')
    op.drop_column('assessment_categories', 'dutch_weight')
    op.drop_column('assessment_categories', 'is_dutch_specific') 