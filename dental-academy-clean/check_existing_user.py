#!/usr/bin/env python3
"""
Проверить существующих пользователей
"""
import os
import sys
from datetime import datetime, timezone

# Добавляем путь к проекту
sys.path.append('/home/render/project/src/dental-academy-clean')

def check_existing_users():
    """Проверить существующих пользователей"""
    try:
        from app import app, db
        from models import User
        
        with app.app_context():
            # Проверяем всех пользователей
            users = User.query.all()
            print(f"📊 Всего пользователей в базе: {len(users)}")
            
            # Проверяем конкретного пользователя
            test_user = User.query.filter_by(email='mentora@bigmentor.nl').first()
            if test_user:
                print(f"✅ Пользователь уже существует:")
                print(f"   Email: {test_user.email}")
                print(f"   Username: {test_user.username}")
                print(f"   ID: {test_user.id}")
                print(f"   Active: {test_user.is_active}")
                print(f"   Admin: {test_user.is_admin}")
                return test_user
            else:
                print("❌ Пользователь mentora@bigmentor.nl не найден")
                
                # Показываем последних 5 пользователей
                recent_users = User.query.order_by(User.id.desc()).limit(5).all()
                print("\n📋 Последние 5 пользователей:")
                for user in recent_users:
                    print(f"   {user.id}: {user.email} ({user.username})")
                
                return None
            
    except Exception as e:
        print(f"❌ Ошибка проверки пользователей: {e}")
        return None

def main():
    """Основная функция"""
    print("🔍 Проверка существующих пользователей")
    print("=" * 50)
    
    user = check_existing_users()
    
    if user:
        print("\n🎉 Пользователь найден! Можно тестировать вход.")
        print("\n📝 Учетные данные для входа:")
        print("   Email: mentora@bigmentor.nl")
        print("   Username: mentora_prod_test")
        print("   Password: mentora2024!")
    else:
        print("\n❌ Пользователь не найден. Нужно создать нового.")

if __name__ == "__main__":
    main()


