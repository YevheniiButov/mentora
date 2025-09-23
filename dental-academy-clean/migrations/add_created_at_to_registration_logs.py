#!/usr/bin/env python3
"""
Migration: Add created_at field to RegistrationLog model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from sqlalchemy import text

def upgrade():
    """Add created_at column to registration_logs table"""
    with app.app_context():
        try:
            # Check if column already exists (SQLite way)
            result = db.session.execute(text("PRAGMA table_info(registration_logs)"))
            columns = [row[1] for row in result.fetchall()]

            if 'created_at' in columns:
                print("✅ Column created_at already exists in registration_logs table")
                return

            # Add the column
            db.session.execute(text("""
                ALTER TABLE registration_logs
                ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """))

            # Add index
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_registration_logs_created_at
                ON registration_logs (created_at)
            """))

            db.session.commit()
            print("✅ Successfully added created_at column to registration_logs table")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding created_at column: {str(e)}")
            raise

def downgrade():
    """Remove created_at column from registration_logs table"""
    with app.app_context():
        try:
            # Drop index
            db.session.execute(text("""
                DROP INDEX IF EXISTS ix_registration_logs_created_at
            """))

            # Note: SQLite doesn't support DROP COLUMN directly
            # This would require recreating the table
            print("⚠️ SQLite doesn't support DROP COLUMN directly")
            print("⚠️ To remove created_at column, you would need to recreate the table")

            db.session.commit()
            print("✅ Successfully removed created_at index from registration_logs table")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error removing created_at column: {str(e)}")
            raise

if __name__ == '__main__':
    upgrade()
