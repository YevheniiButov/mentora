#!/usr/bin/env python3
"""
Скрипт для проверки прав администратора пользователя
Можно запускать на продакшене для проверки
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import User, db

def check_user_admin(email=None):
    """Проверяет права администратора пользователя"""
    app = create_app()
    
    with app.app_context():
        try:
            if email:
                user = User.query.filter_by(email=email).first()
                if not user:
                    print(f"❌ Пользователь с email {email} не найден!")
                    return 1
                
                print(f"\n👤 Пользователь: {user.email}")
                print(f"   ID: {user.id}")
                print(f"   Роль: {user.role}")
                print(f"   is_admin (property): {user.is_admin}")
                print(f"   is_active: {user.is_active}")
                print(f"   email_confirmed: {user.email_confirmed}")
                
                if user.role != 'admin':
                    print(f"\n⚠️  Пользователь НЕ является администратором!")
                    print(f"   Чтобы сделать администратором, выполните:")
                    print(f"   python scripts/set_user_admin.py {email}")
                else:
                    print(f"\n✅ Пользователь является администратором!")
            else:
                # Показать всех администраторов
                admins = User.query.filter_by(role='admin').all()
                print(f"\n👑 Всего администраторов: {len(admins)}")
                
                if len(admins) == 0:
                    print("⚠️  Администраторов не найдено!")
                else:
                    print("\n📋 Список администраторов:")
                    for admin in admins:
                        print(f"   - ID: {admin.id:3d} | {admin.email:40s} | role: {admin.role}")
            
            print("\n" + "="*80)
            
        except Exception as e:
            print(f"❌ Ошибка при проверке: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == '__main__':
    email = sys.argv[1] if len(sys.argv) > 1 else None
    exit(check_user_admin(email))

