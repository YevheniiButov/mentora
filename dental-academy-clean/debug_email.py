#!/usr/bin/env python3
"""
Email Debug Script - простая проверка настроек
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_smtp_direct():
    """Прямое тестирование SMTP без Flask"""
    print("🔧 Direct SMTP Test (без Flask)")
    print("=" * 50)
    
    # Настройки из Render
    smtp_server = 'smtp-relay.brevo.com'
    smtp_port = 587
    username = '96d92f002@smtp-brevo.com'  # Новый логин
    password = 'AdHL3pP0rkRt1S8N'  # Новый master password
    sender_email = 'noreply@mentora.com.in'
    
    print(f"Сервер: {smtp_server}")
    print(f"Порт: {smtp_port}")
    print(f"Пользователь: {username}")
    print(f"Отправитель: {sender_email}")
    print("=" * 50)
    
    try:
        # Создаем соединение
        print("🔄 Подключение к SMTP серверу...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        # Включаем debug режим
        server.set_debuglevel(1)
        
        print("🔄 Инициализация TLS...")
        server.starttls()
        
        print("🔄 Аутентификация...")
        server.login(username, password)
        
        print("✅ Успешное подключение к SMTP!")
        
        # Создаем тестовое письмо
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = 'xapstom@gmail.com'  # Ваш личный email
        msg['Subject'] = 'Mentora SMTP Test (Direct)'
        
        body = """
Прямой тест SMTP соединения с Brevo

Если вы получили это письмо, значит:
✅ SMTP сервер работает
✅ Аутентификация прошла успешно
✅ Письма отправляются корректно

Настройки:
- Сервер: smtp-relay.brevo.com
- Порт: 587
- TLS: Включен

С уважением,
Система тестирования Mentora
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        print("📧 Отправка тестового письма...")
        server.send_message(msg)
        
        print("✅ Письмо отправлено успешно!")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Ошибка аутентификации: {e}")
        print("🔍 Проверьте логин и пароль в Brevo")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ Ошибка подключения: {e}")
        print("🔍 Проверьте сервер и порт")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP ошибка: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        print(f"Тип ошибки: {type(e).__name__}")
        return False

def check_brevo_settings():
    """Проверка настроек Brevo"""
    print("\n🔍 Проверка настроек Brevo")
    print("=" * 50)
    
    settings = {
        'SMTP Server': 'smtp-relay.brevo.com',
        'Port': '587',
        'Username': '96d92f001@smtp-brevo.com',
        'Use TLS': 'Yes',
        'Sender': 'noreply@mentora.com.in'
    }
    
    for key, value in settings.items():
        print(f"{key}: {value}")
    
    print("\n💡 Рекомендации:")
    print("1. Убедитесь, что в Brevo панели включен SMTP доступ")
    print("2. Проверьте, что API ключи активны")
    print("3. Убедитесь, что домен mentora.com.in верифицирован")
    print("4. Проверьте лимиты отправки в аккаунте Brevo")

if __name__ == '__main__':
    print("🦷 Mentora Email Debug Tool")
    print("=" * 50)
    
    # Проверяем настройки
    check_brevo_settings()
    
    # Спрашиваем о тесте
    print("\n")
    choice = input("Выполнить прямой тест SMTP? (y/n): ").lower().strip()
    
    if choice in ['y', 'yes', 'да', 'д']:
        success = test_smtp_direct()
        
        if success:
            print("\n✅ Прямой SMTP тест прошел успешно!")
            print("Теперь можно тестировать через Flask приложение.")
        else:
            print("\n❌ Прямой SMTP тест не прошел.")
            print("Проверьте настройки в Brevo панели.")
    else:
        print("Тест отменен.")
