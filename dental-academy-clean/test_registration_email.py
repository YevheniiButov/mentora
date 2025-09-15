#!/usr/bin/env python3
"""
Тестовый скрипт регистрации с email отправкой
Проверяет полный процесс регистрации включая отправку подтверждения
"""

import os
import sys
from datetime import datetime

# Устанавливаем правильные переменные окружения
os.environ['MAIL_SERVER'] = 'smtp-relay.brevo.com'
os.environ['MAIL_PORT'] = '587'
os.environ['MAIL_USE_TLS'] = 'True'
os.environ['MAIL_USERNAME'] = '96d92f002@smtp-brevo.com'
os.environ['MAIL_PASSWORD'] = 'AdHL3pP0rkRt1S8N'
os.environ['MAIL_DEFAULT_SENDER'] = 'Mentora <noreply@mentora.com.in>'
os.environ['FLASK_ENV'] = 'development'
os.environ['MAIL_SUPPRESS_SEND'] = 'False'  # Отключаем подавление для теста

try:
    from app import app
    from extensions import db, mail
    from models import User
    from utils.email_service import send_email_confirmation
    
    def test_registration_flow():
        """Тестируем полный процесс регистрации"""
        print("🧪 Тестирование полного процесса регистрации")
        print("=" * 60)
        
        with app.app_context():
            # Удаляем тестового пользователя если существует
            test_email = 'test.registration@example.com'
            existing_user = User.query.filter_by(email=test_email).first()
            if existing_user:
                print(f"🗑️ Удаляем существующего тестового пользователя: {test_email}")
                db.session.delete(existing_user)
                db.session.commit()
            
            # Создаем нового пользователя
            print(f"👤 Создаем нового пользователя: {test_email}")
            user = User(
                email=test_email,
                first_name='Test',
                last_name='User',
                nationality='NL',
                profession='dentist',
                dutch_level='B2',
                legal_status='non_eu',
                university_name='Test University',
                degree_type='bachelor',
                study_start_year=2020,
                study_end_year=2024,
                study_country='NL',
                required_consents=True,
                digital_signature='Test User',
                registration_completed=True,
                is_active=True
            )
            
            # Устанавливаем пароль
            user.set_password('TestPassword123')
            
            # Генерируем токен подтверждения email
            print("🔑 Генерируем токен подтверждения email...")
            confirmation_token = user.generate_email_confirmation_token()
            
            # Сохраняем пользователя
            db.session.add(user)
            db.session.commit()
            
            print(f"✅ Пользователь создан с ID: {user.id}")
            print(f"📧 Email: {user.email}")
            print(f"🔑 Токен: {confirmation_token[:20]}...")
            
            # Проверяем email конфигурацию
            print("\n📧 Конфигурация email:")
            print("=" * 40)
            print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
            print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
            print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
            print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
            print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
            print(f"MAIL_SUPPRESS_SEND: {app.config.get('MAIL_SUPPRESS_SEND')}")
            
            # Тестируем отправку email
            print("\n📬 Отправляем email подтверждения...")
            email_sent = send_email_confirmation(user, confirmation_token)
            
            if email_sent:
                print("✅ Email отправлен успешно!")
                print(f"📨 Проверьте почтовый ящик: {user.email}")
                
                # Генерируем ссылку подтверждения
                base_url = app.config.get('BASE_URL', 'http://localhost:5000')
                confirmation_url = f"{base_url}/auth/confirm-email/{confirmation_token}"
                print(f"🔗 Ссылка подтверждения: {confirmation_url}")
                
                return True
            else:
                print("❌ Ошибка отправки email!")
                return False
    
    def test_email_template():
        """Тестируем шаблон email"""
        print("\n🎨 Тестирование шаблона email")
        print("=" * 40)
        
        try:
            from flask import render_template
            
            test_user = {
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com'
            }
            
            confirmation_url = 'http://localhost:5000/auth/confirm-email/test-token'
            
            # Пробуем рендерить HTML шаблон
            try:
                html_content = render_template('emails/confirm_email.html', 
                                             user=test_user, 
                                             confirmation_url=confirmation_url)
                print("✅ HTML шаблон загружен успешно")
                print(f"📄 Размер HTML: {len(html_content)} символов")
            except Exception as e:
                print(f"❌ Ошибка HTML шаблона: {e}")
                print("ℹ️ Будет использован fallback HTML")
            
            # Пробуем рендерить текстовый шаблон
            try:
                text_content = render_template('emails/confirm_email.txt', 
                                             user=test_user, 
                                             confirmation_url=confirmation_url)
                print("✅ Текстовый шаблон загружен успешно")
                print(f"📄 Размер текста: {len(text_content)} символов")
            except Exception as e:
                print(f"❌ Ошибка текстового шаблона: {e}")
                print("ℹ️ Будет использован fallback текст")
                
        except Exception as e:
            print(f"❌ Общая ошибка шаблонов: {e}")
    
    def run_full_test():
        """Запускаем полный тест"""
        print("🦷 Mentora Registration Email Test")
        print("=" * 60)
        print(f"🕐 Время запуска: {datetime.now()}")
        print("=" * 60)
        
        # Тестируем шаблоны
        test_email_template()
        
        # Тестируем полный процесс
        registration_success = test_registration_flow()
        
        print("\n📋 Результаты тестирования:")
        print("=" * 40)
        print(f"✅ Регистрация: {'УСПЕШНО' if registration_success else 'ОШИБКА'}")
        
        if registration_success:
            print("\n🎉 Тест завершен успешно!")
            print("📧 Проверьте email: test.registration@example.com")
            print("🔗 Или используйте ссылку подтверждения выше")
        else:
            print("\n❌ Тест не прошел")
            print("🔍 Проверьте настройки email и логи")
    
    if __name__ == '__main__':
        run_full_test()

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("🔍 Убедитесь, что вы запускаете скрипт из корневой директории проекта")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
    import traceback
    print(f"📋 Трейсбек: {traceback.format_exc()}")
