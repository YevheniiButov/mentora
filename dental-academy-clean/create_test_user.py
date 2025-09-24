#!/usr/bin/env python3
"""
Скрипт для создания тестового пользователя для mentora.com.in
"""
import os
import sys
from datetime import datetime, timezone

# Добавить путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User

def create_test_user():
    """Создать тестового пользователя для mentora.com.in"""
    app = create_app()
    
    with app.app_context():
        # Проверить, существует ли уже тестовый пользователь
        existing_user = User.query.filter_by(email='test@mentora.com').first()
        if existing_user:
            print(f"✅ Тестовый пользователь уже существует:")
            print(f"   Email: {existing_user.email}")
            print(f"   Username: {existing_user.username}")
            print(f"   ID: {existing_user.id}")
            print(f"   Активен: {existing_user.is_active}")
            return existing_user
        
        # Создать нового тестового пользователя
        test_user = User(
            email='test@mentora.com',
            username='mentora_test',
            first_name='Test',
            last_name='User',
            is_active=True,
            role='user',
            email_confirmed=True,
            registration_completed=True,
            profession='tandarts',  # стоматолог
            created_at=datetime.now(timezone.utc)
        )
        
        # Установить пароль
        test_user.set_password('mentora123')
        
        # Сохранить в БД
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Тестовый пользователь создан успешно!")
        print(f"   Email: {test_user.email}")
        print(f"   Username: {test_user.username}")
        print(f"   Password: mentora123")
        print(f"   ID: {test_user.id}")
        
        return test_user

def create_admin_user():
    """Создать админ пользователя для mentora.com.in"""
    app = create_app()
    
    with app.app_context():
        # Проверить, существует ли уже админ пользователь
        existing_admin = User.query.filter_by(email='admin@mentora.com').first()
        if existing_admin:
            print(f"✅ Админ пользователь уже существует:")
            print(f"   Email: {existing_admin.email}")
            print(f"   Username: {existing_admin.username}")
            print(f"   ID: {existing_admin.id}")
            print(f"   Роль: {existing_admin.role}")
            return existing_admin
        
        # Создать нового админ пользователя
        admin_user = User(
            email='admin@mentora.com',
            username='mentora_admin',
            first_name='Admin',
            last_name='User',
            is_active=True,
            role='admin',
            email_confirmed=True,
            registration_completed=True,
            profession='tandarts',
            created_at=datetime.now(timezone.utc)
        )
        
        # Установить пароль
        admin_user.set_password('admin123')
        
        # Сохранить в БД
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Админ пользователь создан успешно!")
        print(f"   Email: {admin_user.email}")
        print(f"   Username: {admin_user.username}")
        print(f"   Password: admin123")
        print(f"   ID: {admin_user.id}")
        print(f"   Роль: {admin_user.role}")
        
        return admin_user

def list_all_users():
    """Показать всех пользователей"""
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        
        print(f"📋 Всего пользователей в БД: {len(users)}")
        print("=" * 60)
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Username: {user.username}")
            print(f"Name: {user.first_name} {user.last_name}")
            print(f"Role: {user.role}")
            print(f"Active: {user.is_active}")
            print(f"Email Confirmed: {user.email_confirmed}")
            print(f"Created: {user.created_at}")
            print("-" * 40)

def main():
    """Основная функция"""
    print("🚀 Создание тестовых пользователей для mentora.com.in")
    print("=" * 60)
    
    try:
        # Создать тестового пользователя
        print("1. Создание тестового пользователя...")
        test_user = create_test_user()
        
        print("\n2. Создание админ пользователя...")
        admin_user = create_admin_user()
        
        print("\n3. Список всех пользователей:")
        list_all_users()
        
        print("\n" + "=" * 60)
        print("✅ Тестовые пользователи готовы!")
        print("\n🔑 Учетные данные для входа:")
        print("   Обычный пользователь:")
        print("   - Email: test@mentora.com")
        print("   - Username: mentora_test")
        print("   - Password: mentora123")
        print("\n   Админ пользователь:")
        print("   - Email: admin@mentora.com")
        print("   - Username: mentora_admin")
        print("   - Password: admin123")
        
        print("\n🌐 Тестирование:")
        print("1. Откройте https://mentora.com.in")
        print("2. Введите любые из учетных данных выше")
        print("3. Нажмите 'Come In'")
        print("4. Проверьте, что происходит вход в систему")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
