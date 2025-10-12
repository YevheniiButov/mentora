#!/usr/bin/env python3
"""
Скрипт для запуска приложения в локальном режиме разработки
с правильными настройками URL
"""

import os
import sys

# Устанавливаем переменные окружения для локальной разработки
os.environ['BASE_URL'] = 'http://127.0.0.1:5002'
os.environ['SERVER_NAME'] = '127.0.0.1:5002'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = 'true'

# Импортируем приложение
from app import app

if __name__ == '__main__':
    print("🚀 Запуск Mentora в локальном режиме разработки")
    print(f"📍 BASE_URL: {os.environ.get('BASE_URL')}")
    print(f"📍 SERVER_NAME: {os.environ.get('SERVER_NAME')}")
    print("🌐 Откройте браузер: http://127.0.0.1:5002")
    print("=" * 50)
    
    # Запускаем приложение
    app.run(
        host='127.0.0.1',
        port=5002,
        debug=True
    )
