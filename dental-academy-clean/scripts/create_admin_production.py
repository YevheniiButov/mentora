#!/usr/bin/env python3
"""
Скрипт для создания администратора в production
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import User, db

def create_admin_production():
    """Создает администратора для production"""
    
    with app.app_context():
        try:
            # Проверяем, есть ли уже админы
            existing_admins = User.query.filter_by(role='admin').count()
            
            if existing_admins > 0:
                print(f"✅ Администраторы уже существуют ({existing_admins} шт.)")
                return
            
            # Создаем администратора
            admin_email = "admin@mentora.com"
            admin_password = "AdminPass123!"
            
            # Проверяем, не существует ли уже пользователь с таким email
            if User.query.filter_by(email=admin_email).first():
                print(f"✅ Пользователь {admin_email} уже существует")
                return
            
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
            
        except Exception as e:
            print(f"❌ Ошибка создания администратора: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    create_admin_production()
