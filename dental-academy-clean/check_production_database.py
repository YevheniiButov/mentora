#!/usr/bin/env python3
"""
Скрипт для проверки состояния базы данных в продакшене
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_production_database():
    """Проверяет состояние базы данных в продакшене"""
    
    print("🔍 ПРОВЕРКА БАЗЫ ДАННЫХ MENTORA")
    print("=" * 50)
    print(f"Время проверки: {datetime.now()}")
    print()
    
    # Проверяем переменные окружения
    print("📋 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ:")
    database_url = os.environ.get('DATABASE_URL', 'НЕ УСТАНОВЛЕНА')
    print(f"DATABASE_URL: {database_url}")
    
    # Определяем тип базы данных
    if 'sqlite' in database_url.lower():
        print("🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: Используется SQLite!")
        print("   SQLite НЕ подходит для продакшена - данные теряются при деплое")
    elif 'postgres' in database_url.lower():
        print("✅ Используется PostgreSQL - это правильно")
    else:
        print(f"❓ Неизвестный тип БД")
    
    print()
    
    try:
        # Загружаем приложение
        from app import app
        from models import db, User
        
        with app.app_context():
            print("🔧 КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ:")
            print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
            print(f"FLASK_ENV: {app.config.get('FLASK_ENV')}")
            print()
            
            # Проверяем подключение к БД
            print("📊 СОСТОЯНИЕ БАЗЫ ДАННЫХ:")
            try:
                # Проверяем подключение
                db.session.execute('SELECT 1')
                print("✅ Подключение к БД: Успешно")
                
                # Считаем пользователей
                total_users = User.query.count()
                admin_users = User.query.filter_by(role='admin').count()
                active_users = User.query.filter_by(is_active=True).count()
                
                print(f"👥 Всего пользователей: {total_users}")
                print(f"🔑 Администраторов: {admin_users}")
                print(f"✅ Активных пользователей: {active_users}")
                
                if total_users == 0:
                    print("🚨 ПРОБЛЕМА: В базе данных НЕТ пользователей!")
                    print("   Это объясняет, почему пользователи 'исчезают'")
                
                # Показываем последних пользователей
                if total_users > 0:
                    print("\n📋 ПОСЛЕДНИЕ ПОЛЬЗОВАТЕЛИ:")
                    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
                    for user in recent_users:
                        created = user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'Неизвестно'
                        print(f"   - {user.email} ({user.role}) - {created}")
                
                # Проверяем таблицы
                print(f"\n🗂️ ТАБЛИЦЫ В БД:")
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"   Найдено таблиц: {len(tables)}")
                
                # Проверяем важные таблицы
                important_tables = ['user', 'learning_path', 'subject', 'lesson']
                for table in important_tables:
                    if table in tables:
                        print(f"   ✅ {table}")
                    else:
                        print(f"   ❌ {table} - ОТСУТСТВУЕТ!")
                
            except Exception as db_error:
                print(f"❌ Ошибка доступа к БД: {str(db_error)}")
                print("   Возможные причины:")
                print("   - База данных не создана")
                print("   - Неправильные права доступа")
                print("   - Проблемы с сетью")
            
    except Exception as app_error:
        print(f"❌ Ошибка загрузки приложения: {str(app_error)}")
        print("   Возможные причины:")
        print("   - Отсутствуют зависимости")
        print("   - Ошибки в коде")
        print("   - Проблемы с конфигурацией")
    
    print()
    print("🔧 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ:")
    
    if 'sqlite' in database_url.lower():
        print("1. 🚨 НЕМЕДЛЕННО переключиться на PostgreSQL:")
        print("   - В Render Dashboard создать PostgreSQL базу")
        print("   - Подключить её к веб-сервису")
        print("   - Проверить, что DATABASE_URL указывает на PostgreSQL")
        print()
        print("2. 🔄 После переключения на PostgreSQL:")
        print("   - Сделать деплой")
        print("   - Создать админа заново")
        print("   - Проверить, что пользователи сохраняются")
    
    elif 'postgres' in database_url.lower():
        print("1. ✅ PostgreSQL настроен правильно")
        print("2. 🔍 Проверить логи деплоя на ошибки")
        print("3. 🔄 Добавить дополнительное логирование")
        print("4. 📊 Мониторить количество пользователей после деплоя")
    
    else:
        print("1. 🔧 Настроить DATABASE_URL")
        print("2. 📋 Проверить конфигурацию Render")
    
    print()
    print("=" * 50)
    print("✅ Проверка завершена")

if __name__ == "__main__":
    check_production_database()
