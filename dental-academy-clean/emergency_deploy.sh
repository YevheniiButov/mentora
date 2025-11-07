#!/bin/bash
# 🚨 Экстренный деплой для восстановления работы сервера

echo "🚨 ЭКСТРЕННЫЙ ДЕПЛОЙ - ВОССТАНОВЛЕНИЕ РАБОТЫ СЕРВЕРА"
echo "=================================================="

# 1. Останавливаем сервис
echo "1. Остановка сервиса..."
systemctl stop your-app-service

# 2. Переходим в директорию приложения
cd /path/to/your/app

# 3. Получаем последние изменения
echo "2. Получение последних изменений..."
git pull origin main

# 4. Устанавливаем зависимости
echo "3. Установка зависимостей..."
pip3 install -r requirements.txt

# 5. Создаем .env файл с временными значениями
echo "4. Создание .env файла..."
cat > .env << EOF
SECRET_KEY=mentora-production-temp-key-2024
FLASK_ENV=production
FLASK_DEBUG=0
MAIL_USERNAME=MS_uUzJtfkAxyPn@mentora.mlsender.net
MAIL_PASSWORD=mssp.eTIPhpXlO2nu.e6t7xgcGA1kl.Bw3hiAB80JpM
MAIL_DEFAULT_SENDER=Mentora <noreply@mentora.com>
MAIL_SUPPRESS_SEND=true
DATABASE_URL=your-production-database-url
EOF

# 6. Устанавливаем права доступа
chmod 600 .env

# 7. Запускаем миграции БД
echo "5. Запуск миграций БД..."
python3 -c "
import os
os.environ['FLASK_APP'] = 'app.py'
from flask_migrate import upgrade
from app import create_app
app = create_app()
with app.app_context():
    upgrade()
"

# 8. Запускаем сервис
echo "6. Запуск сервиса..."
systemctl start your-app-service

# 9. Проверяем статус
echo "7. Проверка статуса..."
sleep 5
systemctl status your-app-service --no-pager

echo "✅ ЭКСТРЕННЫЙ ДЕПЛОЙ ЗАВЕРШЕН"
echo "🌐 Проверьте сайт: https://www.mentora.com.in"
