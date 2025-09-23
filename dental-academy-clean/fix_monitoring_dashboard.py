#!/usr/bin/env python3
"""
Fix monitoring dashboard issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from sqlalchemy import text

def fix_monitoring_dashboard():
    """Fix monitoring dashboard database issues"""
    with app.app_context():
        try:
            print("🔧 Fixing monitoring dashboard issues...")
            
            # Check if columns exist in registration_visitors table
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'registration_visitors' 
                AND column_name IN ('first_name_entered', 'last_name_entered', 'name_entered_at')
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            print(f"📊 Existing columns: {existing_columns}")
            
            # Add missing columns
            if 'first_name_entered' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE registration_visitors 
                    ADD COLUMN first_name_entered VARCHAR(100)
                """))
                print("✅ Added first_name_entered column")
            
            if 'last_name_entered' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE registration_visitors 
                    ADD COLUMN last_name_entered VARCHAR(100)
                """))
                print("✅ Added last_name_entered column")
            
            if 'name_entered_at' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE registration_visitors 
                    ADD COLUMN name_entered_at TIMESTAMP
                """))
                print("✅ Added name_entered_at column")
            
            # Add indexes
            try:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_registration_visitors_first_name_entered 
                    ON registration_visitors (first_name_entered)
                """))
                print("✅ Added index for first_name_entered")
            except Exception as e:
                print(f"⚠️ Index for first_name_entered: {e}")
            
            try:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_registration_visitors_last_name_entered 
                    ON registration_visitors (last_name_entered)
                """))
                print("✅ Added index for last_name_entered")
            except Exception as e:
                print(f"⚠️ Index for last_name_entered: {e}")
            
            # Test the monitoring dashboard query
            print("🧪 Testing monitoring dashboard query...")
            test_result = db.session.execute(text("""
                SELECT COUNT(*) as total_visitors
                FROM registration_visitors 
                WHERE entry_time >= NOW() - INTERVAL '24 hours'
            """))
            total_visitors = test_result.fetchone()[0]
            print(f"✅ Test query successful: {total_visitors} visitors in last 24h")
            
            db.session.commit()
            print("🎉 Monitoring dashboard fixes applied successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing monitoring dashboard: {str(e)}")
            raise

if __name__ == '__main__':
    fix_monitoring_dashboard()
