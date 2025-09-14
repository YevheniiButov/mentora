#!/usr/bin/env python3
"""
Быстрое создание администратора через командную строку
Использование: python3 quick_admin.py email@example.com "Имя Фамилия" "password123"
"""

import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import User, db

def create_admin_quick(email, name, password):
    """Быстрое создание администратора"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Проверяем, не существует ли уже пользователь
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                if existing_user.role == 'admin':
                    print(f"✅ Пользователь {email} уже является администратором")
                    return True
                else:
                    # Делаем существующего пользователя админом
                    existing_user.role = 'admin'
                    existing_user.is_active = True
                    existing_user.email_confirmed = True
                    db.session.commit()
                    print(f"✅ Пользователь {email} теперь администратор!")
                    return True
            
            # Разделяем имя и фамилию
            name_parts = name.strip().split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Создаем нового администратора
            admin = User(
                email=email,
                username=email,
                first_name=first_name,
                last_name=last_name,
                role='admin',
                is_active=True,
                email_confirmed=True,
                registration_completed=True,
                language='en',
                created_at=datetime.utcnow()
            )
            
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            
            print(f"✅ Администратор создан: {email}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            db.session.rollback()
            return False

def main():
    if len(sys.argv) != 4:
        print("❌ Использование: python3 quick_admin.py email@example.com \"Имя Фамилия\" \"password123\"")
        print("Пример: python3 quick_admin.py admin@mentora.com \"Admin User\" \"admin123456\"")
        sys.exit(1)
    
    email = sys.argv[1]
    name = sys.argv[2]
    password = sys.argv[3]
    
    if create_admin_quick(email, name, password):
        print(f"🌐 Войдите в админ панель: /admin")
        print(f"📧 Email: {email}")
        print(f"🔐 Пароль: {password}")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
