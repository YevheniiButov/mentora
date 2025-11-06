#!/usr/bin/env python3
"""
🛡️ СИСТЕМА ЗАЩИТЫ ДАННЫХ MENTORA
Автоматические бэкапы и восстановление
"""
import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProtectionSystem:
    """Система защиты данных"""
    
    def __init__(self):
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_full_backup(self):
        """Создание полного бэкапа"""
        from app import create_app
        from extensions import db
        from models import User, UserProgress, WebsiteVisit, UserSession
        
        app = create_app()
        
        with app.app_context():
            try:
                timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
                backup_file = self.backup_dir / f'full_backup_{timestamp}.json'
                
                logger.info("🔄 Creating full backup...")
                
                # Получаем всех пользователей
                users = User.query.all()
                
                backup_data = {
                    'timestamp': timestamp,
                    'version': '1.0',
                    'total_users': len(users),
                    'users': []
                }
                
                for user in users:
                    # Собираем все данные пользователя
                    user_data = {
                        # Основные поля
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'password_hash': user.password_hash,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role,
                        'is_active': user.is_active,
                        'email_confirmed': user.email_confirmed,
                        
                        # DigiD поля
                        'created_via_digid': user.created_via_digid,
                        'digid_username': user.digid_username,
                        'bsn': user.bsn,
                        'digid_verified': user.digid_verified,
                        
                        # Профиль
                        'profession': user.profession,
                        'workplace': user.workplace,
                        'language': user.language,
                        'phone': user.phone,
                        'birth_date': user.birth_date.isoformat() if user.birth_date else None,
                        'gender': user.gender,
                        'nationality': user.nationality,
                        
                        # Регистрация
                        'registration_completed': user.registration_completed,
                        'diploma_file': user.diploma_file,
                        'language_certificate': user.language_certificate,
                        
                        # Обучение
                        'legal_status': user.legal_status,
                        'dutch_level': user.dutch_level,
                        'english_level': user.english_level,
                        'big_exam_registered': user.big_exam_registered,
                        'exam_date': user.exam_date.isoformat() if user.exam_date else None,
                        'preparation_time': user.preparation_time,
                        
                        # Геймификация
                        'level': user.level,
                        'xp': user.xp,
                        'has_subscription': user.has_subscription,
                        
                        # Настройки
                        'notification_settings': user.notification_settings,
                        'privacy_settings': user.privacy_settings,
                        
                        # Согласия
                        'required_consents': user.required_consents,
                        'optional_consents': user.optional_consents,
                        'digital_signature': user.digital_signature,
                        
                        # Временные метки
                        'created_at': user.created_at.isoformat() if user.created_at else None,
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                        'profile_updated_at': user.profile_updated_at.isoformat() if user.profile_updated_at else None,
                        
                        # Прогресс
                        'progress_count': user.progress.count(),
                        'requires_diagnostic': user.requires_diagnostic
                    }
                    
                    backup_data['users'].append(user_data)
                
                # Сохраняем бэкап
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ Full backup created: {backup_file}")
                logger.info(f"   Users backed up: {len(users)}")
                logger.info(f"   File size: {backup_file.stat().st_size} bytes")
                
                return str(backup_file)
                
            except Exception as e:
                logger.error(f"❌ Backup failed: {e}")
                return None
    
    def restore_full_backup(self, backup_file_path):
        """Восстановление из полного бэкапа"""
        from app import create_app
        from extensions import db
        from models import User
        
        app = create_app()
        
        with app.app_context():
            try:
                backup_file = Path(backup_file_path)
                
                if not backup_file.exists():
                    logger.error(f"❌ Backup file not found: {backup_file}")
                    return False
                
                # Загружаем бэкап
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                users_data = backup_data.get('users', [])
                logger.info(f"📥 Restoring {len(users_data)} users...")
                
                restored_count = 0
                updated_count = 0
                skipped_count = 0
                
                for user_data in users_data:
                    try:
                        # Ищем существующего пользователя
                        existing_user = None
                        
                        # Сначала по ID
                        if user_data.get('id'):
                            existing_user = User.query.get(user_data['id'])
                        
                        # Потом по email
                        if not existing_user and user_data.get('email'):
                            existing_user = User.query.filter_by(email=user_data['email']).first()
                        
                        # Потом по username
                        if not existing_user and user_data.get('username'):
                            existing_user = User.query.filter_by(username=user_data['username']).first()
                        
                        if existing_user:
                            # Обновляем существующего пользователя
                            self._update_user_from_backup(existing_user, user_data)
                            updated_count += 1
                            logger.info(f"🔄 Updated user: {user_data['email']}")
                        else:
                            # Создаем нового пользователя
                            new_user = self._create_user_from_backup(user_data)
                            if new_user:
                                db.session.add(new_user)
                                restored_count += 1
                                logger.info(f"🆕 Restored user: {user_data['email']}")
                            else:
                                skipped_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to restore user {user_data.get('email')}: {e}")
                        skipped_count += 1
                        continue
                
                # Сохраняем изменения
                db.session.commit()
                
                logger.info("✅ Restore completed!")
                logger.info(f"   Users restored: {restored_count}")
                logger.info(f"   Users updated: {updated_count}")
                logger.info(f"   Users skipped: {skipped_count}")
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Restore failed: {e}")
                db.session.rollback()
                return False
    
    def _update_user_from_backup(self, user, user_data):
        """Обновление пользователя из бэкапа"""
        # Обновляем только безопасные поля
        safe_fields = [
            'first_name', 'last_name', 'profession', 'workplace',
            'language', 'phone', 'gender', 'nationality',
            'legal_status', 'dutch_level', 'english_level',
            'big_exam_registered', 'preparation_time',
            'level', 'xp', 'notification_settings', 'privacy_settings'
        ]
        
        for field in safe_fields:
            if field in user_data and user_data[field] is not None:
                setattr(user, field, user_data[field])
        
        # Специальная обработка дат
        if user_data.get('birth_date'):
            try:
                user.birth_date = datetime.fromisoformat(user_data['birth_date']).date()
            except:
                pass
        
        if user_data.get('exam_date'):
            try:
                user.exam_date = datetime.fromisoformat(user_data['exam_date']).date()
            except:
                pass
    
    def _create_user_from_backup(self, user_data):
        """Создание пользователя из бэкапа"""
        from models import User
        
        try:
            user = User(
                email=user_data['email'],
                username=user_data.get('username'),
                password_hash=user_data.get('password_hash'),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                role=user_data.get('role', 'user'),
                is_active=user_data.get('is_active', True),
                email_confirmed=user_data.get('email_confirmed', False),
                
                # DigiD
                created_via_digid=user_data.get('created_via_digid', False),
                digid_username=user_data.get('digid_username'),
                bsn=user_data.get('bsn'),
                digid_verified=user_data.get('digid_verified', False),
                
                # Профиль
                profession=user_data.get('profession'),
                workplace=user_data.get('workplace'),
                language=user_data.get('language', 'nl'),
                phone=user_data.get('phone'),
                gender=user_data.get('gender'),
                nationality=user_data.get('nationality'),
                
                # Регистрация
                registration_completed=user_data.get('registration_completed', False),
                diploma_file=user_data.get('diploma_file'),
                language_certificate=user_data.get('language_certificate'),
                
                # Обучение
                legal_status=user_data.get('legal_status'),
                dutch_level=user_data.get('dutch_level'),
                english_level=user_data.get('english_level'),
                big_exam_registered=user_data.get('big_exam_registered'),
                preparation_time=user_data.get('preparation_time'),
                
                # Геймификация
                level=user_data.get('level', 1),
                xp=user_data.get('xp', 0),
                has_subscription=user_data.get('has_subscription', False),
                
                # Настройки
                notification_settings=user_data.get('notification_settings'),
                privacy_settings=user_data.get('privacy_settings'),
                
                # Согласия
                required_consents=user_data.get('required_consents', False),
                optional_consents=user_data.get('optional_consents', False),
                digital_signature=user_data.get('digital_signature'),
                
                # Прогресс
                requires_diagnostic=user_data.get('requires_diagnostic', True)
            )
            
            # Обработка дат
            if user_data.get('birth_date'):
                try:
                    user.birth_date = datetime.fromisoformat(user_data['birth_date']).date()
                except:
                    pass
            
            if user_data.get('exam_date'):
                try:
                    user.exam_date = datetime.fromisoformat(user_data['exam_date']).date()
                except:
                    pass
            
            if user_data.get('created_at'):
                try:
                    user.created_at = datetime.fromisoformat(user_data['created_at'])
                except:
                    pass
            
            if user_data.get('last_login'):
                try:
                    user.last_login = datetime.fromisoformat(user_data['last_login'])
                except:
                    pass
            
            return user
            
        except Exception as e:
            logger.error(f"Error creating user from backup: {e}")
            return None
    
    def list_backups(self):
        """Список бэкапов"""
        backup_files = list(self.backup_dir.glob('full_backup_*.json'))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        logger.info(f"📋 Available backups ({len(backup_files)}):")
        
        for backup_file in backup_files:
            size = backup_file.stat().st_size
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            # Читаем метаданные
            try:
                with open(backup_file, 'r') as f:
                    data = json.load(f)
                users_count = data.get('total_users', 0)
            except:
                users_count = 'unknown'
            
            logger.info(f"   📄 {backup_file.name}")
            logger.info(f"      Created: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"      Size: {size:,} bytes")
            logger.info(f"      Users: {users_count}")
            logger.info("")
        
        return backup_files
    
    def auto_backup_if_needed(self):
        """Автоматический бэкап если нужен"""
        from app import create_app
        from models import User
        
        app = create_app()
        
        with app.app_context():
            users_count = User.query.count()
            
            if users_count == 0:
                logger.info("📊 No users found - skipping backup")
                return None
            
            # Проверяем последний бэкап
            backup_files = list(self.backup_dir.glob('full_backup_*.json'))
            
            if not backup_files:
                logger.info("🔄 No existing backups - creating first backup")
                return self.create_full_backup()
            
            # Находим самый новый бэкап
            latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
            latest_time = datetime.fromtimestamp(latest_backup.stat().st_mtime)
            hours_since_backup = (datetime.now() - latest_time).total_seconds() / 3600
            
            if hours_since_backup > 24:  # Бэкап раз в сутки
                logger.info(f"⏰ Last backup was {hours_since_backup:.1f} hours ago - creating new backup")
                return self.create_full_backup()
            else:
                logger.info(f"✅ Recent backup exists ({hours_since_backup:.1f} hours ago)")
                return str(latest_backup)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🛡️  MENTORA DATA PROTECTION SYSTEM")
        print("")
        print("Usage:")
        print("  python scripts/data_protection.py backup           # Create full backup")
        print("  python scripts/data_protection.py restore <file>   # Restore from backup")
        print("  python scripts/data_protection.py list             # List available backups")
        print("  python scripts/data_protection.py auto             # Auto backup if needed")
        sys.exit(1)
    
    command = sys.argv[1]
    protection = DataProtectionSystem()
    
    if command == 'backup':
        backup_file = protection.create_full_backup()
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
        success = protection.restore_full_backup(backup_file)
        if success:
            print("✅ Restore completed")
        else:
            print("❌ Restore failed")
            sys.exit(1)
    
    elif command == 'list':
        protection.list_backups()
    
    elif command == 'auto':
        backup_file = protection.auto_backup_if_needed()
        if backup_file:
            print(f"✅ Auto backup: {backup_file}")
        else:
            print("ℹ️  No backup needed")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
