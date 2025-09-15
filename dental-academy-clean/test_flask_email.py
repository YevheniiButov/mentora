#!/usr/bin/env python3
"""
Тест отправки email через Flask приложение
Проверяет, работает ли отправка писем при регистрации
"""

import os
import sys
from datetime import datetime, timedelta

# Добавляем путь к приложению
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_flask_email():
    """Тестирует отправку email через Flask приложение"""
    print("🧪 Тест отправки email через Flask приложение")
    print("=" * 60)
    
    try:
        # Импортируем Flask приложение
        from app import app
        from models import User, db
        from utils.email_service import send_email_confirmation
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            print("✅ Flask приложение загружено")
            
            # Проверяем настройки email
            print(f"\n📧 Настройки email:")
            print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
            print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
            print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
            print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
            print(f"MAIL_PASSWORD: {'SET' if app.config.get('MAIL_PASSWORD') else 'NOT SET'}")
            print(f"MAIL_SUPPRESS_SEND: {app.config.get('MAIL_SUPPRESS_SEND')}")
            
            # Создаем тестового пользователя
            test_email = 'test@example.com'
            
            # Проверяем, существует ли уже тестовый пользователь
            existing_user = User.query.filter_by(email=test_email).first()
            if existing_user:
                print(f"\n👤 Используем существующего тестового пользователя: {existing_user.email}")
                user = existing_user
            else:
                print(f"\n👤 Создаем тестового пользователя: {test_email}")
                user = User(
                    email=test_email,
                    first_name='Test',
                    last_name='User',
                    password_hash=generate_password_hash('testpassword'),
                    role='user',
                    email_confirmed=False,
                    email_confirmation_token='test-token-123',
                    email_confirmation_sent_at=datetime.utcnow()
                )
                db.session.add(user)
                db.session.commit()
                print("✅ Тестовый пользователь создан")
            
            # Тестируем отправку email подтверждения
            print(f"\n📧 Отправка email подтверждения...")
            success = send_email_confirmation(user, 'test-token-123')
            
            if success:
                print("✅ Email подтверждения отправлен успешно!")
                return True
            else:
                print("❌ Ошибка при отправке email подтверждения")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка при тестировании Flask email: {str(e)}")
        import traceback
        print(f"Детали ошибки:\n{traceback.format_exc()}")
        return False

def test_direct_smtp():
    """Тестирует прямое SMTP соединение для сравнения"""
    print("\n🔧 Прямой SMTP тест для сравнения")
    print("=" * 60)
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Настройки из .env
        smtp_server = 'smtp-relay.brevo.com'
        smtp_port = 587
        username = '96d92f001@smtp-brevo.com'
        password = 'JrbVFGpHhgynKMOQ'
        sender_email = 'noreply@mentora.com'
        
        print(f"Сервер: {smtp_server}")
        print(f"Порт: {smtp_port}")
        print(f"Пользователь: {username}")
        print(f"Отправитель: {sender_email}")
        
        # Создаем соединение
        print("\n🔄 Подключение к SMTP серверу...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        print("✅ Успешное подключение к SMTP!")
        
        # Создаем тестовое письмо
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = 'xapstom@gmail.com'  # Ваш email для тестирования
        msg['Subject'] = 'Mentora Flask Email Test'
        
        body = """
Тест отправки email через Flask приложение

Если вы получили это письмо, значит:
✅ SMTP сервер работает
✅ Аутентификация прошла успешно
✅ Flask приложение может отправлять письма

Настройки:
- Сервер: smtp-relay.brevo.com
- Порт: 587
- TLS: Включен
- Flask: Работает

С уважением,
Система тестирования Mentora
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        print("📧 Отправка тестового письма...")
        server.send_message(msg)
        print("✅ Письмо отправлено успешно!")
        
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при прямом SMTP тесте: {str(e)}")
        return False

def main():
    print("🦷 Mentora Flask Email Test")
    print("=" * 60)
    
    # Тестируем прямое SMTP соединение
    smtp_success = test_direct_smtp()
    
    # Тестируем Flask приложение
    flask_success = test_flask_email()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    print(f"Прямое SMTP соединение: {'✅ УСПЕШНО' if smtp_success else '❌ ОШИБКА'}")
    print(f"Flask приложение: {'✅ УСПЕШНО' if flask_success else '❌ ОШИБКА'}")
    
    if smtp_success and flask_success:
        print("\n🎉 Все тесты прошли успешно!")
        print("Email отправка работает корректно.")
    elif smtp_success and not flask_success:
        print("\n⚠️ Прямое SMTP работает, но Flask приложение не может отправлять письма.")
        print("Проверьте настройки Flask-Mail и код отправки писем.")
    elif not smtp_success and flask_success:
        print("\n⚠️ Flask приложение работает, но прямое SMTP не работает.")
        print("Это странно, но основная функциональность работает.")
    else:
        print("\n❌ Ни один тест не прошел.")
        print("Проверьте настройки email и подключение к интернету.")

if __name__ == '__main__':
    main()
