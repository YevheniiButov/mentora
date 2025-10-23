#!/usr/bin/env python3
"""
Тест отправки welcome email
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User
from utils.email_service import send_welcome_email

def test_welcome_email():
    """Тестируем отправку welcome email"""
    with app.app_context():
        print("🔍 ДИАГНОСТИКА WELCOME EMAIL")
        print("=" * 50)
        
        # 1. Проверяем настройки email
        print("\n📧 EMAIL SETTINGS:")
        print(f"   EMAIL_PROVIDER: {app.config.get('EMAIL_PROVIDER')}")
        print(f"   MAIL_SUPPRESS_SEND: {app.config.get('MAIL_SUPPRESS_SEND')}")
        print(f"   MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"   MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"   MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"   MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        print(f"   MAIL_PASSWORD: {'SET' if app.config.get('MAIL_PASSWORD') else 'NOT SET'}")
        print(f"   MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        print(f"   BASE_URL: {app.config.get('BASE_URL')}")
        
        # 2. Проверяем Resend настройки
        if app.config.get('EMAIL_PROVIDER') == 'resend':
            print(f"\n🔑 RESEND SETTINGS:")
            print(f"   RESEND_API_KEY: {'SET' if app.config.get('RESEND_API_KEY') else 'NOT SET'}")
            print(f"   RESEND_FROM_EMAIL: {app.config.get('RESEND_FROM_EMAIL')}")
        
        # 3. Ищем тестового пользователя
        print(f"\n👤 ПОИСК ТЕСТОВОГО ПОЛЬЗОВАТЕЛЯ:")
        test_email = input("Введите email для тестирования (или нажмите Enter для поиска последнего пользователя): ").strip()
        
        if not test_email:
            # Ищем последнего пользователя
            user = User.query.order_by(User.id.desc()).first()
            if user:
                test_email = user.email
                print(f"   Найден пользователь: {user.get_display_name()} ({user.email})")
            else:
                print("   ❌ Пользователи не найдены!")
                return
        else:
            user = User.query.filter_by(email=test_email).first()
            if not user:
                print(f"   ❌ Пользователь с email {test_email} не найден!")
                return
            print(f"   Найден пользователь: {user.get_display_name()} ({user.email})")
        
        # 4. Проверяем статус пользователя
        print(f"\n📊 СТАТУС ПОЛЬЗОВАТЕЛЯ:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.get_display_name()}")
        print(f"   Active: {user.is_active}")
        print(f"   Deleted: {user.is_deleted}")
        print(f"   Email Confirmed: {user.email_confirmed}")
        print(f"   Created: {user.created_at}")
        
        # 5. Тестируем отправку welcome email
        print(f"\n📧 ТЕСТИРОВАНИЕ WELCOME EMAIL:")
        try:
            result = send_welcome_email(user)
            if result:
                print("   ✅ Welcome email отправлен успешно!")
            else:
                print("   ❌ Ошибка отправки welcome email!")
        except Exception as e:
            print(f"   ❌ Ошибка: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 6. Проверяем логи
        print(f"\n📝 ПРОВЕРКА ЛОГОВ:")
        print("   Проверьте консоль на наличие сообщений о отправке email")
        print("   Ищите сообщения вида: '=== WELCOME EMAIL START ==='")

if __name__ == "__main__":
    test_welcome_email()
