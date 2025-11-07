#!/bin/bash
# 🚨 Экстренное исправление ошибки 500

echo "🚨 Экстренное исправление ошибки 500 на production сервере"
echo "=========================================================="

# 1. Проверяем переменные окружения
echo "1. Проверка переменных окружения..."
if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY не установлен!"
    export SECRET_KEY="emergency-secret-key-$(date +%s)"
    echo "✅ Установлен временный SECRET_KEY"
fi

if [ -z "$MAIL_USERNAME" ]; then
    echo "❌ MAIL_USERNAME не установлен!"
    export MAIL_SUPPRESS_SEND="true"
    echo "✅ Отключена отправка email"
fi

# 2. Проверяем базу данных
echo "2. Проверка базы данных..."
python3 -c "
import os
os.environ['FLASK_APP'] = 'app.py'
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.engine.execute('SELECT 1')
        print('✅ База данных доступна')
    except Exception as e:
        print(f'❌ Ошибка БД: {e}')
"

# 3. Перезапускаем сервис
echo "3. Перезапуск сервиса..."
systemctl restart your-app-service
sleep 5

# 4. Проверяем статус
echo "4. Проверка статуса..."
systemctl status your-app-service --no-pager

echo "✅ Экстренное исправление завершено"
