#!/usr/bin/env python3
"""
Диагностика функции send_email_confirmation
Проверяем что происходит именно при регистрации
"""

import os
import sys

# Настройки как в продакшене
os.environ['FLASK_ENV'] = 'production'
os.environ['MAIL_SUPPRESS_SEND'] = 'false'
os.environ['MAIL_SERVER'] = 'smtp-relay.brevo.com'
os.environ['MAIL_PORT'] = '587'
os.environ['MAIL_USE_TLS'] = 'True'
os.environ['MAIL_USERNAME'] = '96d92f002@smtp-brevo.com'
os.environ['MAIL_PASSWORD'] = 'AdHL3pP0rkRt1S8N'
os.environ['MAIL_DEFAULT_SENDER'] = 'Mentora <noreply@mentora.com.in>'

try:
    from app import app
    from extensions import db, mail
    from models import User
    from utils.email_service import send_email_confirmation
    from flask_mail import Message
    
    def test_direct_mail():
        """Тест 1: Прямая отправка через Flask-Mail (как в test-email)"""
        print("🧪 Тест 1: Прямая отправка (как на test-email странице)")
        print("-" * 60)
        
        with app.app_context():
            try:
                msg = Message(
                    subject='🦷 Direct Test Email',
                    recipients=['xapstom@gmail.com'],
                    sender=app.config['MAIL_DEFAULT_SENDER']
                )
                
                msg.body = "Прямой тест email через Flask-Mail"
                msg.html = "<h1>Прямой тест email через Flask-Mail</h1>"
                
                print(f"✅ Создание сообщения: OK")
                print(f"📧 Отправитель: {msg.sender}")
                print(f"📨 Получатель: {msg.recipients}")
                
                mail.send(msg)
                print("✅ Отправка успешна!")
                return True
                
            except Exception as e:
                print(f"❌ Ошибка прямой отправки: {e}")
                return False
    
    def test_email_confirmation():
        """Тест 2: Отправка через send_email_confirmation"""
        print("\n🧪 Тест 2: Отправка через send_email_confirmation")
        print("-" * 60)
        
        with app.app_context():
            # Создаем тестового пользователя
            test_user = User(
                email='test.confirmation@example.com',
                first_name='Test',
                last_name='Confirmation'
            )
            test_user.id = 999  # Фейковый ID для теста
            
            test_token = 'test-confirmation-token-123'
            
            print(f"👤 Тестовый пользователь: {test_user.first_name} {test_user.last_name}")
            print(f"📧 Email: {test_user.email}")
            print(f"🔑 Токен: {test_token}")
            
            try:
                result = send_email_confirmation(test_user, test_token)
                
                if result:
                    print("✅ send_email_confirmation вернул True")
                    return True
                else:
                    print("❌ send_email_confirmation вернул False")
                    return False
                    
            except Exception as e:
                print(f"❌ Ошибка send_email_confirmation: {e}")
                import traceback
                print(f"📋 Трейсбек: {traceback.format_exc()}")
                return False
    
    def check_config_differences():
        """Тест 3: Проверяем различия в конфигурации"""
        print("\n🧪 Тест 3: Анализ конфигурации")
        print("-" * 60)
        
        with app.app_context():
            config_items = [
                'MAIL_SERVER',
                'MAIL_PORT', 
                'MAIL_USE_TLS',
                'MAIL_USE_SSL',
                'MAIL_USERNAME',
                'MAIL_PASSWORD',
                'MAIL_DEFAULT_SENDER',
                'MAIL_SUPPRESS_SEND',
                'FLASK_ENV',
                'BASE_URL'
            ]
            
            print("📋 Текущая конфигурация:")
            for item in config_items:
                value = app.config.get(item)
                if item == 'MAIL_PASSWORD':
                    value = '***' if value else 'НЕ УСТАНОВЛЕНО'
                print(f"   {item}: {value}")
            
            # Проверяем специфичные проблемы
            print("\n🔍 Анализ потенциальных проблем:")
            
            suppress = app.config.get('MAIL_SUPPRESS_SEND')
            if suppress:
                print(f"⚠️ MAIL_SUPPRESS_SEND = {suppress} (должно быть False)")
            else:
                print(f"✅ MAIL_SUPPRESS_SEND = {suppress}")
            
            sender = app.config.get('MAIL_DEFAULT_SENDER')
            if sender and 'mentora.com.in' in sender:
                print(f"✅ MAIL_DEFAULT_SENDER использует правильный домен")
            else:
                print(f"⚠️ MAIL_DEFAULT_SENDER: {sender}")
            
            base_url = app.config.get('BASE_URL')
            print(f"🌐 BASE_URL: {base_url}")
    
    def test_template_rendering():
        """Тест 4: Проверяем рендеринг шаблонов"""
        print("\n🧪 Тест 4: Рендеринг email шаблонов")
        print("-" * 60)
        
        with app.app_context():
            from flask import render_template
            
            test_user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User'
            )
            test_user.id = 1
            
            confirmation_url = 'https://mentora.com.in/auth/confirm-email/test-token'
            unsubscribe_url = 'https://mentora.com.in/auth/unsubscribe/1'
            privacy_policy_url = 'https://mentora.com.in/privacy'
            
            try:
                html_content = render_template('emails/confirm_email.html',
                                             user=test_user,
                                             confirmation_url=confirmation_url,
                                             unsubscribe_url=unsubscribe_url,
                                             privacy_policy_url=privacy_policy_url)
                print(f"✅ HTML шаблон: {len(html_content)} символов")
                
                text_content = render_template('emails/confirm_email.txt',
                                             user=test_user,
                                             confirmation_url=confirmation_url,
                                             unsubscribe_url=unsubscribe_url,
                                             privacy_policy_url=privacy_policy_url)
                print(f"✅ Текстовый шаблон: {len(text_content)} символов")
                return True
                
            except Exception as e:
                print(f"❌ Ошибка рендеринга шаблонов: {e}")
                return False
    
    def run_comprehensive_test():
        """Запускаем комплексный тест"""
        print("🦷 Mentora Email Confirmation Diagnosis")
        print("=" * 60)
        print("Сравниваем работающую test-email с регистрацией")
        print()
        
        # Выполняем все тесты
        test1_result = test_direct_mail()
        test2_result = test_email_confirmation()
        test4_result = test_template_rendering()
        
        check_config_differences()
        
        print("\n📋 РЕЗУЛЬТАТЫ СРАВНЕНИЯ:")
        print("=" * 40)
        print(f"✅ Прямая отправка (test-email): {'РАБОТАЕТ' if test1_result else 'НЕ РАБОТАЕТ'}")
        print(f"{'✅' if test2_result else '❌'} send_email_confirmation: {'РАБОТАЕТ' if test2_result else 'НЕ РАБОТАЕТ'}")
        print(f"✅ Рендеринг шаблонов: {'РАБОТАЕТ' if test4_result else 'НЕ РАБОТАЕТ'}")
        
        if test1_result and not test2_result:
            print("\n🎯 ПРОБЛЕМА НАЙДЕНА!")
            print("📧 Прямая отправка работает, но send_email_confirmation НЕ РАБОТАЕТ")
            print("\n🔍 Возможные причины:")
            print("1. Ошибка в логике send_email_confirmation")
            print("2. Проблема с рендерингом email шаблонов")
            print("3. Неправильная обработка исключений")
            print("4. Проблема с URL генерацией")
        elif test1_result and test2_result:
            print("\n🎉 ОБЕ ФУНКЦИИ РАБОТАЮТ!")
            print("📧 Проблема может быть в другом месте процесса регистрации")
        
        return test1_result, test2_result
    
    if __name__ == '__main__':
        run_comprehensive_test()

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("🔍 Убедитесь, что скрипт запускается из корневой директории проекта")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
    import traceback
    print(f"📋 Трейсбек: {traceback.format_exc()}")
