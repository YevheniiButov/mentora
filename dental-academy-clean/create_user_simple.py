#!/usr/bin/env python3
"""
Простое создание пользователя без проблемных полей
"""
import os
import sys
from datetime import datetime, timezone

# Добавляем путь к проекту
sys.path.append('/home/render/project/src/dental-academy-clean')

def create_simple_user():
    """Создать пользователя простым способом"""
    try:
        from app import app, db
        from models import User
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # Проверяем, существует ли уже пользователь
            existing_user = User.query.filter_by(email='mentora@bigmentor.nl').first()
            if existing_user:
                print(f"✅ Пользователь уже существует: {existing_user.email}")
                return existing_user
            
            # Создаем нового пользователя с минимальными полями
            test_user = User(
                email='mentora@bigmentor.nl',
                username='mentora_prod_test',
                password_hash=generate_password_hash('mentora2024!'),
                first_name='Mentora',
                last_name='Test',
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
            
            # НЕ устанавливаем is_admin - оставляем по умолчанию
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Тестовый пользователь создан успешно!")
            print(f"   Email: {test_user.email}")
            print(f"   Username: {test_user.username}")
            print(f"   Password: mentora2024!")
            print(f"   ID: {test_user.id}")
            print(f"   Active: {test_user.is_active}")
            print(f"   Admin: {test_user.is_admin}")
            
            return test_user
            
    except Exception as e:
        print(f"❌ Ошибка создания пользователя: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Основная функция"""
    print("🚀 Простое создание тестового пользователя")
    print("=" * 50)
    
    user = create_simple_user()
    
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


