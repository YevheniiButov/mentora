#!/usr/bin/env python3
"""
Email Configuration Diagnostic Script
Проверяет конфигурацию email и тестирует отправку
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def check_email_config():
    """Проверяет конфигурацию email"""
    print("🔍 EMAIL CONFIGURATION DIAGNOSTIC")
    print("=" * 50)
    
    # Проверяем переменные окружения
    config_vars = [
        'MAIL_SERVER',
        'MAIL_PORT', 
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'MAIL_USE_TLS',
        'MAIL_USE_SSL',
        'MAIL_DEFAULT_SENDER',
        'MAIL_SUPPRESS_SEND'
    ]
    
    config = {}
    for var in config_vars:
        value = os.environ.get(var)
        if var == 'MAIL_PASSWORD' and value:
            value = '*' * len(value)  # Скрываем пароль
        config[var] = value
        status = "✅" if value else "❌"
        print(f"{status} {var}: {value}")
    
    print("\n" + "=" * 50)
    
    # Проверяем критические настройки
    critical_vars = ['MAIL_SERVER', 'MAIL_USERNAME', 'MAIL_PASSWORD']
    missing_vars = [var for var in critical_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ КРИТИЧЕСКИЕ НАСТРОЙКИ ОТСУТСТВУЮТ: {', '.join(missing_vars)}")
        return False
    
    if os.environ.get('MAIL_SUPPRESS_SEND', 'false').lower() in ['true', 'on', '1']:
        print("⚠️  MAIL_SUPPRESS_SEND=true - email отправка отключена")
        return False
    
    print("✅ Все критические настройки присутствуют")
    return True

def test_smtp_connection():
    """Тестирует SMTP соединение"""
    print("\n🔗 TESTING SMTP CONNECTION")
    print("=" * 50)
    
    try:
        server = os.environ.get('MAIL_SERVER')
        port = int(os.environ.get('MAIL_PORT', 587))
        username = os.environ.get('MAIL_USERNAME')
        password = os.environ.get('MAIL_PASSWORD')
        
        print(f"Подключение к {server}:{port}...")
        
        # Создаем SMTP соединение
        smtp = smtplib.SMTP(server, port)
        smtp.starttls()  # Включаем TLS
        smtp.login(username, password)
        
        print("✅ SMTP соединение успешно")
        smtp.quit()
        return True
        
    except Exception as e:
        print(f"❌ SMTP соединение не удалось: {e}")
        return False

def test_email_sending():
    """Тестирует отправку email"""
    print("\n📧 TESTING EMAIL SENDING")
    print("=" * 50)
    
    try:
        # Получаем настройки
        server = os.environ.get('MAIL_SERVER')
        port = int(os.environ.get('MAIL_PORT', 587))
        username = os.environ.get('MAIL_USERNAME')
        password = os.environ.get('MAIL_PASSWORD')
        sender = os.environ.get('MAIL_DEFAULT_SENDER', username)
        
        # Создаем тестовое сообщение
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = username  # Отправляем себе
        msg['Subject'] = "Mentora - Email Test"
        
        body = """
        Это тестовое сообщение от Mentora.
        
        Если вы получили это сообщение, значит email система работает корректно.
        
        Время отправки: {time}
        """.format(time=os.popen('date').read().strip())
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Отправляем email
        smtp = smtplib.SMTP(server, port)
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(msg)
        smtp.quit()
        
        print("✅ Тестовое сообщение отправлено успешно")
        print(f"📧 Отправлено на: {username}")
        return True
        
    except Exception as e:
        print(f"❌ Отправка email не удалась: {e}")
        return False

def main():
    """Основная функция диагностики"""
    print("🚀 MENTORA EMAIL DIAGNOSTIC TOOL")
    print("=" * 50)
    
    # Проверяем конфигурацию
    config_ok = check_email_config()
    
    if not config_ok:
        print("\n❌ Конфигурация неполная. Проверьте переменные окружения.")
        return
    
    # Тестируем SMTP соединение
    smtp_ok = test_smtp_connection()
    
    if not smtp_ok:
        print("\n❌ SMTP соединение не удалось. Проверьте настройки сервера.")
        return
    
    # Тестируем отправку email
    email_ok = test_email_sending()
    
    if email_ok:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("Email система настроена и работает корректно.")
    else:
        print("\n❌ Отправка email не удалась. Проверьте настройки.")

if __name__ == "__main__":
    main()
