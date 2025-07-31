#!/usr/bin/env python3
"""
WSGI файл для PythonAnywhere
"""

import sys
import os

# Добавляем путь к проекту
path = '/home/yourusername/dental-academy-clean'
if path not in sys.path:
    sys.path.append(path)

# Настройки окружения
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Импортируем приложение
try:
    from app import app as application
    print("✅ Приложение успешно импортировано!")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    # Создаем простое приложение-заглушку
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def hello():
        return '''
        <h1>Dental Academy</h1>
        <p>Приложение загружается...</p>
        <p>Ошибка: {}</p>
        <p>Проверьте логи в разделе Web на PythonAnywhere</p>
        '''.format(str(e))

# Для отладки
if __name__ == "__main__":
    application.run() 