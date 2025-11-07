#!/usr/bin/env python3
"""
Тестовый скрипт для проверки отправки email с временным паролем.
"""

import os
import sys
from datetime import datetime, timezone

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User

def test_password_reset_email():
    """Тестирует отправку email с временным паролем"""
    
    with app.app_context():
        try:
            print("📧 Тестирование отправки email с временным паролем...")
            
            # Находим первого пользователя для тестирования
            user = User.query.first()
            
            if not user:
                print("❌ Нет пользователей в базе данных для тестирования")
                return False
            
            print(f"👤 Тестируем с пользователем: {user.email} ({user.first_name} {user.last_name})")
            
            # Генерируем тестовый пароль
            import secrets
            import string
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            
            print(f"🔑 Тестовый пароль: {temp_password}")
            
            # Отправляем email
            from utils.email_service import send_admin_password_reset_email
            
            print("📤 Отправляем email...")
            email_sent = send_admin_password_reset_email(user, temp_password, 'en')
            
            if email_sent:
                print("✅ Email отправлен успешно!")
                print(f"📧 Получатель: {user.email}")
                print(f"🔑 Пароль в письме: {temp_password}")
                print(f"🌐 Язык: English")
            else:
                print("❌ Не удалось отправить email")
            
            return email_sent
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def test_template_rendering():
    """Тестирует рендеринг шаблонов email"""
    
    with app.app_context():
        try:
            print("🎨 Тестирование рендеринга шаблонов...")
            
            # Создаем тестового пользователя
            test_user = type('User', (), {
                'first_name': 'Тест',
                'last_name': 'Пользователь',
                'email': 'test@example.com'
            })()
            
            temp_password = 'TestPassword123'
            login_url = 'https://bigmentor.nl/auth/login'
            
            # Тестируем HTML шаблон
            try:
                from flask import render_template_string
                with open('templates/emails/password_reset_admin_en.html', 'r', encoding='utf-8') as f:
                    html_template = f.read()
                html_body = render_template_string(html_template, 
                                                 user=test_user, 
                                                 temp_password=temp_password,
                                                 login_url=login_url)
                print("✅ HTML шаблон рендерится корректно")
            except Exception as e:
                print(f"❌ Ошибка рендеринга HTML шаблона: {str(e)}")
                return False
            
            # Тестируем текстовый шаблон
            try:
                with open('templates/emails/password_reset_admin_en.txt', 'r', encoding='utf-8') as f:
                    text_template = f.read()
                text_body = render_template_string(text_template,
                                                 user=test_user,
                                                 temp_password=temp_password,
                                                 login_url=login_url)
                print("✅ Текстовый шаблон рендерится корректно")
            except Exception as e:
                print(f"❌ Ошибка рендеринга текстового шаблона: {str(e)}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании шаблонов: {str(e)}")
            return False

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--template':
        success = test_template_rendering()
    else:
        print("🧪 Тестирование отправки email с временным паролем")
        print("=" * 50)
        print()
        
        # Сначала тестируем шаблоны
        print("1. Тестирование шаблонов...")
        template_success = test_template_rendering()
        
        if template_success:
            print("\n2. Тестирование отправки email...")
            email_success = test_password_reset_email()
            
            if email_success:
                print("\n🎉 Все тесты прошли успешно!")
                print("📧 Email с временным паролем отправлен")
            else:
                print("\n❌ Тест отправки email не прошел")
        else:
            print("\n❌ Тест шаблонов не прошел")
