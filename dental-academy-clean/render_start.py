#!/usr/bin/env python3
"""
Файл запуска для Render
"""

import os
import sys
from app import app, db

# Настройки для Render
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Инициализация базы данных
with app.app_context():
    try:
        db.create_all()
        print("✅ База данных инициализирована успешно!")
    except Exception as e:
        print(f"⚠️ Ошибка инициализации БД: {e}")

if __name__ == '__main__':
    # Получаем порт из переменной окружения Render
    port = int(os.environ.get('PORT', 5000))
    
    # Запускаем приложение
    app.run(host='0.0.0.0', port=port, debug=False) 