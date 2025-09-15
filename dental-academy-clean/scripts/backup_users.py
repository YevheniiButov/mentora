#!/usr/bin/env python3
"""
DATABASE BACKUP & RESTORE UTILITY
Создание и восстановление бэкапов пользователей
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from extensions import db
from models import User, UserProgress, WebsiteVisit, UserSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_user_backup():
    """Создание бэкапа всех пользователей"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups'
        
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup file path
        backup_file = os.path.join(backup_dir, f'users_backup_{timestamp}.json')
        
        # Get all users
        users = User.query.all()
        
        backup_data = {
            'timestamp': timestamp,
            'total_users': len(users),
            'users': []
        }
        
        for user in users:
            user_data = {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'password_hash': user.password_hash,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active,
                'email_confirmed': user.email_confirmed,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'profession': user.profession,
                'workplace': user.workplace,
                'language': user.language,
                'created_via_digid': user.created_via_digid,
                'digid_username': user.digid_username,
                'bsn': user.bsn,
                'digid_verified': user.digid_verified,
                'level': user.level,
                'xp': user.xp,
                'has_subscription': user.has_subscription
            }
            backup_data['users'].append(user_data)
        
        # Save backup
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Backup created: {backup_file}")
        logger.info(f"   Users backed up: {len(users)}")
        
        return backup_file
        
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return None

def restore_user_backup(backup_file):
    """Восстановление пользователей из бэкапа"""
    try:
        if not os.path.exists(backup_file):
            logger.error(f"❌ Backup file not found: {backup_file}")
            return False
        
        # Load backup data
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        users_data = backup_data.get('users', [])
        logger.info(f"📥 Restoring {len(users_data)} users from backup...")
        
        restored_count = 0
        skipped_count = 0
        
        for user_data in users_data:
            try:
                # Check if user already exists
                existing_user = User.query.filter(
                    (User.email == user_data['email']) | 
                    (User.username == user_data['username'])
                ).first()
                
                if existing_user:
                    logger.info(f"⏭️  Skipping existing user: {user_data['email']}")
                    skipped_count += 1
                    continue
                
                # Create new user
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    is_active=user_data['is_active'],
                    email_confirmed=user_data['email_confirmed'],
                    profession=user_data.get('profession'),
                    workplace=user_data.get('workplace'),
                    language=user_data.get('language', 'nl'),
                    created_via_digid=user_data.get('created_via_digid', False),
                    digid_username=user_data.get('digid_username'),
                    bsn=user_data.get('bsn'),
                    digid_verified=user_data.get('digid_verified', False),
                    level=user_data.get('level', 1),
                    xp=user_data.get('xp', 0),
                    has_subscription=user_data.get('has_subscription', False)
                )
                
                # Parse timestamps
                if user_data.get('created_at'):
                    user.created_at = datetime.fromisoformat(user_data['created_at'])
                if user_data.get('last_login'):
                    user.last_login = datetime.fromisoformat(user_data['last_login'])
                
                db.session.add(user)
                restored_count += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to restore user {user_data.get('email')}: {e}")
                continue
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"✅ Restore completed!")
        logger.info(f"   Users restored: {restored_count}")
        logger.info(f"   Users skipped: {skipped_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Restore failed: {e}")
        db.session.rollback()
        return False

def list_backups():
    """Список доступных бэкапов"""
    backup_dir = 'backups'
    
    if not os.path.exists(backup_dir):
        logger.info("📂 No backup directory found")
        return []
    
    backup_files = [f for f in os.listdir(backup_dir) if f.startswith('users_backup_') and f.endswith('.json')]
    backup_files.sort(reverse=True)  # Newest first
    
    logger.info(f"📋 Available backups ({len(backup_files)}):")
    for backup_file in backup_files:
        backup_path = os.path.join(backup_dir, backup_file)
        size = os.path.getsize(backup_path)
        mtime = datetime.fromtimestamp(os.path.getmtime(backup_path))
        logger.info(f"   {backup_file} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
    
    return backup_files

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/backup_users.py create         # Create backup")
        print("  python scripts/backup_users.py restore <file> # Restore backup")
        print("  python scripts/backup_users.py list          # List backups")
        sys.exit(1)
    
    command = sys.argv[1]
    
    app = create_app()
    
    with app.app_context():
        if command == 'create':
            backup_file = create_user_backup()
            if backup_file:
                print(f"✅ Backup created: {backup_file}")
            else:
                print("❌ Backup failed")
                sys.exit(1)
                
        elif command == 'restore':
            if len(sys.argv) < 3:
                print("❌ Please specify backup file")
                sys.exit(1)
            
            backup_file = sys.argv[2]
            if not backup_file.startswith('/'):
                backup_file = os.path.join('backups', backup_file)
            
            success = restore_user_backup(backup_file)
            if success:
                print("✅ Restore completed")
            else:
                print("❌ Restore failed")
                sys.exit(1)
                
        elif command == 'list':
            list_backups()
            
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)

if __name__ == '__main__':
    main()
