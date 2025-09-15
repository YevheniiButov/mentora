#!/usr/bin/env python3
"""
Скрипт для проверки пользователей в базе данных
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, User

def check_users():
    """Проверяет пользователей в базе данных"""
    
    with app.app_context():
        try:
            print("🔍 ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ В БАЗЕ ДАННЫХ")
            print("=" * 50)
            
            # Проверяем общее количество пользователей
            total_users = User.query.count()
            print(f"👥 Всего пользователей: {total_users}")
            
            if total_users == 0:
                print("❌ Пользователи не найдены!")
                print("🔧 Возможные причины:")
                print("   - База данных пуста")
                print("   - Проблемы с подключением к БД")
                print("   - Таблица users не существует")
                return
            
            # Показываем всех пользователей
            users = User.query.all()
            print(f"\n📋 СПИСОК ПОЛЬЗОВАТЕЛЕЙ:")
            for user in users:
                print(f"   - ID: {user.id}")
                print(f"     Email: {user.email}")
                print(f"     Имя: {user.first_name} {user.last_name}")
                print(f"     Роль: {user.role}")
                print(f"     Активен: {user.is_active}")
                print(f"     Создан: {user.created_at}")
                print(f"     Последний вход: {user.last_login}")
                print()
            
            # Проверяем админов
            admins = User.query.filter_by(role='admin').all()
            print(f"👑 Администраторов: {len(admins)}")
            for admin in admins:
                print(f"   - {admin.email} ({admin.first_name} {admin.last_name})")
            
            # Проверяем активных пользователей
            active_users = User.query.filter_by(is_active=True).count()
            print(f"✅ Активных пользователей: {active_users}")
            
            print("\n✅ ПРОВЕРКА ЗАВЕРШЕНА")
            
        except Exception as e:
            print(f"❌ Ошибка проверки пользователей: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    check_users()
