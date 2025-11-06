#!/usr/bin/env python3
"""
Скрипт для диагностики и исправления проблем с миграциями Alembic.
Использование: python scripts/fix_migrations.py [--check-only] [--force-sync]
"""

import os
import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from flask_migrate import Migrate
from extensions import db
import sqlalchemy as sa


def check_migration_files():
    """Проверяет целостность файлов миграций"""
    migrations_dir = Path('migrations/versions')
    files = [f for f in migrations_dir.iterdir() if f.suffix == '.py' and not f.name.startswith('__')]
    
    revisions = {}
    print("🔍 Checking migration files...")
    
    for file in files:
        try:
            content = file.read_text(encoding='utf-8')
            rev_match = re.search(r"revision\s*=\s*['\"]([^'\"]+)['\"]", content)
            down_match = re.search(r"down_revision\s*=\s*['\"]([^'\"]+)['\"]", content)
            
            if rev_match:
                rev_id = rev_match.group(1)
                down_rev = down_match.group(1) if down_match else None
                revisions[rev_id] = {'file': file.name, 'down': down_rev}
        except Exception as e:
            print(f"❌ Error reading {file.name}: {e}")
    
    print(f"✅ Found {len(revisions)} migration files")
    
    # Check for broken references
    broken = []
    for rev, data in revisions.items():
        if data['down'] and data['down'] not in revisions and data['down'] != 'None':
            broken.append((rev, data['file'], data['down']))
            print(f"❌ {data['file']}: references non-existent revision '{data['down']}'")
    
    if broken:
        print(f"\n⚠️  Found {len(broken)} broken references!")
        return False
    else:
        print("✅ No broken references found")
        return True


def check_database_state():
    """Проверяет состояние миграций в базе данных"""
    # Import app here to avoid circular imports
    from app import app
    with app.app_context():
        try:
            # Check if alembic_version table exists
            inspector = sa.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'alembic_version' not in tables:
                print("⚠️  alembic_version table does not exist")
                return None
            
            # Get current revision from DB
            result = db.session.execute(sa.text("SELECT version_num FROM alembic_version"))
            row = result.fetchone()
            
            if row:
                current_rev = row[0]
                print(f"📊 Current database revision: {current_rev}")
                return current_rev
            else:
                print("⚠️  alembic_version table is empty")
                return None
                
        except Exception as e:
            print(f"❌ Error checking database: {e}")
            return None


def sync_to_head(force=False):
    """Синхронизирует состояние БД с текущим head"""
    # Import app here to avoid circular imports
    from app import app
    with app.app_context():
        try:
            # Get current head - use flask db heads command output parsing
            import subprocess
            result = subprocess.run(['flask', 'db', 'heads'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Error getting heads: {result.stderr}")
                return False
            
            # Parse head from output (first line should contain head revision)
            output_lines = result.stdout.split('\n')
            head_rev = None
            for line in output_lines:
                if '(head)' in line and 'revision' in line.lower():
                    # Extract revision ID (usually at the start)
                    parts = line.split()
                    for part in parts:
                        if len(part) > 10 and not part.startswith('('):
                            head_rev = part.strip('(),')
                            break
                elif line and not line.startswith('INFO') and not line.startswith('✅'):
                    # Try to find revision ID in the line
                    import re
                    match = re.search(r'([a-f0-9]{12}|[a-zA-Z0-9_]+)\s*\(head\)', line)
                    if match:
                        head_rev = match.group(1)
                        break
            
            if not head_rev:
                # Fallback: try to get from migration files
                from flask_migrate import history
                try:
                    heads = history()
                    if heads:
                        head_rev = heads[0].revision
                except:
                    pass
            
            if not head_rev:
                print("❌ Could not determine head revision")
                print("Output:", result.stdout[:500])
                return False
            
            print(f"📌 Current head revision: {head_rev}")
            
            # Get current DB revision
            current_rev = check_database_state()
            
            # Update alembic_version table directly (bypass Alembic's revision chain check)
            try:
                # First, try to update
                db.session.execute(sa.text("UPDATE alembic_version SET version_num = :rev"), {'rev': head_rev})
                db.session.commit()
                print(f"✅ Successfully updated alembic_version to {head_rev}")
                return True
            except Exception as e:
                # If UPDATE fails, try DELETE + INSERT
                try:
                    db.session.execute(sa.text("DELETE FROM alembic_version"))
                    db.session.execute(sa.text("INSERT INTO alembic_version (version_num) VALUES (:rev)"), {'rev': head_rev})
                    db.session.commit()
                    print(f"✅ Successfully synced alembic_version to {head_rev}")
                    return True
                except Exception as e2:
                    print(f"❌ Error updating alembic_version: {e2}")
                    db.session.rollback()
                    return False
            
        except Exception as e:
            print(f"❌ Error syncing database: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fix Alembic migration issues')
    parser.add_argument('--check-only', action='store_true', help='Only check, do not fix')
    parser.add_argument('--force-sync', action='store_true', help='Force sync database to head')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔧 Alembic Migration Fixer")
    print("=" * 60)
    
    # Step 1: Check migration files
    files_ok = check_migration_files()
    if not files_ok and not args.force_sync:
        print("\n❌ Migration files have issues. Fix them first.")
        return 1
    
    # Step 2: Check database state
    db_rev = check_database_state()
    
    if args.check_only:
        print("\n✅ Check complete (--check-only mode)")
        return 0
    
    # Step 3: Sync if needed
    if args.force_sync or db_rev is None:
        print("\n" + "=" * 60)
        print("🔄 Syncing database...")
        print("=" * 60)
        success = sync_to_head(force=args.force_sync)
        if success:
            print("\n✅ Migration sync complete!")
            return 0
        else:
            print("\n❌ Migration sync failed!")
            return 1
    
    print("\n✅ Everything looks good!")
    return 0


if __name__ == '__main__':
    sys.exit(main())

