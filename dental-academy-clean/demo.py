#!/usr/bin/env python3
"""
Dental Academy - Demo Registration System
Простой запуск демо-версии
"""

import os
from app import app

if __name__ == '__main__':
    # Устанавливаем демо-режим для email
    os.environ['MAIL_SUPPRESS_SEND'] = 'true'
    os.environ['FLASK_ENV'] = 'development'
    
    port = int(os.environ.get('PORT', 5002))
    
    print("🦷 Dental Academy - Demo Registration System")
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




