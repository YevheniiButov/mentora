#!/usr/bin/env python3
"""
Безопасный деплой скрипт для Mentora
Предотвращает потерю данных пользователей при деплое
"""

import os
import sys
import shutil
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def log_message(message, level="INFO"):
    """Логирование сообщений"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def check_database_connection():
    """Проверка подключения к базе данных"""
    try:
        from app import app
        from models import db, User
        
        with app.app_context():
            # Проверяем подключение к БД
            db.session.execute('SELECT 1')
            user_count = User.query.count()
            log_message(f"✅ Подключение к БД успешно. Пользователей: {user_count}")
            return True
    except Exception as e:
        log_message(f"❌ Ошибка подключения к БД: {str(e)}", "ERROR")
        return False

def create_backup():
    """Создание резервной копии базы данных"""
    try:
        from app import app
        from models import db, User, Contact, Profession
        
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.json"
        
        with app.app_context():
            backup_data = {
                'timestamp': timestamp,
                'users': [],
                'contacts': [],
                'professions': [],
                'metadata': {
                    'user_count': User.query.count(),
                    'contact_count': Contact.query.count() if hasattr(Contact, 'query') else 0,
                    'profession_count': Profession.query.count() if hasattr(Profession, 'query') else 0
                }
            }
            
            # Сохраняем пользователей
            for user in User.query.all():
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
                backup_data['users'].append(user_data)
            
            # Сохраняем контакты (если модель существует)
            try:
                for contact in Contact.query.all():
                    contact_data = {
                        'id': contact.id,
                        'full_name': contact.full_name,
                        'email': contact.email,
                        'phone': contact.phone,
                        'profession_id': contact.profession_id,
                        'contact_status': contact.contact_status,
                        'created_at': contact.created_at.isoformat() if contact.created_at else None
                    }
                    backup_data['contacts'].append(contact_data)
            except:
                log_message("⚠️ Модель Contact не найдена, пропускаем")
            
            # Сохраняем профессии (если модель существует)
            try:
                for profession in Profession.query.all():
                    profession_data = {
                        'id': profession.id,
                        'name': profession.name,
                        'name_nl': profession.name_nl,
                        'code': profession.code,
                        'category': profession.category,
                        'is_active': profession.is_active,
                        'created_at': profession.created_at.isoformat() if profession.created_at else None
                    }
                    backup_data['professions'].append(profession_data)
            except:
                log_message("⚠️ Модель Profession не найдена, пропускаем")
            
            # Сохраняем резервную копию
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            log_message(f"✅ Резервная копия создана: {backup_file}")
            log_message(f"📊 Сохранено: {len(backup_data['users'])} пользователей")
            
            return str(backup_file)
            
    except Exception as e:
        log_message(f"❌ Ошибка создания резервной копии: {str(e)}", "ERROR")
        return None

def restore_backup(backup_file):
    """Восстановление из резервной копии"""
    try:
        from app import app
        from models import db, User, Contact, Profession
        
        if not os.path.exists(backup_file):
            log_message(f"❌ Файл резервной копии не найден: {backup_file}", "ERROR")
            return False
        
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        with app.app_context():
            # Восстанавливаем пользователей
            restored_users = 0
            for user_data in backup_data['users']:
                existing_user = User.query.filter_by(email=user_data['email']).first()
                if not existing_user:
                    user = User(
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        role=user_data['role'],
                        is_active=user_data['is_active']
                    )
                    db.session.add(user)
                    restored_users += 1
            
            # Восстанавливаем контакты (если модель существует)
            restored_contacts = 0
            try:
                for contact_data in backup_data['contacts']:
                    existing_contact = Contact.query.filter_by(email=contact_data['email']).first()
                    if not existing_contact:
                        contact = Contact(
                            full_name=contact_data['full_name'],
                            email=contact_data['email'],
                            phone=contact_data['phone'],
                            profession_id=contact_data['profession_id'],
                            contact_status=contact_data['contact_status']
                        )
                        db.session.add(contact)
                        restored_contacts += 1
            except:
                log_message("⚠️ Модель Contact не найдена, пропускаем восстановление")
            
            # Восстанавливаем профессии (если модель существует)
            restored_professions = 0
            try:
                for profession_data in backup_data['professions']:
                    existing_profession = Profession.query.filter_by(code=profession_data['code']).first()
                    if not existing_profession:
                        profession = Profession(
                            name=profession_data['name'],
                            name_nl=profession_data['name_nl'],
                            code=profession_data['code'],
                            category=profession_data['category'],
                            is_active=profession_data['is_active']
                        )
                        db.session.add(profession)
                        restored_professions += 1
            except:
                log_message("⚠️ Модель Profession не найдена, пропускаем восстановление")
            
            db.session.commit()
            
            log_message(f"✅ Восстановление завершено:")
            log_message(f"   - Пользователей восстановлено: {restored_users}")
            log_message(f"   - Контактов восстановлено: {restored_contacts}")
            log_message(f"   - Профессий восстановлено: {restored_professions}")
            
            return True
            
    except Exception as e:
        log_message(f"❌ Ошибка восстановления: {str(e)}", "ERROR")
        return False

def ensure_admin_user():
    """Обеспечение наличия администратора"""
    try:
        from app import app
        from models import db, User
        
        with app.app_context():
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                log_message("⚠️ Администратор не найден, создаем...")
                
                # Создаем админа
                admin = User(
                    email='admin@mentora.com',
                    first_name='Admin',
                    last_name='Mentora',
                    role='admin',
                    is_active=True
                )
                admin.set_password('admin123')  # Временный пароль
                
                db.session.add(admin)
                db.session.commit()
                
                log_message("✅ Администратор создан: admin@mentora.com / admin123")
            else:
                log_message(f"✅ Администратор найден: {admin.email}")
                
            return True
            
    except Exception as e:
        log_message(f"❌ Ошибка создания администратора: {str(e)}", "ERROR")
        return False

def run_database_migrations():
    """Выполнение миграций базы данных"""
    try:
        log_message("🔄 Выполнение миграций базы данных...")
        
        # Создаем все таблицы
        from app import app
        from models import db
        
        with app.app_context():
            db.create_all()
            log_message("✅ Таблицы базы данных созданы/обновлены")
            
        return True
        
    except Exception as e:
        log_message(f"❌ Ошибка миграций: {str(e)}", "ERROR")
        return False

def cleanup_old_backups():
    """Очистка старых резервных копий (оставляем последние 10)"""
    try:
        backup_dir = Path("backups")
        if not backup_dir.exists():
            return
        
        backup_files = list(backup_dir.glob("backup_*.json"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Удаляем старые копии (оставляем последние 10)
        for old_backup in backup_files[10:]:
            old_backup.unlink()
            log_message(f"🗑️ Удалена старая резервная копия: {old_backup.name}")
            
    except Exception as e:
        log_message(f"⚠️ Ошибка очистки старых копий: {str(e)}", "WARNING")

def main():
    """Основная функция безопасного деплоя"""
    log_message("🚀 Начало безопасного деплоя Mentora")
    
    # 1. Проверяем подключение к БД
    if not check_database_connection():
        log_message("❌ Не удалось подключиться к БД, прерываем деплой", "ERROR")
        return False
    
    # 2. Создаем резервную копию
    backup_file = create_backup()
    if not backup_file:
        log_message("❌ Не удалось создать резервную копию, прерываем деплой", "ERROR")
        return False
    
    # 3. Выполняем миграции
    if not run_database_migrations():
        log_message("❌ Ошибка миграций, восстанавливаем из резервной копии", "ERROR")
        restore_backup(backup_file)
        return False
    
    # 4. Обеспечиваем наличие администратора
    if not ensure_admin_user():
        log_message("❌ Ошибка создания администратора", "ERROR")
        return False
    
    # 5. Очищаем старые резервные копии
    cleanup_old_backups()
    
    log_message("✅ Безопасный деплой завершен успешно!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
