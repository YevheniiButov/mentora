#!/usr/bin/env python3
"""
Скрипт для установки пользователя как администратора
Использование: python scripts/set_user_admin.py email@example.com
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import User, db

def set_user_admin(email):
    """Устанавливает пользователя как администратора"""
    app = create_app()
    
    with app.app_context():
        try:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                print(f"❌ Пользователь с email {email} не найден!")
                return 1
            
            print(f"\n👤 Найден пользователь: {user.email}")
            print(f"   Текущая роль: {user.role}")
            
            if user.role == 'admin':
                print(f"✅ Пользователь уже является администратором!")
                return 0
            
            # Устанавливаем роль администратора
            user.role = 'admin'
            user.is_active = True
            user.email_confirmed = True
            
            db.session.commit()
            
            print(f"✅ Роль изменена на: {user.role}")
            print(f"✅ Пользователь активирован: {user.is_active}")
            print(f"✅ Email подтвержден: {user.email_confirmed}")
            
            # Проверяем результат
            print(f"\n✅ Пользователь {email} теперь администратор!")
            
        except Exception as e:
            print(f"❌ Ошибка при установке роли: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return 1
    
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python scripts/set_user_admin.py email@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    exit(set_user_admin(email))

