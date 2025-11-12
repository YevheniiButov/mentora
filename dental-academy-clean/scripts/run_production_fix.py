#!/usr/bin/env python3
"""
🚨 URGENT: Fix Production Database Missing Columns
Python version of the fix script for easy execution
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and show the result"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(result.stdout)
        else:
            print(f"❌ {description} - ERROR")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

def main():
    print("🚨 Starting production database fix...")
    print("=" * 50)
    
    # Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        return 1
    
    print("✅ DATABASE_URL found")
    print("🔧 Connecting to production database...")
    
    # Step 1: Check missing columns
    check_cmd = f'psql "{database_url}" -c "SELECT column_name FROM information_schema.columns WHERE table_name = \'personal_learning_plan\' AND column_name = \'current_category_focus\';"'
    run_command(check_cmd, "Checking if current_category_focus exists")
    
    # Step 2: Add missing columns
    fix_commands = [
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS current_category_focus VARCHAR(100) DEFAULT NULL;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS weak_categories JSONB DEFAULT NULL;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS strong_categories JSONB DEFAULT NULL;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS category_abilities JSONB DEFAULT NULL;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS time_invested INTEGER DEFAULT 0;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS daily_question_goal INTEGER DEFAULT 20;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS daily_time_goal INTEGER DEFAULT 30;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS daily_streak INTEGER DEFAULT 0;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS last_activity_date DATE DEFAULT NULL;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS longest_daily_streak INTEGER DEFAULT 0;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS daily_goal_met_count INTEGER DEFAULT 0;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS learning_velocity FLOAT DEFAULT 0.0;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS retention_rate FLOAT DEFAULT 0.0;"',
        f'psql "{database_url}" -c "ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS category_progress JSONB DEFAULT NULL;"'
    ]
    
    success_count = 0
    for cmd in fix_commands:
        if run_command(cmd, "Adding missing column"):
            success_count += 1
    
    # Step 3: Verify the fix
    verify_cmd = f'psql "{database_url}" -c "SELECT column_name FROM information_schema.columns WHERE table_name = \'personal_learning_plan\' AND column_name IN (\'current_category_focus\', \'weak_categories\', \'strong_categories\', \'time_invested\');"'
    run_command(verify_cmd, "Verifying columns were added")
    
    print("\n" + "=" * 50)
    print(f"🎉 Production database fix completed!")
    print(f"✅ Successfully added {success_count} columns")
    print("✅ Check the status above")
    print("✅ Test your Learning Map now")
    print("✅ API endpoints should work (200 instead of 500)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())







