#!/usr/bin/env python3
"""
Скрипт для создания бэкапа продакшн базы данных
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime
import json

def create_backup_directory():
    """Создает директорию для бэкапов"""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"✅ Created backup directory: {backup_dir}")
    return backup_dir

def backup_sqlite_database():
    """Создает бэкап SQLite базы данных"""
    backup_dir = create_backup_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Путь к продакшн БД
    prod_db_path = "instance/app.db"
    if not os.path.exists(prod_db_path):
        print(f"❌ Production database not found: {prod_db_path}")
        return False
    
    # Создаем бэкап
    backup_filename = f"production_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        shutil.copy2(prod_db_path, backup_path)
        print(f"✅ SQLite backup created: {backup_path}")
        
        # Создаем метаданные бэкапа
        metadata = {
            "backup_type": "sqlite",
            "timestamp": timestamp,
            "source_path": prod_db_path,
            "backup_path": backup_path,
            "file_size": os.path.getsize(backup_path),
            "created_by": "backup_production.py"
        }
        
        metadata_path = os.path.join(backup_dir, f"backup_metadata_{timestamp}.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Backup metadata created: {metadata_path}")
        return backup_path
        
    except Exception as e:
        print(f"❌ Error creating SQLite backup: {e}")
        return False

def backup_postgresql_database():
    """Создает бэкап PostgreSQL базы данных"""
    backup_dir = create_backup_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Получаем URL базы данных
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    # Создаем бэкап
    backup_filename = f"production_backup_{timestamp}.sql"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Используем pg_dump для создания бэкапа
        cmd = f"pg_dump {database_url} > {backup_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ PostgreSQL backup created: {backup_path}")
            
            # Создаем метаданные бэкапа
            metadata = {
                "backup_type": "postgresql",
                "timestamp": timestamp,
                "database_url": database_url,
                "backup_path": backup_path,
                "file_size": os.path.getsize(backup_path),
                "created_by": "backup_production.py"
            }
            
            metadata_path = os.path.join(backup_dir, f"backup_metadata_{timestamp}.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Backup metadata created: {metadata_path}")
            return backup_path
        else:
            print(f"❌ Error creating PostgreSQL backup: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception creating PostgreSQL backup: {e}")
        return False

def create_staging_copy(backup_path):
    """Создает копию для staging из бэкапа"""
    if not backup_path:
        print("❌ No backup path provided")
        return False
    
    staging_dir = "staging"
    if not os.path.exists(staging_dir):
        os.makedirs(staging_dir)
    
    # Определяем тип бэкапа
    if backup_path.endswith('.db'):
        # SQLite бэкап
        staging_db_path = os.path.join(staging_dir, 'staging.db')
        try:
            shutil.copy2(backup_path, staging_db_path)
            print(f"✅ Staging SQLite copy created: {staging_db_path}")
            return staging_db_path
        except Exception as e:
            print(f"❌ Error creating staging copy: {e}")
            return False
    
    elif backup_path.endswith('.sql'):
        # PostgreSQL бэкап
        staging_db_path = os.path.join(staging_dir, 'staging.sql')
        try:
            shutil.copy2(backup_path, staging_db_path)
            print(f"✅ Staging PostgreSQL copy created: {staging_db_path}")
            return staging_db_path
        except Exception as e:
            print(f"❌ Error creating staging copy: {e}")
            return False
    
    else:
        print(f"❌ Unknown backup format: {backup_path}")
        return False

def verify_backup(backup_path):
    """Проверяет целостность бэкапа"""
    if not os.path.exists(backup_path):
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    file_size = os.path.getsize(backup_path)
    if file_size == 0:
        print(f"❌ Backup file is empty: {backup_path}")
        return False
    
    print(f"✅ Backup verification passed: {file_size} bytes")
    return True

def main():
    """Основная функция создания бэкапа"""
    
    print("💾 Creating production database backup...")
    print("=" * 50)
    
    backup_path = None
    
    # Определяем тип базы данных
    database_url = os.environ.get('DATABASE_URL', '')
    
    if database_url.startswith('postgresql://') or database_url.startswith('postgres://'):
        print("🐘 Detected PostgreSQL database")
        backup_path = backup_postgresql_database()
    elif os.path.exists('instance/app.db'):
        print("🗃️ Detected SQLite database")
        backup_path = backup_sqlite_database()
    else:
        print("❌ No database found to backup")
        sys.exit(1)
    
    if not backup_path:
        print("❌ Backup failed")
        sys.exit(1)
    
    # Проверяем бэкап
    if not verify_backup(backup_path):
        print("❌ Backup verification failed")
        sys.exit(1)
    
    # Создаем копию для staging
    staging_path = create_staging_copy(backup_path)
    if not staging_path:
        print("❌ Staging copy creation failed")
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 Backup completed successfully!")
    print(f"📁 Production backup: {backup_path}")
    print(f"📁 Staging copy: {staging_path}")
    print()
    print("⚠️  Keep backup safe before proceeding with migration!")

if __name__ == "__main__":
    main()


