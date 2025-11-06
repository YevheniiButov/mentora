"""Add membership fields to User model - SAFE VERSION

Revision ID: safe_membership_fields
Revises: 496c010bf6c2
Create Date: 2025-10-02 10:00:00.000000

SAFE MIGRATION - Only adds new columns, no data loss
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'safe_membership_fields'
down_revision = '496c010bf6c2'
branch_labels = None
depends_on = None

def upgrade():
    """Safely add membership fields to user table"""
    
    # Step 1: Add columns with NULL allowed (safe for existing data)
    with op.batch_alter_table('user', schema=None) as batch_op:
        # Add membership_type with default 'free' for new users only
        batch_op.add_column(sa.Column('membership_type', sa.String(length=20), nullable=True))
        
        # Add other fields as nullable (existing users won't be affected)
        batch_op.add_column(sa.Column('membership_expires', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('member_id', sa.String(length=12), nullable=True))
        batch_op.add_column(sa.Column('qr_code_path', sa.String(length=200), nullable=True))
    
    # Step 2: Set default values for existing users (preserve all data)
    op.execute("""
        UPDATE "user" 
        SET membership_type = 'free' 
        WHERE membership_type IS NULL
    """)
    
    # Step 3: Make membership_type NOT NULL after setting defaults
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('membership_type', nullable=False)
    
    # Step 4: Create index (safe operation)
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index('ix_user_member_id', ['member_id'], unique=True)

def downgrade():
    """Safely remove membership fields"""
    with op.batch_alter_table('user', schema=None) as batch_op:
        # Drop index first
        batch_op.drop_index('ix_user_member_id')
        
        # Drop columns (existing user data remains intact)
        batch_op.drop_column('qr_code_path')
        batch_op.drop_column('member_id')
        batch_op.drop_column('membership_expires')
        batch_op.drop_column('membership_type')
