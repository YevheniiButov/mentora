#!/usr/bin/env python3
"""
Простой скрипт для создания тестового пользователя на продакшн сервере
"""
import os
import sys
from datetime import datetime, timezone

# Добавляем путь к проекту
sys.path.append('/home/render/project/src/dental-academy-clean')

def create_test_user():
    """Создать тестового пользователя"""
    try:
        from app import app, db
        from models import User
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # Проверяем, существует ли уже пользователь
            existing_user = User.query.filter_by(email='mentora@bigmentor.nl').first()
            if existing_user:
                print(f"✅ Пользователь уже существует: {existing_user.email}")
                print(f"   Username: {existing_user.username}")
                print(f"   ID: {existing_user.id}")
                return existing_user
            
            # Создаем нового пользователя
            test_user = User(
                email='mentora@bigmentor.nl',
                username='mentora_prod_test',
                password_hash=generate_password_hash('mentora2024!'),
                first_name='Mentora',
                last_name='Test',
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
            
            # Устанавливаем is_admin через свойство
            test_user.is_admin = False
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Тестовый пользователь создан успешно!")
            print(f"   Email: {test_user.email}")
            print(f"   Username: {test_user.username}")
            print(f"   Password: mentora2024!")
            print(f"   ID: {test_user.id}")
            
            return test_user
            
    except Exception as e:
        print(f"❌ Ошибка создания пользователя: {e}")
        return None

def main():
    """Основная функция"""
    print("🚀 Создание тестового пользователя для mentora.com.in")
    print("=" * 50)
    
    # Проверяем переменные окружения
    print("📋 Проверка переменных окружения:")
    print(f"   DATABASE_URL: {'✅ Установлен' if os.getenv('DATABASE_URL') else '❌ Не установлен'}")
    print(f"   SECRET_KEY: {'✅ Установлен' if os.getenv('SECRET_KEY') else '❌ Не установлен'}")
    
    # Создаем пользователя
    user = create_test_user()
    
    if user:
        print("\n🎉 Готово! Теперь можно тестировать вход на mentora.com.in")
        print("\n📝 Учетные данные для входа:")
        print("   Email: mentora@bigmentor.nl")
        print("   Username: mentora_prod_test")
        print("   Password: mentora2024!")
    else:
        print("\n❌ Не удалось создать пользователя")

if __name__ == "__main__":
    main()
