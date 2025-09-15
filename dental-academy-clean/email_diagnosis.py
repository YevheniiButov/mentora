#!/usr/bin/env python3
"""
Диагностика проблем с email при регистрации
Проверяем каждый шаг процесса отправки
"""

import os
import sys

# Устанавливаем переменные окружения
os.environ['MAIL_SERVER'] = 'smtp-relay.brevo.com'
os.environ['MAIL_PORT'] = '587'
os.environ['MAIL_USE_TLS'] = 'True'
os.environ['MAIL_USERNAME'] = '96d92f002@smtp-brevo.com'
os.environ['MAIL_PASSWORD'] = 'AdHL3pP0rkRt1S8N'
os.environ['MAIL_DEFAULT_SENDER'] = 'Mentora <noreply@mentora.com.in>'
os.environ['FLASK_ENV'] = 'development'

def step1_check_imports():
    """Шаг 1: Проверяем импорты"""
    print("📋 Шаг 1: Проверка импортов")
    print("-" * 40)
    
    try:
        from app import app
        print("✅ app импортирован")
        
        from extensions import db, mail
        print("✅ extensions импортированы")
        
        from models import User
        print("✅ models импортированы")
        
        from utils.email_service import send_email_confirmation
        print("✅ email_service импортирован")
        
        from flask_mail import Message
        print("✅ Flask-Mail импортирован")
        
        return True, (app, db, mail, User, send_email_confirmation, Message)
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False, None

def step2_check_config(app):
    """Шаг 2: Проверяем конфигурацию"""
    print("\n📋 Шаг 2: Проверка конфигурации")
    print("-" * 40)
    
    with app.app_context():
        config_items = [
            ('MAIL_SERVER', app.config.get('MAIL_SERVER')),
            ('MAIL_PORT', app.config.get('MAIL_PORT')),
            ('MAIL_USE_TLS', app.config.get('MAIL_USE_TLS')),
            ('MAIL_USE_SSL', app.config.get('MAIL_USE_SSL')),
            ('MAIL_USERNAME', app.config.get('MAIL_USERNAME')),
            ('MAIL_PASSWORD', '***' if app.config.get('MAIL_PASSWORD') else 'НЕ УСТАНОВЛЕНО'),
            ('MAIL_DEFAULT_SENDER', app.config.get('MAIL_DEFAULT_SENDER')),
            ('MAIL_SUPPRESS_SEND', app.config.get('MAIL_SUPPRESS_SEND')),
        ]
        
        all_ok = True
        for key, value in config_items:
            if key == 'MAIL_PASSWORD':
                status = "✅" if app.config.get('MAIL_PASSWORD') else "❌"
            elif value is None:
                status = "❌"
                all_ok = False
            else:
                status = "✅"
            
            print(f"{status} {key}: {value}")
        
        return all_ok

def step3_test_templates(app):
    """Шаг 3: Тестируем шаблоны email"""
    print("\n📋 Шаг 3: Проверка шаблонов email")
    print("-" * 40)
    
    with app.app_context():
        from flask import render_template
        
        test_user = type('User', (), {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com'
        })()
        
        confirmation_url = 'http://localhost:5000/auth/confirm-email/test-token'
        unsubscribe_url = 'http://localhost:5000/auth/unsubscribe/1'
        privacy_policy_url = 'http://localhost:5000/privacy'
        
        try:
            html_content = render_template('emails/confirm_email.html',
                                         user=test_user,
                                         confirmation_url=confirmation_url,
                                         unsubscribe_url=unsubscribe_url,
                                         privacy_policy_url=privacy_policy_url)
            print(f"✅ HTML шаблон: {len(html_content)} символов")
            html_ok = True
        except Exception as e:
            print(f"❌ HTML шаблон: {e}")
            html_ok = False
        
        try:
            text_content = render_template('emails/confirm_email.txt',
                                         user=test_user,
                                         confirmation_url=confirmation_url,
                                         unsubscribe_url=unsubscribe_url,
                                         privacy_policy_url=privacy_policy_url)
            print(f"✅ Текстовый шаблон: {len(text_content)} символов")
            text_ok = True
        except Exception as e:
            print(f"❌ Текстовый шаблон: {e}")
            text_ok = False
        
        return html_ok and text_ok

def step4_test_mail_object(app, mail):
    """Шаг 4: Тестируем объект Mail"""
    print("\n📋 Шаг 4: Проверка объекта Mail")
    print("-" * 40)
    
    with app.app_context():
        try:
            print(f"✅ Mail объект создан: {mail is not None}")
            print(f"✅ Mail привязан к app: {hasattr(mail, 'app') and mail.app is not None}")
            return True
        except Exception as e:
            print(f"❌ Ошибка Mail объекта: {e}")
            return False

def step5_test_message_creation(app, mail, Message):
    """Шаг 5: Тестируем создание сообщения"""
    print("\n📋 Шаг 5: Создание тестового сообщения")
    print("-" * 40)
    
    with app.app_context():
        try:
            msg = Message(
                subject='Test Email - Mentora',
                recipients=['test@example.com'],
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            
            msg.body = "Тестовое сообщение"
            msg.html = "<h1>Тестовое сообщение</h1>"
            
            print("✅ Сообщение создано успешно")
            print(f"📧 Тема: {msg.subject}")
            print(f"📨 Получатель: {msg.recipients}")
            print(f"👤 Отправитель: {msg.sender}")
            
            return True, msg
            
        except Exception as e:
            print(f"❌ Ошибка создания сообщения: {e}")
            return False, None

def step6_test_smtp_connection():
    """Шаг 6: Прямое тестирование SMTP"""
    print("\n📋 Шаг 6: Прямое SMTP подключение")
    print("-" * 40)
    
    import smtplib
    
    try:
        server = smtplib.SMTP('smtp-relay.brevo.com', 587)
        server.starttls()
        server.login('96d92f002@smtp-brevo.com', 'AdHL3pP0rkRt1S8N')
        print("✅ SMTP подключение успешно")
        server.quit()
        return True
    except Exception as e:
        print(f"❌ SMTP ошибка: {e}")
        return False

def step7_test_email_service(app, send_email_confirmation, User):
    """Шаг 7: Тестируем email service"""
    print("\n📋 Шаг 7: Тестирование email service")
    print("-" * 40)
    
    with app.app_context():
        # Создаем тестового пользователя (без сохранения в БД)
        test_user = User(
            email='test.diagnosis@example.com',
            first_name='Test',
            last_name='Diagnosis'
        )
        test_user.id = 999  # Фейковый ID
        
        # Генерируем тестовый токен
        test_token = 'test-token-123'
        
        try:
            # Переключаем в режим консоли для теста
            original_suppress = app.config.get('MAIL_SUPPRESS_SEND')
            app.config['MAIL_SUPPRESS_SEND'] = True
            
            result = send_email_confirmation(test_user, test_token)
            
            # Возвращаем оригинальное значение
            app.config['MAIL_SUPPRESS_SEND'] = original_suppress
            
            if result:
                print("✅ Email service работает")
                return True
            else:
                print("❌ Email service вернул False")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка email service: {e}")
            return False

def run_diagnosis():
    """Запускаем полную диагностику"""
    print("🦷 Mentora Email Diagnosis")
    print("=" * 50)
    print("Проверяем каждый шаг процесса отправки email\n")
    
    # Шаг 1: Импорты
    imports_ok, modules = step1_check_imports()
    if not imports_ok:
        print("❌ Диагностика остановлена из-за ошибок импорта")
        return
    
    app, db, mail, User, send_email_confirmation, Message = modules
    
    # Шаг 2: Конфигурация
    config_ok = step2_check_config(app)
    
    # Шаг 3: Шаблоны
    templates_ok = step3_test_templates(app)
    
    # Шаг 4: Mail объект
    mail_ok = step4_test_mail_object(app, mail)
    
    # Шаг 5: Создание сообщения
    message_ok, test_msg = step5_test_message_creation(app, mail, Message)
    
    # Шаг 6: SMTP
    smtp_ok = step6_test_smtp_connection()
    
    # Шаг 7: Email service
    service_ok = step7_test_email_service(app, send_email_confirmation, User)
    
    # Итоги
    print("\n📋 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ")
    print("=" * 50)
    
    results = [
        ("Импорты", imports_ok),
        ("Конфигурация", config_ok),
        ("Шаблоны", templates_ok),
        ("Mail объект", mail_ok),
        ("Создание сообщения", message_ok),
        ("SMTP подключение", smtp_ok),
        ("Email service", service_ok)
    ]
    
    all_ok = True
    for step, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {step}")
        if not result:
            all_ok = False
    
    print("\n📝 РЕКОМЕНДАЦИИ:")
    print("-" * 30)
    
    if not config_ok:
        print("🔧 Проверьте переменные окружения в .env файле")
    
    if not templates_ok:
        print("🎨 Проверьте шаблоны emails в templates/emails/")
    
    if not smtp_ok:
        print("📧 Проверьте настройки SMTP в Brevo панели")
    
    if not service_ok:
        print("⚙️ Проверьте логику в utils/email_service.py")
    
    if all_ok:
        print("🎉 Все проверки прошли успешно!")
        print("📧 Email отправка должна работать корректно")
        print("\n💡 Если письма все еще не приходят:")
        print("   1. Проверьте спам-папку")
        print("   2. Убедитесь что MAIL_SUPPRESS_SEND=false в продакшене")
        print("   3. Проверьте логи Render.com")
    else:
        print("❌ Найдены проблемы, которые нужно исправить")

if __name__ == '__main__':
    try:
        run_diagnosis()
    except Exception as e:
        print(f"\n💥 Критическая ошибка диагностики: {e}")
        import traceback
        print(f"📋 Трейсбек:\n{traceback.format_exc()}")
