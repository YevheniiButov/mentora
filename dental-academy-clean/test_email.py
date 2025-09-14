#!/usr/bin/env python3
"""
Email Test Script for Mentora
Тестирование отправки email с настройками Brevo
"""

import os
import sys
from datetime import datetime

# Устанавливаем переменные окружения из Render
os.environ['MAIL_SERVER'] = 'smtp-relay.brevo.com'
os.environ['MAIL_PORT'] = '587'
os.environ['MAIL_USE_TLS'] = 'True'
os.environ['MAIL_USERNAME'] = '96d92f002@smtp-brevo.com'  # Новые данные Brevo
os.environ['MAIL_PASSWORD'] = 'AdHL3pP0rkRt1S8N'
os.environ['MAIL_DEFAULT_SENDER'] = 'noreply@mentora.com.in'
os.environ['FLASK_ENV'] = 'development'

# Отключаем подавление отправки для теста
os.environ['MAIL_SUPPRESS_SEND'] = 'False'

try:
    from app import app
    from extensions import mail
    from flask_mail import Message
    
    def test_email_configuration():
        """Тестирование конфигурации email"""
        print("🔧 Testing Email Configuration")
        print("=" * 50)
        
        with app.app_context():
            print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
            print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
            print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
            print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
            print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
            print(f"MAIL_SUPPRESS_SEND: {app.config.get('MAIL_SUPPRESS_SEND')}")
            print("=" * 50)
    
    def send_test_email():
        """Отправка тестового email"""
        print("📧 Sending Test Email...")
        
        with app.app_context():
            try:
                msg = Message(
                    subject='Mentora Test Email',
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=['xapstom@gmail.com']  # Ваш личный email для теста
                )
                
                msg.body = f"""
Тестовое письмо от Mentora

Время отправки: {datetime.now()}
Сервер: {app.config.get('MAIL_SERVER')}
Порт: {app.config.get('MAIL_PORT')}
Пользователь: {app.config.get('MAIL_USERNAME')}

Если вы получили это письмо, значит настройка email работает корректно!

С уважением,
Команда Mentora
                """
                
                msg.html = f"""
                <html>
                <body>
                    <h2>🦷 Mentora - Тестовое письмо</h2>
                    <p>Время отправки: <strong>{datetime.now()}</strong></p>
                    
                    <h3>Настройки SMTP:</h3>
                    <ul>
                        <li>Сервер: {app.config.get('MAIL_SERVER')}</li>
                        <li>Порт: {app.config.get('MAIL_PORT')}</li>
                        <li>Пользователь: {app.config.get('MAIL_USERNAME')}</li>
                    </ul>
                    
                    <p><strong>✅ Если вы получили это письмо, значит настройка email работает корректно!</strong></p>
                    
                    <hr>
                    <p><em>С уважением,<br>Команда Mentora</em></p>
                </body>
                </html>
                """
                
                mail.send(msg)
                print("✅ Тестовое письмо отправлено успешно!")
                return True
                
            except Exception as e:
                print(f"❌ Ошибка при отправке письма: {e}")
                print(f"Тип ошибки: {type(e).__name__}")
                
                # Дополнительная диагностика
                if "authentication" in str(e).lower():
                    print("🔍 Возможная проблема с аутентификацией SMTP")
                    print("Проверьте MAIL_USERNAME и MAIL_PASSWORD")
                elif "connection" in str(e).lower():
                    print("🔍 Возможная проблема с подключением к SMTP серверу")
                    print("Проверьте MAIL_SERVER и MAIL_PORT")
                elif "tls" in str(e).lower() or "ssl" in str(e).lower():
                    print("🔍 Возможная проблема с TLS/SSL")
                    print("Проверьте MAIL_USE_TLS и MAIL_USE_SSL")
                
                return False
    
    def test_brevo_api_connection():
        """Тестирование подключения к Brevo API (альтернативный способ)"""
        print("🔄 Testing Brevo API Connection...")
        
        try:
            import requests
            
            # Если у вас есть API ключ Brevo, можно протестировать через API
            # Это базовый тест доступности сервера
            response = requests.get('https://api.brevo.com/v3/account', timeout=10)
            print(f"Brevo API response status: {response.status_code}")
            
            if response.status_code == 401:
                print("✅ Brevo API сервер доступен (получен ответ 401 - нужна авторизация)")
            else:
                print(f"ℹ️ Brevo API ответил со статусом: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка подключения к Brevo API: {e}")
        except ImportError:
            print("ℹ️ Модуль requests не установлен, пропускаем тест API")

    if __name__ == '__main__':
        print("🦷 Mentora Email Test")
        print("=" * 50)
        
        # Тестируем конфигурацию
        test_email_configuration()
        
        # Тестируем подключение к Brevo
        test_brevo_api_connection()
        
        # Отправляем тестовое письмо
        print("\n")
        choice = input("Отправить тестовое письмо? (y/n): ").lower().strip()
        
        if choice in ['y', 'yes', 'да', 'д']:
            recipient = input("Введите email получателя (или нажмите Enter для xapstom@gmail.com): ").strip()
            if recipient:
                # Здесь можно изменить получателя
                pass
            
            success = send_test_email()
            
            if success:
                print("\n✅ Тест завершен успешно!")
                print("Проверьте почтовый ящик получателя.")
            else:
                print("\n❌ Тест не пройден.")
                print("Проверьте настройки SMTP в Render Environment Variables.")
        else:
            print("Тест отменен.")

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что вы запускаете скрипт из правильной директории:")
    print("/Users/evgenijbutov/Desktop/demo/flask-app 2/dental-academy-clean/")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
    print(f"Тип ошибки: {type(e).__name__}")
