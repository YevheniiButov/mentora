#!/usr/bin/env python3
"""
Gmail SMTP Test - быстрая альтернатива Brevo
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_smtp():
    """Тест Gmail SMTP"""
    print("📧 Gmail SMTP Test")
    print("=" * 50)
    
    # Gmail настройки
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    username = input("Введите ваш Gmail: ")
    password = input("Введите App Password (не обычный пароль!): ")
    
    print(f"Тестируем: {username}")
    print("=" * 50)
    
    try:
        # Подключение
        print("🔄 Подключение к Gmail SMTP...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        print("🔄 Аутентификация...")
        server.login(username, password)
        
        print("✅ Успешная аутентификация!")
        
        # Отправка тестового письма
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = username  # Отправляем себе
        msg['Subject'] = 'Mentora Gmail SMTP Test'
        
        body = """
Тест Gmail SMTP для Mentora

Если вы получили это письмо, значит Gmail SMTP работает корректно!

Можно использовать эти настройки в Mentora.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        print("📧 Отправка тестового письма...")
        server.send_message(msg)
        
        print("✅ Письмо отправлено успешно!")
        print("📬 Проверьте свой Gmail inbox")
        
        server.quit()
        
        print("\n" + "="*50)
        print("🎯 НАСТРОЙКИ ДЛЯ MENTORA:")
        print(f"MAIL_SERVER = 'smtp.gmail.com'")
        print(f"MAIL_PORT = '587'")
        print(f"MAIL_USERNAME = '{username}'")
        print(f"MAIL_PASSWORD = '{password}'")
        print(f"MAIL_DEFAULT_SENDER = '{username}'")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        
        if "authentication" in str(e).lower():
            print("\n🔍 Проблема с аутентификацией:")
            print("1. Убедитесь, что включена 2-Step Verification")
            print("2. Используйте App Password, а не обычный пароль")
            print("3. Перейдите: https://myaccount.google.com/apppasswords")
        
        return False

if __name__ == '__main__':
    print("🦷 Mentora - Gmail SMTP Test")
    print("\n💡 Для работы нужен App Password:")
    print("1. Включите 2-Step Verification в Google")
    print("2. Создайте App Password в Google Account")
    print("3. Используйте App Password вместо обычного пароля")
    print()
    
    choice = input("Продолжить тест? (y/n): ").lower()
    if choice in ['y', 'yes']:
        test_gmail_smtp()
    else:
        print("Тест отменен.")
