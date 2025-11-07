#!/usr/bin/env python3
"""
Упрощенный файл запуска для PythonAnywhere
"""

import os
import sys

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Настройки для PythonAnywhere
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Импортируем приложение
try:
    from app import app, db
    
    # Инициализируем базу данных
    with app.app_context():
        try:
            db.create_all()
            print("✅ База данных инициализирована успешно!")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации БД: {e}")
    
    print("✅ Приложение готово к запуску!")
    print("🌐 URL: https://yourusername.pythonanywhere.com")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("📦 Убедитесь, что все зависимости установлены:")
    print("   pip3 install --user Flask Flask-Login Flask-SQLAlchemy")
except Exception as e:
    print(f"❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000) 