#!/usr/bin/env python3
"""
Скрипт для исправления роли администратора
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, User

def fix_admin_role():
    """Исправляет роль администратора"""
    
    with app.app_context():
        try:
            print("🔧 ИСПРАВЛЕНИЕ РОЛИ АДМИНИСТРАТОРА")
            print("=" * 50)
            
            # Находим пользователя admin@mentora.com
            admin_user = User.query.filter_by(email='admin@mentora.com').first()
            
            if not admin_user:
                print("❌ Пользователь admin@mentora.com не найден!")
                return
            
            print(f"👤 Найден пользователь: {admin_user.email}")
            print(f"   Текущая роль: {admin_user.role}")
            print(f"   Активен: {admin_user.is_active}")
            
            # Меняем роль на admin
            admin_user.role = 'admin'
            admin_user.is_active = True
            admin_user.email_confirmed = True
            admin_user.registration_completed = True
            
            db.session.commit()
            
            print(f"✅ Роль изменена на: {admin_user.role}")
            print(f"✅ Пользователь активирован: {admin_user.is_active}")
            print(f"✅ Email подтвержден: {admin_user.email_confirmed}")
            
            # Проверяем результат
            admins = User.query.filter_by(role='admin').count()
            print(f"\n👑 Всего администраторов: {admins}")
            
            print("\n✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО")
            print("🔑 Теперь вы можете войти в админку с:")
            print("   Email: admin@mentora.com")
            print("   Пароль: AdminPass123!")
            
        except Exception as e:
            print(f"❌ Ошибка исправления роли: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    fix_admin_role()
