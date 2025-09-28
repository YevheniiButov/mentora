#!/usr/bin/env python3
"""
Migration: Add missing columns to registration_visitors table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from sqlalchemy import text

def upgrade():
    """Add missing columns to registration_visitors table"""
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'registration_visitors' 
                AND column_name IN ('first_name_entered', 'last_name_entered', 'name_entered_at')
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            # Add first_name_entered if it doesn't exist
            if 'first_name_entered' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE registration_visitors 
                    ADD COLUMN first_name_entered VARCHAR(100)
                """))
                print("✅ Added first_name_entered column")
            
            # Add last_name_entered if it doesn't exist
            if 'last_name_entered' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE registration_visitors 
                    ADD COLUMN last_name_entered VARCHAR(100)
                """))
                print("✅ Added last_name_entered column")
            
            # Add name_entered_at if it doesn't exist
            if 'name_entered_at' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE registration_visitors 
                    ADD COLUMN name_entered_at TIMESTAMP
                """))
                print("✅ Added name_entered_at column")
            
            # Add indexes for the new columns
            try:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_registration_visitors_first_name_entered 
                    ON registration_visitors (first_name_entered)
                """))
                print("✅ Added index for first_name_entered")
            except Exception as e:
                print(f"⚠️ Index for first_name_entered already exists or error: {e}")
            
            try:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_registration_visitors_last_name_entered 
                    ON registration_visitors (last_name_entered)
                """))
                print("✅ Added index for last_name_entered")
            except Exception as e:
                print(f"⚠️ Index for last_name_entered already exists or error: {e}")
            
            db.session.commit()
            print("✅ Successfully added missing columns to registration_visitors table")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding columns to registration_visitors: {str(e)}")
            raise

def downgrade():
    """Remove added columns from registration_visitors table"""
    with app.app_context():
        try:
            # Drop indexes first
            db.session.execute(text("""
                DROP INDEX IF EXISTS ix_registration_visitors_first_name_entered
            """))
            db.session.execute(text("""
                DROP INDEX IF EXISTS ix_registration_visitors_last_name_entered
            """))
            
            # Drop columns
            db.session.execute(text("""
                ALTER TABLE registration_visitors 
                DROP COLUMN IF EXISTS first_name_entered
            """))
            db.session.execute(text("""
                ALTER TABLE registration_visitors 
                DROP COLUMN IF EXISTS last_name_entered
            """))
            db.session.execute(text("""
                ALTER TABLE registration_visitors 
                DROP COLUMN IF EXISTS name_entered_at
            """))
            
            db.session.commit()
            print("✅ Successfully removed columns from registration_visitors table")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error removing columns from registration_visitors: {str(e)}")
            raise

if __name__ == '__main__':
    upgrade()


