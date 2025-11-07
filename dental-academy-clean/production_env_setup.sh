#!/bin/bash
# 🚨 Быстрая настройка переменных окружения для production

echo "🚨 Настройка переменных окружения для production сервера"
echo "========================================================"

# Создаем .env файл для production
cat > .env << EOF
# Production Environment Variables
SECRET_KEY=mentora-production-secret-key-$(date +%s)
FLASK_ENV=production
FLASK_DEBUG=0

# Database
DATABASE_URL=your-production-database-url

# Email Configuration - Brevo
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=96d92f001@smtp-brevo.com
MAIL_PASSWORD=JrbVFGpHhgynKMOQ
MAIL_DEFAULT_SENDER=Mentora <noreply@mentora.com>

# Email Settings
MAIL_SUPPRESS_SEND=false
EMAIL_CONFIRMATION_SALT=mentora-production-salt-$(date +%s)
EOF

echo "✅ .env файл создан для production"

# Устанавливаем права доступа
chmod 600 .env
echo "✅ Права доступа установлены (600)"

# Перезапускаем сервис (замените на ваш сервис)
echo "🔄 Перезапуск приложения..."
systemctl restart your-app-service

echo "✅ Готово! Проверьте статус: systemctl status your-app-service"
