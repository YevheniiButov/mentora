#!/usr/bin/env python3
"""
Migration: Add session_id field to PageView model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from sqlalchemy import text

def upgrade():
    """Add session_id column to page_views table"""
    with app.app_context():
        try:
            # Check if column already exists (SQLite way)
            result = db.session.execute(text("PRAGMA table_info(page_views)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'session_id' in columns:
                print("✅ Column session_id already exists in page_views table")
                return
            
            # Add the column
            db.session.execute(text("""
                ALTER TABLE page_views 
                ADD COLUMN session_id VARCHAR(100)
            """))
            
            # Add index
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_page_views_session_id 
                ON page_views (session_id)
            """))
            
            db.session.commit()
            print("✅ Successfully added session_id column to page_views table")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding session_id column: {str(e)}")
            raise

def downgrade():
    """Remove session_id column from page_views table"""
    with app.app_context():
        try:
            # Drop index
            db.session.execute(text("""
                DROP INDEX IF EXISTS ix_page_views_session_id
            """))
            
            # Note: SQLite doesn't support DROP COLUMN directly
            # This would require recreating the table
            print("⚠️ SQLite doesn't support DROP COLUMN directly")
            print("⚠️ To remove session_id column, you would need to recreate the table")
            
            db.session.commit()
            print("✅ Successfully removed session_id index from page_views table")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error removing session_id column: {str(e)}")
            raise

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()
