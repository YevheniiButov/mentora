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
    # Используем прямой SQL для проверки существования колонки (избегаем проблем с транзакциями)
    from sqlalchemy import text
    
    conn = op.get_bind()
    
    # Проверяем существование колонки через raw SQL
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'english_passages' 
        AND column_name = 'image_url'
    """))
    
    if result.fetchone() is None:
        # Колонка не существует, добавляем её
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

