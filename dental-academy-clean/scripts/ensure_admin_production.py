#!/usr/bin/env python3
"""
Надежный скрипт для создания админа в production
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, User

def ensure_admin_production():
    """Гарантированно создает админа в production"""
    
    with app.app_context():
        try:
            print("🔧 ENSURE ADMIN PRODUCTION SCRIPT")
            print("=" * 50)
            
            # Проверяем подключение к БД
            try:
                db.session.execute('SELECT 1')
                print("✅ Подключение к базе данных: OK")
            except Exception as e:
                print(f"❌ Ошибка подключения к БД: {e}")
                return False
            
            # Проверяем таблицы
            try:
                total_users = User.query.count()
                print(f"📊 Всего пользователей в БД: {total_users}")
            except Exception as e:
                print(f"❌ Ошибка запроса пользователей: {e}")
                return False
            
            # Проверяем админов
            try:
                existing_admins = User.query.filter_by(role='admin').all()
                print(f"👑 Найдено администраторов: {len(existing_admins)}")
                
                if existing_admins:
                    print("📋 Список существующих админов:")
                    for admin in existing_admins:
                        print(f"   - {admin.email} (ID: {admin.id}, Активен: {admin.is_active})")
                    print("✅ Администраторы уже существуют - НЕ СОЗДАЕМ НОВЫХ")
                    return True
                
            except Exception as e:
                print(f"❌ Ошибка проверки админов: {e}")
                return False
            
            # Создаем админа
            print("🔨 Создаем администратора...")
            
            admin_email = "admin@mentora.com"
            admin_password = "AdminPass123!"
            
            # Проверяем, не существует ли уже пользователь с таким email
            existing_user = User.query.filter_by(email=admin_email).first()
            if existing_user:
                print(f"⚠️  Пользователь {admin_email} уже существует, но не админ")
                # Делаем его админом
                existing_user.role = 'admin'
                existing_user.is_active = True
                existing_user.email_confirmed = True
                existing_user.registration_completed = True
                db.session.commit()
                print(f"✅ Пользователь {admin_email} назначен администратором")
                return True
            
            # Создаем нового админа
            admin = User(
                email=admin_email,
                username=admin_email,
                first_name="Admin",
                last_name="User",
                role='admin',
                is_active=True,
                email_confirmed=True,
                registration_completed=True,
                language='en'
            )
            
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            
            print(f"✅ Администратор создан:")
            print(f"   Email: {admin_email}")
            print(f"   Пароль: {admin_password}")
            print(f"   Роль: admin")
            print("🔒 ВАЖНО: Существующие пользователи НЕ затронуты!")
            
            return True
            
        except Exception as e:
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = ensure_admin_production()
    if not success:
        print("❌ СКРИПТ ЗАВЕРШИЛСЯ С ОШИБКОЙ")
        sys.exit(1)
    else:
        print("✅ СКРИПТ ВЫПОЛНЕН УСПЕШНО")
