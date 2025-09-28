#!/usr/bin/env python3
"""
Скрипт для создания тестового пользователя на продакшн сервере
Используйте этот скрипт на сервере bigmentor.nl
"""
import os
import sys
from datetime import datetime, timezone

def create_production_test_user():
    """Создать тестового пользователя на продакшн сервере"""
    
    # Настройки для продакшн БД
    # Эти переменные должны быть установлены в продакшн среде
    db_host = os.environ.get('DATABASE_HOST', 'localhost')
    db_port = os.environ.get('DATABASE_PORT', '5432')
    db_name = os.environ.get('DATABASE_NAME', 'mentora_production')
    db_user = os.environ.get('DATABASE_USER', 'mentora_user')
    db_password = os.environ.get('DATABASE_PASSWORD')
    
    if not db_password:
        print("❌ DATABASE_PASSWORD не установлен в переменных окружения")
        print("Установите переменные окружения для продакшн БД:")
        print("export DATABASE_HOST=your_host")
        print("export DATABASE_PORT=5432")
        print("export DATABASE_NAME=your_db_name")
        print("export DATABASE_USER=your_user")
        print("export DATABASE_PASSWORD=your_password")
        return False
    
    try:
        # Импортировать модули приложения
        from app import create_app, db
        from models import User
        
        app = create_app()
        
        with app.app_context():
            # Проверить, существует ли уже тестовый пользователь
            existing_user = User.query.filter_by(email='mentora@bigmentor.nl').first()
            if existing_user:
                print(f"✅ Тестовый пользователь уже существует:")
                print(f"   Email: {existing_user.email}")
                print(f"   Username: {existing_user.username}")
                print(f"   ID: {existing_user.id}")
                print(f"   Активен: {existing_user.is_active}")
                return existing_user
            
            # Создать нового тестового пользователя
            test_user = User(
                email='mentora@bigmentor.nl',
                username='mentora_prod_test',
                first_name='Mentora',
                last_name='Test',
                is_active=True,
                role='user',
                email_confirmed=True,
                registration_completed=True,
                profession='tandarts',
                created_at=datetime.now(timezone.utc)
            )
            
            # Установить пароль
            test_user.set_password('mentora2024!')
            
            # Сохранить в БД
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Тестовый пользователь создан на продакшн сервере!")
            print(f"   Email: {test_user.email}")
            print(f"   Username: {test_user.username}")
            print(f"   Password: mentora2024!")
            print(f"   ID: {test_user.id}")
            
            return test_user
            
    except Exception as e:
        print(f"❌ Ошибка создания пользователя: {str(e)}")
        return False

def main():
    """Основная функция"""
    print("🚀 Создание тестового пользователя на продакшн сервере")
    print("=" * 60)
    
    print("⚠️  ВНИМАНИЕ: Этот скрипт создает пользователя в продакшн БД!")
    print("Убедитесь, что вы находитесь на правильном сервере.")
    
    response = input("\n❓ Продолжить? (y/N): ")
    if response.lower() != 'y':
        print("❌ Отменено")
        return False
    
    success = create_production_test_user()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Тестовый пользователь создан!")
        print("\n🔑 Учетные данные для входа на mentora.com.in:")
        print("   Email: mentora@bigmentor.nl")
        print("   Username: mentora_prod_test")
        print("   Password: mentora2024!")
        
        print("\n🌐 Тестирование:")
        print("1. Задеплойте изменения на mentora.com.in")
        print("2. Откройте https://mentora.com.in")
        print("3. Введите учетные данные выше")
        print("4. Нажмите 'Come In'")
        print("5. Проверьте, что происходит вход в систему")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


