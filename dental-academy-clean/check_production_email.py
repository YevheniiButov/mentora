#!/usr/bin/env python3
"""
Диагностика настроек email в production
"""

import os
import sys
from flask import Flask
from config import Config

def check_email_config():
    """Проверяем настройки email"""
    print("🔍 ДИАГНОСТИКА НАСТРОЕК EMAIL")
    print("=" * 50)
    
    # Создаем Flask app для проверки конфигурации
    app = Flask(__name__)
    app.config.from_object(Config)
    
    print("📧 НАСТРОЙКИ EMAIL:")
    print(f"   MAIL_SERVER: {app.config.get('MAIL_SERVER', 'НЕ УСТАНОВЛЕН')}")
    print(f"   MAIL_PORT: {app.config.get('MAIL_PORT', 'НЕ УСТАНОВЛЕН')}")
    print(f"   MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS', 'НЕ УСТАНОВЛЕН')}")
    print(f"   MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL', 'НЕ УСТАНОВЛЕН')}")
    print(f"   MAIL_USERNAME: {app.config.get('MAIL_USERNAME', 'НЕ УСТАНОВЛЕН')}")
    print(f"   MAIL_PASSWORD: {'УСТАНОВЛЕН' if app.config.get('MAIL_PASSWORD') else 'НЕ УСТАНОВЛЕН'}")
    print(f"   MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER', 'НЕ УСТАНОВЛЕН')}")
    print(f"   MAIL_SUPPRESS_SEND: {app.config.get('MAIL_SUPPRESS_SEND', 'НЕ УСТАНОВЛЕН')}")
    
    print("\n🌍 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ:")
    print(f"   MAIL_SERVER: {os.environ.get('MAIL_SERVER', 'НЕ УСТАНОВЛЕН')}")
    print(f"   MAIL_PORT: {os.environ.get('MAIL_PORT', 'НЕ УСТАНОВЛЕН')}")
    print(f"   MAIL_USE_TLS: {os.environ.get('MAIL_USE_TLS', 'НЕ УСТАНОВЛЕН')}")
    print(f"   MAIL_USE_SSL: {os.environ.get('MAIL_USE_SSL', 'НЕ УСТАНОВЛЕН')}")
    print(f"   MAIL_USERNAME: {os.environ.get('MAIL_USERNAME', 'НЕ УСТАНОВЛЕН')}")
    print(f"   MAIL_PASSWORD: {'УСТАНОВЛЕН' if os.environ.get('MAIL_PASSWORD') else 'НЕ УСТАНОВЛЕН'}")
    print(f"   MAIL_DEFAULT_SENDER: {os.environ.get('MAIL_DEFAULT_SENDER', 'НЕ УСТАНОВЛЕН')}")
    print(f"   MAIL_SUPPRESS_SEND: {os.environ.get('MAIL_SUPPRESS_SEND', 'НЕ УСТАНОВЛЕН')}")
    
    print("\n🔧 АНАЛИЗ ПРОБЛЕМ:")
    
    # Проверяем MAIL_SUPPRESS_SEND
    suppress_send = app.config.get('MAIL_SUPPRESS_SEND', False)
    if suppress_send:
        print("   ❌ MAIL_SUPPRESS_SEND = True - Email отключен!")
        print("   💡 Решение: Установите MAIL_SUPPRESS_SEND=false в Render")
    else:
        print("   ✅ MAIL_SUPPRESS_SEND = False - Email включен")
    
    # Проверяем настройки сервера
    mail_server = app.config.get('MAIL_SERVER')
    if not mail_server:
        print("   ❌ MAIL_SERVER не установлен")
    elif 'brevo' in mail_server.lower():
        print("   ⚠️  Используется Brevo (smtp-relay.brevo.com)")
        print("   💡 Убедитесь, что учетные данные Brevo корректны")
    elif 'mailersend' in mail_server.lower():
        print("   ⚠️  Используется MailerSend (smtp.mailersend.net)")
        print("   💡 Убедитесь, что учетные данные MailerSend корректны")
    else:
        print(f"   ⚠️  Неизвестный email провайдер: {mail_server}")
    
    # Проверяем обязательные поля
    required_fields = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD']
    missing_fields = []
    for field in required_fields:
        if not app.config.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        print(f"   ❌ Отсутствуют обязательные поля: {', '.join(missing_fields)}")
    else:
        print("   ✅ Все обязательные поля настроены")
    
    print("\n📋 РЕКОМЕНДАЦИИ:")
    if suppress_send:
        print("   1. В Render Dashboard → Environment Variables")
        print("   2. Добавьте/обновите: MAIL_SUPPRESS_SEND = false")
        print("   3. Сохраните и перезапустите сервис")
    
    if 'brevo' in (mail_server or '').lower():
        print("   4. Убедитесь, что учетные данные Brevo корректны:")
        print("      - MAIL_USERNAME должен быть полным email")
        print("      - MAIL_PASSWORD должен быть SMTP ключом Brevo")
        print("      - MAIL_DEFAULT_SENDER должен быть подтвержденным доменом")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    check_email_config()
