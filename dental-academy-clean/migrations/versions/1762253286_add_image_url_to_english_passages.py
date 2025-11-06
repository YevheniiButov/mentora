"""add image_url to english_passages

Revision ID: 1762253286
Revises: 
Create Date: 2024-12-XX

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1762253286'
down_revision = 'eadf0bc80aff'  # After daily_assignments migration
branch_labels = None
depends_on = None


def upgrade():
    # Add image_url column to english_passages table
    # Используем прямой SQL для проверки существования колонки
    from sqlalchemy import inspect, text
    
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('english_passages')]
    
    if 'image_url' not in columns:
        op.add_column('english_passages', 
            sa.Column('image_url', sa.String(length=500), nullable=True)
        )
    else:
        # Колонка уже существует, ничего не делаем
        pass


def downgrade():
    # Remove image_url column
    try:
        op.drop_column('english_passages', 'image_url')
    except Exception as e:
        print(f"Note: Could not remove image_url column: {e}")

