#!/usr/bin/env python3
"""
Mentora - Demo Registration System
Простой запуск демо-версии
"""

import os
from app import app

if __name__ == '__main__':
    # Устанавливаем демо-режим для email (отключено для тестирования)
    # os.environ['MAIL_SUPPRESS_SEND'] = 'true'
    
    # Email настройки для тестирования
    os.environ['MAIL_SERVER'] = 'smtp-relay.brevo.com'
    os.environ['MAIL_PORT'] = '587'
    os.environ['MAIL_USE_TLS'] = 'True'
    os.environ['MAIL_USERNAME'] = '96d92f002@smtp-brevo.com'  # Новый логин
    os.environ['MAIL_PASSWORD'] = 'AdHL3pP0rkRt1S8N'  # Новый master password
    os.environ['MAIL_DEFAULT_SENDER'] = 'noreply@mentora.com.in'
    os.environ['MAIL_SUPPRESS_SEND'] = 'false'  # Включаем отправку email
    os.environ['FLASK_ENV'] = 'development'
    
    port = int(os.environ.get('PORT', 5002))
    
    print("Mentora - Registration System")
    print("=" * 50)
    print("✅ Расширенная форма регистрации")
    print("✅ Опциональная загрузка документов")
    print("✅ Расширенные согласия на данные")
    print("=" * 50)
    print(f"🚀 Запуск на порту: {port}")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"📝 Регистрация: http://localhost:{port}/auth/register")
    print(f"🔐 Вход: http://localhost:{port}/auth/login")
    print("=" * 50)
    print("Нажмите Ctrl+C для остановки")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )




