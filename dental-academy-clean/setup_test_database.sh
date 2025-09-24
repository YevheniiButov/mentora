#!/bin/bash
# Скрипт для создания тестовой БД на основе продакшн бэкапа

echo "🗃️ Создание тестовой БД..."

# Создать пользователя и БД
sudo -u postgres psql -c "CREATE USER mentora_test_user WITH PASSWORD 'test_password';"
sudo -u postgres psql -c "CREATE DATABASE mentora_test_db OWNER mentora_test_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mentora_test_db TO mentora_test_user;"

# Восстановить из бэкапа (замените на актуальный путь к бэкапу)
echo "📥 Восстановление из бэкапа..."
PGPASSWORD=test_password psql -h localhost -U mentora_test_user -d mentora_test_db -f backups/latest_production_backup.sql

echo "✅ Тестовая БД создана и настроена"
