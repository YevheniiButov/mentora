#!/usr/bin/env python3
"""
Админский скрипт для сброса пароля конкретному пользователю.
"""

import os
import sys
from datetime import datetime, timezone

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User

def reset_user_password(email, new_password=None):
    """Сбрасывает пароль пользователя"""
    
    with app.app_context():
        try:
            print(f"🔍 Поиск пользователя: {email}")
            
            # Находим пользователя
            user = User.query.filter_by(email=email).first()
            
            if not user:
                print(f"❌ Пользователь с email {email} не найден")
                return False
            
            print(f"✅ Найден пользователь: {user.first_name} {user.last_name}")
            print(f"   - ID: {user.id}")
            print(f"   - Email: {user.email}")
            print(f"   - Активен: {user.is_active}")
            print(f"   - Email подтвержден: {user.email_confirmed}")
            
            # Генерируем пароль если не указан
            if not new_password:
                import secrets
                import string
                new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            
            # Устанавливаем новый пароль
            user.set_password(new_password)
            
            # Активируем аккаунт
            user.is_active = True
            user.email_confirmed = True
            
            # Сохраняем изменения
            db.session.commit()
            
            print(f"✅ Пароль успешно сброшен!")
            print(f"🔑 Новый пароль: {new_password}")
            print(f"✅ Аккаунт активирован")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка при сбросе пароля: {str(e)}")
            return False

def list_all_users():
    """Показывает список всех пользователей"""
    
    with app.app_context():
        try:
            print("👥 Список всех пользователей:")
            print("=" * 60)
            
            users = User.query.all()
            
            for user in users:
                status = "✅ Активен" if user.is_active else "❌ Заблокирован"
                email_status = "✅ Подтвержден" if user.email_confirmed else "❌ Не подтвержден"
                password_status = "✅ Есть" if user.password_hash else "❌ Нет"
                
                print(f"\n👤 ID: {user.id}")
                print(f"   📧 Email: {user.email}")
                print(f"   👤 Имя: {user.first_name} {user.last_name}")
                print(f"   🔐 Пароль: {password_status}")
                print(f"   ✅ Статус: {status}")
                print(f"   📧 Email: {email_status}")
                print(f"   📅 Регистрация: {user.created_at.strftime('%Y-%m-%d %H:%M')}")
                
        except Exception as e:
            print(f"❌ Ошибка при получении списка пользователей: {str(e)}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--list':
            list_all_users()
        elif command == '--reset' and len(sys.argv) > 2:
            email = sys.argv[2]
            new_password = sys.argv[3] if len(sys.argv) > 3 else None
            reset_user_password(email, new_password)
        else:
            print("❌ Неверная команда")
            print("\nИспользование:")
            print("  python admin_reset_user_password.py --list")
            print("  python admin_reset_user_password.py --reset email@example.com")
            print("  python admin_reset_user_password.py --reset email@example.com new_password")
    else:
        print("🔧 Админский инструмент для сброса паролей")
        print("=" * 40)
        print()
        print("Доступные команды:")
        print("  --list                    - Показать всех пользователей")
        print("  --reset email             - Сбросить пароль пользователю")
        print("  --reset email password    - Установить конкретный пароль")
        print()
        print("Примеры:")
        print("  python admin_reset_user_password.py --list")
        print("  python admin_reset_user_password.py --reset user@example.com")
        print("  python admin_reset_user_password.py --reset user@example.com MyNewPassword123")
