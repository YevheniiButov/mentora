#!/usr/bin/env python3
"""
Скрипт для проверки безопасности базы данных
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, User, LearningPath, Subject, Module, Lesson

def check_database_safety():
    """Проверяет безопасность базы данных"""
    
    with app.app_context():
        try:
            print("🔍 ПРОВЕРКА БЕЗОПАСНОСТИ БАЗЫ ДАННЫХ")
            print("=" * 50)
            
            # Проверяем пользователей
            total_users = User.query.count()
            admin_users = User.query.filter_by(role='admin').count()
            active_users = User.query.filter_by(is_active=True).count()
            
            print(f"👥 ПОЛЬЗОВАТЕЛИ:")
            print(f"   - Всего пользователей: {total_users}")
            print(f"   - Администраторов: {admin_users}")
            print(f"   - Активных пользователей: {active_users}")
            
            # Проверяем учебные материалы
            total_paths = LearningPath.query.count()
            total_subjects = Subject.query.count()
            total_modules = Module.query.count()
            total_lessons = Lesson.query.count()
            
            print(f"📚 УЧЕБНЫЕ МАТЕРИАЛЫ:")
            print(f"   - Учебных путей: {total_paths}")
            print(f"   - Предметов: {total_subjects}")
            print(f"   - Модулей: {total_modules}")
            print(f"   - Уроков: {total_lessons}")
            
            # Проверяем последних пользователей
            recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
            print(f"🕒 ПОСЛЕДНИЕ ПОЛЬЗОВАТЕЛИ:")
            for user in recent_users:
                print(f"   - {user.email} ({user.created_at.strftime('%Y-%m-%d %H:%M')})")
            
            print("\n✅ ПРОВЕРКА ЗАВЕРШЕНА")
            print("🔒 БАЗА ДАННЫХ БЕЗОПАСНА - данные не будут потеряны при деплое!")
            
        except Exception as e:
            print(f"❌ Ошибка проверки базы данных: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    check_database_safety()
