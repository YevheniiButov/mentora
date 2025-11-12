"""Merge all migration heads

Revision ID: merge_all_heads_202511120333
Revises: 23f09af28990, 2ff97374f815, 34a1e08591b4, 5a4e86d1603e, 5acb6d9128f0... (25 total)
Create Date: 2025-11-12 03:34:08.057205

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_all_heads_202511120333'
down_revision = ('23f09af28990', '2ff97374f815', '34a1e08591b4', '5a4e86d1603e', '5acb6d9128f0', '616149fd23c7', '685ba377cd47', '86d6846076f9', '8b2f6eda6f2e', '99228e12c0b3', 'a1b2c3d4e5f6', 'add_confidence_level_001', 'add_diagnostic_reassessment_fields', 'add_difficulty_to_lesson', 'add_new_big_domains_complete', 'add_profession_question_001', 'add_requires_diagnostic_field', 'bdd626cb7589', 'big_diagnostic_001', 'cf4b399693db', 'clean_membership_fields', 'merge_all_heads_202511120333', 'remove_irt_duplication', 'safe_membership_fields', 'spaced_repetition_001')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
