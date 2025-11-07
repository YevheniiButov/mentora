#!/usr/bin/env python3
"""
Скрипт для исправления проблем с паролями существующих пользователей.
Активирует аккаунты и убирает требование подтверждения email.
"""

import os
import sys
from datetime import datetime, timezone

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User

def fix_existing_users():
    """Исправляет проблемы с паролями существующих пользователей"""
    
    with app.app_context():
        try:
            print("🔍 Начинаем исправление существующих пользователей...")
            
            # Находим всех пользователей с заблокированными аккаунтами
            blocked_users = User.query.filter(
                (User.is_active == False) | (User.email_confirmed == False)
            ).all()
            
            print(f"📋 Найдено {len(blocked_users)} пользователей с проблемами:")
            
            fixed_count = 0
            
            for user in blocked_users:
                print(f"\n👤 Пользователь: {user.email} ({user.first_name} {user.last_name})")
                print(f"   - Активен: {user.is_active}")
                print(f"   - Email подтвержден: {user.email_confirmed}")
                print(f"   - Есть пароль: {user.password_hash is not None}")
                print(f"   - Дата регистрации: {user.created_at}")
                
                # Активируем аккаунт
                user.is_active = True
                user.email_confirmed = True
                
                # Если нет пароля, генерируем временный
                if not user.password_hash:
                    import secrets
                    import string
                    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                    user.set_password(temp_password)
                    print(f"   ✅ Сгенерирован временный пароль: {temp_password}")
                else:
                    print(f"   ✅ Пароль уже установлен")
                
                fixed_count += 1
            
            # Сохраняем изменения
            db.session.commit()
            
            print(f"\n🎉 Исправлено {fixed_count} пользователей!")
            print(f"📊 Всего пользователей в базе: {User.query.count()}")
            print(f"📊 Активных пользователей: {User.query.filter_by(is_active=True).count()}")
            
            # Показываем статистику
            print(f"\n📈 Статистика:")
            print(f"   - Всего пользователей: {User.query.count()}")
            print(f"   - Активных: {User.query.filter_by(is_active=True).count()}")
            print(f"   - С подтвержденным email: {User.query.filter_by(email_confirmed=True).count()}")
            print(f"   - С паролями: {User.query.filter(User.password_hash.isnot(None)).count()}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка при исправлении пользователей: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def show_user_details():
    """Показывает детали всех пользователей"""
    
    with app.app_context():
        try:
            print("👥 Детали всех пользователей:")
            print("=" * 80)
            
            users = User.query.all()
            
            for user in users:
                print(f"\n👤 ID: {user.id}")
                print(f"   📧 Email: {user.email}")
                print(f"   👤 Имя: {user.first_name} {user.last_name}")
                print(f"   🔐 Есть пароль: {user.password_hash is not None}")
                print(f"   ✅ Активен: {user.is_active}")
                print(f"   📧 Email подтвержден: {user.email_confirmed}")
                print(f"   📅 Дата регистрации: {user.created_at}")
                print(f"   🏥 Профессия: {user.profession}")
                
        except Exception as e:
            print(f"❌ Ошибка при показе пользователей: {str(e)}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--show':
        show_user_details()
    else:
        print("🚀 Исправление проблем с паролями существующих пользователей")
        print("=" * 60)
        print()
        print("Этот скрипт:")
        print("✅ Активирует заблокированные аккаунты")
        print("✅ Убирает требование подтверждения email")
        print("✅ Генерирует временные пароли для аккаунтов без паролей")
        print()
        
        confirm = input("Продолжить? (y/N): ").strip().lower()
        if confirm == 'y':
            success = fix_existing_users()
            if success:
                print("\n✅ Исправление завершено успешно!")
                print("\n📧 Пользователи могут:")
                print("   1. Войти с временным паролем (если он был сгенерирован)")
                print("   2. Использовать 'Забыли пароль' для сброса пароля")
                print("   3. Обратиться к администратору за помощью")
            else:
                print("\n❌ Исправление завершилось с ошибками!")
        else:
            print("Отменено пользователем.")


