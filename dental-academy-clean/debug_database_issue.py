#!/usr/bin/env python3
"""
Скрипт для диагностики проблемы с исчезновением пользователей
"""

import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def diagnose_database_issue():
    """Диагностируем проблему с базой данных"""
    
    print("🔍 ДИАГНОСТИКА ПРОБЛЕМЫ С БАЗОЙ ДАННЫХ")
    print("=" * 60)
    
    # 1. Проверяем переменные окружения
    print("1. 📋 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ:")
    print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', 'НЕ УСТАНОВЛЕНА')}")
    print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV', 'НЕ УСТАНОВЛЕНА')}")
    print(f"   SQLALCHEMY_DATABASE_URI: {os.environ.get('SQLALCHEMY_DATABASE_URI', 'НЕ УСТАНОВЛЕНА')}")
    
    # 2. Проверяем тип базы данных
    database_url = os.environ.get('DATABASE_URL', '')
    if 'sqlite' in database_url.lower():
        print("   ⚠️ ОБНАРУЖЕНА SQLITE - это может быть причиной!")
    elif 'postgres' in database_url.lower():
        print("   ✅ Используется PostgreSQL")
    else:
        print(f"   ❓ Неизвестный тип БД: {database_url}")
    
    print()
    
    # 3. Проверяем Flask приложение
    try:
        from app import app
        from models import db, User
        
        print("2. 🔧 КОНФИГУРАЦИЯ FLASK:")
        with app.app_context():
            print(f"   SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
            print(f"   DATABASE_URL: {app.config.get('DATABASE_URL')}")
            print(f"   FLASK_ENV: {app.config.get('FLASK_ENV')}")
            print()
            
            # 4. Проверяем состояние базы данных
            print("3. 📊 СОСТОЯНИЕ БАЗЫ ДАННЫХ:")
            try:
                user_count = User.query.count()
                print(f"   Количество пользователей: {user_count}")
                
                # Показываем последних пользователей
                recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
                print(f"   Последние 5 пользователей:")
                for user in recent_users:
                    print(f"     - {user.email} ({user.role}) - {user.created_at}")
                
            except Exception as db_error:
                print(f"   ❌ Ошибка доступа к БД: {str(db_error)}")
            
            print()
            
            # 5. Проверяем таблицы
            print("4. 🗂️ ТАБЛИЦЫ В БАЗЕ ДАННЫХ:")
            try:
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"   Найдено таблиц: {len(tables)}")
                for table in sorted(tables):
                    print(f"     - {table}")
            except Exception as table_error:
                print(f"   ❌ Ошибка получения списка таблиц: {str(table_error)}")
            
            print()
            
    except Exception as app_error:
        print(f"❌ Ошибка загрузки приложения: {str(app_error)}")
    
    # 6. Анализ возможных причин
    print("5. 🔍 ВОЗМОЖНЫЕ ПРИЧИНЫ ПРОБЛЕМЫ:")
    print()
    
    if 'sqlite' in database_url.lower():
        print("   ⚠️ КРИТИЧЕСКАЯ ПРОБЛЕМА: Используется SQLite!")
        print("   SQLite файлы могут:")
        print("     - Перезаписываться при каждом деплое")
        print("     - Не сохраняться между деплоями")
        print("     - Быть в .gitignore и не попадать в репозиторий")
        print()
        print("   🔧 РЕШЕНИЕ: Переключиться на PostgreSQL")
        print("     1. В Render создать PostgreSQL базу")
        print("     2. Подключить её к приложению")
        print("     3. Убедиться, что DATABASE_URL указывает на PostgreSQL")
    
    elif not database_url:
        print("   ⚠️ ПРОБЛЕМА: DATABASE_URL не установлена!")
        print("   🔧 РЕШЕНИЕ: Установить правильную DATABASE_URL")
    
    elif 'postgres' in database_url.lower():
        print("   ✅ База данных PostgreSQL настроена правильно")
        print("   🔍 Другие возможные причины:")
        print("     - Скрипты деплоя очищают данные")
        print("     - Проблемы с миграциями")
        print("     - Ошибки в коде создания пользователей")
    
    print()
    print("6. 📋 РЕКОМЕНДАЦИИ:")
    print("   1. Проверить тип базы данных в Render")
    print("   2. Убедиться, что используется PostgreSQL")
    print("   3. Проверить логи деплоя на наличие ошибок")
    print("   4. Добавить дополнительное логирование")
    
    print()
    print("=" * 60)
    print("🔍 Диагностика завершена")

if __name__ == "__main__":
    diagnose_database_issue()
