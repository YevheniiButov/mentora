#!/bin/bash
# Скрипт для деплоя на тестовый домен mentora.com.in

echo "🚀 Деплой на тестовый домен mentora.com.in..."

# Переключиться на тестовую конфигурацию
cp .env.test .env

# Установить зависимости
pip install -r requirements.txt

# Запустить миграции БД
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Собрать статические файлы
python3 -c "from app import create_app; app = create_app(); app.app_context().push()"

# Запустить приложение
echo "🌐 Запуск приложения на тестовом домене..."
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app

echo "✅ Деплой завершен"
