#!/usr/bin/env python3
"""
Скрипт для настройки тестового домена mentora.com.in
"""
import os
import subprocess
import json
from pathlib import Path

def create_test_env_file():
    """Создать .env файл для тестового домена"""
    test_env_content = """# Test Domain Configuration - mentora.com.in
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration (Test)
DATABASE_URL=postgresql://mentora_test_user:test_password@localhost:5432/mentora_test_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=mentora_test_db
DATABASE_USER=mentora_test_user
DATABASE_PASSWORD=test_password

# Security
SECRET_KEY=test_secret_key_change_in_production
WTF_CSRF_ENABLED=True

# Email Configuration (Test)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=test@mentora.com.in
MAIL_PASSWORD=test_email_password

# Resend API (Test)
RESEND_API_KEY=test_resend_api_key

# reCAPTCHA (Test)
RECAPTCHA_PUBLIC_KEY=test_recaptcha_public_key
RECAPTCHA_PRIVATE_KEY=test_recaptcha_private_key

# Domain Configuration
TEST_DOMAIN=mentora.com.in
PRODUCTION_DOMAIN=bigmentor.nl

# Feature Flags
ENABLE_ANALYTICS=True
ENABLE_DIAGNOSTICS=True
ENABLE_IRT_TESTING=True
ENABLE_DEBUG_MODE=False

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/test_domain.log
"""
    
    with open('.env.test', 'w') as f:
        f.write(test_env_content)
    
    print("✅ Создан .env.test файл для тестового домена")

def create_test_database_script():
    """Создать скрипт для настройки тестовой БД"""
    script_content = """#!/bin/bash
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
"""
    
    with open('setup_test_database.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('setup_test_database.sh', 0o755)
    print("✅ Создан скрипт setup_test_database.sh")

def create_deployment_script():
    """Создать скрипт для деплоя на тестовый домен"""
    script_content = """#!/bin/bash
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
"""
    
    with open('deploy_test_domain.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('deploy_test_domain.sh', 0o755)
    print("✅ Создан скрипт deploy_test_domain.sh")

def create_nginx_config():
    """Создать конфигурацию Nginx для тестового домена"""
    nginx_config = """server {
    listen 80;
    server_name mentora.com.in www.mentora.com.in;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mentora.com.in www.mentora.com.in;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/mentora.com.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mentora.com.in/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Static files
    location /static {
        alias /path/to/mentora/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Logging
    access_log /var/log/nginx/mentora.com.in.access.log;
    error_log /var/log/nginx/mentora.com.in.error.log;
}
"""
    
    with open('nginx_mentora_test.conf', 'w') as f:
        f.write(nginx_config)
    
    print("✅ Создана конфигурация Nginx nginx_mentora_test.conf")

def create_test_checklist():
    """Создать чек-лист для тестирования"""
    checklist = {
        "test_domain_setup": [
            "✅ Создать .env.test файл",
            "✅ Настроить тестовую БД",
            "✅ Создать скрипты деплоя",
            "✅ Настроить Nginx конфигурацию",
            "✅ Получить SSL сертификат для mentora.com.in"
        ],
        "deployment_steps": [
            "1. Создать резервную копию продакшн БД",
            "2. Настроить тестовую БД на основе бэкапа",
            "3. Задеплоить коммиты после d727518 на тестовый домен",
            "4. Протестировать все функции",
            "5. После успешного тестирования - задеплоить на продакшн"
        ],
        "testing_checklist": [
            "🔍 Проверить работу аналитики (исправления PostgreSQL)",
            "🔍 Протестировать IRT диагностику",
            "🔍 Проверить регистрацию пользователей",
            "🔍 Протестировать админ панель",
            "🔍 Проверить работу форума",
            "🔍 Протестировать email уведомления",
            "🔍 Проверить производительность"
        ],
        "rollback_plan": [
            "1. В случае проблем - откатиться к коммиту d727518",
            "2. Восстановить БД из резервной копии",
            "3. Проверить работоспособность продакшн сайта"
        ]
    }
    
    with open('test_domain_checklist.json', 'w', encoding='utf-8') as f:
        json.dump(checklist, f, indent=2, ensure_ascii=False)
    
    print("✅ Создан чек-лист test_domain_checklist.json")

def main():
    """Основная функция"""
    print("🚀 Настройка тестового домена mentora.com.in")
    print("=" * 50)
    
    # Создать все необходимые файлы
    create_test_env_file()
    create_test_database_script()
    create_deployment_script()
    create_nginx_config()
    create_test_checklist()
    
    print("\n" + "=" * 50)
    print("✅ Настройка тестового домена завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Создать резервную копию продакшн БД:")
    print("   python3 backup_production_postgresql.py")
    print("\n2. Настроить тестовую БД:")
    print("   ./setup_test_database.sh")
    print("\n3. Задеплоить на тестовый домен:")
    print("   ./deploy_test_domain.sh")
    print("\n4. Проверить чек-лист:")
    print("   cat test_domain_checklist.json")

if __name__ == "__main__":
    main()
