"""Add membership fields to User model

Revision ID: clean_membership_fields
Revises: 496c010bf6c2
Create Date: 2025-10-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'clean_membership_fields'
down_revision = '496c010bf6c2'
branch_labels = None
depends_on = None

def upgrade():
    """Add membership fields to user table"""
    # Add membership fields to user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('membership_type', sa.String(length=20), nullable=True, default='free'))
        batch_op.add_column(sa.Column('membership_expires', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('member_id', sa.String(length=12), nullable=True))
        batch_op.add_column(sa.Column('qr_code_path', sa.String(length=200), nullable=True))
        
        # Create index for member_id
        batch_op.create_index('ix_user_member_id', ['member_id'], unique=True)
    
    # Set default values for existing users
    op.execute("UPDATE user SET membership_type = 'free' WHERE membership_type IS NULL")

def downgrade():
    """Remove membership fields from user table"""
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('ix_user_member_id')
        batch_op.drop_column('qr_code_path')
        batch_op.drop_column('member_id')
        batch_op.drop_column('membership_expires')
        batch_op.drop_column('membership_type')
