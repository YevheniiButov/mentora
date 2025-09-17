#!/usr/bin/env python3
"""
Повторная отправка email подтверждений пользователям с неподтвержденными email
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
import secrets

# Загружаем переменные окружения
load_dotenv()

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from extensions import init_extensions, db
from models import User
from utils.email_service import send_email_confirmation

def generate_confirmation_token():
    """Генерируем токен подтверждения"""
    return secrets.token_urlsafe(32)

def resend_email_confirmations():
    """Повторно отправляем email подтверждения"""
    
    # Создаем Flask приложение
    app = Flask(__name__)
    
    # Настройки для работы с базой данных
    app.config.update({
        'SECRET_KEY': 'test-secret-key',
        'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL', 'sqlite:///dental_academy_clean.db'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'MAIL_SERVER': os.environ.get('MAIL_SERVER'),
        'MAIL_PORT': int(os.environ.get('MAIL_PORT', 587)),
        'MAIL_USE_TLS': os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true',
        'MAIL_USERNAME': os.environ.get('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_DEFAULT_SENDER'),
        'MAIL_SUPPRESS_SEND': os.environ.get('MAIL_SUPPRESS_SEND', 'false').lower() == 'true',
        'BASE_URL': os.environ.get('BASE_URL', 'https://bigmentor.nl'),
    })
    
    # Инициализируем расширения
    init_extensions(app)
    
    with app.app_context():
        print("=== ПОВТОРНАЯ ОТПРАВКА EMAIL ПОДТВЕРЖДЕНИЙ ===")
        print()
        
        # Находим пользователей с неподтвержденными email
        unconfirmed_users = User.query.filter_by(email_confirmed=False).all()
        print(f"📧 Найдено пользователей с неподтвержденными email: {len(unconfirmed_users)}")
        
        if not unconfirmed_users:
            print("✅ Все пользователи уже подтвердили свои email адреса!")
            return
        
        print()
        print("🔍 СПИСОК ПОЛЬЗОВАТЕЛЕЙ ДЛЯ ПОВТОРНОЙ ОТПРАВКИ:")
        print("-" * 80)
        
        success_count = 0
        error_count = 0
        
        for i, user in enumerate(unconfirmed_users, 1):
            print(f"{i}. {user.email} ({user.first_name} {user.last_name})")
            
            try:
                # Генерируем новый токен подтверждения
                confirmation_token = generate_confirmation_token()
                
                # Отправляем email подтверждения
                result = send_email_confirmation(user, confirmation_token)
                
                if result:
                    print(f"   ✅ Email отправлен успешно")
                    success_count += 1
                else:
                    print(f"   ❌ Ошибка отправки email")
                    error_count += 1
                    
            except Exception as e:
                print(f"   ❌ Ошибка: {str(e)}")
                error_count += 1
            
            print()
        
        print("=" * 80)
        print("📊 ИТОГИ:")
        print(f"✅ Успешно отправлено: {success_count}")
        print(f"❌ Ошибок: {error_count}")
        print(f"📧 Всего обработано: {len(unconfirmed_users)}")
        
        if success_count > 0:
            print()
            print("💡 РЕКОМЕНДАЦИИ:")
            print("1. Проверьте почтовые ящики пользователей")
            print("2. Убедитесь, что письма не попали в спам")
            print("3. Пользователи могут подтвердить email по ссылке в письме")
            print("4. После подтверждения они смогут войти в систему")

if __name__ == '__main__':
    resend_email_confirmations()
