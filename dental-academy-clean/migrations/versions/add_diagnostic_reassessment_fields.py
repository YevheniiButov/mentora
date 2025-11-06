"""Add diagnostic reassessment fields to PersonalLearningPlan

Revision ID: add_diagnostic_reassessment_fields
Revises: a037f7cd2416
Create Date: 2025-01-27 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_diagnostic_reassessment_fields'
down_revision = 'a037f7cd2416'
branch_labels = None
depends_on = None

def upgrade():
    # Add diagnostic reassessment fields to personal_learning_plan table
    op.add_column('personal_learning_plan', sa.Column('next_diagnostic_date', sa.Date(), nullable=True))
    op.add_column('personal_learning_plan', sa.Column('diagnostic_reminder_sent', sa.Boolean(), nullable=False, server_default='false'))

def downgrade():
    # Remove diagnostic reassessment fields from personal_learning_plan table
    op.drop_column('personal_learning_plan', 'diagnostic_reminder_sent')
    op.drop_column('personal_learning_plan', 'next_diagnostic_date') 